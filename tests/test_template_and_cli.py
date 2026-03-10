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



def test_inspect_template_output() -> None:
    result = run_cli("inspect-template", "--template", "default")
    assert result.returncode == 0
    assert "template: default" in result.stdout
    assert "title_and_bullets" in result.stdout
