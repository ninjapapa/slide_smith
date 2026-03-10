from __future__ import annotations

from pathlib import Path
from typing import Any

from pptx import Presentation

from slide_smith.styling import apply_text_style, load_styles
from slide_smith.template_loader import template_dir


class RenderingError(Exception):
    """Raised when a deck cannot be rendered."""



def _presentation_for_template(template_id: str, templates_dir: str | None = None) -> Presentation:
    pptx_path = template_dir(template_id, templates_dir) / "template.pptx"
    if pptx_path.exists():
        return Presentation(str(pptx_path))
    return Presentation()



def _layout_by_name(prs: Presentation, name: str):
    for layout in prs.slide_layouts:
        if layout.name == name:
            return layout
    raise RenderingError(f"Slide layout '{name}' not found in template presentation")



def _set_placeholder_text(slide, idx: int, text: str | None, style=None) -> None:
    if text is None:
        return
    try:
        ph = slide.placeholders[idx]
        ph.text = text
        if style is not None and hasattr(ph, "text_frame"):
            apply_text_style(ph.text_frame, style)
    except KeyError as exc:
        raise RenderingError(f"Placeholder idx={idx} not found on slide") from exc



def _render_title(slide, spec: dict[str, Any], styles) -> None:
    _set_placeholder_text(slide, 0, spec.get("title", ""), styles.get("title"))
    _set_placeholder_text(slide, 1, spec.get("subtitle", ""), styles.get("subtitle"))



def _render_section(slide, spec: dict[str, Any], styles) -> None:
    _set_placeholder_text(slide, 0, spec.get("title", ""), styles.get("title"))
    _set_placeholder_text(slide, 1, spec.get("subtitle") or spec.get("body", ""), styles.get("subtitle"))



def _render_title_and_bullets(slide, spec: dict[str, Any], styles) -> None:
    _set_placeholder_text(slide, 0, spec.get("title", ""), styles.get("title"))
    body_placeholder = slide.placeholders[1]
    text_frame = body_placeholder.text_frame
    bullets = spec.get("bullets") or []
    if not bullets:
        text_frame.text = spec.get("body", "")
        apply_text_style(text_frame, styles.get("body"))
        return
    text_frame.text = bullets[0]
    for bullet in bullets[1:]:
        paragraph = text_frame.add_paragraph()
        paragraph.text = bullet
        paragraph.level = 0
    apply_text_style(text_frame, styles.get("bullets"))



def _render_image_left_text_right(slide, spec: dict[str, Any], base_dir: Path, styles) -> None:
    _set_placeholder_text(slide, 0, spec.get("title", ""), styles.get("title"))

    image_field = spec.get("image")
    image_path = None
    if isinstance(image_field, str):
        image_path = image_field
    elif isinstance(image_field, dict):
        image_path = image_field.get("path")

    if image_path:
        p = Path(str(image_path)).expanduser()
        resolved = (base_dir / p).resolve() if not p.is_absolute() else p.resolve()
        if not resolved.exists():
            raise RenderingError(f"Image file not found: {resolved}")
        if not resolved.is_file():
            raise RenderingError(f"Image path is not a file: {resolved}")
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
    apply_text_style(body_placeholder.text_frame, styles.get("body"))



def _set_notes(slide, notes: str | None) -> None:
    if not notes:
        return
    # python-pptx creates notes slide lazily.
    notes_slide = slide.notes_slide
    notes_slide.notes_text_frame.text = notes



def render_deck(
    deck_spec: dict[str, Any],
    template_spec: dict[str, Any],
    template_id: str,
    output_path: str,
    base_dir: str | None = None,
    templates_dir: str | None = None,
) -> str:
    prs = _presentation_for_template(template_id, templates_dir=templates_dir)
    source_dir = Path(base_dir or ".").resolve()

    styles = load_styles(template_spec)
    archetypes = {item["id"]: item for item in template_spec.get("archetypes", [])}

    for slide_spec in deck_spec.get("slides", []):
        archetype = slide_spec["archetype"]
        if archetype not in archetypes:
            raise RenderingError(f"Archetype '{archetype}' not supported by template '{template_id}'")
        layout_name = archetypes[archetype]["layout"]
        slide = prs.slides.add_slide(_layout_by_name(prs, layout_name))

        if archetype == "title":
            _render_title(slide, slide_spec, styles)
        elif archetype == "section":
            _render_section(slide, slide_spec, styles)
        elif archetype == "title_and_bullets":
            _render_title_and_bullets(slide, slide_spec, styles)
        elif archetype == "image_left_text_right":
            _render_image_left_text_right(slide, slide_spec, source_dir, styles)
        else:
            raise RenderingError(f"Archetype '{archetype}' is not implemented")

        _set_notes(slide, slide_spec.get("notes"))

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(out))
    return str(out)
