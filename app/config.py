"""Environment-based configuration. No secrets or personal data live here."""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# LLM provider
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "anthropic")
LLM_MODEL = os.getenv("LLM_MODEL", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")

# LangSmith / LangChain tracing (picked up automatically by langchain if set)
LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2", "false")
LANGCHAIN_PROJECT = os.getenv("LANGCHAIN_PROJECT", "personal-recruiter-chatbot")

# Admin auth
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")

# RAG / vector store
CHROMA_PATH = os.getenv("CHROMA_PATH", str(BASE_DIR / "data" / "chroma"))
CHROMA_COLLECTION = os.getenv("CHROMA_COLLECTION", "resume")
EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "local")
EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "gemini-embedding-001" if EMBEDDING_PROVIDER == "gemini" else "all-MiniLM-L6-v2",
)
TOP_K = int(os.getenv("TOP_K", "5"))
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "800"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "100"))

# Profile storage
PROFILE_PATH = os.getenv("PROFILE_PATH", str(BASE_DIR / "data" / "profile.json"))

# Upload limits
MAX_UPLOAD_SIZE_BYTES = int(os.getenv("MAX_UPLOAD_SIZE_BYTES", str(10 * 1024 * 1024)))
ALLOWED_RESUME_EXTENSIONS = {".pdf", ".docx"}
