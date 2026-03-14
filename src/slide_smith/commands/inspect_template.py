from __future__ import annotations

from slide_smith.template_loader import load_template_spec


def handle_inspect_template(*, template: str, templates_dir: str | None) -> tuple[int, str]:
    spec = load_template_spec(template, templates_dir=templates_dir)

    lines: list[str] = []
    lines.append(f"template: {spec['template_id']} ({spec.get('name', 'unnamed')})")
    lines.append(f"version: {spec.get('version', 'n/a')}")
    deck = spec.get("deck", {})
    lines.append(f"aspect_ratio: {deck.get('aspect_ratio', 'unknown')}")

    native_pref = deck.get("native_preferred")
    if isinstance(native_pref, dict) and native_pref:
        lines.append("native_preferred:")
        for k, v in native_pref.items():
            lines.append(f"- {k} -> {v}")

    if spec.get("styles"):
        lines.append("styles:")
        for k, v in (spec.get("styles") or {}).items():
            lines.append(f"- {k}: {v}")

    def dump_archetypes(header: str, archetypes: list[object]) -> None:
        lines.append(header)
        for archetype in archetypes:
            if not isinstance(archetype, dict):
                continue
            lines.append(f"- {archetype['id']}: {archetype.get('description', '')}")
            lines.append(f"  layout: {archetype.get('layout', 'unknown')}")
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
                lines.append(f"  - slot {slot['name']}: {slot['type']} [{required}]{extra_text}")

    dump_archetypes("archetypes:", list(spec.get("archetypes", []) or []))

    native = spec.get("native")
    if isinstance(native, dict) and native.get("archetypes"):
        dump_archetypes("native_archetypes:", list(native.get("archetypes") or []))

    return 0, "\n".join(lines)
