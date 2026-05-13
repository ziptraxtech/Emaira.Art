"""Emaira Architects QC/QA module — self-contained APIRouter for the Architects business line.

Shared runtime singletons (db, require_auth, log_activity, User, logger) are
sourced from `_runtime` to avoid circular imports with server.py.
"""
import os
import re
import json
import uuid
import asyncio
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any

from fastapi import (
    APIRouter,
    HTTPException,
    Request,
    Response,
    UploadFile,
    File,
    Form,
)
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

import httpx
import _runtime as rt

SEGMENTATION_URL = os.getenv(
    "SEGMENTATION_URL",
    "http://defect-alb-1564603409.ap-south-1.elb.amazonaws.com/segment-video",
)


# ===== Models =====

class ArchitectsProject(BaseModel):
    project_id: str = Field(default_factory=lambda: f"proj_{uuid.uuid4().hex[:10]}")
    user_id: str
    name: str
    location: Optional[str] = None
    project_type: Optional[str] = None  # commercial, residential, infra, industrial
    description: Optional[str] = None
    status: str = "active"  # active, archived
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ArchitectsInspection(BaseModel):
    inspection_id: str = Field(default_factory=lambda: f"insp_{uuid.uuid4().hex[:10]}")
    user_id: str
    project_id: str
    title: str
    inspection_type: str  # defect_detection, safety_monitoring, design_validation
    video_filename: Optional[str] = None
    video_size_bytes: int = 0
    video_duration_sec: Optional[float] = None
    frame_width: Optional[int] = None
    frame_height: Optional[int] = None
    keyframe_count: int = 0
    design_reference_image_id: Optional[str] = None
    segmented_video_filename: Optional[str] = None
    segmentation_frames: Optional[int] = None
    segmentation_detections: Optional[int] = None
    notes: Optional[str] = None
    status: str = "uploaded"  # uploaded, analyzing, completed, failed
    analysis_started_at: Optional[datetime] = None
    analysis_completed_at: Optional[datetime] = None
    overall_summary: Optional[str] = None
    overall_risk_level: Optional[str] = None  # low, medium, high, critical
    defects_count: int = 0
    safety_violations_count: int = 0
    design_deviations_count: int = 0
    ai_model: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ArchitectsFinding(BaseModel):
    finding_id: str = Field(default_factory=lambda: f"find_{uuid.uuid4().hex[:10]}")
    inspection_id: str
    user_id: str
    category: str  # defect, safety_violation, design_deviation, material_note
    type: str  # e.g. "crack", "spalling", "no_hardhat", "misalignment"
    severity: str  # low, medium, high, critical
    confidence: float = 0.0
    timestamp_sec: Optional[float] = None
    bbox_hint: Optional[str] = None  # "top-left", "center", etc.
    description: str
    recommendation: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ArchitectsTier(BaseModel):
    tier_id: str
    name: str
    price: float
    currency: str = "usd"
    period: str
    inspection_limit: int  # -1 = unlimited
    features: List[str]
    is_contact_only: bool = False


ARCHITECTS_TIERS: Dict[str, ArchitectsTier] = {
    "architects_starter": ArchitectsTier(
        tier_id="architects_starter", name="Starter", price=499.0, period="month",
        inspection_limit=10,
        features=[
            "10 video inspections / month",
            "Defect detection (cracks, spalling, misalignment)",
            "Safety monitoring (PPE checks)",
            "PDF/JSON report export",
            "Up to 500 MB per video",
            "Email support",
        ],
    ),
    "architects_pro": ArchitectsTier(
        tier_id="architects_pro", name="Pro", price=1999.0, period="month",
        inspection_limit=-1,
        features=[
            "Unlimited video inspections",
            "All Starter features",
            "Reality vs. Design validation",
            "Custom safety rulesets",
            "Team workspace (up to 10 users)",
            "Priority Gemini 3 Pro analysis queue",
            "Slack / Teams webhook alerts",
            "Dedicated support",
        ],
    ),
    "architects_enterprise": ArchitectsTier(
        tier_id="architects_enterprise", name="Enterprise", price=0.0, period="year",
        inspection_limit=-1, is_contact_only=True,
        features=[
            "Everything in Pro",
            "Custom integrations (BIM, Procore, ACC)",
            "On-premise / private cloud deployment",
            "Custom CV model fine-tuning",
            "24/7 SLA",
            "Dedicated account manager",
        ],
    ),
}



# ===== Router =====

architects_router = APIRouter(prefix="/architects", tags=["Emaira Architects"])

# Local cache dirs (keyframes only — videos stored in S3)
ARCHITECTS_VIDEO_DIR = Path(__file__).parent / "cache" / "architects" / "videos"
ARCHITECTS_KEYFRAME_DIR = Path(__file__).parent / "cache" / "architects" / "keyframes"
ARCHITECTS_VIDEO_DIR.mkdir(parents=True, exist_ok=True)
ARCHITECTS_KEYFRAME_DIR.mkdir(parents=True, exist_ok=True)

S3_BUCKET = os.getenv("S3_BUCKET", "emaira-inspection-videos")

import boto3  # noqa: E402
from botocore.config import Config  # noqa: E402
_s3_region = os.getenv("AWS_DEFAULT_REGION", "ap-south-1")
_s3 = boto3.client(
    "s3",
    region_name=_s3_region,
    endpoint_url=f"https://s3.{_s3_region}.amazonaws.com",
    config=Config(s3={"addressing_style": "virtual"}, signature_version="s3v4"),
)

ARCHITECTS_MAX_VIDEO_MB = 500
ARCHITECTS_VALID_INSPECTION_TYPES = {"defect_detection", "safety_monitoring", "design_validation"}


def _arch_enforce_quota(user: rt.User, inspections_this_month: int) -> None:
    """Raise 403 if user has exceeded their Architects plan inspection quota."""
    tier_id = user.subscription_tier or ""
    tier = ARCHITECTS_TIERS.get(tier_id)
    if not tier:
        # Allow a generous free trial of 2 inspections for any logged-in user
        if inspections_this_month >= 2:
            raise HTTPException(
                status_code=403,
                detail="Free trial exhausted (2 inspections). Upgrade to Emaira Architects Starter or Pro.",
            )
        return
    if tier.inspection_limit == -1:
        return
    if inspections_this_month >= tier.inspection_limit:
        raise HTTPException(
            status_code=403,
            detail=f"Monthly inspection limit ({tier.inspection_limit}) reached on the {tier.name} plan.",
        )


