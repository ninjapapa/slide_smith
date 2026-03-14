from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Iterable


@dataclass(frozen=True)
class CompileExemplarResult:
    deck_spec: dict[str, Any]


def _norm_ph_type(t: str) -> str:
    return (t or "").strip().lower()


def _layout_signature(layout: dict[str, Any]) -> dict[str, Any]:
    """Compute a normalized signature for deterministic layout matching."""

    placeholders = layout.get("placeholders") or []
    counts: dict[str, int] = {}

    for ph in placeholders:
        t = _norm_ph_type(str(ph.get("type", "")))
        if not t:
            continue
        counts[t] = counts.get(t, 0) + 1

    # provide consistent ordering
    return {
        "counts": {k: counts[k] for k in sorted(counts.keys())},
    }


def _ph_sort_key(ph: dict[str, Any]) -> tuple[int, str]:
    idx = ph.get("idx")
    try:
        idx_i = int(idx)
    except Exception:
        idx_i = 10**9
    return (idx_i, str(ph.get("type", "")))


def _choose_layout(
    *,
    intent: str,
    layouts: list[dict[str, Any]],
) -> dict[str, Any]:
    """Choose the best layout for an intent.

    Deterministic tie-breaking:
    1) tighter placeholder match (fewest unused placeholders)
    2) then stable layoutId lexical
    """

    intent = (intent or "").strip().lower()

    def score(layout: dict[str, Any]) -> tuple[int, int, str]:
        # smaller is better
        phs = layout.get("placeholders") or []
        sig = _layout_signature(layout)
        counts = sig["counts"]

        title_n = counts.get("title", 0) + counts.get("center_title", 0)
        body_n = counts.get("body", 0)
        pic_n = counts.get("picture", 0)

        ok = False
        if intent == "title":
            ok = title_n >= 1
        elif intent in ("section",):
            ok = title_n >= 1
        elif intent in ("bullets",):
            ok = title_n >= 1 and body_n >= 1
        elif intent in ("image",):
            ok = title_n >= 0 and pic_n >= 1
        elif intent in ("two_column",):
            ok = title_n >= 1 and (body_n >= 2 or (body_n >= 1 and pic_n >= 1))

        if not ok:
            return (10**6, 10**6, str(layout.get("layoutId", "")))

        # unused placeholders: count placeholders beyond what we can fill for the intent
        # very simple v1.2 heuristic.
        used = 0
        if intent == "title":
            used = 1
        elif intent == "bullets":
            used = 2
        elif intent == "image":
            used = 1
        elif intent == "two_column":
            used = 3
        else:
            used = 1

        unused = max(0, len(phs) - used)

        # Prefer fewer placeholders overall.
        return (unused, len(phs), str(layout.get("layoutId", "")))

    ranked = sorted(layouts, key=score)
    best = ranked[0] if ranked else None
    if not best or score(best)[0] >= 10**6:
        # build helpful message
        candidates = []
        for l in layouts:
            sig = _layout_signature(l)
            candidates.append({"layoutId": l.get("layoutId"), "name": l.get("name"), "counts": sig["counts"]})
        raise ValueError(
            "No compatible layout found for intent=%r. Candidate layout signatures: %s"
            % (intent, json.dumps(candidates, sort_keys=True))
        )

    return best


def _select_placeholder(
    layout: dict[str, Any], *, accept_types: Iterable[str]
) -> dict[str, Any] | None:
    accept = {_norm_ph_type(t) for t in accept_types}
    phs = list(layout.get("placeholders") or [])
    for ph in sorted(phs, key=_ph_sort_key):
        if _norm_ph_type(str(ph.get("type", ""))) in accept:
            return ph
    return None


def compile_exemplar(*, slide_plan: dict[str, Any], style_profile: dict[str, Any]) -> CompileExemplarResult:
    """Compile SlidePlan + StyleProfile into an exemplar-first DeckSpec.

    Output deck spec is intentionally minimal and placeholder-based.
    """

    if not isinstance(slide_plan, dict):
        raise TypeError("slide_plan must be dict")
    if not isinstance(style_profile, dict):
        raise TypeError("style_profile must be dict")

    layouts = style_profile.get("layouts") or []
    if not isinstance(layouts, list) or not layouts:
        raise ValueError("style_profile.layouts must be a non-empty list")

    reference = style_profile.get("reference") or {}
    ref_path = reference.get("path")
    ref_sha = reference.get("sha256")

    out_slides: list[dict[str, Any]] = []

    for i, s in enumerate(slide_plan.get("slides") or []):
        if not isinstance(s, dict):
            raise TypeError(f"slide_plan.slides[{i}] must be dict")

        intent = str(s.get("intent", "")).strip().lower()
        fields = s.get("fields") or {}
        if not isinstance(fields, dict):
            raise TypeError(f"slide_plan.slides[{i}].fields must be dict")

        layout = _choose_layout(intent=intent, layouts=layouts)

        fills: list[dict[str, Any]] = []

        # Title fill
        title_val = fields.get("title")
        if isinstance(title_val, str) and title_val.strip():
            ph_title = _select_placeholder(layout, accept_types=["title", "center_title"]) or _select_placeholder(
                layout, accept_types=["body"]
            )
            if ph_title is not None:
                fills.append(
                    {
                        "placeholder": {"type": ph_title.get("type"), "idx": int(ph_title.get("idx"))},
                        "text": title_val.strip(),
                    }
                )

        # Bullets fill into a body placeholder
        if intent == "bullets":
            bullets = fields.get("bullets")
            if isinstance(bullets, list):
                btxt = "\n".join([str(b).strip() for b in bullets if str(b).strip()])
                if btxt:
                    ph_body = _select_placeholder(layout, accept_types=["body"])
                    if ph_body is None:
                        raise ValueError(f"No body placeholder for bullets slide at index {i}")
                    fills.append(
                        {
                            "placeholder": {"type": ph_body.get("type"), "idx": int(ph_body.get("idx"))},
                            "text": btxt,
                        }
                    )

        # Image fill into picture placeholder
        if intent == "image":
            img = fields.get("image")
            if isinstance(img, dict) and isinstance(img.get("path"), str):
                ph_pic = _select_placeholder(layout, accept_types=["picture"])
                if ph_pic is None:
                    raise ValueError(f"No picture placeholder for image slide at index {i}")
                fills.append(
                    {
                        "placeholder": {"type": ph_pic.get("type"), "idx": int(ph_pic.get("idx"))},
                        "image": {"path": img["path"], **({"alt": img.get("alt")} if img.get("alt") else {})},
                    }
                )

        out_slides.append({"layoutId": layout.get("layoutId"), "fills": fills})

    deck_spec: dict[str, Any] = {
        "version": "1",
        "reference": {"path": ref_path, "sha256": ref_sha},
        "slides": out_slides,
    }

    # Deterministic / JSON-safe
    raw = json.dumps(deck_spec, sort_keys=True, separators=(",", ":")).encode("utf-8")
    deck_spec["sha1"] = hashlib.sha1(raw).hexdigest()

    return CompileExemplarResult(deck_spec=deck_spec)
