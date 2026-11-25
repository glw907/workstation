# Artist photos: a photo for every artist in the pavilion library

Status: approved

Written on Opus. Geoff ruled that this spec is written on Opus, because Fable's weekly limit is used up until
Nov 27.

## Intent

Geoff, 2026-11-24: "Please make sure all of them have appropriate images, and we'll need a process for getting
them." And: "And we'll need to make sure that this issue doesn't occur for future incoming music."

His rulings the same day:

- Sources: "Consider sources in order or likely usefulness." The order below is by how many missing artists each
  source filled in the probes, most first. It is decided, not open.
- A Discogs token: `DISCOGS_TOKEN` is in the age store, `~/.local/secrets`, and Proton Pass as "Discogs token
  (music library)" in the Infrastructure vault. Probe: `/oauth/identity` returns 200.
- Artist images for dubplate are dubplate backlog #187. This spec covers pavilion only.
- For dubplate: "For dubplate, consider options that we can access programmatically." See "Related work".

The gap, probed on the live database today (the query is task 2's goal item 4). Of the 245 artists who have the
artist or album-artist role and a MusicBrainz ID, 26 have no image, 216 have a Deezer image, and 3 have an
`artist.*` file. Most of them are compilation track artists or featured guests, such as Dan Papaila on Slightly
Stoopid's "Top of the World", who have no artist folder. Deezer matches by name. Its matches for "Jessy",
"Valentina", "Lambda", and "Plexus" are suspect: its search returns 4, 3, 2, and 1 exact-name artists for them,
and for Jessy the exact match is the fourth result.

Goals: every artist above shows a photo from a source tied to its MusicBrainz ID, or the cover of one of its releases
when no photo exists, and a short report names each fallback and each low-confidence match. New music from Fresh
Tracks gets the same treatment within minutes, and a monthly run retries the fallbacks.

Non-goals: Spotify, Fanart.tv, any dubplate change, and Rufin. No web page and no desktop notice. Composers,
lyricists, and other artists with no artist or album-artist role. Wendy Milan, the one such artist with no
MusicBrainz ID, keeps her Deezer image.

Failure: a wrong person's photo for an artist with no warning in the report, a hand-placed file overwritten, or a
run that stops new imports from getting photos with nothing in the journal.

Trust: the inputs are public APIs and public pages, read by a helper that runs as Geoff. A remote reply decides
only the bytes of an image, never a file name or a path, and an image is written only after it passes the checks
under "What a file must pass". A review finding whose fix adds behavior this Design doesn't name goes under
`## For Geoff` rather than into the build (backlog #124).

## Approaches

1. A separate helper in a separate unit, writing into Navidrome's `ArtistImageFolder` (picked). Fresh Tracks
   starts it through `OnSuccess=`, and a monthly timer starts it too. `fresh-tracks` and its sandbox don't
   change. Documented pieces: `ArtistImageFolder` and `ArtistArtPriority` (Navidrome configuration options) and
   `OnSuccess=` (`systemd.unit(5)`).
2. A step inside `fresh-tracks`. That puts the network, a secret, and Navidrome's state inside a sandbox built
   for neither, and it grows a script that already outran its scale (backlog #124).
3. Upload each photo through Navidrome's web-UI upload (`EnableArtworkUpload`). An upload outranks every other
   source, so the helper's photos would collide with uploads Geoff makes by hand, and a Navidrome admin credential would
   have to sit in a unit.

## Design

- **Folder.** `~/Music/.artist-images/`, mode 0755. Navidrome's scanner and watcher skip dot folders
  (`Scanner.IgnoreDotFolders` defaults to true), and the folder moves with any copy of the library.
- **Navidrome.** `navidrome.service` gains `Environment=ND_ARTISTIMAGEFOLDER=%h/Music/.artist-images` and
  `Environment="ND_ARTISTARTPRIORITY=artist.*, album/artist.*, image-folder, external"`. The order keeps the 3
  artists with an `artist.*` file on that file, and keeps Deezer behind the folder. A file named
  `<mbid>.<ext>` matches when its base name equals the artist's MusicBrainz ID, case-insensitive, with any image
  extension. Probe on a copy of the database, with these settings: `navidrome -n artwork explain --live ar
  2aAtnW1NZIOOghPaFea7df` (Lambda) printed `image-folder hit .../10a7fa20-6731-425f-a7c2-707dc664cfc6.JPG`. A
  hit is stored with source `folder` and a `source_path` in that folder (`resolve.go`, 0.64.2).
- **Script.** `bin/.local/bin/artist-photos`, one file of stdlib Python with the shebang `#!/usr/bin/python3 -I`.
  Go replaces it if it ever needs a package or a second file. A test sets the folder, the two databases, the
  `navidrome` binary, and the state folder through environment variables.
- **Which artists.** It reads Navidrome's database with sqlite `mode=ro`: each artist that isn't missing, has the
  artist or album-artist role, and has a MusicBrainz ID, less those whose stored art is an `artist.*` file in the
  library. Each artist's state in `state.json` decides whether the chain runs: no state, or deferred by a failed
  request, runs now; `fallback` or `none` runs again once its last try is more than 28 days old; `photo` and
  `manual` never run again.
- **Waiting for a scan.** While `max(added)` in beets' `items` table (`~/.local/share/beets/library.db`,
  read-only; epoch seconds, probe `1795578363.2082806`) is later than Navidrome's `library.last_scan_at` (text
  with an offset, probe `2026-11-24 18:46:32.582002428-09:00`), compared in UTC, it polls every 15 seconds, for up
  to 10 minutes. Probe: the watcher scan at 18:46:32 today set `last_scan_at`.
- **Sources, in order.** Each MusicBrainz lookup is
  `/ws/2/artist/<mbid>?inc=url-rels+release-groups`. The first source that yields an image that passes wins.
  Counts are from the 2026-11-24 probes: the first two were run on 139 artists, Discogs on the 91 those two
  missed, and the rest on the 37 still missing after Discogs.
  1. Discogs, through the MusicBrainz `discogs` link, then `api.discogs.com/artists/<id>`: its `primary` image,
     else the first. 54 of 77 checked.
  2. Wikidata `P18` through the MusicBrainz `wikidata` link, fetched as Commons
     `Special:FilePath/<file>?width=1200`, so an original over 10 MB arrives scaled. 42 of 139.
  3. Bandcamp, the `og:image` of the MusicBrainz `bandcamp` link. 16 of 139.
  4. Apple Music: the iTunes Search API (`entity=musicArtist`) on the exact normalized name, then the
     `og:image` of the artist's page, taken only when its path contains `AMCArtistImages`. 10 of 37.
  5. The `og:image` of a MusicBrainz `social network` link. 8 of 37.
  6. SoundCloud, the `og:image` of that link. 6 of 37.
  7. YouTube, the `og:image` of that link. 6 of 37.
  8. The `og:image` of the MusicBrainz `official homepage` link. 3 of 37.
  9. The MusicBrainz `image` link. 2 of 37.
  10. Deezer, `api.deezer.com/search/artist` on the exact name.

  A name-matched source (4 and 10) is taken only for a candidate whose name equals the artist's after
  normalizing (NFKD, casefold, punctuation dropped, spaces collapsed), and only when one of that candidate's album
  titles, from one request (iTunes `lookup?id=<id>&entity=album`, Deezer `/artist/<id>/albums`), equals a library
  album or track title after the same normalizing. Each exact-name candidate is checked in turn. Sources 3 to 8 are page scrapes:
  fragile, best-effort, and placed behind the APIs. Beatport is left out (24 HTTP errors in 29 tries, and its API
  is for partners only). Partyflock and Resident Advisor weren't probed, so they appear in the report only as
  places to look by hand.
- **Fallback covers.** With no photo, it takes the first of these: the `primary` image of the earliest release
  (by year) where the artist has the `Main` role in `api.discogs.com/artists/<id>/releases`, read from its master
  or release, Apple's album cover from source 4, or the library cover of an album where the artist
  is the sole album artist. With none, it writes no file. Ten artists had nothing in any probe, among them 303
  Abuse, 909 Abuse, Psyche Out, and Random Rampage.
- **What a file must pass.** The MusicBrainz ID is a UUID, checked by pattern, and names the file. A reply must
  be `image/jpeg`, `image/png`, or `image/webp`, open with that type's magic bytes, and stay under 10 MB. The
  extension comes from the magic bytes. The helper writes to `.<mbid>.part` in the folder, then renames it over
  the target, and removes the earlier file it wrote for that ID if the extension changed.
- **State and manual files.** `~/Music/.artist-images/state.json` records, for each file the helper wrote, its
  sha256, source, URL, kind (photo or fallback), confidence, and last try. A `<mbid>.*` file whose hash isn't
  recorded is manual: the helper never replaces it, never tries that artist again, deletes the file it wrote for that
  ID if one is there, records the manual file's hash, and lists it in the report. Geoff or Claude replaces a photo
  by dropping in `<mbid>.jpg`, then starting `artist-photos.service`, which refreshes that artist. A web-UI upload in Navidrome still outranks the
  folder.
- **Confidence.** Discogs, Wikidata, Bandcamp, and the MusicBrainz `image` link are sure: each is reached from
  the ID, and each holds the artist's chosen picture. Apple and Deezer are low confidence, being name-matched.
  Social, SoundCloud, YouTube, and homepage images are reached from the ID too, but a profile image is often a
  logo or a small avatar and a homepage image often a banner, so they are low confidence as well.
- **Telling Navidrome.** Navidrome doesn't re-resolve stored art unprompted. After writing, the helper runs
  `navidrome artwork refresh ar <id>...` once for every artist whose stored `source_path` isn't its file in the
  folder, and for every artist whose file is new this run under the same name. The server's artwork worker reads that queue every 5 seconds. An artist Navidrome hasn't stored yet
  finds its file at first resolve.
- **Report.** `~/.local/state/artist-photos/report.md`, rewritten each run, lists each fallback, each
  low-confidence photo, each manual file, each artist with no file (with its MusicBrainz, Partyflock, and
  Resident Advisor search links), and each artist a failed request deferred. One summary line goes to the
  journal: artists tried, photos, fallbacks, none, deferred.
- **Units.** `artist-photos.service` is `Type=oneshot` with `ConditionHost=pavilion`, `TimeoutStartSec=2h`, the
  same `ND_MUSICFOLDER`, `ND_DATAFOLDER`, `ND_ARTISTIMAGEFOLDER`, and `ND_ARTISTARTPRIORITY` lines as
  `navidrome.service`, `ProtectHome=tmpfs`, `BindPaths=%h/Music/.artist-images %h/.local/state/navidrome`,
  `BindReadOnlyPaths=` for `%h/Music` (the library covers; systemd mounts the deeper read-write bind over it),
  `%h/.local/share/beets`, `%h/.local/secrets`,
  `%h/.local/bin`, `%h/.dotfiles/bin`, and `/var/home/linuxbrew/.linuxbrew`, plus `StateDirectory=artist-photos`,
  `PrivateTmp=yes`, and `NoNewPrivileges=yes`. `artist-photos.timer` has `OnCalendar=monthly` and
  `Persistent=true`. `fresh-tracks.service` gains `OnSuccess=artist-photos.service`. The Homebrew bind is needed
  because `ProtectHome=tmpfs` hides `/home`, where the `navidrome` binary lives.
- **Token.** `DISCOGS_TOKEN` from the environment, else the one `export DISCOGS_TOKEN=` line of
  `~/.local/secrets`, parsed by the helper. `cairn-tripwire` reads that file itself too, though it sources the
  whole file. With no token, it skips Discogs and says so
  in the report.
- **User-Agent.** MusicBrainz requires `App/<version> ( contact )` and throttles generic agents. Geoff ruled on
  2026-11-24 for the technical mailbox, over the public repo URL and over no contact, so every request sends
  `artist-photos/<version> ( glw@907.life )`.
- **Backup.** Geoff ruled on 2026-11-24 for "Add a backup task", over backing up only the photo folder and over no
  backup for now. Nothing on pavilion pushes to R2 today, and the music key is read-only, so neither
  `.artist-images` nor a Fresh Tracks import has a copy. Task 4 adds one:
  - A new key, `ws-r2-music-rw`: account-owned, R2 object read and write on `music-library` only, with no IP
    filter and no expiry, per the scheme in `~/.claude/docs/cloudflare-estate/api-tokens.md`. It's stored as
    `CF_WS_R2_MUSIC_RW_TOKEN` with its S3 pair `_KEY_ID` and `_SECRET`, in the age store, the registry, and
    Proton Pass. `ws-r2-music-ro` stays as it is.
  - `bin/.local/bin/music-backup`, bash glue. It sources `~/.local/secrets`, sets rclone's remote through
    `RCLONE_CONFIG_R2_*` variables (type `s3`, provider Cloudflare, the stored pair, the account's R2 endpoint, `NO_CHECK_BUCKET=true`, since a
    bucket-scoped key can't create a bucket), and runs `rclone copy "$HOME/Music" r2:music-library/library
    --exclude '.artist-images/.*.part'`. It exits nonzero, running nothing, when a key is missing.
  - `music-backup.service`, `Type=oneshot`, with `ConditionHost=pavilion`, `TimeoutStartSec=6h`,
    `ProtectSystem=strict`, `ProtectHome=read-only`, `PrivateTmp=yes`, `NoNewPrivileges=yes`, and
    `IOSchedulingClass=idle`. `music-backup.timer` has `OnCalendar=*-*-* 03:30` and `Persistent=true`.
  - It's `rclone copy`, never `rclone sync`, in both directions. The backup never deletes an object, so a local
    loss can't reach R2. An object whose local file changed is overwritten, and a path deleted locally stays in
    R2: today 2 of the bucket's 254 objects are covers the cover rule replaced. The pull from R2 to `~/Music`
    stays `rclone copy` too. A `sync` from R2 would delete every file the last backup hadn't reached, the photo
    folder included before its first backup.
  - The first run uploads about 33 GB: `~/Music` holds 1,475 files and 40 GB, and the bucket holds 254 of them, 6.6
    GiB. A run the timeout stops resumes the next night, since `copy` skips what's already there.
  - It copies `~/Music` only. The beets and Navidrome databases under the bucket's `state/` aren't refreshed.

## When it goes wrong

| Case | What happens | Limit |
| --- | --- | --- |
| MusicBrainz answers 503 | Backs off 5, 10, 20, then 40 seconds; after the fifth try the artist is deferred to the next run and listed | 1 request per 1.1 s |
| Discogs nears its limit | Waits when `X-Discogs-Ratelimit-Remaining` reaches 2 | 1 request per s; 60 per minute (header) |
| The iTunes Search API | Paced below its published limit | 1 request per 3.5 s (about 20 per minute) |
| Any other host | Paced per host; a timeout or error moves on to the next source | 1 request per s, 20 s timeout |
| A reply isn't an image or is too large | Not written; the chain moves on | 10 MB |
| A scrape's page changes shape | That source finds nothing; the next source or a fallback fills in, and the report shows the drop | none |
| Navidrome is mid-scan when Fresh Tracks finishes | Waits for the scan | 10 min, then runs anyway |
| The run crashes or times out | The service fails and `systemctl --user status artist-photos` shows it; files already written stay | 2 h |
| `navidrome artwork refresh` fails | The run fails after writing its files; the next run refreshes them | none |
| An artist has no source and no cover | No file; Navidrome's Deezer agent may still fill it; the report lists it for a hand-picked file | none |
| The backup fails or is refused | `music-backup.service` fails and `systemctl --user status music-backup` shows it; the next night retries | 6 h |

## Sources and labels

- `ArtistImageFolder`, `ArtistArtPriority`, `image-folder`, MBID-then-name matching: documented (Navidrome
  configuration options) and probed on a copy of the database, quoted under "Navidrome".
- `navidrome artwork refresh` and `reprocess --all -y`: documented in their `--help`, run today on the copy
  (`refresh` printed `ar/2aAtnW1NZIOOghPaFea7df: queued`). `reprocess --all` clears the config fingerprint warning
  only with no `--source` filter and every kind (`cmd/artwork.go`, 0.64.2).
- The worker draining the queue every 5 seconds: read in Navidrome's source (`workerPollInterval`), not probed live.
- Dot folders skipped by the scanner: documented (`Scanner.IgnoreDotFolders`).
- MusicBrainz rate limit and User-Agent: documented, musicbrainz.org/doc/MusicBrainz_API/Rate_Limiting; the 503
  at about 1 request per second probed.
- Discogs token header and limit: documented (Discogs API); the 60-per-minute header probed with the token.
- iTunes Search limit: documented, "limited to approximately 20 calls per minute" (iTunes Search API).
- `og:image`: documented (the Open Graph protocol). Each site's use of it was probed by count, not documented.
- `AMCArtistImages` as Apple's mark of a real photo: probed (10 of 26 Apple hits; the other 16 were album covers).
- Commons `Special:FilePath` with `width`: documented (MediaWiki, Help:Special:FilePath).
- `OnSuccess=`, `OnCalendar=monthly`, `Persistent=true`, `ProtectHome=tmpfs`: documented (`systemd.unit(5)`,
  `systemd.timer(5)`, `systemd.exec(5)`).
- `rclone copy` never deleting at the destination, `--exclude`, and the `RCLONE_CONFIG_<REMOTE>_*` variables:
  documented (rclone docs, `copy` and Environment variables). `no_check_bucket` for a bucket-scoped R2 key:
  documented (Cloudflare R2, rclone). rclone v1.75.2 is at `/usr/bin/rclone`, from the image. The bucket's listing
  and the 252-of-254 path match: probed today with the read-only key.
- The key's form, the stored pair, and the smoke test: the scheme and the `CF_WS_R2_ARCHIVE_RW_*` registry
  section, which minted `ws-r2-archive-rw` the same way on 2026-10-18.
- The 28-day retry, the 10-minute scan wait, the 10 MB cap, the pacing for hosts without a published limit, the
  03:30 start, and the 6-hour timeout: invented.

Assumptions more than one task rests on:

1. The running server's worker drains a queue row that the `navidrome` CLI wrote from another process. Least
   proven: read in the source only. Task 2's `## Before merge` check proves it live.
2. Discogs stays the best first source across the whole set. Its 54 of 77 came from the residual 91, and 14
   artists went unchecked when a 404 crashed the probe.

## Files

Searches: `rg -l -i navidrome --hidden -g '!docs/specs/**' -g '!.git/**' .` (8 hits: `navidrome.service` and
`secrets/registry.md` change; `beets/.config/beets/plugins/coverrule.py`, `bluefin/Brewfile`, the
`vps-conventions` skill, and three files under `docs/model-review/` and `docs/plans/` are dismissed, since none
sets artist art). `rg -l DISCOGS --hidden -g '!.git/**' .` (0 hits). `rg -n fresh-tracks scripts/check.sh` (1
hit, line 149's pytest list). In household-it, `rg -n -i 'navidrome|artist' docs/systems/workstations.md` (2
hits, lines 13 and 17, the music server's section).

- Task 1: `bin/.local/bin/artist-photos` (new), `tests/test_artist_photos.py` (new), `tests/fixtures/artist-photos/`
  (new), `scripts/check.sh`.
- Task 2: `systemd/.config/systemd/user/navidrome.service`, `artist-photos.{service,timer}` (new),
  `fresh-tracks.service`, `tests/test_artist_photos_units.py` (new), `scripts/check.sh` (the pytest trigger).
- Task 3: household-it `docs/systems/workstations.md`.
- Task 4: `bin/.local/bin/music-backup` (new), `music-backup.{service,timer}` (new), `tests/test_music_backup.py`
  (new), `scripts/check.sh`, `secrets/registry.md`, `secrets/values.age` (written under `## Before merge`), and
  `claude/.claude/docs/cloudflare-estate/api-tokens.md`. `rg -n -i 'music|r2' ...` over the last two finds the
  `MUSIC_R2_RO_*` section and routing rows, and the `ws-r2-music-ro` row at `api-tokens.md` line 64. No
  `music-pull` script exists: the registry names it, and the pull has been a hand-run `rclone copy`.

Commands the tasks run (pytest, `systemd-analyze --user verify`, `navidrome artwork`, `stow`, `systemctl
--user`, `sqlite3` with `mode=ro`, `rclone`, `secret-set.sh`, `claude-pass`, the Cloudflare tokens API) were
checked against the last 30 days of `~/.local/state/claude-denials.jsonl`. Of its 165 lines, 2 touch the music
work, a dubplate `musicbrainz` read and a `sed` of a unit file to `/tmp`, and neither matches a command here. One
matches task 4: on 2026-11-01 the `[Secret-Store Writes]` rule denied a `secret-set.sh --delete` run. So task 4's
store writes and minting run in the merging session, which Geoff is talking to, and never in a background task
session.

## Tasks

Pavilion is the host because Navidrome, its database, and the library live there, and the helper only feeds that
server: a Cloudflare or Hetzner host would hold a copy of the library's artist list for nothing.

Start conditions:

- Fresh Tracks (workstation#280) has merged and its units are live, and the dotfiles main checkout is pulled.
- The age store's `DISCOGS_TOKEN` entry and its registry row are on `origin/main`. They landed directly in
  4591bf5b ("Store and register the Discogs token"), as earlier store-and-register commits did.
- For task 3, household-it's local gate passes on its main branch, which needs room in `/tmp`.
- For task 4's merge, Geoff is at his terminal for the one dashboard step under its `## Before merge`.

### Task 1: the helper

Name: artist-photos
Tier: ask
Files: `bin/.local/bin/artist-photos`, `tests/test_artist_photos.py`, `tests/fixtures/artist-photos/**`, `scripts/check.sh`

Ask because `scripts/**` is on the Ask-only list. `standards:diff-reviewer` reads the branch, with
`standards:python-conventions`. Builds on nothing. Minutes: 100
(workstation median actual path 41.5, p90 145, `task-report` 2026-11-24; this task has ten sources, a fixture
database, and a stubbed network). Model: Opus at high. It changes nothing live and makes no network request.

Goal:

1. `bash scripts/gate.sh` passes on the last commit, with `artist-photos` in the pytest leg's list. Today: passes,
   without it (`rg -c artist-photos scripts/check.sh` prints nothing).
2. `uv run --with pytest --no-project python -m pytest tests/test_artist_photos.py -q` passes. A test replaces
   the helper's one fetch function with fixture replies, a stub `navidrome` records its arguments, and a fixture
   Navidrome database is built under `tmp_path` and opened read-only. Tests show each of these: an artist with
   Discogs and Wikidata replies gets the Discogs image; an Apple image without `AMCArtistImages` is passed over;
   a Deezer match with no shared title is refused and one with a shared title is taken as low confidence; a
   manual file is never replaced or retried, and the file the helper wrote for that ID is deleted; an HTML reply, a wrong magic number, and an 11 MB reply are not
   written; five MusicBrainz 503s defer that artist while the rest run; a fallback tried 29 days ago runs again
   and one tried 27 days ago doesn't; the stub receives `artwork refresh ar` with exactly the artists whose stored
   path isn't their file; and the report lists each fallback, low-confidence, manual, none, and deferred artist.
   Today: the file doesn't exist.
3. Every request the helper sends carries the User-Agent `artist-photos/<version> ( glw@907.life )`, Geoff's
   ruling of 2026-11-24 for the technical mailbox, and a test asserts it on each fixture request. Today: the file
   doesn't exist.

### Task 2: the units and the install

Name: artist-photos-wire
Tier: ask
Files: `systemd/.config/systemd/user/navidrome.service`, `systemd/.config/systemd/user/artist-photos.*`, `systemd/.config/systemd/user/fresh-tracks.service`, `tests/test_artist_photos_units.py`, `scripts/check.sh`

Ask because `scripts/**` is on the Ask-only list: the pytest leg's trigger gains the three unit paths, so a unit
change runs the units test. The install also needs `## Before merge`, which a Show task can't carry. Builds on task 1. Reviewers: `standards:diff-reviewer`. Minutes: 40. Model: Opus at high.

The task session changes nothing live. The merging session installs it under `## Before merge`:

1. `mkdir -p -m 0755 ~/Music/.artist-images`, since `BindPaths=` fails on a missing folder.
2. `stow -R bin systemd`, then `systemctl --user daemon-reload`, then `systemd-analyze --user verify
   ~/.config/systemd/user/artist-photos.{service,timer}`, which prints nothing.
3. `systemctl --user restart navidrome`.
4. `systemctl --user enable --now artist-photos.timer`.
5. `systemctl --user start artist-photos.service`, the one-time fill. Within 10 minutes, `navidrome artwork
   status` (with the `ND_` values below) shows an empty queue, which proves the least-proven assumption.
6. `navidrome artwork reprocess --all -y`, with `ND_MUSICFOLDER`, `ND_DATAFOLDER`, `ND_ARTISTIMAGEFOLDER`, and
   `ND_ARTISTARTPRIORITY` set as in `navidrome.service`. Wait until `navidrome artwork status` shows an empty
   queue again.
7. The check below, then the report shown to Geoff.

Goal:

1. `bash scripts/gate.sh` passes on the last commit. Today: passes.
2. `uv run --with pytest --no-project python -m pytest tests/test_artist_photos_units.py -q` passes. It shows
   that `navidrome.service` and `artist-photos.service` carry the same four `ND_` lines named under "Units",
   that each `BindPaths=` folder exists in step 1 or as a `StateDirectory=`, and that
   `fresh-tracks.service` holds `OnSuccess=artist-photos.service`. Today: the file doesn't exist, and
   `rg -c 'ND_ARTIST|OnSuccess' systemd/.config/systemd/user/` prints nothing.
3. The PR's `## Before merge` lists the steps above and this check. After step 6, this query on the live
   database prints a `folder` count equal to 3 plus the photos, fallbacks, and manual files the report names, and
   its other rows (blank or `external:`) add up to the report's count of artists with no file:

   ```bash
   sqlite3 "file:$HOME/.local/state/navidrome/navidrome.db?mode=ro" "select coalesce(i.source,''), count(*) from artist a left join item_artwork i on i.item_kind='ar' and i.item_id=a.id and i.image_type='primary' where a.missing=0 and a.mbz_artist_id<>'' and exists(select 1 from media_file_artists m where m.artist_id=a.id and m.role in ('artist','albumartist')) group by 1;"
   ```

   Today it prints `|26`, `external:deezer|216`, and `folder|3`.

### Task 3: the runbook

Name: artist-photos-runbook
Tier: ask
Files: `docs/systems/workstations.md`

household-it has no Ask-only list, so Ask. Its repo is private and runs no CI, so its local gate stands in.
Builds on tasks 2 and 4 (it documents what merged). Reviewers: `standards:diff-reviewer`. Minutes: 25. Model:
Sonnet at medium.

Goal:

1. `docs/systems/workstations.md`, in the music server's section, says where artist photos come from, where the
   report is, how to replace a photo (a `<mbid>.jpg` in `~/Music/.artist-images/`, named by the artist's
   MusicBrainz ID, then `systemctl --user start artist-photos.service`), and how to check the timer (`systemctl --user list-timers artist-photos.timer`), in the
   voice of `docs/contributing.md`. Today: none of it.
2. The same section says that `music-backup.timer` copies `~/Music` to `music-library/library/` each night, names
   the key `ws-r2-music-rw` and its store names, and says that a restore is `rclone copy` from R2, never `rclone
   sync`, which would delete every file the last backup hadn't reached. Today: "Where it lives" calls `~/Music` a copy
   of the bucket's `library/` folder, made on 2026-11-24, and names no backup.
3. `bash scripts/check.sh < /dev/null` passes. Today: fails, because `/tmp` hit its per-user quota mid-run (`check-docs.test.sh`: `cp: ... Disk quota exceeded`), not on a code fault.

### Task 4: the library backup

Name: music-backup
Tier: ask
Files: `bin/.local/bin/music-backup`, `systemd/.config/systemd/user/music-backup.*`, `tests/test_music_backup.py`, `scripts/check.sh`, `secrets/registry.md`, `secrets/values.age`, `claude/.claude/docs/cloudflare-estate/api-tokens.md`

A sign-in task: `secrets/**` is `auth-data` in `dotfiles-pass`'s path map, and the task mints and stores a key.
So `standards:web-auth-security-reviewer` reads the branch beside `standards:diff-reviewer`, the pull request is
flagged as an `auth-data` change, and the close runs one `gitleaks git` scan of the branch's history. Builds on
nothing, so it can run beside task 1. It merges after task 2, since both edit the pytest list in
`scripts/check.sh`, and the photo folder then exists for the first run. Minutes: 40 (a short script, two units, a
stubbed test, and two doc rows). Model: Opus at high.

The task session changes nothing live and writes no secret. It writes the script, the units, the test, the
registry's `CF_WS_R2_MUSIC_RW_*` section and its routing row, and the `api-tokens.md` row, with the token id left
as `(minted at merge)`. The merging session runs `## Before merge`:

1. Geoff creates `tmp-account-tokens` (Account API Tokens Edit, ending tomorrow) on the dashboard, per rule 6 of
   the scheme, and Claude launches `secret-receive` into the RAM-only scratch store the scheme names. This is the
   one step only Geoff can do.
2. With it, mint `ws-r2-music-rw`: account-owned, R2 object read and write on `music-library` only, no IP filter,
   no expiry.
3. Store `CF_WS_R2_MUSIC_RW_TOKEN`, `_KEY_ID`, and `_SECRET` through `scripts/secrets/secret-set.sh --file`, each
   from a mode 0600 file under `$XDG_RUNTIME_DIR` that's removed after. Write the token id into the registry and
   the `api-tokens.md` row, and commit `secrets/values.age` with them to the branch.
4. Create the Proton Pass item through `claude-pass`, values on stdin, in the vault and under the name the
   `proton-pass` skill sets.
5. Smoke-test over S3 with the stored pair: the key lists `music-library` (200), is refused `servers-archive`
   (403), and writes then deletes one object under `music-library/_smoke/`. Record the result on the registry's
   "Minted" line.
6. Delete `tmp-account-tokens` with itself, and remove the scratch store.
7. `stow -R bin systemd`, `systemctl --user daemon-reload`, and `systemd-analyze --user verify
   ~/.config/systemd/user/music-backup.{service,timer}`, which prints nothing. Then `systemctl --user enable --now
   music-backup.timer` and `systemctl --user start --no-block music-backup.service`, the first run.
8. Once the first run ends, the check below, shown to Geoff.

Goal:

1. `bash scripts/gate.sh` passes on the last commit, with `music-backup` in the pytest leg's list. Today: passes,
   without it.
2. `uv run --with pytest --no-project python -m pytest tests/test_music_backup.py -q` passes. With a stub
   `rclone` on `PATH` and a fixture secrets file under `tmp_path`, it shows that the script calls `rclone copy`
   with exactly the source, destination, and exclude under "Backup", with the `RCLONE_CONFIG_R2_*` values
   from "Backup" set; that it runs nothing and exits nonzero when either half of the pair is missing; that no file in the task
   names `rclone sync`; and that the service carries `ConditionHost=pavilion` and the timer `Persistent=true`.
   Today: the file doesn't exist.
3. `rg -n 'CF_WS_R2_MUSIC_RW' secrets/registry.md claude/.claude/docs/cloudflare-estate/api-tokens.md` shows the
   section, one routing row, and the table row. Today: prints nothing.
4. The PR's `## Before merge` lists the steps above and this check. After the first run, `rclone check
   --one-way --size-only "$HOME/Music" r2:music-library/library --exclude '.artist-images/.*.part'`, run as
   the script runs it, reports 0 differences, and `systemctl --user list-timers music-backup.timer` shows the
   next run. Today: 1,223 local files have no object.

Merge order: task 1, task 2, task 4, task 3. After task 2 merges, Geoff picks files for the artists the report
lists with no file, in a sitting.

## Backlog sweep

Scoped sweep (`artist|photo|navidrome|discogs|deezer|music|beets|fresh tracks|r2` in the workstation and
household-it backlogs): workstation #124 (review loops growing a build) keep, and this spec's trust line applies
its lesson; workstation #2 (move the music-VPS docs) keep, unrelated; household-it #11 already done. No edits.

## Related work: dubplate #187

Dubplate's artist images are its backlog #187, out of scope here. For Geoff's ruling there ("For dubplate,
consider options that we can access programmatically"), the sources reached through an API are MusicBrainz,
Wikidata and Commons, Discogs (with a token), Deezer, the Spotify Web API (a free app), and the Apple Music API
(a paid developer account). Bandcamp, Apple's page `og:image`, the profile images, and Beatport without partner
access are page scrapes. This helper's chain and counts are the starting data for that spec.

## For Geoff at approval

Nothing is open. Geoff ruled on 2026-11-24 on the backup (task 4) and the User-Agent contact (task 1, goal item
3), and the backup's ruling settles the third reading: both directions stay `rclone copy`, and "Backup" warns that
a `sync` from R2 would delete the photo folder and any file not yet backed up.

## Calls Claude made

- A separate helper and unit over a step in `fresh-tracks`, so that sandbox stays as built.
- The folder is a dot folder inside `~/Music`, so Navidrome never scans it and it travels with the library.
- `image-folder` sits after `artist.*` and `album/artist.*` and before `external`, so the 3 artist files keep
  winning and Deezer remains the last resort.
- The source order follows the probe counts, so the MusicBrainz `image` link (2) comes after the profile images,
  where the suggested order had it second.
- Apple and Deezer need a shared title before they count, because Deezer returned several exact-name artists.
- A manual file is any file whose hash isn't recorded as one the helper wrote, so no list of overrides is kept,
  and replacing a photo by hand needs no Navidrome ID.
- Photos are never retried; fallbacks and empty artists are retried after 28 days.
- The helper parses the one token line from `~/.local/secrets` rather than sourcing the file.
- Every Deezer image is replaced wherever another source or a cover exists, as in the design Geoff saw (one-time
  fill of all current artists).
- The unit test that keeps the `ND_` lines equal in two units, over a shared environment file.
- The task sessions install nothing; the merging session does, after Geoff's approval.
- The backup sends no `--backup-dir`. A dated archive would keep the version a changed file overwrote, but a beets
  retag rewrites whole files, so the archive would grow with every tag edit. The ruled guard is against deletion,
  and `copy` keeps it.
- The backup key is a new key beside `ws-r2-music-ro`, not a widened one, so the pull keeps a key that can't write.
- The first run starts with `--no-block` and resumes across nights rather than carrying a longer timeout.
