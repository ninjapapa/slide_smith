from __future__ import annotations

import json
from pathlib import Path
from typing import Any


SUPPORTED_ARCHETYPES = {
    "title",
    "section",
    "title_and_bullets",
    "image_left_text_right",
}


def load_deck_spec(path: str) -> dict[str, Any]:
    file_path = Path(path)
    return json.loads(file_path.read_text())


def _path(*parts: str) -> str:
    # JSON-pointer-ish for humans.
    return "$." + ".".join(parts)



def validate_deck_spec(spec: dict[str, Any]) -> list[str]:
    """Lightweight validation with human-friendly error paths.

    This intentionally does not depend on jsonschema; it validates the small subset
    we actively render/edit.
    """

    errors: list[str] = []

    slides = spec.get("slides")
    if not isinstance(slides, list) or not slides:
        return [f"{_path('slides')}: must be a non-empty array"]

    for idx, slide in enumerate(slides):
        sp = f"slides[{idx}]"
        if not isinstance(slide, dict):
            errors.append(f"{_path(sp)}: must be an object")
            continue

        archetype = slide.get("archetype")
        if not isinstance(archetype, str):
            errors.append(f"{_path(sp, 'archetype')}: must be a string")
            continue
        if archetype not in SUPPORTED_ARCHETYPES:
            errors.append(
                f"{_path(sp, 'archetype')}: must be one of: {', '.join(sorted(SUPPORTED_ARCHETYPES))}"
            )
            continue

        # Common fields
        if "notes" in slide and not isinstance(slide.get("notes"), str):
            errors.append(f"{_path(sp, 'notes')}: must be a string")

        def req_str(field: str) -> None:
            if not isinstance(slide.get(field), str) or not slide.get(field):
                errors.append(f"{_path(sp, field)}: required non-empty string")

        if archetype in {"title", "section", "title_and_bullets", "image_left_text_right"}:
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

        elif archetype == "image_left_text_right":
            req_str("body")
            req_str("image")

    return errors
