from __future__ import annotations

from slide_smith.deck_spec import normalize_deck_spec
from slide_smith.schema_validation import validate_against_schema


def test_normalize_deck_spec_preserves_layout_id_and_adds_internal_archetype() -> None:
    spec = {
        "slides": [
            {"layout_id": "title_and_bullets", "title": "Highlights", "bullets": ["One", "Two"]}
        ]
    }

    out, warnings = normalize_deck_spec(spec)
    assert warnings == []
    assert out["slides"][0]["layout_id"] == "title_and_bullets"
    assert out["slides"][0]["archetype"] == "title_and_bullets"


def test_normalize_deck_spec_deprecated_layout_id_updates_both_fields() -> None:
    spec = {
        "slides": [
            {"layout_id": "image_left_text_right", "title": "T", "body": "B", "image": "x.png"}
        ]
    }

    out, warnings = normalize_deck_spec(spec)
    assert len(warnings) == 1
    assert "layout_id" in warnings[0]
    assert out["slides"][0]["layout_id"] == "text_with_image"
    assert out["slides"][0]["archetype"] == "text_with_image"


def test_schema_validation_accepts_layout_id_compatibility_shape() -> None:
    spec = {
        "slides": [
            {"layout_id": "title_and_bullets", "title": "Highlights", "bullets": ["One", "Two"]}
        ]
    }

    res = validate_against_schema(spec)
    assert res.ok, res.errors
