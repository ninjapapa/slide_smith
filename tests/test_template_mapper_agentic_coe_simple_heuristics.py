from __future__ import annotations

from slide_smith.template_mapper import infer_standard_mappings
from slide_smith.template_mapper_extended import infer_extended_mappings


def _layout_archetype(aid: str, layout: str, *, title: bool = True, subtitle: bool = False, bullets: bool = False, body: bool = False, image: int = 0):
    slots = []
    if title:
        slots.append({"name": "title", "type": "text", "placeholder_idx": 0})
    if subtitle:
        slots.append({"name": "subtitle", "type": "text", "placeholder_idx": 10})
    if bullets:
        slots.append({"name": "bullets", "type": "bullets", "placeholder_idx": 11})
    if body:
        slots.append({"name": "body", "type": "text", "placeholder_idx": 12})
    for i in range(image):
        slots.append({"name": f"image{i+1}", "type": "image", "placeholder_idx": 20 + i})
    return {"id": aid, "layout": layout, "slots": slots}


def test_standard_mapper_prefers_cover_for_title_and_session_for_section() -> None:
    spec = {
        "archetypes": [
            _layout_archetype("layout__cover", "Cover: light mode", subtitle=True),
            _layout_archetype("layout__session", "Session"),
        ]
    }
    out = infer_standard_mappings(spec)
    by_id = {a["id"]: a for a in out["archetypes"] if isinstance(a, dict) and isinstance(a.get("id"), str)}

    assert by_id["title"]["layout"] == "Cover: light mode"
    assert by_id["section"]["layout"] == "Session"


def test_standard_mapper_prefers_content_box_for_title_and_bullets() -> None:
    spec = {
        "archetypes": [
            _layout_archetype("layout__content_box", "Content: title content-box", bullets=True),
            _layout_archetype("layout__subtitle_only", "Content: title subtitle only", subtitle=True, bullets=True),
        ]
    }
    out = infer_standard_mappings(spec)
    by_id = {a["id"]: a for a in out["archetypes"] if isinstance(a, dict) and isinstance(a.get("id"), str)}

    assert by_id["title_and_bullets"]["layout"] == "Content: title content-box"


def test_standard_mapper_prefers_column_image_for_text_with_image_over_agenda() -> None:
    spec = {
        "archetypes": [
            _layout_archetype("layout__agenda", "Agenda: image", body=True, image=1),
            _layout_archetype("layout__col_img", "Content: column + image", body=True, image=1),
        ]
    }
    out = infer_standard_mappings(spec)
    by_id = {a["id"]: a for a in out["archetypes"] if isinstance(a, dict) and isinstance(a.get("id"), str)}

    assert by_id["text_with_image"]["layout"] == "Content: column + image"


def test_extended_mapper_prefers_explicit_3_col_icons_and_picture_compare() -> None:
    spec = {
        "archetypes": [
            _layout_archetype("layout__3icons", "Content: 3 columns with icons", body=True, image=3),
            _layout_archetype("layout__5icons", "Content: 5 columns with icon", body=True, image=5),
            _layout_archetype("layout__compare", "Content: picture compare", body=True, image=2),
        ]
    }

    out = infer_extended_mappings(spec)
    by_id = {a["id"]: a for a in out["archetypes"] if isinstance(a, dict) and isinstance(a.get("id"), str)}

    assert by_id["three_col_with_icons"]["layout"] == "Content: 3 columns with icons"
    assert by_id["picture_compare"]["layout"] == "Content: picture compare"
