"""One-time migration: copy all MongoDB collections to Neon (PostgreSQL).

Run locally:
    pip install motor pymongo asyncpg
    MONGO_URL="mongodb+srv://..." DATABASE_URL="postgresql://..." python migrate_mongo_to_neon.py

Each MongoDB document is stored as a JSONB row in the corresponding table.
Existing rows (same _doc content) are silently skipped via ON CONFLICT DO NOTHING.
"""

import asyncio
import json
import os
from datetime import datetime, date

from motor.motor_asyncio import AsyncIOMotorClient
import asyncpg

COLLECTIONS = [
    "users",
    "user_sessions",
    "user_activities",
    "artworks",
    "artwork_scans",
    "stories",
    "email_campaigns",
    "email_sends",
    "museum_partners",
    "advisory_sessions",
    "payment_transactions",
    "forensic_analyses",
    "reviews",
    "review_helpful",
    "notifications",
    "share_links",
    "condition_reports",
    "restoration_simulations",
    "uploaded_images",
    "generated_images",
    "restored_images",
    "vr_narratives",
    "organizations",
    "crm_notes",
    "architects_projects",
    "architects_inspections",
    "architects_findings",
    "architects_share_links",
]


def _json_default(o):
    if isinstance(o, (datetime, date)):
        return o.isoformat()
    raise TypeError(f"Not serializable: {type(o)}")


def doc_to_json(doc: dict) -> str:
    doc.pop("_id", None)
    return json.dumps(doc, default=_json_default)


async def migrate():
    mongo_url = os.environ["MONGO_URL"]
    mongo_db_name = os.environ.get("DB_NAME", "emaira_art")
    db_url = os.environ["DATABASE_URL"]

    print(f"Connecting to MongoDB ({mongo_db_name})...")
    mongo_client = AsyncIOMotorClient(mongo_url)
    mongo_db = mongo_client[mongo_db_name]

    print("Connecting to Neon (PostgreSQL)...")
    pg_pool = await asyncpg.create_pool(db_url, min_size=2, max_size=5)

    # Apply schema first
    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    with open(schema_path) as f:
        schema_sql = f.read()
    async with pg_pool.acquire() as conn:
        await conn.execute(schema_sql)
    print("Schema applied.")

    total_migrated = 0

    for collection_name in COLLECTIONS:
        collection = mongo_db[collection_name]
        count = await collection.count_documents({})
        if count == 0:
            print(f"  {collection_name}: empty, skipping")
            continue

        print(f"  {collection_name}: migrating {count} documents...")
        migrated = 0
        batch = []

        async for doc in collection.find({}, {"_id": 0}):
            batch.append(doc_to_json(doc))
            if len(batch) >= 200:
                async with pg_pool.acquire() as conn:
                    await conn.executemany(
                        f"INSERT INTO {collection_name} (_doc) VALUES ($1) ON CONFLICT DO NOTHING",
                        [(row,) for row in batch],
                    )
                migrated += len(batch)
                batch = []

        if batch:
            async with pg_pool.acquire() as conn:
                await conn.executemany(
                    f"INSERT INTO {collection_name} (_doc) VALUES ($1) ON CONFLICT DO NOTHING",
                    [(row,) for row in batch],
                )
            migrated += len(batch)

        print(f"    → {migrated} rows inserted")
        total_migrated += migrated

    print(f"\nDone. Total rows migrated: {total_migrated}")
    mongo_client.close()
    await pg_pool.close()


if __name__ == "__main__":
    asyncio.run(migrate())
