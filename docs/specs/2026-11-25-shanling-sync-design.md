# shanling-sync: mirror the music library to the Shanling Q2's card

Status: approved

Its fresh reader ran on Opus at high, because Fable's weekly limit is used up until Nov 27.

## Intent

Geoff, 2026-11-25: "I'd like to upload my music to a Shanling Q2 player." He first asked for a compressed copy
of the library, then ruled: "I'll just get a 128 GB card and copy the libary in as-is." Asked for a script that
finds the mounted card: "Please do. And I'll probably just plug the whole device in via usb-c if that's an
option." On deletions he picked "Mirror": an album that leaves `~/Music` leaves the card too, after he confirms
the list.

Goals: with the Q2 or its card plugged into pavilion, one command, `shanling-sync`, makes the card's `Music/`
folder match `~/Music`, copying only what changed.

Non-goals: no transcoding, no change to the beets config, no automatic run on plug-in, no playlists, no MTP
transfer.

Failure: a file deleted outside the marked card's `Music/` folder, a deletion Geoff didn't confirm, or a run
that fills the card and stops partway.

## Approaches

1. A stdlib Python script around `rsync` (picked). It parses rsync's dry-run list, which the tool-language rule
   sends to Python rather than Bash.
2. A Bash script around the same `rsync` lines. It's shorter, but parsing the list and summing sizes is the data
   work that rule moves to Python.
3. No script, only the `rsync` line in a doc. Geoff asked for the script, and an unconfirmed `--delete` typed by
   hand is the failure above.

## Design

`bin/.local/bin/shanling-sync`, shebang `#!/usr/bin/python3 -I`, as `fresh-tracks` has. Three environment
variables point a test at scratch folders: `SHANLING_SYNC_MUSIC` (default `~/Music`), `SHANLING_SYNC_MEDIA`
(default `/run/media/$USER`), and `SHANLING_SYNC_GVFS` (default `/run/user/<uid>/gvfs`). Usage:
`shanling-sync [--dry-run]` and `shanling-sync --init <volume>`.

- **The card.** The card is a folder directly under the media root whose top level holds a file named
  `.shanling-sync`. The library goes to `<card>/Music/`. A marker is needed because other drives mount there
  too: today `/run/media/glw907/titanoboa_boot` is a mounted iso9660 USB stick.
- **`--init <volume>`.** Resolves the path. It exits 1 unless the resolved path is a direct child of the
  resolved media root and a mount point (`os.path.ismount`). An existing marker exits 0 with `already marked`.
  A write that fails, such as on a read-only volume, exits 1 with the error.
- **Finding the card.** A media root that doesn't exist counts as no volumes. With no marked card, the script
  exits 1, names the unmarked volumes, and gives the `--init` line. If an `mtp:*` entry exists under the gvfs
  root, it adds that the Q2 is connected as an MTP device, which the script can't write to, and that the Q2's USB
  mode should be storage or the card should go in a card reader. Two or more marked cards exit 1, listing each.
- **The source.** A music folder that is missing or holds no file exits 1 with nothing done, so an empty source
  can never empty the card.
