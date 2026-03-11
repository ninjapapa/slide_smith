from __future__ import annotations

from slide_smith.template_validator import validate_template


def test_validate_template_standard_profile_default_template_ok() -> None:
    res = validate_template("default", profile="standard")
    assert res.ok, res.errors
