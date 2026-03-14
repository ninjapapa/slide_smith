from __future__ import annotations

import json

from slide_smith.openxml_layouts import inspect_openxml_layouts
from slide_smith.pptx_inspector import inspect_pptx


def handle_inspect_pptx(*, pptx: str, fmt: str = "json", mode: str = "pptx") -> tuple[int, str]:
    mode = (mode or "pptx").strip().lower()
    if mode not in {"pptx", "raw"}:
        return 1, f"Invalid --mode: {mode} (expected pptx|raw)"

    if mode == "pptx":
        try:
            base = inspect_pptx(pptx)
        except Exception as exc:
            return 1, f"Inspect failed: {exc}"
        slide_size = base.slide_size
        layouts = base.layouts
    else:
        # raw mode should work for both pptx and potx without python-pptx
        from slide_smith.openxml_presentation import inspect_openxml_presentation

        pres = inspect_openxml_presentation(pptx)
        slide_size = pres.slide_size

        raw = inspect_openxml_layouts(pptx)
        # Normalize raw layouts into the inspect-pptx shape.
        layouts = []
        for i, l in enumerate(raw.layouts):
            placeholders = []
            for ph in l.get("placeholders") or []:
                placeholders.append(
                    {
                        "idx": int(ph.get("idx", -1)),
                        "name": "",
                        "ph_type": str(ph.get("type", "")),
                        "shape_type": "",
                        **({"bbox": ph.get("bbox")} if isinstance(ph.get("bbox"), dict) else {}),
                    }
                )
            layouts.append(
                {
                    "name": l.get("name", ""),
                    "index": i,
                    "part": l.get("part", ""),
                    "placeholders": placeholders,
                }
            )

    if fmt == "text":
        lines = [
            f"pptx: {pptx}",
            f"mode: {mode}",
            f"slide_size: {slide_size['width_emu']}x{slide_size['height_emu']} emu",
        ]
        for layout in layouts:
            lines.append(f"\nlayout[{layout.get('index','?')}]: {layout.get('name','')}")
            if layout.get("part"):
                lines.append(f"  part: {layout.get('part')}")
            for ph in layout.get("placeholders", []):
                lines.append(f"  - idx={ph['idx']} type={ph.get('ph_type','')} name={ph.get('name','')}")
        return 0, "\n".join(lines)

    return 0, json.dumps(
        {"pptx": pptx, "mode": mode, "slide_size": slide_size, "layouts": layouts},
        indent=2,
        sort_keys=True,
    )
