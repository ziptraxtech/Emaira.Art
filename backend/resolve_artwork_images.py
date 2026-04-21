"""Resolve authentic artwork image URLs by querying the Wikipedia REST API
for each masterpiece page and extracting its lead image (originalimage or thumbnail).

Why: Wikimedia thumbnail paths are hash-based and change; hand-crafted URLs
return 404 if the underlying file was re-scaled or renamed. The REST API
always gives the current valid image path.

Usage:
    python3 resolve_artwork_images.py         # prints {artwork_id: url}
    python3 resolve_artwork_images.py --apply # also updates Mongo + server.py
"""
import asyncio
import json
import os
import re
import sys
import time
from pathlib import Path

import requests
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

ROOT = Path(__file__).parent
load_dotenv(ROOT / ".env")

MONGO_URL = os.environ["MONGO_URL"]
DB_NAME = os.environ["DB_NAME"]
SERVER_PY = ROOT / "server.py"

UA = "EmairaArt/1.0 (contact@emaira.art) Research"

# artwork_id -> (Wikipedia page title for EN wikipedia)
ARTWORK_WIKI_TITLES = {
    "art_mona_lisa": "Mona Lisa",
    "art_last_supper": "The Last Supper (Leonardo)",
    "art_creation_adam": "The Creation of Adam",
    "art_birth_venus": "The Birth of Venus",
    "art_girl_pearl": "Girl with a Pearl Earring",
    "art_night_watch": "The Night Watch",
    "art_las_meninas": "Las Meninas",
    "art_arnolfini": "Arnolfini Portrait",
    "art_starry_night": "The Starry Night",
    "art_cafe_terrace": "Café Terrace at Night",
    "art_water_lilies": "Water Lilies (Monet series)",
    "art_impression_sunrise": "Impression, Sunrise",
    "art_grande_jatte": "A Sunday Afternoon on the Island of La Grande Jatte",
    "art_the_kiss": "The Kiss (Klimt)",
    "art_scream": "The Scream",
    "art_persistence": "The Persistence of Memory",
    "art_guernica": "Guernica (Picasso)",
    "art_american_gothic": "American Gothic",
    "art_nighthawks": "Nighthawks",
    "art_great_wave": "The Great Wave off Kanagawa",
    "art_campbell_soup": "Campbell's Soup Cans",
    "art_marilyn_diptych": "Marilyn Diptych",
    "art_drowning_girl": "Drowning Girl",
    "art_no_5_1948": "No. 5, 1948",
    "art_rothko_orange": "Orange, Red, Yellow",
    "art_balloon_dog": "Balloon Dog",
    "art_girl_balloon": "Girl with Balloon",
    "art_physical_impossibility": "The Physical Impossibility of Death in the Mind of Someone Living",
    "art_warhol_marilyn": "Shot Marilyns",
    "art_basquiat_skull": "Untitled (1981 painting by Jean-Michel Basquiat)",
    "art_hockney_splash": "A Bigger Splash",
    "art_kusama_infinity": "Infinity Mirrored Room",
    "art_kaws_companion": "KAWS",
    "art_ai_weiwei_seeds": "Sunflower Seeds (Ai Weiwei)",
    "art_richter_abstract": "Abstraktes Bild",
    "art_bacon_triptych": "Three Studies of Lucian Freud",
    "art_bourgeois_spider": "Maman (sculpture)",
    "art_kapoor_bean": "Cloud Gate",
    "art_wanderer_sea_fog": "Wanderer above the Sea of Fog",
    "art_olympia": "Olympia (Manet)",
    "art_liberty_leading": "Liberty Leading the People",
    "art_girl_earring_vermeer": "The Milkmaid (Vermeer)",
    "art_school_athens": "The School of Athens",
    "art_garden_delights": "The Garden of Earthly Delights",
    "art_whistlers_mother": "Whistler's Mother",
    "art_david_michelangelo": "David (Michelangelo)",
    "art_nighthawks_hopper": "Nighthawks",
    "art_the_thinker": "The Thinker",
    "art_son_of_man": "The Son of Man (Magritte)",
    "art_venus_de_milo": "Venus de Milo",
}


def fetch_wiki_image(title: str) -> str | None:
    """Use the Wikipedia REST summary API which returns a stable image URL."""
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{requests.utils.quote(title, safe='')}"
    try:
        r = requests.get(url, headers={"User-Agent": UA}, timeout=15)
        if r.status_code != 200:
            return None
        data = r.json()
        # Prefer originalimage (full size), fall back to thumbnail
        img = (data.get("originalimage") or data.get("thumbnail") or {}).get("source")
        return img
    except Exception:
        return None


def resolve_all() -> dict[str, str]:
    resolved = {}
    for aid, title in ARTWORK_WIKI_TITLES.items():
        img = fetch_wiki_image(title)
        if img:
            resolved[aid] = img
            print(f"  ✔ {aid:<32} -> {img[:100]}")
        else:
            print(f"  ✘ {aid:<32} (no image for '{title}')")
        time.sleep(0.8)
    return resolved


def thumbnail_for(url: str) -> str:
    # If URL already uses a /thumb/ path with a Npx prefix, swap the size.
    m = re.match(r"^(.*/thumb/.*?)/(\d+)px-(.*)$", url)
    if m:
        return f"{m.group(1)}/400px-{m.group(3)}"
    return url


async def apply_updates(resolved: dict[str, str]):
    # Patch MongoDB
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    upd = 0
    for aid, url in resolved.items():
        r = await db.artworks.update_one(
            {"artwork_id": aid},
            {"$set": {"image_url": url, "thumbnail_url": thumbnail_for(url)}},
        )
        upd += r.matched_count
    client.close()
    print(f"\nMongoDB: updated {upd}/{len(resolved)} artworks")

    # Patch server.py seed data
    text = SERVER_PY.read_text()
    patched = 0
    for aid, url in resolved.items():
        thumb = thumbnail_for(url)
        pattern = re.compile(
            r'("artwork_id":\s*"' + re.escape(aid) + r'",[\s\S]*?)'
            r'"image_url":\s*"[^"]*",(\s*)"thumbnail_url":\s*"[^"]*",'
        )
        new_text, n = pattern.subn(
            lambda m: (
                m.group(1)
                + f'"image_url": "{url}",'
                + m.group(2)
                + f'"thumbnail_url": "{thumb}",'
            ),
            text,
            count=1,
        )
        if n:
            text = new_text
            patched += 1
    SERVER_PY.write_text(text)
    print(f"server.py: patched {patched}/{len(resolved)} artwork blocks")


def main():
    apply = "--apply" in sys.argv
    print(f"Resolving {len(ARTWORK_WIKI_TITLES)} artwork images from Wikipedia...")
    resolved = resolve_all()
    print(f"\nResolved {len(resolved)}/{len(ARTWORK_WIKI_TITLES)} images")
    out = ROOT / "artwork_images_resolved.json"
    out.write_text(json.dumps(resolved, indent=2))
    print(f"Saved mapping -> {out}")
    if apply:
        asyncio.run(apply_updates(resolved))


if __name__ == "__main__":
    main()
