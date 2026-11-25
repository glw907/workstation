# Fresh Tracks: an inbox share for new music

Status: approved

## Intent

Geoff, 2026-11-24: "share a folder for incoming music. The folder can be called Fresh Tracks. This machine will
watch the folder, move in any new music using beets, and rescan with navidrome."

His rulings the same day:

- The `music` share turns read-only once Fresh Tracks exists, so new music arrives only through beets. Later the
  same day: "Going forward, we only need the Fresh Tracks share. The Music share can go away." So `[music]` is
  removed, and `Fresh Tracks` is pavilion's one share.
- Music beets won't import moves to `Fresh Tracks/Not imported/`, with a note saying why. Skipped music is never
  deleted.
- Archives (`.zip`, `.tar`, `.tar.gz`, `.tgz`, `.tar.xz`, `.tar.bz2`) are checked, unpacked, and imported. After a
  clean import the archive is deleted; if anything in it was skipped, the archive moves to `Not imported/` instead.
- After a folder imports cleanly, whatever beets left in it (a `.cue`, a rip log, booklet scans) is deleted with
  the folder.
- "This isn't a long-term solutions, so python/bash is fine." The importer is a small script, built to be thrown
  away, and nothing here is sized for growth.

Goals: Oliver or Geoff drops an album folder, loose tracks, or an archive into the `Fresh Tracks` share from a
laptop, and minutes later it plays in Navidrome, tagged by MusicBrainz and holding a cover by the cover rule.

Non-goals: no desktop notice (calm desktop), no web page, no second library, no change to Navidrome's settings.

Failure: an album lands in `~/Music` half-copied, an unsafe archive member is written outside the work folder, or the watcher stops watching and nobody can tell.

## Approaches

1. A systemd path unit that starts a one-shot importer (picked). `PathChanged=` on the inbox folder starts
   `fresh-tracks.service`, which waits for the inbox to go quiet, imports, and exits. Documented
   (`systemd.path(5)`). It runs only when something arrives.
2. A long-running watcher daemon (inotify through a library). Recursive watching, but a new dependency and a
   process that runs all day for a few drops a month.
3. A timer every 15 minutes. Simplest, but a drop waits up to 15 minutes, and each run starts beets for nothing.

## Design

- **Folder.** `~/Fresh Tracks` on pavilion, mode 0750. It gets the `samba_share_t` label the way `~/Music` does
  (`etc-drift.md`, the Samba entry): `semanage fcontext -a -t samba_share_t '/var/home/glw907/Fresh[[:space:]]Tracks(/.*)?'`,
  then `restorecon -R`. Probe today: `matchpathcon /var/home/glw907/Fresh Tracks` gives `user_home_t`.
  `check-drift`'s label check moves from `~/Music` to `~/Fresh Tracks`, since no share reads `~/Music` now.
  The `~/Music` fcontext rule stays: it costs nothing, and imported files carry that label anyway.
- **Share.** A `[Fresh Tracks]` section in `bluefin/etc/samba/smb.conf.pavilion`: path
  `/var/home/glw907/Fresh Tracks`, `valid users = oliver glw907`, `read only = no`, `force user` and
  `force group = glw907`, `create mask = 0644`, `directory mask = 0755`, `hide dot files = yes`,
  `veto files = /.fresh-tracks-work/`, and the `hosts allow` the `[music]` section uses today. The `[music]`
  section is removed, with its comments.
- **Units.** `systemd/.config/systemd/user/fresh-tracks.path` (`PathChanged=%h/Fresh Tracks`, `MakeDirectory=yes`,
  `DirectoryMode=0750`) and `fresh-tracks.service` (`Type=oneshot`, `ConditionHost=pavilion`,
  `ExecStart=%h/.local/bin/fresh-tracks`, `WantedBy=default.target`). `PathChanged=` sees only the top folder,
  which is enough: each drop creates or closes a top-level entry. It doesn't fire for entries present at start
  ("Something similar does not apply to PathChanged=", `systemd.path(5)`), so the service also runs once at
  login and sweeps whatever is waiting.
