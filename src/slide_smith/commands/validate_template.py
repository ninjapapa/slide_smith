from __future__ import annotations

import json

from slide_smith.template_validator import validate_template


def handle_validate_template(*, template: str, templates_dir: str | None, profile: str) -> tuple[int, str]:
    result = validate_template(template, templates_dir=templates_dir, profile=profile)
    if not result.ok:
        # Keep human-friendly output; also keep an exit code.
        lines = ["Template validation failed:"] + [f"- {e}" for e in result.errors]
        return 1, "\n".join(lines)

    # Surface warnings but still exit 0.
    out_lines: list[str] = []
    if result.errors:
        out_lines.extend(result.errors)
    out_lines.append(json.dumps({"template": template, "status": "ok"}, indent=2))
    return 0, "\n".join(out_lines)
