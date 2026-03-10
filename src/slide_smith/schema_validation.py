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
    # repo-local path
    return Path(__file__).resolve().parents[2] / "docs" / "design" / "deck-spec.schema.json"


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

    errs: list[str] = []
    for e in sorted(validator.iter_errors(spec), key=lambda x: list(x.path)):
        # e.path is a deque of keys/indices
        path = "$"
        for part in e.path:
            if isinstance(part, int):
                path += f"[{part}]"
            else:
                path += f".{part}"
        errs.append(f"{path}: {e.message}")

    return SchemaValidationResult(ok=(len(errs) == 0), errors=errs)
