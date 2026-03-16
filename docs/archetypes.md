# Archetypes Guide

This is the user-facing guide to the current Slide Smith archetype set.

Use this doc when you want to know:
- which archetype to choose
- what fields each archetype expects
- how repeated-item layouts are represented
- which legacy names are still accepted

For the exact machine-readable contract, see:
- `docs/design/deck-spec.schema.json`

---

# Quick start

Slide Smith has two practical groups of archetypes:

## Base archetypes
Use these first. They are the most stable and broadly reusable.

- `title`
- `section`
- `title_and_bullets`
- `title_subtitle_and_bullets`
- `text_with_image`

## Extended archetypes
Use these when your template supports richer branded layouts.

- `title_subtitle`
- `version_page`
- `agenda_with_image`
- `two_col_with_subtitle`
- `three_col_with_subtitle`
- `three_col_with_icons`
- `five_col_with_icons`
- `picture_compare`
- `title_only_freeform`

---

# General rules

## Prefer semantic names
Use names that describe the content pattern, not the geometry.

Preferred:
- `text_with_image`
- `picture_compare`

Legacy but still accepted:
- `image_left_text_right`

## Template decides layout
The archetype describes the slide’s content shape.
The template decides the actual visual layout and placeholder mapping.

## Images
Image fields accept either:
- a string path
- or an object like:

```json
{ "path": "assets/example.png", "alt": "description" }
```

## Notes
Any slide may include:

```json
"notes": "speaker notes here"
```

---

# Base archetypes

## `title`
Best for cover/opening slides.

### Required
- `title`

### Optional
- `subtitle`

### Example

```json
{
  "archetype": "title",
  "title": "Q2 Business Review",
  "subtitle": "Draft for leadership review"
}
```

---

## `section`
Best for section divider slides.

### Required
- `title`

### Example

```json
{
  "archetype": "section",
  "title": "Market Context"
}
```

---

## `title_and_bullets`
Best for a standard explanatory content slide.

### Required
- `title`
- one of:
  - `bullets`
  - `body`

### Example with bullets

```json
{
  "archetype": "title_and_bullets",
  "title": "Highlights",
  "bullets": ["Revenue up 20%", "Margin improved", "Pipeline strong"]
}
```

### Example with body

```json
{
  "archetype": "title_and_bullets",
  "title": "Summary",
  "body": "A concise explanation of the slide content."
}
```

---

## `title_subtitle_and_bullets`
Like `title_and_bullets`, but with a required subtitle.

### Required
- `title`
- `subtitle`
- one of:
  - `bullets`
  - `body`

### Example

```json
{
  "archetype": "title_subtitle_and_bullets",
  "title": "Plan",
  "subtitle": "Next 90 days",
  "bullets": ["Stabilize", "Measure", "Scale"]
}
```

---

## `text_with_image`
Best for a slide with explanatory text plus one image.

### Required
- `title`
- `body`
- `image`

### Legacy alias
- `image_left_text_right`

### Example

```json
{
  "archetype": "text_with_image",
  "title": "Target workflow",
  "body": "The new flow reduces manual handoffs and clarifies ownership.",
  "image": "assets/workflow.png"
}
```

---

# Extended archetypes

## `title_subtitle`
Best for a simple title + subtitle slide without body content.

### Required
- `title`
- `subtitle`

### Example

```json
{
  "archetype": "title_subtitle",
  "title": "Operating model",
  "subtitle": "Overview"
}
```

---

## `version_page`
Best for release/version history pages.

### Required
- `title`
- `table_text`

### Example

```json
{
  "archetype": "version_page",
  "title": "Version history",
  "table_text": "| Version | Date | Notes |\n|---|---|---|\n| 2.0 | 2026-03-15 | Archetype redesign |"
}
```

---

## `agenda_with_image`
Best for agenda/steps slides with a supporting visual.

### Required
- `title`
- `image`
- `items`

### `items[]` shape
Each item should look like:

```json
{ "marker": "1", "body": "Introduction" }
```

`marker` is optional.

### Example

```json
{
  "archetype": "agenda_with_image",
  "title": "Agenda",
  "image": "assets/agenda.png",
  "items": [
    { "marker": "1", "body": "Context" },
    { "marker": "2", "body": "Approach" },
    { "marker": "3", "body": "Recommendation" }
  ]
}
```

---

## `two_col_with_subtitle`
Best for two parallel text columns with a subtitle.

### Required
- `title`
- `subtitle`
- `col1_body`
- `col2_body`

### Example

