"""Text normalization and structured-profile JSON parsing/validation."""

import json
import re

REQUIRED_PROFILE_FIELDS = ["name", "headline", "skills"]


class IngestionError(ValueError):
    """Raised when uploaded content fails validation."""


def normalize_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def validate_profile(profile: dict) -> None:
    if not isinstance(profile, dict):
        raise IngestionError("Profile JSON must be an object.")
    missing = [f for f in REQUIRED_PROFILE_FIELDS if f not in profile]
    if missing:
        raise IngestionError(f"Profile JSON is missing required fields: {', '.join(missing)}")


def parse_profile_json(raw_bytes: bytes) -> dict:
    try:
        profile = json.loads(raw_bytes.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise IngestionError(f"Invalid JSON profile: {exc}") from exc
    validate_profile(profile)
    return profile
