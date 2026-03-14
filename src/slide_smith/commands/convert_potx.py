from __future__ import annotations

import json
from pathlib import Path

from slide_smith.potx_converter import convert_potx_to_pptx


def handle_convert_potx(*, potx: str, out: str, overwrite: bool = False) -> tuple[int, str]:
    res = convert_potx_to_pptx(potx_path=potx, pptx_path=out, overwrite=overwrite)
    return 0, json.dumps({"pptx": str(Path(res.output_path))})
