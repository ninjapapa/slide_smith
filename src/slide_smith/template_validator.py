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


def _validate_semantic(archetypes: list[object], profile: str) -> list[str]:
    errors: list[str] = []

    if profile not in {"standard", "extended"}:
        return errors

    required: dict[str, dict[str, bool]] = {
        "title": {"title": True},
        "section": {"title": True},
        "title_and_bullets": {"title": True, "bullets": True},
        "image_left_text_right": {"title": True, "image": True, "body": True},
    }

    if profile == "extended":
        required |= {
            "two_col": {"title": True, "col1_body": True, "col2_body": True},
            "three_col": {"title": True, "col1_body": True, "col2_body": True, "col3_body": True},
            "four_col": {"title": True, "col1_body": True, "col2_body": True, "col3_body": True, "col4_body": True},
            "pillars_3": {"title": True, "pillar1_body": True, "pillar2_body": True, "pillar3_body": True},
            "pillars_4": {"title": True, "pillar1_body": True, "pillar2_body": True, "pillar3_body": True, "pillar4_body": True},
            "table": {"title": True, "table_text": True},
            "table_plus_description": {"title": True, "table_text": True, "body": True},
            "timeline_horizontal": {"title": True, "milestone1_body": True},
        }

    typed_archetypes = [a for a in archetypes if isinstance(a, dict)]
    by_id = {a.get("id"): a for a in typed_archetypes}

    prefix = f"{profile} profile"
    for aid, req_slots in required.items():
        if aid not in by_id:
            errors.append(f"{prefix}: missing required archetype '{aid}'")
            continue
        a = by_id[aid]
        slots = a.get("slots") or []
        if not isinstance(slots, list):
            errors.append(f"{prefix}: archetype '{aid}' slots must be a list")
            continue
        slot_by_name = {s.get("name"): s for s in slots if isinstance(s, dict)}
        for slot_name, must in req_slots.items():
            if not must:
                continue
            if slot_name not in slot_by_name:
                errors.append(f"{prefix}: archetype '{aid}' missing required slot '{slot_name}'")
                continue
            slot = slot_by_name[slot_name]
            idx = slot.get("placeholder_idx")
            if not isinstance(idx, int):
                errors.append(f"{prefix}: archetype '{aid}' slot '{slot_name}' missing int placeholder_idx")

    return errors


def _validate_structural(archetypes: list[object], prs: Presentation) -> list[str]:
    errors: list[str] = []

    layout_names = {layout.name for layout in prs.slide_layouts}

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
        # Box-only archetypes (slide-instance-derived) may not require a resolvable layout.
        slots = a.get("slots") or []
        box_only = False
        if isinstance(slots, list) and slots:
            typed_slots = [s for s in slots if isinstance(s, dict)]
            if typed_slots and all(("placeholder_idx" not in s) and isinstance(s.get("box"), dict) for s in typed_slots):
                box_only = True

        if not isinstance(layout_name, str) or not layout_name:
            if box_only:
                errors.append(f"warning: archetype '{aid}' missing layout (box-only archetype; skipping layout checks)")
                continue
            errors.append(f"archetype '{aid}' missing required 'layout'")
            continue

        if layout_name not in layout_names:
            if box_only:
                errors.append(
                    f"warning: archetype '{aid}': slide layout not found: '{layout_name}' (box-only archetype; skipping layout checks)"
                )
                continue
            errors.append(f"archetype '{aid}': slide layout not found: '{layout_name}'")
            continue

        layout = layout_by_name(layout_name)
        if layout is None:
            if box_only:
                errors.append(
                    f"warning: archetype '{aid}': slide layout not found: '{layout_name}' (box-only archetype; skipping layout checks)"
                )
                continue
            errors.append(f"archetype '{aid}': slide layout not found: '{layout_name}'")
            continue

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
            found = False
            for ph in layout.placeholders:
                try:
                    if int(ph.placeholder_format.idx) == idx:
                        found = True
                        break
                except Exception:
                    continue
            if not found:
                errors.append(
                    f"archetype '{aid}': layout '{layout_name}' missing placeholder idx={idx} for slot '{slot.get('name','?')}'"
                )

    return errors


def validate_template(
    template_id: str,
    templates_dir: str | None = None,
    profile: str = "structural",
) -> TemplateValidationResult:
    errors: list[str] = []

    spec = load_template_spec(template_id, templates_dir=templates_dir)
    tdir = template_dir(template_id, templates_dir=templates_dir)
    pptx_path = tdir / "template.pptx"

    if profile not in {"structural", "standard", "extended"}:
        raise TemplateValidationError(f"Unknown validation profile: {profile}")

    archetypes = spec.get("archetypes") or []
    if not isinstance(archetypes, list) or not archetypes:
        return TemplateValidationResult(False, ["template spec must include non-empty 'archetypes' list"])

    # Semantic checks can run without a pptx.
    if profile in {"standard", "extended"}:
        errors.extend(_validate_semantic(archetypes, profile))
        if errors:
            return TemplateValidationResult(False, errors)

    has_pptx = pptx_path.exists()
    if not has_pptx and profile == "structural":
        return TemplateValidationResult(
            ok=True,
            errors=[f"warning: template.pptx not found; skipping layout/placeholder checks: {pptx_path}"],
        )

    if has_pptx:
        prs = Presentation(str(pptx_path))
        errors.extend(_validate_structural(archetypes, prs))

    fatal = [e for e in errors if not str(e).startswith("warning:")]
    return TemplateValidationResult(ok=(len(fatal) == 0), errors=errors)
