from __future__ import annotations

import json
from pathlib import Path

from slide_smith.exemplar_validator import validate_exemplar


def handle_validate_exemplar(*, reference: str, pptx: str, style_profile: str, out: str | None) -> tuple[int, str]:
    profile_obj = json.loads(Path(style_profile).expanduser().read_text(encoding="utf-8"))

    res = validate_exemplar(reference_pptx=reference, pptx=pptx, style_profile=profile_obj)

    payload = json.dumps(res.report, indent=2, sort_keys=True) + "\n"

    if out:
        out_path = Path(out).expanduser().resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(payload, encoding="utf-8")
        return (0 if res.ok else 1), json.dumps({"ok": res.ok, "report": str(out_path)})

    return (0 if res.ok else 1), payload
