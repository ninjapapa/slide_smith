# Archetype Redesign Examples

These sample deck specs demonstrate the proposed Base vs Extended archetypes.

## Files

- `base.sample.json`
- `extended.sample.json`

## Usage

```bash
slide-smith validate-deck-spec --input docs/examples/redesign/base.sample.json --profile legacy
slide-smith validate-deck-spec --input docs/examples/redesign/extended.sample.json --profile legacy

# render (requires a template that maps these archetypes)
slide-smith create \
  --input docs/examples/redesign/base.sample.json \
  --template <template_id> \
  --templates-dir <templates_dir> \
  --output /tmp/base.sample.pptx \
  --print none
```

Notes:
- `text_with_image` expects an `image` path. The example uses placeholder paths under `./assets/`.
- Extended archetypes like `three_col_with_icons` require the template spec to expose slot names like `col1_icon`, `col1_title`, etc.
