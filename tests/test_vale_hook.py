"""Tests for the vale-hook PostToolUse prose feedback hook."""
import importlib.machinery
import importlib.util
import io
import json
import os
import pathlib

import pytest

TOOL = pathlib.Path(__file__).resolve().parent.parent / "bin" / ".local" / "bin" / "vale-hook"

# Matches tests/vale/run-fixtures.sh: styles live at ~/.config/vale/styles, populated by
# `vale sync` (bootstrap's setup_vale_styles step), not in this repo.
STYLES_PATH = os.path.expanduser("~/.config/vale/styles")


def _load():
    loader = importlib.machinery.SourceFileLoader("vale_hook", str(TOOL))
    spec = importlib.util.spec_from_loader("vale_hook", loader)
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod


vh = _load()


def test_changed_span_single_line():
    assert vh.changed_span("a\nWe delve here\nc\n", "We delve here") == {2}


def test_changed_span_multiline():
    assert vh.changed_span("a\nb1\nb2\nd\n", "b1\nb2") == {2, 3}


def test_changed_span_write_scopes_whole_file():
    assert vh.changed_span("a\nb\nc\n", "") == {1, 2, 3, 4}


def test_changed_span_absent_falls_back():
    assert vh.changed_span("a\nb\nc\n", "not here") == {1, 2, 3, 4}


def test_new_text_reads_edit_and_write():
    assert vh.new_text("Edit", {"new_string": "x"}) == "x"
    assert vh.new_text("Write", {"content": "y"}) == "y"


def test_config_root_finds_nearest(tmp_path):
    (tmp_path / ".vale.ini").write_text("StylesPath = x\n")
    sub = tmp_path / "a" / "b"
    sub.mkdir(parents=True)
    assert vh.config_root(str(sub)) == str(tmp_path)


def test_non_markdown_is_skipped(tmp_path, monkeypatch):
    payload = {"tool_name": "Edit",
               "tool_input": {"file_path": str(tmp_path / "x.ts"), "new_string": "x"}}
    monkeypatch.setattr("sys.stdin", io.StringIO(json.dumps(payload)))
    assert vh.main() == 0


class _PastSkip(Exception):
    """Marks that main() ran past the extension and planning-folder gates."""


def _raise_past_skip(_start_dir):
    raise _PastSkip


def _feed(monkeypatch, file_path, content):
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content)
    payload = {"tool_name": "Write", "tool_input": {"file_path": str(file_path), "content": content}}
    monkeypatch.setattr("sys.stdin", io.StringIO(json.dumps(payload)))


def test_planning_skip_is_a_path_segment(tmp_path, monkeypatch):
    """A docs planning folder is skipped; a "plans" directory outside docs is linted."""
    monkeypatch.setattr(vh, "config_root", _raise_past_skip)

    for linted in (tmp_path / "plans" / "docs" / "a.md", tmp_path / "mydocs" / "plans" / "a.md"):
        _feed(monkeypatch, linted, "prose\n")
        with pytest.raises(_PastSkip):
            vh.main()

    for folder in ("specs", "plans", "research", "archive"):
        _feed(monkeypatch, tmp_path / "docs" / folder / "a.md", "prose\n")
        assert vh.main() == 0


def test_md_gate_uses_splitext_on_basename(tmp_path, monkeypatch):
    """The Markdown gate reads the basename's extension, not a `.md` substring in the path."""
    monkeypatch.setattr(vh, "config_root", _raise_past_skip)

    # A ".md" directory segment must not make a non-Markdown file look like one.
    trapped = tmp_path / ".md" / "notes.txt"
    _feed(monkeypatch, trapped, "x")
    assert vh.main() == 0

    real_md = tmp_path / "page.md"
    _feed(monkeypatch, real_md, "x")
    with pytest.raises(_PastSkip):
        vh.main()


def _fixture_repo(tmp_path):
    """Build a three-section repo: docs/admin/ on Microsoft, docs/extend/ on Google,
    src/content/ on neither (the base Vale package, a positive control).
    """
    (tmp_path / ".vale.ini").write_text(
        f"StylesPath = {STYLES_PATH}\n"
        "MinAlertLevel = suggestion\n\n"
        "[docs/admin/**]\n"
        "BasedOnStyles = Microsoft\n\n"
        "[docs/extend/**]\n"
        "BasedOnStyles = Google\n\n"
        "[src/content/**]\n"
        "BasedOnStyles = Vale\n"
    )
    return tmp_path


def test_path_grading_resolves_the_microsoft_section(tmp_path, monkeypatch, capsys):
    root = _fixture_repo(tmp_path)
    page = root / "docs" / "admin" / "page.md"
    _feed(monkeypatch, page, "# Admin\n\nIn order to save your work, click Save.\n")
    assert vh.main() == 0
    out = capsys.readouterr().out
    assert f"(graded from config root {root}, as docs/admin/page.md)" in out
    assert "Microsoft" in out


def test_path_grading_resolves_the_google_section(tmp_path, monkeypatch, capsys):
    root = _fixture_repo(tmp_path)
    page = root / "docs" / "extend" / "page.md"
    _feed(
        monkeypatch, page,
        "# Extend\n\nThe API was designed by us. It helps developers extend the site.\n",
    )
    assert vh.main() == 0
    out = capsys.readouterr().out
    assert f"(graded from config root {root}, as docs/extend/page.md)" in out
    assert "Google" in out


def test_path_grading_resolves_neither_section(tmp_path, monkeypatch, capsys):
    """src/content/ matches neither the Microsoft nor the Google section. Vale.Spelling
    is the positive control: it proves Vale ran and graded this path rather than the
    hook failing open, which would look the same as "no findings" otherwise.
    """
    root = _fixture_repo(tmp_path)
    page = root / "src" / "content" / "page.md"
    _feed(monkeypatch, page, "# Content\n\nThis is recieved content with a typo.\n")
    assert vh.main() == 2
    err = capsys.readouterr().err
    assert f"(graded from config root {root}, as src/content/page.md)" in err
    assert "Vale.Spelling" in err
