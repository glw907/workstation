"""Tests for fresh-tracks, the Fresh Tracks share's importer.

Each test imports through the real beet with a scratch config: no plugins, no autotagging, and a
library under tmp_path, so nothing reaches the network or the live library.
"""

import fcntl
import importlib.machinery
import importlib.util
import io
import os
from pathlib import Path
import shutil
import tarfile
import zipfile

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "bin/.local/bin/fresh-tracks"
FIXTURES = ROOT / "tests/fixtures/fresh-tracks"
BEET = Path.home() / ".local/bin/beet"

loader = importlib.machinery.SourceFileLoader("fresh_tracks", str(SCRIPT))
spec = importlib.util.spec_from_loader("fresh_tracks", loader)
ft = importlib.util.module_from_spec(spec)
loader.exec_module(ft)

needs_beet = pytest.mark.skipif(not BEET.exists(), reason="beets isn't installed (uv-tools.txt)")


@pytest.fixture
def box(tmp_path, monkeypatch):
    """Point the importer at a scratch inbox, state folder, and beets config."""
    inbox = tmp_path / "FreshTracks"
    inbox.mkdir()
    beets = tmp_path / "beets"
    beets.mkdir()
    (beets / "config.yaml").write_text(
        f"directory: {tmp_path / 'Music'}\n"
        f"library: {tmp_path / 'library.db'}\n"
        "plugins: []\n"
        "import:\n"
        "  autotag: no\n"
        "  move: yes\n"
        "  write: yes\n"
        "  quiet_fallback: skip\n"
        "  none_rec_action: skip\n"
        "  group_albums: yes\n"
        "  duplicate_action: skip\n"
    )
    monkeypatch.setenv("BEETSDIR", str(beets))
    monkeypatch.setenv("FRESH_TRACKS_INBOX", str(inbox))
    monkeypatch.setenv("FRESH_TRACKS_BEET", str(BEET))
    monkeypatch.setenv("FRESH_TRACKS_QUIET", "0")
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path / "state"))
    return tmp_path


def music(box):
    lib = box / "Music"
    return sorted(str(p.relative_to(lib)) for p in lib.rglob("*.mp3")) if lib.exists() else []


def inbox_names(box):
    return sorted(p.name for p in (box / "FreshTracks").iterdir())


def why(box, label):
    return (box / "FreshTracks" / "Not imported" / label / "WHY.txt").read_text()


def state_log(box):
    return (box / "state/fresh-tracks/log").read_text()


def add_album(dest):
    shutil.copytree(FIXTURES / "album-a", dest)
    (dest / "album.cue").write_text("FILE 01.mp3\n")
    (dest / "rip.log").write_text("ripped\n")


def tar_with(path, members):
    """Write a .tar.gz from (name, data-or-TarInfo) pairs."""
    with tarfile.open(path, "w:gz") as tar:
        for name, data in members:
            if isinstance(data, tarfile.TarInfo):
                tar.addfile(data)
            else:
                info = tarfile.TarInfo(name)
                info.size = len(data)
                tar.addfile(info, io.BytesIO(data))


def album_members(prefix="Album A/"):
    return [(prefix + p.name, p.read_bytes()) for p in sorted((FIXTURES / "album-a").iterdir())]


@needs_beet
def test_folder_imports_and_leftovers_go(box):
    add_album(box / "FreshTracks/Album A")
    assert ft.main() == 0
    assert music(box) == ["Fixture Artist/Album A/01 Track 1.mp3", "Fixture Artist/Album A/02 Track 2.mp3"]
    assert inbox_names(box) == [".fresh-tracks-work"]
    assert list((box / "FreshTracks/.fresh-tracks-work").iterdir()) == []
    assert "Album A: 1 albums imported, 0 skipped." in state_log(box)


@needs_beet
def test_loose_tracks_split_into_albums_by_tags(box):
    for track in (FIXTURES / "loose").iterdir():
        shutil.copy(track, box / "FreshTracks")
    ft.main()
    assert music(box) == ["Second Artist/Album B/01 B Side.mp3", "Third Artist/Album C/01 C Side.mp3"]
    assert inbox_names(box) == [".fresh-tracks-work"]
    assert "Loose tracks: 2 albums imported, 0 skipped." in state_log(box)


