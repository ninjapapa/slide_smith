from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class SchemaValidationResult:
    ok: bool
    errors: list[str]


def _schema_path() -> Path:
    """Locate the deck spec JSON schema.

    Preference order:
    1) Packaged schema within the slide_smith module (works for installed wheels)
    2) Repo-local schema under docs/ (works in a source checkout)

    This avoids a common failure mode where an older installed version validates
    against an outdated schema (or a schema file is missing from the package).
    """

    # 1) packaged schema
    try:  # pragma: no cover
        from importlib import resources

        return resources.files("slide_smith").joinpath("schemas/deck-spec.schema.json")  # type: ignore[return-value]
    except Exception:
        pass

    # 2) repo-local path
    return Path(__file__).resolve().parents[2] / "docs" / "design" / "deck-spec.schema.json"


def _schema_runtime_spec(spec: dict[str, Any]) -> dict[str, Any]:
    """Adapt user-facing deck specs to the current schema runtime shape.

    The published v3-facing docs prefer `layout_id`, while the current schema is still
    keyed on `archetype`. Until the schema is fully migrated, validate a compatibility
    shape here.
    """

    if not isinstance(spec, dict):
        return spec

    out = dict(spec)
    slides = out.get("slides")
    if not isinstance(slides, list):
        return out

    out_slides: list[Any] = []
    for slide in slides:
        if not isinstance(slide, dict):
            out_slides.append(slide)
            continue
        s2 = dict(slide)
        if "archetype" not in s2 and isinstance(s2.get("layout_id"), str):
            s2["archetype"] = s2["layout_id"]
        # current schema doesn't yet permit layout_id as an additional property
        s2.pop("layout_id", None)
        out_slides.append(s2)

    out["slides"] = out_slides
    return out


def validate_against_schema(spec: dict[str, Any]) -> SchemaValidationResult:
    """Validate deck spec against the published JSON schema.

    Requires `jsonschema` installed.
    """
    try:
        from jsonschema import Draft202012Validator
    except Exception as exc:  # pragma: no cover
        return SchemaValidationResult(False, [f"jsonschema is not installed: {exc}"])

    schema = json.loads(_schema_path().read_text())
    validator = Draft202012Validator(schema)
    runtime_spec = _schema_runtime_spec(spec)

    errs: list[str] = []
    for e in sorted(validator.iter_errors(runtime_spec), key=lambda x: list(x.path)):
        # e.path is a deque of keys/indices
        path = "$"
        for part in e.path:
            if isinstance(part, int):
                path += f"[{part}]"
            else:
                path += f".{part}"
        errs.append(f"{path}: {e.message}")

    return SchemaValidationResult(ok=(len(errs) == 0), errors=errs)
