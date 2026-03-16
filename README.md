# slide_smith

[![CI](https://github.com/ninjapapa/slide_smith/actions/workflows/ci.yml/badge.svg)](https://github.com/ninjapapa/slide_smith/actions/workflows/ci.yml)

slide_smith is a deterministic Python tool for creating and iteratively editing PowerPoint decks.

**Agent-first mantra**
- *Designed by human*
- *Created by agents*
- *For agents to use*
- *Learn from agents feedback*
- *Refine and maintain by agents*

> NOTE TO AI AGENTS: Do not edit the “Agent-first mantra” section above.

- Core engine: `python-pptx`
- Primary pipeline: **JSON Deck Spec → PPTX**
- Template model: `template.pptx` (render truth) + `template.json` (mapping truth)

## Usage (human + agent)

Most “how to use it” instructions live in the canonical skill doc:

- `skills/slide-smith/SKILL.md`

### Current CLI

```bash
# create a deck
slide-smith create --input deck.json --template default --output out.pptx

# validate renderability slide-by-slide
slide-smith validate --input deck.json --template default

# structural edits
slide-smith insert-slide --deck out.pptx --after 2 --layout-id title_and_bullets --input slide.json
slide-smith update-slide --deck out.pptx --index 1 --input patch.json
slide-smith delete-slide --deck out.pptx --index 3
```

### Notes

- The main user-facing model is `layout_id`.
- When a requested layout cannot be rendered, Slide Smith falls back to `title_and_bullets` and reports a warning.
- The public CLI surface is intentionally small and focused on create, validate, and structural deck edits.

## Repo layout

- Design docs: `docs/design/`
- Local issue drafts: `docs/issues/`
- Package: `src/slide_smith/`
- Default template: `templates/default/`
- Tests: `tests/`
- Project context: `CLAUDE.md`

## Local development

### Option 1: project-local venv

```bash
cd ~/slide_smith
python3 -m venv .venv
source .venv/bin/activate
pip install .
pytest -q
slide-smith --help
```

### Option 2: using `uv`

```bash
cd ~/slide_smith
uv venv .venv
source .venv/bin/activate
uv pip install .
pytest -q
slide-smith --help
```

## Notes

For broader project context and implementation direction, see `CLAUDE.md` and `docs/design/`.