- **The plan.** `rsync -rt --modify-window=1 --delete --dry-run --out-format='%i %l %n' <music>/ <card>/Music/`.
  A line starting `>f` is a copy, and its second field is the file's size in bytes. A line starting `*deleting`
  is a deletion, of a file or a folder (a folder's name ends in `/`). Every other line is ignored, such as
  `.d..t......` for a folder's time or `cd+++++++++` for a new folder. A dry run that exits non-zero ends the
  script with that exit code and nothing done. `-rt` copies no owner, group, or permissions, which exFAT can't
  hold.
- **Space.** The bytes needed are each copy's size rounded up to the card's cluster size (`f_bsize` from
  `os.statvfs`), plus 256 MiB. When that exceeds the free space (`f_bavail * f_frsize`), the script prints both
  figures and exits 1 with nothing done. Space freed by deletions isn't counted.
- **`--dry-run`.** Prints the copy count, the bytes needed, and each deletion, then runs the space check and
  exits 0, or 1 on a shortfall. It changes nothing.
- **Deletions.** When there are any, the script prints every path, files and folders alike, and asks `Delete
  these <n> paths from the card? [y/N]`, where `<n>` counts every printed line. Only `y` or `yes` deletes. Any
  other answer, end of input, Ctrl-C, or stdin that isn't a terminal keeps them, with no traceback. The script
  deletes only the confirmed paths, itself, before the copy: each resolves and must lie under the resolved
  `<card>/Music/`, or the script exits 1 before deleting anything. Files go first, then folders, deepest first,
  with `rmdir`, so a folder that gained a file since the plan stays. Kept paths are counted in the last line.
- **The copy.** `rsync -rt --modify-window=1 --info=progress2 <music>/ <card>/Music/`, without `--delete`, so
  the copy can't remove a path Geoff didn't see. A non-zero rsync exit is the script's exit. After a clean copy
  it calls `os.sync()` and prints `Done. Eject the card before unplugging it.`

## When it goes wrong

- Unplugged mid-copy: rsync exits non-zero. rsync writes each file under a temporary name and renames it when
  done, so no half-written file keeps its real name. A leftover temporary file shows in the next run's deletion
  list.
- The card fills anyway, after Geoff keeps paths he could have deleted: rsync exits 11 (probed below) and the
  script passes it through.
- fresh-tracks imports between the plan and the copy: the copy brings the new album too. Deletion covers only the
  confirmed list, so nothing new is deleted.
- The Q2 writes its own files inside `Music/`: they show in the deletion list on each run until a follow-up adds
  an exclude. Unknown until the device is here.
- The Q2 is MTP-only: the script says so. An MTP path is a follow-up spec once the device is here.
- Limits: a 256 MiB space margin, and a search one level deep under the media root.

## Sources and labels

- `rsync` `-r`, `-t`, `--delete`, `--dry-run`, `--out-format` with `%i %l %n`, and `--info=progress2`:
  documented, rsync(1), version 3.5.2 on pavilion. `--modify-window=1`: documented, "Specifying 1 is useful for
  copies to/from MS Windows FAT filesystems, because FAT represents times with a 2-second resolution" (rsync(1)).
- rsync on exFAT, probed on a 2 GiB image made with `mkfs.exfat` and mounted through `udisksctl loop-setup`
  under `/run/media/glw907/`, with one real artist folder from `~/Music`:
  - A second dry run listed 0 lines, with `--modify-window=1` and without it.
  - A file whose time changed listed as `>f..t...... 992077 Smokers Delight/cover.jpg`.
  - A deleted folder listed as `*deleting   0 Gone/x.flac` and `*deleting   0 Gone/`.
  - `f_bsize` was 32768. A 512 MiB image ran out of space, and rsync exited 11 with `No space left on device`.
- Removable drives mount under `/run/media/$USER/`: probe, `findmnt` shows `/dev/sda1` mounted at
  `/run/media/glw907/titanoboa_boot`, and the test image mounted at `/run/media/glw907/Q2TEST`.
- gvfs exposes its mounts through FUSE under `/run/user/<uid>/gvfs`: probe, `findmnt` shows `gvfsd-fuse`
  mounted there. An MTP device shows in it as `mtp:host=...`: unproven, since no MTP device is attached.
- The Q2 shows its card as a USB drive: unproven, and the least-proven assumption. Its predecessor's manual says
  "The card will be displayed as a new external drive" (Shanling Q1 manual). Reviews list only the Q2's USB DAC
  and audio-out modes. A card reader is the fallback.
- The library copies to exFAT unchanged: probe of `~/Music` found 0 symlinks, 0 names that differ only by
  case, a longest name of 81 bytes, and 0 names holding any of `:?"*<>|\`.

## Files

Searches: `rg -l shanling .` found 0 files. `rg -n 'fresh-tracks' scripts/check.sh` found 1 hit, the pytest
leg's list at line 149, which gains `shanling-sync`. No doc describes copying music off pavilion, so no doc
changes, and the script's docstring carries the usage.

- `bin/.local/bin/shanling-sync` (new)
- `tests/test_shanling_sync.py` (new)
- `scripts/check.sh` (the pytest leg's list)

## Tasks

### Task 1: the script

Name: shanling-sync
Tier: ask
Files: `bin/.local/bin/shanling-sync`, `tests/test_shanling_sync.py`, `scripts/check.sh`

Ask, because `scripts/**` is on the Ask-only list. `standards:diff-reviewer` reads the branch, with
`standards:python-conventions`. Builds on nothing. Minutes: 45 (artist-photos, a larger helper, planned 100 and
measured 43). Model: Sonnet at high. It touches no live card: every test runs against folders under `tmp_path`.
The denials log for the last 30 days holds no refusal of `rsync`, `pytest`, or `gate.sh`.

The tests load the script in-process, as `tests/test_fresh_tracks.py` does, and run the real `rsync`. Three
seams are monkeypatched there: stdin's `isatty` with the answer fed on stdin, the free-space figure through one
function, and `os.path.ismount` for `--init`.

Goal:

1. `bash scripts/gate.sh` passes on the last commit, with `shanling-sync` in the pytest leg's list. Today: passes,
   and `rg -c shanling-sync scripts/check.sh` prints nothing.
2. `uv run --with pytest --no-project python -m pytest tests/test_shanling_sync.py -q` passes, with tests that
   show each of these:
   - A marked card gets the library under `Music/`, and a second run copies nothing.
   - No marked card exits 1 and names an unmarked volume. An `mtp:host=x` folder under the gvfs root adds the MTP
     message. Two marked cards exit 1.
   - `--init` writes the marker, reports an existing one, and exits 1 for a path outside the media root or not a
     mount point.
   - A missing or empty music folder exits 1 and the card is unchanged.
   - `--dry-run` changes no file.
   - The answer `y` deletes a removed album's files and folder. A file on the card beside `Music/` and a file on
     an unmarked volume both survive.
   - The answers `n` and end of input, and stdin that isn't a terminal, keep the album while a new one still
     copies.
   - A free-space figure below the bytes needed exits 1 with nothing copied.
   - A card whose `Music/` folder is read-only passes rsync's non-zero exit through.

   Today: the file doesn't exist.
3. `python3 -I bin/.local/bin/shanling-sync --help` prints the usage, naming `--init` and `--dry-run`. Today:
   the file doesn't exist.

After the merge, Geoff's session runs `stow -R bin` ("After a merge" in `dotfiles-pass`), then
`bash -lic 'shanling-sync --help'`. Today `bash -lic 'command -v shanling-sync'` exits 1.

## Backlog sweep

Scoped sweep of `BACKLOG.md` for `beets`, `music`, `shanling`, `navidrome`, and `rsync`: one hit, #2 (move the
music-VPS docs to household-it). Verdict: keep; it's unrelated to this work.

## Calls Claude made

- Python over Bash, because the script parses rsync's output.
- A marker file over a volume label, because the label the Q2 writes when it formats a card is unknown.
- The script deletes the confirmed paths itself and copies without `--delete`, and a plan that swaps a
  file and a folder is refused, so rsync never deletes a path Geoff didn't see.
- A declined deletion still copies the new files, so one "no" never holds back new albums.
- Space is rounded up per cluster, and space freed by deletions isn't counted, so the check errs toward refusing.
- Files the Q2 may write inside `Music/` wait for the device; they would only show in the deletion list.
- No automatic run on plug-in, which Geoff didn't ask for.
