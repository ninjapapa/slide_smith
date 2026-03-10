from __future__ import annotations


def test_validate_deck_spec_accepts_image_object() -> None:
    from slide_smith.deck_spec import validate_deck_spec

    spec = {
        "slides": [
            {
                "archetype": "image_left_text_right",
                "title": "T",
                "body": "B",
                "image": {"path": "a.png", "alt": "alt"},
            }
        ]
    }
    assert validate_deck_spec(spec) == []


def test_validate_deck_spec_rejects_bad_image_object() -> None:
    from slide_smith.deck_spec import validate_deck_spec

    spec = {
        "slides": [
            {
                "archetype": "image_left_text_right",
                "title": "T",
                "body": "B",
                "image": {"alt": 123},
            }
        ]
    }
    errors = validate_deck_spec(spec)
    assert any("$.slides[0].image.path" in e for e in errors)
    assert any("$.slides[0].image.alt" in e for e in errors)
