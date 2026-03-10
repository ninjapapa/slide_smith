# MVP Project Plan

## Purpose

This document translates the current `slide_smith` design direction into an implementation plan for the MVP.

The goal is to build a narrow, reliable, agent-first PowerPoint generation app on top of `python-pptx`, with a strong CLI and a small set of clearly supported workflows.

## MVP outcome

At MVP completion, an agent should be able to:

1. choose a known template
2. provide a markdown or JSON description of a deck
3. generate a `.pptx` presentation
4. perform a small set of predictable follow-up edits

The MVP should prioritize reliability, inspectability, and structured behavior over breadth.

## Product boundaries

### In scope
- template-driven deck creation
- markdown input
- JSON input
- structured intermediate deck spec
- known template packages (`template.pptx` + `template.json`)
- placeholder-first slide generation
- basic iterative editing operations
- CLI designed for agent use

### Out of scope
- arbitrary PowerPoint authoring
- full reverse-engineering of user-provided decks
- perfect template extraction
- sophisticated slide deletion/reordering workflows unless proven safe
- polished GUI or web app
- advanced collaborative features

## MVP principles

- **Narrow beats broad**
- **Reliable beats clever**
- **Placeholder-first beats coordinate-first**
- **Structured inputs beat ambiguous prompts**
- **A good CLI is part of the product, not an afterthought**

## Proposed MVP architecture

The MVP can be organized into these layers:

### 1. CLI layer
Responsible for:
- parsing commands
- validating arguments
- loading files
- routing to the correct workflow
- returning clear success/error output

### 2. Input normalization layer
Responsible for:
- parsing markdown
- parsing JSON
- converting both into a common deck spec

### 3. Template layer
Responsible for:
- loading template packages
- exposing template archetypes and slots
- validating that requested content fits the template contract

### 4. Rendering layer
Responsible for:
- opening `template.pptx`
- adding slides from layouts
- filling placeholders
- inserting images/tables/charts when supported
- saving output deck

### 5. Edit operations layer
Responsible for narrow updates such as:
- add slide
- update text content on a known slide
- replace image on a known slide

## Proposed repository additions

A reasonable near-term repo shape could be:

```text
slide_smith/
  docs/
    design/
  templates/
    default/
      template.pptx
      template.json
  src/
    slide_smith/
      cli.py
      deck_spec.py
      markdown_parser.py
      template_loader.py
      renderer.py
      commands/
        create.py
        inspect_template.py
        add_slide.py
        update_slide.py
  tests/
```

Exact packaging can change, but the separation of concerns is useful.

## Primary workflows

### Workflow 1: Create deck from markdown
Input:
- markdown file
- template id
- output path

Flow:
1. parse markdown into deck spec
2. load template JSON
3. map slides to template archetypes
4. render with `template.pptx`
5. save output

### Workflow 2: Create deck from JSON
Input:
- JSON deck spec
- template id
- output path

Flow:
1. validate JSON schema
2. load template JSON
3. map content to archetypes
4. render via `python-pptx`
5. save output

### Workflow 3: Inspect template
Input:
- template id or `.pptx`

Flow:
1. load template JSON
2. print supported archetypes, slots, and constraints
3. optionally show placeholder mapping details

This workflow matters because agents need a way to learn the tool.

### Workflow 4: Narrow iterative edits
Input:
- generated deck path
- operation
- target slide
- replacement content

Possible MVP edits:
- add a new supported slide after index N
- update title/body on slide N
- replace image on slide N

## Recommended CLI surface

A reasonable MVP CLI could be:

```bash
slide-smith create --input brief.md --template default --output out.pptx
slide-smith create --input brief.json --template default --output out.pptx
slide-smith inspect-template --template default
slide-smith add-slide --deck out.pptx --after 3 --type title_and_bullets --input slide.json
slide-smith update-slide --deck out.pptx --index 2 --input patch.json
```

This is intentionally small.

