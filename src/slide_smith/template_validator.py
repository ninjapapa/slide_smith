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
        # Base (standard profile)
        "title": {"title": True},
        "section": {"title": True},
        "title_and_bullets": {"title": True, "bullets": True},
        "title_subtitle_and_bullets": {"title": True, "subtitle": True, "bullets": True},
        "text_with_image": {"title": True, "image": True, "body": True},

        # Legacy base alias (allowed but not required)
        "image_left_text_right": {"title": False, "image": False, "body": False},
    }

    if profile == "extended":
        required |= {
            # Legacy extended
            "two_col": {"title": True, "col1_body": True, "col2_body": True},
            "three_col": {"title": True, "col1_body": True, "col2_body": True, "col3_body": True},
            "four_col": {"title": True, "col1_body": True, "col2_body": True, "col3_body": True, "col4_body": True},
            "pillars_3": {"title": True, "pillar1_body": True, "pillar2_body": True, "pillar3_body": True},
            "pillars_4": {"title": True, "pillar1_body": True, "pillar2_body": True, "pillar3_body": True, "pillar4_body": True},
            "table": {"title": True, "table_text": True},
            "table_plus_description": {"title": True, "table_text": True, "body": True},
            "timeline_horizontal": {"title": True, "milestone1_body": True},

            # Redesign extended
            "title_subtitle": {"title": True, "subtitle": True},
            "version_page": {"title": True, "table_text": True},
            "agenda_with_image": {"title": True, "image": True, "bullets": True},
            "two_col_with_subtitle": {"title": True, "subtitle": True, "col1_body": True, "col2_body": True},
            "three_col_with_subtitle": {"title": True, "subtitle": True, "col1_body": True, "col2_body": True, "col3_body": True},
            "three_col_with_icons": {
                "title": True,
                "col1_title": True,
                "col1_body": True,
                "col1_icon": True,
                "col2_title": True,
                "col2_body": True,
                "col2_icon": True,
                "col3_title": True,
                "col3_body": True,
                "col3_icon": True,
            },
            "five_col_with_icons": {
                "title": True,
                "item1_icon": True,
                "item1_body": True,
                "item2_icon": True,
                "item2_body": True,
                "item3_icon": True,
                "item3_body": True,
                "item4_icon": True,
                "item4_body": True,
                "item5_icon": True,
                "item5_body": True,
            },
            "picture_compare": {
                "title": True,
                "left_image": True,
                "right_image": True,
                "left_body": True,
                "right_body": True,
            },
            "title_only_freeform": {"title": True},
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
            box = slot.get("box")
            if not isinstance(idx, int) and not isinstance(box, dict):
                errors.append(
                    f"{prefix}: archetype '{aid}' slot '{slot_name}' missing placeholder_idx (int) or box (object)"
                )

    return errors


def _validate_structural(archetypes: list[object], prs: Presentation, *, pptx_path: str) -> list[str]:
    errors: list[str] = []

    layout_names = {layout.name for layout in prs.slide_layouts}

    def layout_by_name(name: str):
        for layout in prs.slide_layouts:
            if layout.name == name:
                return layout
        return None

    # Raw OpenXML inventory (for part-based matching when names don't resolve)
    raw_by_part: dict[str, dict[str, Any]] = {}
    try:
        from slide_smith.openxml_layouts import inspect_openxml_layouts

        raw = inspect_openxml_layouts(pptx_path)
        for l in raw.layouts:
            part = l.get("part")
            if isinstance(part, str) and part:
                raw_by_part[part] = l
    except Exception:
        raw_by_part = {}

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

        layout_part = a.get("layout_part")
        if isinstance(layout_part, str) and layout_part.startswith("/"):
            layout_part = layout_part.lstrip("/")

        if layout_name not in layout_names:
            # Try part-based match using raw OpenXML inventory.
            if isinstance(layout_part, str) and layout_part in raw_by_part:
                # We'll validate placeholder_idx against raw placeholder idx set.
                raw_layout = raw_by_part[layout_part]
                raw_idxs = {
                    int(ph.get("idx"))
                    for ph in (raw_layout.get("placeholders") or [])
                    if isinstance(ph, dict) and isinstance(ph.get("idx"), int)
                }

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
                    if idx not in raw_idxs:
                        errors.append(
                            f"archetype '{aid}': layout_part '{layout_part}' missing placeholder idx={idx} for slot '{slot.get('name','?')}'"
                        )

                # If it's box-only, treat missing layout name as warning but still ok.
                if box_only:
                    errors.append(
                        f"warning: archetype '{aid}': slide layout name not found: '{layout_name}' (matched by layout_part)"
                    )
                continue

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

    # Template-native archetypes (optional). These are additional archetype definitions that
    # may be referenced directly by callers (namespaced IDs recommended), or used via
    # deck.native_preferred to select a richer layout while keeping a core slide archetype.
    native = spec.get("native") or {}
    native_archetypes = []
    if isinstance(native, dict):
        native_archetypes = native.get("archetypes") or []

    if native_archetypes and not isinstance(native_archetypes, list):
        return TemplateValidationResult(False, ["template spec 'native.archetypes' must be a list when present"])

    # Validate native_preferred mapping integrity (only when present).
    deck = spec.get("deck") or {}
    native_pref = deck.get("native_preferred")
    if native_pref is not None and not isinstance(native_pref, dict):
        return TemplateValidationResult(False, ["template spec 'deck.native_preferred' must be an object when present"])

    # Semantic checks can run without a pptx.
    if profile in {"standard", "extended"}:
        errors.extend(_validate_semantic(archetypes, profile))
        if errors:
            return TemplateValidationResult(False, errors)

    # Validate deck.native_preferred references.
    if isinstance(native_pref, dict):
        typed_core = [a for a in archetypes if isinstance(a, dict) and isinstance(a.get("id"), str)]
        typed_native = [a for a in native_archetypes if isinstance(a, dict) and isinstance(a.get("id"), str)]
        core_ids = {a["id"] for a in typed_core}
        native_ids = {a["id"] for a in typed_native}
        for core_id, preferred_id in native_pref.items():
            if not isinstance(core_id, str) or not isinstance(preferred_id, str):
                errors.append("deck.native_preferred: keys/values must be strings")
                continue
            if core_id not in core_ids:
                errors.append(f"deck.native_preferred: unknown core archetype id '{core_id}'")
            if preferred_id not in (core_ids | native_ids):
                errors.append(f"deck.native_preferred: preferred archetype id '{preferred_id}' not found in archetypes/native.archetypes")

        if errors and profile in {"standard", "extended"}:
            return TemplateValidationResult(False, errors)

    has_pptx = pptx_path.exists()
    if not has_pptx and profile == "structural":
        return TemplateValidationResult(
            ok=True,
            errors=[f"warning: template.pptx not found; skipping layout/placeholder checks: {pptx_path}"],
        )

    if has_pptx:
        prs = Presentation(str(pptx_path))
        errors.extend(_validate_structural(archetypes, prs, pptx_path=str(pptx_path)))
        if native_archetypes:
            errors.extend(_validate_structural(native_archetypes, prs, pptx_path=str(pptx_path)))

    fatal = [e for e in errors if not str(e).startswith("warning:")]
    return TemplateValidationResult(ok=(len(fatal) == 0), errors=errors)
