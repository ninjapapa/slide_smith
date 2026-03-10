from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pptx import Presentation

from slide_smith.template_loader import load_template_spec, template_dir


@dataclass(frozen=True)
class TemplateValidationResult:
    ok: bool
    errors: list[str]


class TemplateValidationError(Exception):
    pass


def validate_template(template_id: str) -> TemplateValidationResult:
    errors: list[str] = []

    spec = load_template_spec(template_id)
    tdir = template_dir(template_id)
    pptx_path = tdir / "template.pptx"

    # Allow templates that are JSON-only (no pptx) for early-stage prototyping.
    if not pptx_path.exists():
        return TemplateValidationResult(
            ok=True,
            errors=[f"warning: template.pptx not found; skipping layout/placeholder checks: {pptx_path}"],
        )

    prs = Presentation(str(pptx_path))

    # Layout existence check.
    layout_names = {layout.name for layout in prs.slide_layouts}

    archetypes = spec.get("archetypes") or []
    if not isinstance(archetypes, list) or not archetypes:
        errors.append("template spec must include non-empty 'archetypes' list")
        return TemplateValidationResult(False, errors)

    def layout_by_name(name: str):
        for layout in prs.slide_layouts:
            if layout.name == name:
                return layout
        return None

    for a in archetypes:
        if not isinstance(a, dict):
            errors.append("archetypes[] must be objects")
            continue
        aid = a.get("id")
        layout_name = a.get("layout")
        if not isinstance(aid, str) or not aid:
            errors.append("archetype missing required 'id'")
            continue
        if not isinstance(layout_name, str) or not layout_name:
            errors.append(f"archetype '{aid}' missing required 'layout'")
            continue
        if layout_name not in layout_names:
            errors.append(f"archetype '{aid}': slide layout not found: '{layout_name}'")
            continue

        layout = layout_by_name(layout_name)
        if layout is None:
            # defensive
            errors.append(f"archetype '{aid}': slide layout not found: '{layout_name}'")
            continue

        # Placeholder indices exist check.
        for slot in a.get("slots") or []:
            if not isinstance(slot, dict):
                errors.append(f"archetype '{aid}': slot entries must be objects")
                continue
            if "placeholder_idx" not in slot:
                continue
            idx = slot.get("placeholder_idx")
            if not isinstance(idx, int):
                errors.append(f"archetype '{aid}': slot '{slot.get('name','?')}' placeholder_idx must be int")
                continue
            try:
                _ = layout.placeholders[idx]
            except KeyError:
                errors.append(
                    f"archetype '{aid}': layout '{layout_name}' missing placeholder idx={idx} for slot '{slot.get('name','?')}'"
                )

    return TemplateValidationResult(ok=(len(errors) == 0), errors=errors)
