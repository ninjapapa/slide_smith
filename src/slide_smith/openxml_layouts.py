from __future__ import annotations

import re
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET


# OpenXML namespaces used in PPTX parts
_NS = {
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
}


def _int(v: str | None, default: int = 0) -> int:
    try:
        return int(v) if v is not None else default
    except Exception:
        return default


def _localname(tag: str) -> str:
    if "}" in tag:
        return tag.split("}", 1)[1]
    return tag


@dataclass(frozen=True)
class RawLayoutPlaceholder:
    type: str
    idx: int
    bbox: dict[str, int] | None


@dataclass(frozen=True)
class RawSlideLayout:
    part: str
    name: str | None
    placeholders: list[RawLayoutPlaceholder]


@dataclass(frozen=True)
class InspectOpenXmlLayoutsResult:
    pptx: str
    layouts: list[dict[str, Any]]


def inspect_openxml_layouts(pptx_path: str) -> InspectOpenXmlLayoutsResult:
    """Enumerate slide layouts directly from the PPTX/POTX OpenXML package.

    This is meant to provide *parity* with the raw contents when python-pptx
    enumeration is incomplete.

    Notes:
    - Layout "name" is best-effort; it may not be present in all files.
    - Placeholder bbox comes from `a:xfrm/a:off` + `a:xfrm/a:ext` when present.
    """

    path = Path(pptx_path).expanduser().resolve()
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"PPTX/POTX not found: {path}")

    layouts: list[RawSlideLayout] = []

    with zipfile.ZipFile(path, "r") as z:
        # Collect all slide layout parts.
        parts = [n for n in z.namelist() if re.match(r"^ppt/slideLayouts/slideLayout\d+\.xml$", n)]
        parts.sort(key=lambda p: int(re.findall(r"\d+", p)[-1]))

        for part in parts:
            xml = z.read(part)
            root = ET.fromstring(xml)

            # Best-effort: p:cSld/@name or p:sldLayout/@name
            name = root.get("name")
            if not name:
                cSld = root.find("p:cSld", _NS)
                if cSld is not None:
                    name = cSld.get("name")

            placeholders: list[RawLayoutPlaceholder] = []

            # Shapes are under p:cSld/p:spTree/*
            spTree = root.find("p:cSld/p:spTree", _NS)
            if spTree is not None:
                for shape in list(spTree):
                    # only consider shapes with placeholder info
                    ph = shape.find("p:nvSpPr/p:nvPr/p:ph", _NS)
                    if ph is None:
                        # picture placeholders might be p:pic
                        ph = shape.find("p:nvPicPr/p:nvPr/p:ph", _NS)
                    if ph is None:
                        continue

                    ph_type = ph.get("type") or ""
                    idx = _int(ph.get("idx"), default=-1)

                    # Geometry: a:xfrm (for sp/pic) under p:spPr/a:xfrm
                    xfrm = shape.find("p:spPr/a:xfrm", _NS)
                    if xfrm is None:
                        xfrm = shape.find("p:spPr/a:xfrm", _NS)

                    bbox: dict[str, int] | None = None
                    if xfrm is not None:
                        off = xfrm.find("a:off", _NS)
                        ext = xfrm.find("a:ext", _NS)
                        if off is not None and ext is not None:
                            bbox = {
                                "x": _int(off.get("x")),
                                "y": _int(off.get("y")),
                                "w": _int(ext.get("cx")),
                                "h": _int(ext.get("cy")),
                            }

                    placeholders.append(RawLayoutPlaceholder(type=ph_type, idx=idx, bbox=bbox))

            layouts.append(RawSlideLayout(part=part, name=name, placeholders=placeholders))

    # Convert to dicts for callers
    payload: list[dict[str, Any]] = []
    for l in layouts:
        payload.append(
            {
                "part": l.part,
                "name": l.name or "",
                "placeholders": [
                    {"type": ph.type, "idx": ph.idx, **({"bbox": ph.bbox} if ph.bbox else {})}
                    for ph in l.placeholders
                ],
            }
        )

    return InspectOpenXmlLayoutsResult(pptx=str(path), layouts=payload)
