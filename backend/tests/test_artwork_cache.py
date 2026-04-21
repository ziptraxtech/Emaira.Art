"""Tests for new /api/artworks/cache endpoint and regression checks."""
import os
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://vr-storyteller.preview.emergentagent.com").rstrip("/")
BEARER = "TEST_SESSION_TOKEN_RESTORATION_2026"

ARTWORK_IDS = [
    "art_mona_lisa", "art_starry_night", "art_girl_pearl", "art_persistence",
    "art_birth_venus", "art_last_supper", "art_guernica", "art_scream",
    "art_water_lilies", "art_night_watch", "art_american_gothic", "art_the_kiss",
    "art_las_meninas", "art_great_wave", "art_grande_jatte", "art_creation_adam",
    "art_impression_sunrise", "art_cafe_terrace", "art_arnolfini", "art_nighthawks",
    "art_campbell_soup", "art_marilyn_diptych", "art_drowning_girl", "art_no_5_1948",
    "art_rothko_orange", "art_balloon_dog", "art_girl_balloon",
    "art_physical_impossibility", "art_warhol_marilyn", "art_basquiat_skull",
    "art_hockney_splash", "art_kusama_infinity", "art_kaws_companion",
    "art_ai_weiwei_seeds", "art_richter_abstract", "art_bacon_triptych",
    "art_bourgeois_spider", "art_kapoor_bean", "art_wanderer_sea_fog",
    "art_olympia", "art_liberty_leading", "art_girl_earring_vermeer",
    "art_school_athens", "art_garden_delights", "art_whistlers_mother",
    "art_david_michelangelo", "art_nighthawks_hopper", "art_the_thinker",
    "art_son_of_man", "art_venus_de_milo",
]


# ===================== Artwork cache endpoint =====================

@pytest.mark.parametrize("artwork_id", ARTWORK_IDS)
def test_cache_returns_valid_jpeg(artwork_id):
    r = requests.get(f"{BASE_URL}/api/artworks/cache/{artwork_id}", timeout=30)
    assert r.status_code == 200, f"{artwork_id} -> {r.status_code}"
    assert r.headers.get("content-type", "").startswith("image/jpeg"), (
        f"{artwork_id} content-type: {r.headers.get('content-type')}"
    )
    assert len(r.content) > 5000, f"{artwork_id} size {len(r.content)}"
    # JPEG magic bytes
    assert r.content[:2] == b"\xff\xd8", f"{artwork_id} not valid JPEG start"


def test_cache_invalid_id_returns_400():
    r = requests.get(f"{BASE_URL}/api/artworks/cache/INVALID!id", timeout=15)
    assert r.status_code == 400


def test_cache_missing_id_returns_404():
    r = requests.get(f"{BASE_URL}/api/artworks/cache/art_doesnotexist", timeout=15)
    assert r.status_code == 404


def test_cache_control_header_mona_lisa():
    r = requests.get(f"{BASE_URL}/api/artworks/cache/art_mona_lisa", timeout=15)
    assert r.status_code == 200
    cc = r.headers.get("cache-control", "")
    assert "public" in cc and "max-age=31536000" in cc and "immutable" in cc, f"got: {cc}"


# ===================== /api/artworks listing uses local URLs =====================

def test_artworks_list_uses_local_cache_urls():
    r = requests.get(f"{BASE_URL}/api/artworks", timeout=30)
    assert r.status_code == 200
    artworks = r.json()
    assert isinstance(artworks, list)
    assert len(artworks) >= 50, f"expected >=50 artworks, got {len(artworks)}"
    bad = [a for a in artworks if not str(a.get("image_url", "")).startswith("/api/artworks/cache/")]
    assert not bad, f"artworks with non-local image_url: {[a.get('artwork_id') for a in bad[:5]]}"


# ===================== Regression =====================

def test_auth_me_with_bearer():
    r = requests.get(
        f"{BASE_URL}/api/auth/me",
        headers={"Authorization": f"Bearer {BEARER}"},
        timeout=15,
    )
    assert r.status_code == 200, r.text
    data = r.json()
    assert "email" in data


def test_payments_tiers():
    r = requests.get(f"{BASE_URL}/api/payments/tiers", timeout=15)
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, (list, dict))


def test_restoration_scans_with_bearer():
    r = requests.get(
        f"{BASE_URL}/api/restoration/scans",
        headers={"Authorization": f"Bearer {BEARER}"},
        timeout=15,
    )
    assert r.status_code == 200


def test_artwork_periods():
    r = requests.get(f"{BASE_URL}/api/artworks/periods", timeout=15)
    assert r.status_code == 200