@architects_router.get("/tiers")
async def list_architects_tiers():
    """Public endpoint — lists Emaira Architects subscription tiers."""
    return [t.model_dump() for t in ARCHITECTS_TIERS.values()]


@architects_router.post("/projects")
async def create_architects_project(request: Request):
    user = await rt.require_auth(request)
    body = await request.json()
    name = (body.get("name") or "").strip()
    if not name:
        raise HTTPException(status_code=400, detail="Project name is required")
    project = ArchitectsProject(
        user_id=user.user_id,
        name=name,
        location=body.get("location"),
        project_type=body.get("project_type"),
        description=body.get("description"),
    )
    doc = project.model_dump()
    doc["created_at"] = doc["created_at"].isoformat()
    await rt.db.architects_projects.insert_one(doc)
    doc.pop("_id", None)
    return doc


@architects_router.get("/projects")
async def list_architects_projects(request: Request):
    user = await rt.require_auth(request)
    projects = await rt.db.architects_projects.find(
        {"user_id": user.user_id}, {"_id": 0}
    ).sort("created_at", -1).to_list(100)
    # Attach inspection counts
    for p in projects:
        p["inspection_count"] = await rt.db.architects_inspections.count_documents(
            {"project_id": p["project_id"], "user_id": user.user_id}
        )
    return {"projects": projects}


@architects_router.get("/projects/{project_id}")
async def get_architects_project(project_id: str, request: Request):
    user = await rt.require_auth(request)
    project = await rt.db.architects_projects.find_one(
        {"project_id": project_id, "user_id": user.user_id}, {"_id": 0}
    )
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    inspections = await rt.db.architects_inspections.find(
        {"project_id": project_id, "user_id": user.user_id}, {"_id": 0}
    ).sort("created_at", -1).to_list(200)
    return {"project": project, "inspections": inspections}


