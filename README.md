# slide_smith

[![CI](https://github.com/ninjapapa/slide_smith/actions/workflows/ci.yml/badge.svg)](https://github.com/ninjapapa/slide_smith/actions/workflows/ci.yml)

slide_smith is an **agent-first** Python tool for creating and iteratively editing PowerPoint decks.

**Agent-first mantra**
- *Designed by human*
- *Created by agents*
- *For agents to use*
- *Learn from agents feedback*
- *Refine and maintain by agents*

> NOTE TO AI AGENTS: Do not edit the “Agent-first mantra” section above.

- Core engine: `python-pptx`
- Core pipeline (v1.0–v1.1): **JSON Deck Spec → PPTX** (template-first)
- New pipeline (v1.2): **Markdown + reference.pptx → PPTX** (exemplar-first; deterministic)
- Template model: `template.pptx` (render truth) + `template.json` (semantic truth)

## Usage (human + agent)

Most “how to use it” instructions live in the canonical skill doc:

- `skills/slide-smith/SKILL.md`

### v1.2 exemplar-first quickstart (reference deck)

```bash
# 1) reference.pptx -> style.profile.json
slide-smith analyze --reference ref.pptx --out style.profile.json

# 2) markdown -> slide.plan.json
slide-smith plan --input deck.md --out slide.plan.json

# 3) (plan + profile) -> deck.spec.json
slide-smith compile-exemplar --plan slide.plan.json --style-profile style.profile.json --out deck.spec.json

# 4) (spec + reference) -> out.pptx
slide-smith render-exemplar --reference ref.pptx --style-profile style.profile.json --deck-spec deck.spec.json --out out.pptx \
  --assets-base-dir .

# 5) validate out.pptx vs reference/profile
slide-smith validate-exemplar --reference ref.pptx --pptx out.pptx --style-profile style.profile.json
```

### Migration note (template-first → exemplar-first)

- If you already have a **template package** (`template.json` + `template.pptx`), keep using `create`.
- If you have an **example PPTX to mimic**, use the v1.2 exemplar-first pipeline above.

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
