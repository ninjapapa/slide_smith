---
name: slide-smith
description: "Generate and iteratively edit PowerPoint (.pptx) decks using the slide-smith agent-first CLI. Use when an agent needs to: (1) render a PPTX from a JSON Deck Spec, (2) inspect/validate templates, (3) collect/copy image assets for reproducible runs, or (4) perform narrow deck edits (add/update/list/delete slides) on an existing PPTX."
---

# Slide Smith (agent-first PPTX tool)

## Role split: caller agent vs. Slide Smith (important)

Slide Smith is a **deterministic PPTX tool, not an LLM**.

Use this responsibility split:

- **Caller agent**: do semantic reasoning; decide the story; pick candidate slides/layouts; map intent → archetype; provide hints only when mappings are ambiguous.
- **Slide Smith**: inspect PPTX/POTX structure; discover layouts/placeholders; build/update `template.json`; prefer **placeholder-first** mappings; render decks; validate output.

If output looks “visually OK” but is structurally wrong (duplicated text, overlay boxes, titles not discoverable), you likely used box mappings where placeholders were available.

## Canonical workflow (template-first, JSON-first)

Slide Smith’s v1.0–v1.1 core pipeline is:

1) **JSON Deck Spec** → 2) **PPTX** (using a template package)

Markdown ingestion is optional; prefer caller-side skills/tools to convert Markdown → JSON.

## v1.2 workflow (exemplar-first / reference deck)

Also see: `docs/design/rich-potx-and-hybrid-workflow.md` for POTX-heavy templates and hybrid workflows.

v1.2 adds an LLM-free, deterministic pipeline for: **Markdown + reference.(pptx|potx) → output.pptx**.

Notes:
- `.potx` (PowerPoint template) is supported as a **reference** for v1.2 when using `--mode raw` (no python-pptx dependency).
- Some python-pptx-based commands may reject `.potx` due to content-type checks.
  - Use `slide-smith convert-potx --potx in.potx --out out.pptx` to generate a `.pptx` compatible with python-pptx.

Pipeline commands:

```bash
# 1) reference.(pptx|potx) -> style.profile.json
# For .potx, use --mode raw.
slide-smith analyze --reference ref.pptx --out style.profile.json
slide-smith analyze --reference ref.potx --out style.profile.json --mode raw

# 2) markdown -> slide.plan.json
slide-smith plan --input deck.md --out slide.plan.json

# 3) (plan + profile) -> deck.spec.json
slide-smith compile-exemplar --plan slide.plan.json --style-profile style.profile.json --out deck.spec.json

# 4) (spec + reference) -> out.pptx
slide-smith render-exemplar --reference ref.pptx --style-profile style.profile.json --deck-spec deck.spec.json --out out.pptx \
  --assets-base-dir .

# 5) validate out.pptx vs reference/profile
slide-smith validate-exemplar --reference ref.pptx --pptx out.pptx --style-profile style.profile.json

# Optional: also write a validation report JSON
slide-smith validate-exemplar --reference ref.pptx --pptx out.pptx --style-profile style.profile.json --out validate.report.json
```

### Inputs
- Deck Spec schema: `docs/design/deck-spec.schema.json`
- Example fixtures:
  - Legacy v1 examples:
    - `docs/design/examples/deck-spec.full.sample.json`
    - `docs/design/examples/deck-spec.sample.json`
  - Redesign (base vs extended) examples:
    - `docs/examples/redesign/base.sample.json`
    - `docs/examples/redesign/extended.sample.json`

## Local setup (recommended)

Option 1: project-local venv

```bash
cd ~/slide_smith
python3 -m venv .venv
source .venv/bin/activate
pip install .
pytest -q
slide-smith --help
```

Option 2: using `uv`

```bash
cd ~/slide_smith
uv venv .venv
source .venv/bin/activate
uv pip install .
pytest -q
slide-smith --help
```

## Rich branded template workflow (recommended)

Use this workflow when the source file is a branded PPTX/POTX with many example slides/layouts.

1) **Inspect inventory**
- `inspect-pptx` to see layouts + placeholder indices
- `inspect-slide` on representative slides to understand real geometry + patterns

2) **Decide the story before mapping**
- Determine narrative + slide intents first
- Then map intent → archetype/layout

3) **Choose candidate layouts deliberately**
- Prefer layouts that expose real placeholders when editability matters

4) **Prefer placeholder-first**
- Use `placeholder_idx` when possible
- Use `box` slots only as fallback (or `--boxes-only` for debug/compat)

5) **Validate + smoke test**
- `validate-template` before rendering a real deck
- render a small dummy deck first (`make-dummy-deck-spec` + `create`)

6) **Inspect output critically**
- no unwanted sample/template slides preserved
- text is in placeholders (not overlay boxes)
- no duplicated “sample” text visible

## Common failure modes (diagnosis)

1) **Output keeps sample/template slides at the front**
- fix: render should start from zero content slides (template as theme/layout source)

2) **Text appears in the right place but sits on top of existing template text**
- likely cause: box slots used where placeholders exist
- fix: rebuild mapping placeholder-first

3) **All slides look like the same background/layout**
- likely cause: template exposes only one usable layout to python-pptx
- fix: inspect layout inventory; consider raw OpenXML mode + rebuild template package

4) **Generated titles are blank in inspection tools**
- likely cause: overlay boxes rather than title placeholders
- fix: ensure title maps to TITLE placeholder idx

