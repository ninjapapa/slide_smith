from __future__ import annotations

import json

from slide_smith.dummy_deck import make_dummy_deck_spec


def handle_make_dummy_deck_spec(*, template: str, templates_dir: str | None) -> tuple[int, str]:
    res = make_dummy_deck_spec(template, templates_dir=templates_dir)
    return 0, json.dumps(res.deck_spec, indent=2, sort_keys=True) + "\n"
