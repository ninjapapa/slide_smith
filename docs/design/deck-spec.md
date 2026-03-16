# Deck Spec

This is the current normalized deck-spec model for `slide-smith` v2.x.

The JSON schema source of truth is:
- `docs/design/deck-spec.schema.json`

## Purpose

All supported inputs normalize into a deck spec before schema validation and rendering.

The deck spec is designed to be:
- easy for agents to author
- explicit enough to validate reliably
- compatible with both legacy aliases and the current redesigned archetypes
- template-first, so templates control actual layout/slot mapping

## Top-level shape

```json
{
  "title": "Q2 Business Review",
  "subtitle": "Draft for leadership review",
  "slides": [
    {
      "archetype": "title_and_bullets",
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
- `archetype: string`
- `title: string`
- `subtitle?: string`
- `body?: string`
- `bullets?: string[]`
- `image?: string | { path: string, alt?: string }`
- `notes?: string`

Additional archetype-specific fields include things like:
- `table_text`
- `items[]`
- `colN_*`
- `itemN_*`
- `left` / `right`

## Current archetype families

### Base
- `title`
- `section`
- `title_and_bullets`
- `title_subtitle_and_bullets`
- `text_with_image`

### Legacy alias still accepted
- `image_left_text_right` → normalized/treated as `text_with_image`

### Extended
- `title_subtitle`
- `version_page`
- `agenda_with_image`
- `two_col_with_subtitle`
- `three_col_with_subtitle`
- `three_col_with_icons`
- `five_col_with_icons`
- `picture_compare`
- `title_only_freeform`

### Legacy extended archetypes still supported
- `two_col`
- `three_col`
- `four_col`
- `pillars_3`
- `pillars_4`
- `table`
- `table_plus_description`
- `timeline_horizontal`

## Validation

Use:

```bash
slide-smith validate-deck-spec --input <deck.json> --profile legacy
```

Schema validation is also applied during `slide-smith create` when `jsonschema` is available.

## Examples

Current examples live under:
- `docs/examples/redesign/base.sample.json`
- `docs/examples/redesign/extended.sample.json`

## Notes

- Template layout resolution is controlled by `template.json`, not by the deck spec itself.
- Repeated-item archetypes use canonical slot naming conventions documented in `docs/archetypes.md`.
- The schema file should be treated as authoritative when there is any ambiguity.
