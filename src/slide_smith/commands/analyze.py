from __future__ import annotations

import json
from pathlib import Path

from slide_smith.reference_analyzer import analyze_reference


def handle_analyze(*, reference: str, out: str) -> tuple[int, str]:
    res = analyze_reference(reference)

    out_path = Path(out).expanduser().resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(res.style_profile, indent=2, sort_keys=True) + "\n")

    return 0, json.dumps({"style_profile": str(out_path)})
