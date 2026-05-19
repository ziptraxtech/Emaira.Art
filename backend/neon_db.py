"""MongoDB-compatible async adapter over asyncpg/Neon PostgreSQL.

Every collection is stored as a JSONB `_doc` column with expression indexes
on the fields that appear in WHERE clauses. The public API mirrors Motor so
that existing call-sites need no changes.
"""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional, Tuple

import asyncpg


# ---------------------------------------------------------------------------
# JSON helpers
# ---------------------------------------------------------------------------

def _dumps(v: Any) -> str:
    """Serialize a Python value to a JSON string (handles datetime, etc.)."""
    from datetime import datetime, date
    def _default(o):
        if isinstance(o, (datetime, date)):
            return o.isoformat()
        raise TypeError(f"Object of type {type(o)} is not JSON serializable")
    return json.dumps(v, default=_default)


def _loads(s: str | None) -> Any:
    if s is None:
        return None
    return json.loads(s)


# ---------------------------------------------------------------------------
# WHERE-clause builder
# ---------------------------------------------------------------------------

def _build_where(filter_: Dict, offset: int = 0) -> Tuple[str, List]:
    """Translate a MongoDB filter dict to a SQL WHERE clause + param list.

    Returns (sql_fragment, params) where params are 1-indexed starting at
    offset+1.
    """
    if not filter_:
        return "TRUE", []

    parts: List[str] = []
    params: List[Any] = []

    def next_idx() -> int:
        return offset + len(params) + 1

    for key, value in filter_.items():
        if key == "$or":
            sub_parts = []
            for sub in value:
                sub_sql, sub_p = _build_where(sub, offset + len(params))
                sub_parts.append(f"({sub_sql})")
                params.extend(sub_p)
            parts.append(f"({' OR '.join(sub_parts)})")
        elif key == "$and":
            for sub in value:
                sub_sql, sub_p = _build_where(sub, offset + len(params))
                parts.append(f"({sub_sql})")
                params.extend(sub_p)
        elif isinstance(value, dict):
            for op, op_val in value.items():
                idx = next_idx()
                if op == "$eq":
                    params.append(_dumps(op_val))
                    parts.append(f"_doc->'{key}' = ${idx}::jsonb")
                elif op == "$ne":
                    params.append(_dumps(op_val))
                    parts.append(f"(_doc->'{key}' != ${idx}::jsonb OR NOT (_doc ? '{key}'))")
                elif op == "$gt":
                    params.append(str(op_val))
                    parts.append(f"(_doc->>'{key}')::numeric > ${idx}::numeric")
                elif op == "$gte":
                    params.append(str(op_val) if not isinstance(op_val, str) else op_val)
                    if isinstance(op_val, str):
                        parts.append(f"_doc->>'{key}' >= ${idx}")
                    else:
                        parts.append(f"(_doc->>'{key}')::numeric >= ${idx}::numeric")
                elif op == "$lt":
                    params.append(str(op_val) if not isinstance(op_val, str) else op_val)
                    if isinstance(op_val, str):
                        parts.append(f"_doc->>'{key}' < ${idx}")
                    else:
                        parts.append(f"(_doc->>'{key}')::numeric < ${idx}::numeric")
                elif op == "$lte":
                    params.append(str(op_val) if not isinstance(op_val, str) else op_val)
                    if isinstance(op_val, str):
                        parts.append(f"_doc->>'{key}' <= ${idx}")
                    else:
                        parts.append(f"(_doc->>'{key}')::numeric <= ${idx}::numeric")
                elif op == "$in":
                    if not op_val:
                        parts.append("FALSE")
                    else:
                        placeholders = []
                        for item in op_val:
                            i = next_idx()
                            params.append(str(item))
                            placeholders.append(f"${i}")
                        parts.append(f"_doc->>'{key}' IN ({', '.join(placeholders)})")
                elif op == "$nin":
                    if not op_val:
                        parts.append("TRUE")
                    else:
                        placeholders = []
                        for item in op_val:
                            i = next_idx()
                            params.append(str(item))
                            placeholders.append(f"${i}")
                        parts.append(f"(_doc->>'{key}' NOT IN ({', '.join(placeholders)}) OR NOT (_doc ? '{key}'))")
                elif op == "$exists":
                    if op_val:
                        parts.append(f"_doc ? '{key}'")
                    else:
                        parts.append(f"NOT (_doc ? '{key}')")
                elif op == "$regex":
                    params.append(op_val)
                    parts.append(f"_doc->>'{key}' ~ ${idx}")
                elif op == "$options":
                    pass  # handled with $regex above
                elif op == "$size":
                    params.append(str(op_val))
                    parts.append(f"jsonb_array_length(COALESCE(_doc->'{key}', '[]'::jsonb)) = ${idx}::int")
        else:
            idx = next_idx()
            if value is None:
                parts.append(f"(_doc->'{key}' IS NULL OR NOT (_doc ? '{key}'))")
            elif isinstance(value, bool):
                params.append(_dumps(value))
                parts.append(f"_doc->'{key}' = ${idx}::jsonb")
            elif isinstance(value, (int, float)):
                params.append(_dumps(value))
                parts.append(f"_doc->'{key}' = ${idx}::jsonb")
            else:
                params.append(str(value))
                parts.append(f"_doc->>'{key}' = ${idx}")

    return (" AND ".join(parts) if parts else "TRUE"), params


