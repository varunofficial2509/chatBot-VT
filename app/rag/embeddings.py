"""Embedding function used for both ingestion and retrieval."""

from functools import lru_cache

import chromadb.utils.embedding_functions as embedding_functions
from chromadb.api.types import Documents, Embeddings

from app import config


class _GeminiEmbeddingFunction(embedding_functions.EmbeddingFunction):
    """Adapts langchain's Gemini embeddings to Chroma's EmbeddingFunction protocol."""

    def __init__(self, model: str, api_key: str):
        from langchain_google_genai import GoogleGenerativeAIEmbeddings

        self._embeddings = GoogleGenerativeAIEmbeddings(model=model, google_api_key=api_key)

    def __call__(self, input: Documents) -> Embeddings:
        return self._embeddings.embed_documents(list(input))


@lru_cache(maxsize=1)
def get_embedding_function() -> embedding_functions.EmbeddingFunction:
    """Return the configured embedding function (local Sentence Transformers or Gemini)."""
    if config.EMBEDDING_PROVIDER == "gemini":
        if not config.GOOGLE_API_KEY:
            raise RuntimeError("GOOGLE_API_KEY is not set")
        return _GeminiEmbeddingFunction(
            model=config.EMBEDDING_MODEL, api_key=config.GOOGLE_API_KEY
        )

    return embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=config.EMBEDDING_MODEL
    )
