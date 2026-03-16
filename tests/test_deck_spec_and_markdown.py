from __future__ import annotations

from pathlib import Path

from slide_smith.deck_spec import validate_deck_spec
from slide_smith.markdown_parser import parse_markdown


ROOT = Path(__file__).resolve().parents[1]



def test_validate_deck_spec_accepts_sample_json() -> None:
    sample = ROOT / "docs" / "examples" / "redesign" / "base.sample.json"
    import json

    spec = json.loads(sample.read_text())
    assert validate_deck_spec(spec) == []



def test_markdown_normalizes_to_expected_archetypes(tmp_path: Path) -> None:
    md = tmp_path / "sample.md"
    md.write_text(
        "# Demo Deck\n\nSubtitle\n\n## Highlights\n- One\n- Two\n\n## Product\nSome body text\n\n[image: image.png]\n"
    )
    spec = parse_markdown(str(md))
    assert spec["title"] == "Demo Deck"
    assert spec["slides"][0]["archetype"] == "title_and_bullets"
    assert spec["slides"][1]["archetype"] == "image_left_text_right"
