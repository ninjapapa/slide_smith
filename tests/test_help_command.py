from __future__ import annotations

import json

from slide_smith.commands.help import handle_help


def test_help_api_text_mentions_supported_layouts() -> None:
    code, out = handle_help(topic="api", fmt="text")
    assert code == 0
    assert "Slide Smith layout_id API" in out
    assert "Fallback layout: title_and_bullets" in out
    assert "title_and_bullets" in out
    assert "picture_compare" in out


def test_help_api_json_returns_layout_contract() -> None:
    code, out = handle_help(topic="api", fmt="json")
    assert code == 0
    payload = json.loads(out)
    assert payload["topic"] == "api"
    assert payload["fallback_layout_id"] == "title_and_bullets"
    assert any(item["layout_id"] == "title" for item in payload["layout_ids"])
    title = next(item for item in payload["layout_ids"] if item["layout_id"] == "title")
    assert title["required_fields"] == ["title"]