def _extract_keyframes(video_path: Path, out_dir: Path, inspection_id: str, max_frames: int = 6) -> Dict[str, Any]:
    """Use OpenCV to probe the video and save evenly-spaced keyframes.
    Returns {duration_sec, width, height, keyframe_count}.
    Keyframes saved as `{inspection_id}_f{index}.jpg`."""
    import cv2  # local import to keep startup fast
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        return {"duration_sec": None, "width": None, "height": None, "keyframe_count": 0}
    fps = cap.get(cv2.CAP_PROP_FPS) or 0
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)
    duration = total / fps if fps > 0 else None
    saved = 0
    if total > 0:
        # evenly-spaced frame indices, skipping the very first and last
        step = max(total // (max_frames + 1), 1)
        for i in range(1, max_frames + 1):
            idx = min(step * i, total - 1)
            cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
            ok, frame = cap.read()
            if not ok or frame is None:
                continue
            # Downscale if very large
            if frame.shape[1] > 1280:
                scale = 1280 / frame.shape[1]
                frame = cv2.resize(frame, (1280, int(frame.shape[0] * scale)))
            out = out_dir / f"{inspection_id}_f{saved}.jpg"
            cv2.imwrite(str(out), frame, [cv2.IMWRITE_JPEG_QUALITY, 82])
            saved += 1
    cap.release()
    return {"duration_sec": duration, "width": width, "height": height, "keyframe_count": saved}


@architects_router.post("/inspections/presign")
async def presign_inspection_upload(request: Request):
    """Return presigned S3 PUT URL(s) for a video or image inspection.
    Optionally also presigns a design_reference image upload."""
    user = await rt.require_auth(request)
    body = await request.json()
    filename = (body.get("filename") or "video.mp4").strip()
    suffix = Path(filename).suffix.lower() or ".mp4"

    VIDEO_EXTS = {".mp4", ".mov", ".m4v", ".webm"}
    IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp"}
    if suffix not in VIDEO_EXTS | IMAGE_EXTS:
        raise HTTPException(status_code=400, detail="Unsupported file format")

    is_image = suffix in IMAGE_EXTS
    inspection_id = f"insp_{uuid.uuid4().hex[:10]}"
    folder = "images" if is_image else "videos"
    s3_key = f"{folder}/{user.user_id}/{inspection_id}{suffix}"

    url = await asyncio.to_thread(
        _s3.generate_presigned_url,
        "put_object",
        Params={"Bucket": S3_BUCKET, "Key": s3_key},
        ExpiresIn=3600,
    )
    result = {"upload_url": url, "inspection_id": inspection_id, "s3_key": s3_key, "is_image": is_image}

    # Optionally presign a design_reference image
    ref_filename = (body.get("ref_filename") or "").strip()
    if ref_filename:
        ref_suffix = Path(ref_filename).suffix.lower() or ".jpg"
        if ref_suffix not in IMAGE_EXTS:
            raise HTTPException(status_code=400, detail="Design reference must be JPG/PNG/WebP")
        ref_key = f"design-refs/{user.user_id}/{inspection_id}{ref_suffix}"
        ref_url = await asyncio.to_thread(
            _s3.generate_presigned_url,
            "put_object",
            Params={"Bucket": S3_BUCKET, "Key": ref_key},
            ExpiresIn=3600,
        )
        result["ref_upload_url"] = ref_url
        result["ref_s3_key"] = ref_key

    return result


@architects_router.post("/inspections/finalize")
async def finalize_inspection_upload(request: Request):
    """Called after the browser finishes the S3 PUT. Downloads the video from S3,
    extracts keyframes, creates the inspection record, and starts AI analysis."""
    user = await rt.require_auth(request)
    body = await request.json()
    inspection_id = (body.get("inspection_id") or "").strip()
    s3_key = (body.get("s3_key") or "").strip()
    project_id = (body.get("project_id") or "").strip()
    title = (body.get("title") or "").strip()
    inspection_type = body.get("inspection_type", "defect_detection")
    notes = body.get("notes") or None

    ref_s3_key = body.get("ref_s3_key") or None

    if not inspection_id or not s3_key or not project_id or not title:
        raise HTTPException(status_code=400, detail="inspection_id, s3_key, project_id and title are required")
    if inspection_type not in ARCHITECTS_VALID_INSPECTION_TYPES:
        raise HTTPException(status_code=400, detail="Invalid inspection_type")

    IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp"}
    suffix = Path(s3_key).suffix.lower()
    is_image = suffix in IMAGE_EXTS
    allowed_prefix = ("images" if is_image else "videos") + f"/{user.user_id}/"
    if not s3_key.startswith(allowed_prefix):
        raise HTTPException(status_code=403, detail="Forbidden")

    project = await rt.db.architects_projects.find_one(
        {"project_id": project_id, "user_id": user.user_id}, {"_id": 0}
    )
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    month_start = datetime.now(timezone.utc).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    count = await rt.db.architects_inspections.count_documents(
        {"user_id": user.user_id, "created_at": {"$gte": month_start.isoformat()}}
    )
    _arch_enforce_quota(user, count)

    # Verify the primary file exists in S3
    try:
        head = await asyncio.to_thread(_s3.head_object, Bucket=S3_BUCKET, Key=s3_key)
    except Exception:
        raise HTTPException(status_code=400, detail="File not found in S3 — upload may have failed")
    size = head["ContentLength"]
    if size > 500 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File exceeds 500 MB limit")

    if is_image:
        # Image inspection: copy image into keyframes dir so analysis can use it
        img_path = ARCHITECTS_KEYFRAME_DIR / f"{inspection_id}_f0{suffix}"
        await asyncio.to_thread(_s3.download_file, S3_BUCKET, s3_key, str(img_path))
        kf_s3_key = f"keyframes/{user.user_id}/{inspection_id}_f0{suffix}"
        await asyncio.to_thread(_s3.upload_file, str(img_path), S3_BUCKET, kf_s3_key)
        probe = {"duration_sec": None, "width": None, "height": None, "keyframe_count": 1}
    else:
        # Video inspection: download and extract keyframes
        video_path = ARCHITECTS_VIDEO_DIR / f"{inspection_id}{suffix}"
        await asyncio.to_thread(_s3.download_file, S3_BUCKET, s3_key, str(video_path))
        probe = await asyncio.to_thread(_extract_keyframes, video_path, ARCHITECTS_KEYFRAME_DIR, inspection_id)
        # Upload keyframes to S3 so they survive container restarts
        for idx in range(probe["keyframe_count"]):
            kf_local = ARCHITECTS_KEYFRAME_DIR / f"{inspection_id}_f{idx}.jpg"
            if kf_local.exists():
                kf_s3_key = f"keyframes/{user.user_id}/{inspection_id}_f{idx}.jpg"
                await asyncio.to_thread(_s3.upload_file, str(kf_local), S3_BUCKET, kf_s3_key)

    # Optional design reference image
    design_ref_id = None
    if ref_s3_key and ref_s3_key.startswith(f"design-refs/{user.user_id}/"):
        ref_suffix = Path(ref_s3_key).suffix.lower() or ".jpg"
        design_ref_id = f"{inspection_id}_design{ref_suffix}"
        await asyncio.to_thread(
            _s3.download_file, S3_BUCKET, ref_s3_key,
            str(ARCHITECTS_KEYFRAME_DIR / design_ref_id)
        )

    inspection = ArchitectsInspection(
        inspection_id=inspection_id,
        user_id=user.user_id,
        project_id=project_id,
        title=title,
        inspection_type=inspection_type,
        video_filename=Path(s3_key).name,
        video_size_bytes=size,
        video_duration_sec=probe["duration_sec"],
        frame_width=probe["width"],
        frame_height=probe["height"],
        keyframe_count=probe["keyframe_count"],
        design_reference_image_id=design_ref_id,
        notes=notes,
        status="uploaded",
    )
    doc = inspection.model_dump()
    doc["created_at"] = doc["created_at"].isoformat()
    doc["s3_key"] = s3_key
    await rt.db.architects_inspections.insert_one(doc)
    await rt.log_activity(user.user_id, "architects_inspection_upload", {
        "inspection_id": inspection_id, "size_mb": round(size / 1_048_576, 2)
    })
    await rt.db.architects_inspections.update_one(
        {"inspection_id": inspection_id},
        {"$set": {
            "status": "analyzing",
            "analysis_started_at": datetime.now(timezone.utc).isoformat(),
        }},
    )
    asyncio.create_task(_run_architects_analysis(inspection_id, user.user_id))
    doc.pop("_id", None)
    doc["status"] = "analyzing"
    return {"inspection_id": inspection_id, "status": "analyzing"}


@architects_router.get("/inspections")
async def list_architects_inspections(request: Request, limit: int = 50):
    user = await rt.require_auth(request)
    items = await rt.db.architects_inspections.find(
        {"user_id": user.user_id}, {"_id": 0}
    ).sort("created_at", -1).to_list(limit)
    return {"inspections": items}


@architects_router.get("/inspections/{inspection_id}")
async def get_architects_inspection(inspection_id: str, request: Request):
    user = await rt.require_auth(request)
    insp = await rt.db.architects_inspections.find_one(
        {"inspection_id": inspection_id, "user_id": user.user_id}, {"_id": 0}
    )
    if not insp:
        raise HTTPException(status_code=404, detail="Inspection not found")
    findings = await rt.db.architects_findings.find(
        {"inspection_id": inspection_id}, {"_id": 0}
    ).sort("timestamp_sec", 1).to_list(500)
    insp["findings"] = findings
    insp["video_url"] = f"/api/architects/inspections/{inspection_id}/video"
    insp["keyframes"] = [
        f"/api/architects/inspections/{inspection_id}/keyframe/{i}"
        for i in range(insp.get("keyframe_count", 0))
    ]
    return insp


@architects_router.get("/inspections/{inspection_id}/video")
async def stream_architects_video(inspection_id: str, request: Request):
    user = await rt.require_auth(request)
    insp = await rt.db.architects_inspections.find_one(
        {"inspection_id": inspection_id, "user_id": user.user_id}, {"_id": 0}
    )
    if not insp:
        raise HTTPException(status_code=404, detail="Inspection not found")
    # Prefer YOLO-segmented video; fall back to original
    seg = ARCHITECTS_VIDEO_DIR / f"{inspection_id}_segmented.mp4"
    if seg.exists():
        return FileResponse(seg, media_type="video/mp4")
    for ext in (".mp4", ".mov", ".m4v", ".webm"):
        p = ARCHITECTS_VIDEO_DIR / f"{inspection_id}{ext}"
        if p.exists():
            mime = {
                ".mp4": "video/mp4", ".mov": "video/quicktime",
                ".m4v": "video/mp4", ".webm": "video/webm",
            }[ext]
            return FileResponse(p, media_type=mime)
    # Cache miss — download from S3 using stored s3_key
    stored_key = insp.get("s3_key") or (
        f"videos/{user.user_id}/{insp['video_filename']}" if insp.get("video_filename") else None
    )
    if not stored_key:
        raise HTTPException(status_code=404, detail="Video file missing")
    ext = Path(stored_key).suffix.lower() or ".mp4"
    local_path = ARCHITECTS_VIDEO_DIR / f"{inspection_id}{ext}"
    try:
        await asyncio.to_thread(_s3.download_file, S3_BUCKET, stored_key, str(local_path))
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Video not found in S3: {e}")
    mime = {".mp4": "video/mp4", ".mov": "video/quicktime", ".m4v": "video/mp4", ".webm": "video/webm"}.get(ext, "video/mp4")
    return FileResponse(local_path, media_type=mime)


@architects_router.get("/inspections/{inspection_id}/keyframe/{idx}")
async def get_architects_keyframe(inspection_id: str, idx: int, request: Request):
    user = await rt.require_auth(request)
    insp = await rt.db.architects_inspections.find_one(
        {"inspection_id": inspection_id, "user_id": user.user_id}, {"_id": 0}
    )
    if not insp:
        raise HTTPException(status_code=404, detail="Inspection not found")
    if idx < 0 or idx >= int(insp.get("keyframe_count", 0)):
        raise HTTPException(status_code=404, detail="Keyframe not found")
    p = ARCHITECTS_KEYFRAME_DIR / f"{inspection_id}_f{idx}.jpg"
    if not p.exists():
        # Try downloading from S3
        kf_s3_key = f"keyframes/{user.user_id}/{inspection_id}_f{idx}.jpg"
        try:
            await asyncio.to_thread(_s3.download_file, S3_BUCKET, kf_s3_key, str(p))
        except Exception:
            raise HTTPException(status_code=404, detail="Keyframe not found in S3")
    return FileResponse(p, media_type="image/jpeg", headers={"Cache-Control": "public, max-age=86400"})


def _architects_prompt(inspection_type: str, inspection_title: str) -> str:
    base = (
        "You are Emaira Architects AI — a senior construction Quality Control engineer. "
        "Analyze the uploaded site video carefully. Reply with STRICT VALID JSON only, no prose, "
        "no markdown fences. Schema:\n"
        "{\n"
        "  \"overall_summary\": string (2-3 sentences),\n"
        "  \"overall_risk_level\": \"low\"|\"medium\"|\"high\"|\"critical\",\n"
        "  \"findings\": [\n"
        "     {\"category\": \"defect\"|\"safety_violation\"|\"design_deviation\"|\"material_note\",\n"
        "      \"type\": string (slug, e.g. \"crack\", \"no_hardhat\"),\n"
        "      \"severity\": \"low\"|\"medium\"|\"high\"|\"critical\",\n"
        "      \"confidence\": number 0-1,\n"
        "      \"timestamp_sec\": number (where in the video),\n"
        "      \"bbox_hint\": string (e.g. \"top-left\", \"center\", \"bottom-right\"),\n"
        "      \"description\": string (1-2 sentences of what you observe),\n"
        "      \"recommendation\": string (concrete action)}\n"
        "  ]\n"
        "}\n"
        f"Inspection title: {inspection_title}\n"
    )
    if inspection_type == "defect_detection":
        base += (
            "FOCUS: structural & finish defects — cracks, spalling, honeycombing, efflorescence, "
            "rebar exposure, water damage, misalignment of walls/columns, uneven finishes, "
            "incorrect material usage. Ignore safety gear. Category MUST be \"defect\"."
        )
    elif inspection_type == "safety_monitoring":
        base += (
            "FOCUS: worker safety — missing hardhat, missing high-vis vest, missing gloves, "
            "unsafe scaffolding, unsafe edge (fall risk), unsafe manual handling, smoking on site, "
            "unsafe crane operation. Category MUST be \"safety_violation\". Always call out individuals "
            "if PPE is missing, and note their location in the frame."
        )
    elif inspection_type == "design_validation":
        base += (
            "FOCUS: reality vs. design — visible deviations from typical construction drawings: "
            "incorrect column locations, missing structural members, wrong opening sizes, "
            "incorrect finish materials, incorrect MEP routing. Category MUST be \"design_deviation\"."
        )
    base += "\nReturn at minimum 1 finding (or an empty array with risk=low if truly nothing observed)."
    return base


async def _call_segmentation(
    video_path: Path, inspection_id: str
) -> tuple[Optional[Path], Optional[int], Optional[int]]:
    """POST video to ECS YOLO service (async job pattern), poll until done, download result.
    Returns (segmented_path, frames, detections) or (None, None, None) on failure."""
    out_path = ARCHITECTS_VIDEO_DIR / f"{inspection_id}_segmented.mp4"
    base_url = SEGMENTATION_URL.rsplit("/segment-video", 1)[0]
    mime_map = {".mp4": "video/mp4", ".mov": "video/quicktime", ".m4v": "video/mp4", ".webm": "video/webm"}
    mime = mime_map.get(video_path.suffix.lower(), "video/mp4")
    try:
        async with httpx.AsyncClient(timeout=300.0) as client:
            # Step 1: submit job
            with open(video_path, "rb") as f:
                resp = await client.post(
                    f"{base_url}/segment-video",
                    files={"file": (video_path.name, f, mime)},
                )
            if resp.status_code != 200:
                rt.logger.warning("Segmentation submit HTTP %s", resp.status_code)
                return None, None, None
            job_id = resp.json().get("job_id")
            if not job_id:
                rt.logger.warning("Segmentation: no job_id in response")
                return None, None, None

            # Step 2: poll status
            for _ in range(120):  # up to ~10 min (5s intervals)
                await asyncio.sleep(5)
                status_resp = await client.get(f"{base_url}/jobs/{job_id}/status")
                status = status_resp.json().get("status")
                if status == "done":
                    break
                if status in ("error", "not_found"):
                    rt.logger.warning("Segmentation job %s failed: %s", job_id, status_resp.json())
                    return None, None, None

            # Step 3: download segmented video
            async with client.stream("GET", f"{base_url}/jobs/{job_id}/download") as dl:
                if dl.status_code != 200:
                    rt.logger.warning("Segmentation download HTTP %s", dl.status_code)
                    return None, None, None
                frames = int(dl.headers.get("x-frames") or 0) or None
                detections = int(dl.headers.get("x-detections") or 0) or None
                with open(out_path, "wb") as out:
                    async for chunk in dl.aiter_bytes(1 << 20):
                        out.write(chunk)

        return out_path, frames, detections
    except Exception as exc:
        rt.logger.warning("Segmentation failed, falling back to original: %s", exc)
        out_path.unlink(missing_ok=True)
        return None, None, None


async def _run_architects_analysis(inspection_id: str, user_id: str):
    """Background analysis worker. Updates the inspection doc + findings collection."""
    insp = await rt.db.architects_inspections.find_one(
        {"inspection_id": inspection_id, "user_id": user_id}, {"_id": 0}
    )
    if not insp:
        return
    video_path = None
    for ext in (".mp4", ".mov", ".m4v", ".webm"):
        p = ARCHITECTS_VIDEO_DIR / f"{inspection_id}{ext}"
        if p.exists():
            video_path = p
            break
    if not video_path:
        await rt.db.architects_inspections.update_one(
            {"inspection_id": inspection_id},
            {"$set": {"status": "failed", "error_message": "Video file missing"}},
        )
        return

    # Run YOLO segmentation; fall back to original on failure
    seg_path, seg_frames, seg_detections = await _call_segmentation(video_path, inspection_id)
    if seg_path:
        await rt.db.architects_inspections.update_one(
            {"inspection_id": inspection_id},
            {"$set": {
                "segmented_video_filename": seg_path.name,
                "segmentation_frames": seg_frames,
                "segmentation_detections": seg_detections,
            }},
        )
    analysis_video_path = seg_path if seg_path else video_path

    # Optional design reference (BIM image) for design_validation
    design_ref_path = None
    if insp.get("inspection_type") == "design_validation" and insp.get("design_reference_image_id"):
        ref_p = ARCHITECTS_KEYFRAME_DIR / insp["design_reference_image_id"]
        if ref_p.exists():
            design_ref_path = ref_p
    try:
        from google import genai as _genai
        from google.genai import types as _gtypes
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("EMERGENT_LLM_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY missing")
        gemini = _genai.Client(api_key=api_key)
        mime = {
            ".mp4": "video/mp4", ".mov": "video/quicktime",
            ".m4v": "video/mp4", ".webm": "video/webm",
        }.get(analysis_video_path.suffix.lower(), "video/mp4")

        # Upload segmented (or original fallback) video to Gemini Files API
        video_upload = await asyncio.to_thread(
            gemini.files.upload,
            file=analysis_video_path,
            config=_gtypes.UploadFileConfig(mime_type=mime, display_name=inspection_id),
        )
        # Wait for Gemini to finish processing the video
        while video_upload.state == _gtypes.FileState.PROCESSING:
            await asyncio.sleep(3)
            video_upload = await asyncio.to_thread(gemini.files.get, name=video_upload.name)
        if video_upload.state == _gtypes.FileState.FAILED:
            raise RuntimeError("Gemini file processing failed")

        parts = [_gtypes.Part.from_uri(file_uri=video_upload.uri, mime_type=mime)]

        if design_ref_path is not None:
            ref_mime = {
                ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
                ".png": "image/png", ".webp": "image/webp",
            }.get(design_ref_path.suffix.lower(), "image/jpeg")
            design_upload = await asyncio.to_thread(
                gemini.files.upload,
                file=design_ref_path,
                config=_gtypes.UploadFileConfig(mime_type=ref_mime),
            )
            parts.append(_gtypes.Part.from_uri(file_uri=design_upload.uri, mime_type=ref_mime))

        prompt = _architects_prompt(insp["inspection_type"], insp["title"])
        if design_ref_path is not None:
            prompt += (
                "\n\nThe SECOND attachment is the reference BIM/design drawing or render. "
                "Compare each frame of the video to this reference and call out every visible deviation."
            )
        parts.append(_gtypes.Part.from_text(text=prompt))

        resp = await gemini.aio.models.generate_content(
            model="gemini-2.5-flash",
            contents=[_gtypes.Content(role="user", parts=parts)],
            config=_gtypes.GenerateContentConfig(
                system_instruction="You are Emaira Architects AI, a construction QC expert. Always reply in strict JSON.",
            ),
        )
        raw = (resp.text or "").strip()
        if raw.startswith("```"):
            raw = raw.split("```", 2)[1]
            if raw.lower().startswith("json"):
                raw = raw[4:]
            raw = raw.rsplit("```", 1)[0].strip()
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            parsed = {
                "overall_summary": "AI returned non-JSON output; stored as free-text note.",
                "overall_risk_level": "low",
                "findings": [{
                    "category": "material_note", "type": "ai_parse_error",
                    "severity": "low", "confidence": 0.2, "timestamp_sec": 0,
                    "bbox_hint": "n/a",
                    "description": raw[:400],
                    "recommendation": "Re-run analysis.",
                }],
            }

        findings_in = parsed.get("findings") or []
        defect = safety = design = 0
        stored = 0
        for f in findings_in:
            cat = f.get("category") or "material_note"
            if cat == "defect":
                defect += 1
            elif cat == "safety_violation":
                safety += 1
            elif cat == "design_deviation":
                design += 1
            finding = ArchitectsFinding(
                inspection_id=inspection_id,
                user_id=user_id,
                category=cat,
                type=str(f.get("type") or "unknown")[:80],
                severity=str(f.get("severity") or "medium"),
                confidence=float(f.get("confidence") or 0.0),
                timestamp_sec=float(f.get("timestamp_sec") or 0.0) or None,
                bbox_hint=f.get("bbox_hint"),
                description=str(f.get("description") or ""),
                recommendation=f.get("recommendation"),
            )
            fdoc = finding.model_dump()
            fdoc["created_at"] = fdoc["created_at"].isoformat()
            await rt.db.architects_findings.insert_one(fdoc)
            stored += 1

        await rt.db.architects_inspections.update_one(
            {"inspection_id": inspection_id},
            {"$set": {
                "status": "completed",
                "analysis_completed_at": datetime.now(timezone.utc).isoformat(),
                "overall_summary": parsed.get("overall_summary"),
                "overall_risk_level": parsed.get("overall_risk_level") or "low",
                "defects_count": defect,
                "safety_violations_count": safety,
                "design_deviations_count": design,
                "ai_model": "gemini-3.1-pro-preview",
                "error_message": None,
            }},
        )
        await rt.log_activity(user_id, "architects_inspection_analyzed", {
            "inspection_id": inspection_id, "findings": stored,
        })
    except Exception as exc:
        rt.logger.exception("Architects analysis failed: %s", exc)
        await rt.db.architects_inspections.update_one(
            {"inspection_id": inspection_id},
            {"$set": {"status": "failed", "error_message": str(exc)[:500]}},
        )


@architects_router.post("/inspections/{inspection_id}/analyze")
async def analyze_architects_inspection(inspection_id: str, request: Request):
    """Kick off background Gemini 3 Pro video analysis. Returns immediately with status='analyzing'."""
    user = await rt.require_auth(request)
    insp = await rt.db.architects_inspections.find_one(
        {"inspection_id": inspection_id, "user_id": user.user_id}, {"_id": 0}
    )
    if not insp:
        raise HTTPException(status_code=404, detail="Inspection not found")
    if insp["status"] == "analyzing":
        raise HTTPException(status_code=409, detail="Analysis already in progress")

    video_exists = any((ARCHITECTS_VIDEO_DIR / f"{inspection_id}{ext}").exists()
                       for ext in (".mp4", ".mov", ".m4v", ".webm"))
    if not video_exists:
        raise HTTPException(status_code=404, detail="Video file missing")

    await rt.db.architects_inspections.update_one(
        {"inspection_id": inspection_id},
        {"$set": {
            "status": "analyzing",
            "analysis_started_at": datetime.now(timezone.utc).isoformat(),
            "error_message": None,
        }},
    )
    await rt.db.architects_findings.delete_many({"inspection_id": inspection_id})
    asyncio.create_task(_run_architects_analysis(inspection_id, user.user_id))
    return {"inspection_id": inspection_id, "status": "analyzing"}


@architects_router.delete("/inspections/{inspection_id}")
async def delete_architects_inspection(inspection_id: str, request: Request):
    user = await rt.require_auth(request)
    insp = await rt.db.architects_inspections.find_one(
        {"inspection_id": inspection_id, "user_id": user.user_id}, {"_id": 0}
    )
    if not insp:
        raise HTTPException(status_code=404, detail="Inspection not found")
    await rt.db.architects_inspections.delete_one({"inspection_id": inspection_id})
    await rt.db.architects_findings.delete_many({"inspection_id": inspection_id})
    await rt.db.architects_share_links.delete_many({"inspection_id": inspection_id})
    # Clean up video + segmented video + keyframes + design reference
    for ext in (".mp4", ".mov", ".m4v", ".webm"):
        (ARCHITECTS_VIDEO_DIR / f"{inspection_id}{ext}").unlink(missing_ok=True)
    (ARCHITECTS_VIDEO_DIR / f"{inspection_id}_segmented.mp4").unlink(missing_ok=True)
    for f in ARCHITECTS_KEYFRAME_DIR.glob(f"{inspection_id}_*"):
        f.unlink(missing_ok=True)
    return {"deleted": True, "inspection_id": inspection_id}


# ---------------- Design-reference image (BIM) ----------------
@architects_router.get("/inspections/{inspection_id}/design-reference")
async def get_architects_design_reference(inspection_id: str, request: Request):
    user = await rt.require_auth(request)
    insp = await rt.db.architects_inspections.find_one(
        {"inspection_id": inspection_id, "user_id": user.user_id}, {"_id": 0}
    )
    if not insp or not insp.get("design_reference_image_id"):
        raise HTTPException(status_code=404, detail="No design reference")
    p = ARCHITECTS_KEYFRAME_DIR / insp["design_reference_image_id"]
    if not p.exists():
        raise HTTPException(status_code=404, detail="Design reference missing on disk")
    mime = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png", "webp": "image/webp"}.get(
        p.suffix.lstrip(".").lower(), "image/jpeg"
    )
    return FileResponse(p, media_type=mime, headers={"Cache-Control": "public, max-age=86400"})


