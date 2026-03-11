from __future__ import annotations

from slide_smith.hints import apply_hints_to_template_spec


def test_apply_hints_applies_slot_placeholder_idx_by_layout() -> None:
    spec = {
        "template_id": "t",
        "archetypes": [
            {
                "id": "two_col",
                "layout": "L1",
                "slots": [
                    {"name": "title", "type": "text", "required": True, "placeholder_idx": 0},
                    {"name": "col1_body", "type": "text", "required": True, "placeholder_idx": 10},
                    {"name": "col2_body", "type": "text", "required": True, "placeholder_idx": 11},
                ],
            }
        ],
    }

    hints = {
        "hints_version": 1,
        "layouts": {
            "L1": {
                "slot_hints": {
                    "col1_body": {"placeholder_idx": 20}
                }
            }
        },
    }

    out = apply_hints_to_template_spec(spec, hints)
    a = out["archetypes"][0]
    col1 = [s for s in a["slots"] if s["name"] == "col1_body"][0]
    assert col1["placeholder_idx"] == 20
    assert a.get("hinting", {}).get("applied") is True
