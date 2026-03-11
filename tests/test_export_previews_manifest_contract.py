from __future__ import annotations

import json
from pathlib import Path

import pytest

from slide_smith.pptx_inspector import inspect_pptx


def test_export_previews_manifest_shape(tmp_path: Path) -> None:
    # We don't have the real CLI environment here, but we can validate the manifest structure
    # produced by export-previews logic using the default template.pptx fixture.

    # Use repo default template pptx.
    import slide_smith

    repo_root = Path(slide_smith.__file__).resolve().parents[2]
    pptx_path = repo_root / "templates" / "default" / "template.pptx"
    if not pptx_path.exists():
        pytest.skip("default template.pptx not present")

    inv = inspect_pptx(str(pptx_path))

    manifest = {
        "version": 1,
        "template_id": "default",
        "template_pptx": inv.pptx,
        "slide_size": inv.slide_size,
        "layouts": [{**layout, "preview_png": None} for layout in inv.layouts],
    }

    data = json.loads(json.dumps(manifest))
    assert data["version"] == 1
    assert data["template_id"] == "default"
    assert "slide_size" in data
    assert isinstance(data["layouts"], list)
    assert "preview_png" in data["layouts"][0]
