from __future__ import annotations

from pathlib import Path
from typing import Any

from pptx import Presentation

from slide_smith.template_loader import template_dir


class RenderingError(Exception):
    """Raised when a deck cannot be rendered."""



def _presentation_for_template(template_id: str) -> Presentation:
    pptx_path = template_dir(template_id) / "template.pptx"
    if pptx_path.exists():
        return Presentation(str(pptx_path))
    return Presentation()



def _layout_by_name(prs: Presentation, name: str):
    for layout in prs.slide_layouts:
        if layout.name == name:
            return layout
    raise RenderingError(f"Slide layout '{name}' not found in template presentation")



def _set_placeholder_text(slide, idx: int, text: str | None) -> None:
    if text is None:
        return
    try:
        slide.placeholders[idx].text = text
    except KeyError as exc:
        raise RenderingError(f"Placeholder idx={idx} not found on slide") from exc



def _render_title(slide, spec: dict[str, Any]) -> None:
    _set_placeholder_text(slide, 0, spec.get("title", ""))
    _set_placeholder_text(slide, 1, spec.get("subtitle", ""))



def _render_section(slide, spec: dict[str, Any]) -> None:
    _set_placeholder_text(slide, 0, spec.get("title", ""))
    _set_placeholder_text(slide, 1, spec.get("subtitle") or spec.get("body", ""))



def _render_title_and_bullets(slide, spec: dict[str, Any]) -> None:
    _set_placeholder_text(slide, 0, spec.get("title", ""))
    body_placeholder = slide.placeholders[1]
    text_frame = body_placeholder.text_frame
    bullets = spec.get("bullets") or []
    if not bullets:
        text_frame.text = spec.get("body", "")
        return
    text_frame.text = bullets[0]
    for bullet in bullets[1:]:
        paragraph = text_frame.add_paragraph()
        paragraph.text = bullet
        paragraph.level = 0



def _render_image_left_text_right(slide, spec: dict[str, Any], base_dir: Path) -> None:
    _set_placeholder_text(slide, 0, spec.get("title", ""))

    image_path = spec.get("image")
    if image_path:
        resolved = (base_dir / image_path).resolve() if not Path(image_path).is_absolute() else Path(image_path)
        if not resolved.exists():
            raise RenderingError(f"Image file not found: {resolved}")
        image_placeholder = slide.placeholders[1]
        slide.shapes.add_picture(
            str(resolved),
            image_placeholder.left,
            image_placeholder.top,
            width=image_placeholder.width,
            height=image_placeholder.height,
        )

    body_placeholder = slide.placeholders[2]
    body_placeholder.text = spec.get("body", "")



def render_deck(deck_spec: dict[str, Any], template_spec: dict[str, Any], template_id: str, output_path: str, base_dir: str | None = None) -> str:
    prs = _presentation_for_template(template_id)
    source_dir = Path(base_dir or ".").resolve()

    archetypes = {item["id"]: item for item in template_spec.get("archetypes", [])}

    for slide_spec in deck_spec.get("slides", []):
        archetype = slide_spec["archetype"]
        if archetype not in archetypes:
            raise RenderingError(f"Archetype '{archetype}' not supported by template '{template_id}'")
        layout_name = archetypes[archetype]["layout"]
        slide = prs.slides.add_slide(_layout_by_name(prs, layout_name))

        if archetype == "title":
            _render_title(slide, slide_spec)
        elif archetype == "section":
            _render_section(slide, slide_spec)
        elif archetype == "title_and_bullets":
            _render_title_and_bullets(slide, slide_spec)
        elif archetype == "image_left_text_right":
            _render_image_left_text_right(slide, slide_spec, source_dir)
        else:
            raise RenderingError(f"Archetype '{archetype}' is not implemented")

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(out))
    return str(out)
