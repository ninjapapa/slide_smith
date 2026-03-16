from __future__ import annotations

from typing import Any


FALLBACK_LAYOUT_ID = "title_and_bullets"


def _fallback_text_lines(slide_spec: dict[str, Any]) -> list[str]:
    lines: list[str] = []

    def add(value: object) -> None:
        if isinstance(value, str) and value.strip():
            lines.append(value.strip())

    subtitle = slide_spec.get("subtitle")
    add(subtitle)

    body = slide_spec.get("body")
    add(body)

    for i in range(1, 6):
        add(slide_spec.get(f"col{i}_title"))
        add(slide_spec.get(f"col{i}_body"))
        add(slide_spec.get(f"pillar{i}_body"))
        add(slide_spec.get(f"item{i}_body"))

    bullets = slide_spec.get("bullets")
    if isinstance(bullets, list):
        for item in bullets:
            add(item)

    for key in ("left", "right"):
        side = slide_spec.get(key)
        if isinstance(side, dict):
            add(side.get("title"))
            add(side.get("body"))

    items = slide_spec.get("items")
    if isinstance(items, list):
        for item in items:
            if isinstance(item, dict):
                for key in ("marker", "title", "heading", "body", "caption", "label"):
                    add(item.get(key))

    for key in ("left_image", "right_image"):
        if key in slide_spec:
            add(f"[{key}: provided]")

    if not lines:
        lines.append("Content could not be rendered in the requested layout.")

    return lines


def _make_fallback_slide_spec(slide_spec: dict[str, Any], *, requested_layout_id: str, reason: str) -> dict[str, Any]:
    title = slide_spec.get("title")
    if not isinstance(title, str) or not title.strip():
        title = f"Fallback for {requested_layout_id}"

    bullets = _fallback_text_lines(slide_spec)
    out = dict(slide_spec)
    out["layout_id"] = FALLBACK_LAYOUT_ID
    out["title"] = title
    out["bullets"] = bullets
    out.pop("image", None)
    return out


def _record_render_warning(deck_spec: dict[str, Any], *, slide_index: int, requested_layout_id: str, reason: str) -> None:
    warnings = deck_spec.setdefault("render_warnings", [])
    if not isinstance(warnings, list):
        return
    warnings.append(
        {
            "slide_index": slide_index,
            "requested_layout_id": requested_layout_id,
            "fallback_layout_id": FALLBACK_LAYOUT_ID,
            "reason": reason,
            "status": "fallback",
        }
    )
