# North Star Ambition

## Goal

The goal of `slide_smith` is to become an agent-first PowerPoint creation application built in Python.

At its core, the application should expose a command-line interface that an agent can use to reliably generate and modify presentation decks.

The primary workflow is:

1. take a markdown or JSON description of a presentation
2. apply a chosen template or layout strategy
3. generate a PowerPoint deck as output

## Agent-First Framing

This project is not just a Python wrapper around `python-pptx`.

The ambition is to create a usable application surface for agents, which means:

- a clear CLI for core operations
- predictable inputs and outputs
- documentation that teaches agents how to use the tool
- structured feedback and error messages
- simple multi-step editing flows

The app should be something an agent can call, inspect, correct, and call again.

## Core Product Direction

For the first version, the app should focus on a small number of high-value capabilities:

- **Create** a deck from a JSON presentation description
- **Apply a template** to generate a deck in a chosen style
- **Iteratively edit an existing deck** in simple ways (add/update/list/delete slides)

This keeps the MVP narrow while still supporting useful agent workflows.

## V1 Release Goal: Agent-assisted template bootstrap from an example PPTX

For v1, the key missing piece is enabling a *human* (working through an agent like OpenClaw / Claude Code) to bring their own PPTX and turn it into a usable Slide Smith template package.

### Typical user experience (agent-mediated)

1. **User shares a local path to a PPTX** they want to use as a template seed.
2. **Agent inspects the PPTX** (layouts/placeholders) using Slide Smith tooling.
3. **Agent selectively bootstraps a template package**:
   - the PPTX may contain far more layouts than needed
   - the agent uses knowledge of what Slide Smith supports (canonical `skills/slide-smith/SKILL.md`) to choose a minimal supported subset
4. **Agent iterates with Slide Smith over multiple steps** to resolve issues (naming, missing placeholders, unsupported constructs). The point is to let the LLM handle decision-making while Slide Smith stays deterministic.
5. **Agent produces a dummy rendered deck** using the bootstrapped template (with placeholder content) so the human can visually review the result.
6. **Human gives feedback**, and the agent refines the template JSON / selection and re-renders until it’s “good enough”.

### Definition of “bootstrap a template package” (v1)

Given an example PPTX and an agent’s selection of what to include, Slide Smith can:
- Create a new template folder containing `template.pptx`.
- Generate a starter `template.json` that inventories selected slide layouts and placeholders (including placeholder indices) so rendering can target the right placeholders deterministically.
- Produce inspectable output so an agent can guide the user through mapping layouts → archetypes (manual refinement is expected).

### Non-goals for v1 bootstrap

- Fully automatic, high-fidelity reverse-engineering of arbitrary decks.
- Perfect archetype detection without human/agent review.
- Eliminating the need for iterative “render → review → tweak” loops.

## Template Ambition

A major part of the product design is template handling.

The application should eventually be able to accept example decks from users and derive a reusable template representation from them.

That raises an important design question:

### How should templates be stored?

Possible approaches:

1. **Raw example deck as the template source**
   - Keep the original PowerPoint file as the main template artifact
   - Infer layout behavior from the example deck at runtime or through preprocessing

2. **Descriptive template representation**
   - Convert the example deck into a descriptive intermediate format
   - Capture layout intent, slide types, style rules, and placeholders in a human-readable structure

3. **Structured template data model**
   - Store templates as structured data such as JSON/YAML
   - Represent slide archetypes, placeholders, formatting rules, and deck-level styles explicitly

The MVP does not need to fully solve template extraction, but the design should leave room for this.

## Proposed MVP Scope

### Inputs
- JSON presentation description
- Optional: Markdown presentation description (nice-to-have; not required for v1)
- Optional template selection
- Optional: example PPTX path (for template bootstrap)

### Outputs
- PowerPoint deck (`.pptx`)

### Basic operations
- Create deck
- Add slide
- Delete slide
- Regenerate part of a deck

### Non-goals for MVP
- Full fidelity reverse-engineering of arbitrary decks
- Comprehensive visual editing
- Highly advanced layout optimization
- Rich collaborative workflows

## Suggested Early CLI Shape

A simple CLI could look something like:

```bash
# Render
slide-smith create --input brief.json --template default --output out.pptx

# Iterative edits
slide-smith add-slide --deck out.pptx --after 3 --type title_and_bullets --input slide.json
slide-smith update-slide --deck out.pptx --index 1 --input patch.json
slide-smith delete-slide --deck out.pptx --index 4

# Template operations
slide-smith inspect-template --template default
slide-smith validate-template --template default

# V1 goal: bootstrap a template package from an example PPTX
slide-smith bootstrap-template --pptx /path/to/example.pptx --template-id my_template --out-dir ./templates
```

This is only directional, but it captures the type of interface agents should be able to use.

## Design Principles

- **Keep the MVP narrow**
- **Make the CLI reliable before making it broad**
- **Prefer simple, inspectable data formats**
- **Support iterative deck editing, not just one-shot generation**
- **Design with future template learning in mind**

## Working Thesis

`slide_smith` should start as a simple agent-operable PowerPoint generator and editor, then grow into a broader agent-first presentation application that can learn from example decks, apply reusable template logic, and support iterative creation and refinement workflows.
