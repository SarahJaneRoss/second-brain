from click.testing import CliRunner

from second_brain.app import cli


def test_new_creates_file(tmp_path, monkeypatch):
    monkeypatch.setenv("NOTES_DIR", str(tmp_path))
    runner = CliRunner()
    runner.invoke(cli, ["new", "My brilliant idea about caching"])
    files = list(tmp_path.glob("*.md"))
    assert len(files) == 1


def test_new_file_contains_text(tmp_path, monkeypatch):
    monkeypatch.setenv("NOTES_DIR", str(tmp_path))
    runner = CliRunner()
    runner.invoke(cli, ["new", "My brilliant idea about caching"])
    files = list(tmp_path.glob("*.md"))
    content = files[0].read_text()
    assert "My brilliant idea about caching" in content


def test_new_creates_directory(tmp_path, monkeypatch):
    notes_dir = tmp_path / "nested" / "notes"
    monkeypatch.setenv("NOTES_DIR", str(notes_dir))
    runner = CliRunner()
    runner.invoke(cli, ["new", "Testing directory creation"])
    assert notes_dir.exists()


def test_new_prints_confirmation(tmp_path, monkeypatch):
    monkeypatch.setenv("NOTES_DIR", str(tmp_path))
    runner = CliRunner()
    result = runner.invoke(cli, ["new", "Hello world"])
    assert "Note saved:" in result.output


def test_list_shows_directory_path(tmp_path, monkeypatch):
    monkeypatch.setenv("NOTES_DIR", str(tmp_path))
    runner = CliRunner()
    runner.invoke(cli, ["new", "A note"])
    result = runner.invoke(cli, ["list"])
    assert str(tmp_path) in result.output


def test_list_shows_numbered_files(tmp_path, monkeypatch):
    monkeypatch.setenv("NOTES_DIR", str(tmp_path))
    runner = CliRunner()
    runner.invoke(cli, ["new", "First note"])
    runner.invoke(cli, ["new", "Second note"])
    result = runner.invoke(cli, ["list"])
    assert "1." in result.output
    assert "2." in result.output


def test_list_empty_directory(tmp_path, monkeypatch):
    monkeypatch.setenv("NOTES_DIR", str(tmp_path))
    runner = CliRunner()
    result = runner.invoke(cli, ["list"])
    assert "No notes found" in result.output


def test_list_no_directory(tmp_path, monkeypatch):
    notes_dir = tmp_path / "does_not_exist"
    monkeypatch.setenv("NOTES_DIR", str(notes_dir))
    runner = CliRunner()
    result = runner.invoke(cli, ["list"])
    assert "No notes found" in result.output


def test_show_prints_note_content(tmp_path, monkeypatch):
    monkeypatch.setenv("NOTES_DIR", str(tmp_path))
    runner = CliRunner()
    runner.invoke(cli, ["new", "My brilliant idea"])
    result = runner.invoke(cli, ["show", "1"])
    assert "My brilliant idea" in result.output


def test_show_prints_filename(tmp_path, monkeypatch):
    monkeypatch.setenv("NOTES_DIR", str(tmp_path))
    runner = CliRunner()
    runner.invoke(cli, ["new", "My brilliant idea"])
    result = runner.invoke(cli, ["show", "1"])
    assert ".md" in result.output


def test_show_invalid_number(tmp_path, monkeypatch):
    monkeypatch.setenv("NOTES_DIR", str(tmp_path))
    runner = CliRunner()
    runner.invoke(cli, ["new", "Only one note"])
    result = runner.invoke(cli, ["show", "99"])
    assert "not found" in result.output


def test_show_no_notes(tmp_path, monkeypatch):
    monkeypatch.setenv("NOTES_DIR", str(tmp_path))
    runner = CliRunner()
    result = runner.invoke(cli, ["show", "1"])
    assert "No notes found" in result.output


def test_new_with_title_uses_title_in_filename(tmp_path, monkeypatch):
    monkeypatch.setenv("NOTES_DIR", str(tmp_path))
    runner = CliRunner()
    runner.invoke(cli, ["new", "A very long note with lots of detail", "--title", "building features"])
    files = list(tmp_path.glob("*.md"))
    assert "building-features" in files[0].name


def test_new_with_title_still_saves_full_text(tmp_path, monkeypatch):
    monkeypatch.setenv("NOTES_DIR", str(tmp_path))
    runner = CliRunner()
    runner.invoke(cli, ["new", "A very long note with lots of detail", "--title", "building features"])
    files = list(tmp_path.glob("*.md"))
    assert "A very long note with lots of detail" in files[0].read_text()


def test_new_without_title_uses_note_text(tmp_path, monkeypatch):
    monkeypatch.setenv("NOTES_DIR", str(tmp_path))
    runner = CliRunner()
    runner.invoke(cli, ["new", "My brilliant idea"])
    files = list(tmp_path.glob("*.md"))
    assert "my-brilliant-idea" in files[0].name
