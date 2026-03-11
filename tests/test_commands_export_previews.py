from __future__ import annotations

import json
from pathlib import Path

import pytest

from slide_smith.commands.export_previews import handle_export_previews


def test_handle_export_previews_errors_when_pptx_missing(tmp_path: Path) -> None:
    # Point at a templates dir without the template.
    code, out = handle_export_previews(template="missing", templates_dir=str(tmp_path), out_dir=str(tmp_path / "o"))
    assert code == 1
    payload = json.loads(out)
    assert payload["status"] == "error"


def test_handle_export_previews_ok_for_default_template(tmp_path: Path) -> None:
    import slide_smith

    repo_root = Path(slide_smith.__file__).resolve().parents[2]
    templates_dir = repo_root / "templates"

    code, out = handle_export_previews(template="default", templates_dir=str(templates_dir), out_dir=str(tmp_path / "o"))
    assert code == 0
    payload = json.loads(out)
    assert payload["status"] == "ok"
    manifest_path = Path(payload["manifest"])
    assert manifest_path.exists()
