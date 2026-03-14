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


def _layout_for_archetype(prs: Presentation, archetype_spec: dict[str, Any]):
    """Resolve a layout for an archetype.

    Prefer `layout_part` when available (more stable for rich branded templates).
    Fallback to `layout` name.
    """

    from slide_smith.layout_resolver import LayoutResolveError, resolve_layout

    layout_name = archetype_spec.get("layout")
    layout_part = archetype_spec.get("layout_part")

    try:
        return resolve_layout(prs=prs, layout_name=layout_name, layout_part=layout_part).layout
    except LayoutResolveError as exc:
        raise RenderingError(str(exc)) from exc


def _slot_spec(archetype_spec: dict[str, Any], slot_name: str) -> dict[str, Any] | None:
    for slot in archetype_spec.get("slots", []):
        if isinstance(slot, dict) and slot.get("name") == slot_name:
            return slot
    return None


def _slot_index(archetype_spec: dict[str, Any], slot_name: str, default: int | None = None) -> int | None:
    """Resolve placeholder_idx for a slot.

    `default` is only used when the slot is missing entirely.
    If the slot exists but does not declare placeholder_idx (e.g. box-based slots),
    this returns None.
    """

    slot = _slot_spec(archetype_spec, slot_name)
    if slot is None:
        return default
    idx = slot.get("placeholder_idx")
    if isinstance(idx, int):
        return idx
    return None


def _slot_box(archetype_spec: dict[str, Any], slot_name: str) -> dict[str, Any] | None:
    slot = _slot_spec(archetype_spec, slot_name)
    if slot is None:
        return None
    box = slot.get("box")
    if isinstance(box, dict):
        return box
    return None


def _box_to_emu(box: dict[str, Any], *, slide_w_emu: int, slide_h_emu: int) -> tuple[int, int, int, int] | None:
    """Convert a slot box to EMU coordinates.

    Supported forms:
    - units=relative: x,y,w,h are floats in [0,1]
    - units=emu: left,top,width,height are ints (or x,y,w,h)

    Returns: (left, top, width, height)
    """

    units = box.get("units")
    if units == "relative":
        try:
            x = float(box["x"])
            y = float(box["y"])
            w = float(box["w"])
            h = float(box["h"])
        except Exception:
            return None
        left = int(x * slide_w_emu)
        top = int(y * slide_h_emu)
        width = int(w * slide_w_emu)
        height = int(h * slide_h_emu)
        return left, top, width, height

    if units == "emu":
        # Accept either (left,top,width,height) or (x,y,w,h)
        def gi(*keys):
            for k in keys:
                v = box.get(k)
                if isinstance(v, int):
                    return v
            return None

        left = gi("left", "x")
        top = gi("top", "y")
        width = gi("width", "w")
        height = gi("height", "h")
        if None in (left, top, width, height):
            return None
        return int(left), int(top), int(width), int(height)

    return None


def _required_slot_target(
    archetype_id: str,
    archetype_spec: dict[str, Any],
    slot_name: str,
    *,
    default_idx: int | None = None,
) -> tuple[int | None, dict[str, Any] | None]:
    slot = _slot_spec(archetype_spec, slot_name)
    idx = _slot_index(archetype_spec, slot_name, default_idx)
    box = _slot_box(archetype_spec, slot_name)

    required = bool(slot.get("required")) if slot is not None else False
    if required and idx is None and box is None:
        raise RenderingError(
            f"Template archetype '{archetype_id}' missing required slot mapping '{slot_name}' (placeholder_idx or box)"
        )

    return idx, box


def _set_placeholder_text(slide, idx: int | None, text: str | None, style=None, *, context: str = "") -> None:
    if idx is None or text is None:
        return
    try:
        ph = slide.placeholders[idx]
        ph.text = text
        if style is not None and hasattr(ph, "text_frame"):
            apply_text_style(ph.text_frame, style)
    except KeyError as exc:
        ctx = f" ({context})" if context else ""
        raise RenderingError(f"Placeholder idx={idx} not found on slide{ctx}") from exc


def _set_box_text(slide, box_emu: tuple[int, int, int, int] | None, text: str | None, style=None) -> None:
    if box_emu is None or text is None:
        return
    left, top, width, height = box_emu
    tb = slide.shapes.add_textbox(left, top, width, height)
    tf = tb.text_frame
    tf.text = text
    if style is not None:
        apply_text_style(tf, style)


