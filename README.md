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

## Agent-first posture

**Designed by human. Created by agents. For agents to use.**

This repo is intentionally shaped to be operated by calling agents:
- *Designed by human*
- *Created by agents*
- *For agents to use*
- *Learn from agents feedback*
- *Refine and maintain by agents*

### JSON-first workflow

The core pipeline is **JSON Deck Spec -> PPTX**. Markdown ingestion is optional and can be handled by caller-side skills/tools.

### Agent skill (for Claude Code / OpenClaw)

This repo ships an agent skill file that teaches calling agents how to operate Slide Smith via CLI:

- `skills/slide-smith/SKILL.md`

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
pip install .
pytest -q
python -m slide_smith.cli --help
```

### Option 2: using `uv`

```bash
uv venv .venv
source .venv/bin/activate
uv pip install .
pytest -q
python -m slide_smith.cli --help
```

## Current CLI

Prefer the installed entrypoint:

```bash
slide-smith inspect-template --template default
slide-smith validate-template --template default
slide-smith create --input docs/design/examples/deck-spec.sample.json --template default --output out.pptx
slide-smith create --input docs/design/examples/deck-spec.sample.json --template default --assets-dir /tmp/slide-smith-assets --output out.pptx

# If your templates live somewhere else:
slide-smith inspect-template --template default --templates-dir /path/to/templates

slide-smith add-slide --deck out.pptx --after 2 --type title_and_bullets --input slide.json
slide-smith update-slide --deck out.pptx --index 1 --input patch.json
slide-smith list-slides --deck out.pptx
slide-smith delete-slide --deck out.pptx --index 0
```

(You can still run via `python -m slide_smith.cli ...` if needed.)

## Current design direction

- input: JSON (primary); markdown is optional and best handled caller-side
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
