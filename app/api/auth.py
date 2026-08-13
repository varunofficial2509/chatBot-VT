"""Minimal signed-token auth for the admin ingestion endpoint.

No third-party auth framework — a single shared ADMIN_PASSWORD gates a
short-lived HMAC-signed token. This is intentionally simple: there is
exactly one admin (the candidate), not a multi-user system.
"""

import base64
import hashlib
import hmac
import json
import time

from fastapi import Header, HTTPException

from app import config

TOKEN_TTL_SECONDS = 60 * 60  # 1 hour


def _secret() -> bytes:
    if not config.ADMIN_PASSWORD:
        raise RuntimeError("ADMIN_PASSWORD is not set")
    return config.ADMIN_PASSWORD.encode("utf-8")


def _b64encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")


def _b64decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def create_token() -> str:
    payload = json.dumps({"exp": int(time.time()) + TOKEN_TTL_SECONDS}).encode("utf-8")
    payload_b64 = _b64encode(payload)
    signature = hmac.new(_secret(), payload_b64.encode("utf-8"), hashlib.sha256).digest()
    return f"{payload_b64}.{_b64encode(signature)}"


def verify_token(token: str) -> bool:
    try:
        payload_b64, signature_b64 = token.split(".", 1)
        expected_signature = hmac.new(
            _secret(), payload_b64.encode("utf-8"), hashlib.sha256
        ).digest()
        if not hmac.compare_digest(expected_signature, _b64decode(signature_b64)):
            return False
        payload = json.loads(_b64decode(payload_b64))
        return int(payload.get("exp", 0)) >= int(time.time())
    except (ValueError, KeyError, json.JSONDecodeError):
        return False


def require_admin(authorization: str = Header(default="")) -> None:
    """FastAPI dependency: raises 401 unless a valid Bearer token is supplied."""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing admin token")
    token = authorization.removeprefix("Bearer ").strip()
    if not verify_token(token):
        raise HTTPException(status_code=401, detail="Invalid or expired admin token")
