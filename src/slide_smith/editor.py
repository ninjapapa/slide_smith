from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pptx import Presentation

from slide_smith.renderer import RenderingError, _layout_by_name, _render_image_left_text_right, _render_section, _render_title, _render_title_and_bullets
from slide_smith.template_loader import load_template_spec


class EditError(Exception):
    """Raised when an edit operation cannot be completed safely."""



def _load_json(path: str) -> dict[str, Any]:
    return json.loads(Path(path).read_text())



def add_slide_to_deck(deck_path: str, after_index: int, archetype: str, input_path: str, template_id: str = "default") -> str:
    prs = Presentation(deck_path)
    if after_index != len(prs.slides) - 1:
        raise EditError(
            "Only append-style add-slide is supported right now; use --after with the current last slide index"
        )

    template_spec = load_template_spec(template_id)
    archetypes = {item["id"]: item for item in template_spec.get("archetypes", [])}
    if archetype not in archetypes:
        raise EditError(f"Archetype '{archetype}' is not supported by template '{template_id}'")

    slide_spec = _load_json(input_path)
    slide_spec.setdefault("archetype", archetype)
    layout_name = archetypes[archetype]["layout"]
    slide = prs.slides.add_slide(_layout_by_name(prs, layout_name))
    base_dir = Path(input_path).resolve().parent

    if archetype == "title":
        _render_title(slide, slide_spec)
    elif archetype == "section":
        _render_section(slide, slide_spec)
    elif archetype == "title_and_bullets":
        _render_title_and_bullets(slide, slide_spec)
    elif archetype == "image_left_text_right":
        _render_image_left_text_right(slide, slide_spec, base_dir)
    else:
        raise EditError(f"Archetype '{archetype}' is not implemented")

    prs.save(deck_path)
    return deck_path



def update_slide_in_deck(deck_path: str, index: int, input_path: str) -> str:
    prs = Presentation(deck_path)
    if index < 0 or index >= len(prs.slides):
        raise EditError(f"Slide index {index} out of range")

    patch = _load_json(input_path)
    slide = prs.slides[index]

    if "title" in patch:
        try:
            slide.shapes.title.text = patch["title"]
        except Exception as exc:
            raise EditError("Target slide does not have a writable title placeholder") from exc

    if "subtitle" in patch:
        try:
            slide.placeholders[1].text = patch["subtitle"]
        except Exception as exc:
            raise EditError("Target slide does not support subtitle update via placeholder 1") from exc

    if "body" in patch:
        try:
            slide.placeholders[1].text = patch["body"]
        except Exception:
            try:
                slide.placeholders[2].text = patch["body"]
            except Exception as exc:
                raise EditError("Target slide does not support body update via known placeholders") from exc

    if "bullets" in patch:
        try:
            text_frame = slide.placeholders[1].text_frame
        except Exception as exc:
            raise EditError("Target slide does not support bullet updates") from exc
        bullets = patch["bullets"]
        if not bullets:
            text_frame.text = ""
        else:
            text_frame.text = bullets[0]
            for bullet in bullets[1:]:
                p = text_frame.add_paragraph()
                p.text = bullet
                p.level = 0

    prs.save(deck_path)
    return deck_path
