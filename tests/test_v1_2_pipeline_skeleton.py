from __future__ import annotations

from pathlib import Path

import pytest


@pytest.mark.xfail(reason="v1.2 exemplar-first pipeline not implemented yet")
def test_v1_2_pipeline_fixture_contracts_exist() -> None:
    root = Path(__file__).resolve().parents[0]
    fx = root / "fixtures" / "v1_2_exemplar_first"

    assert (fx / "markdown" / "sample.md").exists()
    assert (fx / "style_profile" / "sample.style.profile.json").exists()
    assert (fx / "slide_plan" / "expected.slide.plan.json").exists()

    # Future: once commands exist, this test becomes:
    # - plan(sample.md) == expected.slide.plan.json
    # - analyze(ref.pptx) emits stable style.profile.json
    # - compile(plan, profile) produces deck.spec.json
    # - render(spec, ref) produces output.pptx
    # - validate(output, profile) yields 0 errors
    raise AssertionError("pipeline not implemented")