# ---------------- PDF export ----------------
PAID_ARCHITECTS_TIERS = {"architects_starter", "architects_pro", "architects_enterprise"}


def _build_inspection_pdf(insp: Dict[str, Any], findings: List[Dict[str, Any]]) -> bytes:
    """Render a polished one-page-ish PDF of the inspection report. Returns bytes."""
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.colors import HexColor, black, white
    from reportlab.lib.units import inch
    from reportlab.lib.enums import TA_LEFT
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        PageBreak, Image as RLImage,
    )
    import io

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=letter,
        leftMargin=0.6 * inch, rightMargin=0.6 * inch,
        topMargin=0.6 * inch, bottomMargin=0.6 * inch,
        title=f"Emaira Architects — {insp.get('title')}",
    )
    styles = getSampleStyleSheet()
    h1 = ParagraphStyle("h1", parent=styles["Heading1"], fontName="Helvetica-Bold",
                        textColor=HexColor("#0a0a0a"), fontSize=22, spaceAfter=4)
    sub = ParagraphStyle("sub", parent=styles["Normal"], fontName="Helvetica",
                         textColor=HexColor("#888"), fontSize=10, spaceAfter=10)
    body = ParagraphStyle("body", parent=styles["Normal"], fontSize=10, leading=14, alignment=TA_LEFT)
    small = ParagraphStyle("small", parent=styles["Normal"], fontSize=8.5, textColor=HexColor("#555"))
    sec = ParagraphStyle("sec", parent=styles["Heading3"], fontName="Helvetica-Bold",
                         textColor=HexColor("#B8860B"), fontSize=13, spaceBefore=12, spaceAfter=6)

    story = []
    # Brand strip
    brand_table = Table(
        [[Paragraph("<b>EMAIRA</b><font color='#B8860B'>.</font>ARCHITECTS", h1),
          Paragraph("Construction QC Inspection Report", sub)]],
        colWidths=[4.5 * inch, 3.0 * inch],
    )
    brand_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LINEBELOW", (0, 0), (-1, -1), 1.5, HexColor("#B8860B")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(brand_table)
    story.append(Spacer(1, 12))

    # Title block
    story.append(Paragraph(f"<b>{insp.get('title') or 'Untitled inspection'}</b>", h1))
    meta = [
        f"Inspection ID: {insp.get('inspection_id')}",
        f"Type: {(insp.get('inspection_type') or '').replace('_',' ').title()}",
        f"Risk: <b>{(insp.get('overall_risk_level') or 'n/a').upper()}</b>",
        f"AI: {insp.get('ai_model') or '—'}",
        f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
    ]
    story.append(Paragraph(" &nbsp;·&nbsp; ".join(meta), small))
    story.append(Spacer(1, 8))

    # Summary
    story.append(Paragraph("Executive Summary", sec))
    story.append(Paragraph(insp.get("overall_summary") or "No summary recorded.", body))

    # KPI strip
    counts = [
        ["Defects", str(insp.get("defects_count", 0))],
        ["Safety Violations", str(insp.get("safety_violations_count", 0))],
        ["Design Deviations", str(insp.get("design_deviations_count", 0))],
        ["Total Findings", str(len(findings))],
    ]
    kpi = Table([list(zip(*counts))[0], list(zip(*counts))[1]], colWidths=[1.7 * inch] * 4)
    kpi.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), HexColor("#0a0a0a")),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("FONTSIZE", (0, 1), (-1, 1), 22),
        ("FONTNAME", (0, 1), (-1, 1), "Helvetica-Bold"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
        ("TOPPADDING", (0, 0), (-1, 0), 6),
        ("BOTTOMPADDING", (0, 1), (-1, 1), 12),
        ("TOPPADDING", (0, 1), (-1, 1), 6),
        ("BACKGROUND", (0, 1), (-1, 1), HexColor("#f8f5ee")),
        ("TEXTCOLOR", (0, 1), (-1, 1), HexColor("#0a0a0a")),
    ]))
    story.append(Spacer(1, 8))
    story.append(kpi)
    story.append(Spacer(1, 8))

    # Keyframes (up to 4 across)
    kf_paths = sorted(ARCHITECTS_KEYFRAME_DIR.glob(f"{insp['inspection_id']}_f*.jpg"))[:4]
    if kf_paths:
        story.append(Paragraph("Keyframes", sec))
        imgs = []
        for kp in kf_paths:
            try:
                imgs.append(RLImage(str(kp), width=1.7 * inch, height=1.2 * inch))
            except Exception:
                pass
        if imgs:
            row = Table([imgs], colWidths=[1.8 * inch] * len(imgs))
            row.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 0, white)]))
            story.append(row)

    # Findings
    severity_color = {
        "low": HexColor("#1F8A4C"), "medium": HexColor("#C9A227"),
        "high": HexColor("#D17B23"), "critical": HexColor("#B23A3A"),
    }
    cat_label = {
        "defect": "DEFECT", "safety_violation": "SAFETY",
        "design_deviation": "DESIGN", "material_note": "NOTE",
    }
    story.append(Paragraph(f"Findings ({len(findings)})", sec))
    if not findings:
        story.append(Paragraph("No issues detected.", body))
    for f in findings:
        sev = (f.get("severity") or "medium").lower()
        cat = f.get("category") or "material_note"
        ts = f.get("timestamp_sec")
        ts_label = f"@ {ts:.1f}s" if isinstance(ts, (int, float)) else ""
        conf = f.get("confidence")
        conf_label = f"{round((conf or 0) * 100)}% conf" if conf is not None else ""
        head = (
            f'<font color="{severity_color.get(sev, black).hexval()}"><b>[{sev.upper()}]</b></font> '
            f'<font color="#666"><b>{cat_label.get(cat, cat.upper())}</b> · {f.get("type")}</font> '
            f'<font color="#999">{ts_label} {conf_label}</font>'
        )
        story.append(Paragraph(head, small))
        story.append(Paragraph(f.get("description") or "—", body))
        if f.get("recommendation"):
            story.append(Paragraph(
                f'<font color="#B8860B"><i>→ {f["recommendation"]}</i></font>', body
            ))
        if f.get("bbox_hint"):
            story.append(Paragraph(f'<font color="#888">Location: {f["bbox_hint"]}</font>', small))
        story.append(Spacer(1, 4))

    story.append(Spacer(1, 16))
    story.append(Paragraph(
        "Generated by Emaira Architects · Video AI QC/QA · emaira.art/architects",
        small,
    ))
    doc.build(story)
    return buf.getvalue()


