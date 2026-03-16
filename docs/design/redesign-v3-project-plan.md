# Slide Smith v3 Project Plan

This plan turns `docs/design/redesign-v3-requirements.md` into an implementation roadmap.

## Objective

Deliver a simplified `slide-smith` that is:
- a deterministic PPTX renderer/editor
- centered on a small set of supported `layout_id` values
- reliable about fallback to `title_and_bullets`
- materially smaller in code surface, CLI surface, and docs surface

## Product outcome for v3

At the end of v3, the primary user journey should be:

- prepare a compact deck spec with `layout_id`
- run `create`
- optionally run `validate`
- optionally `insert-slide`, `update-slide`, or `delete-slide`

Everything else should either be removed or clearly internal-only.

---

# 1. Scope summary

## In scope
- compact deck spec with `layout_id`
- create deck
- validate deck against a template
- insert slide
- update slide
- delete slide
- deterministic fallback to `title_and_bullets`
- concise slide-by-slide warnings/errors
- rename external terminology from `archetype` to `layout_id`

## Out of scope / to remove
- inspect commands
- analyze / plan / exemplar flows
- bootstrap and template-authoring workflows
- map-template as a user-facing workflow
- list-slides
- advanced developer/tier-3 commands
- semantic archetype language in the product surface

---

# 2. v3 target model

## Supported layout IDs

The supported v3 layout IDs are:
- `title`
- `section`
- `title_and_bullets`
- `title_subtitle_and_bullets`
- `text_with_image`
- `version_page`
- `agenda_with_image`
- `two_col`
- `three_col_with_icons`
- `picture_compare`

## Fallback contract

Fallback target:
- `title_and_bullets`

Fallback triggers:
- unknown/unsupported `layout_id`
- missing template layout mapping
- missing required placeholders
- invalid content shape for requested layout
- validation failure for requested layout

Fallback output requirements:
- deck still renders successfully
- warning is emitted with slide index, requested layout, fallback layout, and reason

---

# 3. Workstreams

## Workstream A — Product surface simplification

### Goal
Reduce the CLI and docs to the minimal supported product.

### Tasks
1. Remove or hide obsolete CLI commands:
   - `inspect-template`
   - `inspect-pptx`
   - `inspect-slide`
   - `list-slides`
   - `analyze`
   - `plan`
   - `compile-exemplar`
   - `render-exemplar`
   - `validate-exemplar`
   - `bootstrap-template`
   - `bootstrap-from-slide`
   - `map-template`
   - `export-previews`
   - `dummy-deck`
   - `convert-potx` if no longer part of the core user journey
2. Keep only:
   - `create`
   - `validate` (likely rename from `validate-template` / unify with deck validation)
   - `insert-slide`
   - `update-slide`
   - `delete-slide`
3. Update `--help` text and examples to match the reduced surface.

### Deliverable
A small CLI that matches the requirements doc and is easy to explain in one screen.

---

## Workstream B — Terminology migration (`archetype` -> `layout_id`)

### Goal
Make `layout_id` the only external term.

### Tasks
1. Update deck spec schema to prefer/require `layout_id` externally.
2. Add compatibility normalization for old input using `archetype`.
3. Update CLI output, validation output, docs, warnings, and errors to say `layout_id`.
4. Keep internal aliasing temporarily where needed to avoid a risky big-bang rewrite.
5. Decide whether internal code symbols remain `archetype_*` for one version or get renamed immediately.

### Recommendation
Do a two-layer migration:
- external API/docs/validation: `layout_id`
- internal compatibility shim: translate `layout_id` -> existing internal representation until cleanup is complete

### Deliverable
Users only see `layout_id`; legacy `archetype` input still works during migration.

---

## Workstream C — Compact deck spec redesign

### Goal
Shrink the deck spec to a minimal, practical layout-driven model.

### Tasks
1. Define the v3 schema around:
   - `title`
   - `slides[]`
   - per-slide `layout_id`
   - only layout-specific fields
2. Normalize old shapes into the new minimal forms where sensible.
3. For each supported layout, define minimal field contracts:
   - `title`: `title`, optional `subtitle`
   - `section`: `title`
   - `title_and_bullets`: `title`, `bullets`
   - `title_subtitle_and_bullets`: `title`, `subtitle`, `bullets`
   - `text_with_image`: `title`, `body|bullets`, `image`
   - `version_page`: `title`, `table_text`
   - `agenda_with_image`: `title`, `image`, `items[]`
   - `two_col`: `title`, `left`, `right`
   - `three_col_with_icons`: `title`, `columns[]`
   - `picture_compare`: `title`, `left_image`, `right_image`, optional captions/text
