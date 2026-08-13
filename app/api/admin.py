"""Owner-only endpoints: admin login and knowledge-base ingestion."""

import logging
import tempfile
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel

from app import config
from app.api.auth import create_token, require_admin
from app.rag.ingestion import IngestionError, ingest

logger = logging.getLogger("recruiter_bot.admin")
router = APIRouter()


class LoginRequest(BaseModel):
    password: str


class LoginResponse(BaseModel):
    token: str


@router.post("/api/admin/login", response_model=LoginResponse)
def login(request: LoginRequest) -> LoginResponse:
    if not config.ADMIN_PASSWORD:
        raise HTTPException(status_code=500, detail="Admin login is not configured on the server")
    if request.password != config.ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Incorrect password")
    return LoginResponse(token=create_token())


def _validate_upload(file: UploadFile, allowed_extensions: set[str]) -> str:
    filename = Path(file.filename or "").name  # strip any directory components
    suffix = Path(filename).suffix.lower()
    if suffix not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{suffix}'. Allowed: {', '.join(sorted(allowed_extensions))}",
        )
    return filename


@router.post("/api/admin/ingest", dependencies=[Depends(require_admin)])
async def ingest_documents(
    resume: UploadFile | None = File(None),
    profile_json: UploadFile | None = File(None),
):
    if resume is None and profile_json is None:
        raise HTTPException(status_code=400, detail="Upload a resume, a profile JSON, or both.")

    resume_filename: str | None = None
    resume_bytes: bytes | None = None
    if resume is not None:
        resume_filename = _validate_upload(resume, config.ALLOWED_RESUME_EXTENSIONS)
        resume_bytes = await resume.read()
        if len(resume_bytes) > config.MAX_UPLOAD_SIZE_BYTES:
            raise HTTPException(status_code=400, detail="resume file is too large")
        if len(resume_bytes) == 0:
            raise HTTPException(status_code=400, detail="resume file is empty")

    profile_bytes: bytes | None = None
    if profile_json is not None:
        _validate_upload(profile_json, {".json"})
        profile_bytes = await profile_json.read()
        if len(profile_bytes) > config.MAX_UPLOAD_SIZE_BYTES:
            raise HTTPException(status_code=400, detail="profile JSON file is too large")
        if len(profile_bytes) == 0:
            raise HTTPException(status_code=400, detail="profile JSON file is empty")

    # Resume bytes only ever touch disk as a delete-on-close temp file, purely so
    # PyMuPDF/python-docx can open it by path; nothing is persisted beyond ingestion.
    tmp = None
    try:
        if resume_bytes is not None:
            tmp = tempfile.NamedTemporaryFile(suffix=Path(resume_filename).suffix, delete=True)
            tmp.write(resume_bytes)
            tmp.flush()

        status = ingest(
            Path(tmp.name) if tmp is not None else None,
            resume_filename,
            profile_bytes,
        )
    except IngestionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception:
        logger.exception("Ingestion failed")
        raise HTTPException(status_code=500, detail="Ingestion failed unexpectedly") from None
    finally:
        if tmp is not None:
            tmp.close()

    return status
