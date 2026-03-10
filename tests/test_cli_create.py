from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_JSON = ROOT / "docs" / "design" / "examples" / "deck-spec.sample.json"


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


def test_cli_version_smoke() -> None:
    res = run_cli("--version")
    assert res.returncode == 0
    assert res.stdout.strip()  # may be 'unknown' when not installed


def test_cli_create_print_none(tmp_path: Path) -> None:
    out = tmp_path / "out.pptx"
    res = run_cli(
        "create",
        "--input",
        str(EXAMPLE_JSON),
        "--template",
        "default",
        "--output",
        str(out),
        "--print",
        "none",
    )
    assert res.returncode == 0
    assert out.exists()

    payload = json.loads(res.stdout)
    assert payload["output"].endswith("out.pptx")
    assert "deck" not in payload