## Data model plan

### Deck spec
Define one internal structured deck spec that all inputs normalize into.

Likely top-level fields:
- deck title
- optional subtitle / metadata
- slide list

Each slide should have fields like:
- archetype or requested slide type
- title
- subtitle
- body
- bullets
- image refs
- table data
- chart data
- notes

### Template spec
Use the paired template model:
- `template.pptx`
- `template.json`

The template JSON should define:
- supported archetypes
- placeholder mappings
- required/optional slots
- soft constraints

## Milestones

### Milestone 1: Project skeleton
Deliverables:
- Python package scaffold
- CLI entrypoint
- docs for local setup
- initial template directory structure

Success criteria:
- `slide-smith --help` works
- repo has a clean starting structure

### Milestone 2: Deck spec and input parsing
Deliverables:
- internal deck spec definition
- JSON schema draft
- markdown-to-deck-spec parser

Success criteria:
- sample markdown and JSON can both normalize into the same internal model

### Milestone 3: Template package support
Deliverables:
- template loader
- template JSON schema
- one working default template package

Success criteria:
- tool can inspect and validate a known template

### Milestone 4: Rendering MVP
Deliverables:
- create command
- render title and bullet slides
- render at least one image-based layout
- save `.pptx`

Success criteria:
- agent can generate a non-trivial deck from markdown/JSON into PowerPoint

### Milestone 5: Basic edit operations
Deliverables:
- add-slide command
- update-slide command for text fields
- optional image replacement command

Success criteria:
- agent can iteratively refine a generated deck without recreating everything from scratch

### Milestone 6: Template inspection UX
Deliverables:
- useful `inspect-template` output
- clear slot/archetype documentation
- better error messages

Success criteria:
- an agent can discover how to use a template without reading source code

## Suggested implementation order

1. project scaffold
2. internal deck spec
3. template JSON schema
4. one hand-authored template package
5. create command for JSON input
6. markdown parser
7. template inspection command
8. add/update slide commands
9. tests and sample fixtures

That order gets to a usable end-to-end path early.

## Testing strategy

The MVP should include practical tests at three levels:

### Unit tests
- markdown parsing
- JSON validation
- template loading
- deck spec normalization

### Integration tests
- create deck from sample markdown
- create deck from sample JSON
- inspect template output

### Artifact checks
- generated `.pptx` file exists
- expected slide count is correct
- expected slide titles/body text are present

Since PowerPoint files are structured packages, some validation can be done without opening PowerPoint manually.

## Risks and mitigations

### Risk 1: template complexity grows too fast
Mitigation:
- start with one curated template
- define a small archetype set

### Risk 2: edit operations become messy
Mitigation:
- only support edits on generated/structured decks first
- avoid promising arbitrary deck surgery

### Risk 3: markdown parsing becomes underspecified
Mitigation:
- define a simple markdown convention
- keep JSON as the most explicit input mode

### Risk 4: agents misuse the CLI
Mitigation:
- make command output explicit
- return validation errors with actionable suggestions
- expose inspect-template as a first-class discovery path

## Immediate next tasks

Recommended immediate next work:

1. define the internal deck spec
2. define the template JSON schema
3. create a first hand-authored template package
4. scaffold the Python package and CLI
5. implement `inspect-template`
6. implement `create` for JSON first, markdown second

## Definition of MVP done

The MVP is done when all of the following are true:

- a user can select a known template
- an agent can inspect that template via CLI
- markdown or JSON input can be converted into a deck spec
- the system can generate a `.pptx` deck from that spec
- the output is structurally reliable for supported slide archetypes
- at least one narrow iterative edit flow works
- docs are good enough that an agent can operate the tool without source diving

## Final recommendation

The MVP should be built as a **small, disciplined, template-first CLI application**.

If we do that well, it will already be a meaningful agent-first app.
Later capabilities like template extraction, richer edits, and deeper deck understanding can grow on top of that foundation.
