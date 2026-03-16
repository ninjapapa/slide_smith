from __future__ import annotations

from pathlib import Path

from slide_smith.assets import collect_assets


def test_collect_assets_image_object_preserves_alt(tmp_path: Path) -> None:
    base = tmp_path / "input"
    base.mkdir()
    (base / "imgs").mkdir()
    src = base / "imgs" / "demo.png"
    src.write_bytes(b"fakepng")

    assets_dir = tmp_path / "assets"

    deck = {
        "title": "T",
        "slides": [
            {
                "layout_id": "text_with_image",
                "title": "X",
                "image": {"path": "imgs/demo.png", "alt": "alt text"},
                "body": "b",
            }
        ],
    }

    out = collect_assets(deck, base_dir=base, assets_dir=assets_dir)
    img = out["slides"][0]["image"]
    assert isinstance(img, dict)
    assert img["alt"] == "alt text"
    p = Path(img["path"])
    assert p.is_absolute() and p.exists()
