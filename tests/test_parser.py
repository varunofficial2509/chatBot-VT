import json

import pytest

from src.ingestion.parser import IngestionError, normalize_text, parse_profile_json, validate_profile


def test_validate_profile_accepts_required_fields():
    validate_profile({"name": "A", "headline": "B", "skills": ["C"]})


def test_validate_profile_rejects_missing_fields():
    with pytest.raises(IngestionError):
        validate_profile({"name": "A"})


def test_parse_profile_json_rejects_invalid_json():
    with pytest.raises(IngestionError):
        parse_profile_json(b"not json")


def test_parse_profile_json_returns_dict():
    raw = json.dumps({"name": "A", "headline": "B", "skills": ["C"]}).encode("utf-8")
    assert parse_profile_json(raw)["name"] == "A"


def test_normalize_text_collapses_whitespace_and_blank_lines():
    result = normalize_text("Hello   world\r\n\r\n\r\nNext line")
    assert result == "Hello world\n\nNext line"