4. Remove legacy extended shapes from user-facing docs and schema if they are outside the supported set.
5. Add examples for all 10 supported layout IDs.

### Deliverable
A single small user-facing schema that is easy for an LLM or human to produce.

---

## Workstream D — Render/fallback engine hardening

### Goal
Guarantee “render succeeds with fallback” for layout-level failures.

### Tasks
1. Introduce a central layout resolution pipeline:
   - validate requested `layout_id`
   - assess whether target template can render it
   - if not, rewrite to fallback path
2. Implement a standard fallback adapter for each unsupported/invalid layout case.
3. Ensure fallback content mapping is deterministic:
   - title preserved
   - subtitle/body/bullets collapsed sensibly into fallback bullets/body
   - warning attached to result
4. Ensure fallback never produces invalid PPTX.
5. Add regression coverage for:
   - unknown layout
   - missing template slot
   - invalid content shape
   - partial placeholder mismatch
   - fallback under insert/update, not only create

### Deliverable
Fallback becomes a first-class product contract rather than ad hoc behavior.

---

## Workstream E — Validation redesign

### Goal
Make validation answer the practical question: “Can this template render this deck spec?”

### Tasks
1. Create a single concise validate command and output format.
2. Validation should emit slide-by-slide statuses such as:
   - `ok`
   - `warning`
   - `fallback`
   - `error`
3. Validation checks:
   - supported `layout_id`
   - template mapping exists
   - required placeholders exist
   - content shape is acceptable
   - fallback likely/required
4. Validation should not expose exploratory/template-authoring details.
5. Align validate output with create output warnings.

### Deliverable
A short, actionable validation report that mirrors runtime behavior.

---

## Workstream F — Structural slide editing simplification

### Goal
Keep only the narrow deck-editing operations required by the spec.

### Tasks
1. Rename/add commands to align with requirements:
   - `insert-slide`
   - `update-slide`
   - `delete-slide`
2. Ensure insert/update accept the compact v3 slide spec.
3. Ensure insert/update also use fallback logic when requested `layout_id` cannot render.
4. Remove `list-slides` from the supported user surface.
5. Tighten invalid-index error messages.

### Deliverable
Slide editing is narrow, deterministic, and consistent with create/validate.

---

## Workstream G — Codebase deletion / retirement

### Goal
Actually shrink the codebase, not just hide features.

### Candidate removals after migration
- `commands/analyze.py`
- `commands/compile_exemplar.py`
- `commands/render_exemplar.py`
- `commands/validate_exemplar.py`
- `commands/bootstrap_from_slide.py`
- `commands/inspect_pptx.py`
- `commands/inspect_slide.py`
- `commands/inspect_template.py`
- `commands/map_template.py`
- `commands/plan.py`
- `commands/export_previews.py`
- `reference_analyzer.py`
- `exemplar_*`
- `template_bootstrapper.py`
- `template_mapper*.py` if mapper is no longer a supported workflow
- `pptx_inspector.py` / `openxml_*` if only used by removed flows
- other orphaned helper modules after command removal

### Tasks
1. Build a dependency map before deletion.
2. Remove dead commands first.
3. Remove no-longer-referenced modules second.
4. Run tests after each deletion wave.

### Deliverable
A meaningfully smaller package with less maintenance overhead.

---

## Workstream H — Docs and packaging cleanup

### Goal
Make docs match the simplified product exactly.

### Tasks
1. Rewrite docs around:
   - what `slide-smith` is
   - supported layout IDs
   - compact deck spec
   - fallback behavior
   - create/validate/edit commands
2. Remove template-authoring and design-history docs from the primary product docs.
3. Add a single user-facing layout guide for the 10 supported layouts.
4. Add a migration note:
   - `archetype` -> `layout_id`
   - removed commands
   - fallback semantics
5. Review packaging metadata and entry points so only supported commands remain documented/tested.

### Deliverable
A small docs set aligned with the simplified system.

---

# 4. Recommended implementation phases

## Phase 0 — Planning and compatibility scaffolding

### Goals
- agree final v3 external model
- minimize migration risk

### Tasks
- freeze supported layout IDs
- freeze compact deck spec shape
- define external `layout_id` compatibility layer
- define fallback warning schema
- document keep/remove command list

### Exit criteria
- one approved schema direction
- one approved CLI surface
- one approved fallback contract

---

## Phase 1 — External API shift to `layout_id`

### Goals
- users can start using v3 language immediately

