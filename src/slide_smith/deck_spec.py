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


def validate_deck_spec(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    slides = spec.get("slides")
    if not isinstance(slides, list) or not slides:
        errors.append("'slides' must be a non-empty array")
        return errors

    for idx, slide in enumerate(slides):
        if not isinstance(slide, dict):
            errors.append(f"slide[{idx}] must be an object")
            continue
        archetype = slide.get("archetype")
        if not isinstance(archetype, str):
            errors.append(f"slide[{idx}].archetype must be a string")
        elif archetype not in SUPPORTED_ARCHETYPES:
            errors.append(
                f"slide[{idx}].archetype must be one of: {', '.join(sorted(SUPPORTED_ARCHETYPES))}"
            )

    return errors
