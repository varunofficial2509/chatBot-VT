"""Loads the portfolio's presentation content (bio, projects, experience, skills).

Deliberately separate from app.rag.profile_store: that module feeds the
chatbot's grounding data (data/knowledge/profile.json), this one feeds the
Home/Projects pages (data/profile.json, projects.json, experience.json,
skills.json). Same underlying facts, different shape for a different job.
"""

import json
from pathlib import Path

from app import config as settings

CONTENT_DIR = settings.BASE_DIR / "data"


def _load_json(filename: str, default):
    path = CONTENT_DIR / filename
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return default


def load_profile() -> dict:
    return _load_json("profile.json", {})


def load_projects() -> list[dict]:
    return _load_json("projects.json", [])


def load_experience() -> list[dict]:
    return _load_json("experience.json", [])


def load_skills() -> list[str]:
    return _load_json("skills.json", [])


def resume_path() -> Path | None:
    """Path to a resume PDF in the knowledge base, if one has been uploaded."""
    candidates = sorted(settings.KNOWLEDGE_DIR.glob("*.pdf")) if settings.KNOWLEDGE_DIR.exists() else []
    return candidates[0] if candidates else None
