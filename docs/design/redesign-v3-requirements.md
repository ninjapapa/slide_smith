# Slide-Smith Design Requirements

## Executive Summary

`slide-smith` should be simplified into a focused **PowerPoint deck renderer with limited structural slide operations**. It should accept a **small deck spec**, render slides using a constrained set of supported **layout IDs**, allow **insert/delete/update slide** operations, and always **fall back to `title_and_bullets`** when a requested layout cannot be rendered. Advanced inspection, exemplar workflows, and template-authoring/tooling should be removed from scope.

---

## 1. Purpose

`slide-smith` exists to do one job well:

- render a PowerPoint deck from a compact structured spec
- support narrow structural slide operations on an existing deck
- validate whether a requested layout can be rendered against a template

It should **not** be a story planner, design ideation system, template exploration tool, or exemplar-driven deck synthesis system.

---

## 2. Product Positioning

### 2.1 Core Role
`slide-smith` is a **deterministic PPTX renderer/editor**.

### 2.2 Responsibility Split
- **Caller agent / user workflow**
  - decides the story
  - chooses slide sequence
  - selects the intended layout ID
  - prepares the small deck spec

- **slide-smith**
  - validates requested layout IDs against the template
  - maps content into placeholders
  - renders valid PPTX output
  - supports insert/delete/update slide operations
  - applies fallback when a layout is unsupported or invalid

---

## 3. Explicit Non-Goals

The following are out of scope:

- exemplar workflow
- reference-first workflow
- inspect commands
- list commands
- tier-3 / advanced developer tooling
- template bootstrapping
- template mapping as a user-facing workflow
- story planning inside the tool
- semantic “archetype” language in the product surface

Use the term **layout ID** consistently instead of **archetype**.

---

## 4. Supported Layout IDs

The supported layout IDs are:

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

These should define the complete intended rendering vocabulary for v1 of the simplified system.

---

## 5. Fallback Behavior

### 5.1 Required Fallback
If a requested layout ID cannot be rendered for any reason, `slide-smith` must always fall back to:

- `title_and_bullets`

### 5.2 When Fallback Applies
Fallback should occur when:
- the layout ID is unsupported
- the layout is missing from the template
- required placeholders are unavailable
- content does not fit the target layout contract
- the mapping fails validation

### 5.3 Fallback Requirements
When fallback happens:
- rendering must still succeed
- output deck must remain valid and open cleanly in PowerPoint
- the tool should emit a clear warning identifying:
  - requested layout ID
  - fallback layout used
  - reason for fallback

---

## 6. Required Operations

### 6.1 Create Deck
Render a new PPTX from a compact deck spec.

### 6.2 Insert Slide
Insert a new slide at a specified position using one of the supported layout IDs, with fallback if necessary.

### 6.3 Delete Slide
Delete a slide by index.

### 6.4 Update Slide
Update a slide’s content and/or layout ID at a specified index, with fallback if necessary.

---

## 7. Removed Operations

The following commands/capabilities should not be part of the simplified design:

- inspect template/deck
- list slides
- analyze
- plan
- compile-exemplar
- render-exemplar
- validate-exemplar
- bootstrap-template
- advanced tier-3 workflows

Only **validate** should remain from the template-support class of operations.

---

## 8. Validation Requirements

### 8.1 Validation Scope
Validation should answer a practical question:

**Can this template render this deck spec using these layout IDs?**

### 8.2 Validation Responsibilities
Validation should check:
- requested layout IDs exist or are recognized
- required placeholders exist
- content shape matches layout requirements
- fallback conditions are identified ahead of render when possible

### 8.3 Validation Output
Validation should be concise and actionable:
- valid / warning / fallback / error
- slide-by-slide results
- explicit fallback recommendations where applicable

Validation should not become a deep exploratory inspection tool.

---

## 9. Deck Spec Requirements

### 9.1 Design Goals
The deck spec should be:
- small
- easy for an LLM to produce
- easy for a human to read
- directly tied to supported layout IDs
- free of unnecessary design abstraction

### 9.2 Required Structure
At minimum:
- deck-level metadata
- ordered slide list
- per-slide `layout_id`
- only the fields required for each layout type

### 9.3 Recommended Shape
Example:

```json
{
  "title": "Deck Title",
  "slides": [
    {
      "layout_id": "title",
      "title": "Deck Title",
      "subtitle": "Optional subtitle"
    },
    {
      "layout_id": "section",
      "title": "Why this matters"
    },
    {
      "layout_id": "title_and_bullets",
      "title": "Key points",
      "bullets": [
        "Point one",
        "Point two",
        "Point three"
      ]
    }
  ]
}
```

### 9.4 Layout-Specific Fields
Each layout ID should have a minimal content contract.

Examples:

- `title`
  - `title`
  - `subtitle` optional

- `section`
  - `title`

- `title_and_bullets`
  - `title`
  - `bullets`

- `title_subtitle_and_bullets`
  - `title`
  - `subtitle`
  - `bullets`

- `text_with_image`
  - `title`
  - `body` or `bullets`
  - `image`

- `two_col`
  - `title`
  - `left`
  - `right`

- `three_col_with_icons`
  - `title`
  - `columns`

- `picture_compare`
  - `title`
  - `left_image`
  - `right_image`
  - optional captions

This should remain minimal and practical, not deeply expressive.

---

## 10. Layout ID Model

### 10.1 Terminology
Use **layout ID** everywhere in:
- commands
- schemas
- logs
- docs
- validation output

Avoid using **archetype** in the external interface.

### 10.2 Mapping Principle
A layout ID should correspond to a known renderable template pattern.

The system should not require users to think in both:
- abstract semantic types
- template-native identifiers

Instead, the chosen layout ID should be the operational unit.

---

## 11. Reliability Requirements

The simplified system should prioritize:

- valid PowerPoint output
- deterministic behavior
- consistent placeholder mapping
- predictable fallback
- low cognitive load for callers

A “boring but reliable” render path is preferable to rich but fragile layout support.

---

## 12. CLI/Product Surface

The simplified command surface should roughly center on:

- `create`
- `validate`
- `insert-slide`
- `delete-slide`
- `update-slide`

Nothing else should be necessary for the primary user journey.

---

## 13. Error Handling Requirements

Errors should be structured and concise.

Every failure or warning should identify:
- slide index
- requested layout ID
- issue detected
- fallback action, if any

Hard failure should be reserved for cases where:
- the deck cannot be produced at all
- the template cannot be loaded
- the output cannot be written
- update/insert/delete targets are invalid

Whenever possible, layout/content mismatch should degrade via fallback rather than fail the entire render.

---

## 14. Success Criteria

The redesign is successful if:

1. a caller can generate a deck using only the reduced deck spec
2. the caller only needs to think in supported layout IDs
3. the output opens reliably in PowerPoint
4. unsupported layouts degrade automatically to `title_and_bullets`
5. slide operations are limited to create / insert / delete / update
6. the system surface is materially smaller and easier to explain
