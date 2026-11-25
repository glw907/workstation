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
def test_loose_file_beets_skips_is_kept(box):
    for track in (FIXTURES / "loose").iterdir():
        shutil.copy(track, box / "FreshTracks")
    (box / "FreshTracks/Album.rar").write_bytes(b"Rar!\x1a\x07\x00")
    ft.main()
    assert len(music(box)) == 2
    kept = box / "FreshTracks/Not imported/Loose tracks"
    assert sorted(p.name for p in kept.iterdir()) == ["Album.rar", "WHY.txt"]
    assert "Album.rar" in why(box, "Loose tracks")


@needs_beet
def test_archive_inside_a_folder_is_kept(box):
    add_album(box / "FreshTracks/Album A")
    (box / "FreshTracks/Album A/Disc 2.zip").write_bytes(b"PK\x05\x06" + bytes(18))
    (box / "FreshTracks/Album A/Bonus.rar").write_bytes(b"Rar!\x1a\x07\x00")
    ft.main()
    assert len(music(box)) == 2
    kept = box / "FreshTracks/Not imported/Album A"
    assert sorted(p.name for p in kept.iterdir()) == ["Bonus.rar", "Disc 2.zip", "WHY.txt"]
    assert "Disc 2.zip" in why(box, "Album A")


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
    assert "Album A again: 0 albums imported, 1 skipped, moved to Not imported/Album A again." in state_log(box)


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


@pytest.mark.parametrize("name", ["bad.zip", "bad.tar.xz"])
def test_corrupt_compressed_archive_is_refused(box, name):
    # zlib.error and lzma.LZMAError aren't OSErrors, so each needs a case of its own.
    path = box / "FreshTracks" / name
    member = "Album A/01.mp3"
    data = b"".join(b"%08d" % i for i in range(40000))
    if name.endswith(".zip"):
        with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
            z.writestr(member, data)
        # The deflate stream starts after the 30-byte local header and the name.
        at = 30 + len(member)
    else:
        with tarfile.open(path, "w:xz") as tar:
            info = tarfile.TarInfo(member)
            info.size = len(data)
            tar.addfile(info, io.BytesIO(data))
        at = path.stat().st_size // 2
    raw = bytearray(path.read_bytes())
    raw[at : at + 8] = b"\xff" * 8
    path.write_bytes(bytes(raw))
    assert ft.main() == 0
    assert "damaged or incomplete" in why(box, name.split(".")[0])


def test_folder_with_a_link_is_refused(box):
    add_album(box / "FreshTracks/Album A")
    os.symlink("/etc/passwd", box / "FreshTracks/Album A/03.mp3")
    ft.main()
    assert "a link or a special file: 03.mp3" in why(box, "Album A")
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
