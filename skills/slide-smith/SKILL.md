---
name: slide-smith
description: "Create, validate, and structurally edit PowerPoint (.pptx) decks with Slide Smith. Use when an agent needs to render a PPTX from a JSON deck spec, validate template renderability slide by slide, inspect the supported `layout_id` API, or insert/update/delete slides in an existing deck."
---

# Slide Smith

Use Slide Smith as a deterministic JSON-deck-spec → PPTX tool with a small public CLI surface.

## Use it for
- `create` — render a deck spec to PPTX
- `validate` — check whether a template can render each slide
- `help api` — print the supported `layout_id` values and field expectations
- `insert-slide` — insert a new slide into an existing deck
- `update-slide` — patch a slide in an existing deck
- `delete-slide` — remove a slide from an existing deck

## Environment-specific defaults
Keep machine-local paths and defaults in agent memory or local notes, not in this shared skill.

Parameterize these when applying the skill:
- `<preferred_cli>`
- `<deck_workspace>`
- `<template_id>`
- `<templates_root>`

## Core model
- user-facing slide field: `layout_id`
- template package field: `layouts`
- optional template-native field: `native.layouts`
- fallback layout: `title_and_bullets`
- keep inputs as JSON deck specs
- let the template decide visual layout; `layout_id` describes content shape

## API discovery

Read the current supported API before inventing layouts or field names:

```bash
<preferred_cli> help api
```

If machine-readable output is available in the installed build, prefer:

```bash
<preferred_cli> help api --format json
```

## Current stable layout set
Prefer these first-class `layout_id` values:
- `title`
- `section`
- `title_and_bullets`
- `title_subtitle_and_bullets`
- `text_with_image`
- `version_page`
- `agenda_with_image`
- `two_col`
- `three_col_with_icons`
- `picture_compare`

## Recommended commands

### Render
```bash
<preferred_cli> create \
  --input <deck_workspace>/<deck>.json \
  --template <template_id> \
  --templates-dir <templates_root> \
  --output <deck_workspace>/<deck>.pptx
```

### Validate
```bash
<preferred_cli> validate \
  --input <deck_workspace>/<deck>.json \
  --template <template_id> \
  --templates-dir <templates_root>
```

### Insert slide
```bash
<preferred_cli> insert-slide \
  --deck /path/to/out.pptx \
  --after 1 \
  --layout-id title_and_bullets \
  --input /path/to/slide.json
```

### Update / delete
```bash
<preferred_cli> update-slide --deck /path/to/out.pptx --index 1 --input /path/to/patch.json
<preferred_cli> delete-slide --deck /path/to/out.pptx --index 1
```

## Deck shape

Use a top-level deck object like:

```json
{
  "title": "Optional",
  "subtitle": "Optional",
  "slides": [
    {
      "layout_id": "title_and_bullets",
      "title": "Example",
      "bullets": ["Point 1", "Point 2"]
    }
  ]
}
```

## Guidance
- Prefer the small stable layout set before proposing new layout types.
- Use `help api` instead of guessing layout names or field shapes.
- Run `validate` before `create` when unsure whether a template supports the requested layout mix.
- If validation reports fallback behavior, either accept the fallback or simplify the requested `layout_id`.
- Write deck specs with `layout_id`.
- For template packages, use `layouts` in `template.json` and `native.layouts` when needed.
- Keep the skill focused on normal deck creation, validation, and structural slide edits with the current CLI surface.
