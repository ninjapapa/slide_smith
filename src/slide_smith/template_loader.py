from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def templates_root(templates_dir: str | None = None) -> Path:
    """Return the root directory containing template packages.

    By default we use the repo-local `templates/` directory. Callers may override
    this (e.g. from CLI) to point at a different templates root.
    """

    if templates_dir:
        return Path(templates_dir).expanduser().resolve()
    return Path(__file__).resolve().parents[2] / "templates"


def template_dir(template_id: str, templates_dir: str | None = None) -> Path:
    return templates_root(templates_dir) / template_id


def load_template_spec(template_id: str, templates_dir: str | None = None) -> dict[str, Any]:
    path = template_dir(template_id, templates_dir) / "template.json"
    if not path.exists():
        raise FileNotFoundError(f"Template '{template_id}' not found at {path}")
    spec = json.loads(path.read_text())
    if isinstance(spec, dict):
        if "layouts" not in spec and isinstance(spec.get("archetypes"), list):
            spec["layouts"] = spec.get("archetypes")
        native = spec.get("native")
        if isinstance(native, dict) and "layouts" not in native and isinstance(native.get("archetypes"), list):
            native["layouts"] = native.get("archetypes")
    return spec
