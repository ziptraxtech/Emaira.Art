"""Fix artwork images: replace generic Unsplash URLs with authentic Wikimedia Commons
masterpiece images for all 50 seeded artworks.

Updates:
  1. MongoDB `artworks` collection (image_url + thumbnail_url) for documents already seeded.
  2. Patches /app/backend/server.py so the next /api/seed call uses correct URLs.

Run: python3 /app/backend/fix_artwork_images.py
"""
import asyncio
import os
import re
import sys
from pathlib import Path
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

ROOT = Path(__file__).parent
load_dotenv(ROOT / ".env")

MONGO_URL = os.environ["MONGO_URL"]
DB_NAME = os.environ["DB_NAME"]
SERVER_PY = ROOT / "server.py"

# Authentic Wikimedia Commons / Wikipedia URLs for each masterpiece (public domain
# or fair-use where original work remains copyrighted).  We request an 800px thumb
# version so the page loads fast while preserving artwork fidelity.
ARTWORK_IMAGES = {
    "art_mona_lisa": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ec/Mona_Lisa%2C_by_Leonardo_da_Vinci%2C_from_C2RMF_retouched.jpg/800px-Mona_Lisa%2C_by_Leonardo_da_Vinci%2C_from_C2RMF_retouched.jpg",
    "art_last_supper": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4b/%C3%9Altima_Cena_-_Da_Vinci_5.jpg/800px-%C3%9Altima_Cena_-_Da_Vinci_5.jpg",
    "art_creation_adam": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6a/Michelangelo_-_Creation_of_Adam_%28cropped%29.jpg/800px-Michelangelo_-_Creation_of_Adam_%28cropped%29.jpg",
    "art_birth_venus": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0b/Sandro_Botticelli_-_La_nascita_di_Venere_-_Google_Art_Project_-_edited.jpg/800px-Sandro_Botticelli_-_La_nascita_di_Venere_-_Google_Art_Project_-_edited.jpg",
    "art_girl_pearl": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0f/1665_Girl_with_a_Pearl_Earring.jpg/800px-1665_Girl_with_a_Pearl_Earring.jpg",
    "art_night_watch": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0b/The_Night_Watch_-_HD.jpg/800px-The_Night_Watch_-_HD.jpg",
    "art_las_meninas": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/19/Las_Meninas_01.jpg/800px-Las_Meninas_01.jpg",
    "art_arnolfini": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/86/Van_Eyck_-_Arnolfini_Portrait.jpg/800px-Van_Eyck_-_Arnolfini_Portrait.jpg",
    "art_starry_night": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ea/Van_Gogh_-_Starry_Night_-_Google_Art_Project.jpg/800px-Van_Gogh_-_Starry_Night_-_Google_Art_Project.jpg",
    "art_cafe_terrace": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/00/Van_Gogh_-_Terrasse_des_Caf%C3%A9s_an_der_Place_du_Forum_in_Arles_am_Abend1.jpeg/800px-Van_Gogh_-_Terrasse_des_Caf%C3%A9s_an_der_Place_du_Forum_in_Arles_am_Abend1.jpeg",
    "art_water_lilies": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/99/Claude_Monet_038.jpg/800px-Claude_Monet_038.jpg",
    "art_impression_sunrise": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/59/Monet_-_Impression%2C_Sunrise.jpg/800px-Monet_-_Impression%2C_Sunrise.jpg",
    "art_grande_jatte": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7d/A_Sunday_on_La_Grande_Jatte%2C_Georges_Seurat%2C_1884.jpg/800px-A_Sunday_on_La_Grande_Jatte%2C_Georges_Seurat%2C_1884.jpg",
    "art_the_kiss": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/40/The_Kiss_-_Gustav_Klimt_-_Google_Cultural_Institute.jpg/800px-The_Kiss_-_Gustav_Klimt_-_Google_Cultural_Institute.jpg",
    "art_scream": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Edvard_Munch%2C_1893%2C_The_Scream%2C_oil%2C_tempera_and_pastel_on_cardboard%2C_91_x_73_cm%2C_National_Gallery_of_Norway.jpg/800px-Edvard_Munch%2C_1893%2C_The_Scream%2C_oil%2C_tempera_and_pastel_on_cardboard%2C_91_x_73_cm%2C_National_Gallery_of_Norway.jpg",
    "art_persistence": "https://upload.wikimedia.org/wikipedia/en/d/dd/The_Persistence_of_Memory.jpg",
    "art_guernica": "https://upload.wikimedia.org/wikipedia/en/7/74/PicassoGuernica.jpg",
    "art_american_gothic": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/cc/Grant_Wood_-_American_Gothic_-_Google_Art_Project.jpg/800px-Grant_Wood_-_American_Gothic_-_Google_Art_Project.jpg",
    "art_nighthawks": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/ba/Nighthawks_by_Edward_Hopper_1942.jpg/800px-Nighthawks_by_Edward_Hopper_1942.jpg",
    "art_great_wave": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a5/Tsunami_by_hokusai_19th_century.jpg/800px-Tsunami_by_hokusai_19th_century.jpg",
    "art_campbell_soup": "https://upload.wikimedia.org/wikipedia/en/3/3c/Campbells_Soup_Cans_MOMA.jpg",
    "art_marilyn_diptych": "https://upload.wikimedia.org/wikipedia/en/5/51/Marilyndiptych.jpg",
    "art_drowning_girl": "https://upload.wikimedia.org/wikipedia/en/d/df/Roy_Lichtenstein_Drowning_Girl.jpg",
    "art_no_5_1948": "https://upload.wikimedia.org/wikipedia/en/6/69/No._5%2C_1948.jpg",
    "art_rothko_orange": "https://upload.wikimedia.org/wikipedia/en/2/27/Orange%2C_Red%2C_Yellow.jpg",
    "art_balloon_dog": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/47/Jeff_Koons_Balloon_Dog_%28Magenta%29.jpg/800px-Jeff_Koons_Balloon_Dog_%28Magenta%29.jpg",
    "art_girl_balloon": "https://upload.wikimedia.org/wikipedia/en/d/d7/Banksy_Girl_and_Heart_Balloon.jpg",
    "art_physical_impossibility": "https://upload.wikimedia.org/wikipedia/en/9/9a/Physical_Impossibility.jpg",
    "art_warhol_marilyn": "https://upload.wikimedia.org/wikipedia/en/1/1b/Shot_Sage_Blue_Marilyn.jpg",
    "art_basquiat_skull": "https://upload.wikimedia.org/wikipedia/en/5/5f/Basquiat-untitled-skull.jpg",
    "art_hockney_splash": "https://upload.wikimedia.org/wikipedia/en/c/cc/ABiggerSplash.jpg",
    "art_kusama_infinity": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c6/Infinity_Mirrored_Room_-_The_Souls_of_Millions_of_Light_Years_Away.jpg/800px-Infinity_Mirrored_Room_-_The_Souls_of_Millions_of_Light_Years_Away.jpg",
    "art_kaws_companion": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/33/KAWS_COMPANION_%28Passing_Through%29_at_Harbour_City%2C_Hong_Kong.jpg/800px-KAWS_COMPANION_%28Passing_Through%29_at_Harbour_City%2C_Hong_Kong.jpg",
    "art_ai_weiwei_seeds": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d9/Sunflower_Seeds_at_the_Tate_Modern_%28Turbine_Hall%29_-_2010-11-08.jpg/800px-Sunflower_Seeds_at_the_Tate_Modern_%28Turbine_Hall%29_-_2010-11-08.jpg",
    "art_richter_abstract": "https://upload.wikimedia.org/wikipedia/en/a/a6/Gerhard_Richter_Abstraktes_Bild_1994.jpg",
    "art_bacon_triptych": "https://upload.wikimedia.org/wikipedia/en/3/34/Three_Studies_of_Lucian_Freud.jpg",
    "art_bourgeois_spider": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5f/Maman_by_Louise_Bourgeois_%28Guggenheim_Bilbao%29.jpg/800px-Maman_by_Louise_Bourgeois_%28Guggenheim_Bilbao%29.jpg",
    "art_kapoor_bean": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/08/Cloud_Gate_%28The_Bean%29_from_east%27.jpg/800px-Cloud_Gate_%28The_Bean%29_from_east%27.jpg",
    "art_wanderer_sea_fog": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b9/Caspar_David_Friedrich_-_Wanderer_above_the_sea_of_fog.jpg/800px-Caspar_David_Friedrich_-_Wanderer_above_the_sea_of_fog.jpg",
    "art_olympia": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5c/Edouard_Manet_-_Olympia_-_Google_Art_Project_3.jpg/800px-Edouard_Manet_-_Olympia_-_Google_Art_Project_3.jpg",
    "art_liberty_leading": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/05/Eug%C3%A8ne_Delacroix_-_La_libert%C3%A9_guidant_le_peuple.jpg/800px-Eug%C3%A8ne_Delacroix_-_La_libert%C3%A9_guidant_le_peuple.jpg",
    "art_girl_earring_vermeer": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/20/Johannes_Vermeer_-_Het_melkmeisje_-_Google_Art_Project.jpg/800px-Johannes_Vermeer_-_Het_melkmeisje_-_Google_Art_Project.jpg",
    "art_school_athens": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/94/Sanzio_01.jpg/800px-Sanzio_01.jpg",
    "art_garden_delights": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ae/The_Garden_of_earthly_delights.jpg/800px-The_Garden_of_earthly_delights.jpg",
    "art_whistlers_mother": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b7/Whistlers_Mother_high_res.jpg/800px-Whistlers_Mother_high_res.jpg",
    "art_david_michelangelo": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/80/%27David%27_by_Michelangelo_Fir_JBU002.jpg/800px-%27David%27_by_Michelangelo_Fir_JBU002.jpg",
    "art_nighthawks_hopper": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/ba/Nighthawks_by_Edward_Hopper_1942.jpg/800px-Nighthawks_by_Edward_Hopper_1942.jpg",
    "art_the_thinker": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0e/The_Thinker%2C_Auguste_Rodin.jpg/800px-The_Thinker%2C_Auguste_Rodin.jpg",
    "art_son_of_man": "https://upload.wikimedia.org/wikipedia/en/e/e5/Magritte_TheSonOfMan.jpg",
    "art_venus_de_milo": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/41/Front_views_of_the_Venus_de_Milo.jpg/800px-Front_views_of_the_Venus_de_Milo.jpg",
}


