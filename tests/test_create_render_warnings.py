from __future__ import annotations

import json
from pathlib import Path

from slide_smith.commands.create import handle_create


def test_handle_create_surfaces_render_fallback_warnings(tmp_path: Path) -> None:
    spec_path = tmp_path / "deck.json"
    spec_path.write_text(
        json.dumps(
            {
                "slides": [
                    {"layout_id": "two_col", "title": "Two", "col1_body": "L", "col2_body": "R"}
                ]
            }
        )
    )

    code, out = handle_create(
        input_path=str(spec_path),
        template="default",
        output=str(tmp_path / "out.pptx"),
        assets_dir=None,
        print_mode="none",
        templates_dir=None,
    )

    assert code == 0
    payload = json.loads(out)
    assert payload["output"].endswith("out.pptx")
    assert isinstance(payload.get("warnings"), list)
    assert any(isinstance(w, dict) and w.get("status") == "fallback" for w in payload["warnings"])
