from __future__ import annotations

import json
from pathlib import Path

from slide_smith.template_validator import validate_template


def test_validate_template_extended_profile_missing_archetypes_is_not_ok(tmp_path: Path) -> None:
    # Create a JSON-only template that only has core standard archetypes.
    tdir = tmp_path / "templates" / "t1"
    tdir.mkdir(parents=True)
    spec = {
        "template_id": "t1",
        "name": "t1",
        "version": "0.1",
        "deck": {},
        "styles": {},
        "archetypes": [
            {"id": "title", "layout": "L", "slots": [{"name": "title", "type": "text", "required": True, "placeholder_idx": 0}]},
            {"id": "section", "layout": "L", "slots": [{"name": "title", "type": "text", "required": True, "placeholder_idx": 0}]},
            {
                "id": "title_and_bullets",
                "layout": "L",
                "slots": [
                    {"name": "title", "type": "text", "required": True, "placeholder_idx": 0},
                    {"name": "bullets", "type": "bullet_list", "required": True, "placeholder_idx": 1},
                ],
            },
            {
                "id": "image_left_text_right",
                "layout": "L",
                "slots": [
                    {"name": "title", "type": "text", "required": True, "placeholder_idx": 0},
                    {"name": "image", "type": "image", "required": True, "placeholder_idx": 1},
                    {"name": "body", "type": "text", "required": True, "placeholder_idx": 2},
                ],
            },
        ],
    }
    (tdir / "template.json").write_text(json.dumps(spec))

    res = validate_template("t1", templates_dir=str(tmp_path / "templates"), profile="extended")
    assert not res.ok
    assert any("missing required archetype" in e for e in res.errors)
