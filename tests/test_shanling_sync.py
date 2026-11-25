"""Tests for shanling-sync, the Shanling Q2 card mirror.

Every test runs the real rsync against folders under tmp_path, so no live card or volume under
/run/media is touched. Three seams are patched: stdin's isatty with the answer fed on stdin, the
free-space figure through space(), and os.path.ismount for --init.
"""

import contextlib
import importlib.machinery
import importlib.util
import io
import os
from pathlib import Path
import shutil

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "bin/.local/bin/shanling-sync"

loader = importlib.machinery.SourceFileLoader("shanling_sync", str(SCRIPT))
spec = importlib.util.spec_from_loader("shanling_sync", loader)
ss = importlib.util.module_from_spec(spec)
loader.exec_module(ss)


class Stdin(io.StringIO):
    """A stdin that feeds an answer and says whether it is a terminal."""

    def __init__(self, text: str, tty: bool):
        super().__init__(text)
        self.tty = tty

    def isatty(self):
        return self.tty


def answer(monkeypatch, text: str, tty: bool = True):
    monkeypatch.setattr("sys.stdin", Stdin(text, tty))


@contextlib.contextmanager
def locked(path: Path, mode: int):
    """Set a folder's mode for the block and restore it after, so tmp_path can be removed."""
    path.chmod(mode)
    try:
        yield
    finally:
        path.chmod(0o755)


def write(path: Path, data: str = "audio") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(data)


def tree(root: Path) -> dict[str, str]:
    """Return every file and folder under root with its content or None, to compare before and after."""
    out = {}
    for p in sorted(root.rglob("*")):
        out[str(p.relative_to(root))] = p.read_text() if p.is_file() else None
    return out


@pytest.fixture
def rig(tmp_path, monkeypatch):
    """A library of two albums, a marked card, an unmarked volume, and an empty gvfs folder."""
    music = tmp_path / "Music"
    write(music / "Artist A/Album 1/01.flac", "a1")
    write(music / "Artist A/Album 1/cover.jpg", "cover")
    write(music / "Artist B/Album 2/01.flac", "b2")
    media = tmp_path / "media"
    card = media / "Q2CARD"
    card.mkdir(parents=True)
    (card / ss.MARKER).touch()
    stick = media / "usbstick"
    stick.mkdir()
    write(stick / "keep.txt")
    gvfs = tmp_path / "gvfs"
    gvfs.mkdir()
    monkeypatch.setenv("SHANLING_SYNC_MUSIC", str(music))
    monkeypatch.setenv("SHANLING_SYNC_MEDIA", str(media))
    monkeypatch.setenv("SHANLING_SYNC_GVFS", str(gvfs))
    monkeypatch.setattr(ss, "space", lambda card: (4096, 1 << 40))
    answer(monkeypatch, "", tty=False)
    return {"music": music, "media": media, "card": card, "stick": stick, "gvfs": gvfs}


def synced(rig):
    """Run one clean sync so the card holds the library."""
    assert ss.main([]) == 0
    return rig["card"] / "Music"


def test_first_run_copies_library_and_second_run_copies_nothing(rig, capsys):
    dest = synced(rig)
    assert tree(dest) == tree(rig["music"])
    assert capsys.readouterr().out.rstrip().endswith("Done. Eject the card before unplugging it.")
    assert ss.main(["--dry-run"]) == 0
    out = capsys.readouterr().out
    assert "Copy 0 files" in out
    assert "Deletions" not in out


def test_no_marked_card_names_the_unmarked_volume(rig, capsys):
    (rig["card"] / ss.MARKER).unlink()
    assert ss.main([]) == 1
    err = capsys.readouterr().err
    assert "usbstick" in err
    assert "Q2CARD" in err
    assert "--init" in err
    assert "MTP" not in err
    assert not (rig["card"] / "Music").exists()


def test_no_volumes_at_all_exits_1(rig, capsys):
    shutil.rmtree(rig["media"])
    assert ss.main([]) == 1
    assert "Nothing is mounted" in capsys.readouterr().err


def test_mtp_entry_adds_the_mtp_message(rig, capsys):
    (rig["card"] / ss.MARKER).unlink()
    (rig["gvfs"] / "mtp:host=x").mkdir()
    assert ss.main([]) == 1
    err = capsys.readouterr().err
    assert "MTP device" in err
    assert "storage" in err


def test_two_marked_cards_exit_1(rig, capsys):
    (rig["stick"] / ss.MARKER).touch()
    assert ss.main([]) == 1
    err = capsys.readouterr().err
    assert "Q2CARD" in err
    assert "usbstick" in err
    assert not (rig["card"] / "Music").exists()


