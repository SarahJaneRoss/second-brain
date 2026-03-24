# second-brain

A personal knowledge base for capturing notes, todos, journal entries, and daily work logs — with a built-in standup generator for end-of-day reporting.

## Cheat Sheet

| Command | What it does |
|---|---|
| `todo <the thing you want to remember>` | Adds a todo item |
| `todos` | Shows all your todos |
| `note "<your note text>"` | Saves a quick note |
| `log <what just happened>` | Adds a timestamped bullet to today's journal |
| `journal` | Shows today's journal entries |
| `import_log` | Paste a work log from another tool into today's journal |
| `standup` | Generates your Basecamp check-in from today's journal |
| `sb` | Opens the visual app (press Ctrl+C to quit) |

### How to use import_log

1. Type `import_log` and press Enter
2. Paste your work log contents
3. Press **Ctrl+D** (hold Control, tap D) — this tells the terminal you're done
4. It will confirm: "Work log added to today's journal"

### How to open Claude Code in this project

1. Open a terminal window
2. Type: `cd ~/claude-code-course/playground/second-brain`
3. Type: `claude`

## Installation

Clone the repository and install dependencies:

```bash
git clone <repo-url>
cd second-brain
uv sync
```

## Usage

### Save a note

```bash
uv run second_brain new "My brilliant idea about caching"
```

Add an optional `--title` for a shorter, more meaningful filename:

```bash
uv run second_brain new "My brilliant idea about caching" --title "caching idea"
```

Saves as `2026-03-22_caching-idea.md` — the full note text is still inside the file.

### List your notes

```bash
uv run second_brain list
```

Shows the notes folder path and a numbered list of all your saved notes.

### Read a note

```bash
uv run second_brain show 1
```

Prints the content of note #1 (use the number from `second_brain list`).

This saves a markdown file to your notes folder with a filename like `2026-03-22_my-brilliant-idea-about-caching.md`.

With dev environment loaded:

```bash
uv run --env-file .env second_brain new "My brilliant idea"
```

## Environment Variables

Copy `.env.example` to `.env` for development:

```bash
cp .env.example .env
```

| Variable    | Default           | Description                                                  |
|-------------|-------------------|--------------------------------------------------------------|
| `LOG_LEVEL` | `INFO`            | Console log level. Set to `DEBUG` in `.env` for verbose output. |
| `LOG_FILE`  | `app.log`         | Path to the log file.                                        |
| `NOTES_DIR` | `~/second_brain`  | Folder where notes are saved. Created automatically if it doesn't exist. |

Note: `uv run --env-file .env` loads the dev environment explicitly — there is no auto-loading.

## Testing

Run tests:

```bash
uv run pytest
```

Run tests with coverage:

```bash
uv run pytest --cov
```

## Documentation

Preview docs locally:

```bash
uv run python scripts/serve_docs.py
```

Build static docs:

```bash
uv run mkdocs build
```
