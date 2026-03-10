# Release / packaging notes

## Local smoke

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
pytest -q
slide-smith --help
```

## Build / check

```bash
pip install build twine
python -m build
python -m twine check dist/*
```

## Tagging

```bash
git tag -a v0.1.0 -m "v0.1.0"
git push --tags
```

(If we publish to PyPI later, add twine upload steps.)
