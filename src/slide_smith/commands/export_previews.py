from __future__ import annotations

import json
from pathlib import Path

from slide_smith.pptx_inspector import inspect_pptx
from slide_smith.template_loader import template_dir


def handle_export_previews(*, template: str, templates_dir: str | None, out_dir: str, mode: str = "layouts") -> tuple[int, str]:
    tdir = template_dir(template, templates_dir=templates_dir)
    pptx_path = tdir / "template.pptx"
    if not pptx_path.exists():
        return 1, json.dumps(
            {"template": template, "status": "error", "error": f"template.pptx not found: {pptx_path}"},
            indent=2,
        )

    out_path = Path(out_dir).expanduser().resolve()
    out_path.mkdir(parents=True, exist_ok=True)

    inv = inspect_pptx(str(pptx_path))

    manifest = {
        "version": 1,
        "template_id": template,
        "template_pptx": inv.pptx,
        "slide_size": inv.slide_size,
        "mode": mode,
        "layouts": [{**layout, "preview_png": None} for layout in inv.layouts],
    }

    manifest_path = out_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")

    return 0, json.dumps({"template": template, "status": "ok", "manifest": str(manifest_path)}, indent=2)
