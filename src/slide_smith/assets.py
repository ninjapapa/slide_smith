from __future__ import annotations

import copy
import hashlib
import shutil
from pathlib import Path
from typing import Any


class AssetError(Exception):
    pass


def resolve_asset_path(path: str, base_dir: str | Path) -> Path:
    p = Path(path).expanduser()
    base = Path(base_dir)
    if not p.is_absolute():
        p = base / p
    return p.resolve()


def _dedup_name(dest_dir: Path, src: Path) -> Path:
    """Return a destination path under dest_dir that won't collide."""
    candidate = dest_dir / src.name
    if not candidate.exists():
        return candidate

    # If it exists and is the same file content, keep it.
    try:
        if candidate.stat().st_size == src.stat().st_size:
            return candidate
    except OSError:
        pass

    h = hashlib.sha1(str(src).encode("utf-8")).hexdigest()[:10]
    return dest_dir / f"{src.stem}-{h}{src.suffix}"


def collect_assets(deck_spec: dict[str, Any], base_dir: str | Path, assets_dir: str | Path) -> dict[str, Any]:
    """Copy referenced assets into assets_dir and rewrite deck_spec paths.

    Currently only handles slide field: `image` (string path).

    Returns a deep-copied deck_spec with updated image paths.
    """
    src_base = Path(base_dir).resolve()
    dest_dir = Path(assets_dir).expanduser().resolve()
    dest_dir.mkdir(parents=True, exist_ok=True)

    spec = copy.deepcopy(deck_spec)

    for slide in spec.get("slides", []):
        image_path = slide.get("image")
        if not image_path:
            continue

        src = resolve_asset_path(str(image_path), src_base)
        if not src.exists():
            raise AssetError(f"Image file not found: {src}")
        if not src.is_file():
            raise AssetError(f"Image path is not a file: {src}")

        dest = _dedup_name(dest_dir, src)
        if not dest.exists():
            shutil.copy2(src, dest)

        # Store as absolute for reliability.
        slide["image"] = str(dest)

    return spec
