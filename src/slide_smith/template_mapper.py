from __future__ import annotations

"""Template mapping utilities.

This module helps bridge the gap between a *bootstrapped* template (raw layout
inventory) and a *standard-compatible* template usable for normal deck creation.

It intentionally keeps heuristics conservative and reviewable.
"""

from dataclasses import dataclass
from typing import Any, Iterable


STANDARD_ARCHETYPES: dict[str, dict[str, Any]] = {
    "title": {
        "required_slots": [
            {"name": "title", "type": "text", "required": True},
            {"name": "subtitle", "type": "text", "required": False},
        ]
    },
    "section": {
        "required_slots": [
            {"name": "title", "type": "text", "required": True},
            # section can use subtitle OR body; we keep subtitle optional.
            {"name": "subtitle", "type": "text", "required": False},
            {"name": "body", "type": "text", "required": False},
        ]
    },
    "title_and_bullets": {
        "required_slots": [
            {"name": "title", "type": "text", "required": True},
            {"name": "bullets", "type": "bullet_list", "required": True},
        ]
    },
    "image_left_text_right": {
        "required_slots": [
            {"name": "title", "type": "text", "required": True},
            {"name": "image", "type": "image", "required": True},
            {"name": "body", "type": "text", "required": True},
        ]
    },
}


@dataclass(frozen=True)
class InferenceCandidate:
    archetype_id: str
    score: float
    reason: str


def _slot_counts(archetype: dict[str, Any]) -> dict[str, int]:
    counts: dict[str, int] = {"title": 0, "subtitle": 0, "body": 0, "bullets": 0, "image": 0, "unknown": 0}
    for s in archetype.get("slots") or []:
        if not isinstance(s, dict):
            continue
        n = s.get("name")
        t = s.get("type")
        if n == "title":
            counts["title"] += 1
        elif n == "subtitle":
            counts["subtitle"] += 1
        elif n == "image" or t == "image":
            counts["image"] += 1
        elif n == "bullets" or t in {"bullets", "bullet_list"}:
            counts["bullets"] += 1
        elif n == "body" or t == "text":
            counts["body"] += 1
        else:
            counts["unknown"] += 1
    return counts


def _first_slot_idx(archetype: dict[str, Any], *, want_name: str | None = None, want_type: str | None = None) -> int | None:
    for s in archetype.get("slots") or []:
        if not isinstance(s, dict):
            continue
        if want_name is not None and s.get("name") != want_name:
            continue
        if want_type is not None and s.get("type") != want_type:
            continue
        idx = s.get("placeholder_idx")
        if isinstance(idx, int):
            return idx
    return None


def _pick_best(archetypes: Iterable[dict[str, Any]], scorer) -> InferenceCandidate | None:
    best: InferenceCandidate | None = None
    for a in archetypes:
        if not isinstance(a, dict):
            continue
        aid = a.get("id")
        if not isinstance(aid, str) or not aid:
            continue
        score, reason = scorer(a)
        if score <= 0:
            continue
        cand = InferenceCandidate(archetype_id=aid, score=score, reason=reason)
        if best is None or cand.score > best.score:
            best = cand
    return best


