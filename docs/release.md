# Release Checklist

Current release line: `v3.x`

## Local verification

Use the project-local virtual environment.

```bash
cd ~/slide_smith
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
pytest -q
slide-smith --version
slide-smith --help
```

## Build / package checks

```bash
.venv/bin/python -m pip install build twine
.venv/bin/python -m build
.venv/bin/python -m twine check dist/*
```

## Release prep

- Ensure `pyproject.toml` version is updated.
- Ensure `src/slide_smith/__init__.py` version matches.
- Ensure docs reflect the current release surface only.
- Ensure current examples validate via `slide-smith validate` and render against supported templates.
- Ensure the default template remains compatible with current base archetype names.

## Tagging and GitHub release

```bash
git push origin main
git tag -a vX.Y.Z -m "slide-smith vX.Y.Z"
git push origin vX.Y.Z
gh release create vX.Y.Z --repo ninjapapa/slide_smith --title "vX.Y.Z"
```

## Suggested release notes sections

- Highlights
- Added / changed archetypes
- Validation / schema changes
- Template workflow changes
- Compatibility notes / deprecations
