from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from pptx.dml.color import RGBColor
from pptx.util import Pt


@dataclass(frozen=True)
class TextStyle:
    font: str | None = None
    size_pt: int | float | None = None
    color_hex: str | None = None  # e.g. "112233"


def _parse_style(obj: dict[str, Any] | None) -> TextStyle:
    if not obj:
        return TextStyle()
    return TextStyle(
        font=obj.get("font"),
        size_pt=obj.get("size_pt"),
        color_hex=obj.get("color_hex"),
    )


def load_styles(template_spec: dict[str, Any]) -> dict[str, TextStyle]:
    styles = template_spec.get("styles") or {}
    return {
        "title": _parse_style(styles.get("title")),
        "subtitle": _parse_style(styles.get("subtitle")),
        "body": _parse_style(styles.get("body")),
        "bullets": _parse_style(styles.get("bullets")),
    }


def apply_text_style(text_frame, style: TextStyle) -> None:
    """Best-effort style application across all paragraphs/runs."""
    for paragraph in text_frame.paragraphs:
        # Ensure at least one run exists in common cases.
        runs = list(paragraph.runs)
        if not runs and paragraph.text:
            # paragraph.text should already create a run, but keep defensive.
            _ = paragraph.add_run()
            runs = list(paragraph.runs)

        for run in runs:
            font = run.font
            if style.font:
                font.name = style.font
            if style.size_pt is not None:
                font.size = Pt(style.size_pt)
            if style.color_hex:
                font.color.rgb = RGBColor.from_string(style.color_hex.upper())
