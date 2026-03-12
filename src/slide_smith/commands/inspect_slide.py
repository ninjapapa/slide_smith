from __future__ import annotations

import json

from slide_smith.pptx_inspector import inspect_slide


def handle_inspect_slide(*, pptx: str, slide_number: int, fmt: str = "json") -> tuple[int, str]:
    try:
        res = inspect_slide(pptx, slide_number=slide_number)
    except Exception as exc:
        return 1, f"inspect-slide failed: {exc}"

    payload = {
        "pptx": res.pptx,
        "slide_number": res.slide_number,
        "slide_size": res.slide_size,
        "shapes": res.shapes,
    }

    if fmt == "text":
        lines = [
            f"pptx: {payload['pptx']}",
            f"slide_number: {payload['slide_number']}",
            f"slide_size: {payload['slide_size']['width_emu']} x {payload['slide_size']['height_emu']} emu",
        ]
        for s in payload["shapes"]:
            bbox = s.get("bbox_emu") or {}
            norm = s.get("bbox_rel") or {}
            lines.append(
                f"- z={s.get('z')} type={s.get('shape_type')} name={s.get('name','')} "
                f"bbox_emu=({bbox.get('left')},{bbox.get('top')},{bbox.get('width')},{bbox.get('height')}) "
                f"bbox_rel=({norm.get('x'):.3f},{norm.get('y'):.3f},{norm.get('w'):.3f},{norm.get('h'):.3f})"
                if all(isinstance(norm.get(k), (int, float)) for k in ['x','y','w','h'])
                else f"- z={s.get('z')} type={s.get('shape_type')} name={s.get('name','')} bbox_emu=({bbox.get('left')},{bbox.get('top')},{bbox.get('width')},{bbox.get('height')})"
            )
            if s.get("text"):
                lines.append(f"  text: {s['text']}")
            if s.get("placeholder"):
                ph = s["placeholder"]
                lines.append(f"  placeholder: idx={ph.get('idx')} type={ph.get('ph_type')} name={ph.get('name','')}")
        return 0, "\n".join(lines)

    return 0, json.dumps(payload, indent=2, sort_keys=True)
