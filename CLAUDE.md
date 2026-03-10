# CLAUDE.md

## Project overview

`slide_smith` is an agent-first PowerPoint creation application built in Python.

The goal is not only to generate decks, but to expose a reliable application surface that agents can use to:
- inspect templates
- normalize markdown/JSON input into a structured deck spec
- render `.pptx` output
- later perform narrow iterative edits

The core rendering library is `python-pptx`.

## Current product direction

The working north star is:
- input: markdown or JSON deck description
- template model: paired artifacts
  - `template.pptx` as render truth
  - `template.json` as agent-operable semantic truth
- output: PowerPoint `.pptx`
- interaction model: CLI-first, designed for agents

## Current repo state

### Design docs
Key design docs live in `docs/design/`:
- `north-star.md`
- `python-pptx-feasibility.md`
- `template-model.md`
- `mvp-project-plan.md`
- `deck-spec.md`
- `deck-spec.schema.json`

### Issue docs
Local issue-tracking drafts live in `docs/issues/`.

### Code status
Current implementation includes:
- Python package scaffold in `src/slide_smith/`
- CLI entrypoint in `src/slide_smith/cli.py`
- deck spec validation in `src/slide_smith/deck_spec.py`
- markdown normalization in `src/slide_smith/markdown_parser.py`
- template loading in `src/slide_smith/template_loader.py`
- initial rendering path in `src/slide_smith/renderer.py`
- narrow deck edit operations in `src/slide_smith/editor.py`
- test coverage under `tests/`

### Template status
There is currently a hand-authored default template package at:
- `templates/default/template.json`
- `templates/default/README.md`

The JSON template currently defines these MVP archetypes:
- `title`
- `section`
- `title_and_bullets`
- `image_left_text_right`

## Development environment

Project-local virtual environment:
- `.venv/`

Typical setup/use:

```bash
cd ~/slide_smith
source .venv/bin/activate
pip install -e .[dev]
pytest -q
python -m slide_smith.cli --help
```

## Current priorities

The next active GitHub issues are:
1. implement rendering MVP with `python-pptx`
2. add tests and fixtures for normalization and template inspection
3. implement narrow iterative edit operations for generated decks

## Working assumptions

- keep MVP narrow and reliable
- prefer placeholders over coordinate-heavy manual layout
- prefer semantic JSON over raw shape dumps
- treat imported example deck understanding as a later-phase problem
- optimize for agent usability, inspectability, and repeatability

## Notes for future work

When extending the system:
- keep the CLI explicit and discoverable
- preserve a stable deck spec contract
- keep template JSON semantic
- avoid overpromising arbitrary PowerPoint surgery too early
- prefer generated decks that remain easy to edit predictably later
