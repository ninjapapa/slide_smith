from __future__ import annotations

import argparse
import json
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="slide-smith",
        description="Deterministic PowerPoint creation and editing tool.",
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
    create.add_argument(
        "--templates-dir",
        default=None,
        help="Optional root directory containing template packages (defaults to repo-local templates/).",
    )
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

    insert_slide = subparsers.add_parser("insert-slide", help="Insert a slide into an existing deck.")
    insert_slide.add_argument("--deck", required=True, help="Path to target deck.")
    insert_slide.add_argument("--after", type=int, required=True, help="Insert after slide index.")
    insert_slide.add_argument("--layout-id", required=True, help="Requested layout_id for the new slide.")
    insert_slide.add_argument("--input", required=True, help="Path to slide input JSON.")

    update_slide = subparsers.add_parser("update-slide", help="Update a slide in an existing deck.")
    update_slide.add_argument("--deck", required=True, help="Path to target deck.")
    update_slide.add_argument("--index", type=int, required=True, help="Slide index to update.")
    update_slide.add_argument("--input", required=True, help="Path to patch JSON.")

    delete_slide = subparsers.add_parser("delete-slide", help="Delete a slide in an existing deck.")
    delete_slide.add_argument("--deck", required=True, help="Path to target deck.")
    delete_slide.add_argument("--index", type=int, required=True, help="Slide index to delete.")

    validate = subparsers.add_parser(
        "validate",
        help="Validate whether a template can render a deck spec, slide by slide.",
    )
    validate.add_argument("--input", required=True, help="Path to deck spec (.json or .md)")
    validate.add_argument("--template", required=True, help="Template id to validate against.")
    validate.add_argument(
        "--templates-dir",
        default=None,
        help="Optional root directory containing template packages (defaults to repo-local templates/).",
    )

    help_cmd = subparsers.add_parser("help", help="Print the supported layout_id API.")
    help_cmd.add_argument("topic", nargs="?", default="api", choices=["api"], help="Help topic to print.")
    help_cmd.add_argument("--format", choices=["text", "json"], default="text", help="Output format.")

    return parser






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

    if args.command == "create":
        from slide_smith.commands.create import handle_create

        code, out = handle_create(
            input_path=args.input,
            template=args.template,
            output=args.output,
            assets_dir=getattr(args, "assets_dir", None),
            print_mode=getattr(args, "print_mode", "normalized"),
            templates_dir=getattr(args, "templates_dir", None),
        )
        print(out)
        return code

    if args.command == "insert-slide":
        from slide_smith.commands.edit_ops import handle_add_slide

        code, out = handle_add_slide(deck=args.deck, after=args.after, layout_id=args.layout_id, input_path=args.input)
        print(out)
        return code

    if args.command == "update-slide":
        from slide_smith.commands.edit_ops import handle_update_slide

        code, out = handle_update_slide(deck=args.deck, index=args.index, input_path=args.input)
        print(out)
        return code

    if args.command == "delete-slide":
        from slide_smith.commands.edit_ops import handle_delete_slide

        code, out = handle_delete_slide(deck=args.deck, index=args.index)
        print(out)
        return code

    if args.command == "validate":
        from slide_smith.commands.validate import handle_validate

        code, out = handle_validate(
            input_path=args.input,
            template=args.template,
            templates_dir=getattr(args, "templates_dir", None),
        )
        print(out)
        return code

    if args.command == "help":
        from slide_smith.commands.help import handle_help

        code, out = handle_help(topic=args.topic, fmt=getattr(args, "format", "text"))
        print(out, end="" if out.endswith("\n") else "\n")
        return code

    print(f"Command '{args.command}' is not supported.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
