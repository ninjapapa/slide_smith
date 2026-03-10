# slide_smith

[![CI](https://github.com/ninjapapa/slide_smith/actions/workflows/ci.yml/badge.svg)](https://github.com/ninjapapa/slide_smith/actions/workflows/ci.yml)

slide_smith is an **agent-first** Python tool for creating and iteratively editing PowerPoint decks.

- Core engine: `python-pptx`
- Core pipeline: **JSON Deck Spec → PPTX**
- Template model: `template.pptx` (render truth) + `template.json` (semantic truth)

## Usage (human + agent)

All “how to use it” instructions live in the canonical skill doc:

- `skills/slide-smith/SKILL.md`

That doc is written to be usable by both humans and calling agents (command examples, recommended workflow, fixtures).

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
