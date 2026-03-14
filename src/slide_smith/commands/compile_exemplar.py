from __future__ import annotations

import json
from pathlib import Path

from slide_smith.exemplar_compiler import compile_exemplar


def handle_compile_exemplar(*, plan: str, style_profile: str, out: str) -> tuple[int, str]:
    plan_obj = json.loads(Path(plan).expanduser().read_text(encoding="utf-8"))
    profile_obj = json.loads(Path(style_profile).expanduser().read_text(encoding="utf-8"))

    res = compile_exemplar(slide_plan=plan_obj, style_profile=profile_obj)

    out_path = Path(out).expanduser().resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(res.deck_spec, indent=2, sort_keys=True) + "\n")

    return 0, json.dumps({"deck_spec": str(out_path)})