def thumbnail_for(url: str) -> str:
    """Derive a 400px thumbnail URL from an 800px Wikimedia thumb URL."""
    return url.replace("/800px-", "/400px-")


async def update_mongo():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    updated, missing = 0, []
    for art_id, url in ARTWORK_IMAGES.items():
        res = await db.artworks.update_one(
            {"artwork_id": art_id},
            {"$set": {"image_url": url, "thumbnail_url": thumbnail_for(url)}},
        )
        if res.matched_count:
            updated += 1
        else:
            missing.append(art_id)
    client.close()
    return updated, missing


def patch_server_py():
    """Regex-replace image_url + thumbnail_url lines inside each artwork block."""
    text = SERVER_PY.read_text()
    patched = 0
    skipped = []

    # Split only the seed area to keep regex scope small.
    # Strategy: for each artwork_id in the dict, locate its block
    # "artwork_id": "<id>",  ...  "thumbnail_url": "<url>",
    # and rewrite the two URL lines.
    for art_id, url in ARTWORK_IMAGES.items():
        thumb = thumbnail_for(url)
        # Match the artwork block from its artwork_id to its thumbnail_url line.
        pattern = re.compile(
            r'("artwork_id":\s*"' + re.escape(art_id) + r'",[\s\S]*?)'
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
        else:
            skipped.append(art_id)

    SERVER_PY.write_text(text)
    return patched, skipped


async def main():
    print("Patching /app/backend/server.py seed URLs...")
    patched, skipped = patch_server_py()
    print(f"  patched {patched}/{len(ARTWORK_IMAGES)} artwork blocks")
    if skipped:
        print(f"  WARN skipped (not found in seed): {skipped}")

    print("Updating MongoDB artworks collection...")
    updated, missing = await update_mongo()
    print(f"  updated {updated}/{len(ARTWORK_IMAGES)} artworks in DB")
    if missing:
        print(f"  NOTE not in DB (maybe not seeded yet): {missing}")

    print("Done.")


if __name__ == "__main__":
    asyncio.run(main())