# ---------------------------------------------------------------------------
# UPDATE builder ($set, $push, $pull, $inc, $unset, $addToSet)
# ---------------------------------------------------------------------------

def _build_update(update_dict: Dict, param_offset: int = 0) -> Tuple[str, List]:
    """Translate a MongoDB update dict to a SQL SET fragment."""
    parts: List[str] = []
    params: List[Any] = []

    def next_idx() -> int:
        return param_offset + len(params) + 1

    for op, fields in update_dict.items():
        if op == "$set":
            # Merge all flat fields into one JSONB object to avoid
            # "multiple assignments to same column" PostgreSQL error.
            flat: Dict[str, Any] = {}
            nested_parts: List[str] = []
            for key, val in fields.items():
                if "." in key:
                    keys = key.split(".")
                    path = "{" + ",".join(keys) + "}"
                    idx = next_idx()
                    params.append(_dumps(val))
                    nested_parts.append(
                        f"jsonb_set(_doc, '{path}', ${idx}::jsonb, true)"
                    )
                else:
                    flat[key] = val
            # Apply flat fields as a single merge
            if flat:
                idx = next_idx()
                params.append(_dumps(flat))
                base = f"_doc || ${idx}::jsonb"
                # Chain nested jsonb_set calls on top of the flat merge
                for np in nested_parts:
                    base = np.replace("_doc", f"({base})", 1)
                parts.append(f"_doc = {base}")
            elif nested_parts:
                base = nested_parts[0]
                for np in nested_parts[1:]:
                    base = np.replace("_doc", f"({base})", 1)
                parts.append(f"_doc = {base}")
        elif op == "$unset":
            for key in (fields if isinstance(fields, list) else fields.keys()):
                parts.append(f"_doc = _doc - '{key}'")
        elif op == "$inc":
            for key, val in fields.items():
                parts.append(
                    f"_doc = jsonb_set(_doc, '{{{key}}}', "
                    f"(COALESCE((_doc->>'{key}')::numeric, 0) + {val})::text::jsonb)"
                )
        elif op == "$push":
            for key, val in fields.items():
                idx = next_idx()
                params.append(_dumps(val))
                parts.append(
                    f"_doc = jsonb_set(_doc, '{{{key}}}', "
                    f"COALESCE(_doc->'{key}', '[]'::jsonb) || ${idx}::jsonb)"
                )
        elif op == "$pull":
            for key, val in fields.items():
                idx = next_idx()
                params.append(_dumps(val))
                parts.append(
                    f"_doc = jsonb_set(_doc, '{{{key}}}', "
                    f"(SELECT COALESCE(jsonb_agg(elem), '[]'::jsonb) "
                    f"FROM jsonb_array_elements(COALESCE(_doc->'{key}', '[]'::jsonb)) elem "
                    f"WHERE elem != ${idx}::jsonb))"
                )
        elif op == "$addToSet":
            for key, val in fields.items():
                idx = next_idx()
                params.append(_dumps(val))
                parts.append(
                    f"_doc = CASE WHEN _doc->'{key}' @> ${idx}::jsonb THEN _doc "
                    f"ELSE jsonb_set(_doc, '{{{key}}}', "
                    f"COALESCE(_doc->'{key}', '[]'::jsonb) || ${idx}::jsonb) END"
                )

    return ", ".join(parts) if parts else "_doc = _doc", params


# ---------------------------------------------------------------------------
# Cursor (mimics Motor cursor: .sort .skip .limit .to_list)
# ---------------------------------------------------------------------------

class _Cursor:
    def __init__(self, pool: asyncpg.Pool, sql: str, params: List):
        self._pool = pool
        self._sql = sql
        self._params = params
        self._sort_field: Optional[str] = None
        self._sort_dir = "DESC"
        self._skip_val = 0
        self._limit_val: Optional[int] = None

    def sort(self, key, direction=-1):
        if isinstance(key, list):
            key = key[0][0] if key else "created_at"
        self._sort_field = key
        self._sort_dir = "ASC" if direction == 1 else "DESC"
        return self

    def skip(self, n: int):
        self._skip_val = n
        return self

    def limit(self, n: int):
        self._limit_val = n
        return self

    async def to_list(self, max_length: Optional[int]):
        sql = self._sql
        if self._sort_field:
            sql += f" ORDER BY _doc->>'{self._sort_field}' {self._sort_dir}"
        limit = max_length
        if self._limit_val is not None:
            limit = self._limit_val if max_length is None else min(self._limit_val, max_length)
        if limit is not None:
            sql += f" LIMIT {limit}"
        if self._skip_val:
            sql += f" OFFSET {self._skip_val}"
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(sql, *self._params)
            return [_loads(r["_doc"]) for r in rows]


