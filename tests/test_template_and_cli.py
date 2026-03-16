from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from slide_smith.template_loader import load_template_spec


ROOT = Path(__file__).resolve().parents[1]



def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    env = {"PYTHONPATH": str(ROOT / "src")}
    return subprocess.run(
        [sys.executable, "-m", "slide_smith.cli", *args],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )



def test_load_default_template() -> None:
    spec = load_template_spec("default")
    assert spec["template_id"] == "default"
    assert len(spec["archetypes"]) >= 3



def test_cli_help_surfaces_simplified_primary_commands() -> None:
    result = run_cli("--help")
    assert result.returncode == 0
    assert "create" in result.stdout
    assert "validate" in result.stdout
    assert "insert-slide" in result.stdout
    assert "update-slide" in result.stdout
    assert "delete-slide" in result.stdout
    assert "list-slides" not in result.stdout
