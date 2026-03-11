from __future__ import annotations

import json
from pathlib import Path

from slide_smith.deck_spec import load_deck_spec, validate_deck_spec
from slide_smith.markdown_parser import parse_markdown
from slide_smith.renderer import RenderingError, render_deck
from slide_smith.template_loader import load_template_spec


def handle_create(
    *,
    input_path: str,
    template: str,
    output: str,
    assets_dir: str | None,
    print_mode: str,
    templates_dir: str | None,
) -> tuple[int, str]:
    template_spec = load_template_spec(template, templates_dir=templates_dir)

    if input_path.endswith(".json"):
        spec = load_deck_spec(input_path)
    elif input_path.endswith(".md"):
        spec = parse_markdown(input_path)
    else:
        return 1, "Unsupported input type. Use .json or .md"

    if assets_dir:
        from slide_smith.assets import AssetError, collect_assets

        try:
            spec = collect_assets(spec, base_dir=str(Path(input_path).resolve().parent), assets_dir=assets_dir)
        except AssetError as exc:
            return 1, f"Asset collection failed: {exc}"

    errors = validate_deck_spec(spec)
    if errors:
        lines = ["Deck spec validation failed:"] + [f"- {e}" for e in errors]
        return 1, "\n".join(lines)

    # Schema validation is the source of truth when jsonschema is available.
    try:
        from slide_smith.schema_validation import validate_against_schema

        schema_res = validate_against_schema(spec)
        if not schema_res.ok:
            lines = ["Deck spec schema validation failed:"] + [f"- {e}" for e in schema_res.errors]
            return 1, "\n".join(lines)
    except Exception:
        pass

    try:
        rendered_path = render_deck(
            spec,
            template_spec,
            template,
            output,
            base_dir=str(Path(input_path).resolve().parent),
            templates_dir=templates_dir,
        )
    except RenderingError as exc:
        return 1, f"Rendering failed: {exc}"

    if print_mode == "none":
        return 0, json.dumps({"output": rendered_path}, indent=2)
    return 0, json.dumps({"template": template, "output": rendered_path, "deck": spec}, indent=2)
