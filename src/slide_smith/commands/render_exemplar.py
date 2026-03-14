from __future__ import annotations

import json
from pathlib import Path

from slide_smith.exemplar_renderer import render_exemplar


def handle_render_exemplar(
    *,
    reference: str,
    style_profile: str,
    deck_spec: str,
    out: str,
    assets_base_dir: str | None = None,
) -> tuple[int, str]:
    profile_obj = json.loads(Path(style_profile).expanduser().read_text(encoding="utf-8"))
    spec_obj = json.loads(Path(deck_spec).expanduser().read_text(encoding="utf-8"))

    res = render_exemplar(
        reference_pptx=reference,
        style_profile=profile_obj,
        deck_spec=spec_obj,
        output_pptx=out,
        assets_base_dir=assets_base_dir,
    )

    return 0, json.dumps({"pptx": res.output_pptx})
