from __future__ import annotations

import json

from slide_smith.pptx_inspector import inspect_pptx


def handle_inspect_pptx(*, pptx: str, fmt: str = "json") -> tuple[int, str]:
    try:
        res = inspect_pptx(pptx)
    except Exception as exc:
        return 1, f"Inspect failed: {exc}"

    if fmt == "text":
        lines = [
            f"pptx: {res.pptx}",
            f"slide_size: {res.slide_size['width_emu']}x{res.slide_size['height_emu']} emu",
        ]
        for layout in res.layouts:
            lines.append(f"\nlayout[{layout['index']}]: {layout['name']}")
            for ph in layout.get("placeholders", []):
                lines.append(f"  - idx={ph['idx']} type={ph['ph_type']} name={ph.get('name','')}")
        return 0, "\n".join(lines)

    return 0, json.dumps({"pptx": res.pptx, "slide_size": res.slide_size, "layouts": res.layouts}, indent=2, sort_keys=True)
