from __future__ import annotations

import argparse
from pathlib import Path



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

    inspect_template = subparsers.add_parser(
        "inspect-template", help="Inspect a template package."
    )
    inspect_template.add_argument("--template", required=True, help="Template id to inspect.")
    inspect_template.add_argument(
        "--templates-dir",
        default=None,
        help="Optional root directory containing template packages (defaults to repo-local templates/).",
    )

    add_slide = subparsers.add_parser("add-slide", help="Add a slide to an existing deck.")
    add_slide.add_argument("--deck", required=True, help="Path to target deck.")
    add_slide.add_argument("--after", type=int, required=True, help="Insert after slide index.")
    add_slide.add_argument("--type", required=True, help="Archetype to add.")
    add_slide.add_argument("--input", required=True, help="Path to slide input JSON.")

    update_slide = subparsers.add_parser("update-slide", help="Update a slide in an existing deck.")
    update_slide.add_argument("--deck", required=True, help="Path to target deck.")
    update_slide.add_argument("--index", type=int, required=True, help="Slide index to update.")
    update_slide.add_argument("--input", required=True, help="Path to patch JSON.")

    list_slides = subparsers.add_parser("list-slides", help="List slides in an existing deck.")
    list_slides.add_argument("--deck", required=True, help="Path to target deck.")

    delete_slide = subparsers.add_parser("delete-slide", help="Delete a slide in an existing deck.")
    delete_slide.add_argument("--deck", required=True, help="Path to target deck.")
    delete_slide.add_argument("--index", type=int, required=True, help="Slide index to delete.")

    validate_template_cmd = subparsers.add_parser(
        "validate-template", help="Validate that a template package matches its PPTX (layouts/placeholders)."
    )
    validate_template_cmd.add_argument("--template", required=True, help="Template id to validate.")
    validate_template_cmd.add_argument(
        "--templates-dir",
        default=None,
        help="Optional root directory containing template packages (defaults to repo-local templates/).",
    )
    validate_template_cmd.add_argument(
        "--profile",
        choices=["structural", "standard", "extended"],
        default="structural",
        help="Validation profile: 'structural' checks layouts/placeholders; 'standard' checks core archetypes; 'extended' checks extended archetype library compatibility.",
    )

    map_template = subparsers.add_parser(
        "map-template",
        help="Add best-effort standard archetype mappings to a bootstrapped template.json (reviewable).",
    )
    map_template.add_argument("--template", required=True, help="Template id to map.")
    map_template.add_argument(
        "--templates-dir",
        default=None,
        help="Optional root directory containing template packages (defaults to repo-local templates/).",
    )
    map_template.add_argument(
        "--write",
        action="store_true",
        help="Write changes back to template.json (otherwise prints the updated spec JSON).",
    )
    map_template.add_argument(
        "--interactive",
        action="store_true",
        help="Interactively confirm/override inferred mappings (layout + placeholder_idx per slot).",
    )
    map_template.add_argument(
        "--print",
        dest="map_print_mode",
        choices=["spec", "patch", "help-request"],
        default="spec",
        help="Output mode when not using --write: 'spec' prints full updated template.json; 'patch' prints only standard archetype additions; 'help-request' prints a structured request for caller-agent hints.",
    )
    map_template.add_argument(
        "--hints",
        default=None,
        help="Optional JSON file containing caller-agent mapping hints (v1.1).",
    )

    bootstrap = subparsers.add_parser(
        "bootstrap-template",
        help="Bootstrap a template package (template.pptx + starter template.json) from an example PPTX.",
    )
    bootstrap.add_argument("--pptx", required=True, help="Path to example .pptx to bootstrap from.")
    bootstrap.add_argument("--template-id", required=True, help="Template id for the new template package.")
    bootstrap.add_argument("--out-dir", required=True, help="Directory to write the new template package into.")
    bootstrap.add_argument(
        "--include-layout",
        action="append",
        default=[],
        help="Include only layouts with this exact name (repeatable). If omitted, all layouts are included.",
    )
    bootstrap.add_argument(
        "--exclude-layout",
        action="append",
        default=[],
        help="Exclude layouts with this exact name (repeatable).",
    )
    bootstrap.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite the output template folder if it already exists.",
    )
    bootstrap.add_argument(
        "--print",
        dest="print_mode",
        choices=["report", "json", "none"],
        default="report",
        help="Output mode: report (human), json (machine), or none.",
    )

    export_previews = subparsers.add_parser(
        "export-previews",
        help="Export layout preview artifacts for caller-agent assistance (manifest now; images best-effort).",
    )
    export_previews.add_argument("--template", required=True, help="Template id to export previews for.")
    export_previews.add_argument(
        "--templates-dir",
        default=None,
        help="Optional root directory containing template packages (defaults to repo-local templates/).",
    )
    export_previews.add_argument("--out-dir", required=True, help="Output directory for previews + manifest.")
    export_previews.add_argument(
        "--mode",
        choices=["layouts"],
        default="layouts",
        help="Export mode (v1.1 supports layouts).",
    )

    inspect_pptx = subparsers.add_parser(
        "inspect-pptx",
        help="Inspect an arbitrary PPTX and print layout + placeholder inventory (agent-friendly).",
    )
    inspect_pptx.add_argument("--pptx", required=True, help="Path to a .pptx file to inspect.")
    inspect_pptx.add_argument(
        "--format",
        choices=["json", "text"],
        default="json",
        help="Output format (default: json).",
    )

    dummy = subparsers.add_parser(
        "make-dummy-deck-spec",
        help="Generate a dummy deck spec JSON that exercises a template's archetypes.",
    )
    dummy.add_argument("--template", required=True, help="Template id to generate dummy deck spec for.")
    dummy.add_argument(
        "--templates-dir",
        default=None,
        help="Optional root directory containing template packages (defaults to repo-local templates/).",
    )
    dummy.add_argument(
        "--output",
        default="-",
        help="Output path for JSON deck spec (default: '-' for stdout).",
    )

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

    if args.command == "inspect-template":
        from slide_smith.commands.inspect_template import handle_inspect_template

        code, out = handle_inspect_template(template=args.template, templates_dir=getattr(args, "templates_dir", None))
        print(out)
        return code

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

    if args.command == "add-slide":
        from slide_smith.commands.edit_ops import handle_add_slide

        code, out = handle_add_slide(deck=args.deck, after=args.after, archetype=args.type, input_path=args.input)
        print(out)
        return code

    if args.command == "update-slide":
        from slide_smith.commands.edit_ops import handle_update_slide

        code, out = handle_update_slide(deck=args.deck, index=args.index, input_path=args.input)
        print(out)
        return code

    if args.command == "list-slides":
        from slide_smith.commands.edit_ops import handle_list_slides

        code, out = handle_list_slides(deck=args.deck)
        print(out)
        return code

    if args.command == "delete-slide":
        from slide_smith.commands.edit_ops import handle_delete_slide

        code, out = handle_delete_slide(deck=args.deck, index=args.index)
        print(out)
        return code

    if args.command == "validate-template":
        from slide_smith.commands.validate_template import handle_validate_template

        code, out = handle_validate_template(
            template=args.template,
            templates_dir=getattr(args, "templates_dir", None),
            profile=getattr(args, "profile", "structural"),
        )
        print(out)
        return code

    if args.command == "map-template":
        from slide_smith.commands.map_template import handle_map_template

        code, out = handle_map_template(
            template=args.template,
            templates_dir=getattr(args, "templates_dir", None),
            write=getattr(args, "write", False),
            interactive=getattr(args, "interactive", False),
            print_mode=getattr(args, "map_print_mode", "spec"),
            hints_path=getattr(args, "hints", None),
        )
        print(out)
        return code

    if args.command == "bootstrap-template":
        from slide_smith.template_bootstrapper import BootstrapError, bootstrap_template

        try:
            res = bootstrap_template(
                pptx_path=args.pptx,
                template_id=args.template_id,
                out_dir=args.out_dir,
                include_layouts=getattr(args, "include_layout", None) or [],
                exclude_layouts=getattr(args, "exclude_layout", None) or [],
                overwrite=getattr(args, "overwrite", False),
            )
        except BootstrapError as exc:
            print(f"Bootstrap failed: {exc}")
            return 1

        mode = getattr(args, "print_mode", "report")
        if mode == "none":
            return 0
        if mode == "json":
            print(
                json.dumps(
                    {
                        "template_dir": res.template_dir,
                        "template_pptx": res.template_pptx,
                        "template_json": res.template_json,
                        "included_layouts": res.included_layouts,
                        "excluded_layouts": res.excluded_layouts,
                    },
                    indent=2,
                    sort_keys=True,
                )
            )
            return 0

        # report
        print(f"template_dir: {res.template_dir}")
        print(f"- template.pptx: {res.template_pptx}")
        print(f"- template.json: {res.template_json}")
        if res.included_layouts:
            print("included_layouts:")
            for n in res.included_layouts:
                print(f"- {n}")
        if res.excluded_layouts:
            print("excluded_layouts:")
            for n in res.excluded_layouts:
                print(f"- {n}")
        return 0

    if args.command == "export-previews":
        from slide_smith.commands.export_previews import handle_export_previews

        code, out = handle_export_previews(
            template=args.template,
            templates_dir=getattr(args, "templates_dir", None),
            out_dir=args.out_dir,
            mode=getattr(args, "mode", "layouts"),
        )
        print(out)
        return code

    if args.command == "inspect-pptx":
        from slide_smith.pptx_inspector import inspect_pptx

        try:
            res = inspect_pptx(args.pptx)
        except Exception as exc:
            print(f"Inspect failed: {exc}")
            return 1

        if getattr(args, "format", "json") == "text":
            print(f"pptx: {res.pptx}")
            print(f"slide_size: {res.slide_size['width_emu']}x{res.slide_size['height_emu']} emu")
            for layout in res.layouts:
                print(f"\nlayout[{layout['index']}]: {layout['name']}")
                for ph in layout.get("placeholders", []):
                    print(f"  - idx={ph['idx']} type={ph['ph_type']} name={ph.get('name','')}")
        else:
            print(
                json.dumps(
                    {"pptx": res.pptx, "slide_size": res.slide_size, "layouts": res.layouts},
                    indent=2,
                    sort_keys=True,
                )
            )
        return 0

    if args.command == "make-dummy-deck-spec":
        from slide_smith.dummy_deck import make_dummy_deck_spec

        res = make_dummy_deck_spec(args.template, templates_dir=getattr(args, "templates_dir", None))
        payload = json.dumps(res.deck_spec, indent=2, sort_keys=True) + "\n"

        out_path = getattr(args, "output", "-")
        if out_path == "-":
            print(payload, end="")
        else:
            Path(out_path).expanduser().resolve().write_text(payload)
        return 0

    print(f"Command '{args.command}' is scaffolded but not implemented yet.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
