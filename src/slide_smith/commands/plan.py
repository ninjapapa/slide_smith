from __future__ import annotations

import json
from pathlib import Path

from slide_smith.slide_plan import plan_from_markdown


def handle_plan(*, input_path: str, out: str) -> tuple[int, str]:
    res = plan_from_markdown(input_path)

    out_path = Path(out).expanduser().resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(res.slide_plan, indent=2, sort_keys=True) + "\n")

    return 0, json.dumps({"slide_plan": str(out_path)})
