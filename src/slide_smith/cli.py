import argparse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="slide-smith",
        description="Agent-first PowerPoint creation tool.",
    )
    subparsers = parser.add_subparsers(dest="command")

    create = subparsers.add_parser("create", help="Create a deck from structured input.")
    create.add_argument("--input", required=True, help="Path to markdown or JSON input.")
    create.add_argument("--template", required=True, help="Template id to use.")
    create.add_argument("--output", required=True, help="Output .pptx path.")

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


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    print(f"Command '{args.command}' is scaffolded but not implemented yet.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
