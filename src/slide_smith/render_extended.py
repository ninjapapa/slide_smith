from __future__ import annotations

from pathlib import Path
from typing import Any

from slide_smith.render_core import _render_title_and_bullets
from slide_smith.render_support import (
    RenderingError,
    _resolve_image_path,
    _set_slot_image,
    _set_slot_text,
    _slot_spec,
)


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
    """Renderer for the current stable non-core layouts."""

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
        context=f"layout_id={archetype_id} slot=title",
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
            context=f"layout_id={archetype_id} slot={slot_name}",
        )

    if archetype_id == "two_col":
        for i in (1, 2):
            set_text_slot(f"col{i}_body", spec.get(f"col{i}_body"))
        return

    if archetype_id == "version_page":
        set_text_slot("table_text", spec.get("table_text"), style_key="body")
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
                context=f"layout_id={archetype_id} slot=left_image",
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
                context=f"layout_id={archetype_id} slot=right_image",
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
            context=f"layout_id={archetype_id} slot=image",
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

    if archetype_id == "three_col_with_icons":
        items = spec.get("items") or []
        if not isinstance(items, list):
            items = []

        for idx, it in enumerate(items, start=1):
            if not isinstance(it, dict):
                continue
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
                context=f"layout_id={archetype_id} slot=col{idx}_icon",
            )
        return

    raise RenderingError(f"Layout '{archetype_id}' is retired and no longer supported")
