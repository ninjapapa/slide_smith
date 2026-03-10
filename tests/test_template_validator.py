from __future__ import annotations

from slide_smith.template_validator import validate_template


def test_validate_default_template_ok() -> None:
    res = validate_template("default")
    assert res.ok
    # In early stage the default template may not ship a template.pptx.
    # In that case we treat it as ok with warnings.
