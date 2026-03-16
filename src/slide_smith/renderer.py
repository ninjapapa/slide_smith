from __future__ import annotations

from pathlib import Path
from typing import Any

from pptx import Presentation

from slide_smith.deck_spec import normalize_deck_spec
from slide_smith.render_core import (
    _render_section,
    _render_text_with_image,
    _render_title,
    _render_title_and_bullets,
)
from slide_smith.render_fallback import (
    FALLBACK_LAYOUT_ID,
    _make_fallback_slide_spec,
    _record_render_warning,
)
from slide_smith.render_extended import _render_extended
from slide_smith.render_support import RenderingError, _layout_for_spec
from slide_smith.styling import load_styles
from slide_smith.template_loader import template_dir


def _presentation_for_template(
    template_id: str,
    templates_dir: str | None = None,
    *,
    preserve_template_slides: bool = False,
) -> Presentation:
    """Load a Presentation for rendering.

    By default we treat template.pptx as a *theme/layout source* and start with zero
    content slides (rich templates often include many sample slides that should not
    be preserved in generated outputs).

    If preserve_template_slides=True, keep any existing slides from template.pptx.
    """

    pptx_path = template_dir(template_id, templates_dir) / "template.pptx"
    if not pptx_path.exists():
        return Presentation()

    prs = Presentation(str(pptx_path))

    if preserve_template_slides:
        return prs

    try:
        from slide_smith.pptx_edit import delete_slide

        while len(prs.slides) > 0:
            delete_slide(prs, 0)
    except Exception as exc:
        raise RenderingError(f"Failed to clear template slides: {exc}") from exc

    return prs


def _set_notes(slide, notes: str | None) -> None:
    if not notes:
        return
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
    original_deck_spec = deck_spec
    deck_spec, _ = normalize_deck_spec(deck_spec)
    preserve = bool(deck_spec.get("preserve_template_slides"))
    prs = _presentation_for_template(template_id, templates_dir=templates_dir, preserve_template_slides=preserve)
    source_dir = Path(base_dir or ".").resolve()

    slide_w_emu = int(prs.slide_width)
    slide_h_emu = int(prs.slide_height)

    styles = load_styles(template_spec)
    layout_specs = {
        item["id"]: item
        for item in template_spec.get("archetypes", [])
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }

    def resolve_template_layout_id(slide_layout_id: str) -> str:
        return slide_layout_id

    def render_one(slide_spec: dict[str, Any]) -> None:
        layout_id = slide_spec["layout_id"]
        template_layout_id = resolve_template_layout_id(layout_id)
        if template_layout_id not in layout_specs:
            raise RenderingError(
                f"Layout '{layout_id}' not supported by template '{template_id}'"
            )
        layout_spec = layout_specs[template_layout_id]
        slide = prs.slides.add_slide(_layout_for_spec(prs, layout_spec))

        if layout_id == "title":
            _render_title(slide, slide_spec, styles, layout_spec, layout_id, slide_w_emu=slide_w_emu, slide_h_emu=slide_h_emu)
        elif layout_id == "section":
            _render_section(slide, slide_spec, styles, layout_spec, layout_id, slide_w_emu=slide_w_emu, slide_h_emu=slide_h_emu)
        elif layout_id == "title_and_bullets":
            _render_title_and_bullets(slide, slide_spec, styles, layout_spec, layout_id, slide_w_emu=slide_w_emu, slide_h_emu=slide_h_emu)
        elif layout_id == "text_with_image":
            _render_text_with_image(slide, slide_spec, source_dir, styles, layout_spec, layout_id, slide_w_emu=slide_w_emu, slide_h_emu=slide_h_emu)
        elif layout_id == "title_subtitle_and_bullets":
            _render_title_and_bullets(slide, slide_spec, styles, layout_spec, layout_id, slide_w_emu=slide_w_emu, slide_h_emu=slide_h_emu)
            from slide_smith.render_support import _set_slot_text

            _set_slot_text(
                slide,
                layout_id,
                layout_spec,
                "subtitle",
                slide_spec.get("subtitle"),
                styles.get("subtitle"),
                slide_w_emu=slide_w_emu,
                slide_h_emu=slide_h_emu,
                context=f"layout_id={layout_id} slot=subtitle",
            )
        elif layout_id in {
            "two_col",
            "version_page",
            "agenda_with_image",
            "three_col_with_icons",
            "picture_compare",
        }:
            _render_extended(
                slide,
                slide_spec,
                source_dir,
                styles,
                layout_spec,
                layout_id,
                slide_w_emu=slide_w_emu,
                slide_h_emu=slide_h_emu,
            )
        else:
            raise RenderingError(f"Layout '{layout_id}' is not implemented")

        _set_notes(slide, slide_spec.get("notes"))

    for i, slide_spec in enumerate(deck_spec.get("slides", [])):
        before_count = len(prs.slides)
        try:
            render_one(slide_spec)
        except RenderingError as exc:
            try:
                from slide_smith.pptx_edit import delete_slide

                while len(prs.slides) > before_count:
                    delete_slide(prs, len(prs.slides) - 1)
            except Exception:
                pass

            requested_layout_id = str(slide_spec.get("layout_id") or "unknown")
            if requested_layout_id == FALLBACK_LAYOUT_ID:
                raise
            _record_render_warning(deck_spec, slide_index=i, requested_layout_id=requested_layout_id, reason=str(exc))
            fallback_spec = _make_fallback_slide_spec(slide_spec, requested_layout_id=requested_layout_id, reason=str(exc))
            render_one(fallback_spec)

    if isinstance(original_deck_spec, dict):
        if isinstance(deck_spec.get("render_warnings"), list):
            original_deck_spec["render_warnings"] = deck_spec.get("render_warnings")
        if isinstance(deck_spec.get("slides"), list):
            original_deck_spec["slides"] = deck_spec.get("slides")

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(out))
    return str(out)
