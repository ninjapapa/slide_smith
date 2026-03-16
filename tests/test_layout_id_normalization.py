from __future__ import annotations

from slide_smith.deck_spec import normalize_deck_spec
from slide_smith.schema_validation import validate_against_schema


def test_normalize_deck_spec_preserves_layout_id_without_legacy_fields() -> None:
    spec = {
        "slides": [
            {"layout_id": "title_and_bullets", "title": "Highlights", "bullets": ["One", "Two"]}
        ]
    }

    out, warnings = normalize_deck_spec(spec)
    assert warnings == []
    assert out["slides"][0]["layout_id"] == "title_and_bullets"
    assert "archetype" not in out["slides"][0]


def test_schema_validation_accepts_layout_id_compatibility_shape() -> None:
    spec = {
        "slides": [
            {"layout_id": "title_and_bullets", "title": "Highlights", "bullets": ["One", "Two"]}
        ]
    }

    res = validate_against_schema(spec)
    assert res.ok, res.errors
