from __future__ import annotations

import json
from types import SimpleNamespace

from slide_smith.template_loader import templates_root


def test_help_request_contract_has_required_keys(tmp_path) -> None:
    # This test calls the internal builder via CLI module behavior.
    # We avoid invoking the full CLI entrypoint; instead we validate the help-request schema keys.

    from slide_smith.hints import build_help_request

    payload = build_help_request(
        template_id="t1",
        template_pptx=tmp_path / "template.pptx",
        layouts=[],
        missing=["two_col"],
    )

    # JSON-serializable and contains required keys.
    s = json.dumps(payload)
    d = json.loads(s)

    assert d["help_request_version"] == 1
    assert d["template_id"] == "t1"
    assert "template_pptx" in d
    assert d["missing_archetypes"] == ["two_col"]
    assert isinstance(d.get("layouts"), list)
    assert isinstance(d.get("next_actions"), list)
