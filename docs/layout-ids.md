# Layout IDs Guide

This is the user-facing guide to the current Slide Smith `layout_id` API.

Use this doc when you want to know:
- which `layout_id` values are supported
- what fields each layout expects
- how repeated-item layouts are represented
- which legacy names are still accepted during migration

For the machine-readable contract, use:
- `slide-smith help api --format json`
- `docs/design/deck-spec.schema.json`

---

## Quick start

Supported `layout_id` values:
- `title`
- `section`
- `title_and_bullets`
- `title_subtitle_and_bullets`
- `text_with_image`
- `version_page`
- `agenda_with_image`
- `two_col`
- `three_col_with_icons`
- `picture_compare`

Fallback target when a requested layout cannot render:
- `title_and_bullets`

---

## General rules

### Use `layout_id`
The user-facing term is `layout_id`.

Legacy `archetype` input may still be accepted internally during migration, but callers should provide `layout_id`.

### Template decides visual layout
The `layout_id` describes the content shape.
The template decides the actual visual layout and placeholder mapping.

### Images
Image fields accept either:
- a string path
- or an object like:

```json
{ "path": "assets/example.png", "alt": "description" }
```

### Notes
Any slide may include:

```json
"notes": "speaker notes here"
```

---

## Layout IDs

### `title`
Required:
- `title`

Optional:
- `subtitle`
- `notes`

Example:
```json
{ "layout_id": "title", "title": "Q2 Business Review", "subtitle": "Draft for leadership review" }
```

---

### `section`
Required:
- `title`

Optional:
- `notes`

Example:
```json
{ "layout_id": "section", "title": "Market Context" }
```

---

### `title_and_bullets`
Required:
- `title`

Recommended:
- `bullets`

Also accepted:
- `body`
- `notes`

Example:
```json
{ "layout_id": "title_and_bullets", "title": "Highlights", "bullets": ["Revenue up 20%", "Margin improved", "Pipeline strong"] }
```

---

### `title_subtitle_and_bullets`
Required:
- `title`
- `subtitle`

Recommended:
- `bullets`

Also accepted:
- `body`
- `notes`

Example:
```json
{ "layout_id": "title_subtitle_and_bullets", "title": "Plan", "subtitle": "Next 90 days", "bullets": ["Stabilize", "Measure", "Scale"] }
```

---

### `text_with_image`
Required:
- `title`
- `image`

Recommended:
- `body`

Also accepted:
- `bullets`
- `notes`

Example:
```json
{ "layout_id": "text_with_image", "title": "Target workflow", "body": "The new flow reduces manual handoffs.", "image": "assets/workflow.png" }
```

Legacy alias still accepted during migration:
- `image_left_text_right`

---

### `version_page`
Required:
- `title`
- `table_text`

Example:
```json
{ "layout_id": "version_page", "title": "Version history", "table_text": "| Version | Date | Notes |\n|---|---|---|\n| 2.0 | 2026-03-15 | Simplified CLI |" }
```

---

### `agenda_with_image`
Required:
- `title`
- `image`
- `items`

`items[]` shape:
```json
{ "marker": "1", "body": "Introduction" }
```

Example:
```json
{ "layout_id": "agenda_with_image", "title": "Agenda", "image": "assets/agenda.png", "items": [{ "marker": "1", "body": "Context" }, { "marker": "2", "body": "Approach" }] }
```

---

### `two_col`
Required:
- `title`
- `col1_body`
- `col2_body`

Example:
```json
{ "layout_id": "two_col", "title": "Compare options", "col1_body": "Current state", "col2_body": "Target state" }
```

---

### `three_col_with_icons`
Required:
- `title`
- `items`

`items[]` shape:
```json
{ "title": "...", "body": "...", "icon": "assets/icon.png", "caption": "optional" }
```

Expected length: 3.

Example:
```json
{ "layout_id": "three_col_with_icons", "title": "Capabilities", "items": [{ "title": "Analyze", "body": "Find patterns", "icon": "assets/a.png" }, { "title": "Automate", "body": "Reduce manual work", "icon": "assets/b.png" }, { "title": "Govern", "body": "Control and review", "icon": "assets/c.png" }] }
```

---

### `picture_compare`
Required:
- `title`
- `left`
- `right`

`left` / `right` shape:
```json
{ "image": "assets/example.png", "title": "optional", "body": "optional" }
```

Example:
```json
{ "layout_id": "picture_compare", "title": "Before and after", "left": { "image": "assets/before.png", "title": "Before" }, "right": { "image": "assets/after.png", "title": "After" } }
```

---

## Deck shape

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

---

## Template slot conventions

Most users do not need to care about template slot names directly.

If you are editing `template.json`, the current canonical render-time slot names are:
- `item{n}_body`, `item{n}_marker` for `agenda_with_image`
- `col{n}_icon`, `col{n}_title`, `col{n}_body`, `col{n}_caption` for `three_col_with_icons`
- `left_image`, `left_title`, `left_body`, `right_image`, `right_title`, `right_body` for `picture_compare`

---

## Recommended discovery path

For callers and agents:
- `slide-smith help api`
- `slide-smith help api --format json`

Use this doc for readable examples and the CLI help command for the current compact API contract.
