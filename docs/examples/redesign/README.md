# Redesign Examples

These are the current sample deck specs for the redesigned/base+extended archetype set.

## Files

- `base.sample.json`
- `extended.sample.json`

## Validate

```bash
slide-smith validate --input docs/examples/redesign/base.sample.json --template default
slide-smith validate --input docs/examples/redesign/extended.sample.json --template default
```

## Render

```bash
slide-smith create \
  --input docs/examples/redesign/base.sample.json \
  --template <template_id> \
  --templates-dir <templates_dir> \
  --output /tmp/base.sample.pptx \
  --print none

slide-smith create \
  --input docs/examples/redesign/extended.sample.json \
  --template <template_id> \
  --templates-dir <templates_dir> \
  --output /tmp/extended.sample.pptx \
  --print none
```

## Notes

- `text_with_image` expects an image path or image object.
- Extended item-based layouts require template slot names that follow the current conventions table in `docs/layout-ids.md`.
- These examples replace the older `docs/design/examples/*` samples as the current reference set.
