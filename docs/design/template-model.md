# Template Storage and Representation Model

## Decision

`slide_smith` should use a **dual-artifact template model**:

1. **canonical render artifact:** a cleaned-up `.pptx` template
2. **agent-operable semantic artifact:** a derived `JSON` template specification

This design keeps real PowerPoint fidelity while also giving agents a clean, inspectable interface for reasoning and generation.

## Why this is the right approach

If we store templates only as `.pptx` files:
- rendering fidelity is strong
- PowerPoint-native layouts and placeholders are preserved
- `python-pptx` integration is straightforward
- but the template is harder for agents to inspect, reason about, diff, and modify safely

If we store templates only as JSON:
- agents get a clearer semantic representation
- diffs and edits are easier
- but we risk rebuilding too much of PowerPoint semantics ourselves
- and we lose the natural rendering source that `python-pptx` already knows how to work with

The dual-artifact model avoids both extremes.

## Core principle

- **`.pptx` is the source of rendering truth**
- **JSON is the source of agent interaction truth**

The JSON should not try to represent every last PowerPoint detail.
It should represent the parts of the template that matter for agent planning and content mapping.

## Template lifecycle

A template should move through these stages:

### 1. Input example deck
The user provides an example PowerPoint deck.

### 2. Template cleanup / normalization
A cleaned-up `.pptx` is produced as the template artifact.

This may involve:
- removing noisy content
- standardizing slide layouts
- clarifying placeholder usage
- ensuring repeated slide patterns are consistent
- naming or tagging key slide archetypes if needed

### 3. Extraction and interpretation
A parser and/or multimodal model analyzes the cleaned-up deck and produces a semantic representation.

### 4. JSON template spec generation
The system emits a normalized JSON template description.

### 5. Runtime generation
At generation time:
- the agent reads the JSON template spec
- picks slide archetypes and fills slots
- the renderer uses the `.pptx` template to create the actual deck

## What belongs in the `.pptx`

The `.pptx` template should preserve:
- master/theme behavior
- slide layouts
- placeholder positions and types
- text styling defaults
- visual structure
- background and theme colors
- presentation-native formatting behavior

This is the artifact used directly by `python-pptx`.

## What belongs in the JSON spec

The JSON template spec should contain the **semantic contract** of the template.

Recommended contents:

### Template metadata
- template id
- name
- version
- source deck reference
- extraction timestamp
- extraction confidence or notes

### Deck-level metadata
- slide size / aspect ratio
- theme summary
- default style hints
- supported slide archetypes

### Slide archetypes
Each archetype should represent a reusable slide pattern, such as:
- `title`
- `section`
- `title_and_bullets`
- `image_left_text_right`
- `chart_summary`
- `table_summary`

For each archetype, capture:
- archetype id
- human-readable description
- backing slide layout name or identifier
- intended use
- constraints and content expectations

### Slots / placeholders
For each archetype, represent semantic slots such as:
- `title`
- `subtitle`
- `body`
- `bullets`
- `image`
- `table`
- `chart`
- `footer`

For each slot, include:
- slot name
- content type
- required vs optional
- placeholder mapping if known
- text length guidance
- bullet count guidance
- image aspect ratio guidance
- notes for the agent

### Style hints
Do not try to fully recreate PowerPoint styling in JSON.
Instead, store high-value semantic hints like:
- alignment preference
- density (`sparse`, `standard`, `dense`)
- title emphasis
- image prominence
- chart-first vs text-first layout intent

### Examples
Optionally include examples derived from the source deck:
- example title
- example body structure
- example slide intent

These examples can help agents choose the right archetype.

## Proposed file layout

A template package could look like this:

```text
templates/
  consulting-classic/
    template.pptx
    template.json
    previews/
      01-title.png
      02-section.png
    extraction/
      source-deck.pptx
      extraction-notes.md
```

For MVP, only these are required:

```text
templates/
  consulting-classic/
    template.pptx
    template.json
```

## Example JSON shape

This is directional, not final:

```json
{
  "template_id": "consulting-classic",
  "name": "Consulting Classic",
  "version": "0.1",
  "deck": {
    "aspect_ratio": "16:9",
    "supported_archetypes": [
      "title",
      "section",
      "title_and_bullets",
      "image_left_text_right"
    ]
  },
  "archetypes": [
    {
      "id": "title_and_bullets",
      "layout": "Title and Content",
      "description": "A title with a body area suited for bullets.",
      "slots": [
        {
          "name": "title",
          "type": "text",
          "required": true,
          "placeholder_idx": 0
        },
        {
          "name": "bullets",
          "type": "bullet_list",
          "required": true,
          "placeholder_idx": 1,
          "max_items": 6,
          "notes": "Prefer short bullets. Avoid long paragraphs."
        }
      ]
    }
  ]
}
```

## Role of image understanding models

A multimodal model can help with template interpretation, but it should not be the only source of truth.

It is useful for:
- recognizing slide intent
- grouping similar slide types
- summarizing visual hierarchy
- identifying likely title/body/image regions
- generating descriptive notes for archetypes

But it should be paired with structural extraction from the `.pptx` itself when possible.

Best practice:
- use PowerPoint structure when available
- use multimodal interpretation to fill semantic gaps
- store the result in normalized JSON

## Recommended extraction strategy

### Structural extraction layer
Use code to inspect:
- slide layouts
- placeholders
- shape types
- text presence
- image/table/chart presence
- repeated slide patterns

### Semantic interpretation layer
Use an image understanding model and/or LLM to infer:
- likely slide archetype labels
- what each slide is “for”
- visual hierarchy
- content-density guidance
- reusable design patterns

### Normalization layer
Convert the extracted structure and model interpretation into a stable JSON schema.

## Design constraints

### Constraint 1: JSON should stay semantic, not geometric-first
Avoid building a raw “shape dump” JSON as the main interface.

A giant export of every box, coordinate, and style attribute will be hard for agents to use well.

Geometry may still be retained internally, but the primary JSON should be semantic.

### Constraint 2: `.pptx` should remain renderable without JSON regeneration
The `.pptx` must stand on its own as a usable rendering template.

### Constraint 3: Generated decks should preserve editability
Where possible, decks generated from templates should follow stable conventions so later agent edits remain predictable.

## MVP recommendation

For MVP:

### In scope
- manually curated `template.pptx`
- manually authored or semi-automatically generated `template.json`
- a small number of slide archetypes
- placeholder-based content mapping

### Out of scope
- fully automatic template extraction from arbitrary decks
- perfect reverse-engineering of design semantics
- arbitrary shape-level reconstruction as the main interface

This keeps the system realistic.

## Recommended product path

### Phase 1
Hand-curated templates with paired JSON specs.

### Phase 2
Template inspection tools that generate draft JSON from a `.pptx`.

### Phase 3
Multimodal template interpretation from example decks.

### Phase 4
Semi-automatic template authoring workflow with human review.

## Final recommendation

The template system for `slide_smith` should be built around a **paired template package**:

- a cleaned-up `.pptx` for rendering fidelity
- a semantic JSON spec for agent reasoning and control

That gives us the right split between PowerPoint-native execution and agent-native usability.
