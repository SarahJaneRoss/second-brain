# second-brain

A Python application project scaffolded with best practices for logging, testing, and documentation.

## Key facts

- **Package manager:** `uv` — always use `uv run` to run commands, never `pip` or `python` directly
- **Package name:** `second_brain` (underscores, not hyphens)
- **Python version:** 3.13+
- **Source layout:** all application code lives in `src/second_brain/`

## Running the app

```bash
uv run second_brain                       # run with defaults
uv run --env-file .env second_brain       # run with dev settings
```

## Running tests

```bash
uv run pytest                             # run tests
uv run pytest --cov                       # run tests with coverage report
```

## Adding dependencies

```bash
uv add <package-name>                     # add a runtime dependency
uv add --dev <package-name>               # add a dev-only dependency
```

## Project owner context

The project owner is a non-developer learning about Claude Code. Explain things in plain, simple language without assuming programming knowledge.
