from __future__ import annotations

import json
from pathlib import Path
from typing import Any


# NOTE: This list should track what the renderer supports.
# v1.0 core + v1.1 extended (renderer supports both).
SUPPORTED_ARCHETYPES = {
    # current stable surface
    "title",
    "section",
    "title_and_bullets",
    "text_with_image",
    "title_subtitle_and_bullets",
    "version_page",
    "agenda_with_image",
    "two_col",
    "three_col_with_icons",
    "picture_compare",
    # legacy alias kept for migration
    "image_left_text_right",
}


# Backward-compatible archetype aliases. This enables additive evolution of
# archetype names without breaking existing deck specs.
ARCHETYPE_ALIASES: dict[str, str] = {
    # prefer semantic naming vs geometry-bound naming
    "image_left_text_right": "text_with_image",
    # legacy v1 naming
    "title_and_bullets_with_subtitle": "title_subtitle_and_bullets",
}

# External v3-facing term. We keep internal archetype compatibility during migration.
LAYOUT_ID_TO_ARCHETYPE: dict[str, str] = {}


def _normalized_slide_kind(slide: dict[str, Any]) -> tuple[str | None, str | None]:
    """Return (internal_archetype, external_layout_id) for a slide.

    During the v3 transition we accept either:
    - layout_id (preferred external term)
    - archetype (legacy/existing term)
    """

    layout_id = slide.get("layout_id")
    if isinstance(layout_id, str) and layout_id:
        internal = LAYOUT_ID_TO_ARCHETYPE.get(layout_id, layout_id)
        return internal, layout_id

    archetype = slide.get("archetype")
    if isinstance(archetype, str) and archetype:
        return archetype, archetype

    return None, None


def normalize_deck_spec(spec: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    """Normalize a deck spec in a backwards-compatible way.

    Returns: (normalized_spec, warnings)

    This currently:
    - accepts `layout_id` as the preferred external slide kind field
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

        archetype, layout_id = _normalized_slide_kind(slide)
        slide2 = dict(slide)

        if isinstance(slide.get("layout_id"), str):
            # Keep the preferred external term in normalized output for user-facing flows,
            # but synthesize the internal `archetype` field for the current renderer/validator.
            slide2["archetype"] = archetype
        elif isinstance(layout_id, str):
            slide2.setdefault("layout_id", layout_id)

        if isinstance(archetype, str) and archetype in ARCHETYPE_ALIASES:
            new_id = ARCHETYPE_ALIASES[archetype]
            field = "layout_id" if isinstance(slide.get("layout_id"), str) else "archetype"
            warnings.append(f"$.slides[{i}].{field}: '{archetype}' is deprecated; use '{new_id}'")
            slide2["archetype"] = new_id
            slide2["layout_id"] = new_id

        out_slides.append(slide2)

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
    - legacy: current stable renderer support plus migration aliases

    The goal is to keep validation aligned with the current supported product surface.
    """

    errors: list[str] = []

    slides = spec.get("slides")
    if not isinstance(slides, list) or not slides:
        return [f"{_path('slides')}: must be a non-empty array"]

    allowed = set(SUPPORTED_ARCHETYPES)

    allowed |= {
        # allow legacy aliases so validation doesn't fail before normalization
        "title_and_bullets_with_subtitle",
    }

    for idx, slide in enumerate(slides):
        sp = f"slides[{idx}]"
        if not isinstance(slide, dict):
            errors.append(f"{_path(sp)}: must be an object")
            continue

        archetype, _layout_id = _normalized_slide_kind(slide)
        if not isinstance(archetype, str):
            errors.append(f"{_path(sp, 'layout_id')}: must be a string")
            continue
        if archetype not in allowed:
            errors.append(f"{_path(sp, 'layout_id')}: must be one of: {', '.join(sorted(allowed))}")
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
            "text_with_image",
            "title_subtitle_and_bullets",
            "version_page",
            "agenda_with_image",
            "two_col",
            "three_col_with_icons",
            "picture_compare",
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

        elif archetype == "title_subtitle_and_bullets":
            req_str("subtitle")
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

        elif archetype == "two_col":
            for i in (1, 2):
                f = f"col{i}_body"
                if not isinstance(slide.get(f), str) or not slide.get(f):
                    errors.append(f"{_path(sp, f)}: required non-empty string")

        elif archetype == "version_page":
            if not isinstance(slide.get("table_text"), str) or not slide.get("table_text"):
                errors.append(f"{_path(sp, 'table_text')}: required non-empty string")

        elif archetype == "agenda_with_image":
            image = slide.get("image")
            if isinstance(image, str):
                if not image:
                    errors.append(f"{_path(sp, 'image')}: required non-empty string")
            elif isinstance(image, dict):
                ip = image.get("path")
                if not isinstance(ip, str) or not ip:
                    errors.append(f"{_path(sp, 'image.path')}: required non-empty string")
            else:
                errors.append(f"{_path(sp, 'image')}: must be a string or an object")

            items = slide.get("items")
            if not isinstance(items, list) or not items:
                errors.append(f"{_path(sp, 'items')}: must be a non-empty array")
            else:
                for j, it in enumerate(items):
                    if not isinstance(it, dict):
                        errors.append(f"{_path(sp, f'items[{j}]')}: must be an object")
                        continue
                    if not isinstance(it.get("body"), str) or not it.get("body"):
                        errors.append(f"{_path(sp, f'items[{j}].body')}: required non-empty string")
                    marker = it.get("marker")
                    if marker is not None and not isinstance(marker, str):
                        errors.append(f"{_path(sp, f'items[{j}].marker')}: must be a string")

        elif archetype == "three_col_with_icons":
            items = slide.get("items")
            if not isinstance(items, list) or len(items) != 3:
                errors.append(f"{_path(sp, 'items')}: must be an array of exactly 3 objects")
            else:
                for j, it in enumerate(items):
                    if not isinstance(it, dict):
                        errors.append(f"{_path(sp, f'items[{j}]')}: must be an object")
                        continue
                    for field in ("title", "body", "icon"):
                        if not isinstance(it.get(field), str) or not it.get(field):
                            errors.append(f"{_path(sp, f'items[{j}].{field}')}: required non-empty string")
                    if "caption" in it and it.get("caption") is not None and not isinstance(it.get("caption"), str):
                        errors.append(f"{_path(sp, f'items[{j}].caption')}: must be a string")

        elif archetype == "picture_compare":
            for side_name in ("left", "right"):
                side = slide.get(side_name)
                if not isinstance(side, dict):
                    errors.append(f"{_path(sp, side_name)}: required object")
                    continue
                image = side.get("image")
                if isinstance(image, str):
                    if not image:
                        errors.append(f"{_path(sp, f'{side_name}.image')}: required non-empty string")
                elif isinstance(image, dict):
                    ip = image.get("path")
                    if not isinstance(ip, str) or not ip:
                        errors.append(f"{_path(sp, f'{side_name}.image.path')}: required non-empty string")
                else:
                    errors.append(f"{_path(sp, f'{side_name}.image')}: must be a string or an object")
                for field in ("title", "body"):
                    if field in side and side.get(field) is not None and not isinstance(side.get(field), str):
                        errors.append(f"{_path(sp, f'{side_name}.{field}')}: must be a string")

    return errors
