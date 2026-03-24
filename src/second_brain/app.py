import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import click
from loguru import logger


def configure_logging():
    """Configure loguru for console and file logging.

    Removes the default handler and sets up:
    - stderr handler at LOG_LEVEL (default: INFO, configurable via env var)
    - File handler at DEBUG level writing to LOG_FILE (default: app.log)
    """
    log_level = os.environ.get("LOG_LEVEL", "INFO")
    log_file = os.environ.get("LOG_FILE", "app.log")
    logger.remove()
    logger.add(sys.stderr, level=log_level)
    logger.add(log_file, level="DEBUG", rotation="50 KB", retention=1)


def slugify(text):
    """Turn a note into a filename-safe slug.

    Example: "My brilliant idea!" -> "my-brilliant-idea"
    """
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = text.strip("-")
    return text[:60]


def get_notes_dir():
    """Return the notes directory path from env, defaulting to ~/second_brain."""
    notes_dir = os.environ.get("NOTES_DIR", "~/second_brain")
    return Path(notes_dir).expanduser()


@click.group()
def cli():
    """second_brain — your personal knowledge base."""


@cli.command()
@click.argument("text")
@click.option("--title", default=None, help="Short title for the filename (optional)")
def new(text, title):
    """Save a new note.

    Example: second_brain new "My brilliant idea about caching"
    Example: second_brain new "My brilliant idea" --title "caching idea"
    """
    notes_dir = get_notes_dir()
    notes_dir.mkdir(parents=True, exist_ok=True)

    now = datetime.now()
    slug = slugify(title) if title else slugify(text)
    filename = f"{now.strftime('%Y-%m-%d')}_{slug}.md"
    filepath = notes_dir / filename

    content = f"# {text}\n\n*Saved on {now.strftime('%Y-%m-%d %H:%M')}*\n"
    filepath.write_text(content)

    click.echo(f"Note saved: {filepath}")


@cli.command(name="list")
def list_notes():
    """List all saved notes.

    Example: second_brain list
    """
    notes_dir = get_notes_dir()

    if not notes_dir.exists():
        click.echo(f"No notes found in {notes_dir}.")
        return

    notes = sorted(notes_dir.glob("*.md"))

    if not notes:
        click.echo(f"No notes found in {notes_dir}.")
        return

    click.echo(f"\nNotes in {notes_dir}:\n")
    for i, note in enumerate(notes, start=1):
        click.echo(f"{i}. {note.name}")


@cli.command()
@click.argument("number", type=int)
def show(number):
    """Show the content of a note by its number.

    Example: second_brain show 1
    """
    notes_dir = get_notes_dir()
    notes = sorted(notes_dir.glob("*.md")) if notes_dir.exists() else []

    if not notes:
        click.echo(f"No notes found in {notes_dir}.")
        return

    if number < 1 or number > len(notes):
        click.echo(
            f"Error: Note {number} not found. Run 'second_brain list' to see available notes."
        )
        return

    note = notes[number - 1]
    divider = "─" * len(note.name)
    click.echo(f"\n{note.name}\n{divider}\n{note.read_text()}")


def get_todos_path(notes_dir: Path) -> Path:
    """Return the path for the todos inbox file."""
    return notes_dir / "todos.md"


def ensure_todos(notes_dir: Path) -> Path:
    """Get the todos file, creating it if it doesn't exist yet."""
    notes_dir.mkdir(parents=True, exist_ok=True)
    path = get_todos_path(notes_dir)
    if not path.exists():
        path.write_text("# Todos\n\n")
    return path


@cli.group()
def todo():
    """Manage your todo inbox."""


@todo.command(name="add")
@click.argument("item", nargs=-1, required=True)
def todo_add(item):
    """Add a new todo item.

    Example: second_brain todo add buy milk
    """
    text = " ".join(item)
    notes_dir = get_notes_dir()
    path = ensure_todos(notes_dir)

    with path.open("a") as f:
        f.write(f"- [ ] {text}\n")

    click.echo(f"Todo added: {text}")


