# Archetypes v2 — compact core + template-native variants

Status: **DRAFT**

## Context
Issue #77 proposes redefining Slide Smith’s *global* archetype vocabulary into a compact, portable set (≤10) while explicitly separating it from richer **template-native** archetypes/layouts.

Today we have:
- **Core (v1.0)**: `title`, `section`, `title_and_bullets`, `image_left_text_right`
- **Extended (v1.1)**: `two_col`, `three_col`, `four_col`, `pillars_3`, `pillars_4`, `table`, `table_plus_description`, `timeline_horizontal`

The v1.1 set works, but is starting to encode template/layout implementation details as distinct archetype IDs.

This doc proposes a v2 model that:
1) keeps the global vocabulary small and semantically meaningful
2) uses **parameterized families** rather than proliferating IDs
3) allows templates to expose richer patterns as **template-native** archetypes without bloating the core


## Goals
- **Portability**: the core archetype IDs should make sense across many templates.
- **Predictability**: callers (human or agent) can pick an archetype without needing template-specific knowledge.
- **Stability**: adding templates should not require expanding the global core list.
- **Extensibility**: templates can still expose richer page types as *template-native*.
- **Migration**: provide a clear compatibility plan from v1.0/v1.1.

## Non-goals
- Designing a full semantic planner/LLM policy.
- Perfectly modeling every layout in a rich template as a core archetype.


## Proposed compact **core** archetype set (≤10)
These are the portable, globally supported structures.

### 1. `title`
**Purpose**: cover/opening slide.

Slots (suggested):
- `title` (text, required)
- `subtitle` (text, optional)
- `kicker` (text, optional)

### 2. `section`
**Purpose**: section divider.

Slots:
- `title` (text, required)
- `subtitle` (text, optional)
- `body` (text, optional)

### 3. `message`
**Purpose**: key message / headline + supporting text / quote.

Slots:
- `title` (text, required)
- `body` (text, optional)
- `quote` (text, optional)
- `attribution` (text, optional)

Notes:
- `message` is intentionally flexible; templates can map it to “key message”, “quote”, “callout” variants.

### 4. `title_and_bullets`
**Purpose**: canonical explanatory content slide.

Slots:
- `title` (text, required)
- `bullets` (bullet_list, required)
- `subtitle` (text, optional)

### 5. `two_col`
**Purpose**: comparison / parallel content.

Slots:
- `title` (text, required)
- `col1_body` (text, required)
- `col2_body` (text, required)
- `col1_title` (text, optional)
- `col2_title` (text, optional)

### 6. `multi_col`
**Purpose**: repeated buckets/pillars/frameworks (3–4 typical).

Slots:
- `title` (text, required)
- `items` (list, required) where each item may include:
  - `heading` (text, optional)
  - `body` (text, required)
  - `icon` (image, optional)
  - `label` / `number` (text, optional)

Parameters:
- `columns` (int, optional; default derived from `len(items)`)

Rationale:
- collapses `three_col`, `four_col`, `pillars_3`, `pillars_4` into one family.

### 7. `image_text`
**Purpose**: mixed visual + explanatory.

Slots:
- `title` (text, required)
- `body` (text, required)
- `image` (image, required)
- `subtitle` (text, optional)

Parameters:
- `image_side` (`left`|`right`, optional)

Rationale:
- replaces `image_left_text_right` with a bidirectional family.

### 8. `list_visual`
**Purpose**: agenda/steps/list-driven pages (optionally with a visual).

Slots:
- `title` (text, required)
- `items` (list, required) with item fields:
  - `label` (text/number, optional)
  - `body` (text, required)
  - `icon` (image, optional)
- `image` (image, optional)

### 9. `table`
**Purpose**: tabular/matrix content.

Slots:
- `title` (text, required)
- `table` (table, required)
- `body` (text, optional)  

Notes:
- v1.1 rendered `table_text` as plain text. v2 should allow a structured table type, but may keep the text rendering path as MVP.

### 10. `metrics`
**Purpose**: KPIs/stats.

Slots:
- `title` (text, required)
- `metrics` (list, required) where each item may include:
  - `value` (text, required)
  - `label` (text, required)
  - `detail` (text, optional)
  - `icon` (image, optional)
- `subtitle` (text, optional)


