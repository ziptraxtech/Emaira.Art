"""
Emaira Architects backend tests.
Covers: /api/architects/tiers, /projects, /inspections/upload, /inspections,
inspection detail + video + keyframes, analyze (Gemini), delete, regression.
"""
import os
import io
import time
import tempfile
import pytest
import requests
import cv2
import numpy as np
from pathlib import Path

BASE_URL = None
for line in Path("/app/frontend/.env").read_text().splitlines():
    if line.startswith("REACT_APP_BACKEND_URL="):
        BASE_URL = line.split("=", 1)[1].strip().strip('"').strip("'").rstrip("/")
assert BASE_URL, "REACT_APP_BACKEND_URL missing"

BEARER = "TEST_SESSION_TOKEN_RESTORATION_2026"
AUTH = {"Authorization": f"Bearer {BEARER}"}

# Module-level shared state
STATE = {"proj_id": None, "insp_id": None}


def _make_test_mp4(path: str):
    """Create a tiny OpenCV clip: 36 frames @12fps, 320x240."""
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(path, fourcc, 12.0, (320, 240))
    for i in range(36):
        frame = np.full((240, 320, 3), (i * 6 % 255, 100, 200), dtype=np.uint8)
        cv2.putText(frame, f"F{i}", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        writer.write(frame)
    writer.release()


# ---------- TIERS ----------
class TestTiers:
    def test_tiers_returns_200_with_3(self):
        r = requests.get(f"{BASE_URL}/api/architects/tiers", timeout=30)
        assert r.status_code == 200, r.text
        tiers = r.json()
        assert isinstance(tiers, list)
        ids = {t["tier_id"]: t for t in tiers}
        assert "architects_starter" in ids
        assert "architects_pro" in ids
        assert "architects_enterprise" in ids
        assert ids["architects_starter"]["price"] == 499.0
        assert ids["architects_starter"].get("inspections_limit") == 10 or ids["architects_starter"].get("inspection_limit") == 10 or ids["architects_starter"].get("limit") == 10
        assert ids["architects_pro"]["price"] == 1999.0
        # unlimited marker: either -1, None, or an is_unlimited flag
        pro = ids["architects_pro"]
        assert (pro.get("inspections_limit") in (None, -1, 0)
                or pro.get("is_unlimited") is True
                or pro.get("unlimited") is True), f"pro tier: {pro}"
        ent = ids["architects_enterprise"]
        assert ent.get("is_contact_only") is True, f"enterprise tier: {ent}"


# ---------- PROJECTS ----------
class TestProjects:
    def test_create_project_requires_auth(self):
        r = requests.post(f"{BASE_URL}/api/architects/projects", json={"name": "NoAuth"})
        assert r.status_code == 401

    def test_create_project_empty_name_400(self):
        r = requests.post(f"{BASE_URL}/api/architects/projects",
                          json={"name": ""}, headers=AUTH)
        assert r.status_code == 400, r.text

    def test_create_project_success(self):
        r = requests.post(f"{BASE_URL}/api/architects/projects",
                          json={"name": "TEST_Architects_Proj",
                                "description": "pytest project"},
                          headers=AUTH)
        assert r.status_code == 200, r.text
        data = r.json()
        assert "project_id" in data or "id" in data
        pid = data.get("project_id") or data.get("id")
        assert pid
        STATE["proj_id"] = pid

    def test_list_projects(self):
        r = requests.get(f"{BASE_URL}/api/architects/projects", headers=AUTH)
        assert r.status_code == 200, r.text
        projs = r.json()
        # Accept list or wrapped {projects:[]}
        if isinstance(projs, dict):
            projs = projs.get("projects", [])
        assert isinstance(projs, list)
        pid = STATE["proj_id"]
        assert any((p.get("project_id") or p.get("id")) == pid for p in projs)
        for p in projs:
            if (p.get("project_id") or p.get("id")) == pid:
                assert "inspection_count" in p

    def test_get_project_by_id(self):
        pid = STATE["proj_id"]
        r = requests.get(f"{BASE_URL}/api/architects/projects/{pid}", headers=AUTH)
        assert r.status_code == 200, r.text
        d = r.json()
        # Response shape: {project: {...}, inspections: [...]}
        proj = d.get("project", d)
        assert (proj.get("project_id") or proj.get("id")) == pid
        assert "inspections" in d
        assert isinstance(d["inspections"], list)

    def test_get_project_unknown_404(self):
        r = requests.get(f"{BASE_URL}/api/architects/projects/doesnotexist_xyz", headers=AUTH)
        assert r.status_code == 404


# ---------- UPLOAD + ANALYZE + DETAIL + VIDEO + DELETE ----------
@pytest.fixture(scope="module")
def small_mp4():
    tmp = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
    tmp.close()
    _make_test_mp4(tmp.name)
    assert os.path.getsize(tmp.name) > 0
    yield tmp.name
    try:
        os.unlink(tmp.name)
    except Exception:
        pass


@pytest.fixture(scope="module")
def project_id():
    r = requests.post(f"{BASE_URL}/api/architects/projects",
                      json={"name": "TEST_InspProj", "description": "for inspections"},
                      headers=AUTH)
    assert r.status_code == 200, r.text
    data = r.json()
    return data.get("project_id") or data.get("id")


class TestInspections:
    def test_upload_bad_extension_400(self, project_id):
        files = {"video": ("a.txt", b"hello", "text/plain")}
        data = {"project_id": project_id, "title": "Bad",
                "inspection_type": "safety_monitoring"}
        r = requests.post(f"{BASE_URL}/api/architects/inspections/upload",
                          files=files, data=data, headers=AUTH)
        assert r.status_code == 400, r.text

    def test_upload_unknown_project_404(self, small_mp4):
        with open(small_mp4, "rb") as f:
            files = {"video": ("t.mp4", f, "video/mp4")}
            data = {"project_id": "doesnotexist_project",
                    "title": "bad", "inspection_type": "safety_monitoring"}
            r = requests.post(f"{BASE_URL}/api/architects/inspections/upload",
                              files=files, data=data, headers=AUTH)
        assert r.status_code == 404, r.text

    def test_upload_success(self, project_id, small_mp4):
        with open(small_mp4, "rb") as f:
            files = {"video": ("test_clip.mp4", f, "video/mp4")}
            data = {"project_id": project_id,
                    "title": "TEST_Inspection",
                    "inspection_type": "safety_monitoring"}
            r = requests.post(f"{BASE_URL}/api/architects/inspections/upload",
                              files=files, data=data, headers=AUTH, timeout=120)
        assert r.status_code == 200, r.text
        d = r.json()
        insp_id = d.get("inspection_id") or d.get("id")
        assert insp_id
        assert d.get("status") == "uploaded"
        assert d.get("video_size_bytes", 0) > 0
        assert d.get("keyframe_count", 0) > 0
        STATE["insp_id"] = insp_id

    def test_list_inspections(self):
        r = requests.get(f"{BASE_URL}/api/architects/inspections", headers=AUTH)
        assert r.status_code == 200, r.text
        lst = r.json()
        if isinstance(lst, dict):
            lst = lst.get("inspections", [])
        assert isinstance(lst, list)
        assert any((i.get("inspection_id") or i.get("id")) == STATE["insp_id"] for i in lst)

    def test_get_inspection_detail(self):
        insp_id = STATE["insp_id"]
        r = requests.get(f"{BASE_URL}/api/architects/inspections/{insp_id}", headers=AUTH)
        assert r.status_code == 200, r.text
        d = r.json()
        assert d.get("video_url") == f"/api/architects/inspections/{insp_id}/video"
        assert "keyframes" in d and isinstance(d["keyframes"], list) and len(d["keyframes"]) > 0
        assert "findings" in d and isinstance(d["findings"], list)

    def test_stream_video(self):
        insp_id = STATE["insp_id"]
        r = requests.get(f"{BASE_URL}/api/architects/inspections/{insp_id}/video",
                         headers=AUTH, stream=True, timeout=30)
        assert r.status_code == 200, r.text
        ct = r.headers.get("content-type", "")
        assert "video/mp4" in ct or "video" in ct, f"content-type={ct}"
        chunk = next(r.iter_content(1024), b"")
        assert len(chunk) > 0

    def test_keyframe_jpeg(self):
        insp_id = STATE["insp_id"]
        r = requests.get(f"{BASE_URL}/api/architects/inspections/{insp_id}/keyframe/0",
                         headers=AUTH)
        assert r.status_code == 200, r.text
        assert r.headers.get("content-type", "").startswith("image/")
        # JPEG magic bytes
        assert r.content[:3] == b"\xff\xd8\xff"

    def test_keyframe_invalid_idx_404(self):
        insp_id = STATE["insp_id"]
        r = requests.get(f"{BASE_URL}/api/architects/inspections/{insp_id}/keyframe/999",
                         headers=AUTH)
        assert r.status_code == 404

    def test_analyze_with_gemini(self):
        insp_id = STATE["insp_id"]
        r = requests.post(f"{BASE_URL}/api/architects/inspections/{insp_id}/analyze",
                          headers=AUTH, timeout=120)
        assert r.status_code == 200, r.text
        d = r.json()
        assert d.get("status") == "completed", f"analysis body: {d}"
        assert "overall_risk_level" in d
        assert "findings_count" in d

        # Re-GET detail and verify ai_model + analysis_completed_at
        r2 = requests.get(f"{BASE_URL}/api/architects/inspections/{insp_id}", headers=AUTH)
        assert r2.status_code == 200
        d2 = r2.json()
        assert d2.get("ai_model") == "gemini-3.1-pro-preview", f"ai_model={d2.get('ai_model')}"
        assert d2.get("analysis_completed_at")

    def test_delete_inspection_and_cleanup(self):
        insp_id = STATE["insp_id"]
        r = requests.delete(f"{BASE_URL}/api/architects/inspections/{insp_id}", headers=AUTH)
        assert r.status_code in (200, 204), r.text
        # Video endpoint must now 404 (with auth)
        r2 = requests.get(f"{BASE_URL}/api/architects/inspections/{insp_id}/video",
                          headers=AUTH)
        assert r2.status_code == 404
        # Detail GET should also 404
        r3 = requests.get(f"{BASE_URL}/api/architects/inspections/{insp_id}", headers=AUTH)
        assert r3.status_code == 404


# ---------- REGRESSION ----------
class TestRegression:
    def test_auth_me(self):
        r = requests.get(f"{BASE_URL}/api/auth/me", headers=AUTH)
        assert r.status_code == 200, r.text
        assert r.json().get("email") == "test-restoration@emaira.art"

    def test_restoration_scans(self):
        r = requests.get(f"{BASE_URL}/api/restoration/scans", headers=AUTH)
        assert r.status_code == 200

    def test_artworks_cache_mona_lisa(self):
        r = requests.get(f"{BASE_URL}/api/artworks/cache/art_mona_lisa")
        assert r.status_code == 200
        assert r.headers.get("content-type", "").startswith("image/")
