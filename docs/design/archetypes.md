# Archetypes

This document defines Slide Smith archetypes and their slot conventions.

## Core standard archetypes (v1.0)

These are the stable baseline archetypes.

### `title`
Slots:
- `title` (text, required)
- `subtitle` (text, optional)

### `section`
Slots:
- `title` (text, required)
- `subtitle` (text, optional)
- `body` (text, optional)

### `title_and_bullets`
Slots:
- `title` (text, required)
- `bullets` (bullet_list, required)

### `image_left_text_right`
Slots:
- `title` (text, required)
- `image` (image, required)
- `body` (text, required)

---

## Extended archetypes (v1.1)

v1.1 adds an **extended archetype library** focused on:

- columns / buckets / pillars
- tables (MVP text rendering)
- horizontal timeline

### Common conventions

- All archetypes may include `notes` (string) at slide level.
- Slot mappings are resolved via template spec: `template.json` → `archetypes[].slots[].placeholder_idx`.
- Slot names that repeat use numeric suffixes: `col1_body`, `col2_body`, ...

### Columns

#### `two_col`
Slots:
- `title` (text, required)
- `col1_body` (text, required)
- `col2_body` (text, required)

#### `three_col`
Slots:
- `title` (text, required)
- `col1_body` (text, required)
- `col2_body` (text, required)
- `col3_body` (text, required)

#### `four_col`
Slots:
- `title` (text, required)
- `col1_body` (text, required)
- `col2_body` (text, required)
- `col3_body` (text, required)
- `col4_body` (text, required)

### Pillars

#### `pillars_3`
Slots:
- `title` (text, required)
- `pillar1_body` (text, required)
- `pillar2_body` (text, required)
- `pillar3_body` (text, required)

#### `pillars_4`
Slots:
- `title` (text, required)
- `pillar1_body` (text, required)
- `pillar2_body` (text, required)
- `pillar3_body` (text, required)
- `pillar4_body` (text, required)

### Tables (MVP)

v1.1 MVP renders tables as **text** into a placeholder mapped by `table_text`.

#### `table`
Slots:
- `title` (text, required)
- `table_text` (text, required)

#### `table_plus_description`
Slots:
- `title` (text, required)
- `table_text` (text, required)
- `body` (text, required)

### Timeline

#### `timeline_horizontal`
Slots:
- `title` (text, required)
- `milestone1_body` (text, required)
- `milestone2_body` (text, optional)
- ... up to `milestone10_body` (optional; renderer fills best-effort)

---

## Validation

- `slide-smith validate-template --profile standard` validates core standard archetypes.
- `slide-smith validate-template --profile extended` validates both core + extended archetypes.

## Mapping

- `slide-smith map-template` generates best-effort mappings for core + extended archetypes.
- If mapping is ambiguous, callers can:
  - run `slide-smith export-previews` to get a manifest for vision/classification
  - provide `--hints hints.json`
