from __future__ import annotations

import json

from slide_smith.editor import (
    EditError,
    add_slide_to_deck,
    delete_slide_from_deck,
    list_slides_in_deck,
    update_slide_in_deck,
)


def handle_add_slide(*, deck: str, after: int, archetype: str, input_path: str) -> tuple[int, str]:
    try:
        path = add_slide_to_deck(deck, after, archetype, input_path)
    except EditError as exc:
        return 1, f"Add-slide failed: {exc}"
    return 0, json.dumps({"deck": path, "status": "slide added"}, indent=2)


def handle_update_slide(*, deck: str, index: int, input_path: str) -> tuple[int, str]:
    try:
        path = update_slide_in_deck(deck, index, input_path)
    except EditError as exc:
        return 1, f"Update-slide failed: {exc}"
    return 0, json.dumps({"deck": path, "status": "slide updated"}, indent=2)


def handle_list_slides(*, deck: str) -> tuple[int, str]:
    try:
        items = list_slides_in_deck(deck)
    except EditError as exc:
        return 1, f"List-slides failed: {exc}"
    return 0, json.dumps({"deck": deck, "slides": items}, indent=2)


def handle_delete_slide(*, deck: str, index: int) -> tuple[int, str]:
    try:
        path = delete_slide_from_deck(deck, index)
    except EditError as exc:
        return 1, f"Delete-slide failed: {exc}"
    return 0, json.dumps({"deck": path, "status": "slide deleted"}, indent=2)
