---
name: slide-smith
description: Generate and iteratively edit PowerPoint (.pptx) decks using the slide-smith agent-first CLI. Use when an agent needs to: (1) render a PPTX from a JSON Deck Spec, (2) inspect/validate templates, (3) collect/copy image assets for reproducible runs, or (4) perform narrow deck edits (add/update/list/delete slides) on an existing PPTX.
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
pip install -e '.[dev]'
pytest -q
```

## Commands

### Create (render) a deck

```bash
slide-smith create \
  --input docs/design/examples/deck-spec.full.sample.json \
  --template default \
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

### Inspect a template

```bash
slide-smith inspect-template --template default
```

### Validate a template package

```bash
slide-smith validate-template --template default
```

Notes:
- If `templates/<id>/template.pptx` is missing, validation exits 0 with a warning (JSON-only templates are allowed early-stage).

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
