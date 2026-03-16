from __future__ import annotations

import json
from pathlib import Path

from slide_smith.schema_validation import validate_against_schema


ROOT = Path(__file__).resolve().parents[1]


def test_schema_validation_accepts_sample_fixture() -> None:
    sample = ROOT / "docs" / "examples" / "redesign" / "base.sample.json"
    spec = json.loads(sample.read_text())
    res = validate_against_schema(spec)
    assert res.ok


def test_schema_validation_rejects_missing_required() -> None:
    spec = {"slides": [{"archetype": "image_left_text_right", "title": "T"}]}
    res = validate_against_schema(spec)
    assert not res.ok
    # should mention missing required fields
    assert any("image" in e or "body" in e for e in res.errors)
