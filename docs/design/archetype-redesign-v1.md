# Archetype Redesign v1 — Base vs Extended (Branded Template Learnings)

Status: **Draft (v1.1 — vocabulary + slots proposal)**  
Owner: Bo  
Parent: Issue #97  
Sub-issue (vocab/slots): #98

## Context

Recent work with the simplified branded template **“Agentic COE 2026 simple template.pptx”** suggests our current archetype vocabulary is:

- slightly overfit to earlier inferred mappings (`image_left_text_right`, generic `two_col`/`three_col`), and
- not clearly split between a **small, stable base set** vs. **template-native extended layouts**.

This doc proposes a concrete redesign that better matches real-world branded layout sets while preserving template-first generation.

## Goals

1. Establish a **small, stable Base archetype set** for automated generation.
2. Introduce an **Extended archetype set** for richer branded template-native layouts.
3. Improve semantic naming (describe intent, not geometry where possible).
4. Keep the system evolvable: allow templates to map “base” archetypes onto template-native layouts.

## Non-goals

- Rewriting all existing templates immediately.
- Breaking existing deck specs without a deprecation window.
- Designing a fully generic “layout DSL”.

## Template evidence (simplified branded template)

Detected layout names (from issue #97):

- Cover: light mode
- Session
- Version Page
- Content: title only
- Content: title content-box
- Content: title subtitle only
- Content: title subtitle content box
- Content: 2 columns + subtitle
- Agenda: image
- Content: column + image
- Content: picture compare
- Content: 3 columns
- Content: 3 columns with icons
- Content: 5 columns with icon

---

# Vocabulary + Slot Conventions (proposal)

This section is intended to resolve sub-issue **#98**.

## Naming rules

1. **Prefer semantic names** over geometry-bound names.
   - Good: `text_with_image`, `picture_compare`
   - Avoid: `image_left_text_right` (keep only as a legacy alias)

2. **Archetype id reflects content intent**; templates decide exact layout geometry.

3. **Slots are stable API**. If we need to change a slot name, we do it via aliases + deprecation.

## Slot conventions

### Common fields

All slides:
- `archetype: string`
- `title: string`
- `notes?: string`

Optional common:
- `subtitle?: string`

### Text blocks

- Prefer `body: string` for a single text blob.
- Prefer `bullets: string[]` when content is a list.
- For columnar layouts, use explicit `col{i}_body` (and optionally `col{i}_title`).

### Images

`image` uses existing image union:
- string path, or
- `{ path: string, alt?: string }`

## Legacy name migration

Supported legacy → preferred:

- `image_left_text_right` → `text_with_image`
- `title_and_bullets_with_subtitle` → `title_subtitle_and_bullets`

For multi-image layouts:
- `left_image`, `right_image`, etc.

### Repeated items

New archetypes that represent “N repeated things” should use arrays, not `item1_*` fields.

Pattern:

```json
{
  "items": [
    { "title": "...", "body": "...", "icon": {"path": "..."} }
  ]
}
```

We intentionally cap max lengths to the template’s capacity (see Overflow behavior).

## Overflow behavior (must be deterministic)

When an archetype receives more items than a layout supports:

- **Default:** truncate to capacity and add a warning.
- Optional future enhancement: `params.overflow: "error" | "truncate"`.

---

# Proposed Archetype Sets

## Base (stable, reusable)

These should be the default “agent-friendly” primitives.

### 1) `title`
- required: `title`
- optional: `subtitle`

### 2) `section`
- required: `title`

### 3) `title_and_bullets`
- required: `title`
- one of:
  - `bullets: string[]`
  - `body: string`

### 4) `title_subtitle_and_bullets`
- required: `title`, `subtitle`
- one of:
  - `bullets: string[]`
  - `body: string`

### 5) `text_with_image`
- required: `title`, `body`, `image`
- notes:
  - legacy alias: `image_left_text_right`

## Extended (template-native)

### 1) `title_subtitle`
- required: `title`, `subtitle`

### 2) `version_page`
- required: `title`
- one of:
  - `table_text: string` (markdown table or pipe-separated)
  - `table: { columns: string[], rows: string[][] }` (future)

### 3) `agenda_with_image`
- required: `title`, `image`, `items`
- `items: { marker?: string, body: string }[]`

### 4) `two_col_with_subtitle`
- required: `title`, `subtitle`, `col1_body`, `col2_body`

### 5) `three_col_with_subtitle`
- required: `title`, `subtitle`, `items`
- `items: { title?: string, body: string }[]` (expected length 3)

### 6) `three_col_with_icons`
- required: `title`, `items`
- `items: { title: string, body: string, icon: image, caption?: string }[]` (expected length 3)

### 7) `five_col_with_icons`
- required: `title`, `items`
- `items: { icon: image, body: string }[]` (expected length 5)

### 8) `picture_compare`
- required: `title`, `left`, `right`
- `left: { image: image, title?: string, body?: string }`
- `right: { image: image, title?: string, body?: string }`

### 9) `title_only_freeform`
- required: `title`

---

# Schema & Validation Implications

### Deck spec schema

- Add these archetypes to `docs/design/deck-spec.schema.json`.
- Prefer array-based representations for repeated items.

### Backward compatibility

Keep current v1.0/v1.1 archetypes working with a deprecation plan:

- `image_left_text_right` → alias to `text_with_image` (keep 1–2 releases).
- `two_col`/`three_col`/`four_col`/`pillars_*`/`table*` remain “legacy extended” for now.

Recommendation: **Additive-first**.

---

# Rendering & Template Mapping

## Renderer

- Base archetypes should remain directly renderable.
- Extended archetypes should be renderable when the template provides required placeholders.

## Template mapper / validator

- Template validation ensures required placeholders exist for each archetype.
- For array-based archetypes, mapping defines how items map into placeholder groups.

---

# Migration plan (recommended)

1. **Phase 0 (Docs/Spec):** finalize vocabulary + slot conventions.
2. **Phase 1 (Additive):** implement new archetypes alongside existing ones.
3. **Phase 2 (Aliases):** add compatibility aliases (e.g. `image_left_text_right` → `text_with_image`).
4. **Phase 3 (Deprecations):** warn on legacy names in CLI validate/create output.

---

# Open Questions

1. Should `version_page` standardize on `table_text` only initially?
2. Do we want a general `params` object for overflow policy now, or later?
3. For `agenda_with_image.items`, do we want `marker` to be auto-generated (1–5) if missing?

---

# Proposed work breakdown

See sub-issues split from #97.
