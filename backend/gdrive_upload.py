"""Mirror inspection videos to Google Drive for ML training archive.

Runs asynchronously after the S3 upload completes so failures here never block
the inspection pipeline. Credentials come from env vars set in the ECS task:

- GDRIVE_SERVICE_ACCOUNT_JSON: full JSON content of the service account key
- GDRIVE_SHARED_DRIVE_ID: ID of the parent — either a true Shared Drive ID or a
  regular folder ID inside someone's My Drive. The service account must have at
  least Editor access on that folder/drive.

If either env var is missing, uploads are silently skipped (feature is opt-in).
"""

from __future__ import annotations

import io
import json
import logging
import os
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

_SCOPES = ["https://www.googleapis.com/auth/drive"]
_service = None
_folder_cache: dict[str, str] = {}


def _get_service():
    """Build (and cache) the Drive API client from the service account JSON."""
    global _service
    if _service is not None:
        return _service
    raw = os.getenv("GDRIVE_SERVICE_ACCOUNT_JSON")
    if not raw:
        return None
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        info = json.loads(raw)
        creds = service_account.Credentials.from_service_account_info(info, scopes=_SCOPES)
        _service = build("drive", "v3", credentials=creds, cache_discovery=False)
        return _service
    except Exception as exc:
        logger.warning("[gdrive] failed to build Drive service: %s", exc)
        return None


def _get_or_create_folder(svc, name: str, parent_id: str) -> Optional[str]:
    """Look up a folder by name under parent_id, creating it if missing.
    Works for both Shared Drive subfolders and regular My Drive folders."""
    cache_key = f"{parent_id}/{name}"
    if cache_key in _folder_cache:
        return _folder_cache[cache_key]
    safe_name = name.replace("'", "\\'")
    query = (
        f"name = '{safe_name}' "
        f"and mimeType = 'application/vnd.google-apps.folder' "
        f"and '{parent_id}' in parents and trashed = false"
    )
    resp = svc.files().list(
        q=query,
        corpora="allDrives",
        includeItemsFromAllDrives=True,
        supportsAllDrives=True,
        fields="files(id, name)",
        pageSize=1,
    ).execute()
    files = resp.get("files", [])
    if files:
        folder_id = files[0]["id"]
    else:
        created = svc.files().create(
            body={
                "name": name,
                "mimeType": "application/vnd.google-apps.folder",
                "parents": [parent_id],
            },
            supportsAllDrives=True,
            fields="id",
        ).execute()
        folder_id = created["id"]
    _folder_cache[cache_key] = folder_id
    return folder_id


def upload_video_sync(
    local_path: Path,
    *,
    user_label: str,
    project_label: str,
    filename: str,
    mime_type: str = "video/mp4",
) -> Optional[str]:
    """Upload a single file into <SharedDrive>/<user_label>/<project_label>/<filename>.

    Returns the Drive file ID, or None if Drive is not configured or the upload fails.
    Safe to call from a thread (asyncio.to_thread) — does blocking HTTP.
    """
    svc = _get_service()
    if svc is None:
        return None
    root_id = os.getenv("GDRIVE_SHARED_DRIVE_ID")
    if not root_id:
        return None
    try:
        from googleapiclient.http import MediaFileUpload

        user_folder = _get_or_create_folder(svc, user_label, root_id)
        if not user_folder:
            return None
        project_folder = _get_or_create_folder(svc, project_label, user_folder)
        if not project_folder:
            return None

        media = MediaFileUpload(str(local_path), mimetype=mime_type, resumable=True)
        created = svc.files().create(
            body={"name": filename, "parents": [project_folder]},
            media_body=media,
            supportsAllDrives=True,
            fields="id, webViewLink",
        ).execute()
        logger.info(
            "[gdrive] uploaded %s -> id=%s link=%s",
            filename, created.get("id"), created.get("webViewLink"),
        )
        return created.get("id")
    except Exception as exc:
        logger.warning("[gdrive] upload failed for %s: %s", filename, exc)
        return None
