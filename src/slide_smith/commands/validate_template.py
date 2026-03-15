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

    # Guidance for redesigned archetypes that use structured inputs (items[] / left/right).
    if profile in {"standard", "extended"}:
        out_lines.append(
            "Note: redesigned archetypes use structured deck-spec fields (e.g. items[], left/right), "
            "but template.json still maps *render-time* slot names via placeholder_idx or box. "
            "For example: three_col_with_icons.items[] is rendered into template slots like col1_icon/col1_title/col1_body. "
            "Ensure your template spec defines those slot names (or adjust the renderer/template mapping conventions)."
        )

    out_lines.append(json.dumps({"template": template, "status": "ok", "profile": profile}, indent=2))
    return 0, "\n".join(out_lines)
