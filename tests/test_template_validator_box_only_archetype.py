from __future__ import annotations

import json
from pathlib import Path

from pptx import Presentation

from slide_smith.template_loader import template_dir
from slide_smith.template_validator import validate_template


def test_structural_validation_allows_box_only_archetype_when_layout_missing(tmp_path: Path) -> None:
    # Create a minimal template package on disk.
    templates_root = tmp_path / "templates"
    tdir = templates_root / "t1"
    tdir.mkdir(parents=True)

    # template.pptx with default layouts
    prs = Presentation()
    prs.save(tdir / "template.pptx")

    # template.json with a box-only archetype referencing a non-existent layout name.
    spec = {
        "version": "1.0",
        "meta": {"template": "t1"},
        "layouts": [
            {
                "id": "box_only",
                "layout": "THIS LAYOUT DOES NOT EXIST",
                "slots": [
                    {"name": "title", "box": {"x": 0.1, "y": 0.1, "w": 0.8, "h": 0.1, "units": "relative"}},
                    {"name": "body", "box": {"x": 0.1, "y": 0.3, "w": 0.8, "h": 0.5, "units": "relative"}},
                ],
            }
        ],
    }
    (tdir / "template.json").write_text(json.dumps(spec), encoding="utf-8")

    res = validate_template("t1", templates_dir=str(templates_root), profile="structural")
    assert res.ok, f"expected ok; got errors: {res.errors}"
    assert any(str(e).startswith("warning:") for e in res.errors)
