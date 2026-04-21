"""Download every seeded artwork image from its current Wikimedia source URL
into `/app/backend/cache/artworks/{artwork_id}.jpg`, with polite throttling
to stay under Wikimedia rate limits, and update MongoDB so `image_url` and
`thumbnail_url` point to the local API endpoint `/api/artworks/image/{id}`.

Run: python3 /app/backend/download_artwork_cache.py
"""
import asyncio
import os
import sys
import time
from pathlib import Path

import requests
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

ROOT = Path(__file__).parent
load_dotenv(ROOT / ".env")
CACHE = ROOT / "cache" / "artworks"
CACHE.mkdir(parents=True, exist_ok=True)

UA = "EmairaArt/1.0 (https://emaira.art; contact@emaira.art) Research"
MONGO_URL = os.environ["MONGO_URL"]
DB_NAME = os.environ["DB_NAME"]


def download_with_retry(url: str, max_retries: int = 5) -> bytes | None:
    delay = 3
    for attempt in range(max_retries):
        try:
            r = requests.get(url, headers={"User-Agent": UA}, timeout=30)
            if r.status_code == 200 and len(r.content) > 5000:
                return r.content
            if r.status_code in (429, 503):
                print(f"  retry {attempt+1}/{max_retries} in {delay}s (HTTP {r.status_code})")
                time.sleep(delay)
                delay = min(delay * 2, 30)
                continue
            print(f"  failed HTTP {r.status_code}")
            return None
        except Exception as e:
            print(f"  exc: {e}")
            time.sleep(delay)
            delay = min(delay * 2, 30)
    return None


async def main():
    force = "--force" in sys.argv
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    docs = [d async for d in db.artworks.find({}, {"_id": 0, "artwork_id": 1, "image_url": 1, "title": 1})]
    print(f"Found {len(docs)} artworks\n")

    ok, fail = 0, []
    for i, d in enumerate(docs, 1):
        aid = d["artwork_id"]
        cache_file = CACHE / f"{aid}.jpg"
        if cache_file.exists() and cache_file.stat().st_size > 5000 and not force:
            print(f"[{i:>2}/{len(docs)}] ✓ cached  {aid}")
            ok += 1
            continue
        # Skip if already pointing at local cache
        src = d["image_url"]
        if src.startswith("/api/"):
            print(f"[{i:>2}/{len(docs)}] (skip already-local) {aid}")
            continue
        print(f"[{i:>2}/{len(docs)}] ↓ downloading {aid} <- {src[-70:]}")
        content = download_with_retry(src)
        if content:
            cache_file.write_bytes(content)
            print(f"     saved {len(content)} bytes")
            ok += 1
        else:
            fail.append(aid)
        # Polite pacing to avoid Wikimedia rate limits
        time.sleep(2.5)

    # Update MongoDB to use the local endpoint for every successfully cached artwork
    print("\nUpdating MongoDB image_url fields...")
    upd = 0
    for d in docs:
        aid = d["artwork_id"]
        cache_file = CACHE / f"{aid}.jpg"
        if cache_file.exists() and cache_file.stat().st_size > 5000:
            local_url = f"/api/artworks/image/{aid}"
            r = await db.artworks.update_one(
                {"artwork_id": aid},
                {"$set": {"image_url": local_url, "thumbnail_url": local_url}},
            )
            upd += r.matched_count
    print(f"  {upd} artworks now reference local cache")
    print(f"\nDone. ok={ok} failed={fail}")
    client.close()


if __name__ == "__main__":
    asyncio.run(main())
