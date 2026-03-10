from __future__ import annotations


def test_validate_deck_spec_reports_paths() -> None:
    from slide_smith.deck_spec import validate_deck_spec

    spec = {
        "slides": [
            {"archetype": "image_left_text_right", "title": "", "body": 123},
        ]
    }
    errors = validate_deck_spec(spec)
    assert any("$.slides[0].title" in e for e in errors)
    assert any("$.slides[0].body" in e for e in errors)
    assert any("$.slides[0].image" in e for e in errors)
