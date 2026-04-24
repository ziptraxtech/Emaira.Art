"""
Iteration-10 Architects feature tests.
Covers:
  1. Background analyze (upload auto-kick + manual trigger)
  2. Stripe + Razorpay checkout (architects tiers)
  3. BIM design-reference upload + PDF export
  4. Public share links (paid gating, idempotency, public view, asset streaming, revoke)
  5. (Frontend-related share flow ID is produced here for the frontend test)

Re-uses seeded bearer + promotes user to architects_pro via motor during paid tests,
then reverts to collectors_advisory at teardown.
"""
import os
import re
import time
import asyncio
import pytest
import requests
import cv2
import numpy as np
from pathlib import Path
from pymongo import MongoClient

# -------------------- config --------------------
BASE_URL = None
for line in Path("/app/frontend/.env").read_text().splitlines():
    if line.startswith("REACT_APP_BACKEND_URL="):
        BASE_URL = line.split("=", 1)[1].strip().strip('"').strip("'").rstrip("/")
assert BASE_URL, "REACT_APP_BACKEND_URL missing"

env = {}
for line in Path("/app/backend/.env").read_text().splitlines():
    if "=" in line and not line.strip().startswith("#"):
        k, v = line.split("=", 1)
        env[k.strip()] = v.strip().strip('"').strip("'")
MONGO_URL = env["MONGO_URL"]
DB_NAME = env["DB_NAME"]

BEARER = "TEST_SESSION_TOKEN_RESTORATION_2026"
AUTH = {"Authorization": f"Bearer {BEARER}"}
TEST_EMAIL = "test-restoration@emaira.art"

STATE = {"proj_id": None, "insp_id": None, "share_token": None}


