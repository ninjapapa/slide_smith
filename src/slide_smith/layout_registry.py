from __future__ import annotations

"""Layout registry.

This module centralizes which layout ids are considered standard / extended
for validation, inference, and help-request generation.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class LayoutDef:
    id: str


CORE_STANDARD_LAYOUT_IDS: list[str] = [
    "title",
    "section",
    "title_and_bullets",
    "text_with_image",
    "title_subtitle_and_bullets",
]

EXTENDED_LAYOUT_IDS: list[str] = [
    "version_page",
    "agenda_with_image",
    "two_col",
    "three_col_with_icons",
    "picture_compare",
]


def all_known_layout_ids() -> list[str]:
    return CORE_STANDARD_LAYOUT_IDS + EXTENDED_LAYOUT_IDS
