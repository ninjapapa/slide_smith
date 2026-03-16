# Deck Spec

This is the current normalized deck-spec model for `slide-smith` v3.x.

The JSON schema source of truth is:
- `docs/design/deck-spec.schema.json`

## Purpose

All supported inputs normalize into a deck spec before schema validation and rendering.

The deck spec is designed to be:
- easy for agents to author
- explicit enough to validate reliably
- centered on the current `layout_id` API
- template-first, so templates control actual layout/slot mapping

## Top-level shape

```json
{
  "title": "Q2 Business Review",
  "subtitle": "Draft for leadership review",
  "slides": [
    {
      "layout_id": "title_and_bullets",
      "title": "Highlights",
      "bullets": ["Revenue up 20%", "Margin improved", "Pipeline remains strong"]
    }
  ]
}
```

## Top-level fields

- `title?: string`
- `subtitle?: string`
- `slides: Slide[]`

## Shared slide fields

Most slides use some subset of:
- `layout_id: string`
- `title: string`
- `subtitle?: string`
- `body?: string`
- `bullets?: string[]`
- `image?: string | { path: string, alt?: string }`
- `notes?: string`

Additional layout-specific fields include things like:
- `table_text`
- `items[]`
- `col1_body`, `col2_body`
- `left` / `right`

## Current layout families

### Core
- `title`
- `section`
- `title_and_bullets`
- `title_subtitle_and_bullets`
- `text_with_image`

### Stable non-core
- `version_page`
- `agenda_with_image`
- `two_col`
- `three_col_with_icons`
- `picture_compare`

### Migration alias still accepted
- `image_left_text_right` → normalized/treated as `text_with_image`

## Validation

Use:

```bash
slide-smith validate --input <deck.json> --template default
```

Schema validation is also applied during `slide-smith create` when `jsonschema` is available.

## Examples

Current examples live under:
- `docs/examples/redesign/base.sample.json`
- `docs/examples/redesign/extended.sample.json`

## Notes

- Template layout resolution is controlled by `template.json`, not by the deck spec itself.
- Repeated-item layouts use canonical slot naming conventions documented in `docs/layout-ids.md`.
- The schema file should be treated as authoritative when there is any ambiguity.
