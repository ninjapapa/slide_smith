from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class HelpRequest:
    help_request_version: int
    template_id: str
    template_pptx: str
    missing_archetypes: list[str]
    layouts: list[dict[str, Any]]
    next_actions: list[dict[str, Any]]


def build_help_request(*, template_id: str, template_pptx: Path, layouts: list[dict[str, Any]], missing: list[str]) -> dict[str, Any]:
    return {
        "help_request_version": 1,
        "template_id": template_id,
        "template_pptx": str(template_pptx),
        "missing_archetypes": missing,
        "layouts": layouts,
        "next_actions": [
            {
                "action": "export_previews",
                "command": f"slide-smith export-previews --template {template_id} --out-dir /tmp/{template_id}-previews --mode layouts",
            },
            {"action": "provide_hints", "hint_schema": "v1"},
        ],
    }


def load_hints(path: str | None) -> dict[str, Any] | None:
    if not path:
        return None
    p = Path(path).expanduser()
    return json.loads(p.read_text())


def apply_hints_to_template_spec(updated_spec: dict[str, Any], hints: dict[str, Any] | None) -> dict[str, Any]:
    """Apply caller-provided hints to an already-inferred template spec.

    v1.1 behavior is conservative:

    - Hints can attach to a layout name and suggest a standard archetype.
    - Hints can provide slot_hints placeholder_idx values.

    We only apply slot_hints to archetypes that already exist in `updated_spec`.
    """

    if not hints:
        return updated_spec

    out = dict(updated_spec)
    archetypes = [a for a in (out.get("archetypes") or []) if isinstance(a, dict)]
    by_id = {a.get("id"): a for a in archetypes if isinstance(a.get("id"), str)}

    layouts = hints.get("layouts") if isinstance(hints, dict) else None
    if not isinstance(layouts, dict):
        return out

    # For each layout, apply slot hints to archetypes that currently reference that layout.
    for layout_name, hint in layouts.items():
        if not isinstance(layout_name, str) or not isinstance(hint, dict):
            continue
        slot_hints = hint.get("slot_hints")
        if not isinstance(slot_hints, dict):
            continue

        for a in archetypes:
            if a.get("layout") != layout_name:
                continue
            for slot_name, slot_hint in slot_hints.items():
                if not isinstance(slot_hint, dict):
                    continue
                idx = slot_hint.get("placeholder_idx")
                if not isinstance(idx, int):
                    continue
                for s in a.get("slots") or []:
                    if isinstance(s, dict) and s.get("name") == slot_name:
                        s["placeholder_idx"] = idx

            # Mark that hints were applied.
            a.setdefault("hinting", {})
            if isinstance(a["hinting"], dict):
                a["hinting"]["applied"] = True

    out["archetypes"] = archetypes
    return out
