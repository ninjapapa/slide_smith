# Issue 002: Define the internal deck spec and input normalization

## Summary
Define the internal deck specification that becomes the canonical intermediate format for `slide_smith`, and describe how JSON and markdown inputs normalize into it.

## Why
The project needs one stable internal contract between user input and rendering. Without a clear deck spec, the CLI, template model, markdown parser, and renderer will all drift.

## Scope

### In scope
- define deck spec fields
- draft JSON schema direction
- define slide archetype payload shape
- describe markdown-to-deck-spec normalization
- clarify what belongs in v1 vs later

### Out of scope
- full markdown parser implementation
- renderer implementation
- advanced chart/table schema design beyond MVP needs

## Deliverables
- design doc for deck spec
- initial JSON schema draft or schema notes
- examples of valid JSON input
- examples of equivalent normalized structure from markdown

## Core design questions
- what are the top-level deck fields?
- how should slides declare archetype/type?
- how should title/body/bullets/images be represented?
- what should be required vs optional?
- what fields are too ambitious for MVP?

## Acceptance criteria
- there is a clearly documented internal deck spec
- JSON input can be validated against a draft schema
- markdown normalization target is defined
- examples show how multiple inputs converge into one model
- the spec is narrow enough to support reliable rendering

## Notes
Bias toward a simple, agent-friendly structure. JSON should be explicit and inspectable. Markdown should normalize into that same shape rather than becoming a parallel data model.
