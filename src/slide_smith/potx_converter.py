from __future__ import annotations

import zipfile
from dataclasses import dataclass
from pathlib import Path
from xml.etree import ElementTree as ET


_TEMPLATE_CT = "application/vnd.openxmlformats-officedocument.presentationml.template.main+xml"
_PRESENTATION_CT = "application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"


class PotxConvertError(Exception):
    pass


@dataclass(frozen=True)
class ConvertPotxResult:
    input_path: str
    output_path: str


def _rewrite_content_types(xml_bytes: bytes) -> bytes:
    """Rewrite [Content_Types].xml to change presentation.xml from template.main to presentation.main.

    This makes many .potx packages loadable by libraries expecting a pptx.

    We only rewrite the specific Override for /ppt/presentation.xml when present.
    """

    root = ET.fromstring(xml_bytes)

    # namespaces usually none for [Content_Types].xml
    changed = False
    for child in list(root):
        if child.tag.endswith("Override") and child.get("PartName") == "/ppt/presentation.xml":
            ct = child.get("ContentType")
            if ct == _TEMPLATE_CT:
                child.set("ContentType", _PRESENTATION_CT)
                changed = True

    if not changed:
        # Not necessarily an error; may already be pptx.
        return xml_bytes

    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def convert_potx_to_pptx(*, potx_path: str, pptx_path: str, overwrite: bool = False) -> ConvertPotxResult:
    in_path = Path(potx_path).expanduser().resolve()
    out_path = Path(pptx_path).expanduser().resolve()

    if not in_path.exists() or not in_path.is_file():
        raise PotxConvertError(f"Input not found: {in_path}")

    if out_path.exists() and not overwrite:
        raise PotxConvertError(f"Output already exists: {out_path} (pass overwrite=True)")

    out_path.parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(in_path, "r") as zin:
        with zipfile.ZipFile(out_path, "w", compression=zipfile.ZIP_DEFLATED) as zout:
            for info in zin.infolist():
                data = zin.read(info.filename)
                if info.filename == "[Content_Types].xml":
                    data = _rewrite_content_types(data)
                zout.writestr(info, data)

    return ConvertPotxResult(input_path=str(in_path), output_path=str(out_path))
