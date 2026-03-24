from datetime import datetime
from pathlib import Path

from textual.app import App, ComposeResult
from textual.widgets import Button, Footer, Header, ListItem, ListView, MarkdownViewer, TextArea
from textual.containers import Horizontal, Vertical

from second_brain.app import get_notes_dir, slugify


class SecondBrainApp(App):
    """A two-pane TUI for browsing and creating notes."""

    CSS = """
    #sidebar {
        width: 30;
        border-right: solid $primary;
    }

    #note-list {
        height: 1fr;
    }

    #create-btn {
        dock: bottom;
        margin: 1;
    }

    #viewer {
        width: 1fr;
        height: 1fr;
        padding: 1;
    }

    #editor {
        width: 1fr;
        height: 1fr;
        padding: 1;
    }

    #editor-buttons {
        height: 3;
        dock: bottom;
        align: center middle;
    }

    #editor-buttons Button {
        margin: 0 1;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            with Vertical(id="sidebar"):
                yield ListView(id="note-list")
                yield Button("+ Create", id="create-btn", variant="success")
            yield MarkdownViewer("Select a note on the left to view its content.", id="viewer")
        yield Footer()

    def on_mount(self) -> None:
        self._load_notes()

    def _load_notes(self) -> None:
        notes_dir = get_notes_dir()
        self._notes = sorted(notes_dir.glob("*.md")) if notes_dir.exists() else []
        list_view = self.query_one("#note-list", ListView)
        list_view.clear()
        for note in self._notes:
            list_view.append(ListItem(Button(note.stem, classes="note-btn")))

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        index = event.list_view.index
        if index is not None and 0 <= index < len(self._notes):
            note = self._notes[index]
            content = note.read_text()
            viewer = self.query_one("#viewer", MarkdownViewer)
            viewer.document.update(content)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "create-btn":
            self._show_editor()
        elif event.button.id == "save-btn":
            self._save_note()
        elif event.button.id == "cancel-btn":
            self._show_viewer("Select a note on the left to view its content.")

    def _show_editor(self) -> None:
        viewer = self.query_one("#viewer")
        viewer.display = False

        editor_area = TextArea(id="editor")
        btn_row = Horizontal(
            Button("Save", id="save-btn", variant="success"),
            Button("Cancel", id="cancel-btn"),
            id="editor-buttons",
        )
        container = Vertical(editor_area, btn_row, id="editor-container")
        sidebar = self.query_one("#sidebar")
        sidebar.parent.mount(container)

    def _show_viewer(self, content: str = "") -> None:
        container = self.query_one("#editor-container", Vertical)
        container.remove()
        viewer = self.query_one("#viewer")
        viewer.display = True
        if content:
            viewer.document.update(content)

    def _save_note(self) -> None:
        editor = self.query_one("#editor", TextArea)
        text = editor.text.strip()
        if not text:
            self._show_viewer()
            return

        notes_dir = get_notes_dir()
        notes_dir.mkdir(parents=True, exist_ok=True)

        now = datetime.now()
        slug = slugify(text.splitlines()[0])
        filename = f"{now.strftime('%Y-%m-%d')}_{slug}.md"
        filepath = notes_dir / filename

        content = f"# {text.splitlines()[0]}\n\n*Saved on {now.strftime('%Y-%m-%d %H:%M')}*\n"
        if len(text.splitlines()) > 1:
            content += "\n" + "\n".join(text.splitlines()[1:]) + "\n"
        filepath.write_text(content)

        self._load_notes()
        self._show_viewer(content)


def launch_tui() -> None:
    """Launch the Textual TUI."""
    app = SecondBrainApp()
    app.run()
