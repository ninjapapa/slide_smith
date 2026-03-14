# Rich POTX support + hybrid workflow (design)

**Status:** draft

Related issues:
- Master: #71
- POTX layout parity: #72
- Rich layout extraction: #73
- Bootstrap/validation improvements: #74
- Hybrid workflow docs: #75
- Regression fixtures/tests: #76

---

## Context

slide_smith now has two distinct workflows:

1) **Template-first (v1.0–v1.1):** JSON Deck Spec → PPTX using a template package (`template.json` + `template.pptx`).
2) **Exemplar-first (v1.2 WIP):** Markdown → SlidePlan → DeckSpec → PPTX, using a **reference deck** (PPTX/POTX) as a style/layout source.

A recurring real-world need: branded design templates (often delivered as `.potx`) can be *visually rich* but may not be directly usable end-to-end (layout enumeration gaps, validation mismatches, incomplete placeholder semantics). Meanwhile, a “good” exemplar deck may be structurally reliable.

This doc proposes:

- how we should treat **POTX** inputs (reference/template sources)
- how to achieve **layout enumeration parity** with the underlying OpenXML package
- how to support a pragmatic **hybrid workflow** (style source ≠ structural exemplar)

---

## Problem statement

Observed on Graphik-like branded templates:

- A `.potx` can contain a large set of layouts and themes.
- Current inspection/analyze paths may surface only a subset of those layouts.
- Bootstrapping from a slide instance can create useful box-based archetypes, but validation can fail due to layout resolution mismatch.

We need to make “rich template sources” usable without fragile manual steps.

---

## Design goals

### G1 — POTX as a first-class reference source

- Anywhere we accept `--reference <file.pptx>`, we should accept `.potx`.
- Behaviors should not depend on extension; prefer content-based handling.

### G2 — Layout enumeration parity

- `inspect-pptx` and `analyze` should expose as many usable slide layouts as the package contains.
- If we intentionally filter, it must be explicit and documented (e.g., skip layouts with zero placeholders).

### G3 — Stable identifiers

- Layout IDs used by exemplar-first should be stable for a given reference.
- Avoid relying purely on layout names (often duplicated or localized).

### G4 — Hybrid workflow support

Enable using:

- a **structural exemplar** (reliable layouts for deck structure), and
- a **styling source** (branded theme, fonts, colors, design language)

…with a deterministic, documentable pipeline.

### G5 — Testability

Add fixtures and regression tests that cover:

- rich `.potx` sources
- conversion to `.pptx`
- extraction counts and stable IDs
- bootstrapped slide-derived templates

---

## Proposed approach

### A) POTX acceptance

**Current:** `python-pptx` can usually open `.potx` via `Presentation(path)`.

**Design:**
- Treat `.pptx` and `.potx` as equivalent “presentation packages” for reference-style operations.
- CLI help text should explicitly say `(pptx|potx)`.

### B) Improve layout extraction

**Today (python-pptx):** `Presentation(...).slide_layouts` enumerates layouts exposed through python-pptx. In some cases, this set can be smaller than the raw package inventory (or python-pptx may hide certain constructs).

**Design direction:**

1. Keep current python-pptx-based enumeration as baseline.
2. Add an optional *raw OpenXML* inspection mode when parity matters:
   - enumerate `ppt/slideLayouts/slideLayout*.xml`
   - parse placeholders from XML (`p:ph` elements), bbox (`a:xfrm`)
   - attach these as additional “raw layouts” to StyleProfile
3. Document differences:
   - layouts with no usable placeholders
   - duplicate names
   - placeholder type mapping differences

This helps issue #72 and creates a foundation for #73.

### C) Stable Layout IDs

**Today (v1.2):** `layoutId` derived from layout index + name + placeholder signature hash.

**Improvement:** Prefer IDs derived from the **part name** (`slideLayout#.xml`) + placeholder schema hash:

- `layout:{part}:{schemaHash}`

This avoids reindexing instability and supports raw OpenXML enumeration.

### D) Bootstrap-from-slide reliability

When a slide-derived archetype is box-based (no placeholder mapping), validation should not require a layout-name lookup.

**Design:**
- For slide-derived templates, store a “rendering mode”:
  - `mode=box_only` → validation does not require layout resolution
  - `mode=layout_placeholder` → strict validation

This addresses #74.

### E) Hybrid workflow

**Motivation:** style source decks may be great for theme, but not stable for layout-driven generation.

**Proposed workflow:**

- Use `reference_structural.(pptx|potx)` to define layouts + placeholder schemas.
- Use `reference_style.(pptx|potx)` to define theme tokens (fonts/colors) and reusable treatments.

Artifacts:

- `StyleProfile(structure)`
- `StyleProfile(style)` or `ThemeProfile`

Compilation uses structure layouts; rendering applies theme tokens from style profile when possible.

In v1.2 we can document this as a recommended **near-term manual workflow**, and later formalize as a second reference input.

---

## CLI proposals (future; not necessarily v1.2)

- `slide-smith analyze --reference file.(pptx|potx) --out style.profile.json [--mode pptx|raw]`
- `slide-smith inspect-pptx --pptx file.(pptx|potx) [--mode pptx|raw]`
- `slide-smith analyze-theme --reference file.(pptx|potx) --out theme.profile.json`
- `slide-smith render-exemplar --reference-structure A --reference-style B ...` (hybrid)

---

## Validation implications

Validator should distinguish between:

- **structural compliance**: only allowed layouts and placeholder edits
- **style compliance**: theme token usage (best-effort)

For rich template sources, style compliance will often be incomplete; warnings are acceptable.

---

## Test plan (fixtures)

To keep repo size manageable:

- Prefer **minimal synthetic decks** created with python-pptx for unit tests.
- For rich POTX fixtures:
  - store privately or via git-lfs, or
  - store reduced versions (strip media), or
  - store “extraction snapshots” (layout inventory JSON) committed to repo.

Add regression tests for:

- layout count parity expectation (documented filters)
- stable IDs unchanged across runs
- bootstrap-from-slide artifacts validate in box-only mode

---

## Open questions

- What is the acceptable dependency footprint for raw OpenXML parsing (lxml vs stdlib xml.etree)?
- How to define “usable layout” rigorously (at least one placeholder? must include title/body?)
- How to represent multiple themes/masters in StyleProfile?