- **Script.** `bin/.local/bin/fresh-tracks`, stdlib Python with the shebang `#!/usr/bin/python3 -I` (the login
  shell's `python3` is Homebrew's). The user manager's `PATH` lacks `~/.local/bin` (probe: `systemctl --user
  show-environment` prints `PATH=/usr/lib64/ccache:/usr/local/sbin:/usr/local/bin:/usr/bin`), so the script calls
  `~/.local/bin/beet` by full path. A test overrides the beet path, the inbox, and the quiet period through
  environment variables. One run:
  1. Takes an `fcntl` lock on `~/.local/state/fresh-tracks/lock`; a second run exits 0 at once.
  2. Moves anything left in `.fresh-tracks-work/` by a crashed run back to the inbox top level.
  3. Waits until nothing under the inbox (except `Not imported/`) changes size or mtime for 10 minutes. It
     re-sweeps after each batch and exits when the inbox holds only `Not imported/`, so a drop that arrives
     mid-run is taken in the same run.
  4. Each top-level folder or archive is one item. All loose top-level files gather into one item, so beets'
     `group_albums: yes` splits them into albums by their tags instead of one-track albums `-q` would skip.
  5. An archive is opened with `tarfile` or `zipfile` and refused whole on any absolute path, `..` part, link,
     device, FIFO, or control character, and when its unpacked size plus 1 GiB exceeds the free space. Otherwise
     it unpacks into `~/Fresh Tracks/.fresh-tracks-work/<item>/`, with `tarfile`'s `data` filter. A folder or
     loose files move into that work folder by rename, on the inbox's file system, so beets' move into
     `~/Music` is a rename too. Dot-named, it doesn't retrigger the path unit ("files whose name starts with a dot ... are generally
     ignored", `systemd.path(5)`), and the share vetoes it.
  6. Runs `~/.local/bin/beet import -q -l <work>/import.log <work>/<item>` with the live config, and keeps its
     stdout. beets moves what it imports and leaves what it skips, so audio still in the work folder is the
     test of a skip, and the log only names the reason. In the log, `skip` means no confident MusicBrainz match.
     A duplicate of an album already in the library logs `duplicate-keep` even though `duplicate_action: skip`
     leaves its files in place, because `log_choice` tests the choice before the skip (beets 2.14.1,
     `importer/session.py`; probe: Oliver's import, 2026-11-24, logged 20 `duplicate-keep` lines, and all 20
     albums' files stayed in staging). Treat `duplicate-keep`, `duplicate-skip`, and `duplicate-replace` as
     "already in the library".
  7. Audio left in a folder item moves to `Not imported/<item>/`, with `WHY.txt` naming each skipped folder and
     its reason in plain words; the item's other leftovers are deleted. A skipped archive item moves whole to
     `Not imported/` with its `WHY.txt`, and its unpacked files are deleted. A refused or unreadable archive goes
     there whole with its reason. A clean item's work folder is deleted, archive included.
  8. Appends one line per item to `~/.local/state/fresh-tracks/log` and to the journal: albums imported, albums
     skipped, and the "Covers outside the rule:" lines from beets' stdout (the coverrule plugin prints them at
     exit).
- **Rescan.** Navidrome 0.64.2 already watches `~/Music` and rescans changed folders on its own (journal,
  2026-11-24 09:31:47: `Watcher: Triggering scan for changed folders`). The importer makes no API call, so no
  Navidrome credential reaches a unit.

## When it goes wrong

| Case | What happens | Limit |
| --- | --- | --- |
| A copy stalls longer than the quiet period | The partial item imports or is refused; a partial archive fails its check and goes to `Not imported/` | 10 min quiet |
| An archive bigger than the free disk | Refused before unpacking, to `Not imported/` with that reason | 1 GiB headroom |
| beets or the script crashes | The service fails, and `systemctl --user status fresh-tracks` shows it; the next run moves work-folder leftovers back first | none |
| The path unit trips its trigger limit | It stops watching; `systemctl --user is-active fresh-tracks.path` reads `failed` | 200 per 2 s (systemd default) |
| Someone runs `beet` by hand mid-import | SQLite's lock makes one wait | beets' timeout |

## Sources and labels

- Path units, `PathChanged=`, dot files ignored, the trigger limit: documented, `systemd.path(5)`, quoted above.
- `beet import -q -l`: documented, beets CLI reference; the log tags probed in `beets/importer/session.py` 2.14.1.
- Navidrome's watcher: documented (`Scanner.WatcherWait`, Navidrome configuration options) and probed in the
  journal above.
- Samba `read only`, `veto files`, `hide dot files`: documented, `smb.conf(5)`.
- `semanage fcontext` and `restorecon`: documented, Red Hat SELinux guide, "Maintaining SELinux labels"; the
  `~/Music` setup is the probe.
- `tarfile` `data` filter: documented, Python 3.14 `tarfile` "Extraction filters"; probed (`/usr/bin/python3`
  3.14.8 has `tarfile.data_filter`).
- The 10-minute quiet period: invented; an SMB copy updates mtime as it writes (probe: Oliver's 7.3 GB archive's
  mtime tracked the clock during its copy).

Assumption more than one step rests on: an SMB copy keeps updating mtime until it closes, so the quiet period
sees a copy in progress. Least proven; the probe above covers one large file, and goal item 2's quiet-period test
covers the script's side.

## Files

Searches: `rg -l --hidden 'navidrome|beets' systemd bin bluefin` (4 hits: `navidrome.service`, kept as the unit
model; `Brewfile`, `stow-packages.txt`, `uv-tools.txt`, dismissed, no change needed). `rg -n '^\[' bluefin/etc/samba/smb.conf.pavilion`
(2 hits, `[global]` and `[music]`). `rg -n 'Music carries samba_share_t' bin/.local/bin/check-drift` (1 hit, the
label check to copy). `rg -n pytest scripts/check.sh` (1 hit, line 149's list).

- `bin/.local/bin/fresh-tracks` (new), `tests/test_fresh_tracks.py` (new), `scripts/check.sh` (pytest list).
- `systemd/.config/systemd/user/fresh-tracks.{path,service}` (new).
- `bluefin/etc/samba/smb.conf.pavilion`, `claude/.claude/docs/bluefin-admin/etc-drift.md` (its Samba entry),
  `bin/.local/bin/check-drift` (the label check).
- household-it: `docs/systems/workstations.md` (task 2).

Commands each task runs (`testparm`, `systemd-analyze --user verify`, `beet` with a scratch config, pytest) show
no hit in the last 30 days of `~/.local/state/claude-denials.jsonl` (0 of 160 lines).

## Tasks

Start conditions: Oliver's current archive import is finished, workstation#278 (the cover rule) and
household-it#50 (the music share) have merged, and the dotfiles main checkout is pulled, since `~/.config/beets`
links into it and task 1 imports through that config.

### Task 1: the inbox share and its watcher

Name: fresh-tracks
Tier: ask
Files: `bin/.local/bin/fresh-tracks`, `bin/.local/bin/check-drift`, `tests/test_fresh_tracks.py`, `scripts/check.sh`, `systemd/.config/systemd/user/fresh-tracks.*`, `bluefin/etc/samba/smb.conf.pavilion`, `claude/.claude/docs/bluefin-admin/etc-drift.md`

Ask because `bluefin/**`, `scripts/**`, and `check-drift` are on the Ask-only list. `check-drift` is a secrets
path, so `standards:web-auth-security-reviewer` reads it beside `standards:diff-reviewer` (with
`standards:python-conventions`), and the pull request is flagged for Geoff. Builds on nothing. Minutes: 80
(workstation median actual path 41.5, p90 145, `task-report` 2026-11-24; this task has a fixture library and two
units). Model: Opus at high.

The task session changes nothing live. The merging session installs it under `## Before merge`: install the
smb.conf, `testparm -s`, `systemctl reload smb`, the `semanage fcontext` rule and `restorecon`, `stow -R bin
systemd`, `systemctl --user daemon-reload`, `systemctl --user enable fresh-tracks.service`, and
`systemctl --user enable --now fresh-tracks.path`.

Goal:

1. `bash scripts/gate.sh` passes on the last commit. Today: passes, without the new leg.
2. `uv run --with pytest --no-project python -m pytest tests/test_fresh_tracks.py -q` passes. Its scratch beets
   config sets no plugins, `import.autotag: no`, and a `library` and `directory` under `tmp_path`, so no test
   reaches the network. The tests import a fixture album folder, loose tracks of two albums, a fixture
   `.tar.gz`, and a fixture `.zip`, and they send each of these to `Not imported/` with a `WHY.txt` naming the
   reason: a duplicate, an archive with a `..` member, an archive with a symlink, and an archive too big for the
   free space (through a stubbed free-space reading). One test shows a file still changing inside the quiet
   period isn't taken, and one shows a crashed run's work folder moves back. Today: the file doesn't exist.
3. For each setting under "Share", `testparm -s --section-name=<section> --parameter-name=<name>
   bluefin/etc/samba/smb.conf.pavilion` prints the spec's value; a test or the PR quotes each run. Today:
   `--section-name='Fresh Tracks'` finds no section. And `testparm -s bluefin/etc/samba/smb.conf.pavilion`
   prints no `[music]` section. Today: it prints `[music]`.
4. `systemd-analyze --user verify systemd/.config/systemd/user/fresh-tracks.path` prints nothing. The service
   file isn't verified in the task session, because its `ExecStart` exists only after the stow. Today: the file
   doesn't exist.
5. The PR's `## Before merge` lists the install commands above and one check: as `oliver` through
   `smbclient //127.0.0.1/Fresh\ Tracks` (credential `Music share (oliver)`), a fixture album copied in shows in
   `~/Music` and in Navidrome's `getAlbumList2` (credential `Navidrome (pavilion)`, vault `Infrastructure`) within
   15 minutes, and `smbclient -L //127.0.0.1` as `oliver` lists `Fresh Tracks` and no `music`.

### Task 2: the runbook page

Name: fresh-tracks-runbook
Tier: ask
Files: `docs/systems/workstations.md`

household-it, which has no Ask-only list, so Ask. Its repo is private and runs no CI, so its local gate stands
in. Builds on task 1 (it documents what merged). Reviewers: `standards:diff-reviewer`. Minutes: 20. Model:
Sonnet at medium.

Goal:

1. `docs/systems/workstations.md` says how to drop music into `Fresh Tracks`, where skipped music goes and how
   to read `WHY.txt`, that the `music` share is gone and Navidrome is the way to play the library, and how to check the watcher
   (`systemctl --user status fresh-tracks.path`), in the voice of `docs/contributing.md`. Today: none of it.
2. `bash scripts/check.sh < /dev/null` passes. Today: passes.

Merge order: task 1, then task 2.

## Backlog sweep

Scoped sweep (`music|beets|navidrome|samba|smb` in both backlogs): workstation #2 (move the music-VPS docs from
dubplate) keep, unrelated; household-it #11 already done. No edits.

## Calls Claude made

- A path unit over a daemon or a timer.
- Navidrome's own watcher does the rescan, so no credential sits in a unit.
- A 10-minute quiet period, and a partial album as the accepted risk of a copy that stalls past it.
- The folder is `~/Fresh Tracks`, the same name as the share (Geoff, 2026-11-24). A path unit takes the space
  as written: `systemctl --user show` on a test unit printed `Paths=/var/home/glw907/Fresh Tracks`. A sandbox
  line that lists the path quotes it.
- The work folder lives inside the inbox, hidden from Samba, so files keep the share label on their way in.
- Loose top-level files import as one item, grouped by tags.
- The task session installs nothing; the merging session does, after Geoff's approval.