## What moves out of core (v1.1 → v2)
- `three_col` → `multi_col` (columns=3)
- `four_col` → `multi_col` (columns=4)
- `pillars_3` → `multi_col` (columns=3)
- `pillars_4` → `multi_col` (columns=4)
- `image_left_text_right` → `image_text` (image_side=left)
- `table_plus_description` → `table` (with `body`)
- `timeline_horizontal` → **template-native** for now (or later reintroduced as a separate “process/timeline” family if it proves portable)


## Template-native archetypes (new concept)
Templates should be able to advertise a richer set of page types that are **native to that template**.

Key properties:
- IDs are namespaced (recommended): e.g. `acn_graphik:quote_gradient`, `acn_graphik:agenda_image`.
- Template-native archetypes can map to core archetypes as fallbacks.
- Callers can request template-native archetypes explicitly when they know they want them.

### Proposed template metadata structure (conceptual)
In `template.json`:

```json
{
  "core": {
    "supported_archetypes": ["title","section","message","title_and_bullets","two_col","multi_col","image_text","list_visual","table","metrics"]
  },
  "native": {
    "archetypes": [
      {
        "id": "acn_graphik:quote_gradient",
        "description": "Quote slide w/ gradient bg",
        "maps_from_core": ["message"],
        "slots": {
          "quote": {"placeholder_idx": 12},
          "attribution": {"placeholder_idx": 13}
        }
      }
    ]
  }
}
```

(Exact schema TBD; this is to communicate the separation.)


## Deck spec impact (schema changes)
We likely need a v2 deck-spec evolution that supports:
- `archetype`: string ID (core or template-native)
- optional `params`: object (e.g. `image_side`, `columns`)
- typed slot structures for list/table/metrics

Example (conceptual):

```json
{
  "slides": [
    {
      "archetype": "multi_col",
      "params": {"columns": 4},
      "slots": {
        "title": "Operating model pillars",
        "items": [
          {"heading": "People", "body": "..."},
          {"heading": "Process", "body": "..."},
          {"heading": "Tech", "body": "..."},
          {"heading": "Governance", "body": "..."}
        ]
      }
    }
  ]
}
```

Open question: do we keep `colN_body` style slots for compatibility, or standardize on `items[]` for `multi_col`?

Recommendation:
- **Core v2 canonical form** uses `items[]`.
- Provide **input normalization** that can lift legacy `col1_body` / `pillar1_body` into `items[]`.


## Renderer impact
- Introduce renderers for new families: `message`, `multi_col`, `image_text`, `list_visual`, `metrics`.
- For `table`: keep MVP text rendering path first, then progressively move to structured table layout rendering.
- Template mapping needs to map:
  - list-like structures (`items[]`) to placeholder indices, or
  - a single placeholder for “body blob” if template lacks per-item placeholders (fallback rendering).


## Migration / compatibility
We should treat this as a versioned change with explicit compatibility:

1) **Aliases** (input): accept v1 archetype IDs and normalize to v2 families:
   - `three_col` → `multi_col` (items=3)
   - `pillars_4` → `multi_col` (items=4)
   - `image_left_text_right` → `image_text` (image_side=left)

2) **Template mapping profiles**:
   - `standard` / `extended` profiles may become:
     - `core_v1` (legacy)
     - `core_v2` (new)
     - `native` (template-native definitions)

3) **Validation**:
   - validate v2 slot types (lists/tables/metrics) early, before rendering.

4) **Documentation**:
   - keep `docs/design/archetypes.md` as v1 reference
   - link to this doc as v2 direction


## Open questions
- Should `timeline` re-enter core later as `process` family (with items and milestones), or remain template-native longer?
- Do we want exactly 10 core archetypes, or allow 8–10 and treat some as optional extensions?
- How do we represent `items[]` mapping to placeholders in a robust, deterministic way across templates?


## Suggested implementation sequence (work breakdown)
1) **Schema + normalization**: add v2 canonical slot structures + legacy normalization.
2) **Core registry refactor**: update archetype definitions, alias table.
3) **Template schema extension**: add `native.archetypes[]` and a namespacing convention.
4) **Renderer updates**: implement `multi_col`/`image_text`/`message` etc. using canonical slots.
5) **Validation updates**: `validate-template` and `validate-deck` profiles for v2.
6) **Docs**: update README / deck-spec docs; keep v1 docs intact.