@needs_beet
def test_tar_gz_imports_and_is_deleted(box):
    tar_with(box / "FreshTracks/album.tar.gz", album_members())
    ft.main()
    assert len(music(box)) == 2
    assert inbox_names(box) == [".fresh-tracks-work"]


@needs_beet
def test_zip_imports_and_is_deleted(box):
    with zipfile.ZipFile(box / "FreshTracks/album.zip", "w") as z:
        for name, data in album_members():
            z.writestr(name, data)
    ft.main()
    assert len(music(box)) == 2
    assert inbox_names(box) == [".fresh-tracks-work"]


@needs_beet
def test_duplicate_goes_to_not_imported(box):
    add_album(box / "FreshTracks/Album A")
    ft.main()
    add_album(box / "FreshTracks/Album A again")
    ft.main()
    dest = box / "FreshTracks/Not imported/Album A again"
    assert sorted(p.name for p in dest.iterdir()) == ["01.mp3", "02.mp3", "WHY.txt"]
    assert "Album A again: It is already in the library." in why(box, "Album A again")
    assert len(music(box)) == 2
    line = "Album A again: 0 albums imported, 1 skipped, moved to Not imported/Album A again."
    assert line in state_log(box)


@needs_beet
def test_skipped_archive_moves_whole(box):
    add_album(box / "FreshTracks/Album A")
    ft.main()
    tar_with(box / "FreshTracks/again.tar.gz", album_members())
    ft.main()
    dest = box / "FreshTracks/Not imported/again"
    assert sorted(p.name for p in dest.iterdir()) == ["WHY.txt", "again.tar.gz"]
    assert "Album A: It is already in the library." in why(box, "again")


@pytest.mark.parametrize(
    "member, reason",
    [
        (("../escape.mp3", b"x"), 'a path with "..", which would unpack outside its folder: ../escape.mp3'),
        (("/etc/escape.mp3", b"x"), "an absolute path"),
        (("Album/link.mp3", None), "a link: Album/link.mp3"),
        (("Album/fifo", None), "a device or FIFO: Album/fifo"),
        (("Album/bad\nname.mp3", b"x"), "a control character"),
    ],
)
def test_unsafe_tar_member_refuses_the_archive(box, member, reason):
    name, data = member
    if data is None:
        info = tarfile.TarInfo(name)
        if name.endswith("link.mp3"):
            info.type, info.linkname = tarfile.SYMTYPE, "/etc/passwd"
        else:
            info.type = tarfile.FIFOTYPE
        data = info
    archive = box / "FreshTracks/bad.tar.gz"
    tar_with(archive, [*album_members(), (name, data)])
    ft.main()
    dest = box / "FreshTracks/Not imported/bad"
    assert sorted(p.name for p in dest.iterdir()) == ["WHY.txt", "bad.tar.gz"]
    assert reason in why(box, "bad")
    assert not (box / "escape.mp3").exists() and not (box / "FreshTracks/escape.mp3").exists()
    assert music(box) == []


def test_zip_symlink_refuses_the_archive(box):
    with zipfile.ZipFile(box / "FreshTracks/bad.zip", "w") as z:
        for name, data in album_members():
            z.writestr(name, data)
        link = zipfile.ZipInfo("Album A/link.mp3")
        link.external_attr = (0o120777 << 16)
        z.writestr(link, "/etc/passwd")
    ft.main()
    assert "a link: Album A/link.mp3" in why(box, "bad")
    assert (box / "FreshTracks/Not imported/bad/bad.zip").exists()


def test_zip_dotdot_refuses_the_archive(box):
    with zipfile.ZipFile(box / "FreshTracks/bad.zip", "w") as z:
        z.writestr("..\\escape.mp3", "x")
    ft.main()
    assert '"..", which would unpack outside its folder' in why(box, "bad")


