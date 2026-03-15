# Canonical Template Workflow — Agentic COE 2026 Simple Template

Status: draft  
Related: #114, #97

This doc defines a **repeatable workflow** to produce a canonical `template.json` for:

- `/home/bzh/claw_share/Agentic COE 2026 simple template.pptx`

Goal: a template package that renders the redesigned archetypes (base + extended) cleanly and passes:

```bash
slide-smith validate-template --profile standard
slide-smith validate-template --profile extended
```

…and can render:

- `docs/examples/redesign/base.sample.json`
- `docs/examples/redesign/extended.sample.json`

## Why this exists

We now have:

- redesigned archetypes (see `docs/design/archetype-redesign-v1.md`)
- renderer conventions for `items[]`-based archetypes (render-time slot names)

…but we still need one “canonical” mapping for this specific branded template so users can copy a known-good setup.

## Expected archetypes

### Base (standard)

- `title`
- `section`
- `title_and_bullets`
- `title_subtitle_and_bullets`
- `text_with_image`

### Extended

- `title_subtitle`
- `version_page`
- `agenda_with_image`
- `two_col_with_subtitle`
- `three_col_with_subtitle`
- `three_col_with_icons`
- `five_col_with_icons`
- `picture_compare`
- `title_only_freeform`

## Slot conventions (must match renderer)

These are **template.json slot names** used by the renderer.

- `agenda_with_image`
  - `image`
  - Either:
    - fallback: `bullets` (single placeholder/box)
    - preferred: `item1_body` … `itemN_body` and optional `item1_marker` … `itemN_marker`

- `three_col_with_icons`
  - `col1_icon`, `col1_title`, `col1_body`, `col1_caption?`
  - `col2_icon`, `col2_title`, `col2_body`, `col2_caption?`
  - `col3_icon`, `col3_title`, `col3_body`, `col3_caption?`

- `five_col_with_icons`
  - `item1_icon`, `item1_body` … `item5_icon`, `item5_body`

- `picture_compare`
  - `left_image`, `left_title?`, `left_body?`
  - `right_image`, `right_title?`, `right_body?`

## Procedure (local)

### 0) Setup venv

```bash
cd ~/slide_smith
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

### 1) Bootstrap template package

```bash
slide-smith bootstrap-template \
  --pptx "/home/bzh/claw_share/Agentic COE 2026 simple template.pptx" \
  --template-id agentic_coe_2026_simple \
  --out-dir ./templates
```

### 2) Map standard + extended

```bash
slide-smith map-template \
  --template agentic_coe_2026_simple \
  --templates-dir ./templates \
  --write

# (optional) extended inference (legacy + redesign heuristics)
# NOTE: this is best-effort; expect to manually adjust slot names.
python -c "from slide_smith.template_loader import load_template_spec; from slide_smith.template_mapper_extended import infer_extended_mappings; import json; spec=load_template_spec('agentic_coe_2026_simple', templates_dir='./templates'); out=infer_extended_mappings(spec); print(json.dumps(out,indent=2))" > /tmp/extended.json
```

### 3) Validate

```bash
slide-smith validate-template --template agentic_coe_2026_simple --templates-dir ./templates --profile standard
slide-smith validate-template --template agentic_coe_2026_simple --templates-dir ./templates --profile extended
```

### 4) Smoke render the redesign examples

```bash
slide-smith create \
  --input docs/examples/redesign/base.sample.json \
  --template agentic_coe_2026_simple \
  --templates-dir ./templates \
  --output /tmp/agentic.base.pptx \
  --print none

slide-smith create \
  --input docs/examples/redesign/extended.sample.json \
  --template agentic_coe_2026_simple \
  --templates-dir ./templates \
  --output /tmp/agentic.extended.pptx \
  --print none
```

### 5) Output integrity check (no duplicate ZIP members)

```bash
python - <<'PY'
import zipfile
from collections import Counter

def assert_no_dups(path: str):
    with zipfile.ZipFile(path) as z:
        c=Counter(z.namelist())
        d=[(k,v) for k,v in c.items() if v>1]
        if d:
            raise SystemExit('Duplicate zip members:\n'+'\n'.join([f"{v} {k}" for k,v in d[:50]]))

assert_no_dups('/tmp/agentic.base.pptx')
assert_no_dups('/tmp/agentic.extended.pptx')
print('OK: no duplicates')
PY
```

## What to commit

To keep the repo small and avoid licensing issues, prefer committing:

- `templates/agentic_coe_2026_simple/template.json`
- `templates/agentic_coe_2026_simple/README.md` (provenance + how to regenerate)

Avoid committing the PPTX itself unless we explicitly decide it’s OK.

## Known manual steps

Mapper inference may not perfectly name slots for icon/compare/agenda layouts. Manual edits often include:

- renaming `body` placeholders into `col{i}_body` / `item{i}_body`
- adding `*_icon` slots as `type=image` with correct placeholder idx
- creating `left_*` / `right_*` slots for compare layouts

The renderer + validator are now consistent with the conventions above.
