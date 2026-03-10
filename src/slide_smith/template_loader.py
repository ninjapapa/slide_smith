from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def templates_root() -> Path:
    return Path(__file__).resolve().parents[2] / "templates"


def template_dir(template_id: str) -> Path:
    return templates_root() / template_id


def load_template_spec(template_id: str) -> dict[str, Any]:
    path = template_dir(template_id) / "template.json"
    if not path.exists():
        raise FileNotFoundError(f"Template '{template_id}' not found at {path}")
    return json.loads(path.read_text())
