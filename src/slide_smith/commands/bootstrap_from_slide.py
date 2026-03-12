from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from slide_smith.slide_instance_bootstrapper import BootstrapFromSlideError, bootstrap_archetype_from_slide


def handle_bootstrap_from_slide(
    *,
    pptx: str,
    slide_number: int,
    template_id: str,
    out_dir: str,
    archetype: str,
    write: bool,
) -> tuple[int, str]:
    """Bootstrap a new template package from a specific slide instance.

    MVP behavior:
    - copies the provided pptx as template.pptx
    - creates/prints a template.json containing exactly one archetype based on box geometry

    If write=false, prints the template.json payload instead.
    """

    try:
        boot = bootstrap_archetype_from_slide(pptx, slide_number=slide_number, archetype_id=archetype)
    except BootstrapFromSlideError as exc:
        return 1, f"bootstrap-from-slide failed: {exc}"

    out_root = Path(out_dir).expanduser().resolve()
    tdir = out_root / template_id

    template_spec: dict[str, Any] = {
        "template_id": template_id,
        "name": f"{template_id} (bootstrapped)",
        "version": "0.1",
        "deck": {
            "aspect_ratio": "unknown",
            "supported_archetypes": [archetype],
        },
        "archetypes": [boot.archetype_spec],
        "styles": {},
    }

    if not write:
        return 0, json.dumps(template_spec, indent=2, sort_keys=True)

    tdir.mkdir(parents=True, exist_ok=True)
    pptx_out = tdir / "template.pptx"
    shutil.copyfile(boot.pptx, pptx_out)

    json_out = tdir / "template.json"
    json_out.write_text(json.dumps(template_spec, indent=2, sort_keys=True) + "\n")

    return 0, json.dumps(
        {
            "status": "bootstrapped",
            "template_dir": str(tdir),
            "template_pptx": str(pptx_out),
            "template_json": str(json_out),
            "archetype": archetype,
            "slide_number": slide_number,
        },
        indent=2,
        sort_keys=True,
    )
