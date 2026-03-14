from __future__ import annotations

import json
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from pptx import Presentation


def _slugify(text: str) -> str:
    s = text.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s or "layout"


def _enum_name(value: Any) -> str:
    name = getattr(value, "name", None)
    if isinstance(name, str) and name:
        return name
    return str(value)


def _slot_name_and_type(ph_type_name: str) -> tuple[str, str]:
    # Keep these conservative and deterministic.
    if ph_type_name in {"TITLE", "CENTER_TITLE"}:
        return "title", "text"
    if ph_type_name == "SUBTITLE":
        return "subtitle", "text"
    if ph_type_name == "BODY":
        return "body", "bullets"
    if ph_type_name == "PICTURE":
        return "image", "image"
    return "slot", "unknown"


@dataclass(frozen=True)
class BootstrapResult:
    template_dir: str
    template_pptx: str
    template_json: str
    included_layouts: list[str]
    excluded_layouts: list[str]


class BootstrapError(Exception):
    pass


def bootstrap_template(
    *,
    pptx_path: str,
    template_id: str,
    out_dir: str,
    include_layouts: Iterable[str] | None = None,
    exclude_layouts: Iterable[str] | None = None,
    overwrite: bool = False,
    name: str | None = None,
    version: str = "0.1",
) -> BootstrapResult:
    src = Path(pptx_path).expanduser()
    if not src.exists():
        raise BootstrapError(f"PPTX not found: {src}")
    if not src.is_file():
        raise BootstrapError(f"PPTX path is not a file: {src}")

    dest_root = Path(out_dir).expanduser().resolve()
    tdir = dest_root / template_id

    if tdir.exists():
        if not overwrite:
            raise BootstrapError(f"Output template dir already exists: {tdir} (pass --overwrite to replace)")
        # Overwrite means replace just this template folder.
        shutil.rmtree(tdir)

    tdir.mkdir(parents=True, exist_ok=True)

    # Copy PPTX.
    pptx_out = tdir / "template.pptx"
    shutil.copyfile(str(src.resolve()), str(pptx_out))

    prs = Presentation(str(pptx_out))

    include_set = {s.strip() for s in (include_layouts or []) if s.strip()}
    exclude_set = {s.strip() for s in (exclude_layouts or []) if s.strip()}

    included: list[str] = []
    excluded: list[str] = []
    archetypes: list[dict[str, Any]] = []

    # Determine which layouts to include.
    for layout in prs.slide_layouts:
        lname = layout.name
        if include_set and lname not in include_set:
            excluded.append(lname)
            continue
        if lname in exclude_set:
            excluded.append(lname)
            continue

        included.append(lname)

        # Build archetype.
        aid = f"layout__{_slugify(lname)}"
        slots: list[dict[str, Any]] = []
        name_counts: dict[str, int] = {}

        for ph in sorted(layout.placeholders, key=lambda p: int(p.placeholder_format.idx)):
            ph_type = _enum_name(ph.placeholder_format.type)
            base_name, slot_type = _slot_name_and_type(ph_type)

            # Ensure unique slot names per archetype.
            n = name_counts.get(base_name, 0) + 1
            name_counts[base_name] = n
            slot_name = base_name if n == 1 else f"{base_name}_{n}"

            slots.append(
                {
                    "name": slot_name,
                    "type": slot_type,
                    "required": False,
                    "placeholder_idx": int(ph.placeholder_format.idx),
                }
            )

        layout_part = None
        try:
            # Typically like '/ppt/slideLayouts/slideLayout1.xml'
            layout_part = str(layout.part.partname)  # type: ignore[attr-defined]
        except Exception:
            layout_part = None

        archetype: dict[str, Any] = {
            "id": aid,
            "description": f"Bootstrap from layout '{lname}'",
            "layout": lname,
            "slots": slots,
        }
        if layout_part:
            archetype["layout_part"] = layout_part.lstrip("/")

        archetypes.append(archetype)

    if not archetypes:
        raise BootstrapError(
            "No layouts selected for bootstrap. Check --include-layout(s)/--exclude-layout(s) filters."
        )

    spec: dict[str, Any] = {
        "template_id": template_id,
        "name": name or template_id,
        "version": version,
        "deck": {},
        "styles": {},
        "archetypes": archetypes,
    }

    template_json_path = tdir / "template.json"
    template_json_path.write_text(json.dumps(spec, indent=2, sort_keys=True) + "\n")

    return BootstrapResult(
        template_dir=str(tdir),
        template_pptx=str(pptx_out),
        template_json=str(template_json_path),
        included_layouts=included,
        excluded_layouts=excluded,
    )