def test_archive_too_big_for_free_space(box, monkeypatch):
    monkeypatch.setattr(ft, "free_bytes", lambda path: (1 << 30) + 100)
    tar_with(box / "FreshTracks/big.tar.gz", album_members())
    ft.main()
    assert "too big to unpack" in why(box, "big")
    assert (box / "FreshTracks/Not imported/big/big.tar.gz").exists()
    assert not (box / "FreshTracks/.fresh-tracks-work/1").exists()


def test_damaged_archive_is_refused(box):
    tar_with(box / "FreshTracks/cut.tar.gz", album_members())
    path = box / "FreshTracks/cut.tar.gz"
    path.write_bytes(path.read_bytes()[:60])
    ft.main()
    assert "can't be read" in why(box, "cut")


def test_zip_with_corrupt_data_is_refused(box):
    """A damaged deflate stream raises zlib.error, which must not fail the run."""
    path = box / "FreshTracks/cut.zip"
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("Album A/01.mp3", bytes(range(256)) * 64)
    data = bytearray(path.read_bytes())
    start = 30 + len("Album A/01.mp3")
    data[start:start + 40] = b"\xff" * 40
    path.write_bytes(bytes(data))
    assert ft.main() == 0
    assert "can't be read" in why(box, "cut")
    assert (box / "FreshTracks/Not imported/cut/cut.zip").exists()


@needs_beet
def test_unreadable_audio_and_mac_dot_files(box):
    """Audio beets can't read is set aside; a Mac's ._ file is not counted as skipped music."""
    add_album(box / "FreshTracks/Album A")
    (box / "FreshTracks/Album A/._01.mp3").write_bytes(b"mac")
    (box / "FreshTracks/Album A/bonus.dff").write_bytes(b"dsd")
    ft.main()
    assert len(music(box)) == 2
    dest = box / "FreshTracks/Not imported/Album A"
    assert sorted(p.name for p in dest.iterdir()) == ["WHY.txt", "bonus.dff"]
    assert "beets can't read .dff files." in why(box, "Album A")


@needs_beet
def test_archive_beets_cant_open_is_set_aside(box):
    """A .rar among loose tracks, or a .zip inside a folder, is kept, never deleted."""
    shutil.copy(FIXTURES / "loose/b1.mp3", box / "FreshTracks/b1.mp3")
    (box / "FreshTracks/album.rar").write_bytes(b"Rar!")
    add_album(box / "FreshTracks/Album A")
    (box / "FreshTracks/Album A/bonus.zip").write_bytes(b"PK")
    ft.main()
    assert len(music(box)) == 3
    assert (box / "FreshTracks/Not imported/Loose tracks/album.rar").exists()
    assert "beets can't import a .rar archive" in why(box, "Loose tracks")
    assert (box / "FreshTracks/Not imported/Album A/bonus.zip").exists()


def test_folder_with_a_link_is_refused(box):
    add_album(box / "FreshTracks/Album A")
    os.symlink("/etc/passwd", box / "FreshTracks/Album A/03.mp3")
    ft.main()
    assert "a link or a special file: Album A/03.mp3" in why(box, "Album A")
    assert (box / "FreshTracks/Not imported/Album A/Album A/01.mp3").exists()


@needs_beet
def test_folder_with_no_music_is_kept(box):
    (box / "FreshTracks/Scans").mkdir()
    (box / "FreshTracks/Scans/booklet.pdf").write_text("pdf")
    ft.main()
    assert "It holds no music beets can read." in why(box, "Scans")
    assert (box / "FreshTracks/Not imported/Scans/Scans/booklet.pdf").exists()


def test_file_still_changing_is_not_taken(box, monkeypatch):
    """A write inside the quiet period restarts it, so the wait outlasts the last write."""
    monkeypatch.setenv("FRESH_TRACKS_QUIET", "10")
    cfg = ft.load_config()
    track = cfg.inbox / "copying.mp3"
    track.write_bytes(b"a")
    now = [0.0]
    writes = []

    def sleep(seconds):
        now[0] += seconds
        if now[0] <= 8:  # the copy keeps writing for 8 seconds
            with open(track, "ab") as f:
                f.write(b"a")
            writes.append(now[0])

    ft.wait_quiet(cfg, sleep=sleep, clock=lambda: now[0])
    assert writes and now[0] >= writes[-1] + 10


