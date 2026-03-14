from __future__ import annotations

import json
from pathlib import Path

from slide_smith.slide_plan import plan_from_markdown


def test_plan_from_markdown_matches_fixture_structure() -> None:
    fx = Path(__file__).resolve().parents[0] / "fixtures" / "v1_2_exemplar_first"
    md = fx / "markdown" / "sample.md"
    expected_path = fx / "slide_plan" / "expected.slide.plan.json"

    expected = json.loads(expected_path.read_text(encoding="utf-8"))
    res = plan_from_markdown(str(md))

    got = res.slide_plan

    # Compare structure, but ignore sha256 and absolute path differences.
    assert got["version"] == expected["version"]
    assert isinstance(got["source"]["sha256"], str) and len(got["source"]["sha256"]) == 64
    assert got["slides"] == expected["slides"]
