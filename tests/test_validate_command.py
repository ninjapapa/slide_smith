from __future__ import annotations

import json
from pathlib import Path

from slide_smith.commands.validate import handle_validate


def test_validate_reports_slide_by_slide_fallbacks(tmp_path: Path) -> None:
    spec_path = tmp_path / "deck.json"
    spec_path.write_text(
        json.dumps(
            {
                "slides": [
                    {"layout_id": "title", "title": "Intro", "subtitle": "Sub"},
                    {"layout_id": "two_col", "title": "Compare", "col1_body": "L", "col2_body": "R"},
                ]
            }
        )
    )

    code, out = handle_validate(input_path=str(spec_path), template="default", templates_dir=None)
    assert code == 0

    payload = json.loads(out)
    assert payload["summary"]["total"] == 2
    assert payload["summary"]["ok"] == 1
    assert payload["summary"]["fallback"] == 1
    assert payload["slides"][0]["status"] == "ok"
    assert payload["slides"][1]["status"] == "fallback"
    assert payload["slides"][1]["fallback_layout_id"] == "title_and_bullets"


def test_validate_errors_when_slide_is_missing_layout_id(tmp_path: Path) -> None:
    spec_path = tmp_path / "deck.json"
    spec_path.write_text(json.dumps({"slides": [{"title": "No layout"}]}))

    code, out = handle_validate(input_path=str(spec_path), template="default", templates_dir=None)
    assert code == 1
    payload = json.loads(out)
    assert payload["summary"]["error"] == 1
    assert payload["slides"][0]["status"] == "error"
