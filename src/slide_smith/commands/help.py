from __future__ import annotations

import json
from typing import Any

from slide_smith.commands.validate import FALLBACK_LAYOUT_ID, LAYOUT_API


def _text_api() -> str:
    lines: list[str] = []
    lines.append("Slide Smith layout_id API")
    lines.append("")
    lines.append(f"Fallback layout: {FALLBACK_LAYOUT_ID}")
    lines.append("")
    lines.append("Supported layout_id values:")
    for layout_id in sorted(LAYOUT_API):
        spec = LAYOUT_API[layout_id]
        lines.append(f"- {layout_id}")
        required = spec.get("required_fields") or []
        recommended = spec.get("recommended_fields") or []
        optional = spec.get("optional_fields") or []
        notes = spec.get("notes")
        lines.append(f"  required: {', '.join(required) if required else '-'}")
        if recommended:
            lines.append(f"  recommended: {', '.join(recommended)}")
        if optional:
            lines.append(f"  optional: {', '.join(optional)}")
        if isinstance(notes, str) and notes:
            lines.append(f"  notes: {notes}")
        lines.append("")
    lines.append("Top-level deck shape:")
    lines.append('{ "title": "Optional", "subtitle": "Optional", "slides": [{ "layout_id": "title", "title": "Example" }] }')
    return "\n".join(lines).rstrip() + "\n"


def handle_help(*, topic: str, fmt: str) -> tuple[int, str]:
    if topic != "api":
        return 1, f"Unsupported help topic '{topic}'"

    payload: dict[str, Any] = {
        "topic": "api",
        "fallback_layout_id": FALLBACK_LAYOUT_ID,
        "layout_ids": [
            {
                "layout_id": layout_id,
                **LAYOUT_API[layout_id],
            }
            for layout_id in sorted(LAYOUT_API)
        ],
        "deck_shape": {
            "title": "Optional deck title",
            "subtitle": "Optional deck subtitle",
            "slides": [{"layout_id": "title", "title": "Example"}],
        },
    }

    if fmt == "json":
        return 0, json.dumps(payload, indent=2)
    return 0, _text_api()
