from __future__ import annotations

import json
import subprocess
import sys
import zipfile
from collections import Counter
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


def _assert_no_duplicate_zip_members(pptx_path: Path) -> None:
    with zipfile.ZipFile(pptx_path) as z:
        c = Counter(z.namelist())
    dups = [(name, n) for name, n in c.items() if n > 1]
    assert not dups, f"Duplicate zip members found: {dups[:20]}"


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

    _assert_no_duplicate_zip_members(out)