@architects_router.get("/inspections/{inspection_id}/report.pdf")
async def export_architects_inspection_pdf(inspection_id: str, request: Request):
    user = await rt.require_auth(request)
    insp = await rt.db.architects_inspections.find_one(
        {"inspection_id": inspection_id, "user_id": user.user_id}, {"_id": 0}
    )
    if not insp:
        raise HTTPException(status_code=404, detail="Inspection not found")
    findings = await rt.db.architects_findings.find(
        {"inspection_id": inspection_id}, {"_id": 0}
    ).sort("timestamp_sec", 1).to_list(500)
    pdf_bytes = await asyncio.to_thread(_build_inspection_pdf, insp, findings)
    safe_title = re.sub(r"[^a-zA-Z0-9_-]+", "_", (insp.get("title") or inspection_id))[:40]
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="emaira_{safe_title}.pdf"'},
    )


# ---------------- Public share links (paid users only) ----------------
@architects_router.post("/inspections/{inspection_id}/share")
async def create_architects_share_link(inspection_id: str, request: Request):
    user = await rt.require_auth(request)
    if user.subscription_tier not in PAID_ARCHITECTS_TIERS:
        raise HTTPException(
            status_code=403,
            detail="Public share links are available on Architects Starter, Pro and Enterprise plans.",
        )
    insp = await rt.db.architects_inspections.find_one(
        {"inspection_id": inspection_id, "user_id": user.user_id}, {"_id": 0}
    )
    if not insp:
        raise HTTPException(status_code=404, detail="Inspection not found")
    if insp.get("status") != "completed":
        raise HTTPException(status_code=400, detail="Only completed inspections can be shared")

    # Reuse existing token for this inspection if present, else mint new one
    existing = await rt.db.architects_share_links.find_one(
        {"inspection_id": inspection_id, "user_id": user.user_id}, {"_id": 0}
    )
    if existing:
        return existing

    token = uuid.uuid4().hex
    record = {
        "share_id": f"shr_{uuid.uuid4().hex[:10]}",
        "token": token,
        "inspection_id": inspection_id,
        "user_id": user.user_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "view_count": 0,
    }
    await rt.db.architects_share_links.insert_one(record)
    record.pop("_id", None)
    return record


