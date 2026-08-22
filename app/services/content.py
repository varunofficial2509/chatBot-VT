"""Loads the portfolio's presentation content (bio, projects, experience, skills).

Deliberately separate from app.rag.profile_store: that module feeds the
chatbot's grounding data (data/knowledge/profile.json), this one feeds the
Home/Projects pages (data/profile.json, projects.json, experience.json,
skills.json). Same underlying facts, different shape for a different job.
"""

import json
import re
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


def load_skills() -> dict[str, list[str]]:
    return _load_json("skills.json", {})


def mentioned_technologies(description: str, skills: dict[str, list[str]]) -> list[str]:
    """Skills from the master list that are literally named in this text,
    in the order they appear. Never adds anything the description doesn't
    already say — used to surface a "technologies" line on experience
    cards without duplicating that list by hand in experience.json.
    """
    flat = [skill for group in skills.values() for skill in group]
    matches = []
    for skill in flat:
        pattern = r"\b" + re.escape(skill) + r"\b"
        found = re.search(pattern, description, re.IGNORECASE)
        if found:
            matches.append((found.start(), skill))
    matches.sort(key=lambda pair: pair[0])
    return [skill for _, skill in matches]


def resume_path() -> Path | None:
    """Path to a resume PDF in the knowledge base, if one has been uploaded."""
    candidates = sorted(settings.KNOWLEDGE_DIR.glob("*.pdf")) if settings.KNOWLEDGE_DIR.exists() else []
    return candidates[0] if candidates else None