# ---------------------------------------------------------------------------
# Collection
# ---------------------------------------------------------------------------

class Collection:
    def __init__(self, pool: asyncpg.Pool, table: str):
        self._pool = pool
        self._table = table

    # ---- read ----

    def find(self, filter_: Optional[Dict] = None, projection=None) -> _Cursor:
        where, params = _build_where(filter_ or {})
        sql = f"SELECT _doc FROM {self._table} WHERE {where}"
        return _Cursor(self._pool, sql, params)

    async def find_one(self, filter_: Optional[Dict] = None, projection=None) -> Optional[Dict]:
        where, params = _build_where(filter_ or {})
        sql = f"SELECT _doc FROM {self._table} WHERE {where} LIMIT 1"
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(sql, *params)
        return _loads(row["_doc"]) if row else None

    async def count_documents(self, filter_: Optional[Dict] = None) -> int:
        where, params = _build_where(filter_ or {})
        sql = f"SELECT COUNT(*) FROM {self._table} WHERE {where}"
        async with self._pool.acquire() as conn:
            return await conn.fetchval(sql, *params) or 0

    # ---- write ----

    async def insert_one(self, doc: Dict):
        doc_json = _dumps(doc)
        async with self._pool.acquire() as conn:
            await conn.execute(
                f"INSERT INTO {self._table} (_doc) VALUES ($1)",
                doc_json,
            )

    async def update_one(self, filter_: Dict, update_: Dict, upsert: bool = False):
        where, where_params = _build_where(filter_)
        set_sql, set_params = _build_update(update_, param_offset=len(where_params))
        params = where_params + set_params
        sql = f"UPDATE {self._table} SET {set_sql} WHERE {where}"
        async with self._pool.acquire() as conn:
            result = await conn.execute(sql, *params)
            if upsert and result == "UPDATE 0":
                doc = dict(filter_)
                for _, fields in update_.items():
                    if isinstance(fields, dict):
                        doc.update(fields)
                await self.insert_one(doc)

    async def update_many(self, filter_: Dict, update_: Dict):
        where, where_params = _build_where(filter_)
        set_sql, set_params = _build_update(update_, param_offset=len(where_params))
        params = where_params + set_params
        sql = f"UPDATE {self._table} SET {set_sql} WHERE {where}"
        async with self._pool.acquire() as conn:
            await conn.execute(sql, *params)

    async def delete_one(self, filter_: Dict):
        where, params = _build_where(filter_)
        sql = (
            f"DELETE FROM {self._table} WHERE ctid = "
            f"(SELECT ctid FROM {self._table} WHERE {where} LIMIT 1)"
        )
        async with self._pool.acquire() as conn:
            await conn.execute(sql, *params)

    async def delete_many(self, filter_: Dict):
        where, params = _build_where(filter_)
        sql = f"DELETE FROM {self._table} WHERE {where}"
        async with self._pool.acquire() as conn:
            await conn.execute(sql, *params)

    async def replace_one(self, filter_: Dict, replacement: Dict, upsert: bool = False):
        where, params = _build_where(filter_)
        idx = len(params) + 1
        params.append(_dumps(replacement))
        sql = f"UPDATE {self._table} SET _doc = ${idx}::jsonb WHERE {where}"
        async with self._pool.acquire() as conn:
            result = await conn.execute(sql, *params)
            if upsert and result == "UPDATE 0":
                await self.insert_one(replacement)

    # ---- aggregation (manually translated) ----

    async def aggregate(self, pipeline: List[Dict]) -> "_AggResult":
        return _AggResult(self._pool, self._table, pipeline)