def test_quiet_inbox_returns_after_the_period(box, monkeypatch):
    monkeypatch.setenv("FRESH_TRACKS_QUIET", "10")
    cfg = ft.load_config()
    (cfg.inbox / "done.mp3").write_bytes(b"a")
    now = [0.0]
    ft.wait_quiet(cfg, sleep=lambda s: now.__setitem__(0, now[0] + s), clock=lambda: now[0])
    assert 10 <= now[0] < 11


@needs_beet
def test_crashed_run_moves_back_and_imports(box):
    work = box / "FreshTracks/.fresh-tracks-work"
    add_album(work / "1/src/Album A")
    (work / "1/unpacked").mkdir()
    (work / "1/import.log").write_text("import started\n")
    cfg = ft.load_config()
    cfg.state.mkdir(parents=True)
    ft.recover(cfg)
    assert inbox_names(box) == [".fresh-tracks-work", "Album A"]
    assert list(work.iterdir()) == []
    ft.main()
    assert len(music(box)) == 2


def test_crash_while_setting_aside_moves_back(box):
    """A crash after the move into aside/ loses nothing: the next run returns it to the inbox."""
    work = box / "FreshTracks/.fresh-tracks-work"
    add_album(work / "1/aside/Album A")
    (work / "1/aside/WHY.txt").write_text(ft.WHY_HEADER + "Album A: a reason\n")
    cfg = ft.load_config()
    cfg.state.mkdir(parents=True)
    ft.recover(cfg)
    assert inbox_names(box) == [".fresh-tracks-work", "Album A"]
    assert (box / "FreshTracks/Album A/01.mp3").exists()


