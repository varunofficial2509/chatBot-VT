"""Ingestion orchestration: extract -> normalize -> chunk -> embed -> store.

Owns everything under data/knowledge/: saving newly uploaded files, listing
what's currently there, and (re)building the vector store + profile from
whatever files are on disk.
"""

import logging
from pathlib import Path

from src.config import settings
from src.ingestion.chunker import chunk_text
from src.ingestion.loader import extract_text
from src.ingestion.parser import IngestionError, normalize_text, parse_profile_json
from src.rag.vectorstore import get_vectorstore

logger = logging.getLogger("recruiter_bot.ingestion")


def list_knowledge_files() -> list[str]:
    if not settings.KNOWLEDGE_DIR.exists():
        return []
    return sorted(p.name for p in settings.KNOWLEDGE_DIR.iterdir() if p.is_file())


def save_uploaded_file(filename: str, raw_bytes: bytes) -> str:
    """Validate and persist an uploaded knowledge file. Returns the saved filename."""
    suffix = Path(filename).suffix.lower()
    if suffix not in settings.ALLOWED_KNOWLEDGE_EXTENSIONS:
        raise IngestionError(
            f"Unsupported file type '{suffix}'. Allowed: "
            f"{', '.join(sorted(settings.ALLOWED_KNOWLEDGE_EXTENSIONS))}"
        )
    if len(raw_bytes) == 0:
        raise IngestionError(f"{filename} is empty.")
    if len(raw_bytes) > settings.MAX_UPLOAD_SIZE_BYTES:
        raise IngestionError(f"{filename} is too large.")

    if suffix == ".json":
        parse_profile_json(raw_bytes)  # validate before writing
        target = Path(settings.PROFILE_PATH)
    else:
        target = settings.KNOWLEDGE_DIR / Path(filename).name

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(raw_bytes)
    return target.name


def rebuild_knowledge_base() -> dict:
    """Reprocess every file in data/knowledge/ into the vector store.

    JSON files are the structured profile (validated, left on disk as-is).
    PDF/Markdown files are extracted, normalized, chunked, and embedded.
    """
    settings.KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)
    files = [p for p in settings.KNOWLEDGE_DIR.iterdir() if p.is_file()]

    vectorstore = get_vectorstore()
    vectorstore.clear()

    chunks_indexed = 0
    documents_indexed = 0
    for path in sorted(files):
        suffix = path.suffix.lower()
        if suffix == ".json":
            parse_profile_json(path.read_bytes())  # surfaces validation errors
            continue
        if suffix not in {".pdf", ".md"}:
            continue

        text = extract_text(path)
        normalized = normalize_text(text)
        chunks = chunk_text(normalized)
        if not chunks:
            logger.warning("%s produced no usable content after processing", path.name)
            continue
        chunks_indexed += vectorstore.add_documents(chunks, source=path.name)
        documents_indexed += 1

    return {"documents_indexed": documents_indexed, "chunks_indexed": chunks_indexed}


def ensure_knowledge_base() -> None:
    """Build the vector store from disk on startup if it's empty but files exist."""
    if get_vectorstore().count() > 0:
        return
    if not list_knowledge_files():
        return
    rebuild_knowledge_base()
