# V1 Design: Agent-assisted template bootstrap from PPTX

## Status
Draft (v1).

## Summary
V1 adds a new, agent-friendly workflow that turns an existing PowerPoint file into a **usable Slide Smith template package**.

The design assumes the *real* user experience is mediated by an agent (OpenClaw / Claude Code): the human provides a local PPTX path, the agent inspects it, selectively bootstraps a template JSON, renders a dummy deck for review, and iterates.

## Problem
Slide Smith can render decks when a template package already exists (`template.pptx` + `template.json`).

But the *entry path* for humans is almost always a PPTX they already have (a theme deck or a company template). Today, creating `template.json` requires manual python-pptx spelunking.

V1 should remove that friction by letting an agent bootstrap a starter template package from an example PPTX.

## Goals (v1)

### Primary goal: bootstrap a template package from a PPTX
Given an input `.pptx` (and optional selection constraints), Slide Smith can produce a folder that contains:
- `template.pptx` (copied from the input)
- `template.json` (generated starter spec)

The generated `template.json` must:
- reference **real** slide layout names from the PPTX
- inventory placeholders with the correct **placeholder indices** (`placeholder_idx`) so rendering can target placeholders deterministically
- be inspectable and safe for an agent to edit/refine

### Secondary goal: support iterative agent loops
The CLI outputs and intermediate artifacts should support a multi-step loop:

1) inspect → 2) bootstrap → 3) validate → 4) render dummy deck → 5) human feedback → 6) refine template.json → repeat

## Non-goals (v1)
- Full-fidelity reverse engineering of arbitrary decks.
- Perfect archetype inference without human/agent judgment.
- Automatically extracting all visual styling into `styles`.

## Typical user experience (agent-mediated)

1. Human: “Use this PPTX as my template: `/path/to/company-template.pptx`.”
2. Agent runs an inspection command to learn:
   - layout names
   - placeholder indices/types per layout
3. Agent chooses a minimal set of layouts that match what Slide Smith supports (per `skills/slide-smith/SKILL.md`).
4. Agent runs bootstrap to create a new template package.
5. Agent runs `validate-template` to ensure placeholder indices exist.
6. Agent renders a dummy deck with placeholder content to show the human what it looks like.
7. Human gives feedback (“title is wrong placeholder”, “this layout isn’t the one we want”).
8. Agent refines selection and/or edits `template.json`, re-validates, and re-renders.

## Proposed CLI surface (v1)

### 1) Inspect PPTX (read-only)
A read-only inspection command is the foundation for agent reasoning.

```bash
slide-smith inspect-pptx --pptx /path/to/template.pptx
```

**Output:** deterministic JSON to stdout (plus optional `--format text`).

Suggested JSON shape:

```json
{
  "pptx": "/abs/path/to/template.pptx",
  "slide_size": {"width_emu": 12192000, "height_emu": 6858000},
  "layouts": [
    {
      "name": "Title Slide",
      "index": 0,
      "placeholders": [
        {
          "idx": 0,
          "name": "Title 1",
          "ph_type": "TITLE",
          "shape_type": "PLACEHOLDER"
        }
      ]
    }
  ]
}
```

### 2) Bootstrap template package

```bash
slide-smith bootstrap-template \
  --pptx /path/to/template.pptx \
  --template-id my_template \
  --out-dir ./templates
```

Options (v1):
- `--include-layout NAME` (repeatable) or `--include-layouts "A,B"`
- `--exclude-layout NAME` (repeatable)
- `--overwrite`
- `--print report|json|none` (defaults to `report` for humans; agents can use `json`)

**Output artifacts:**
- `<out-dir>/<template-id>/template.pptx`
- `<out-dir>/<template-id>/template.json`
- optional `<out-dir>/<template-id>/README.md` with “next steps” (nice-to-have)

### 3) Validate
Reuse existing:

```bash
slide-smith validate-template --template my_template --templates-dir ./templates
```

### 4) Render dummy deck for human review
Reuse existing `create` using a canned deck-spec fixture that exercises the supported archetypes.

The agent can generate a “dummy input deck” that includes one slide per archetype/layout chosen.

## Template JSON generation rules (v1)

### Archetype mapping strategy
Bootstrap is intentionally conservative:
- It does **not** try to rename layouts into semantic archetypes automatically.
- Each selected layout becomes an archetype with a stable generated id.

Example:
- layout: `"Title Slide"`
- archetype id: `"layout__title_slide"` (slugified)

Agents/humans may later rename archetypes to `title`, `section`, etc.

### Slot generation strategy
Every placeholder on the layout becomes a slot entry.

Each slot includes:
- `placeholder_idx` (source of truth)
- `name` (heuristic)
- `type` (heuristic)
- `required: false` (default)

Heuristics should be deterministic and based on placeholder type:
- TITLE/CENTER_TITLE → `name=title`, `type=text`
- SUBTITLE → `name=subtitle`, `type=text`
- BODY → `name=body`, `type=bullets`
- PICTURE → `name=image`, `type=image`
- Others → `type=unknown` (still included so the inventory is complete)

For duplicates, suffix: `title_2`, `body_2`, etc.

## Error handling & agent ergonomics

### Common failure modes
- PPTX contains layouts without placeholders.
- Layout names are duplicated or confusing.
- Placeholder indices referenced by the agent don’t exist (should be caught by validate).
- The chosen layouts don’t align with supported rendering archetypes.

### Design responses
- `inspect-pptx` must give the agent enough structured data to choose layouts.
- `bootstrap-template` should:
  - fail fast with clear errors if output folder exists without `--overwrite`
  - report exactly what layouts were included/excluded
  - never silently drop placeholders

## Acceptance criteria (v1)
- Given a PPTX path, an agent can run `inspect-pptx` and get structured layout/placeholder data.
- Given a PPTX path, Slide Smith can bootstrap a template folder containing `template.pptx` and `template.json`.
- `validate-template` passes on the bootstrapped template (or fails with actionable, path-qualified errors).
- Using the bootstrapped template, the agent can render a dummy deck without code changes (manual edits to `template.json` are allowed/expected).

## Out of scope for v1 (explicit)
- Extracting fonts/colors into `styles`.
- Supporting arbitrary placeholder types (charts/tables/media) in rendering.
- Automatically learning semantic archetypes from slide content.

## Follow-ups (post-v1)
- Add `slide-smith bootstrap-template --interactive` (agent-friendly prompt loop).
- Add better archetype inference for common Office layouts.
- Add a template “report.md” export that is optimized for human review.
