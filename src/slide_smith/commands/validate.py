from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from slide_smith.deck_spec import load_deck_spec, normalize_deck_spec, validate_deck_spec
from slide_smith.markdown_parser import parse_markdown
from slide_smith.renderer import FALLBACK_LAYOUT_ID
from slide_smith.template_loader import load_template_spec


SUPPORTED_LAYOUT_IDS = {
    "title",
    "section",
    "title_and_bullets",
    "title_subtitle_and_bullets",
    "text_with_image",
    "version_page",
    "agenda_with_image",
    "two_col",
    "three_col_with_icons",
    "picture_compare",
}


REQUIRED_FIELDS: dict[str, tuple[str, ...]] = {
    "title": ("title",),
    "section": ("title",),
    "title_and_bullets": ("title",),
    "title_subtitle_and_bullets": ("title", "subtitle"),
    "text_with_image": ("title", "image"),
    "version_page": ("title", "table_text"),
    "agenda_with_image": ("title", "image", "items"),
    "two_col": ("title", "col1_body", "col2_body"),
    "three_col_with_icons": ("title", "items"),
    "picture_compare": ("title", "left", "right"),
}


def _load_spec(input_path: str) -> dict[str, Any]:
    if input_path.endswith(".json"):
        return load_deck_spec(input_path)
    if input_path.endswith(".md"):
        return parse_markdown(input_path)
    raise ValueError("Unsupported input type. Use .json or .md")


def _has_value(slide: dict[str, Any], field: str) -> bool:
    value = slide.get(field)
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, list):
        return len(value) > 0
    if isinstance(value, dict):
        return len(value) > 0
    return value is not None


def _template_slot_names(template_archetypes: dict[str, dict[str, Any]], layout_id: str) -> set[str]:
    spec = template_archetypes.get(layout_id) or {}
    slots = spec.get("slots") or []
    out: set[str] = set()
    if isinstance(slots, list):
        for s in slots:
            if isinstance(s, dict) and isinstance(s.get("name"), str):
                out.add(s["name"])
    return out


def _predict_slide_status(*, slide: dict[str, Any], index: int, template_archetypes: dict[str, dict[str, Any]]) -> dict[str, Any]:
    layout_id = slide.get("layout_id") or slide.get("archetype")
    if not isinstance(layout_id, str) or not layout_id:
        return {
            "slide_index": index,
            "status": "error",
            "requested_layout_id": None,
            "message": "slide is missing layout_id",
        }

    if layout_id not in SUPPORTED_LAYOUT_IDS:
        return {
            "slide_index": index,
            "status": "fallback",
            "requested_layout_id": layout_id,
            "fallback_layout_id": FALLBACK_LAYOUT_ID,
            "message": f"unsupported layout_id '{layout_id}'; would fall back to '{FALLBACK_LAYOUT_ID}'",
        }

    missing_fields = [f for f in REQUIRED_FIELDS.get(layout_id, ()) if not _has_value(slide, f)]
    if missing_fields:
        return {
            "slide_index": index,
            "status": "fallback",
            "requested_layout_id": layout_id,
            "fallback_layout_id": FALLBACK_LAYOUT_ID,
            "message": f"content does not satisfy layout contract; missing fields: {', '.join(missing_fields)}",
        }

    if layout_id not in template_archetypes:
        return {
            "slide_index": index,
            "status": "fallback",
            "requested_layout_id": layout_id,
            "fallback_layout_id": FALLBACK_LAYOUT_ID,
            "message": f"template does not define layout_id '{layout_id}'",
        }

    slots = _template_slot_names(template_archetypes, layout_id)
    if layout_id == "title" and "title" not in slots:
        return {
            "slide_index": index,
            "status": "fallback",
            "requested_layout_id": layout_id,
            "fallback_layout_id": FALLBACK_LAYOUT_ID,
            "message": "template is missing required slot 'title'",
        }
    if layout_id == "title_and_bullets" and not ({"title", "bullets"} <= slots):
        return {
            "slide_index": index,
            "status": "fallback",
            "requested_layout_id": layout_id,
            "fallback_layout_id": FALLBACK_LAYOUT_ID,
            "message": "template is missing required slots for title_and_bullets",
        }
    if layout_id == "text_with_image" and not ({"title", "body", "image"} <= slots):
        return {
            "slide_index": index,
            "status": "fallback",
            "requested_layout_id": layout_id,
            "fallback_layout_id": FALLBACK_LAYOUT_ID,
            "message": "template is missing required slots for text_with_image",
        }

    return {
        "slide_index": index,
        "status": "ok",
        "requested_layout_id": layout_id,
        "message": "renderable",
    }


def handle_validate(*, input_path: str, template: str, templates_dir: str | None) -> tuple[int, str]:
    try:
        spec = _load_spec(input_path)
    except ValueError as exc:
        return 1, str(exc)

    try:
        template_spec = load_template_spec(template, templates_dir=templates_dir)
    except FileNotFoundError as exc:
        return 1, f"Template validation failed: {exc}"

    spec, normalize_warnings = normalize_deck_spec(spec)
    lightweight_errors = validate_deck_spec(spec, profile="legacy")

    template_archetypes = {
        item["id"]: item
        for item in template_spec.get("archetypes", [])
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }

    slide_results = [
        _predict_slide_status(slide=slide, index=i, template_archetypes=template_archetypes)
        for i, slide in enumerate(spec.get("slides", []))
        if isinstance(slide, dict)
    ]

    hard_errors = [r for r in slide_results if r.get("status") == "error"]
    fallback_count = sum(1 for r in slide_results if r.get("status") == "fallback")

    out: dict[str, Any] = {
        "ok": len(hard_errors) == 0,
        "template": template,
        "slides": slide_results,
        "summary": {
            "total": len(slide_results),
            "ok": sum(1 for r in slide_results if r.get("status") == "ok"),
            "fallback": fallback_count,
            "error": len(hard_errors),
        },
    }
    if normalize_warnings:
        out["warnings"] = normalize_warnings
    if lightweight_errors:
        out.setdefault("warnings", []).extend(lightweight_errors)

    return (0 if len(hard_errors) == 0 else 1), json.dumps(out, indent=2)