@architects_router.delete("/inspections/{inspection_id}/share")
async def revoke_architects_share_link(inspection_id: str, request: Request):
    user = await rt.require_auth(request)
    res = await rt.db.architects_share_links.delete_many(
        {"inspection_id": inspection_id, "user_id": user.user_id}
    )
    return {"revoked": res.deleted_count}


@architects_router.get("/share/{token}")
async def get_architects_shared_inspection(token: str):
    """PUBLIC endpoint — returns a redacted, read-only inspection report."""
    if not re.match(r"^[a-f0-9]{32}$", token):
        raise HTTPException(status_code=400, detail="Invalid token format")
    link = await rt.db.architects_share_links.find_one({"token": token}, {"_id": 0})
    if not link:
        raise HTTPException(status_code=404, detail="Share link not found or revoked")
    await rt.db.architects_share_links.update_one(
        {"token": token}, {"$inc": {"view_count": 1}}
    )
    insp = await rt.db.architects_inspections.find_one(
        {"inspection_id": link["inspection_id"]}, {"_id": 0}
    )
    if not insp or insp.get("status") != "completed":
        raise HTTPException(status_code=404, detail="Shared inspection not available")
    findings = await rt.db.architects_findings.find(
        {"inspection_id": link["inspection_id"]}, {"_id": 0}
    ).sort("timestamp_sec", 1).to_list(500)
    project = await rt.db.architects_projects.find_one(
        {"project_id": insp["project_id"]},
        {"_id": 0, "name": 1, "location": 1, "project_type": 1},
    )
    # Redact uploader's identity beyond their public org context
    insp.pop("user_id", None)
    insp["findings"] = findings
    insp["project"] = project
    insp["share_view_count"] = (link.get("view_count") or 0) + 1
    insp["video_url"] = f"/api/architects/share/{token}/video"
    insp["keyframes"] = [
        f"/api/architects/share/{token}/keyframe/{i}"
        for i in range(insp.get("keyframe_count", 0))
    ]
    if insp.get("design_reference_image_id"):
        insp["design_reference_url"] = f"/api/architects/share/{token}/design"
    return insp


