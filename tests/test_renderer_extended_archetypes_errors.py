from __future__ import annotations

from pathlib import Path

import pytest

from slide_smith.renderer import RenderingError, render_deck


def test_render_deck_extended_archetype_requires_template_support(tmp_path: Path) -> None:
    deck_spec = {
        "title": "Demo",
        "slides": [
            {"archetype": "two_col", "title": "Two", "col1_body": "L", "col2_body": "R"},
        ],
    }

    # Template spec intentionally does not include two_col.
    template_spec = {
        "template_id": "t",
        "archetypes": [
            {"id": "title", "layout": "Title Slide", "slots": [{"name": "title", "type": "text", "placeholder_idx": 0}]}
        ],
        "styles": {},
    }

    with pytest.raises(RenderingError) as excinfo:
        render_deck(deck_spec, template_spec, "default", str(tmp_path / "out.pptx"), base_dir=str(tmp_path))

    assert "not supported" in str(excinfo.value)
