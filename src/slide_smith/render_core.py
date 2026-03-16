from __future__ import annotations

from pathlib import Path
from typing import Any

from slide_smith.render_support import (
    RenderingError,
    _box_to_emu,
    _required_slot_target,
    _resolve_image_path,
    _set_box_bullets,
    _set_box_text,
    _set_placeholder_text,
    _set_slot_image,
    _set_slot_text,
    _slot_box,
    _slot_index,
)
from slide_smith.styling import apply_text_style


def _render_title(slide, spec: dict[str, Any], styles, archetype_spec: dict[str, Any], archetype_id: str, *, slide_w_emu: int, slide_h_emu: int) -> None:
    _set_slot_text(
        slide,
        archetype_id,
        archetype_spec,
        "title",
        spec.get("title", ""),
        styles.get("title"),
        slide_w_emu=slide_w_emu,
        slide_h_emu=slide_h_emu,
        default_idx=0,
        context=f"layout_id={archetype_id} slot=title",
    )
    _set_slot_text(
        slide,
        archetype_id,
        archetype_spec,
        "subtitle",
        spec.get("subtitle", ""),
        styles.get("subtitle"),
        slide_w_emu=slide_w_emu,
        slide_h_emu=slide_h_emu,
        default_idx=1,
        context=f"layout_id={archetype_id} slot=subtitle",
    )


def _render_section(slide, spec: dict[str, Any], styles, archetype_spec: dict[str, Any], archetype_id: str, *, slide_w_emu: int, slide_h_emu: int) -> None:
    _set_slot_text(
        slide,
        archetype_id,
        archetype_spec,
        "title",
        spec.get("title", ""),
        styles.get("title"),
        slide_w_emu=slide_w_emu,
        slide_h_emu=slide_h_emu,
        default_idx=0,
        context=f"layout_id={archetype_id} slot=title",
    )

    subtitle = spec.get("subtitle") or spec.get("body", "")
    subtitle_idx = _slot_index(archetype_spec, "subtitle")
    body_idx = _slot_index(archetype_spec, "body")
    idx = subtitle_idx if subtitle_idx is not None else body_idx
    box = _slot_box(archetype_spec, "subtitle") or _slot_box(archetype_spec, "body")

    if idx is not None:
        _set_placeholder_text(
            slide,
            idx,
            subtitle,
            styles.get("subtitle"),
            context=f"layout_id={archetype_id} slot=subtitle/body",
        )
        return

    if box is not None:
        box_emu = _box_to_emu(box, slide_w_emu=slide_w_emu, slide_h_emu=slide_h_emu)
        _set_box_text(slide, box_emu, subtitle, styles.get("subtitle"))
        return


def _render_title_and_bullets(slide, spec: dict[str, Any], styles, archetype_spec: dict[str, Any], archetype_id: str, *, slide_w_emu: int, slide_h_emu: int) -> None:
    _set_slot_text(
        slide,
        archetype_id,
        archetype_spec,
        "title",
        spec.get("title", ""),
        styles.get("title"),
        slide_w_emu=slide_w_emu,
        slide_h_emu=slide_h_emu,
        default_idx=0,
        context=f"layout_id={archetype_id} slot=title",
    )

    body_idx = _slot_index(archetype_spec, "bullets")
    if body_idx is None:
        body_idx = _slot_index(archetype_spec, "body", 1)

    body_box = _slot_box(archetype_spec, "bullets") or _slot_box(archetype_spec, "body")

    bullets = spec.get("bullets") or []
    if not isinstance(bullets, list):
        bullets = []

    if body_idx is None and body_box is None:
        _required_slot_target(archetype_id, archetype_spec, "bullets")
        raise RenderingError(
            f"Cannot resolve placeholder/box for slot 'bullets/body' in layout '{archetype_id}'"
        )

    if body_idx is not None:
        try:
            body_placeholder = slide.placeholders[body_idx]
        except KeyError as exc:
            raise RenderingError(
                f"Placeholder idx={body_idx} not found on slide (layout_id={archetype_id} slot=bullets/body)"
            ) from exc
        text_frame = body_placeholder.text_frame
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
        return

    box_emu = _box_to_emu(body_box, slide_w_emu=slide_w_emu, slide_h_emu=slide_h_emu) if body_box else None
    if not bullets:
        _set_box_text(slide, box_emu, spec.get("body", ""), styles.get("body"))
    else:
        _set_box_bullets(slide, box_emu, bullets, styles.get("bullets"))


def _render_image_left_text_right(
    slide,
    spec: dict[str, Any],
    base_dir: Path,
    styles,
    archetype_spec: dict[str, Any],
    archetype_id: str,
    *,
    slide_w_emu: int,
    slide_h_emu: int,
) -> None:
    _set_slot_text(
        slide,
        archetype_id,
        archetype_spec,
        "title",
        spec.get("title", ""),
        styles.get("title"),
        slide_w_emu=slide_w_emu,
        slide_h_emu=slide_h_emu,
        default_idx=0,
        context=f"layout_id={archetype_id} slot=title",
    )

    resolved_image = _resolve_image_path(base_dir, spec.get("image"))

    _set_slot_image(
        slide,
        archetype_id,
        archetype_spec,
        "image",
        resolved_image,
        slide_w_emu=slide_w_emu,
        slide_h_emu=slide_h_emu,
        default_idx=1,
        context=f"layout_id={archetype_id} slot=image",
    )

    body_idx, body_box = _required_slot_target(archetype_id, archetype_spec, "body", default_idx=2)

    body_text = spec.get("body", "")
    if body_idx is not None:
        try:
            body_placeholder = slide.placeholders[body_idx]
        except KeyError as exc:
            raise RenderingError(
                f"Placeholder idx={body_idx} not found on slide (layout_id={archetype_id} slot=body)"
            ) from exc
        body_placeholder.text = body_text
        apply_text_style(body_placeholder.text_frame, styles.get("body"))
    elif body_box is not None:
        box_emu = _box_to_emu(body_box, slide_w_emu=slide_w_emu, slide_h_emu=slide_h_emu)
        _set_box_text(slide, box_emu, body_text, styles.get("body"))
