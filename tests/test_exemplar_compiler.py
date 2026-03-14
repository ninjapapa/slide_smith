from __future__ import annotations

import json
from pathlib import Path

from slide_smith.exemplar_compiler import compile_exemplar


def test_compile_exemplar_produces_deck_spec_for_fixture() -> None:
    fx = Path(__file__).resolve().parents[0] / "fixtures" / "v1_2_exemplar_first"
    plan = json.loads((fx / "slide_plan" / "expected.slide.plan.json").read_text(encoding="utf-8"))
    profile = json.loads((fx / "style_profile" / "sample.style.profile.json").read_text(encoding="utf-8"))

    res = compile_exemplar(slide_plan=plan, style_profile=profile)
    spec = res.deck_spec

    assert spec["version"] == "1"
    assert spec["reference"]["path"] == "ref.pptx"
    assert isinstance(spec.get("sha1"), str) and len(spec["sha1"]) == 40

    assert len(spec["slides"]) == len(plan["slides"])

    # Title slide should bind to TitleSlide
    assert spec["slides"][0]["layoutId"].startswith("layout:")

    # Bullets slide should fill a body placeholder
    fills1 = spec["slides"][1]["fills"]
    assert any("text" in f and "One" in f["text"] for f in fills1)


def test_compile_exemplar_errors_when_no_layout_matches() -> None:
    plan = {"version": "1", "slides": [{"intent": "two_column", "fields": {"title": "X"}}]}
    profile = {
        "version": "1",
        "reference": {"path": "ref.pptx", "sha256": "abc"},
        "layouts": [
            {
                "layoutId": "layout:only-title",
                "name": "Only Title",
                "placeholders": [{"type": "title", "idx": 0, "bbox": {"x": 0, "y": 0, "w": 1, "h": 1}}],
            }
        ],
    }

    try:
        compile_exemplar(slide_plan=plan, style_profile=profile)
        assert False, "expected error"
    except ValueError as e:
        assert "No compatible layout" in str(e)
