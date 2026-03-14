from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pptx import Presentation

from slide_smith.openxml_layouts import inspect_openxml_layouts


class LayoutResolveError(Exception):
    pass


@dataclass(frozen=True)
class ResolvedLayout:
    layout: Any
    index: int
    name: str
    part: str | None


def _layout_part(layout: Any) -> str | None:
    try:
        p = str(layout.part.partname)  # type: ignore[attr-defined]
        return p.lstrip("/")
    except Exception:
        return None


def resolve_layout(
    *,
    prs: Presentation,
    layout_name: str | None = None,
    layout_part: str | None = None,
) -> ResolvedLayout:
    """Resolve a slide layout from a Presentation.

    Prefer `layout_part` when provided (more stable than names), otherwise use `layout_name`.

    `layout_part` should be like: `ppt/slideLayouts/slideLayout12.xml`.
    """

    if isinstance(layout_part, str) and layout_part.startswith("/"):
        layout_part = layout_part.lstrip("/")

    # 1) part-based lookup using python-pptx layout.part.partname
    if isinstance(layout_part, str) and layout_part:
        for idx, layout in enumerate(prs.slide_layouts):
            lp = _layout_part(layout)
            if lp == layout_part:
                return ResolvedLayout(layout=layout, index=idx, name=getattr(layout, "name", ""), part=lp)

        # If not found, provide a helpful error including known parts.
        known = []
        for idx, layout in enumerate(prs.slide_layouts):
            known.append({"index": idx, "name": getattr(layout, "name", ""), "part": _layout_part(layout)})
        raise LayoutResolveError(
            f"Slide layout part not found in template presentation: {layout_part}. "
            f"Known layouts: {known}"
        )

    # 2) name-based lookup
    if isinstance(layout_name, str) and layout_name:
        for idx, layout in enumerate(prs.slide_layouts):
            if getattr(layout, "name", None) == layout_name:
                return ResolvedLayout(layout=layout, index=idx, name=layout_name, part=_layout_part(layout))
        raise LayoutResolveError(f"Slide layout name not found in template presentation: {layout_name}")

    raise LayoutResolveError("Must provide layout_name or layout_part")
