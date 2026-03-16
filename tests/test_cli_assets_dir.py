from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


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


def test_create_with_assets_dir_copies_images(tmp_path: Path) -> None:
    # Copy fixture deck + provide a real local image under its base_dir.
    fixture = tmp_path / "deck.json"
    fixture.write_text(
        json.dumps(
            {
                "slides": [
                    {
                        "layout_id": "text_with_image",
                        "title": "T",
                        "body": "B",
                        "image": {"path": "assets/demo.png", "alt": "x"},
                    }
                ]
            }
        )
    )

    (tmp_path / "assets").mkdir()
    # Valid 1x1 PNG; python-pptx validates image data.
    (tmp_path / "assets" / "demo.png").write_bytes(
        bytes.fromhex(
            "89504e470d0a1a0a0000000d4948445200000001000000010804000000b51c0c020000000b4944415478da63fcff1f0002eb01f56c124babaa0000000049454e44ae426082"
        )
    )

    out = tmp_path / "out.pptx"
    assets_dir = tmp_path / "collected"

    res = run_cli(
        "create",
        "--input",
        str(fixture),
        "--template",
        "default",
        "--assets-dir",
        str(assets_dir),
        "--output",
        str(out),
        "--print",
        "normalized",
    )
    assert res.returncode == 0
    assert out.exists()
    payload = json.loads(res.stdout)
    img = payload["deck"]["slides"][0]["image"]
    assert isinstance(img, dict)
    assert Path(img["path"]).exists()
    assert str(Path(img["path"]).parent) == str(assets_dir)