class _AggResult:
    """Executes a MongoDB aggregation pipeline as SQL. Supports a limited
    set of stages: $match, $group ($sum/$avg), $sort, $limit."""

    def __init__(self, pool, table, pipeline):
        self._pool = pool
        self._table = table
        self._pipeline = pipeline

    async def to_list(self, max_length: Optional[int]) -> List[Dict]:
        match_filter: Dict = {}
        group_stage: Optional[Dict] = None
        sort_stage: Optional[Dict] = None
        limit_stage: Optional[int] = max_length

        for stage in self._pipeline:
            if "$match" in stage:
                match_filter = stage["$match"]
            elif "$group" in stage:
                group_stage = stage["$group"]
            elif "$sort" in stage:
                sort_stage = stage["$sort"]
            elif "$limit" in stage:
                limit_stage = stage["$limit"]

        if group_stage is None:
            # No grouping — just return filtered docs
            where, params = _build_where(match_filter)
            sql = f"SELECT _doc FROM {self._table} WHERE {where}"
            if limit_stage:
                sql += f" LIMIT {limit_stage}"
            async with self._pool.acquire() as conn:
                rows = await conn.fetch(sql, *params)
            return [_loads(r["_doc"]) for r in rows]

        where, params = _build_where(match_filter)
        group_id = group_stage.get("_id")

        # Build SELECT expressions
        select_parts: List[str] = []
        field_aliases: List[str] = []

        # Group key
        if group_id is None:
            select_parts.append("NULL AS _id")
        elif isinstance(group_id, str) and group_id.startswith("$"):
            field = group_id[1:]
            select_parts.append(f"_doc->>'{field}' AS _id")
        elif isinstance(group_id, dict):
            sub_parts = []
            for k, v in group_id.items():
                if isinstance(v, str) and v.startswith("$"):
                    f = v[1:]
                    sub_parts.append(f"'{k}', _doc->>'{f}'")
            select_parts.append(f"jsonb_build_object({', '.join(sub_parts)}) AS _id")
        else:
            select_parts.append(f"'{group_id}' AS _id")

        for alias, expr in group_stage.items():
            if alias == "_id":
                continue
            if isinstance(expr, dict):
                op = list(expr.keys())[0]
                field_ref = list(expr.values())[0]
                if isinstance(field_ref, str) and field_ref.startswith("$"):
                    field = field_ref[1:]
                else:
                    field = None
                if op == "$sum":
                    if field:
                        select_parts.append(f"COALESCE(SUM((_doc->>'{field}')::numeric), 0) AS {alias}")
                    else:
                        select_parts.append(f"COUNT(*) AS {alias}")
                elif op == "$avg":
                    select_parts.append(f"AVG((_doc->>'{field}')::numeric) AS {alias}")
                elif op == "$count":
                    select_parts.append(f"COUNT(*) AS {alias}")
                elif op == "$push":
                    if field:
                        select_parts.append(f"jsonb_agg(_doc->'{field}') AS {alias}")
                    else:
                        select_parts.append(f"jsonb_agg(_doc) AS {alias}")
            field_aliases.append(alias)

        # GROUP BY
        if group_id is None:
            group_by = ""
        elif isinstance(group_id, str) and group_id.startswith("$"):
            field = group_id[1:]
            group_by = f"GROUP BY _doc->>'{field}'"
        elif isinstance(group_id, dict):
            group_by = "GROUP BY " + ", ".join(
                f"_doc->>'{v[1:]}'" for v in group_id.values()
                if isinstance(v, str) and v.startswith("$")
            )
        else:
            group_by = ""

        sql = f"SELECT {', '.join(select_parts)} FROM {self._table} WHERE {where} {group_by}"

        # ORDER BY
        if sort_stage:
            order_parts = []
            for field, direction in sort_stage.items():
                dir_str = "ASC" if direction == 1 else "DESC"
                order_parts.append(f"{field} {dir_str}")
            sql += f" ORDER BY {', '.join(order_parts)}"

        if limit_stage:
            sql += f" LIMIT {limit_stage}"

        async with self._pool.acquire() as conn:
            rows = await conn.fetch(sql, *params)

        result = []
        for row in rows:
            d = dict(row)
            # Convert _id back
            if "_id" in d and isinstance(d["_id"], str):
                try:
                    d["_id"] = json.loads(d["_id"])
                except Exception:
                    pass
            # Convert numeric aggregates
            for k in list(d.keys()):
                if k != "_id" and d[k] is not None:
                    try:
                        d[k] = float(d[k])
                    except (ValueError, TypeError):
                        pass
            result.append(d)
        return result


# ---------------------------------------------------------------------------
# Database (collection accessor)
# ---------------------------------------------------------------------------

class Database:
    def __init__(self, pool: asyncpg.Pool):
        self._pool = pool
        self._cols: Dict[str, Collection] = {}

    def __getattr__(self, name: str) -> Collection:
        if name.startswith("_"):
            raise AttributeError(name)
        if name not in self._cols:
            self._cols[name] = Collection(self._pool, name)
        return self._cols[name]

    def __getitem__(self, name: str) -> Collection:
        return self.__getattr__(name)


# ---------------------------------------------------------------------------
# Pool factory
# ---------------------------------------------------------------------------

async def create_pool(database_url: str) -> asyncpg.Pool:
    return await asyncpg.create_pool(database_url, min_size=2, max_size=10)


async def get_db(pool: asyncpg.Pool) -> Database:
    return Database(pool)