def test_init_writes_marker_and_reports_an_existing_one(rig, monkeypatch, capsys):
    monkeypatch.setattr(os.path, "ismount", lambda p: True)
    assert ss.main(["--init", str(rig["stick"])]) == 0
    assert (rig["stick"] / ss.MARKER).is_file()
    assert ss.main(["--init", str(rig["stick"])]) == 0
    assert "already marked" in capsys.readouterr().out


def test_init_refuses_a_path_outside_the_media_root(rig, tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(os.path, "ismount", lambda p: True)
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    assert ss.main(["--init", str(elsewhere)]) == 1
    assert not (elsewhere / ss.MARKER).exists()
    nested = rig["stick"] / "sub"
    nested.mkdir()
    assert ss.main(["--init", str(nested)]) == 1
    assert not (nested / ss.MARKER).exists()
    assert "not a folder directly under" in capsys.readouterr().err


def test_init_refuses_a_folder_that_is_not_a_mount_point(rig, capsys):
    assert ss.main(["--init", str(rig["stick"])]) == 1
    assert not (rig["stick"] / ss.MARKER).exists()
    assert "not a mounted volume" in capsys.readouterr().err


def test_init_exits_1_when_the_volume_is_read_only(rig, monkeypatch, capsys):
    monkeypatch.setattr(os.path, "ismount", lambda p: True)
    with locked(rig["stick"], 0o555):
        assert ss.main(["--init", str(rig["stick"])]) == 1
    assert "Could not mark" in capsys.readouterr().err


@pytest.mark.parametrize("state", ["missing", "empty", "folders only"])
def test_a_missing_or_empty_music_folder_exits_1_and_the_card_is_unchanged(rig, monkeypatch, state):
    dest = synced(rig)
    before = tree(rig["card"])
    shutil.rmtree(rig["music"])
    if state != "missing":
        rig["music"].mkdir()
    if state == "folders only":
        (rig["music"] / "Artist A").mkdir()
    answer(monkeypatch, "y\n")
    assert ss.main([]) == 1
    assert tree(rig["card"]) == before
    assert (dest / "Artist A/Album 1/01.flac").is_file()


def test_dry_run_changes_no_file(rig, capsys):
    dest = synced(rig)
    shutil.rmtree(rig["music"] / "Artist B")
    write(rig["music"] / "Artist C/Album 3/01.flac", "c3")
    before = tree(rig["card"])
    assert ss.main(["--dry-run"]) == 0
    assert tree(rig["card"]) == before
    out = capsys.readouterr().out
    assert "Copy 1 files" in out
    assert "Artist B/" in out
    assert (dest / "Artist B/Album 2/01.flac").is_file()


def test_dry_run_on_a_fresh_card_does_not_create_music(rig):
    assert ss.main(["--dry-run"]) == 0
    assert not (rig["card"] / "Music").exists()


def test_y_deletes_a_removed_album_and_spares_what_is_outside_music(rig, monkeypatch, capsys):
    dest = synced(rig)
    write(rig["card"] / "beside.txt", "beside")
    shutil.rmtree(rig["music"] / "Artist B")
    answer(monkeypatch, "y\n")
    assert ss.main([]) == 0
    assert not (dest / "Artist B").exists()
    assert (dest / "Artist A/Album 1/01.flac").is_file()
    assert (rig["card"] / "beside.txt").read_text() == "beside"
    assert (rig["stick"] / "keep.txt").is_file()
    out = capsys.readouterr().out
    assert "Delete these 3 paths from the card? [y/N]" in out
    assert not out.rstrip().endswith("on the card.")


@pytest.mark.parametrize(
    ("text", "tty"),
    [("n\n", True), ("", True), ("\n", True), ("maybe\n", True), ("y\n", False)],
    ids=["n", "end of input", "enter", "other answer", "not a terminal"],
)
def test_a_declined_deletion_keeps_the_album_and_still_copies_a_new_one(rig, monkeypatch, capsys, text, tty):
    dest = synced(rig)
    shutil.rmtree(rig["music"] / "Artist B")
    write(rig["music"] / "Artist C/Album 3/01.flac", "c3")
    answer(monkeypatch, text, tty)
    assert ss.main([]) == 0
    assert (dest / "Artist B/Album 2/01.flac").read_text() == "b2"
    assert (dest / "Artist C/Album 3/01.flac").read_text() == "c3"
    assert "Kept 3 paths on the card." in capsys.readouterr().out


def test_ctrl_c_at_the_prompt_keeps_the_album_without_a_traceback(rig, monkeypatch, capsys):
    dest = synced(rig)
    shutil.rmtree(rig["music"] / "Artist B")
    answer(monkeypatch, "")

    def interrupt(prompt=""):
        raise KeyboardInterrupt

    monkeypatch.setattr("builtins.input", interrupt)
    assert ss.main([]) == 0
    assert (dest / "Artist B/Album 2/01.flac").is_file()
    assert "Traceback" not in capsys.readouterr().err


def test_free_space_below_the_bytes_needed_exits_1_with_nothing_copied(rig, monkeypatch, capsys):
    monkeypatch.setattr(ss, "space", lambda card: (4096, ss.MARGIN))
    assert ss.main([]) == 1
    assert not (rig["card"] / "Music").exists()
    err = capsys.readouterr().err
    assert f"{ss.MARGIN + 3 * 4096:,}" in err
    assert f"{ss.MARGIN:,}" in err


def test_a_dry_run_that_runs_short_still_prints_the_copy_count_and_deletions(rig, monkeypatch, capsys):
    synced(rig)
    shutil.rmtree(rig["music"] / "Artist B")
    write(rig["music"] / "Artist C/Album 3/01.flac", "c3")
    capsys.readouterr()
    monkeypatch.setattr(ss, "space", lambda card: (4096, ss.MARGIN))
    assert ss.main(["--dry-run"]) == 1
    cap = capsys.readouterr()
    assert "Copy 1 files" in cap.out
    assert "Artist B/Album 2/01.flac" in cap.out
    assert "needs" in cap.err


def test_space_rounds_each_copy_up_to_a_cluster(rig, monkeypatch):
    needed = 3 * 32768 + ss.MARGIN
    monkeypatch.setattr(ss, "space", lambda card: (32768, needed))
    assert ss.main(["--dry-run"]) == 0
    monkeypatch.setattr(ss, "space", lambda card: (32768, needed - 1))
    assert ss.main(["--dry-run"]) == 1


def test_a_copy_that_rsync_cannot_write_passes_its_exit_through(rig):
    # With the card folder read-only rsync can't make Music/ (its exit 11). The dry run, which
    # makes nothing, still passes.
    with locked(rig["card"], 0o555):
        assert ss.main(["--dry-run"]) == 0
        assert ss.main([]) == 11
    assert not (rig["card"] / "Music").exists()


def test_a_read_only_music_folder_exits_with_rsyncs_code(rig):
    dest = synced(rig)
    write(rig["music"] / "Artist C/Album 3/01.flac", "c3")
    with locked(dest, 0):
        assert ss.main([]) == 3
    assert not (dest / "Artist C").exists()


def test_delete_refuses_a_path_outside_music_before_deleting_anything(rig):
    dest = synced(rig)
    outside = rig["card"] / "beside.txt"
    write(outside)
    with pytest.raises(ss.Fail):
        ss.delete(dest, ["Artist B/Album 2/01.flac", "../beside.txt"])
    assert (dest / "Artist B/Album 2/01.flac").is_file()
    assert outside.is_file()


def test_a_file_on_the_card_where_the_library_has_a_folder_exits_1_and_keeps_the_file(rig, capsys):
    (rig["card"] / "Music").mkdir()
    write(rig["card"] / "Music/Artist A", "a file")
    before = tree(rig["card"])
    assert ss.main([]) == 1
    assert tree(rig["card"]) == before
    err = capsys.readouterr().err
    assert "Artist A" in err
    assert ss.main(["--dry-run"]) == 1


def test_an_empty_folder_on_the_card_where_the_library_has_a_file_exits_1(rig, capsys):
    write(rig["music"] / "loose.flac", "loose")
    (rig["card"] / "Music/loose.flac").mkdir(parents=True)
    before = tree(rig["card"])
    assert ss.main([]) == 1
    assert tree(rig["card"]) == before
    assert "loose.flac" in capsys.readouterr().err


def test_delete_unlinks_a_symlink_itself_not_what_it_points_at(rig):
    dest = synced(rig)
    (dest / "link.flac").symlink_to(dest / "Artist B/Album 2/01.flac")
    ss.delete(dest, ["link.flac"])
    assert not (dest / "link.flac").is_symlink()
    assert (dest / "Artist B/Album 2/01.flac").is_file()


def test_an_empty_init_argument_is_not_a_sync(rig):
    before = tree(rig["card"])
    assert ss.main(["--init", ""]) == 1
    assert tree(rig["card"]) == before


def test_delete_leaves_a_folder_that_gained_a_file(rig):
    dest = synced(rig)
    write(dest / "Artist B/Album 2/new.flac")
    names = ["Artist B/Album 2/01.flac", "Artist B/Album 2/", "Artist B/"]
    assert ss.delete(dest, names) == 2
    assert (dest / "Artist B/Album 2/new.flac").is_file()
    assert not (dest / "Artist B/Album 2/01.flac").exists()


def test_help_names_init_and_dry_run(capsys):
    with pytest.raises(SystemExit) as stop:
        ss.main(["--help"])
    assert stop.value.code == 0
    out = capsys.readouterr().out
    assert "--init" in out
    assert "--dry-run" in out
