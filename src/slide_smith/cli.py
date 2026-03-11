from __future__ import annotations

import argparse
import json
from pathlib import Path

from slide_smith.deck_spec import load_deck_spec, validate_deck_spec
from slide_smith.editor import (
    EditError,
    add_slide_to_deck,
    delete_slide_from_deck,
    list_slides_in_deck,
    update_slide_in_deck,
)
from slide_smith.markdown_parser import parse_markdown
from slide_smith.renderer import RenderingError, render_deck
from slide_smith.template_loader import load_template_spec
from slide_smith.template_validator import validate_template



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
        choices=["structural", "standard"],
        default="structural",
        help="Validation profile: 'structural' checks layouts/placeholders; 'standard' also checks standard archetype compatibility.",
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



def handle_inspect_template(template_id: str, templates_dir: str | None = None) -> int:
    spec = load_template_spec(template_id, templates_dir=templates_dir)
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
    templates_dir: str | None = None,
) -> int:
    template_spec = load_template_spec(template_id, templates_dir=templates_dir)
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

    # Schema validation is the source of truth when jsonschema is available.
    try:
        from slide_smith.schema_validation import validate_against_schema

        schema_res = validate_against_schema(spec)
        if not schema_res.ok:
            print("Deck spec schema validation failed:")
            for error in schema_res.errors:
                print(f"- {error}")
            return 1
    except Exception:
        # jsonschema not installed or schema unavailable; keep runtime flexible.
        pass

    try:
        rendered_path = render_deck(
            spec,
            template_spec,
            template_id,
            output_path,
            base_dir=str(Path(input_path).resolve().parent),
            templates_dir=templates_dir,
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
        return handle_inspect_template(args.template, templates_dir=getattr(args, "templates_dir", None))
    if args.command == "create":
        return handle_create(
            args.input,
            args.template,
            args.output,
            assets_dir=getattr(args, "assets_dir", None),
            print_mode=getattr(args, "print_mode", "normalized"),
            templates_dir=getattr(args, "templates_dir", None),
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

    if args.command == "list-slides":
        try:
            items = list_slides_in_deck(args.deck)
        except EditError as exc:
            print(f"List-slides failed: {exc}")
            return 1
        print(json.dumps({"deck": args.deck, "slides": items}, indent=2))
        return 0

    if args.command == "delete-slide":
        try:
            path = delete_slide_from_deck(args.deck, args.index)
        except EditError as exc:
            print(f"Delete-slide failed: {exc}")
            return 1
        print(json.dumps({"deck": path, "status": "slide deleted"}, indent=2))
        return 0

    if args.command == "validate-template":
        result = validate_template(
            args.template,
            templates_dir=getattr(args, "templates_dir", None),
            profile=getattr(args, "profile", "structural"),
        )
        if not result.ok:
            print("Template validation failed:")
            for e in result.errors:
                print(f"- {e}")
            return 1
        # If we returned warnings, surface them but still exit 0.
        if result.errors:
            for e in result.errors:
                print(e)
        print(json.dumps({"template": args.template, "status": "ok"}, indent=2))
        return 0

    if args.command == "map-template":
        from slide_smith.hints import apply_hints_to_template_spec, build_help_request, load_hints
        from slide_smith.pptx_inspector import inspect_pptx
        from slide_smith.template_loader import template_dir
        from slide_smith.template_mapper import infer_standard_mappings, standard_patch

        tdir = template_dir(args.template, templates_dir=getattr(args, "templates_dir", None))
        path = tdir / "template.json"
        spec = load_template_spec(args.template, templates_dir=getattr(args, "templates_dir", None))
        updated = infer_standard_mappings(spec)

        hints = load_hints(getattr(args, "hints", None))
        updated = apply_hints_to_template_spec(updated, hints)

        if getattr(args, "interactive", False):
            pptx_path = tdir / "template.pptx"
            layouts = {}
            if pptx_path.exists():
                try:
                    inv = inspect_pptx(str(pptx_path))
                    layouts = {item["name"]: item for item in inv.layouts}
                except Exception:
                    layouts = {}

            # Build lookup of bootstrapped archetypes by id and by layout name.
            boot = {a.get("id"): a for a in (spec.get("archetypes") or []) if isinstance(a, dict)}
            boot_by_layout = {a.get("layout"): a for a in (spec.get("archetypes") or []) if isinstance(a, dict)}

            updated_by_id = {a.get("id"): a for a in (updated.get("archetypes") or []) if isinstance(a, dict)}
            for std_id in ["title", "section", "title_and_bullets", "image_left_text_right"]:
                a = updated_by_id.get(std_id)
                if not a:
                    continue

                inf = a.get("inference") or {}
                default_src = inf.get("source_archetype") if isinstance(inf, dict) else None
                print(f"\n== map '{std_id}' ==")
                if default_src:
                    print(f"suggested source: {default_src}")
                print(f"current layout: {a.get('layout')}")

                yn = input("accept suggested mapping? [Y/n] ").strip().lower()
                if yn == "n":
                    choice = input("enter source archetype id (layout__*) OR layout name (blank to keep): ").strip()
                    if choice:
                        src = boot.get(choice) or boot_by_layout.get(choice)
                        if not src:
                            print("  ! not found; keeping existing")
                        else:
                            a["layout"] = src.get("layout")
                            a["inference"] = {"manual": True, "source_archetype": src.get("id")}

                layout_name = a.get("layout")
                if isinstance(layout_name, str) and layout_name in layouts:
                    print("placeholders:")
                    for ph in layouts[layout_name].get("placeholders", []):
                        print(f"  - idx={ph['idx']} type={ph['ph_type']} name={ph.get('name','')}")

                for slot in a.get("slots") or []:
                    if not isinstance(slot, dict):
                        continue
                    sname = slot.get("name")
                    cur = slot.get("placeholder_idx")
                    prompt = f"slot '{sname}' placeholder_idx [{cur if cur is not None else ''}]: "
                    raw = input(prompt).strip()
                    if not raw:
                        continue
                    if raw.lower() in {"none", "null", "skip"}:
                        slot.pop("placeholder_idx", None)
                        continue
                    try:
                        slot["placeholder_idx"] = int(raw)
                    except Exception:
                        print("  ! invalid int; keeping existing")

        if getattr(args, "write", False):
            path.write_text(json.dumps(updated, indent=2, sort_keys=True) + "\n")
            print(json.dumps({"template": args.template, "status": "mapped", "template_json": str(path)}, indent=2))
            return 0

        mode = getattr(args, "map_print_mode", "spec")
        if mode == "patch":
            print(json.dumps(standard_patch(updated), indent=2, sort_keys=True))
        elif mode == "help-request":
            pptx_path = tdir / "template.pptx"
            layouts_payload = []
            if pptx_path.exists():
                inv = inspect_pptx(str(pptx_path))
                layouts_payload = inv.layouts

            # For v1.1 we request help for the extended archetypes (hardcoded here; will be sourced from a registry later).
            missing = ["two_col", "three_col", "four_col", "pillars_3", "pillars_4", "table", "table_plus_description", "timeline_horizontal"]
            req = build_help_request(
                template_id=args.template,
                template_pptx=pptx_path,
                layouts=layouts_payload,
                missing=missing,
            )
            print(json.dumps(req, indent=2, sort_keys=True))
        else:
            print(json.dumps(updated, indent=2, sort_keys=True))
        return 0

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
        from slide_smith.pptx_inspector import inspect_pptx
        from slide_smith.template_loader import template_dir

        tdir = template_dir(args.template, templates_dir=getattr(args, "templates_dir", None))
        pptx_path = tdir / "template.pptx"
        if not pptx_path.exists():
            print(json.dumps({"template": args.template, "status": "error", "error": f"template.pptx not found: {pptx_path}"}, indent=2))
            return 1

        out_dir = Path(args.out_dir).expanduser().resolve()
        out_dir.mkdir(parents=True, exist_ok=True)

        inv = inspect_pptx(str(pptx_path))

        # v1.1 MVP: write manifest only. Image export is best-effort and may be added later.
        manifest = {
            "version": 1,
            "template_id": args.template,
            "template_pptx": inv.pptx,
            "slide_size": inv.slide_size,
            "layouts": [
                {
                    **layout,
                    "preview_png": None,
                }
                for layout in inv.layouts
            ],
        }

        manifest_path = out_dir / "manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
        print(json.dumps({"template": args.template, "status": "ok", "manifest": str(manifest_path)}, indent=2))
        return 0

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
