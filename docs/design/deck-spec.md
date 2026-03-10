# Deck Spec Draft

## Purpose

The deck spec is the internal normalized data model for `slide_smith`.

All supported input formats — especially JSON and markdown — should normalize into this structure before template mapping and rendering.

## Design goals

- simple enough for agents to author directly
- explicit enough to validate reliably
- narrow enough to render consistently in MVP
- expressive enough for title, bullets, body text, and images

## Proposed top-level shape

```json
{
  "title": "Q2 Business Review",
  "subtitle": "Draft for leadership review",
  "slides": [
    {
      "archetype": "title_and_bullets",
      "title": "Highlights",
      "bullets": [
        "Revenue up 20%",
        "Margin improved",
        "Pipeline remains strong"
      ]
    }
  ]
}
```

## Top-level fields

### `title`
- type: string
- optional for MVP, but recommended
- deck-level label for the presentation

### `subtitle`
- type: string
- optional

### `slides`
- type: array
- required
- ordered list of slide specifications

## Slide fields

Each slide should support a narrow, explicit shape.

### Required field
- `archetype`: string

### Optional fields
- `title`: string
- `subtitle`: string
- `body`: string
- `bullets`: string[]
- `image`: string
- `notes`: string

## MVP-supported archetypes

Initial archetypes should stay small, for example:
- `title`
- `section`
- `title_and_bullets`
- `image_left_text_right`

## Normalization rules

### JSON input
JSON should already resemble the target structure and mainly need validation.

### Markdown input
Markdown should normalize into the same deck spec.

A simple convention could be:
- `#` for deck title
- `##` for new slide title
- bullet lists become `bullets`
- paragraphs become `body`
- optional slide metadata can be added later

## MVP guidance

For MVP, prefer explicit, narrow slides rather than a rich universal model. The point is to make rendering reliable and template mapping straightforward.