# -------------------- helpers --------------------
def _mk_mp4(path):
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    w = cv2.VideoWriter(path, fourcc, 12.0, (320, 240))
    for i in range(24):
        f = np.full((240, 320, 3), (i * 8 % 255, 120, 200), dtype=np.uint8)
        cv2.putText(f, f"F{i}", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        w.write(f)
    w.release()


def _mk_jpg(path):
    img = np.full((480, 640, 3), (200, 220, 240), dtype=np.uint8)
    cv2.putText(img, "BIM REFERENCE", (60, 240), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (10, 10, 10), 3)
    cv2.imwrite(path, img)


def _promote_user(tier):
    c = MongoClient(MONGO_URL)
    try:
        c[DB_NAME].users.update_one({"email": TEST_EMAIL}, {"$set": {"subscription_tier": tier}})
    finally:
        c.close()


def _poll_completed(insp_id, timeout=90):
    t0 = time.time()
    last = None
    while time.time() - t0 < timeout:
        r = requests.get(f"{BASE_URL}/api/architects/inspections/{insp_id}", headers=AUTH, timeout=30)
        if r.status_code == 200:
            last = r.json().get("status")
            if last == "completed":
                return True, last
            if last == "failed":
                return False, last
        time.sleep(2)
    return False, last


# -------------------- 0. setup: project + upload with design_reference --------------------
class TestSetupUpload:
    def test_create_project(self):
        r = requests.post(
            f"{BASE_URL}/api/architects/projects",
            headers=AUTH,
            json={"name": "TEST_v10_proj", "location": "Dubai", "project_type": "residential"},
            timeout=30,
        )
        assert r.status_code == 200, r.text
        STATE["proj_id"] = r.json()["project_id"]

    def test_upload_with_design_reference_autokicks_analyze(self, tmp_path):
        mp4 = str(tmp_path / "qa.mp4")
        jpg = str(tmp_path / "ref.jpg")
        _mk_mp4(mp4)
        _mk_jpg(jpg)
        with open(mp4, "rb") as vf, open(jpg, "rb") as rf:
            files = {
                "video": ("qa.mp4", vf, "video/mp4"),
                "design_reference": ("ref.jpg", rf, "image/jpeg"),
            }
            data = {
                "project_id": STATE["proj_id"],
                "title": "TEST_v10_insp",
                "inspection_type": "design_validation",
                "notes": "bim test",
            }
            r = requests.post(
                f"{BASE_URL}/api/architects/inspections/upload",
                headers=AUTH,
                files=files,
                data=data,
                timeout=120,
            )
        assert r.status_code == 200, r.text
        body = r.json()
        # ---- Requirement: status is 'analyzing' immediately
        assert body["status"] == "analyzing", f"expected analyzing, got {body['status']}"
        assert body.get("design_reference_image_id"), "design_reference_image_id should be stored"
        STATE["insp_id"] = body["inspection_id"]

    def test_manual_analyze_409_while_analyzing(self):
        # Immediately re-call analyze while the background task is still running
        r = requests.post(
            f"{BASE_URL}/api/architects/inspections/{STATE['insp_id']}/analyze",
            headers=AUTH,
            timeout=15,
        )
        # Either 409 (still analyzing) or 200 (just finished) are acceptable; prefer 409
        assert r.status_code in (200, 409), r.text
        if r.status_code == 200:
            assert r.json().get("status") == "analyzing"

    def test_poll_until_completed(self):
        ok, last = _poll_completed(STATE["insp_id"], timeout=120)
        assert ok, f"inspection did not complete, last status={last}"

    def test_design_reference_endpoint(self):
        r = requests.get(
            f"{BASE_URL}/api/architects/inspections/{STATE['insp_id']}/design-reference",
            headers=AUTH,
            timeout=30,
        )
        assert r.status_code == 200
        assert r.headers.get("content-type", "").startswith("image/")
        assert len(r.content) > 500


# -------------------- 1. PDF export --------------------
class TestPDFExport:
    def test_pdf_export_ok(self, tmp_path):
        r = requests.get(
            f"{BASE_URL}/api/architects/inspections/{STATE['insp_id']}/report.pdf",
            headers=AUTH,
            timeout=60,
        )
        assert r.status_code == 200, r.text
        assert r.headers.get("content-type", "").startswith("application/pdf")
        cd = r.headers.get("content-disposition", "")
        assert "attachment" in cd.lower() or "inline" in cd.lower()
        assert r.content.startswith(b"%PDF-")
        out = tmp_path / "report.pdf"
        out.write_bytes(r.content)
        assert out.stat().st_size > 5000, f"pdf too small: {out.stat().st_size}"


# -------------------- 2. Stripe / Razorpay checkout --------------------
class TestPaymentCheckout:
    def test_stripe_architects_starter_ok(self):
        r = requests.post(
            f"{BASE_URL}/api/payments/stripe/checkout",
            headers=AUTH,
            json={"tier_id": "architects_starter", "origin_url": "https://example.com"},
            timeout=45,
        )
        assert r.status_code == 200, r.text
        body = r.json()
        assert body.get("url"), body
        assert body.get("session_id"), body

        # Verify payment_transactions metadata was recorded correctly
        c = MongoClient(MONGO_URL)
        try:
            doc = c[DB_NAME].payment_transactions.find_one(
                {"session_id": body["session_id"]}
            )
            assert doc is not None, "payment_transactions record missing"
            md = doc.get("metadata") or {}
            assert md.get("type") == "architects_subscription", md
            assert md.get("product") == "architects", md
        finally:
            c.close()

    def test_stripe_enterprise_rejected(self):
        r = requests.post(
            f"{BASE_URL}/api/payments/stripe/checkout",
            headers=AUTH,
            json={"tier_id": "architects_enterprise", "origin_url": "https://example.com"},
            timeout=30,
        )
        assert r.status_code == 400, r.text
        detail = (r.json().get("detail") or "").lower()
        assert "contact" in detail or "enterprise" in detail

    def test_razorpay_architects_pro(self):
        r = requests.post(
            f"{BASE_URL}/api/payments/razorpay/order",
            headers=AUTH,
            json={"tier_id": "architects_pro"},
            timeout=30,
        )
        # Accept 200 (keys configured) or 500 with 'Razorpay not configured'
        if r.status_code == 200:
            body = r.json()
            assert body.get("order_id")
            assert body.get("currency") == "INR"
            assert body.get("amount")
            assert body.get("key_id")
        else:
            assert r.status_code == 500, r.text
            assert "razorpay" in r.json().get("detail", "").lower()


# -------------------- 3. Share-link gating + flow --------------------
class TestShareLinks:
    def test_share_forbidden_for_collectors_advisory(self):
        _promote_user("collectors_advisory")  # ensure current
        r = requests.post(
            f"{BASE_URL}/api/architects/inspections/{STATE['insp_id']}/share",
            headers=AUTH,
            timeout=30,
        )
        assert r.status_code == 403, r.text
        detail = r.json().get("detail", "")
        assert "Architects Starter" in detail and "Pro" in detail and "Enterprise" in detail

    def test_share_ok_after_promotion_idempotent(self):
        _promote_user("architects_pro")
        r1 = requests.post(
            f"{BASE_URL}/api/architects/inspections/{STATE['insp_id']}/share",
            headers=AUTH,
            timeout=30,
        )
        assert r1.status_code == 200, r1.text
        b1 = r1.json()
        assert b1.get("token") and b1.get("share_id")
        STATE["share_token"] = b1["token"]

        # Idempotent: same token returned
        r2 = requests.post(
            f"{BASE_URL}/api/architects/inspections/{STATE['insp_id']}/share",
            headers=AUTH,
            timeout=30,
        )
        assert r2.status_code == 200
        assert r2.json()["token"] == b1["token"]

    def test_public_share_view_redacts_user_id_and_counts(self):
        tok = STATE["share_token"]
        r1 = requests.get(f"{BASE_URL}/api/architects/share/{tok}", timeout=30)
        assert r1.status_code == 200, r1.text
        b1 = r1.json()
        assert "user_id" not in b1, "user_id must be redacted"
        assert b1.get("title")
        assert b1.get("status") == "completed"
        assert isinstance(b1.get("findings"), list)
        assert "video_url" in b1 and "keyframes" in b1
        c1 = b1.get("share_view_count")
        # second call should increment
        r2 = requests.get(f"{BASE_URL}/api/architects/share/{tok}", timeout=30)
        c2 = r2.json().get("share_view_count")
        assert c2 > c1, f"view_count did not increment: {c1} -> {c2}"

    def test_public_share_invalid_and_unknown(self):
        r_bad = requests.get(f"{BASE_URL}/api/architects/share/not-a-hex", timeout=15)
        assert r_bad.status_code == 400
        r_unk = requests.get(f"{BASE_URL}/api/architects/share/{'0'*32}", timeout=15)
        assert r_unk.status_code == 404

    def test_public_share_assets(self):
        tok = STATE["share_token"]
        rv = requests.get(f"{BASE_URL}/api/architects/share/{tok}/video", timeout=30)
        assert rv.status_code == 200
        assert rv.headers.get("content-type", "").startswith("video/")

        rk = requests.get(f"{BASE_URL}/api/architects/share/{tok}/keyframe/0", timeout=30)
        assert rk.status_code == 200
        assert rk.headers.get("content-type", "").startswith("image/")

        rp = requests.get(f"{BASE_URL}/api/architects/share/{tok}/report.pdf", timeout=60)
        assert rp.status_code == 200
        assert rp.headers.get("content-type", "").startswith("application/pdf")
        assert rp.content.startswith(b"%PDF-")

    def test_revoke_share(self):
        tok = STATE["share_token"]
        rd = requests.delete(
            f"{BASE_URL}/api/architects/inspections/{STATE['insp_id']}/share",
            headers=AUTH,
            timeout=30,
        )
        assert rd.status_code == 200
        rg = requests.get(f"{BASE_URL}/api/architects/share/{tok}", timeout=15)
        assert rg.status_code == 404


# -------------------- teardown: revert tier --------------------
def test_zzz_revert_tier():
    _promote_user("collectors_advisory")
    # verify via /api/auth/me
    r = requests.get(f"{BASE_URL}/api/auth/me", headers=AUTH, timeout=15)
    assert r.status_code == 200
    assert r.json().get("subscription_tier") == "collectors_advisory"
