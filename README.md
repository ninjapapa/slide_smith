# slide_smith

[![CI](https://github.com/ninjapapa/slide_smith/actions/workflows/ci.yml/badge.svg)](https://github.com/ninjapapa/slide_smith/actions/workflows/ci.yml)

slide_smith is a demo agent-first application for Python-based PowerPoint creation.

It uses the `python-pptx` (`pptx`) library as the core PowerPoint generation engine, but the goal here is not just deck generation — it is to wrap that capability in an agent-first app that agents can operate reliably.

An agent-first application is designed to be usable not just by humans, but directly by calling agents: it exposes clear operable interfaces, good documentation, informative errors, and feedback loops that let agents reliably create, inspect, and refine outputs over multiple steps.

**Agent-first mantra**
- *Designed by human*
- *Created by agents*
- *For agents to use*
- *Learn from agents feedback*
- *Refine and maintain by agents*

## Early project status

The repo now includes:
- design docs under `docs/design/`
- local issue drafts under `docs/issues/`
- a Python CLI scaffold in `src/slide_smith/`
- a default template package under `templates/default/`
- an initial rendering path using `python-pptx`
- tests under `tests/`
- a project context file in `CLAUDE.md`

## Local development

### Option 1: project-local venv with `python3 -m venv`

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
pytest -q
python -m slide_smith.cli --help
```

### Option 2: using `uv`

```bash
uv venv .venv
source .venv/bin/activate
uv pip install -e .[dev]
pytest -q
python -m slide_smith.cli --help
```

## Current CLI

```bash
python -m slide_smith.cli inspect-template --template default
python -m slide_smith.cli create --input docs/design/examples/deck-spec.sample.json --template default --output out.pptx
python -m slide_smith.cli create --input docs/design/examples/deck-spec.sample.md --template default --output out.pptx
python -m slide_smith.cli add-slide --deck out.pptx --after 2 --type title_and_bullets --input slide.json
python -m slide_smith.cli update-slide --deck out.pptx --index 1 --input patch.json
```

## Current design direction

- input: markdown or JSON
- normalization target: internal deck spec
- template model: `template.pptx` + `template.json`
- rendering approach: placeholder-first
- MVP archetypes:
  - `title`
  - `section`
  - `title_and_bullets`
  - `image_left_text_right`

## Notes

For broader project context and implementation direction, see `CLAUDE.md` and `docs/design/`.
