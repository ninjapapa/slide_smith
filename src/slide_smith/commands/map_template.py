from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from slide_smith.archetype_registry import EXTENDED_ARCHETYPES
from slide_smith.hints import apply_hints_to_template_spec, build_help_request, load_hints
from slide_smith.pptx_inspector import inspect_pptx
from slide_smith.template_loader import load_template_spec, template_dir
from slide_smith.template_mapper import infer_standard_mappings, standard_patch
from slide_smith.template_mapper_extended import infer_extended_mappings


def handle_map_template(
    *,
    template: str,
    templates_dir: str | None,
    write: bool,
    interactive: bool,
    print_mode: str,
    hints_path: str | None,
) -> tuple[int, str]:
    tdir = template_dir(template, templates_dir=templates_dir)
    path = tdir / "template.json"
    spec = load_template_spec(template, templates_dir=templates_dir)

    updated: dict[str, Any] = infer_standard_mappings(spec)
    updated = infer_extended_mappings(updated)

    hints = load_hints(hints_path)
    updated = apply_hints_to_template_spec(updated, hints)

    if interactive:
        pptx_path = tdir / "template.pptx"
        layouts = {}
        if pptx_path.exists():
            try:
                inv = inspect_pptx(str(pptx_path))
                layouts = {item["name"]: item for item in inv.layouts}
            except Exception:
                layouts = {}

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

    if write:
        path.write_text(json.dumps(updated, indent=2, sort_keys=True) + "\n")
        return 0, json.dumps({"template": template, "status": "mapped", "template_json": str(path)}, indent=2)

    if print_mode == "patch":
        return 0, json.dumps(standard_patch(updated), indent=2, sort_keys=True)

    if print_mode == "help-request":
        pptx_path = tdir / "template.pptx"
        layouts_payload = []
        if pptx_path.exists():
            inv = inspect_pptx(str(pptx_path))
            layouts_payload = inv.layouts

        req = build_help_request(
            template_id=template,
            template_pptx=pptx_path,
            layouts=layouts_payload,
            missing=list(EXTENDED_ARCHETYPES),
        )
        return 0, json.dumps(req, indent=2, sort_keys=True)

    return 0, json.dumps(updated, indent=2, sort_keys=True)
