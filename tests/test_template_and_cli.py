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
    assert len(spec["layouts"]) >= 3



def test_cli_help_surfaces_simplified_primary_commands() -> None:
    result = run_cli("--help")
    assert result.returncode == 0
    assert "create" in result.stdout
    assert "validate" in result.stdout
    assert "help" in result.stdout
    assert "insert-slide" in result.stdout
    assert "update-slide" in result.stdout
    assert "delete-slide" in result.stdout
    assert "list-slides" not in result.stdout


def test_cli_help_api_text_works() -> None:
    result = run_cli("help", "api")
    assert result.returncode == 0
    assert "Slide Smith layout_id API" in result.stdout
    assert "title_and_bullets" in result.stdout


def test_cli_help_api_json_works() -> None:
    result = run_cli("help", "api", "--format", "json")
    assert result.returncode == 0
    assert '"layout_ids"' in result.stdout
    assert '"fallback_layout_id": "title_and_bullets"' in result.stdout


def test_retired_command_is_not_supported() -> None:
    result = run_cli("inspect-pptx")
    assert result.returncode != 0
    combined = result.stdout + result.stderr
    assert "invalid choice" in combined or "not supported" in combined
