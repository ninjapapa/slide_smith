from __future__ import annotations

import json

from slide_smith.commands.help import handle_help
from slide_smith.commands.validate import REQUIRED_FIELDS, SUPPORTED_LAYOUT_IDS


def test_help_api_matches_validate_contract() -> None:
    code, out = handle_help(topic="api", fmt="json")
    assert code == 0
    payload = json.loads(out)

    help_layout_ids = {item["layout_id"] for item in payload["layout_ids"]}
    assert help_layout_ids == SUPPORTED_LAYOUT_IDS

    for item in payload["layout_ids"]:
        assert tuple(item.get("required_fields", [])) == REQUIRED_FIELDS[item["layout_id"]]
