from __future__ import annotations

"""Extended archetype inference (v1.1).

This module adds best-effort inference for the v1.1 extended archetype library.

Approach: score bootstrapped `layout__*` archetypes based on placeholder inventory
(as recorded during bootstrap) and choose the best layout for each extended archetype.

All outputs are reviewable and marked `generated: true` with inference notes.
"""

from typing import Any


def _count_slot(a: dict[str, Any], *, want_type: str | None = None, want_name_prefix: str | None = None) -> int:
    n = 0
    for s in a.get("slots") or []:
        if not isinstance(s, dict):
            continue
        if want_type is not None and s.get("type") != want_type:
            continue
        if want_name_prefix is not None:
            name = s.get("name")
            if not isinstance(name, str) or not name.startswith(want_name_prefix):
                continue
        n += 1
    return n


def _has_title(a: dict[str, Any]) -> bool:
    for s in a.get("slots") or []:
        if isinstance(s, dict) and s.get("name") == "title":
            return True
    return False


def _placeholder_idxs(a: dict[str, Any]) -> list[int]:
    out: list[int] = []
    for s in a.get("slots") or []:
        if not isinstance(s, dict):
            continue
        idx = s.get("placeholder_idx")
        if isinstance(idx, int):
            out.append(idx)
    return sorted(set(out))


def infer_extended_mappings(template_spec: dict[str, Any]) -> dict[str, Any]:
    archetypes = [a for a in (template_spec.get("archetypes") or []) if isinstance(a, dict)]

    # Candidate pool is bootstrapped layout inventory.
    candidates = [a for a in archetypes if isinstance(a.get("id"), str) and str(a.get("id")).startswith("layout__")]

    def pick_best(scorer):
        best = None
        for a in candidates:
            score, reason = scorer(a)
            if score <= 0:
                continue
            if best is None or score > best[0]:
                best = (score, reason, a)
        return best

    def score_n_cols(ncols: int):
        def _score(a: dict[str, Any]):
            if not _has_title(a):
                return 0.0, "missing title"
            # Bootstrapper maps BODY to type "bullets" with name "body".
            bodies = _count_slot(a, want_name_prefix="body") + _count_slot(a, want_type="bullets")
            images = _count_slot(a, want_type="image")
            # Prefer many text/bodies and no images.
            score = 5.0 + 2.0 * min(bodies, ncols) - 2.5 * images
            # Penalize if too few bodies.
            if bodies < ncols:
                score -= (ncols - bodies) * 3.0
            return score, f"bodies={bodies} images={images} idxs={_placeholder_idxs(a)}"

        return _score

    # Heuristics are intentionally simple for v1.1.
    picks = {
        "two_col": pick_best(score_n_cols(2)),
        "three_col": pick_best(score_n_cols(3)),
        "four_col": pick_best(score_n_cols(4)),
    }

    def score_table(a: dict[str, Any]):
        if not _has_title(a):
            return 0.0, "missing title"
        unknown = _count_slot(a, want_type="unknown")
        bodies = _count_slot(a, want_type="bullets") + _count_slot(a, want_name_prefix="body")
        # Table placeholders are not currently represented in bootstrapper; we approximate by "unknown".
        score = 4.0 + 2.0 * min(unknown, 1) + 1.0 * min(bodies, 1)
        return score, f"unknown={unknown} bodies={bodies} idxs={_placeholder_idxs(a)}"

    picks["table"] = pick_best(score_table)

    def score_table_plus_desc(a: dict[str, Any]):
        if not _has_title(a):
            return 0.0, "missing title"
        unknown = _count_slot(a, want_type="unknown")
        bodies = _count_slot(a, want_type="bullets") + _count_slot(a, want_name_prefix="body")
        images = _count_slot(a, want_type="image")
        score = 5.0 + 2.0 * min(unknown, 1) + 2.0 * min(bodies, 2) - 2.0 * images
        return score, f"unknown={unknown} bodies={bodies} images={images} idxs={_placeholder_idxs(a)}"

    picks["table_plus_description"] = pick_best(score_table_plus_desc)

    def score_timeline(a: dict[str, Any]):
        if not _has_title(a):
            return 0.0, "missing title"
        bodies = _count_slot(a, want_type="bullets") + _count_slot(a, want_name_prefix="body")
        # Timeline often has multiple similar placeholders.
        score = 4.0 + 1.5 * min(bodies, 5)
        return score, f"bodies={bodies} idxs={_placeholder_idxs(a)}"

    picks["timeline_horizontal"] = pick_best(score_timeline)

    # Pillars are essentially multi-column with emphasis; reuse the column heuristics for now.
    def score_pillars(n: int):
        sc = score_n_cols(n)

        def _score(a: dict[str, Any]):
            base, reason = sc(a)
            # Prefer templates with title + many bodies and no images.
            return base + 0.5, reason

        return _score

    picks["pillars_3"] = pick_best(score_pillars(3))
    picks["pillars_4"] = pick_best(score_pillars(4))

    # Build generated archetypes based on picks.
    generated: list[dict[str, Any]] = []
    for ext_id, best in picks.items():
        if not best:
            continue
        score, reason, src = best
        layout = src.get("layout")
        if not isinstance(layout, str) or not layout:
            continue

        # Minimal slot set for v1.1 mapping: just bodies; caller can refine with hints/interactive.
        slots: list[dict[str, Any]] = [{"name": "title", "type": "text", "required": True, "placeholder_idx": (src.get("slots") or [{}])[0].get("placeholder_idx", 0)}]

        def add_slot(name: str):
            # Choose the next placeholder idx from the source that isn't title.
            for s in src.get("slots") or []:
                if not isinstance(s, dict):
                    continue
                if s.get("name") == "title":
                    continue
                idx = s.get("placeholder_idx")
                if isinstance(idx, int) and all(x.get("placeholder_idx") != idx for x in slots if isinstance(x, dict)):
                    slots.append({"name": name, "type": "text", "required": True, "placeholder_idx": idx})
                    return
            slots.append({"name": name, "type": "text", "required": True})

        if ext_id in {"two_col", "three_col", "four_col"}:
            n = {"two_col": 2, "three_col": 3, "four_col": 4}[ext_id]
            for i in range(1, n + 1):
                add_slot(f"col{i}_body")
        elif ext_id in {"pillars_3", "pillars_4"}:
            n = 3 if ext_id == "pillars_3" else 4
            for i in range(1, n + 1):
                add_slot(f"pillar{i}_body")
        elif ext_id == "table":
            add_slot("table_text")
        elif ext_id == "table_plus_description":
            add_slot("table_text")
            add_slot("body")
        elif ext_id == "timeline_horizontal":
            add_slot("milestone1_body")

        generated.append(
            {
                "id": ext_id,
                "layout": layout,
                "description": f"Generated extended mapping from '{src.get('id')}' (score={score:.1f})",
                "generated": True,
                "inference": {"source_archetype": src.get("id"), "score": score, "reason": reason},
                "slots": slots,
            }
        )

    out = dict(template_spec)
    # Remove existing extended archetypes if present; keep other archetypes.
    ext_ids = set(picks.keys())
    kept = [a for a in archetypes if a.get("id") not in ext_ids]
    out["archetypes"] = generated + kept

    deck = dict(out.get("deck") or {})
    supported = list(deck.get("supported_archetypes") or [])
    for ext_id in ext_ids:
        if ext_id not in supported:
            supported.append(ext_id)
    deck["supported_archetypes"] = supported
    out["deck"] = deck

    return out