## Caller-agent checklist

Before rendering:
- story/intents decided?
- best-fit archetype chosen per slide?
- layouts inspected?
- placeholder-first mapping used?
- smoke test deck rendered?
- template sample slides not preserved?

After rendering:
- layouts/backgrounds match intent?
- no duplicate text?
- images land in intended placeholders?

## Commands

### Bootstrap → map → validate a template from an example PPTX (standard workflow)

Inspect a PPTX/POTX to see layouts and placeholder indices:

```bash
# Standard mode (python-pptx; works on .pptx)
slide-smith inspect-pptx --pptx /path/to/template.pptx

# Raw OpenXML mode (works on .pptx and .potx)
slide-smith inspect-pptx --pptx /path/to/template.potx --mode raw
```

Inspect a *slide instance* (shapes + geometry), useful for decks that use free-positioned boxes rather than layout placeholders:

```bash
slide-smith inspect-slide --pptx /path/to/deck.pptx --slide 10
# text output:
slide-smith inspect-slide --pptx /path/to/deck.pptx --slide 10 --format text
```

Bootstrap a template package (copies PPTX + generates starter template.json containing `layout__*` archetypes):

```bash
# Works on .pptx. If you have a .potx, convert it first:
slide-smith convert-potx --potx /path/to/template.potx --out /tmp/template.pptx

slide-smith bootstrap-template \
  --pptx /tmp/template.pptx \
  --template-id my_template \
  --out-dir ./templates
```

Bootstrap a template *from a specific slide instance* (**placeholder-first**, box fallback). Great for rich branded templates where you want to populate *real placeholders* (editability, style inheritance) rather than overlaying new boxes:

```bash
slide-smith bootstrap-from-slide \
  --pptx /path/to/deck.pptx \
  --slide 10 \
  --template-id my_template \
  --out-dir ./templates \
  --archetype text_with_image \
  --write

# Force box-only (debug/compat):
slide-smith bootstrap-from-slide \
  --pptx /path/to/deck.pptx \
  --slide 10 \
  --template-id my_template \
  --out-dir ./templates \
  --archetype text_with_image \
  --boxes-only \
  --write
```

Notes:
- This creates `templates/my_template/template.pptx` (copy of the input PPTX) + `template.json`.
- Default behavior is **placeholder-first**: when the slide/layout exposes real placeholders, the archetype slots use `placeholder_idx`.
- If placeholders can’t be inferred reliably, it falls back to `box` geometry (`units: relative`).
- You can force legacy behavior with `--boxes-only`.

Map the bootstrapped layout inventory onto **standard archetypes** (adds `title`, `section`, `title_and_bullets`, `title_subtitle_and_bullets`, `text_with_image` — plus legacy `image_left_text_right`):

Non-interactive best-effort mapping (prints updated spec JSON):

```bash
slide-smith map-template --template my_template --templates-dir ./templates
```

Apply caller-agent hints (optional):

```bash
slide-smith map-template --template my_template --templates-dir ./templates --hints /path/to/hints.json
```

Interactive mapping / review + write back to `template.json`:

```bash
slide-smith map-template --template my_template --templates-dir ./templates --interactive --write
```

Tooling-friendly output:

- print only the standard-archetype patch:

```bash
slide-smith map-template --template my_template --templates-dir ./templates --print patch
```

- print a structured help request (for caller-agent hint generation):

```bash
slide-smith map-template --template my_template --templates-dir ./templates --print help-request
```

Validate the generated template package:

Structural validation (layouts/placeholders exist):

```bash
slide-smith validate-template --template my_template --templates-dir ./templates
```

Standard-compat validation (standard archetypes + required slots are mapped). For redesigned archetypes, remember: the **deck spec** may be structured (e.g. `items[]`), but the **template spec** still maps concrete render-time slot names (`col1_body`, `col1_icon`, `left_image`, etc.).

```bash
slide-smith validate-template --template my_template --templates-dir ./templates --profile standard
```

Extended-compat validation (extended archetypes library, including redesigned extended archetypes like `picture_compare`, `three_col_with_icons`, etc. when present in the template spec). For redesigned `items[]`/`left`+`right` archetypes, ensure the template spec exposes the expected render-time slot naming convention (e.g. `col1_icon`, `item1_body`, `left_image`, ...):

```bash
slide-smith validate-template --template my_template --templates-dir ./templates --profile extended
```

Generate a dummy deck spec that exercises a template’s archetypes:

```bash
slide-smith make-dummy-deck-spec \
  --template my_template \
  --templates-dir ./templates \
  --output /tmp/dummy-deck.json
```

Render that dummy deck for human review:

```bash
slide-smith create \
  --input /tmp/dummy-deck.json \
  --template my_template \
  --templates-dir ./templates \
  --output /tmp/dummy-review.pptx
```

### Create (render) a deck

```bash
slide-smith create \
  --input docs/design/examples/deck-spec.full.sample.json \
  --template default \
  --output /tmp/out.pptx

# Redesign examples (base vs extended):
slide-smith create \
  --input docs/examples/redesign/base.sample.json \
  --template default \
  --output /tmp/out.base.pptx

# External templates root:
slide-smith create \
  --input docs/design/examples/deck-spec.full.sample.json \
  --template default \
  --templates-dir /path/to/templates \
  --output /tmp/out.pptx
```
