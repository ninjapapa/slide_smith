from __future__ import annotations

from pathlib import Path
from typing import Any

from slide_smith.render_core import _render_title_and_bullets
from slide_smith.render_support import (
    RenderingError,
    _box_to_emu,
    _required_slot_target,
    _resolve_image_path,
    _set_box_image,
    _set_box_text,
    _set_slot_image,
    _set_slot_text,
    _slot_spec,
)
from slide_smith.styling import apply_text_style


def _render_v2_families(
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
    """MVP renderer for proposed v2 archetype families."""

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

    if archetype_id == "message":
        body = spec.get("body") or spec.get("quote") or ""
        attribution = spec.get("attribution") or ""
        if _slot_spec(archetype_spec, "body") is not None:
            set_text_slot("body", body, style_key="body")
        if _slot_spec(archetype_spec, "quote") is not None:
            set_text_slot("quote", body, style_key="body")
        if _slot_spec(archetype_spec, "attribution") is not None:
            set_text_slot("attribution", attribution, style_key="subtitle")
        elif _slot_spec(archetype_spec, "subtitle") is not None:
            set_text_slot("subtitle", attribution, style_key="subtitle")
        return

    if archetype_id == "multi_col":
        items = spec.get("items") or []
        if not isinstance(items, list):
            items = []
        if not items:
            for i in range(1, 5):
                k = f"col{i}_body"
                if k in spec and isinstance(spec.get(k), str):
                    items.append({"body": spec.get(k)})

        for i, item in enumerate(items[:4], start=1):
            if not isinstance(item, dict):
                continue
            heading = item.get("heading")
            body = item.get("body")
            label = item.get("label") or item.get("number")
            parts = []
            if isinstance(label, str) and label:
                parts.append(label)
            if isinstance(heading, str) and heading:
                parts.append(heading)
            if isinstance(body, str) and body:
                parts.append(body)
            set_text_slot(f"col{i}_body", "\n".join(parts), style_key="body")
        return

    if archetype_id == "image_text":
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
        return

    if archetype_id == "list_visual":
        items = spec.get("items") or []
        bullets = []
        if isinstance(items, list):
            for it in items:
                if not isinstance(it, dict):
                    continue
                label = it.get("label") or it.get("number")
                body = it.get("body")
                if isinstance(label, str) and label and isinstance(body, str) and body:
                    bullets.append(f"{label} {body}")
                elif isinstance(body, str) and body:
                    bullets.append(body)

        if _slot_spec(archetype_spec, "bullets") is not None:
            proxy = dict(spec)
            proxy["bullets"] = bullets
            _render_title_and_bullets(slide, proxy, styles, archetype_spec, archetype_id, slide_w_emu=slide_w_emu, slide_h_emu=slide_h_emu)
        else:
            set_text_slot("body", "\n".join(bullets), style_key="body")
        return

    if archetype_id == "metrics":
        ms = spec.get("metrics") or []
        lines = []
        if isinstance(ms, list):
            for m in ms:
                if not isinstance(m, dict):
                    continue
                value = m.get("value")
                label = m.get("label")
                detail = m.get("detail")
                if isinstance(value, str) and isinstance(label, str):
                    s = f"{value} — {label}" if label else value
                    if isinstance(detail, str) and detail:
                        s += f"\n{detail}"
                    lines.append(s)
        set_text_slot("body", "\n\n".join(lines), style_key="body")
        return

    raise RenderingError(f"v2 archetype family '{archetype_id}' is not implemented")


def _render_extended(
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
    """MVP renderer for v1.1 extended archetypes."""

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

    if archetype_id == "two_col_with_subtitle":
        set_text_slot("subtitle", spec.get("subtitle"), style_key="subtitle")
        for i in (1, 2):
            set_text_slot(f"col{i}_body", spec.get(f"col{i}_body"))
        return

    if archetype_id in {"pillars_3", "pillars_4"}:
        n = 3 if archetype_id == "pillars_3" else 4
        for i in range(1, n + 1):
            set_text_slot(f"pillar{i}_body", spec.get(f"pillar{i}_body"))
        return

    if archetype_id in {"table", "version_page"}:
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

    if archetype_id == "title_subtitle":
        set_text_slot("subtitle", spec.get("subtitle"), style_key="subtitle")
        return

    if archetype_id == "title_only_freeform":
        return

    if archetype_id == "picture_compare":
        left = spec.get("left") or {}
        right = spec.get("right") or {}

        if isinstance(left, dict):
            _set_slot_image(
                slide,
                archetype_id,
                archetype_spec,
                "left_image",
                _resolve_image_path(base_dir, left.get("image")),
                slide_w_emu=slide_w_emu,
                slide_h_emu=slide_h_emu,
                context=f"archetype={archetype_id} slot=left_image",
            )
            set_text_slot("left_title", left.get("title"), style_key="body")
            set_text_slot("left_body", left.get("body"), style_key="body")

        if isinstance(right, dict):
            _set_slot_image(
                slide,
                archetype_id,
                archetype_spec,
                "right_image",
                _resolve_image_path(base_dir, right.get("image")),
                slide_w_emu=slide_w_emu,
                slide_h_emu=slide_h_emu,
                context=f"archetype={archetype_id} slot=right_image",
            )
            set_text_slot("right_title", right.get("title"), style_key="body")
            set_text_slot("right_body", right.get("body"), style_key="body")
        return

    if archetype_id == "agenda_with_image":
        _set_slot_image(
            slide,
            archetype_id,
            archetype_spec,
            "image",
            _resolve_image_path(base_dir, spec.get("image")),
            slide_w_emu=slide_w_emu,
            slide_h_emu=slide_h_emu,
            context=f"archetype={archetype_id} slot=image",
        )

        items = spec.get("items") or []
        has_item_slots = _slot_spec(archetype_spec, "item1_body") is not None
        if has_item_slots and isinstance(items, list):
            for idx, it in enumerate(items, start=1):
                if not isinstance(it, dict):
                    continue
                marker = it.get("marker")
                body = it.get("body")
                if not (isinstance(marker, str) and marker):
                    marker = str(idx)
                if isinstance(body, str) and body:
                    if _slot_spec(archetype_spec, f"item{idx}_marker") is not None:
                        set_text_slot(f"item{idx}_marker", str(marker), style_key="body")
                    set_text_slot(f"item{idx}_body", body, style_key="body")
            return

        lines: list[str] = []
        if isinstance(items, list):
            for it in items:
                if not isinstance(it, dict):
                    continue
                marker = it.get("marker")
                body = it.get("body")
                if isinstance(body, str) and body:
                    if isinstance(marker, str) and marker:
                        lines.append(f"{marker} {body}")
                    else:
                        lines.append(body)

        if _slot_spec(archetype_spec, "bullets") is not None:
            proxy = dict(spec)
            proxy["bullets"] = lines
            _render_title_and_bullets(slide, proxy, styles, archetype_spec, archetype_id, slide_w_emu=slide_w_emu, slide_h_emu=slide_h_emu)
        else:
            set_text_slot("body", "\n".join(lines), style_key="body")
        return

    if archetype_id in {"three_col_with_subtitle", "three_col_with_icons", "five_col_with_icons"}:
        items = spec.get("items") or []
        if archetype_id == "three_col_with_subtitle":
            set_text_slot("subtitle", spec.get("subtitle"), style_key="subtitle")

        if not isinstance(items, list):
            items = []

        for idx, it in enumerate(items, start=1):
            if not isinstance(it, dict):
                continue

            if archetype_id == "three_col_with_subtitle":
                set_text_slot(f"col{idx}_title", it.get("title"), style_key="body")
                set_text_slot(f"col{idx}_body", it.get("body"), style_key="body")
            elif archetype_id == "three_col_with_icons":
                set_text_slot(f"col{idx}_title", it.get("title"), style_key="body")
                set_text_slot(f"col{idx}_body", it.get("body"), style_key="body")
                set_text_slot(f"col{idx}_caption", it.get("caption"), style_key="body")
                _set_slot_image(
                    slide,
                    archetype_id,
                    archetype_spec,
                    f"col{idx}_icon",
                    _resolve_image_path(base_dir, it.get("icon")),
                    slide_w_emu=slide_w_emu,
                    slide_h_emu=slide_h_emu,
                    context=f"archetype={archetype_id} slot=col{idx}_icon",
                )
            else:
                set_text_slot(f"item{idx}_body", it.get("body"), style_key="body")
                _set_slot_image(
                    slide,
                    archetype_id,
                    archetype_spec,
                    f"item{idx}_icon",
                    _resolve_image_path(base_dir, it.get("icon")),
                    slide_w_emu=slide_w_emu,
                    slide_h_emu=slide_h_emu,
                    context=f"archetype={archetype_id} slot=item{idx}_icon",
                )
        return

    raise RenderingError(f"Extended archetype '{archetype_id}' is not implemented")
