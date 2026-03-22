import os
import re
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


def main():
    """Run the application."""
    configure_logging()
    cli()
