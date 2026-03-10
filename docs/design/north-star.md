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

- **Create from scratch** from markdown or JSON presentation descriptions
- **Apply a template** to generate a deck in a chosen style
- **Modify an existing deck** in simple ways
- **Add pages** and **delete pages** as part of iterative editing

This keeps the MVP simple while still supporting useful agent workflows.

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
- Markdown presentation description
- JSON presentation description
- Optional template selection

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
slide-smith create --input brief.md --template default --output out.pptx
slide-smith create --input brief.json --template default --output out.pptx
slide-smith add-slide --deck out.pptx --after 3 --input slide.md
slide-smith delete-slide --deck out.pptx --index 4
slide-smith inspect-template --deck example.pptx
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
