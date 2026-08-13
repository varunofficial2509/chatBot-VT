"""Text extraction for supported knowledge file types (PDF, Markdown)."""

from pathlib import Path

import fitz  # PyMuPDF


class UnsupportedFileType(ValueError):
    """Raised when a file extension isn't one of the supported knowledge types."""


def extract_pdf_text(path: Path) -> str:
    with fitz.open(path) as doc:
        return "\n".join(page.get_text() for page in doc)


def extract_markdown_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def extract_text(path: Path) -> str:
    """Extract raw text from a PDF or Markdown file on disk."""
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return extract_pdf_text(path)
    if suffix == ".md":
        return extract_markdown_text(path)
    raise UnsupportedFileType(f"Unsupported knowledge file type: {suffix}")
