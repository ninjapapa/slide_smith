# Canonical Agentic COE 2026 Simple Template

This note is retained only as historical context for the simplified branded template that influenced the current Slide Smith layout vocabulary.

## Current relevance

What still matters from this template:
- it helped shape the current user-facing layout set
- it validated the move toward simpler semantic layout names
- it reinforced template-first rendering with a smaller stable command surface

## What to use now

Use the current CLI:

```bash
slide-smith create --input <deck.json> --template <template_id> --templates-dir <templates_dir> --output <out.pptx> --print none
slide-smith validate --input <deck.json> --template <template_id> --templates-dir <templates_dir>
slide-smith insert-slide --deck <out.pptx> --after <index> --layout-id <layout_id> --input <slide.json>
slide-smith update-slide --deck <out.pptx> --index <index> --input <patch.json>
slide-smith delete-slide --deck <out.pptx> --index <index>
```

## Current docs to prefer
- `docs/layout-ids.md`
- `docs/design/deck-spec.md`
- `docs/examples/redesign/README.md`

This document no longer describes an active bootstrap/map/validate-template workflow.
