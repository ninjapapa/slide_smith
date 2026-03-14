# Rich template fixtures (placeholder)

This directory is reserved for **regression fixtures** related to rich branded templates (e.g., large `.potx` sources).

Repo size note:
- Avoid committing large binary `.potx` files directly.
- Prefer one of:
  - generated *snapshot JSON* artifacts (e.g., raw layout inventory), or
  - minimal reduced decks (media stripped), or
  - Git LFS / private fixture storage referenced by a download script.

See `docs/design/rich-potx-and-hybrid-workflow.md`.
