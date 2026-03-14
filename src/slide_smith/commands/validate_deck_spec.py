from __future__ import annotations

import json
from pathlib import Path

from slide_smith.deck_spec import load_deck_spec, validate_deck_spec
from slide_smith.markdown_parser import parse_markdown


def handle_validate_deck_spec(*, input_path: str, profile: str) -> tuple[int, str]:
    if input_path.endswith(".json"):
        spec = load_deck_spec(input_path)
    elif input_path.endswith(".md"):
        spec = parse_markdown(input_path)
    else:
        return 1, "Unsupported input type. Use .json or .md"

    errors = validate_deck_spec(spec, profile=profile)
    if errors:
        lines = [f"Deck spec validation failed (profile={profile}):"] + [f"- {e}" for e in errors]
        return 1, "\n".join(lines)

    # Best-effort schema validation (source of truth when jsonschema is present).
    # If jsonschema isn't installed, treat it as a warning (not a hard failure).
    try:
        from slide_smith.schema_validation import validate_against_schema

        schema_res = validate_against_schema(spec)
        if not schema_res.ok:
            if any(str(e).startswith("jsonschema is not installed") for e in schema_res.errors):
                return 0, json.dumps(
                    {
                        "ok": True,
                        "profile": profile,
                        "slides": len(spec.get("slides") or []),
                        "warnings": schema_res.errors,
                    },
                    indent=2,
                )
            lines = ["Deck spec schema validation failed:"] + [f"- {e}" for e in schema_res.errors]
            return 1, "\n".join(lines)
    except Exception:
        pass

    return 0, json.dumps({"ok": True, "profile": profile, "slides": len(spec.get('slides') or [])}, indent=2)
