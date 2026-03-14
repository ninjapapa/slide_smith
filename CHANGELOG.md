# Changelog

## Unreleased

- v1.2 (WIP): exemplar-first / reference deck pipeline (LLM-free):
  - `analyze` → StyleProfile
  - `plan` → SlidePlan
  - `compile-exemplar` → DeckSpec
  - `render-exemplar` → PPTX
  - `validate-exemplar` → validation report

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