```json
{
  "archetype": "two_col_with_subtitle",
  "title": "Compare options",
  "subtitle": "Current vs target",
  "col1_body": "Current state details",
  "col2_body": "Target state details"
}
```

---

## `three_col_with_subtitle`
Best for three repeated text columns with a subtitle.

### Required
- `title`
- `subtitle`
- `items`

### `items[]` shape

```json
{ "title": "Column title", "body": "Column body" }
```

Expected length: 3.

### Example

```json
{
  "archetype": "three_col_with_subtitle",
  "title": "Workstreams",
  "subtitle": "Three parallel tracks",
  "items": [
    { "title": "People", "body": "Roles, skills, adoption" },
    { "title": "Process", "body": "Ways of working" },
    { "title": "Technology", "body": "Platforms and tooling" }
  ]
}
```

---

## `three_col_with_icons`
Best for three repeated columns where each item has an icon.

### Required
- `title`
- `items`

### `items[]` shape

```json
{ "title": "...", "body": "...", "icon": "assets/icon.png", "caption": "optional" }
```

Expected length: 3.

### Example

```json
{
  "archetype": "three_col_with_icons",
  "title": "Capabilities",
  "items": [
    { "title": "Analyze", "body": "Find patterns", "icon": "assets/a.png" },
    { "title": "Automate", "body": "Reduce manual work", "icon": "assets/b.png" },
    { "title": "Govern", "body": "Control and review", "icon": "assets/c.png" }
  ]
}
```

---

## `five_col_with_icons`
Best for five repeated icon+text items.

### Required
- `title`
- `items`

### `items[]` shape

```json
{ "icon": "assets/icon.png", "body": "Item text" }
```

Expected length: 5.

### Example

```json
{
  "archetype": "five_col_with_icons",
  "title": "Principles",
  "items": [
    { "icon": "assets/1.png", "body": "Simple" },
    { "icon": "assets/2.png", "body": "Secure" },
    { "icon": "assets/3.png", "body": "Fast" },
    { "icon": "assets/4.png", "body": "Reusable" },
    { "icon": "assets/5.png", "body": "Measured" }
  ]
}
```

---

## `picture_compare`
Best for left/right visual comparison.

### Required
- `title`
- `left`
- `right`

### `left` / `right` shape

```json
{ "image": "assets/example.png", "title": "optional", "body": "optional" }
```

### Example

```json
{
  "archetype": "picture_compare",
  "title": "Before and after",
  "left": {
    "image": "assets/before.png",
    "title": "Before",
    "body": "Manual handoffs"
  },
  "right": {
    "image": "assets/after.png",
    "title": "After",
    "body": "Automated flow"
  }
}
```

---

## `title_only_freeform`
Best for very low-structure slides where the template mainly needs a title and the rest is intentionally loose.

### Required
- `title`

### Example

```json
{
  "archetype": "title_only_freeform",
  "title": "Discussion"
}
```

---

# Repeated-item conventions

For newer repeated layouts, prefer structured arrays over flat numbered fields.

Use:

```json
{
  "items": [
    { "title": "...", "body": "..." }
  ]
}
```

instead of inventing new input shapes like:
- `item1_body`
- `item2_body`
- `item3_body`

The renderer may still target numbered template slots internally, but user input should stay structured.

---

# Overflow behavior

If you provide more items than a template layout can display:
- current behavior is deterministic and template-limited
- in practice, keep item counts aligned to the intended archetype

Recommended counts:
- `three_col_with_subtitle`: 3 items
- `three_col_with_icons`: 3 items
- `five_col_with_icons`: 5 items

---

# Legacy compatibility

Still accepted:
- `image_left_text_right` → `text_with_image`
- `title_and_bullets_with_subtitle` → `title_subtitle_and_bullets`

Legacy extended archetypes are also still supported in the product, but they are not the preferred current vocabulary.

---

# Template slot conventions

Most users do not need to care about template slot names directly.

If you are editing `template.json`, the current canonical render-time slot names are:
- `item{n}_body`, `item{n}_marker` for `agenda_with_image`
- `col{n}_icon`, `col{n}_title`, `col{n}_body`, `col{n}_caption` for `three_col_with_icons`
- `item{n}_icon`, `item{n}_body` for `five_col_with_icons`
- `left_image`, `left_title`, `left_body`, `right_image`, `right_title`, `right_body` for `picture_compare`

These conventions should stay stable across template mapping and validation.

---

# Recommended default choice

If you are unsure, start with the base set:
- `title`
- `section`
- `title_and_bullets`
- `title_subtitle_and_bullets`
- `text_with_image`

Then move to extended archetypes only when your chosen template clearly supports them.
