# Issue 001: Scaffold the Python package and CLI

## Summary
Create the initial Python project structure for `slide_smith`, including a CLI entrypoint and a minimal command surface that establishes the app as an agent-first tool.

## Why
The MVP plan depends on a disciplined CLI-first architecture. Before building rendering or template logic, the repo needs a clean package layout and a command entrypoint agents can discover and call.

## Scope

### In scope
- create `src/slide_smith/` package structure
- add CLI entrypoint module
- add placeholder command wiring
- add minimal packaging metadata
- make `slide-smith --help` work
- document basic local setup

### Out of scope
- actual deck rendering
- template parsing
- markdown parsing
- edit operations

## Deliverables
- Python package scaffold under `src/slide_smith/`
- CLI entrypoint, likely `cli.py`
- minimal command structure for future subcommands
- basic project metadata/config
- short setup/run notes

## Suggested structure

```text
src/
  slide_smith/
    __init__.py
    cli.py
    commands/
      __init__.py
```

## Acceptance criteria
- repository has a clean Python package layout
- CLI can be invoked locally
- `slide-smith --help` or equivalent works
- command structure is ready for `create` and `inspect-template`
- setup instructions are written down

## Notes
Keep this intentionally small. The goal is to establish the shape of the project without locking in too much implementation detail too early.
