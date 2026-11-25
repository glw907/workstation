"""Hold every album cover to one rule: cover.jpg, at most 1500 px, under 1 MB."""

import datetime
import os
import shutil
from pathlib import Path

from PIL import Image

from beets import ui
from beets.plugins import BeetsPlugin, find_plugins

LONG_SIDE = 1500
FLOOR = 1000
MAX_BYTES = 1_000_000
# Same measure as fetchart's enforce_ratio: edge difference over the long edge.
RATIO = 0.15
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".tif", ".tiff"}
ORIGINALS = Path.home() / ".local/share/music-cover-originals"


def _images(folder: Path) -> list[Path]:
    if not folder.is_dir():
        return []
    return [
        p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in IMAGE_EXTS
    ]

# Pillow picks a decoder by content, and its EPS decoder runs Ghostscript, so a cover is
# opened only as a raster format.
RASTER = ["JPEG", "PNG", "WEBP", "GIF", "BMP", "TIFF"]


def _size(path: Path) -> tuple[int, int]:
    try:
        with Image.open(path, formats=RASTER) as im:
            return im.size
    except OSError:
        return (0, 0)


def _conform(path: Path) -> Path:
    """Rewrite the cover as cover.jpg within the size rule; return its new path."""
    with Image.open(path, formats=RASTER) as im:
        if (
            im.format == "JPEG"
            and path.name == "cover.jpg"
            and max(im.size) <= LONG_SIDE
            and path.stat().st_size <= MAX_BYTES
        ):
            return path
        # fetchart's ImageMagick resize caps width only, so a tall cover
        # passes 1500 px in height; thumbnail caps the long side, never upscales.
        im.thumbnail((LONG_SIDE, LONG_SIDE), Image.Resampling.LANCZOS)
        rgb = im.convert("RGB")
    target = path.with_name("cover.jpg")
    tmp = path.with_name(".cover.jpg.tmp")
    for quality in range(90, 55, -5):
        rgb.save(tmp, "JPEG", quality=quality, optimize=True)
        if tmp.stat().st_size <= MAX_BYTES:
            break
    os.replace(tmp, target)
    if target != path:
        path.unlink(missing_ok=True)
    return target


class CoverRulePlugin(BeetsPlugin):
    def __init__(self):
        super().__init__()
        self.report: list[str] = []
        self.register_listener("art_set", self.on_art_set)
        self.register_listener("import_task_files", self.on_import_files)
        self.register_listener("cli_exit", self.print_report)

    def commands(self):
        cmd = ui.Subcommand(
            "covers",
            help="back up, refetch, and size each album's cover by the cover rule",
        )
        cmd.func = self.covers
        return [cmd]

    def on_art_set(self, album):
        path = Path(os.fsdecode(album.artpath))
        new = _conform(path)
        if new != path:
            album.artpath = os.fsencode(new)

    def on_import_files(self, session, task):
        # Runs after fetchart's own import_task_files listener, because this
        # plugin is listed after it. When nothing online or in the folder met
        # the 1000 px floor, keep the best image the folder had.
        album = getattr(task, "album", None)
        if not task.is_album or album is None:
            return
        if not self._has_art(album):
            # group_albums tasks can carry no paths; old_paths holds each
            # track's file as it was before the move, so its folder is the source.
            sources = [Path(os.fsdecode(p)) for p in task.paths]
            sources += [
                Path(os.fsdecode(p)).parent
                for p in getattr(task, "old_paths", None) or []
            ]
            # An empty or unreadable image sizes as (0, 0) and can't be a cover.
            found = [
                img
                for d in dict.fromkeys(sources)
                for img in _images(d)
                if _size(img) != (0, 0)
            ]
            if found:
                # Album.set_art would send art_set back into this plugin
                # mid-event, which beets refuses, so copy and conform here.
                best = max(found, key=lambda p: max(_size(p)))
                dest = Path(os.fsdecode(album.path)) / f"cover{best.suffix.lower()}"
                shutil.copy2(best, dest)
                try:
                    album.artpath = os.fsencode(_conform(dest))
                except OSError:
                    # A truncated image reads its size but fails to decode.
                    dest.unlink(missing_ok=True)
                else:
                    album.store()
        self._check(album)

    def covers(self, lib, opts, args):
        fetchart = next(p for p in find_plugins() if p.name == "fetchart")
        libdir = Path(os.fsdecode(lib.directory))
        stamp = datetime.date.today().isoformat()
        for album in lib.albums(ui.decargs(args) if hasattr(ui, "decargs") else args):
            folder = Path(os.fsdecode(album.path))
            dest = ORIGINALS / stamp / folder.relative_to(libdir)
            for img in _images(folder):
                if not (dest / img.name).exists():
                    dest.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(img, dest / img.name)
            candidate = fetchart.art_for_album(album, [album.path])
            if candidate:
                album.set_art(candidate.path, False)
            elif not self._has_art(album) and (found := _images(folder)):
                album.artpath = os.fsencode(max(found, key=lambda p: max(_size(p))))
            if self._has_art(album):
                self.on_art_set(album)
                # Navidrome takes any cover.* or folder.*, so a stray cover.png
                # beside the new cover.jpg could win. The backup above holds it.
                keep = Path(os.fsdecode(album.artpath))
                for img in _images(folder):
                    if img != keep:
                        img.unlink()
            album.store()
            ui.print_(f"{album.albumartist} - {album.album}: {self._describe(album)}")
            self._check(album)

    @staticmethod
    def _has_art(album) -> bool:
        return bool(album.artpath) and os.path.isfile(album.artpath)

    def _describe(self, album) -> str:
        if not self._has_art(album):
            return "no cover"
        path = Path(os.fsdecode(album.artpath))
        w, h = _size(path)
        return f"{path.name} {w}x{h} {path.stat().st_size // 1000} KB"

    def _check(self, album):
        name = f"{album.albumartist} - {album.album}"
        if not self._has_art(album):
            self.report.append(f"{name}: no cover found anywhere")
            return
        w, h = _size(Path(os.fsdecode(album.artpath)))
        if max(w, h) < FLOOR:
            self.report.append(
                f"{name}: best cover is {w}x{h}, under the {FLOOR} px floor"
            )
        elif (max(w, h) - min(w, h)) > RATIO * max(w, h):
            self.report.append(
                f"{name}: kept a {w}x{h} cover, more than 15% off square"
            )

    def print_report(self, lib):
        if self.report:
            ui.print_("Covers outside the rule:")
            for line in dict.fromkeys(self.report):
                ui.print_(f"  {line}")