### Tasks
- schema accepts `layout_id`
- input normalization supports legacy `archetype`
- docs/examples all use `layout_id`
- CLI output says `layout_id`

### Exit criteria
- user-facing examples contain no `archetype`
- create/validate work with `layout_id`

---

## Phase 2 — Fallback and validation foundation

### Goals
- make rendering behavior reliable before deleting features

### Tasks
- central fallback engine
- standardized warning payloads/messages
- slide-by-slide validation results
- regression tests for fallback under create/update/insert

### Exit criteria
- unsupported layouts no longer hard-fail deck creation unless template/output is fundamentally broken
- fallback behavior is tested and deterministic

---

## Phase 3 — Compact schema and supported-layout narrowing

### Goals
- align deck spec with the 10-layout vocabulary

### Tasks
- finalize v3 deck schema
- add examples for all supported layouts
- de-emphasize/remove legacy layouts from user-facing docs
- make validation focus on the supported set

### Exit criteria
- v3 schema is default in docs and tests
- supported layout list is explicit everywhere

---

## Phase 4 — CLI contraction

### Goals
- shrink user-facing commands to the target set

### Tasks
- remove obsolete commands from parser/help/docs
- rename editing commands if needed (`add-slide` -> `insert-slide`)
- unify validation commands into the simplified shape

### Exit criteria
- CLI help fits the new mental model
- removed commands are either gone or explicitly unsupported

---

## Phase 5 — Code deletion and hardening

### Goals
- simplify maintenance burden

### Tasks
- delete obsolete modules
- prune dead tests
- tighten package contents
- run full regression suite

### Exit criteria
- dead feature code is removed
- tests cover only supported product behavior

---

## Phase 6 — Release and migration

### Goals
- ship v3 cleanly

### Tasks
- write release notes
- write migration guide
- cut version/tag
- verify docs and examples

### Exit criteria
- release notes explain the simplification clearly
- users can migrate old deck specs with minimal confusion

---

# 5. Risks and mitigations

## Risk 1 — Large rename churn (`archetype` -> `layout_id`)
Mitigation:
- keep compatibility normalization internally first
- avoid renaming every internal symbol at once

## Risk 2 — Fallback hides real failures too aggressively
Mitigation:
- preserve hard failures for template load/output/index errors
- emit explicit fallback warnings with reasons
- make validate mirror fallback prediction

## Risk 3 — Removing commands breaks existing automation
Mitigation:
- provide one release cycle of migration notes
- optionally emit “removed in v3” guidance during transition if commands are still present temporarily

## Risk 4 — Code deletion causes hidden regressions
Mitigation:
- delete in waves after dependency checks
- keep focused tests for core create/validate/edit flows

## Risk 5 — `title_and_bullets` fallback may not preserve enough content
Mitigation:
- define deterministic content-collapse rules
- document what gets preserved in fallback
- add test fixtures for image/compare/column downgrade cases

---

# 6. Suggested issue breakdown

## Epic 1 — External model simplification
- v3 schema with `layout_id`
- legacy input normalization (`archetype` compatibility)
- supported layout contracts

## Epic 2 — Fallback reliability
- central fallback engine
- fallback warning model
- fallback regression suite

## Epic 3 — Validation redesign
- simplified validate command
- slide-by-slide statuses
- fallback prediction

## Epic 4 — Editing flow simplification
- insert/update/delete alignment
- fallback in update/insert
- index/error cleanup

## Epic 5 — CLI contraction
- remove obsolete commands
- rename remaining commands
- help text rewrite

## Epic 6 — Codebase cleanup
- remove exemplar/template-authoring code
- remove inspection code
- prune dead modules/tests

## Epic 7 — Docs and release
- rewrite user docs
- migration guide
- v3 release notes

---

# 7. Acceptance checklist for v3

v3 is done when:

- deck specs use `layout_id`
- only the 10 supported layout IDs are documented as the main vocabulary
- `create` renders reliably with deterministic fallback to `title_and_bullets`
- `validate` reports slide-by-slide renderability and fallback status
- only create / validate / insert-slide / update-slide / delete-slide remain in the core user journey
- removed workflows are no longer part of the docs or primary CLI surface
- docs explain the product in a much smaller, clearer way

---

# 8. Recommended sequence if you want the fastest path

If we optimize for fast delivery rather than perfect elegance:

1. Add external `layout_id` support without rewriting internals.
2. Implement central fallback behavior.
3. Simplify validate output.
4. Hide/remove obsolete CLI commands.
5. Rewrite docs/examples.
6. Delete dead modules last.

That path gets the product simplification visible early while reducing migration risk.
