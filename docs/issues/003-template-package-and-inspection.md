# Issue 003: Design the template package format and implement template inspection

## Summary
Define the MVP template package format (`template.pptx` + `template.json`) and implement the first inspection path so agents can discover supported slide archetypes, slots, and constraints.

## Why
Templates are central to the product. The MVP should not just load templates internally; it should expose them as an inspectable interface that agents can learn and use.

## Scope

### In scope
- define template package directory layout
- define the first `template.json` shape for MVP
- document supported archetypes and slots
- implement or plan `inspect-template`
- create one hand-authored default template package

### Out of scope
- automatic template extraction
- multimodal interpretation pipeline
- arbitrary template reverse-engineering

## Deliverables
- template package design doc or schema notes
- one default template package layout
- initial `template.json`
- initial `inspect-template` command behavior/spec
- example inspection output

## Core design questions
- what belongs in `template.json` for MVP?
- how should archetypes map to PowerPoint layouts/placeholders?
- what slot metadata helps agents most?
- how much style information is worth encoding now?
- what should inspection output look like in the CLI?

## Acceptance criteria
- template package layout is defined and documented
- one default template package exists
- supported archetypes and slots are explicit
- `inspect-template` behavior is defined clearly enough to implement
- the template model is narrow, semantic, and agent-usable

## Notes
The key here is not to dump every shape detail. The template interface should stay semantic and useful, with `.pptx` as render truth and JSON as agent-operable truth.