@architects_router.get("/share/{token}/video")
async def stream_architects_shared_video(token: str):
    link = await rt.db.architects_share_links.find_one({"token": token}, {"_id": 0})
    if not link:
        raise HTTPException(status_code=404, detail="Share link not found")
    inspection_id = link["inspection_id"]
    seg = ARCHITECTS_VIDEO_DIR / f"{inspection_id}_segmented.mp4"
    if seg.exists():
        return FileResponse(seg, media_type="video/mp4")
    for ext in (".mp4", ".mov", ".m4v", ".webm"):
        p = ARCHITECTS_VIDEO_DIR / f"{inspection_id}{ext}"
        if p.exists():
            mime = {
                ".mp4": "video/mp4", ".mov": "video/quicktime",
                ".m4v": "video/mp4", ".webm": "video/webm",
            }[ext]
            return FileResponse(p, media_type=mime)
    # Cache miss — fetch s3_key from inspection doc and download
    insp = await rt.db.architects_inspections.find_one({"inspection_id": inspection_id}, {"_id": 0})
    stored_key = (insp or {}).get("s3_key") or (
        f"videos/{insp['user_id']}/{insp['video_filename']}" if insp and insp.get("video_filename") else None
    )
    if not stored_key:
        raise HTTPException(status_code=404, detail="Video missing")
    ext = Path(stored_key).suffix.lower() or ".mp4"
    local_path = ARCHITECTS_VIDEO_DIR / f"{inspection_id}{ext}"
    try:
        await asyncio.to_thread(_s3.download_file, S3_BUCKET, stored_key, str(local_path))
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Video not found in S3: {e}")
    mime = {".mp4": "video/mp4", ".mov": "video/quicktime", ".m4v": "video/mp4", ".webm": "video/webm"}.get(ext, "video/mp4")
    return FileResponse(local_path, media_type=mime)