def test_second_run_exits_at_once(box):
    cfg = ft.load_config()
    cfg.state.mkdir(parents=True)
    add_album(cfg.inbox / "Album A")
    with open(cfg.state / "lock", "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        assert ft.main() == 0
    assert inbox_names(box) == ["Album A"]


def test_covers_parses_the_coverrule_report():
    out = "noise\nCovers outside the rule:\n  Artist - Album: 640 px\n  Other - Two: none\ndone\n"
    assert ft.covers(out) == ["Artist - Album: 640 px", "Other - Two: none"]


def test_folder_swapped_for_a_link_after_gather_is_refused(box):
    """A folder a client replaces with a link while earlier items import is never followed."""
    outside = box / "Videos"
    add_album(outside)
    cfg = ft.load_config()
    cfg.state.mkdir(parents=True)
    cfg.work.mkdir()
    add_album(cfg.inbox / "Album B")
    [item] = ft.gather(ft.pending(cfg))
    shutil.rmtree(cfg.inbox / "Album B")
    os.symlink(outside, cfg.inbox / "Album B")
    ft.process(cfg, item, cfg.work / "1", None)
    assert sorted(p.name for p in outside.iterdir()) == ["01.mp3", "02.mp3", "album.cue", "rip.log"]
    assert "a link or a special file: Album B" in why(box, "Album B")
    assert (cfg.not_imported / "Album B/Album B").is_symlink()


def test_not_imported_as_a_link_is_moved_aside(box):
    """A link named Not imported is moved away, so nothing is written through it."""
    elsewhere = box / "elsewhere"
    elsewhere.mkdir()
    cfg = ft.load_config()
    os.symlink(elsewhere, cfg.not_imported)
    add_album(cfg.inbox / "Album A")
    os.symlink("/etc/passwd", cfg.inbox / "Album A/03.mp3")
    ft.main()
    assert list(elsewhere.iterdir()) == []
    assert cfg.not_imported.is_dir() and not cfg.not_imported.is_symlink()
    assert "a link or a special file" in why(box, "Album A")
    assert (cfg.not_imported / "Loose tracks/Not imported (moved)").is_symlink()


def test_set_aside_skips_a_name_a_client_planted(box):
    """A link planted at the set-aside folder's name is passed over, and its target untouched."""
    victim = box / "victim"
    victim.mkdir()
    cfg = ft.load_config()
    cfg.state.mkdir(parents=True)
    cfg.not_imported.mkdir()
    os.symlink(victim, cfg.not_imported / "Album A")
    add_album(cfg.inbox / "Album A")
    os.symlink("/etc/passwd", cfg.inbox / "Album A/03.mp3")
    ft.main()
    assert list(victim.iterdir()) == []
    assert "a link or a special file" in why(box, "Album A (2)")


def test_hard_link_and_control_character_are_refused(box):
    add_album(box / "FreshTracks/Album A")
    os.link(box / "FreshTracks/Album A/01.mp3", box / "linked.mp3")
    (box / "FreshTracks/Bad\nName").mkdir()
    (box / "FreshTracks/Bad\nName/01.mp3").write_bytes(b"x")
    ft.main()
    assert "a hard link: Album A/01.mp3" in why(box, "Album A")
    assert "a control character in it: Bad?Name" in why(box, "Bad?Name")
    assert "Bad\nName" not in state_log(box)


def test_plain_tar_ending_in_zeros_is_refused(box):
    """A plain tar whose copy stalled ends in zeros and must not import as complete."""
    path = box / "FreshTracks/stalled.tar"
    with tarfile.open(path, "w") as tar:
        for name, data in album_members():
            info = tarfile.TarInfo(name)
            info.size = len(data)
            tar.addfile(info, io.BytesIO(data))
    with open(path, "ab") as f:
        f.write(bytes(3 * tarfile.RECORDSIZE))
    ft.main()
    assert "its copy may not have finished" in why(box, "stalled")


@needs_beet
def test_item_that_changes_after_the_wait_waits(box, monkeypatch):
    """An item written to while earlier items import waits for the next quiet period."""
    real = ft.wait_quiet
    calls = []

    def wait(cfg):
        seen = real(cfg)
        if not calls:
            (cfg.inbox / "Album A/rip.log").write_text("still ripping, longer now\n")
        calls.append(1)
        return seen

    monkeypatch.setattr(ft, "wait_quiet", wait)
    add_album(box / "FreshTracks/Album A")
    ft.main()
    log = state_log(box)
    assert "Album A: still changing, so it waits for the next quiet period." in log
    assert "Album A: 1 albums imported, 0 skipped." in log
    assert len(calls) == 2


def test_work_folder_as_a_link_is_removed(box):
    """A link at the work folder's name is removed, and the folder it points at is untouched."""
    outside = box / "Documents"
    (outside / "1/src").mkdir(parents=True)
    (outside / "1/src/notes.txt").write_text("mine\n")
    os.symlink(outside, box / "FreshTracks/.fresh-tracks-work")
    cfg = ft.load_config()
    cfg.state.mkdir(parents=True)
    ft.recover(cfg)
    assert (outside / "1/src/notes.txt").read_text() == "mine\n"
    assert inbox_names(box) == []


def test_failed_item_goes_back_and_the_next_imports(box, monkeypatch):
    """An error on one item returns it to the inbox and fails the run; the items after it run."""
    real = ft.check_links

    def check(target):
        if (target / "Album A").exists():
            raise UnicodeEncodeError("utf-8", "x", 0, 1, "planted")
        real(target)

    monkeypatch.setattr(ft, "check_links", check)
    add_album(box / "FreshTracks/Album A")
    (box / "FreshTracks/Scans").mkdir()
    (box / "FreshTracks/Scans/booklet.pdf").write_text("pdf")
    os.symlink("/etc/passwd", box / "FreshTracks/Scans/link")
    assert ft.main() == 1
    assert (box / "FreshTracks/Album A/01.mp3").exists()
    assert not (box / "FreshTracks/Not imported/Album A").exists()
    assert "Album A: the importer failed on it, and what is left" in state_log(box)
    assert "UnicodeEncodeError" in state_log(box)
    assert "a link or a special file" in why(box, "Scans")


def test_failed_set_aside_keeps_the_item(box):
    """A set-aside that fails after its files left src/ returns them to the inbox, deleting none."""
    scans = box / "FreshTracks/Scans"
    scans.mkdir()
    (scans / "booklet.pdf").write_text("pdf")
    os.symlink("/etc/passwd", scans / "link")
    (box / "FreshTracks/Not imported").mkdir(mode=0o500)
    try:
        assert ft.main() == 1
    finally:
        (box / "FreshTracks/Not imported").chmod(0o700)
    assert (scans / "booklet.pdf").read_text() == "pdf"
    assert (scans / "link").is_symlink()
    assert list((box / "FreshTracks/.fresh-tracks-work").iterdir()) == []
    assert state_log(box).count("Scans: the importer failed on it, and what is left") == 1


@needs_beet
def test_skipped_track_with_an_odd_suffix_is_kept(box):
    """beets reads a track by its header, so a skipped .m4p or a renamed MP3 is set aside, not deleted."""
    add_album(box / "FreshTracks/Album A")
    assert ft.main() == 0
    again = box / "FreshTracks/Album A again"
    add_album(again)
    (again / "02.mp3").rename(again / "02.m4p")
    (again / "booklet.txt").write_text("notes")
    assert ft.main() == 0
    kept = box / "FreshTracks/Not imported/Album A again"
    assert sorted(p.name for p in kept.iterdir()) == ["01.mp3", "02.m4p", "WHY.txt"]


def test_header_marks_audio_by_any_name(tmp_path):
    """A file's first bytes, not its suffix, say whether it may be music."""
    mp3 = next((FIXTURES / "album-a").glob("*.mp3"))
    (tmp_path / "track.bin").write_bytes(mp3.read_bytes())
    (tmp_path / "notes.cue").write_text("FILE track.bin MP3")
    assert ft.leftover_audio(tmp_path, []) == [tmp_path / "track.bin"]


def test_dropped_why_txt_is_kept(box):
    """A loose WHY.txt a client dropped is set aside under another name, not overwritten."""
    (box / "FreshTracks/WHY.txt").write_text("my notes")
    os.symlink("/etc/passwd", box / "FreshTracks/link.mp3")
    assert ft.main() == 0
    kept = box / "FreshTracks/Not imported/Loose tracks/WHY (dropped).txt"
    assert kept.read_text() == "my notes"


def test_name_that_isnt_utf8_is_written_escaped(box):
    """A Latin-1 folder name from an old rip is refused or set aside without a crash."""
    name = os.fsdecode(b"Caf\xe9")
    add_album(box / "FreshTracks" / name)
    os.symlink("/etc/passwd", box / "FreshTracks" / name / "03.mp3")
    assert ft.main() == 0
    assert "a link or a special file: Caf?/03.mp3" in why(box, "Caf?")


@needs_beet
def test_locked_folder_imports(box):
    """A folder and a file its owner can't use get their owner bits back, and import."""
    locked = box / "FreshTracks/Locked"
    add_album(locked)
    (locked / "02.mp3").chmod(0o200)
    (locked / "Disc").mkdir()
    (locked / "Disc").chmod(0)
    locked.chmod(0o400)
    assert ft.main() == 0
    assert len(music(box)) == 2
    assert inbox_names(box) == [".fresh-tracks-work"]


def test_item_that_fails_and_cant_move_is_tried_once(box, monkeypatch):
    """An item that fails before it leaves the inbox waits for the next run, not a loop."""
    monkeypatch.setattr(ft, "unlock", lambda path: (_ for _ in ()).throw(OSError("planted")))
    add_album(box / "FreshTracks/Album A")
    assert ft.main() == 1
    assert "Album A" in inbox_names(box)
    assert state_log(box).count("Album A: the importer failed on it, and what is left") == 1
    assert not (box / "FreshTracks/Not imported").exists()


def test_long_name_set_aside_twice(box):
    """A 250-byte folder name set aside a second time is shortened to fit the numbered name."""
    name = "x" * 250
    (box / "FreshTracks/Not imported" / name).mkdir(parents=True)
    add_album(box / "FreshTracks" / name)
    os.symlink("/etc/passwd", box / "FreshTracks" / name / "03.mp3")
    assert ft.main() == 0
    assert "a link or a special file" in why(box, "x" * 240)
