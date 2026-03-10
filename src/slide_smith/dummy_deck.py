from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from slide_smith.template_loader import load_template_spec


@dataclass(frozen=True)
class DummyDeckResult:
    deck_spec: dict[str, Any]


def _dummy_slide_for_archetype(archetype_id: str) -> dict[str, Any]:
    # For known archetypes, provide richer dummy content.
    if archetype_id == "title":
        return {"archetype": "title", "title": "Dummy Title", "subtitle": "Subtitle placeholder"}
    if archetype_id == "section":
        return {"archetype": "section", "title": "Section Heading", "subtitle": "Section subtitle"}
    if archetype_id == "title_and_bullets":
        return {
            "archetype": "title_and_bullets",
            "title": "Bullets Slide",
            "bullets": ["First bullet", "Second bullet", "Third bullet"],
            "notes": "Dummy notes for review",
        }
    if archetype_id == "image_left_text_right":
        # Avoid requiring an image path; keep it renderable without assets.
        return {
            "archetype": "image_left_text_right",
            "title": "Image + Text",
            "body": "(No image in dummy spec; add image.path to test images)",
        }

    # Bootstrapped / unknown archetypes: keep minimal fields.
    return {
        "archetype": archetype_id,
        "title": f"Dummy title ({archetype_id})",
        "subtitle": "Dummy subtitle",
        "body": "Dummy body",
        "bullets": ["Bullet 1", "Bullet 2"],
    }


def make_dummy_deck_spec(template_id: str, templates_dir: str | None = None) -> DummyDeckResult:
    spec = load_template_spec(template_id, templates_dir=templates_dir)

    archetypes = spec.get("archetypes") or []
    slides: list[dict[str, Any]] = []

    for a in archetypes:
        if not isinstance(a, dict):
            continue
        aid = a.get("id")
        if not isinstance(aid, str) or not aid:
            continue
        slides.append(_dummy_slide_for_archetype(aid))

    deck_spec = {
        "version": "1.0",
        "meta": {"title": "Slide Smith Dummy Deck", "template": template_id},
        "slides": slides,
    }

    return DummyDeckResult(deck_spec=deck_spec)
