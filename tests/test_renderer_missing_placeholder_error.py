from __future__ import annotations

from pathlib import Path

import pytest

from slide_smith.renderer import RenderingError, render_deck
from slide_smith.template_loader import load_template_spec


def test_render_deck_missing_placeholder_idx_is_actionable(tmp_path: Path) -> None:
    deck_spec = {
        "title": "Demo",
        "slides": [
            {"archetype": "title", "title": "Demo", "subtitle": "Sub"},
        ],
    }

    template_spec = load_template_spec("default")

    # Break the template mapping to point at a non-existent placeholder index.
    for a in template_spec.get("archetypes", []):
        if a.get("id") == "title":
            for s in a.get("slots", []):
                if s.get("name") == "title":
                    s["placeholder_idx"] = 999

    with pytest.raises(RenderingError) as excinfo:
        render_deck(deck_spec, template_spec, "default", str(tmp_path / "out.pptx"), base_dir=str(tmp_path))

    msg = str(excinfo.value)
    assert "idx=999" in msg
    assert "archetype=title" in msg
