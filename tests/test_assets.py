from __future__ import annotations

from pathlib import Path

import pytest

from slide_smith.assets import AssetError, collect_assets, resolve_asset_path


def test_resolve_asset_path_relative(tmp_path: Path) -> None:
    base = tmp_path / "base"
    base.mkdir()
    p = resolve_asset_path("imgs/a.png", base)
    assert str(p).endswith("/base/imgs/a.png")


def test_collect_assets_copies_and_rewrites(tmp_path: Path) -> None:
    base = tmp_path / "input"
    base.mkdir()
    (base / "imgs").mkdir()
    src = base / "imgs" / "demo.png"
    src.write_bytes(b"fakepng")

    assets_dir = tmp_path / "assets"

    deck = {
        "title": "T",
        "slides": [
            {"layout_id": "text_with_image", "title": "X", "image": "imgs/demo.png", "body": "b"}
        ],
    }

    out = collect_assets(deck, base_dir=base, assets_dir=assets_dir)
    copied = Path(out["slides"][0]["image"])
    assert copied.is_absolute()
    assert copied.exists()
    assert copied.read_bytes() == b"fakepng"


def test_collect_assets_missing_raises(tmp_path: Path) -> None:
    deck = {"slides": [{"layout_id": "text_with_image", "image": "nope.png"}]}
    with pytest.raises(AssetError):
        collect_assets(deck, base_dir=tmp_path, assets_dir=tmp_path / "assets")