@todo.command(name="list")
def todo_list():
    """List all todos.

    Example: second_brain todo list
    """
    notes_dir = get_notes_dir()
    path = get_todos_path(notes_dir)

    if not path.exists():
        click.echo("No todos yet.")
        return

    click.echo(path.read_text())


def get_journal_path(notes_dir: Path) -> Path:
    """Return the path for today's journal file."""
    today = datetime.now().strftime("%Y-%m-%d")
    return notes_dir / f"journal_{today}.md"


def ensure_journal(notes_dir: Path) -> Path:
    """Get today's journal, creating it with a header if it doesn't exist yet."""
    notes_dir.mkdir(parents=True, exist_ok=True)
    path = get_journal_path(notes_dir)
    if not path.exists():
        today = datetime.now().strftime("%Y-%m-%d")
        path.write_text(f"# Journal — {today}\n\n")
    return path


@cli.command()
@click.argument("entry", nargs=-1, required=True)
def log(entry):
    """Add a quick bullet to today's journal entry.

    Example: second_brain log 1:1 Philip — discussed launch timeline
    """
    text = " ".join(entry)
    notes_dir = get_notes_dir()
    path = ensure_journal(notes_dir)

    now = datetime.now().strftime("%H:%M")
    with path.open("a") as f:
        f.write(f"- {now} {text}\n")

    click.echo(f"Logged: {text}")


@cli.command()
def journal():
    """Open today's journal entry."""
    notes_dir = get_notes_dir()
    path = ensure_journal(notes_dir)
    click.echo(path.read_text())


@cli.command(name="import-log")
def import_log():
    """Paste a work log into today's journal.

    Paste your content, then press Ctrl+D to save.

    Example: second_brain import-log
    """
    click.echo("Paste your work log, then press Ctrl+D to save:\n")
    content = sys.stdin.read().strip()

    if not content:
        click.echo("Nothing to import.")
        return

    notes_dir = get_notes_dir()
    path = ensure_journal(notes_dir)

    now = datetime.now().strftime("%H:%M")
    with path.open("a") as f:
        f.write(f"\n## Work log imported at {now}\n\n{content}\n")

    click.echo("\nWork log added to today's journal.")


STANDUP_PROMPT = """You are helping Sarah Jane write her daily Basecamp check-in response to "What have you worked on today?"

Rules:
- Report only what actually happened — no embellishment, no drama, no "finally figured out"
- Tasks and tool runs are reported as plain facts: what was run, what was found, what was done
- Do not group items into categories (no Strategy, Content, Tooling, or any other headings) — everything goes into one flat list
- 1:1s and conversations can be brief narrative since they involve real human context
- No filler phrases like "dove deep", "satisfying", "exciting", or anything that adds color to routine work
- Keep it concise — a grocery list of what got done, written in first person
- Ready to paste into Basecamp as-is

Here is today's journal:

{journal}

Write the check-in now."""


@cli.command()
def standup():
    """Generate a Basecamp standup from today's journal.

    Example: second_brain standup
    """
    notes_dir = get_notes_dir()
    path = get_journal_path(notes_dir)

    if not path.exists():
        click.echo("No journal entries for today yet.")
        return

    journal_content = path.read_text().strip()
    if not journal_content:
        click.echo("Today's journal is empty.")
        return

    prompt = STANDUP_PROMPT.format(journal=journal_content)

    click.echo("Generating your standup...\n")
    result = subprocess.run(
        ["claude", "-p", prompt],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        click.echo(f"Error: {result.stderr}")
        return

    click.echo(result.stdout)


def main():
    """Run the application."""
    configure_logging()
    if len(sys.argv) == 1:
        from second_brain.tui import launch_tui
        launch_tui()
    else:
        cli()
