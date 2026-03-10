from __future__ import annotations

import argparse
import json
from pathlib import Path

from slide_smith.deck_spec import load_deck_spec, validate_deck_spec
from slide_smith.editor import EditError, add_slide_to_deck, update_slide_in_deck
from slide_smith.markdown_parser import parse_markdown
from slide_smith.renderer import RenderingError, render_deck
from slide_smith.template_loader import load_template_spec



def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="slide-smith",
        description="Agent-first PowerPoint creation tool.",
    )
    parser.add_argument(
        "--version",
        action="store_true",
        help="Print version and exit.",
    )
    subparsers = parser.add_subparsers(dest="command")

    create = subparsers.add_parser("create", help="Create a deck from structured input.")
    create.add_argument("--input", required=True, help="Path to markdown or JSON input.")
    create.add_argument("--template", required=True, help="Template id to use.")
    create.add_argument("--output", required=True, help="Output .pptx path.")
    create.add_argument(
        "--assets-dir",
        default=None,
        help="Optional directory to collect/copy referenced assets (e.g., images) for reproducible rendering.",
    )
    create.add_argument(
        "--print",
        dest="print_mode",
        choices=["normalized", "none"],
        default="normalized",
        help="Control stdout output: 'normalized' prints normalized deck JSON; 'none' prints only output path JSON.",
    )

    inspect_template = subparsers.add_parser(
        "inspect-template", help="Inspect a template package."
    )
    inspect_template.add_argument("--template", required=True, help="Template id to inspect.")

    add_slide = subparsers.add_parser("add-slide", help="Add a slide to an existing deck.")
    add_slide.add_argument("--deck", required=True, help="Path to target deck.")
    add_slide.add_argument("--after", type=int, required=True, help="Insert after slide index.")
    add_slide.add_argument("--type", required=True, help="Archetype to add.")
    add_slide.add_argument("--input", required=True, help="Path to slide input JSON.")

    update_slide = subparsers.add_parser("update-slide", help="Update a slide in an existing deck.")
    update_slide.add_argument("--deck", required=True, help="Path to target deck.")
    update_slide.add_argument("--index", type=int, required=True, help="Slide index to update.")
    update_slide.add_argument("--input", required=True, help="Path to patch JSON.")

    return parser



def handle_inspect_template(template_id: str) -> int:
    spec = load_template_spec(template_id)
    print(f"template: {spec['template_id']} ({spec.get('name', 'unnamed')})")
    print(f"version: {spec.get('version', 'n/a')}")
    deck = spec.get("deck", {})
    print(f"aspect_ratio: {deck.get('aspect_ratio', 'unknown')}")

    if spec.get("styles"):
        print("styles:")
        for k, v in (spec.get("styles") or {}).items():
            print(f"- {k}: {v}")

    print("supported_archetypes:")
    for archetype in spec.get("archetypes", []):
        print(f"- {archetype['id']}: {archetype.get('description', '')}")
        print(f"  layout: {archetype.get('layout', 'unknown')}")
        for slot in archetype.get("slots", []):
            required = "required" if slot.get("required") else "optional"
            extras = []
            if "placeholder_idx" in slot:
                extras.append(f"placeholder_idx={slot['placeholder_idx']}")
            if "max_items" in slot:
                extras.append(f"max_items={slot['max_items']}")
            if "aspect_ratio" in slot:
                extras.append(f"aspect_ratio={slot['aspect_ratio']}")
            extra_text = f" ({', '.join(extras)})" if extras else ""
            print(f"  - slot {slot['name']}: {slot['type']} [{required}]{extra_text}")
    return 0



def handle_create(
    input_path: str,
    template_id: str,
    output_path: str,
    assets_dir: str | None = None,
    print_mode: str = "normalized",
) -> int:
    template_spec = load_template_spec(template_id)
    if input_path.endswith(".json"):
        spec = load_deck_spec(input_path)
    elif input_path.endswith(".md"):
        spec = parse_markdown(input_path)
    else:
        print("Unsupported input type. Use .json or .md")
        return 1

    if assets_dir:
        from slide_smith.assets import AssetError, collect_assets

        try:
            spec = collect_assets(spec, base_dir=str(Path(input_path).resolve().parent), assets_dir=assets_dir)
        except AssetError as exc:
            print(f"Asset collection failed: {exc}")
            return 1

    errors = validate_deck_spec(spec)
    if errors:
        print("Deck spec validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    try:
        rendered_path = render_deck(
            spec,
            template_spec,
            template_id,
            output_path,
            base_dir=str(Path(input_path).resolve().parent),
        )
    except RenderingError as exc:
        print(f"Rendering failed: {exc}")
        return 1

    if print_mode == "none":
        print(json.dumps({"output": rendered_path}, indent=2))
    else:
        print(json.dumps({"template": template_id, "output": rendered_path, "deck": spec}, indent=2))
    return 0



def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if getattr(args, "version", False):
        from importlib.metadata import PackageNotFoundError, version

        try:
            print(version("slide-smith"))
        except PackageNotFoundError:
            print("unknown")
        return 0

    if not args.command:
        parser.print_help()
        return 0

    if args.command == "inspect-template":
        return handle_inspect_template(args.template)
    if args.command == "create":
        return handle_create(
            args.input,
            args.template,
            args.output,
            assets_dir=getattr(args, "assets_dir", None),
            print_mode=getattr(args, "print_mode", "normalized"),
        )
    if args.command == "add-slide":
        try:
            path = add_slide_to_deck(args.deck, args.after, args.type, args.input)
        except EditError as exc:
            print(f"Add-slide failed: {exc}")
            return 1
        print(json.dumps({"deck": path, "status": "slide added"}, indent=2))
        return 0
    if args.command == "update-slide":
        try:
            path = update_slide_in_deck(args.deck, args.index, args.input)
        except EditError as exc:
            print(f"Update-slide failed: {exc}")
            return 1
        print(json.dumps({"deck": path, "status": "slide updated"}, indent=2))
        return 0

    print(f"Command '{args.command}' is scaffolded but not implemented yet.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
