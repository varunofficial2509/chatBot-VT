"""Shared Chroma client/collection access."""

from functools import lru_cache

import chromadb
from chromadb.api.models.Collection import Collection

from app import config
from app.rag.embeddings import get_embedding_function


@lru_cache(maxsize=1)
def get_client() -> chromadb.ClientAPI:
    return chromadb.PersistentClient(path=config.CHROMA_PATH)


def get_collection() -> Collection:
    """Get (or lazily create) the resume chunk collection."""
    return get_client().get_or_create_collection(
        name=config.CHROMA_COLLECTION,
        embedding_function=get_embedding_function(),
    )


def collection_has_documents() -> bool:
    return get_collection().count() > 0
