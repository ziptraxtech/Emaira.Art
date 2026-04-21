"""
Art Restoration feature backend tests
Tests: /api/restoration/* endpoints, auth, tier gating, pricing.
"""
import os
import base64
import io
import pytest
import requests
from pathlib import Path

# Load REACT_APP_BACKEND_URL from /app/frontend/.env
def _load_frontend_url():
    env_path = Path("/app/frontend/.env")
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            if line.startswith("REACT_APP_BACKEND_URL="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    return os.environ.get("REACT_APP_BACKEND_URL")

BASE_URL = _load_frontend_url().rstrip("/")
BEARER_TOKEN = "TEST_SESSION_TOKEN_RESTORATION_2026"
AUTH_HEADERS = {"Authorization": f"Bearer {BEARER_TOKEN}"}


def _make_jpeg_base64():
    """Build a small but valid JPEG (10x10 red square) and return base64 string."""
    try:
        from PIL import Image
        img = Image.new("RGB", (10, 10), color=(255, 0, 0))
        buf = io.BytesIO()
        img.save(buf, format="JPEG")
        return base64.b64encode(buf.getvalue()).decode("utf-8")
    except Exception:
        # Minimal valid JPEG fallback (tiny red)
        minimal_jpeg_hex = (
            "ffd8ffe000104a46494600010100000100010000ffdb0043000806060706"
            "0508070709090808090b0c0a0b0b0b0b0c110e0e0e0e0e110d0e0e0e0e0e"
            "0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0effc20011"
            "0800010001010100ffc4001f0000010501010101010100000000000000"
            "000102030405060708090a0bffda00080101000000013fffd9"
        )
        return base64.b64encode(bytes.fromhex(minimal_jpeg_hex)).decode("utf-8")


# ----------------- AUTH PROTECTION -----------------

class TestAuthProtection:
    def test_upload_scan_requires_auth(self):
        r = requests.post(f"{BASE_URL}/api/restoration/upload-scan", json={"image_data": "x"})
        assert r.status_code == 401

    def test_scans_list_requires_auth(self):
        r = requests.get(f"{BASE_URL}/api/restoration/scans")
        assert r.status_code == 401

    def test_condition_report_requires_auth(self):
        r = requests.post(f"{BASE_URL}/api/restoration/condition-report", json={"image_id": "x"})
        assert r.status_code == 401

    def test_condition_reports_list_requires_auth(self):
        r = requests.get(f"{BASE_URL}/api/restoration/condition-reports")
        assert r.status_code == 401

    def test_simulate_restoration_requires_auth(self):
        r = requests.post(f"{BASE_URL}/api/restoration/simulate-restoration", json={})
        assert r.status_code == 401

    def test_simulations_list_requires_auth(self):
        r = requests.get(f"{BASE_URL}/api/restoration/simulations")
        assert r.status_code == 401


# ----------------- AUTH: seeded user -----------------

class TestSeededUser:
    def test_me_returns_collectors_advisory(self):
        r = requests.get(f"{BASE_URL}/api/auth/me", headers=AUTH_HEADERS)
        assert r.status_code == 200, r.text
        data = r.json()
        assert data.get("email") == "test-restoration@emaira.art"
        assert data.get("subscription_tier") == "collectors_advisory"


# ----------------- PRICING TIERS -----------------

class TestPricingTiers:
    def test_tiers_endpoint_returns_200(self):
        r = requests.get(f"{BASE_URL}/api/payments/tiers")
        assert r.status_code == 200
        tiers = r.json()
        assert isinstance(tiers, list)
        ids = {t["tier_id"]: t for t in tiers}
        assert "pro_collector" in ids
        assert "collectors_advisory" in ids

    def test_pro_collector_price_increased(self):
        """Flag if pro_collector price is unchanged from older defaults (e.g., 999)."""
        r = requests.get(f"{BASE_URL}/api/payments/tiers")
        tiers = {t["tier_id"]: t for t in r.json()}
        price = tiers["pro_collector"]["price"]
        # Previous known default was 999; increased value should be >= 1499
        assert price >= 1499.00, f"pro_collector price {price} appears unchanged vs defaults"

    def test_collectors_advisory_price_increased(self):
        r = requests.get(f"{BASE_URL}/api/payments/tiers")
        tiers = {t["tier_id"]: t for t in r.json()}
        price = tiers["collectors_advisory"]["price"]
        # Previous known default was ~2999; increased value should be >= 4999
        assert price >= 4999.00, f"collectors_advisory price {price} appears unchanged vs defaults"


# ----------------- UPLOAD + LIST + FETCH SCAN -----------------

@pytest.fixture(scope="module")
def uploaded_scan():
    img_b64 = _make_jpeg_base64()
    payload = {
        "image_data": img_b64,
        "mime_type": "image/jpeg",
        "title": "TEST_Scan Restoration",
        "artist": "TEST_Artist",
        "notes": "pytest upload",
        "resolution": "4032x3024",
        "device": "TestDevice",
    }
    r = requests.post(
        f"{BASE_URL}/api/restoration/upload-scan", json=payload, headers=AUTH_HEADERS
    )
    assert r.status_code == 200, r.text
    data = r.json()
    assert "image_id" in data and data["image_id"].startswith("scan_")
    assert data["image_url"].endswith(data["image_id"])
    return data["image_id"]


class TestScans:
    def test_list_scans_includes_uploaded(self, uploaded_scan):
        r = requests.get(f"{BASE_URL}/api/restoration/scans", headers=AUTH_HEADERS)
        assert r.status_code == 200
        scans = r.json()["scans"]
        assert any(s["image_id"] == uploaded_scan for s in scans)
        sample = next(s for s in scans if s["image_id"] == uploaded_scan)
        assert "image_url" in sample
        assert sample["title"] == "TEST_Scan Restoration"
        assert "data" not in sample  # base64 blob excluded

    def test_get_scan_returns_image_bytes(self, uploaded_scan):
        r = requests.get(f"{BASE_URL}/api/restoration/scan/{uploaded_scan}")
        assert r.status_code == 200
        assert r.headers.get("content-type", "").startswith("image/")
        assert len(r.content) > 0

    def test_get_scan_404_for_unknown(self):
        r = requests.get(f"{BASE_URL}/api/restoration/scan/scan_doesnotexist123")
        assert r.status_code == 404


# ----------------- CONDITION REPORT (Gemini) -----------------

@pytest.fixture(scope="module")
def condition_report(uploaded_scan):
    r = requests.post(
        f"{BASE_URL}/api/restoration/condition-report",
        json={"image_id": uploaded_scan},
        headers=AUTH_HEADERS,
        timeout=90,
    )
    return r, uploaded_scan


class TestConditionReport:
    def test_condition_report_generated(self, condition_report):
        r, _ = condition_report
        assert r.status_code == 200, r.text
        data = r.json()
        assert "report_id" in data
        assert data.get("status") == "completed"
        assert isinstance(data.get("condition_score"), (int, float))
        # Server-side response shape also includes counts of damage and recommendations
        assert "damage_count" in data
        assert "recommendations_count" in data

    def test_condition_report_fetch_by_id(self, condition_report):
        r, _ = condition_report
        if r.status_code != 200:
            pytest.skip("condition report generation failed")
        report_id = r.json()["report_id"]
        r2 = requests.get(
            f"{BASE_URL}/api/restoration/condition-report/{report_id}",
            headers=AUTH_HEADERS,
        )
        assert r2.status_code == 200
        data = r2.json()
        assert data["report_id"] == report_id
        # Verify response contains fields specified in the request
        assert "damage_assessment" in data
        assert isinstance(data["damage_assessment"], list)
        assert "recommendations" in data
        assert isinstance(data["recommendations"], list)
        assert "estimated_restoration_cost" in data
        assert "image_url" in data

    def test_condition_reports_list(self, condition_report):
        r, _ = condition_report
        if r.status_code != 200:
            pytest.skip("condition report generation failed")
        r2 = requests.get(
            f"{BASE_URL}/api/restoration/condition-reports", headers=AUTH_HEADERS
        )
        assert r2.status_code == 200
        reports = r2.json()["reports"]
        assert any(rep["report_id"] == r.json()["report_id"] for rep in reports)


# ----------------- SIMULATE RESTORATION -----------------

class TestSimulateRestoration:
    def test_simulate_restoration_full(self, condition_report):
        r, _ = condition_report
        if r.status_code != 200:
            pytest.skip("condition report generation failed — can't test simulation")
        report_id = r.json()["report_id"]
        r2 = requests.post(
            f"{BASE_URL}/api/restoration/simulate-restoration",
            json={"report_id": report_id, "restoration_type": "cleaning"},
            headers=AUTH_HEADERS,
            timeout=120,
        )
        assert r2.status_code == 200, r2.text
        data = r2.json()
        assert "simulation_id" in data
        assert data["restoration_type"] == "cleaning"
        assert "ai_confidence" in data
        assert "techniques_applied" in data
        assert isinstance(data["techniques_applied"], list)

    def test_simulations_list(self):
        r = requests.get(f"{BASE_URL}/api/restoration/simulations", headers=AUTH_HEADERS)
        assert r.status_code == 200
        sims = r.json()["simulations"]
        assert isinstance(sims, list)

    def test_simulation_get_by_id(self):
        r = requests.get(f"{BASE_URL}/api/restoration/simulations", headers=AUTH_HEADERS)
        sims = r.json().get("simulations", [])
        if not sims:
            pytest.skip("No simulations available")
        sim_id = sims[0]["simulation_id"]
        r2 = requests.get(
            f"{BASE_URL}/api/restoration/simulation/{sim_id}", headers=AUTH_HEADERS
        )
        assert r2.status_code == 200
        data = r2.json()
        assert data["simulation_id"] == sim_id
        assert "original_image_url" in data
        assert "restoration_type" in data
        assert "status" in data
