from __future__ import annotations

from slide_smith.template_mapper import infer_standard_mappings
from slide_smith.template_mapper_extended import infer_extended_mappings


def _layout_archetype(
    aid: str,
    layout: str,
    *,
    title: bool = True,
    subtitle: bool = False,
    bullets: bool = False,
    body: bool = False,
    images: int = 0,
) -> dict:
    slots: list[dict] = []
    if title:
        slots.append({"name": "title", "type": "text", "placeholder_idx": 0})
    if subtitle:
        slots.append({"name": "subtitle", "type": "text", "placeholder_idx": 10})
    if bullets:
        slots.append({"name": "bullets", "type": "bullets", "placeholder_idx": 11})
    if body:
        slots.append({"name": "body", "type": "text", "placeholder_idx": 12})
    for i in range(images):
        slots.append({"name": f"image{i+1}", "type": "image", "placeholder_idx": 20 + i})
    return {"id": aid, "layout": layout, "slots": slots}


def _slot_names(archetype: dict) -> set[str]:
    out: set[str] = set()
    for s in archetype.get("slots") or []:
        if isinstance(s, dict) and isinstance(s.get("name"), str):
            out.add(s["name"])
    return out


def test_extended_mapper_emits_required_slot_names_for_items_archetypes() -> None:
    """Contract: generated extended archetypes must use canonical slot names.

    This doesn't validate placeholder idx correctness; it just ensures naming is stable.
    """

    spec = {
        "archetypes": [
            # candidates
            _layout_archetype("layout__3icons", "Content: 3 columns with icons", body=True, images=3),
            _layout_archetype("layout__5icons", "Content: 5 columns with icon", body=True, images=5),
            _layout_archetype("layout__compare", "Content: picture compare", body=True, images=2),
        ]
    }

    out = infer_extended_mappings(spec)
    by_id = {a["id"]: a for a in out["archetypes"] if isinstance(a, dict) and isinstance(a.get("id"), str)}

    # three_col_with_icons
    a = by_id["three_col_with_icons"]
    names = _slot_names(a)
    for i in (1, 2, 3):
        assert f"col{i}_icon" in names
        assert f"col{i}_title" in names
        assert f"col{i}_body" in names
        # caption is optional but should exist as a slot in generated skeleton
        assert f"col{i}_caption" in names

    # five_col_with_icons
    a = by_id["five_col_with_icons"]
    names = _slot_names(a)
    for i in (1, 2, 3, 4, 5):
        assert f"item{i}_icon" in names
        assert f"item{i}_body" in names

    # picture_compare
    a = by_id["picture_compare"]
    names = _slot_names(a)
    for n in ("left_image", "right_image", "left_title", "left_body", "right_title", "right_body"):
        assert n in names


def test_standard_mapper_emits_expected_new_base_archetype_ids() -> None:
    spec = {
        "archetypes": [
            _layout_archetype("layout__cover", "Cover: light mode", subtitle=True),
            _layout_archetype("layout__session", "Session"),
            _layout_archetype("layout__content_box", "Content: title content-box", bullets=True),
            _layout_archetype("layout__img", "Content: column + image", body=True, images=1),
            _layout_archetype("layout__sub_box", "Content: title subtitle content box", subtitle=True, bullets=True),
        ]
    }

    out = infer_standard_mappings(spec)
    by_id = {a["id"]: a for a in out["archetypes"] if isinstance(a, dict) and isinstance(a.get("id"), str)}

    # Ensure we generate the new base ids using canonical names.
    assert "text_with_image" in by_id
    assert "title_subtitle_and_bullets" in by_id
