from __future__ import annotations

import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET


_NS = {
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
}


@dataclass(frozen=True)
class InspectOpenXmlPresentationResult:
    pptx: str
    slide_size: dict[str, int]


def inspect_openxml_presentation(pptx_path: str) -> InspectOpenXmlPresentationResult:
    """Inspect presentation-level properties directly from OpenXML.

    Supports both .pptx and .potx (they are both zip OpenXML containers).

    Currently extracts:
    - slide size (EMU) from ppt/presentation.xml p:sldSz
    """

    path = Path(pptx_path).expanduser().resolve()
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"PPTX/POTX not found: {path}")

    with zipfile.ZipFile(path, "r") as z:
        xml = z.read("ppt/presentation.xml")

    root = ET.fromstring(xml)
    sldSz = root.find("p:sldSz", _NS)

    cx = 0
    cy = 0
    if sldSz is not None:
        try:
            cx = int(sldSz.get("cx") or 0)
            cy = int(sldSz.get("cy") or 0)
        except Exception:
            cx, cy = 0, 0

    return InspectOpenXmlPresentationResult(pptx=str(path), slide_size={"width_emu": cx, "height_emu": cy})
