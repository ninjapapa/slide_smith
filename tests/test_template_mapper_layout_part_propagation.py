from __future__ import annotations

from slide_smith.template_mapper import infer_standard_mappings


def test_infer_standard_mappings_propagates_layout_part() -> None:
    spec = {
        "version": "1.0",
        "deck": {},
        "styles": {},
        "archetypes": [
            {
                "id": "layout__x",
                "layout": "Some Layout",
                "layout_part": "ppt/slideLayouts/slideLayout12.xml",
                "slots": [
                    {"name": "title", "type": "text", "placeholder_idx": 0},
                    {"name": "body", "type": "bullets", "placeholder_idx": 1},
                ],
            }
        ],
    }

    out = infer_standard_mappings(spec)
    std = {a["id"]: a for a in out["archetypes"] if a.get("id") in {"title", "section", "title_and_bullets"}}
    assert "title" in std
    assert std["title"].get("layout_part") == "ppt/slideLayouts/slideLayout12.xml"