@architects_router.get("/share/{token}/keyframe/{idx}")
async def get_architects_shared_keyframe(token: str, idx: int):
    link = await rt.db.architects_share_links.find_one({"token": token}, {"_id": 0})
    if not link:
        raise HTTPException(status_code=404, detail="Share link not found")
    inspection_id = link["inspection_id"]
    p = ARCHITECTS_KEYFRAME_DIR / f"{inspection_id}_f{idx}.jpg"
    if not p.exists():
        # Fetch user_id from inspection to build S3 key
        insp = await rt.db.architects_inspections.find_one({"inspection_id": inspection_id}, {"_id": 0, "user_id": 1})
        if not insp:
            raise HTTPException(status_code=404, detail="Keyframe not found")
        kf_s3_key = f"keyframes/{insp['user_id']}/{inspection_id}_f{idx}.jpg"
        try:
            await asyncio.to_thread(_s3.download_file, S3_BUCKET, kf_s3_key, str(p))
        except Exception:
            raise HTTPException(status_code=404, detail="Keyframe not found in S3")
    return FileResponse(p, media_type="image/jpeg",
                        headers={"Cache-Control": "public, max-age=86400"})


@architects_router.get("/share/{token}/design")
async def get_architects_shared_design(token: str):
    link = await rt.db.architects_share_links.find_one({"token": token}, {"_id": 0})
    if not link:
        raise HTTPException(status_code=404, detail="Share link not found")
    insp = await rt.db.architects_inspections.find_one(
        {"inspection_id": link["inspection_id"]}, {"_id": 0, "design_reference_image_id": 1}
    )
    if not insp or not insp.get("design_reference_image_id"):
        raise HTTPException(status_code=404, detail="No design reference")
    p = ARCHITECTS_KEYFRAME_DIR / insp["design_reference_image_id"]
    if not p.exists():
        raise HTTPException(status_code=404, detail="Design reference missing")
    mime = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png", "webp": "image/webp"}.get(
        p.suffix.lstrip(".").lower(), "image/jpeg"
    )
    return FileResponse(p, media_type=mime,
                        headers={"Cache-Control": "public, max-age=86400"})


@architects_router.get("/share/{token}/report.pdf")
async def export_architects_shared_pdf(token: str):
    link = await rt.db.architects_share_links.find_one({"token": token}, {"_id": 0})
    if not link:
        raise HTTPException(status_code=404, detail="Share link not found")
    insp = await rt.db.architects_inspections.find_one(
        {"inspection_id": link["inspection_id"]}, {"_id": 0}
    )
    if not insp:
        raise HTTPException(status_code=404, detail="Inspection not found")
    findings = await rt.db.architects_findings.find(
        {"inspection_id": link["inspection_id"]}, {"_id": 0}
    ).sort("timestamp_sec", 1).to_list(500)
    pdf_bytes = await asyncio.to_thread(_build_inspection_pdf, insp, findings)
    safe_title = re.sub(r"[^a-zA-Z0-9_-]+", "_", (insp.get("title") or "report"))[:40]
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="emaira_{safe_title}.pdf"'},
    )

