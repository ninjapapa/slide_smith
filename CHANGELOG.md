# Changelog

## Unreleased

## v3.1.0 — 2026-03-16

### Highlights
- completed the renderer decomposition and retired legacy layout-family code paths
- removed legacy deck/template compatibility shims so the active surface is now strictly `layout_id` / `layouts`
- cleaned internal/runtime/template naming to match the current model
- refreshed docs, examples, and template metadata around the stable layout set

### Breaking cleanup
- removed legacy deck input compatibility for `archetype`
- removed legacy layout alias compatibility such as `image_left_text_right`
- removed template compatibility for `archetypes` and `native.archetypes`; templates now use `layouts` and `native.layouts`

### Notes
- fallback layout remains `title_and_bullets`
- historical redesign/exemplar artifacts were either retired or clearly marked historical

## v3.0.0 — 2026-03-16

### Highlights
- simplified the public CLI around the current product surface
- made `layout_id` the primary user-facing slide field
- added `slide-smith help api` for discoverable, machine-readable layout guidance
- tightened docs around the stable layout set and fallback behavior

### Current primary commands
- `create`
- `validate`
- `help api`
- `insert-slide`
- `update-slide`
- `delete-slide`

### Compatibility notes
- legacy `archetype` input is still accepted during migration, but callers should use `layout_id`
- fallback layout remains `title_and_bullets`
- old inspect/bootstrap/exemplar workflows are no longer part of the primary product surface

## v2.0.0 — 2026-03-15

- simplified CLI and product surface around current supported workflows
- added layout API help output and aligned docs/tests with the current layout contract
- kept migration compatibility for legacy `archetype` input while moving user-facing docs to `layout_id`

## v1.0.0 — 2026-03-10

- CI workflow (pytest on PR/push)
- Asset collection (`create --assets-dir`)
- Template-driven styling (v1 + v2)
- Speaker notes support
- Deck spec schema validation (jsonschema)
- Edit ops expanded (list/delete slides, update notes/image)
- Template validation tooling (`validate-template`)
- Standard template mapping workflow:
  - `map-template` (best-effort inference, interactive review, patch output)
  - `validate-template --profile standard`
- Renderer now uses `template.json` slot mappings (`placeholder_idx`) and errors are more actionable

