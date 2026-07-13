# Development

This project uses [`uv`](https://docs.astral.sh/uv/) for dependency management
and [`pre-commit`](https://pre-commit.com/) to enforce code quality and
conventional commit messages.

## Setup

After cloning the repository, set up the development environment and register
both pre-commit and commit-msg git hooks:

```bash
uv sync
uv run pre-commit install --hook-type pre-commit --hook-type commit-msg
```

## Testing

To execute the automated test suite and check code coverage:

```bash
uv run pytest
```

To continuously run adaptive, coverage-guided property-based fuzzing on the
hypothesis test suite (`tests/test_properties.py`):

```bash
uv run hypothesis fuzz tests/test_properties.py
```

## Building Documentation

To build and view the documentation locally:

```bash
uv run mkdocs serve
```
