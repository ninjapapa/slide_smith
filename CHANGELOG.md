# Changelog

## Unreleased

- retired legacy renderer families and old experimental layout support from the active product surface
- aligned renderer dispatch, validation, and template semantics to the stable layout set only
- made markdown parsing emit current `layout_id` values instead of legacy archetype names
- simplified deck-spec normalization toward a `layout_id`-native model while keeping the minimal internal renderer shim
- reduced remaining legacy `archetype` wording in renderer/template validation paths
- marked redesign-era planning docs and exemplar fixtures as historical to avoid confusion with the live product surface

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

