"""Retrieval of the most relevant resume chunks for a recruiter question."""

from app import config
from app.rag.vectorstore import get_collection


def retrieve_relevant_chunks(question: str, top_k: int | None = None) -> list[str]:
    """Return up to top_k resume chunks most relevant to the question."""
    collection = get_collection()
    if collection.count() == 0:
        return []

    k = top_k or config.TOP_K
    k = min(k, collection.count())

    results = collection.query(query_texts=[question], n_results=k)
    documents = results.get("documents") or [[]]
    return documents[0]
