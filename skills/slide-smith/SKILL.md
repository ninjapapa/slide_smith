---
name: slide-smith
description: "Generate and iteratively edit PowerPoint (.pptx) decks using the slide-smith agent-first CLI. Use when an agent needs to: (1) render a PPTX from a JSON Deck Spec, (2) inspect/validate templates, (3) collect/copy image assets for reproducible runs, or (4) perform narrow deck edits (add/update/list/delete slides) on an existing PPTX."
---

# Slide Smith (agent-first PPTX tool)

## Canonical workflow (JSON-first)

Slide Smith’s core pipeline is:

1) **JSON Deck Spec** → 2) **PPTX**

Markdown ingestion is optional; prefer caller-side skills/tools to convert Markdown → JSON.

### Inputs
- Deck Spec schema: `docs/design/deck-spec.schema.json`
- Example fixtures:
  - `docs/design/examples/deck-spec.full.sample.json`
  - `docs/design/examples/deck-spec.sample.json`

## Local setup (recommended)

```bash
cd ~/slide_smith
python3 -m venv .venv
source .venv/bin/activate
pip install .
pytest -q
```

## Commands

### Bootstrap → map → validate a template from an example PPTX (standard workflow)

Inspect a PPTX to see layouts and placeholder indices:

```bash
slide-smith inspect-pptx --pptx /path/to/template.pptx
```

Inspect a *slide instance* (shapes + geometry), useful for decks that use free-positioned boxes rather than layout placeholders:

```bash
slide-smith inspect-slide --pptx /path/to/deck.pptx --slide 10
# text output:
slide-smith inspect-slide --pptx /path/to/deck.pptx --slide 10 --format text
```

Bootstrap a template package (copies PPTX + generates starter template.json containing `layout__*` archetypes):

```bash
slide-smith bootstrap-template \
  --pptx /path/to/template.pptx \
  --template-id my_template \
  --out-dir ./templates
```

Bootstrap a template *from a specific slide instance* (MVP: generates a **box-based** archetype draft; great for hand-designed decks with weak masters):

```bash
slide-smith bootstrap-from-slide \
  --pptx /path/to/deck.pptx \
  --slide 10 \
  --template-id my_template \
  --out-dir ./templates \
  --archetype image_left_text_right \
  --write
```

Notes:
- This creates `templates/my_template/template.pptx` (copy of the input PPTX) + `template.json`.
- The generated archetype slots use `box` geometry (`units: relative`) instead of `placeholder_idx`.

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

Render a dummy deck for human review:

```bash
slide-smith create \
  --input docs/design/examples/deck-spec.dummy.sample.json \
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

## Agent guidance

- Prefer the **fixtures** in `docs/design/examples/` when writing tests or smoke commands.
- When rendering with images, use `--assets-dir` to avoid fragile relative-path failures.
- If validation fails:
  - First read the printed path-qualified errors.
  - Then check the schema: `docs/design/deck-spec.schema.json`.
- Keep stdout deterministic for agents: use `--print none` unless the normalized deck JSON is explicitly needed.
