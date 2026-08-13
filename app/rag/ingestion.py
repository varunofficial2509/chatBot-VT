"""Document ingestion pipeline: extract -> normalize -> chunk -> embed -> store."""

import hashlib
import json
import re
from pathlib import Path

import fitz  # PyMuPDF
from docx import Document as DocxDocument
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app import config
from app.rag.vectorstore import get_client

REQUIRED_PROFILE_FIELDS = ["name", "headline", "skills"]


class IngestionError(ValueError):
    """Raised when uploaded content fails validation."""


def extract_pdf_text(path: Path) -> str:
    with fitz.open(path) as doc:
        return "\n".join(page.get_text() for page in doc)


def extract_docx_text(path: Path) -> str:
    doc = DocxDocument(str(path))
    return "\n".join(p.text for p in doc.paragraphs)


def extract_resume_text(path: Path, filename: str) -> str:
    suffix = Path(filename).suffix.lower()
    if suffix == ".pdf":
        text = extract_pdf_text(path)
    elif suffix == ".docx":
        text = extract_docx_text(path)
    else:
        raise IngestionError(f"Unsupported resume file type: {suffix}")

    if not text.strip():
        raise IngestionError("Could not extract any text from the resume file.")
    return text


def normalize_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def chunk_text(text: str) -> list[str]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    return [c for c in splitter.split_text(text) if c.strip()]


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


def _chunk_id(source: str, index: int, content: str) -> str:
    digest = hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]
    return f"{source}-{index}-{digest}"


def rebuild_resume_collection(chunks: list[str], source_filename: str) -> int:
    """Replace the resume collection with fresh chunks. Avoids duplicate chunks on re-ingest."""
    client = get_client()
    try:
        client.delete_collection(name=config.CHROMA_COLLECTION)
    except ValueError:
        pass  # collection doesn't exist yet on first ingest

    from app.rag.embeddings import get_embedding_function

    collection = client.get_or_create_collection(
        name=config.CHROMA_COLLECTION,
        embedding_function=get_embedding_function(),
    )
    if not chunks:
        return 0

    ids = [_chunk_id(source_filename, i, c) for i, c in enumerate(chunks)]
    metadatas = [{"source": source_filename, "chunk_index": i} for i in range(len(chunks))]
    collection.add(documents=chunks, ids=ids, metadatas=metadatas)
    return len(chunks)


def save_profile(profile: dict) -> None:
    path = Path(config.PROFILE_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(profile, indent=2), encoding="utf-8")


def ingest(
    resume_path: Path | None,
    resume_filename: str | None,
    profile_raw: bytes | None,
) -> dict:
    """Run ingestion for whichever of resume/profile was provided, leaving the other untouched."""
    result: dict = {"status": "ok"}

    if profile_raw is not None:
        profile = parse_profile_json(profile_raw)
        save_profile(profile)
        result["profile_name"] = profile.get("name", "")

    if resume_path is not None:
        raw_text = extract_resume_text(resume_path, resume_filename)
        normalized = normalize_text(raw_text)
        chunks = chunk_text(normalized)
        if not chunks:
            raise IngestionError("Resume produced no usable content after processing.")

        result["resume_filename"] = resume_filename
        result["chunks_indexed"] = rebuild_resume_collection(chunks, resume_filename)

    return result
