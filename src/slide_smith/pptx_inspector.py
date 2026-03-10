from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pptx import Presentation


@dataclass(frozen=True)
class InspectPptxResult:
    pptx: str
    slide_size: dict[str, int]
    layouts: list[dict[str, Any]]


def _enum_name(value: Any) -> str:
    """Best-effort conversion of python-pptx enum-ish values into stable strings."""

    # Many python-pptx enums are `EnumValue` with `.name`.
    name = getattr(value, "name", None)
    if isinstance(name, str) and name:
        return name
    return str(value)


def inspect_pptx(pptx_path: str) -> InspectPptxResult:
    path = Path(pptx_path).expanduser()
    if not path.exists():
        raise FileNotFoundError(f"PPTX not found: {path}")
    if not path.is_file():
        raise FileNotFoundError(f"PPTX path is not a file: {path}")

    abs_path = str(path.resolve())
    prs = Presentation(abs_path)

    slide_size = {
        "width_emu": int(prs.slide_width),
        "height_emu": int(prs.slide_height),
    }

    layouts: list[dict[str, Any]] = []
    for idx, layout in enumerate(prs.slide_layouts):
        placeholders = []
        for ph in sorted(layout.placeholders, key=lambda p: int(p.placeholder_format.idx)):
            placeholders.append(
                {
                    "idx": int(ph.placeholder_format.idx),
                    "name": getattr(ph, "name", ""),
                    "ph_type": _enum_name(ph.placeholder_format.type),
                    "shape_type": _enum_name(getattr(ph, "shape_type", None)),
                }
            )

        layouts.append(
            {
                "name": layout.name,
                "index": idx,
                "placeholders": placeholders,
            }
        )

    return InspectPptxResult(pptx=abs_path, slide_size=slide_size, layouts=layouts)
