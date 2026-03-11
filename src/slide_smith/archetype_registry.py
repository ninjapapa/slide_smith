from __future__ import annotations

"""Archetype registry.

This module centralizes which archetypes are considered "standard" / "extended"
for validation, inference, and help-request generation.

v1.1 introduces an extended library (columns/pillars/tables/timeline).
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ArchetypeDef:
    id: str


CORE_STANDARD_ARCHETYPES: list[str] = [
    "title",
    "section",
    "title_and_bullets",
    "image_left_text_right",
]

EXTENDED_ARCHETYPES: list[str] = [
    "two_col",
    "three_col",
    "four_col",
    "pillars_3",
    "pillars_4",
    "table",
    "table_plus_description",
    "timeline_horizontal",
]


def all_known_archetypes() -> list[str]:
    return CORE_STANDARD_ARCHETYPES + EXTENDED_ARCHETYPES
