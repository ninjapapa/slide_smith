from __future__ import annotations

import json
from pathlib import Path
from typing import Any


# NOTE: This list should track what the renderer supports.
# v1.0 core + v1.1 extended (renderer supports both).
SUPPORTED_ARCHETYPES = {
    # v1.0 core
    "title",
    "section",
    "title_and_bullets",
    "image_left_text_right",
    "text_with_image",

    # v1.1 extended
    "two_col",
    "three_col",
    "four_col",
    "pillars_3",
    "pillars_4",
    "table",
    "table_plus_description",
    "timeline_horizontal",
}


# Backward-compatible archetype aliases. This enables additive evolution of
# archetype names without breaking existing deck specs.
ARCHETYPE_ALIASES: dict[str, str] = {
    # prefer semantic naming vs geometry-bound naming
    "image_left_text_right": "text_with_image",
    # legacy v1 naming
    "title_and_bullets_with_subtitle": "title_subtitle_and_bullets",
}


def normalize_deck_spec(spec: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    """Normalize a deck spec in a backwards-compatible way.

    Returns: (normalized_spec, warnings)

    This currently:
    - maps legacy archetype ids to their modern equivalents

    NOTE: This function is intentionally conservative: it avoids mutating other
    fields so callers can reason about what changed.
    """

    if not isinstance(spec, dict):
        return spec, []

    slides = spec.get("slides")
    if not isinstance(slides, list):
        return spec, []

    warnings: list[str] = []
    out = dict(spec)
    out_slides: list[Any] = []

    for i, slide in enumerate(slides):
        if not isinstance(slide, dict):
            out_slides.append(slide)
            continue

        archetype = slide.get("archetype")
        if isinstance(archetype, str) and archetype in ARCHETYPE_ALIASES:
            new_id = ARCHETYPE_ALIASES[archetype]
            warnings.append(f"$.slides[{i}].archetype: '{archetype}' is deprecated; use '{new_id}'")
            slide2 = dict(slide)
            slide2["archetype"] = new_id
            out_slides.append(slide2)
        else:
            out_slides.append(slide)

    out["slides"] = out_slides
    return out, warnings


def load_deck_spec(path: str) -> dict[str, Any]:
    file_path = Path(path)
    return json.loads(file_path.read_text())


def _path(*parts: str) -> str:
    # JSON-pointer-ish for humans.
    return "$." + ".".join(parts)



def validate_deck_spec(spec: dict[str, Any], *, profile: str = "legacy") -> list[str]:
    """Lightweight validation with human-friendly error paths.

    This intentionally does not depend on jsonschema.

    Profiles:
    - legacy: v1.0 core + v1.1 extended archetypes (current renderer support)
    - core_v2: enables proposed v2 families (message/multi_col/image_text/list_visual/metrics)

    The goal is to let new archetype families iterate without immediately freezing a full schema.
    """

    errors: list[str] = []

    slides = spec.get("slides")
    if not isinstance(slides, list) or not slides:
        return [f"{_path('slides')}: must be a non-empty array"]

    allowed = set(SUPPORTED_ARCHETYPES)

    # New archetypes (additive evolution). These are not yet part of the
    # renderer's full coverage, but we allow validation to proceed so templates
    # and agents can iterate.
    allowed |= {
        "text_with_image",
        "title_subtitle_and_bullets",
        "title_subtitle",
        "version_page",
        "agenda_with_image",
        "two_col_with_subtitle",
        "three_col_with_subtitle",
        "three_col_with_icons",
        "five_col_with_icons",
        "picture_compare",
        "title_only_freeform",
        # allow legacy aliases so validation doesn't fail before normalization
        "title_and_bullets_with_subtitle",
    }

    if profile == "core_v2":
        allowed |= {"message", "multi_col", "image_text", "list_visual", "metrics"}

    for idx, slide in enumerate(slides):
        sp = f"slides[{idx}]"
        if not isinstance(slide, dict):
            errors.append(f"{_path(sp)}: must be an object")
            continue

        archetype = slide.get("archetype")
        if not isinstance(archetype, str):
            errors.append(f"{_path(sp, 'archetype')}: must be a string")
            continue
        if archetype not in allowed:
            errors.append(f"{_path(sp, 'archetype')}: must be one of: {', '.join(sorted(allowed))}")
            continue

        # Common fields
        if "notes" in slide and not isinstance(slide.get("notes"), str):
            errors.append(f"{_path(sp, 'notes')}: must be a string")

        def req_str(field: str) -> None:
            if not isinstance(slide.get(field), str) or not slide.get(field):
                errors.append(f"{_path(sp, field)}: required non-empty string")

        if archetype in {
            "title",
            "section",
            "title_and_bullets",
            "image_left_text_right",
            # v1.1 extended
            "two_col",
            "three_col",
            "four_col",
            "pillars_3",
            "pillars_4",
            "table",
            "table_plus_description",
            "timeline_horizontal",
            # v2 families
            "message",
            "multi_col",
            "image_text",
            "list_visual",
            "metrics",
        }:
            req_str("title")

        if archetype == "title":
            if "subtitle" in slide and slide.get("subtitle") is not None and not isinstance(slide.get("subtitle"), str):
                errors.append(f"{_path(sp, 'subtitle')}: must be a string")

        elif archetype == "section":
            # Accept subtitle/body as optional strings.
            for f in ("subtitle", "body"):
                if f in slide and slide.get(f) is not None and not isinstance(slide.get(f), str):
                    errors.append(f"{_path(sp, f)}: must be a string")

        elif archetype == "title_and_bullets":
            bullets = slide.get("bullets")
            body = slide.get("body")
            if bullets is None and body is None:
                errors.append(f"{_path(sp)}: must provide either 'bullets' or 'body'")
            if bullets is not None:
                if not isinstance(bullets, list):
                    errors.append(f"{_path(sp, 'bullets')}: must be an array of strings")
                else:
                    for j, b in enumerate(bullets):
                        if not isinstance(b, str):
                            errors.append(f"{_path(sp, f'bullets[{j}]')}: must be a string")
            if body is not None and not isinstance(body, str):
                errors.append(f"{_path(sp, 'body')}: must be a string")

        elif archetype in {"image_left_text_right", "text_with_image"}:
            req_str("body")
            image = slide.get("image")
            if isinstance(image, str):
                if not image:
                    errors.append(f"{_path(sp, 'image')}: required non-empty string")
            elif isinstance(image, dict):
                ip = image.get("path")
                if not isinstance(ip, str) or not ip:
                    errors.append(f"{_path(sp, 'image.path')}: required non-empty string")
                alt = image.get("alt")
                if alt is not None and not isinstance(alt, str):
                    errors.append(f"{_path(sp, 'image.alt')}: must be a string")
            else:
                errors.append(f"{_path(sp, 'image')}: must be a string or an object")

        elif archetype in {"two_col", "three_col", "four_col"}:
            n = {"two_col": 2, "three_col": 3, "four_col": 4}[archetype]
            for i in range(1, n + 1):
                f = f"col{i}_body"
                if not isinstance(slide.get(f), str) or not slide.get(f):
                    errors.append(f"{_path(sp, f)}: required non-empty string")

        elif archetype in {"pillars_3", "pillars_4"}:
            n = 3 if archetype == "pillars_3" else 4
            for i in range(1, n + 1):
                f = f"pillar{i}_body"
                if not isinstance(slide.get(f), str) or not slide.get(f):
                    errors.append(f"{_path(sp, f)}: required non-empty string")

        elif archetype == "table":
            if not isinstance(slide.get("table_text"), str) or not slide.get("table_text"):
                errors.append(f"{_path(sp, 'table_text')}: required non-empty string")

        elif archetype == "table_plus_description":
            if not isinstance(slide.get("table_text"), str) or not slide.get("table_text"):
                errors.append(f"{_path(sp, 'table_text')}: required non-empty string")
            if not isinstance(slide.get("body"), str) or not slide.get("body"):
                errors.append(f"{_path(sp, 'body')}: required non-empty string")

        elif archetype == "timeline_horizontal":
            # milestoneN_body are optional, but must be strings when present.
            for i in range(1, 11):
                f = f"milestone{i}_body"
                if f in slide and slide.get(f) is not None and not isinstance(slide.get(f), str):
                    errors.append(f"{_path(sp, f)}: must be a string")

        # --- v2 profiles ---

        elif archetype == "message":
            body = slide.get("body")
            quote = slide.get("quote")
            if body is None and quote is None:
                errors.append(f"{_path(sp)}: must provide either 'body' or 'quote'")
            for f in ("body", "quote", "attribution"):
                if f in slide and slide.get(f) is not None and not isinstance(slide.get(f), str):
                    errors.append(f"{_path(sp, f)}: must be a string")

        elif archetype == "multi_col":
            items = slide.get("items")
            if items is None:
                errors.append(f"{_path(sp, 'items')}: required for multi_col")
            elif not isinstance(items, list) or not items:
                errors.append(f"{_path(sp, 'items')}: must be a non-empty array")
            else:
                for j, it in enumerate(items):
                    if not isinstance(it, dict):
                        errors.append(f"{_path(sp, f'items[{j}]')}: must be an object")
                        continue
                    if not isinstance(it.get("body"), str) or not it.get("body"):
                        errors.append(f"{_path(sp, f'items[{j}].body')}: required non-empty string")
                    for k in ("heading", "label", "number"):
                        if k in it and it.get(k) is not None and not isinstance(it.get(k), str):
                            errors.append(f"{_path(sp, f'items[{j}].{k}')}: must be a string")

        elif archetype == "image_text":
            req_str("body")
            image = slide.get("image")
            if isinstance(image, str):
                if not image:
                    errors.append(f"{_path(sp, 'image')}: required non-empty string")
            elif isinstance(image, dict):
                ip = image.get("path")
                if not isinstance(ip, str) or not ip:
                    errors.append(f"{_path(sp, 'image.path')}: required non-empty string")
                alt = image.get("alt")
                if alt is not None and not isinstance(alt, str):
                    errors.append(f"{_path(sp, 'image.alt')}: must be a string")
            else:
                errors.append(f"{_path(sp, 'image')}: must be a string or an object")

            params = slide.get("params")
            if params is not None and not isinstance(params, dict):
                errors.append(f"{_path(sp, 'params')}: must be an object")
            if isinstance(params, dict) and "image_side" in params:
                v = params.get("image_side")
                if v not in {"left", "right"}:
                    errors.append(f"{_path(sp, 'params.image_side')}: must be 'left' or 'right'")

        elif archetype == "list_visual":
            items = slide.get("items")
            if items is None:
                errors.append(f"{_path(sp, 'items')}: required for list_visual")
            elif not isinstance(items, list) or not items:
                errors.append(f"{_path(sp, 'items')}: must be a non-empty array")
            else:
                for j, it in enumerate(items):
                    if not isinstance(it, dict):
                        errors.append(f"{_path(sp, f'items[{j}]')}: must be an object")
                        continue
                    if not isinstance(it.get("body"), str) or not it.get("body"):
                        errors.append(f"{_path(sp, f'items[{j}].body')}: required non-empty string")
                    for k in ("label", "number"):
                        if k in it and it.get(k) is not None and not isinstance(it.get(k), str):
                            errors.append(f"{_path(sp, f'items[{j}].{k}')}: must be a string")

        elif archetype == "metrics":
            ms = slide.get("metrics")
            if ms is None:
                errors.append(f"{_path(sp, 'metrics')}: required for metrics")
            elif not isinstance(ms, list) or not ms:
                errors.append(f"{_path(sp, 'metrics')}: must be a non-empty array")
            else:
                for j, m in enumerate(ms):
                    if not isinstance(m, dict):
                        errors.append(f"{_path(sp, f'metrics[{j}]')}: must be an object")
                        continue
                    if not isinstance(m.get("value"), str) or not m.get("value"):
                        errors.append(f"{_path(sp, f'metrics[{j}].value')}: required non-empty string")
                    if not isinstance(m.get("label"), str) or not m.get("label"):
                        errors.append(f"{_path(sp, f'metrics[{j}].label')}: required non-empty string")
                    if "detail" in m and m.get("detail") is not None and not isinstance(m.get("detail"), str):
                        errors.append(f"{_path(sp, f'metrics[{j}].detail')}: must be a string")

    return errors
