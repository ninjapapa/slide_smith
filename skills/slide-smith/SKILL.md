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
  - `docs/design/examples/deck-spec.full.sample.json`
  - `docs/design/examples/deck-spec.sample.json`

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
  --archetype image_left_text_right \
  --write

# Force box-only (debug/compat):
slide-smith bootstrap-from-slide \
  --pptx /path/to/deck.pptx \
  --slide 10 \
  --template-id my_template \
  --out-dir ./templates \
  --archetype image_left_text_right \
  --boxes-only \
  --write
```

Notes:
- This creates `templates/my_template/template.pptx` (copy of the input PPTX) + `template.json`.
- Default behavior is **placeholder-first**: when the slide/layout exposes real placeholders, the archetype slots use `placeholder_idx`.
- If placeholders can’t be inferred reliably, it falls back to `box` geometry (`units: relative`).
- You can force legacy behavior with `--boxes-only`.

Map the bootstrapped layout inventory onto **standard archetypes** (adds `title`, `section`, `title_and_bullets`, `image_left_text_right`):

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

Standard-compat validation (standard archetypes + required slots are mapped):

```bash
slide-smith validate-template --template my_template --templates-dir ./templates --profile standard
```

Extended-compat validation (extended archetypes library):

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

# External templates root:
slide-smith create \
  --input docs/design/examples/deck-spec.full.sample.json \
  --template default \
  --templates-dir /path/to/templates \
  --output /tmp/out.pptx
```

Script-friendly output only:

```bash
slide-smith create \
  --input <deck.json> \
  --template default \
  --output /tmp/out.pptx \
  --print none
```

Collect assets for reproducible runs (copies images and rewrites deck JSON paths):

```bash
slide-smith create \
  --input <deck.json> \
  --template default \
  --assets-dir /tmp/slide-smith-assets \
  --output /tmp/out.pptx
```

### Export previews for caller-agent assistance (v1.1)

`export-previews` produces a machine-readable manifest of layouts/placeholders for a template (and will later grow optional PNG exports).

```bash
slide-smith export-previews --template my_template --templates-dir ./templates --out-dir /tmp/my_template-previews --mode layouts
```

### Inspect a template

```bash
slide-smith inspect-template --template default
```

If your templates live outside the repo, pass a templates root:

```bash
slide-smith inspect-template --template default --templates-dir /path/to/templates
```

### Validate a template package

Structural validation (layouts/placeholders exist):

```bash
slide-smith validate-template --template default
```

```bash
slide-smith validate-template --template default --templates-dir /path/to/templates
```

Standard-compatibility validation (ensures the template can render standard deck inputs):

```bash
slide-smith validate-template --template default --profile standard
```

Notes:
- If `templates/<id>/template.pptx` is missing, **structural** validation exits 0 with a warning (JSON-only templates are allowed early-stage).
- For `--profile standard` / `--profile extended`, semantic validation still runs against `template.json` even if `template.pptx` is missing.
- `--profile standard` checks for the standard archetypes + required semantic slots having `placeholder_idx` mappings.
- `--profile extended` checks for the extended archetype library slot mappings.
- Box-based slots: rendering supports `slot.box` (units `relative|emu`) as a fallback when `placeholder_idx` is absent (useful for slide-instance-derived templates).

### Iterative edit ops (on an existing PPTX)

List slides:

```bash
slide-smith list-slides --deck /tmp/out.pptx
```

Add slide (append-only right now; `--after` must be the current last index):

```bash
slide-smith add-slide \
  --deck /tmp/out.pptx \
  --after 2 \
  --type title_and_bullets \
  --input /path/to/slide.json
```

Update slide (patch JSON supports `title`, `subtitle`, `body`, `bullets`, `notes`, `image`):

```bash
slide-smith update-slide \
  --deck /tmp/out.pptx \
  --index 1 \
  --input /path/to/patch.json
```

Delete slide:

```bash
slide-smith delete-slide --deck /tmp/out.pptx --index 0
```

## Hybrid workflow (branded style source + reliable structural exemplar)

When a branded `.potx` is visually rich but unreliable for full end-to-end generation:

- Use a **reliable structural reference** (pptx/potx) for layout-driven generation.
- Use the branded template as a **style source** for manual review and iterative refinements.

Near-term recommended flow:

1) Generate a first-pass deck with a structural exemplar:
   - `analyze` / `plan` / `compile-exemplar` / `render-exemplar`
2) Manually apply branded styling in PowerPoint (or bootstrap a template package from the branded file and switch to template-first `create` once mappings validate).

See `docs/design/rich-potx-and-hybrid-workflow.md`.

## Caller-agent workflow notes (important)

Slide Smith has **no LLM**. The intended split of responsibilities is:

- **Caller agent (LLM)**:
  - chooses which template/layouts/slides to use as exemplars
  - decides which archetypes it wants (core or template-native)
  - supplies mapping hints only when needed

- **Slide Smith (deterministic tool)**:
  - inspects PPTX/POTX structure
  - prefers **placeholder-first** mappings (populate real placeholders)
  - falls back to box geometry only when placeholders are not available/usable
  - validates mappings and renders output PPTX

If output shows duplicated text or “boxes on top of placeholders”, it usually means you bootstrapped/mapped using boxes when the layout actually has placeholders. Re-run bootstrap/mapping with placeholder-first.

## Agent guidance

- Prefer the **fixtures** in `docs/design/examples/` when writing tests or smoke commands.
- When rendering with images, use `--assets-dir` to avoid fragile relative-path failures.
- If validation fails:
  - First read the printed path-qualified errors.
  - Then check the schema: `docs/design/deck-spec.schema.json`.
- Keep stdout deterministic for agents: use `--print none` unless the normalized deck JSON is explicitly needed.
