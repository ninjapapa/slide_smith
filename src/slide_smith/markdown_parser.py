from __future__ import annotations

from pathlib import Path
from typing import Any



def parse_markdown(path: str) -> dict[str, Any]:
    text = Path(path).read_text()
    lines = [line.rstrip() for line in text.splitlines()]

    deck: dict[str, Any] = {"slides": []}
    current_slide: dict[str, Any] | None = None
    body_lines: list[str] = []
    bullets: list[str] = []

    def flush_slide() -> None:
        nonlocal current_slide, body_lines, bullets
        if current_slide is None:
            return
        if bullets:
            current_slide["bullets"] = bullets[:]
            current_slide.setdefault("archetype", "title_and_bullets")
        if body_lines:
            current_slide["body"] = "\n".join(body_lines).strip()
        if current_slide.get("image") and current_slide.get("body"):
            current_slide.setdefault("archetype", "image_left_text_right")
        elif current_slide.get("bullets"):
            current_slide.setdefault("archetype", "title_and_bullets")
        else:
            current_slide.setdefault("archetype", "section")
        deck["slides"].append(current_slide)
        current_slide = None
        body_lines = []
        bullets = []

    for line in lines:
        if line.startswith("# ") and "title" not in deck:
            deck["title"] = line[2:].strip()
            continue
        if line.startswith("## "):
            flush_slide()
            current_slide = {"title": line[3:].strip()}
            continue
        if current_slide is None:
            if line.strip():
                deck.setdefault("subtitle", line.strip())
            continue
        if line.startswith("- "):
            bullets.append(line[2:].strip())
            continue
        if line.startswith("[image:") and line.endswith("]"):
            current_slide["image"] = line[len("[image:") : -1].strip()
            continue
        if line.strip():
            body_lines.append(line.strip())

    flush_slide()

    if deck.get("title") and not deck["slides"]:
        deck["slides"].append({
            "archetype": "title",
            "title": deck["title"],
            "subtitle": deck.get("subtitle", ""),
        })

    return deck