def infer_standard_mappings(template_spec: dict[str, Any]) -> dict[str, Any]:
    """Return an updated template spec with best-effort standard archetypes added.

    - Keeps existing archetypes (bootstrapped layout__* inventory).
    - Adds standard archetype entries when a decent match is found.
    - Marks generated archetypes with `generated: true` and includes inference notes.

    This function is deterministic and does not prompt.
    """

    archetypes = [a for a in (template_spec.get("archetypes") or []) if isinstance(a, dict)]

    def score_title(a: dict[str, Any]):
        c = _slot_counts(a)
        # title: needs a title placeholder; prefer having subtitle; penalize image.
        if c["title"] < 1:
            return 0.0, "missing title slot"
        score = 5 + 2 * min(c["subtitle"], 1) - 2 * c["image"] - 1 * c["bullets"]
        return float(score), f"title={c['title']} subtitle={c['subtitle']} image={c['image']} bullets={c['bullets']}"

    def score_section(a: dict[str, Any]):
        c = _slot_counts(a)
        if c["title"] < 1:
            return 0.0, "missing title slot"
        # section often looks like title slide but can be simpler.
        score = 4 + 1 * min(c["subtitle"], 1) + 1 * min(c["body"], 1) - 2 * c["image"]
        return float(score), f"title={c['title']} subtitle={c['subtitle']} body={c['body']} image={c['image']}"

    def score_title_and_bullets(a: dict[str, Any]):
        c = _slot_counts(a)
        if c["title"] < 1:
            return 0.0, "missing title slot"
        if c["bullets"] < 1 and c["body"] < 1:
            return 0.0, "missing bullets/body slot"
        score = 6 + 2 * min(c["bullets"], 1) + 1 * min(c["body"], 1) - 3 * c["image"]
        return float(score), f"title={c['title']} bullets={c['bullets']} body={c['body']} image={c['image']}"

    def score_image_left_text_right(a: dict[str, Any]):
        c = _slot_counts(a)
        if c["title"] < 1:
            return 0.0, "missing title slot"
        if c["image"] < 1:
            return 0.0, "missing image slot"
        if c["body"] < 1 and c["bullets"] < 1:
            return 0.0, "missing body slot"
        score = 7 + 2 * min(c["image"], 1) + 1 * min(c["body"], 1) + 1 * min(c["bullets"], 1)
        return float(score), f"title={c['title']} image={c['image']} body={c['body']} bullets={c['bullets']}"

    picks: dict[str, InferenceCandidate | None] = {
        "title": _pick_best(archetypes, score_title),
        "section": _pick_best(archetypes, score_section),
        "title_and_bullets": _pick_best(archetypes, score_title_and_bullets),
        "image_left_text_right": _pick_best(archetypes, score_image_left_text_right),
    }

    # Build new archetype entries.
    generated: list[dict[str, Any]] = []

    by_id = {a.get("id"): a for a in archetypes if isinstance(a.get("id"), str)}

    for std_id, cand in picks.items():
        if cand is None:
            continue
        src = by_id.get(cand.archetype_id)
        if not src:
            continue
        layout = src.get("layout")
        if not isinstance(layout, str) or not layout:
            continue

        slots: list[dict[str, Any]] = []
        for slot_req in STANDARD_ARCHETYPES[std_id]["required_slots"]:
            name = slot_req["name"]
            stype = slot_req["type"]
            idx: int | None = None
            # Prefer name match from bootstrap (`title`, `subtitle`, `image`, `body`).
            if name in {"title", "subtitle", "image", "body"}:
                idx = _first_slot_idx(src, want_name=name)
            # For bullets, bootstrap uses type "bullets".
            if idx is None and name == "bullets":
                idx = _first_slot_idx(src, want_type="bullets")
            # fallback: accept first text-like slot.
            if idx is None and name in {"subtitle", "body"}:
                idx = _first_slot_idx(src, want_type="text")

            out = {
                "name": name,
                "type": stype,
                "required": bool(slot_req.get("required", False)),
            }
            if idx is not None:
                out["placeholder_idx"] = idx
            slots.append(out)

        generated.append(
            {
                "id": std_id,
                "layout": layout,
                "description": f"Generated mapping from '{cand.archetype_id}' (score={cand.score:.1f})",
                "generated": True,
                "inference": {"source_archetype": cand.archetype_id, "score": cand.score, "reason": cand.reason},
                "slots": slots,
            }
        )

    # Merge into output spec: replace existing standard archetypes if present.
    existing = [a for a in archetypes if a.get("id") not in set(STANDARD_ARCHETYPES.keys())]
    out_spec = dict(template_spec)
    out_spec["archetypes"] = generated + existing

    deck = dict(out_spec.get("deck") or {})
    deck["supported_archetypes"] = list(STANDARD_ARCHETYPES.keys())
    out_spec["deck"] = deck

    return out_spec
