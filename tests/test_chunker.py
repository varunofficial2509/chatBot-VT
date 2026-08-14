from app.rag.ingestion import chunk_text


def test_chunk_text_splits_long_text():
    text = "Sentence one. " * 200
    chunks = chunk_text(text)
    assert len(chunks) > 1
    assert all(chunk.strip() for chunk in chunks)


def test_chunk_text_returns_single_chunk_for_short_text():
    chunks = chunk_text("Short text.")
    assert chunks == ["Short text."]


def test_chunk_text_handles_empty_input():
    assert chunk_text("") == []
