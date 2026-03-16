from __future__ import annotations

"""Archetype registry.

This module centralizes which layout ids are considered standard / extended
for validation, inference, and help-request generation.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ArchetypeDef:
    id: str


CORE_STANDARD_ARCHETYPES: list[str] = [
    "title",
    "section",
    "title_and_bullets",
    "text_with_image",
    "title_subtitle_and_bullets",
]

EXTENDED_ARCHETYPES: list[str] = [
    "version_page",
    "agenda_with_image",
    "two_col",
    "three_col_with_icons",
    "picture_compare",
]


def all_known_archetypes() -> list[str]:
    return CORE_STANDARD_ARCHETYPES + EXTENDED_ARCHETYPES
