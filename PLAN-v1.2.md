# v1.2 Project Plan — Exemplar-first reference deck workflow

Target: **v1.2**

Source design: `docs/design/v1.2-exemplar-first.md`

## Checklist

### M0 — Docs + scaffolding
- [ ] Add JSON schema stubs for StyleProfile / SlidePlan / DeckSpec (optional but recommended)
- [ ] Add fixtures folder structure for reference decks + golden outputs

### M1 — `analyze` (reference → StyleProfile)
- [ ] Extract slide size
- [ ] Enumerate layouts
- [ ] Extract placeholder types/idx + bounding boxes
- [ ] Produce stable `layoutId`
- [ ] Theme extraction (best-effort): major/minor fonts, accent colors
- [ ] Tests: snapshot `style.profile.json`

### M2 — `plan` (markdown → SlidePlan)
- [ ] Deterministic markdown parsing rules
- [ ] Slide intents: title, section, bullets, two_column, image
- [ ] Tests: snapshot `slide.plan.json`

### M3 — `compile` (SlidePlan + StyleProfile → DeckSpec)
- [ ] Layout schema signature + matcher
- [ ] Deterministic tie-breaking
- [ ] Great error messages when no layout matches
- [ ] Tests: golden deck.spec.json for sample plans

### M4 — `render` (DeckSpec + reference → output.pptx)
- [ ] Create slides from reference layouts
- [ ] Fill text placeholders
- [ ] Fill picture placeholders
- [ ] Asset handling (local paths)
- [ ] Tests: render smoke test + validate roundtrip

### M5 — `validate` (output vs reference/profile)
- [ ] Ensure only known layouts used
- [ ] Ensure placeholder-only edits (no unexpected shapes)
- [ ] Theme checks where possible (warn if incomplete)
- [ ] JSON report output

### M6 — Release
- [ ] Update README
- [ ] Update CHANGELOG.md
- [ ] Tag v1.2
