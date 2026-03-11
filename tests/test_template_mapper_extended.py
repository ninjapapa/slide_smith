from __future__ import annotations

from slide_smith.template_mapper_extended import infer_extended_mappings


def test_infer_extended_mappings_adds_supported_archetypes() -> None:
    # Minimal bootstrapped-like spec: one layout__* archetype with title + 4 bodies.
    spec = {
        "template_id": "t",
        "deck": {},
        "archetypes": [
            {
                "id": "layout__four_cols",
                "layout": "Four Cols",
                "slots": [
                    {"name": "title", "type": "text", "placeholder_idx": 0},
                    {"name": "body", "type": "bullets", "placeholder_idx": 10},
                    {"name": "body_2", "type": "bullets", "placeholder_idx": 11},
                    {"name": "body_3", "type": "bullets", "placeholder_idx": 12},
                    {"name": "body_4", "type": "bullets", "placeholder_idx": 13},
                ],
            }
        ],
    }

    out = infer_extended_mappings(spec)
    ids = {a["id"] for a in out.get("archetypes", [])}
    assert "two_col" in ids
    assert "three_col" in ids
    assert "four_col" in ids

    supported = set(out.get("deck", {}).get("supported_archetypes", []))
    assert "four_col" in supported
