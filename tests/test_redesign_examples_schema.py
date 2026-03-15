from __future__ import annotations

import json
from pathlib import Path

from slide_smith.schema_validation import validate_against_schema


ROOT = Path(__file__).resolve().parents[1]


def test_schema_validation_accepts_redesign_base_example() -> None:
    sample = ROOT / "docs" / "examples" / "redesign" / "base.sample.json"
    spec = json.loads(sample.read_text())
    res = validate_against_schema(spec)
    assert res.ok, res.errors


def test_schema_validation_accepts_redesign_extended_example() -> None:
    sample = ROOT / "docs" / "examples" / "redesign" / "extended.sample.json"
    spec = json.loads(sample.read_text())
    res = validate_against_schema(spec)
    assert res.ok, res.errors
