from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


_IMAGE_RE = re.compile(r"^!\[(?P<alt>[^\]]*)\]\((?P<path>[^)]+)\)\s*$")


@dataclass(frozen=True)
class PlanFromMarkdownResult:
    slide_plan: dict[str, Any]


def plan_from_markdown(markdown_path: str) -> PlanFromMarkdownResult:
    """Deterministically convert Markdown into a v1.2 SlidePlan.

    Rules (v1.2):
    - First `# H1` becomes the deck title and produces a `title` intent slide.
    - Each `## H2` starts a new section context.
    - Bullet lists under a section become a `bullets` slide.
    - Markdown images `![alt](path)` become an `image` slide.

    Notes:
    - This is intentionally strict and minimal; unsupported constructs are ignored
      rather than heuristically guessed.
    """

    path = Path(markdown_path).expanduser()
    if not path.exists():
        raise FileNotFoundError(f"Markdown not found: {path}")
    if not path.is_file():
        raise FileNotFoundError(f"Markdown path is not a file: {path}")

    text = path.read_text(encoding="utf-8")
    sha = _sha256_text(text)
    lines = [ln.rstrip("\n") for ln in text.splitlines()]

    deck_title: str | None = None

    current_section: str | None = None
    bullets: list[str] = []
    body_lines: list[str] = []

    slides: list[dict[str, Any]] = []

    def flush_bullets_slide() -> None:
        nonlocal bullets, body_lines, current_section
        if not current_section:
            bullets = []
            body_lines = []
            return

        if bullets:
            slides.append(
                {
                    "intent": "bullets",
                    "fields": {
                        "title": current_section,
                        "bullets": bullets[:],
                    },
                }
            )
        elif body_lines:
            # If there's body text but no bullets, treat as a bullets slide with
            # a single paragraph bullet (keeps downstream deterministic).
            para = " ".join(" ".join(body_lines).split()).strip()
            if para:
                slides.append(
                    {
                        "intent": "bullets",
                        "fields": {"title": current_section, "bullets": [para]},
                    }
                )

        bullets = []
        body_lines = []

    for raw in lines:
        line = raw.strip()

        if line.startswith("# "):
            # Only accept first H1 as deck title.
            if deck_title is None:
                deck_title = line[2:].strip()
            continue

        if line.startswith("## "):
            # New section; flush any pending slide material from previous section.
            flush_bullets_slide()
            current_section = line[3:].strip()
            continue

        if not line:
            # Blank line is a boundary; flush any pending bullet/body content.
            flush_bullets_slide()
            continue

        if line.startswith("- "):
            bullets.append(line[2:].strip())
            continue

        m = _IMAGE_RE.match(line)
        if m:
            # If there is pending bullet/body content for the current section,
            # emit it first, then emit an image slide.
            flush_bullets_slide()

            img_path = m.group("path").strip()
            alt = (m.group("alt") or "").strip() or None

            if current_section:
                slides.append(
                    {
                        "intent": "image",
                        "fields": {
                            "title": current_section,
                            "image": {"path": img_path, **({"alt": alt} if alt else {})},
                        },
                    }
                )
            else:
                slides.append(
                    {
                        "intent": "image",
                        "fields": {"image": {"path": img_path, **({"alt": alt} if alt else {})}},
                    }
                )
            continue

        # Default: treat as body text under current section.
        if current_section:
            body_lines.append(line)

    # End-of-file flush
    flush_bullets_slide()

    if deck_title:
        # Insert a title slide at the beginning.
        slides.insert(0, {"intent": "title", "fields": {"title": deck_title}})

    if not slides:
        raise ValueError("No slides produced from markdown (expected at least a # title or ## section)")

    plan = {
        "version": "1",
        "source": {"path": str(path.resolve()), "sha256": sha},
        "slides": slides,
    }

    # Ensure JSON-serializable determinism.
    json.dumps(plan, sort_keys=True)

    return PlanFromMarkdownResult(slide_plan=plan)