def _set_box_bullets(slide, box_emu: tuple[int, int, int, int] | None, bullets: list[str], style=None) -> None:
    if box_emu is None:
        return
    left, top, width, height = box_emu
    tb = slide.shapes.add_textbox(left, top, width, height)
    tf = tb.text_frame
    if not bullets:
        tf.text = ""
        return
    tf.text = bullets[0]
    for bullet in bullets[1:]:
        p = tf.add_paragraph()
        p.text = bullet
        p.level = 0
    if style is not None:
        apply_text_style(tf, style)


def _set_box_image(slide, box_emu: tuple[int, int, int, int] | None, image_path: Path | None) -> None:
    if box_emu is None or image_path is None:
        return
    left, top, width, height = box_emu
    slide.shapes.add_picture(str(image_path), left, top, width=width, height=height)


def _set_slot_text(
    slide,
    archetype_id: str,
    archetype_spec: dict[str, Any],
    slot_name: str,
    text: str | None,
    style,
    *,
    slide_w_emu: int,
    slide_h_emu: int,
    default_idx: int | None = None,
    context: str = "",
) -> None:
    idx, box = _required_slot_target(archetype_id, archetype_spec, slot_name, default_idx=default_idx)
    if idx is not None:
        _set_placeholder_text(slide, idx, text, style, context=context)
        return
    if box is not None:
        box_emu = _box_to_emu(box, slide_w_emu=slide_w_emu, slide_h_emu=slide_h_emu)
        _set_box_text(slide, box_emu, text, style)


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
        context=f"archetype={archetype_id} slot=title",
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
        context=f"archetype={archetype_id} slot=subtitle",
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
        context=f"archetype={archetype_id} slot=title",
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
            context=f"archetype={archetype_id} slot=subtitle/body",
        )
        return

    if box is not None:
        box_emu = _box_to_emu(box, slide_w_emu=slide_w_emu, slide_h_emu=slide_h_emu)
        _set_box_text(slide, box_emu, subtitle, styles.get("subtitle"))
        return

    # If neither placeholder nor box is provided, keep behavior consistent: no-op.


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
        context=f"archetype={archetype_id} slot=title",
    )

    # bullets/body target
    body_idx = _slot_index(archetype_spec, "bullets")
    if body_idx is None:
        body_idx = _slot_index(archetype_spec, "body", 1)

    body_box = _slot_box(archetype_spec, "bullets") or _slot_box(archetype_spec, "body")

    bullets = spec.get("bullets") or []
    if not isinstance(bullets, list):
        bullets = []

    if body_idx is None and body_box is None:
        # If the template explicitly says bullets is required, fail loudly.
        _required_slot_target(archetype_id, archetype_spec, "bullets")
        raise RenderingError(
            f"Cannot resolve placeholder/box for slot 'bullets/body' in archetype '{archetype_id}'"
        )

    if body_idx is not None:
        try:
            body_placeholder = slide.placeholders[body_idx]
        except KeyError as exc:
            raise RenderingError(
                f"Placeholder idx={body_idx} not found on slide (archetype={archetype_id} slot=bullets/body)"
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

    # box-based bullets
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
        context=f"archetype={archetype_id} slot=title",
    )

    image_field = spec.get("image")
    image_path = None
    if isinstance(image_field, str):
        image_path = image_field
    elif isinstance(image_field, dict):
        image_path = image_field.get("path")

    image_idx, image_box = _required_slot_target(archetype_id, archetype_spec, "image", default_idx=1)
    body_idx, body_box = _required_slot_target(archetype_id, archetype_spec, "body", default_idx=2)

    resolved_image: Path | None = None
    if image_path:
        p = Path(str(image_path)).expanduser()
        resolved_image = (base_dir / p).resolve() if not p.is_absolute() else p.resolve()
        if not resolved_image.exists():
            raise RenderingError(f"Image file not found: {resolved_image}")
        if not resolved_image.is_file():
            raise RenderingError(f"Image path is not a file: {resolved_image}")

    # image
    if resolved_image is not None:
        if image_idx is not None:
            try:
                image_placeholder = slide.placeholders[image_idx]
            except KeyError as exc:
                raise RenderingError(
                    f"Placeholder idx={image_idx} not found on slide (archetype={archetype_id} slot=image)"
                ) from exc
            slide.shapes.add_picture(
                str(resolved_image),
                image_placeholder.left,
                image_placeholder.top,
                width=image_placeholder.width,
                height=image_placeholder.height,
            )
        elif image_box is not None:
            box_emu = _box_to_emu(image_box, slide_w_emu=slide_w_emu, slide_h_emu=slide_h_emu)
            _set_box_image(slide, box_emu, resolved_image)

    # body
    body_text = spec.get("body", "")
    if body_idx is not None:
        try:
            body_placeholder = slide.placeholders[body_idx]
        except KeyError as exc:
            raise RenderingError(
                f"Placeholder idx={body_idx} not found on slide (archetype={archetype_id} slot=body)"
            ) from exc
        body_placeholder.text = body_text
        apply_text_style(body_placeholder.text_frame, styles.get("body"))
    elif body_box is not None:
        box_emu = _box_to_emu(body_box, slide_w_emu=slide_w_emu, slide_h_emu=slide_h_emu)
        _set_box_text(slide, box_emu, body_text, styles.get("body"))


