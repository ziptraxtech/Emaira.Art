"""Seed a test user + session for automated testing.

Creates:
  - User: test-restoration@emaira.art (subscription_tier = collectors_advisory)
  - Session with bearer token = TEST_SESSION_TOKEN_RESTORATION_2026

Run: python3 /app/backend/seed_test_session.py
"""
import asyncio
import os
import uuid
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

ROOT = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(ROOT, ".env"))

MONGO_URL = os.environ["MONGO_URL"]
DB_NAME = os.environ["DB_NAME"]

TEST_EMAIL = "test-restoration@emaira.art"
TEST_TOKEN = "TEST_SESSION_TOKEN_RESTORATION_2026"


async def seed():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]

    existing = await db.users.find_one({"email": TEST_EMAIL}, {"_id": 0})
    if existing:
        user_id = existing["user_id"]
        await db.users.update_one(
            {"user_id": user_id},
            {"$set": {
                "subscription_tier": "collectors_advisory",
                "role": "user",
                "last_active": datetime.now(timezone.utc).isoformat(),
            }}
        )
    else:
        user_id = f"user_{uuid.uuid4().hex[:12]}"
        await db.users.insert_one({
            "user_id": user_id,
            "email": TEST_EMAIL,
            "name": "Restoration Tester",
            "picture": None,
            "role": "user",
            "subscription_tier": "collectors_advisory",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "last_active": datetime.now(timezone.utc).isoformat(),
        })

    # Upsert session
    expires_at = datetime.now(timezone.utc) + timedelta(days=30)
    await db.user_sessions.delete_many({"session_token": TEST_TOKEN})
    await db.user_sessions.insert_one({
        "session_id": str(uuid.uuid4()),
        "user_id": user_id,
        "session_token": TEST_TOKEN,
        "expires_at": expires_at.isoformat(),
        "created_at": datetime.now(timezone.utc).isoformat(),
    })

    print(f"Seeded user_id={user_id} email={TEST_EMAIL}")
    print(f"Bearer token: {TEST_TOKEN}")

    client.close()


if __name__ == "__main__":
    asyncio.run(seed())
