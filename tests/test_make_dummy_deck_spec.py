import json
import subprocess
import sys
from pathlib import Path


def test_make_dummy_deck_spec_outputs_valid_json() -> None:
    repo = Path(__file__).resolve().parents[1]
    cmd = [
        sys.executable,
        "-m",
        "slide_smith.cli",
        "make-dummy-deck-spec",
        "--template",
        "default",
    ]

    out = subprocess.check_output(cmd, cwd=str(repo)).decode("utf-8")
    data = json.loads(out)
    assert data["version"] == "1.0"
    assert "slides" in data
    assert isinstance(data["slides"], list)
    assert len(data["slides"]) > 0


def test_make_dummy_deck_spec_is_deterministic() -> None:
    repo = Path(__file__).resolve().parents[1]
    cmd = [
        sys.executable,
        "-m",
        "slide_smith.cli",
        "make-dummy-deck-spec",
        "--template",
        "default",
    ]
    out1 = subprocess.check_output(cmd, cwd=str(repo)).decode("utf-8")
    out2 = subprocess.check_output(cmd, cwd=str(repo)).decode("utf-8")
    assert out1 == out2