def _render_extended(slide, spec: dict[str, Any], styles, archetype_spec: dict[str, Any], archetype_id: str, *, slide_w_emu: int, slide_h_emu: int) -> None:
    """MVP renderer for v1.1 extended archetypes.

    This implementation is intentionally placeholder-driven and template-mapping-driven.
    It treats the template spec slot mappings as the source of truth.

    v1.2+ note: box-based slots are supported for text fields as a fallback.
    """

    title = spec.get("title", "")
    _set_slot_text(
        slide,
        archetype_id,
        archetype_spec,
        "title",
        title,
        styles.get("title"),
        slide_w_emu=slide_w_emu,
        slide_h_emu=slide_h_emu,
        default_idx=0,
        context=f"archetype={archetype_id} slot=title",
    )

    def set_text_slot(slot_name: str, value: str | None, style_key: str = "body"):
        _set_slot_text(
            slide,
            archetype_id,
            archetype_spec,
            slot_name,
            value,
            styles.get(style_key),
            slide_w_emu=slide_w_emu,
            slide_h_emu=slide_h_emu,
            context=f"archetype={archetype_id} slot={slot_name}",
        )

    if archetype_id in {"two_col", "three_col", "four_col"}:
        n = {"two_col": 2, "three_col": 3, "four_col": 4}[archetype_id]
        for i in range(1, n + 1):
            set_text_slot(f"col{i}_body", spec.get(f"col{i}_body"))
        return

    if archetype_id in {"pillars_3", "pillars_4"}:
        n = 3 if archetype_id == "pillars_3" else 4
        for i in range(1, n + 1):
            set_text_slot(f"pillar{i}_body", spec.get(f"pillar{i}_body"))
        return

    if archetype_id == "table":
        set_text_slot("table_text", spec.get("table_text"), style_key="body")
        return

    if archetype_id == "table_plus_description":
        set_text_slot("table_text", spec.get("table_text"), style_key="body")
        set_text_slot("body", spec.get("body"), style_key="body")
        return

    if archetype_id == "timeline_horizontal":
        for i in range(1, 11):
            k = f"milestone{i}_body"
            if k in spec:
                set_text_slot(k, spec.get(k))
        return

    raise RenderingError(f"Extended archetype '{archetype_id}' is not implemented")


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
    prs = _presentation_for_template(template_id, templates_dir=templates_dir)
    source_dir = Path(base_dir or ".").resolve()

    slide_w_emu = int(prs.slide_width)
    slide_h_emu = int(prs.slide_height)

    styles = load_styles(template_spec)
    archetypes = {item["id"]: item for item in template_spec.get("archetypes", [])}

    for slide_spec in deck_spec.get("slides", []):
        archetype = slide_spec["archetype"]
        if archetype not in archetypes:
            raise RenderingError(f"Archetype '{archetype}' not supported by template '{template_id}'")
        archetype_spec = archetypes[archetype]
        slide = prs.slides.add_slide(_layout_for_archetype(prs, archetype_spec))

        if archetype == "title":
            _render_title(slide, slide_spec, styles, archetype_spec, archetype, slide_w_emu=slide_w_emu, slide_h_emu=slide_h_emu)
        elif archetype == "section":
            _render_section(slide, slide_spec, styles, archetype_spec, archetype, slide_w_emu=slide_w_emu, slide_h_emu=slide_h_emu)
        elif archetype == "title_and_bullets":
            _render_title_and_bullets(slide, slide_spec, styles, archetype_spec, archetype, slide_w_emu=slide_w_emu, slide_h_emu=slide_h_emu)
        elif archetype == "image_left_text_right":
            _render_image_left_text_right(slide, slide_spec, source_dir, styles, archetype_spec, archetype, slide_w_emu=slide_w_emu, slide_h_emu=slide_h_emu)
        elif archetype in {"two_col", "three_col", "four_col", "pillars_3", "pillars_4", "table", "table_plus_description", "timeline_horizontal"}:
            _render_extended(slide, slide_spec, styles, archetype_spec, archetype, slide_w_emu=slide_w_emu, slide_h_emu=slide_h_emu)
        else:
            raise RenderingError(f"Archetype '{archetype}' is not implemented")

        _set_notes(slide, slide_spec.get("notes"))

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(out))
    return str(out)
