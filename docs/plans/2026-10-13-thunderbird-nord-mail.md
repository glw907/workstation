# Thunderbird Nord mail layer: implementation plan

**Design:** `docs/specs/2026-10-13-thunderbird-nord-mail-design.md` (approved by Geoff,
2026-10-13; the "Who merges the PR" decision came back unanswered, so the recommended choice
holds: Geoff reads the screenshots before merge). It runs about a page, and the mechanisms live in
the evidence below, so no separate spec was written (`spec-plan-review` "Depth scales with risk").
**Evidence:** the research report,
`docs/research/2026-10-13-mail-colour-evidence/reports/Mail colour readability evidence.md`
(cited as "report"); its notes in the sibling `research_notes/` folder, including
`nord_palette_measured.md` and its script `nord_measure.py` (cited as "measure"); and the styling
map of Thunderbird 158, `docs/research/2026-10-13-mail-colour-evidence/thunderbird-css-map.md`
(cited as "map"; its line numbers for the theme's `mail.css` and for `messageQuotes.css` are stale,
so this plan cites lines read from the installed files). **Review:** the mechanics lens and the fold
record, `docs/research/2026-10-13-thunderbird-nord-mail-{review-mechanics,plan-fold}.md`.
The fold re-cut the waves by file ownership: the contrast check joined task A, D runs alone, and
the fold record lists every source it read.

**Outcome.** On a machine that has pulled this pass and run `thunderbird-theme-sync`, Thunderbird's
message list and reader follow the design: a nord8 unread dot plus bold, names-only senders,
two-row cards, hidden unflagged stars, neutral quoted text with fading nord8 bars, underlined
plain-text links, mode-tuned signatures, and the local junk filter off. One palette file,
`thunderbird/nord.css`, defines every colour and role, and `thunderbird/README.md` carries the role
map. A headless screenshot harness and a contrast check under `thunderbird/tools/` prove it on test
messages, never on real mail.

**Pass class:** `ordinary`. Every path is `thunderbird/**`, `bin/.local/bin/thunderbird-theme-sync`
(not in the adapter's runner or auth-data lists), `bluefin/SECOND-WORKSTATION.md`, or
`docs/**`. No `live-account` flag: nothing calls a Cloudflare, GitHub (beyond the PR),
or npm account, and the harness runs Thunderbird offline against a scratch profile.

**Out of scope:** the design's list (the sender's HTML design, Outlook and Yahoo quote bars, the
compose window, the calendar, folder-pane changes beyond the colours already on `main`, layout
changes other than two-row cards, poplar's own implementation). Also out: any change to Geoff's
live Thunderbird profile, any edit to `scripts/**` or `tests/**`, and the gate's machine-state
failures (see "Gate").

**End-to-end check.** On the close head:

1. `python3 thunderbird/tools/contrast_check.py` exits 0 and prints every role against every
   background in both modes, with no `FAIL` line.
2. `thunderbird/tools/tb-shots --keep <new dir>` builds the scratch profile, installs the theme
   with `bin/.local/bin/thunderbird-theme-sync --profile <scratch>`, and writes the screenshot set
   listed in task B. Each screenshot shows what D's and E's acceptance names, read by the session
   and by a fresh-context `visual-verifier` dispatch.
3. `bin/.local/bin/thunderbird-theme-sync --check --profile <scratch>` prints the match line for
   the kept profile. Then editing the installed `nord.css` makes the same command print an `x` line
   naming `nord.css`.
4. The kept scratch profile folder is removed, and `ss -ltn | grep -c ':28282 '` prints 0.
5. `bash scripts/gate.sh` prints `gate exit:` with no failure beyond the pavilion baseline below.

**Clock estimate:** 390 path minutes. Wave 1 is A 85 with B 115 (pair) plus a 10-minute merge and
check, so 125. Wave 2 is D 95 alone. Wave 3 is E 95 with F 30 (pair) plus a 10-minute merge and
check, so 105. Close is 65. The path is 125 + 95 + 105 + 65 = 390. That is over the design's
"about 300" and under 600, twice that figure, where pass-core sends a plan back to Geoff (fold
record, "Estimate").

## Launch

Prompt file: `docs/plans/2026-10-13-thunderbird-nord-mail-prompt.txt`. The plan lives
on branch `worktree-thunderbird-nord-mail` (planning commits). The executor continues that branch:
its first act after `EnterWorktree` (name `thunderbird-nord-mail-build`) is `git reset --hard
origin/main`, then `git merge --no-edit worktree-thunderbird-nord-mail`. The reset matters because
at launch (2026-10-13, 15:3x) local `main` carried two unpushed commits from another session,
`dotfiles-44` (`cd99e21` Solaar, `25d4d7c` Bluetooth runbook note). The worktree branches from local
`HEAD`, and the reset keeps those commits out of this pass's PR. It touches only the new build
branch. So the `origin/main..HEAD` check below may print 2 for that reason alone. Launch from the
main checkout after every other check prints what its comment names:

```bash
git -C ~/.dotfiles fetch origin
git -C ~/.dotfiles branch --show-current                # must print main
git -C ~/.dotfiles rev-list --count HEAD..origin/main   # must print 0
git -C ~/.dotfiles rev-list --count origin/main..HEAD   # must print 0
git -C ~/.dotfiles status --porcelain                   # must print nothing
git -C ~/.dotfiles rev-parse worktree-thunderbird-nord-mail origin/worktree-thunderbird-nord-mail   # two equal lines
ss -ltn | grep -c ':28282 '                             # must print 0: no Thunderbird holds the harness port
claude agents --json                                    # no live session named dotfiles-thunderbird-nord-mail
cd ~/.dotfiles && claude --bg --model sonnet --effort medium --name dotfiles-thunderbird-nord-mail \
  "$(git -C ~/.dotfiles show worktree-thunderbird-nord-mail:docs/plans/2026-10-13-thunderbird-nord-mail-prompt.txt)"
```

## Conventions every task follows

- **Gate.** `bash scripts/gate.sh`, Bash `timeout: 600000`, re-issued on exit 75 until it prints
  `gate exit:`. On pavilion the gate already fails on `main` with exactly these four ratchet lines
  and nothing else (2026-10-13, `main` at `7673ed9`):
  ```
  new violation: claude/.claude/CLAUDE.md: ~/Android/
  new violation: claude/.claude/docs/bluefin-admin.md: ~/.config/glib-2.0/
  new violation: claude/.claude/docs/bluefin-admin.md: /etc/systemd/logind.conf.d/
  new violation: claude/.claude/instructions/fastmail-api.md: ~/.contacts/
  ```
  They are machine state (paths absent on pavilion), not this pass's defect. A task's gate passes
  when its only failures are those four lines. Any other failure is a red. The PR body lists the
  baseline under "Found, not done" with a proposed "defer" (fixing it is a `runner` pass). The
  gate's ruff D rules lint every tracked `.py` file (`scripts/check.sh:39`), so both new Python
  files carry PEP 257 docstrings (load `python-conventions` before writing one).
- **Live profile untouched.** Geoff's Thunderbird and its profile
  (`~/.var/app/org.mozilla.thunderbird/.thunderbird/jqkfj0f7.default-release`) are never written,
  launched, or killed. `thunderbird-theme-sync` runs only with `--profile <scratch>` (task B adds
  the flag); in that mode it never runs the theme's installer, never reads `profiles.ini`, and
  never updates the theme clone. Only `bin/.local/bin/thunderbird-theme-sync` from the worktree is
  run, never the bare name, which is the stowed main-checkout copy.
- **The scratch profile.** The Flatpak sandbox sees only `~/.var/app/org.mozilla.thunderbird/` of
  the home directory, so the scratch profile lives at
  `~/.var/app/org.mozilla.thunderbird/.thunderbird/tb-nord-harness` (the path inside the sandbox
  is `/var/home/glw907/.thunderbird/tb-nord-harness`). The harness creates and deletes it. Its
  fixture prefs live in its `prefs.js`, written before first launch, with no key that
  `thunderbird/user.js` also sets: the sync copies the layer's `user.js` over the profile's, and
  libpref reads `prefs.js` before `user.js` (Preferences.cpp:5022-5024), so both survive and
  `--check` still matches.
- **Thunderbird processes.** The harness starts Thunderbird with `flatpak run --instance-id-fd=3
  --env=MOZ_HEADLESS=1 org.mozilla.thunderbird --profile /var/home/glw907/.thunderbird/tb-nord-harness
  --no-remote --marionette -remote-allow-system-access 3>"$tmp/instance"`, waits until the instance
  id is written, and stops it with `flatpak kill <that numeric id>` from an `EXIT` trap that kills
  only a numeric id (with no id it kills nothing). Three methods are banned. `flatpak kill
  org.mozilla.thunderbird` matches by app id, so it would SIGKILL Geoff's instance too
  (flatpak-builtins-kill.c:74-77, :100-101). `pkill -f` patterns can match the session's own
  shell. `kill <pid>` of `flatpak run` leaves the sandbox running (the review's probe). Marionette's
  `quit()` refuses an instance it did not launch (marionette.py:1114-1117), so it is not used.
  Marionette listens on port 28282 (the scratch `prefs.js`'s `marionette.port`); `tb-shots`
  refuses to start while that port is taken, and `tb_shots.py` checks that the connected
  Thunderbird's `ProfD` is the scratch path before it touches anything.
- **One harness user at a time.** Only one task per wave runs Thunderbird: B in wave 1, D in
  wave 2, E in wave 3. Two runs at once would share the scratch path and the port.
- **Probed facts this plan relies on** (planning session and fold, 2026-10-13, Thunderbird 158.0
  Flatpak):
  - Chrome-context Marionette needs the single-dash flag `-remote-allow-system-access`; without it
    `set_context("chrome")` raises "System access is required". The client is
    `uv run --with marionette_driver python …`.
  - Headless screenshots of the main window work: `m.set_context(m.CONTEXT_CHROME)`,
    `m.set_window_rect(width=1600, height=1000)`, `m.screenshot(format="base64")`. A reader shot
    that includes the body is not yet proven (B step 5 proves it first).
  - `Services.prefs.setIntPref("ui.systemUsesDarkTheme", 1|0)` switches the window between dark and
    light live; `mail.threadpane.listview` 0/1 switches cards/table live (map "Views").
  - From the chrome window: `document.getElementById("tabmail").currentAbout3Pane` gives `a3`;
    `a3.displayFolder(uri)`, `a3.gDBView.getMsgHdrAt(i)`, `a3.threadTree.selectedIndex = i` open a
    message in the reader. `MailServices` comes from
    `ChromeUtils.importESModule("resource:///modules/MailServices.sys.mjs")`. The
    `incomingServer.hostName` property reads as undefined there; match accounts by `.type`.
  - `mail.addressDisplayFormat` (int, default 0) and `mail.displayname.version` (int, default 0)
    are static prefs (comm-central `mail/app/StaticPrefList.yaml`). `nsMsgDBView::FetchAuthor`
    caches the formatted sender per `mail.displayname.version`, and format 2 shows the name only,
    falling back to the address when a name spoofs one (`NoSpoofingSender`).
  - `mail.server.default.spamLevel` defaults to 100 (omni `defaults/pref`); Geoff's live prefs set
    no per-server `spamLevel`, so a user.js default of 0 turns the adaptive junk filter off for
    every account.
  - `mail.threadpane.cardsview.rowcount` defaults to 3 and adds `#threadTree.cards-row-compact` at
    2 (map "Views").
  - Message bodies go dark only under `(prefers-color-scheme: dark) and
    -moz-pref("mail.dark-reader.enabled")` (shared/messageBody.css:18-20, :109-114, :247-249;
    the pref defaults to true, all-thunderbird.js:620). A dark system with the reader toggled off
    shows a white body. A user sheet may use `-moz-pref()` (Stylo condition.rs:625 gates it on
    `chrome_rules_enabled()`, true for any non-Author origin, parser.rs:275-277).
  - A running profile holds a `lock` symlink, removed on a clean exit and left behind by SIGKILL;
    `.parentlock` stays on disk after any exit (nsProfileLock.cpp:339, :550, :561-563).
- **Commits.** One commit per task, subject starting with the task letter (`A: Add nord.css and
  its contrast check`), imperative mood, specific files only.
- **Clock.** At each wave's start the session writes `pass-task-clock` in its own worktree's git
  dir with `task=<ids>`, `start=<epoch>`, and `estimate=<the wave's figure>`: 125 for wave 1, 95
  for wave 2, 105 for wave 3, each covering the wave's merge and check. It checks the overrun when
  the wave's last step ends, then removes the file (pass-core "Clock stop"). Pair worktrees hold no
  clock file.
- **Pairs.** Each pair goes to two Agent-tool subagents (`subagent_type: "general-purpose"`,
  `isolation: "worktree"`, model `sonnet`, effort `medium`, `description` `thunderbird-nord-mail
  task <letter>`) after the session's last commit, each with its task's full text and this section
  verbatim. Each commits and never pushes. The session merges both, runs the wave's merge and
  check, runs the gate, and pushes. A merge conflict is a stop. In each pair only one task runs
  Thunderbird (see "One harness user at a time"). D runs in the session's own worktree.
- **Stops.** A red the session cannot fix in two attempts, a merge conflict, or a clock stop: write
  `docs/STATUS.md` on the branch (task, what failed, the one question), run `notify-send -u normal
  "thunderbird-nord-mail: stopped"`, and wait.
- **Scope.** A defect found outside a task goes to the PR body's "Found, not done" list with a
  proposed now, defer, or drop and a one-line reason.
- **CSS rules.** Every new rule refers to a `--mail-*` role or a `--nord*` palette variable from
  `nord.css`, never a hex value. A rule that overrides the GNOME theme matches or beats the theme
  rule's specificity and carries `!important` (map "GNOME theme card overrides"; customChrome.css
  loads last, so a tie wins). Message-body rules live in `customContent.css` outside its
  `@-moz-document` block, are scoped by the body classes in map "Message body", and all carry
  `!important` (body sheets are author origin). A comment names the theme or Thunderbird rule each
  override answers, with its file and a line number found by `grep -n` in the installed file at
  write time (the map's numbers for `mail.css` and `messageQuotes.css` are stale).

## Tasks

### Wave 1: A and B (a pair)

### A. The palette file and its contrast proof (85 min)

**Outcome.** `thunderbird/nord.css` defines the palette and the roles, including the reader's body
forms; `customChrome.css` and `customContent.css` import it and take their Nord values from it; a
script proves every role meets its threshold on every background in both modes, from `nord.css`
itself. A runs no Thunderbird.

**Files.** `thunderbird/nord.css` (new), `thunderbird/customChrome.css`,
`thunderbird/customContent.css`, `thunderbird/user.js`, `thunderbird/tools/contrast_check.py` (new).

**Steps.**
1. `nord.css` declares `--nord0` to `--nord15` on `:root` with the official hex values (measure,
   "Official Nord roles"; nordtheme.com/docs/colors-and-palettes). It then declares its own text
   lightness rule, `--mail-oklab-text`, as `max(l, 0.85) a b` under `@media (prefers-color-scheme:
   dark)` and `min(l, 0.5) a b` otherwise. That is the GNOME theme's rule (`--gnome-standalone-color-oklab`,
   theme light.css:57 and dark.css:10; measure confirms 0.85 and 0.5). The theme's rule already
   reaches content documents through its `userContent.css:1-2` imports. `nord.css` restates it so
   every role lives in one file and so the body forms in step 3 can key to the dark reader.
2. The roles, on `:root`, from the design's role map: `--mail-accent-fill` (raw nord10, for fills
   with white text); `--mail-accent` (nord8 through the text rule: unread dot, new sparkle,
   thread-unread marker); `--mail-attention` (nord13: flagged, To Do); `--mail-error` (nord11);
   `--mail-success` (nord14); `--mail-tag-1` to `--mail-tag-5` (nord11, nord12, nord14, nord13,
   nord15, each through the text rule). Text-rule roles use
   `oklab(from var(--nordN) var(--mail-oklab-text))`.
3. The reader's body forms:
   - A second text rule, `--mail-oklab-body`, resolves to the dark form only under
     `(prefers-color-scheme: dark) and -moz-pref("mail.dark-reader.enabled")`, the condition
     Thunderbird uses to darken a body ("Probed facts"). Everywhere else it resolves to the light
     form.
   - `--mail-body-accent` (nord8 through that rule) is for plain-text links and quote level 1.
   - `--mail-quote-2` and `--mail-quote-3` are `color-mix(in srgb, var(--mail-body-accent) N%,
     transparent)`, two steps with N set so each step reads lighter. That is the same mix form as
     the theme's hover and selection colours (light.css:109-111).
   - Only E's body-class-scoped rules read these, so declaring them on every document's `:root`
     changes nothing elsewhere. If E's shots show the media query does not match in a body, E
     switches these forms to `light-dark(<light form>, <dark form>)` (fold record, finding 5).
4. `customChrome.css`'s existing Nord block (`--gnome-accent-bg` and the four semantic `-bg`
   values) takes its values from the palette variables instead of hex, and its folder colours from
   `--nord*`. Same for the block inside `customContent.css`. `@import "nord.css";` is each file's
   first rule.
5. `user.js`: the To Do tag (`$label4`) becomes nord13 `#ebcb8b` with its comment updated; the
   other four tag colours stay.
6. `thunderbird/tools/contrast_check.py`, with module and function docstrings:
   - Parses `nord.css` (or the file `--css <path>` names) for the `--nordN` hex values and each
     role's source palette entry and adjustment (text rule, body rule, raw, or a mix step). A
     missing file or a role line it cannot read exits 2, distinct from a gated failure.
   - Ports the OKLab conversion, the WCAG 2.2 ratio, and APCA 0.0.98G-4g from
     `research_notes/…/nord_measure.py`, which carries self-tests (black on white 21:1, APCA
     +106.04 / -107.88); they become the script's `--self-test`. It applies the same sRGB clipping
     that script tabulates.
   - List backgrounds: `#threadTree` paints `--gnome-secondary-sidebar-background` (theme
     mail.css:82-84), and cards have no background of their own (mail.css:105). The surfaces are
     light `#f3f3f5` and its backdrop `#f6f6fa` (light.css:82, :161), and dark `#28282c` and its
     backdrop `#252529` (dark.css:23, :55). Hover and selection composite `color-mix(in srgb,
     currentColor 7%/10%, transparent)` (light.css:109-111) over each surface. The mix uses the
     row's own text colour, so a tagged row mixes its tag colour. A focused, selected, tagged row
     is measured with neutral text, because D restores it.
   - Reader backgrounds: the header, which paints `--gnome-window-background` (mail.css:15-17;
     `#fafafb` light, `#222226` dark, light.css:74 and dark.css:19), for the star and tag pills;
     the light body `#ffffff`; the dark-reader body `#18181b` (`--color-gray-90`, messenger
     colors.css:60); and a dark system with the reader off, which is a white body with the body
     forms in their light form.
   - Thresholds: text roles (`--mail-body-accent` as link text, the tag colours as table-row
     text) need WCAG 4.5:1. Non-text roles (unread dot, sparkle, flag, tag icons, quote level 1)
     need 3:1. Quote levels 2 and 3 are composited over each body background and reported but not
     gated, since indentation carries depth (design, "The reader"). APCA Lc prints beside every
     pair and never gates (report: no standing as a standard). Any gated failure prints a `FAIL`
     line and exits 1.
   - A failing pair is fixed in `nord.css`, which A owns. If the fix needs a clamp tighter than
     the theme's rule for a role, the commit body names the role and the surface, and the PR body
     repeats it (fold record, erratum 2).

**Acceptance.**
- `python3 thunderbird/tools/contrast_check.py --self-test` passes, and the plain run exits 0
  against A's `nord.css`.
- With `--css` on a scratch copy whose `--mail-body-accent` is raw nord10, the check exits 1 with
  a `FAIL` line for link text on a body background (raw nord10 measures 4.03:1 on `#ffffff` and
  4.4:1 on `#18181b`). Pointed at a missing file, it exits 2.
- `ruff check thunderbird/tools/` is clean.
- With comments stripped, the hex grep prints only `#fff` lines (white text on accent fills, the
  one allowed exception): `perl -0pe 's{/\*.*?\*/}{}gs' thunderbird/customChrome.css
  thunderbird/customContent.css | grep -nE '#[0-9a-fA-F]{3,8}\b'`.
- The gate passes against the baseline.

### B. The sync's profile mode and the screenshot harness (115 min)

**Outcome.** `thunderbird-theme-sync` can install into, and check, one scratch profile without
touching the theme clone or any live profile. One command builds that profile from tracked test
messages, runs Thunderbird headless, sets each message's state, and writes the screenshot set D and
E need. B is wave 1's only Thunderbird user.

**Files.** `bin/.local/bin/thunderbird-theme-sync`, `thunderbird/tools/tb-shots` (new, executable
bash entry point), `thunderbird/tools/tb_shots.py` (new, the Marionette driver, with docstrings),
`thunderbird/tools/fixtures/` (new: the test messages and the scratch profile's `prefs.js`),
`thunderbird/tools/README.md` (new, short: what each tool does and how to run it).

**Steps.**
1. `thunderbird-theme-sync`:
   - `LAYER` comes from the script's own real path (`readlink -f "$0"`, then `../../../thunderbird`
     relative to `bin/.local/bin/`), so a worktree copy installs its own files.
   - It copies, and `--check` compares, every top-level `thunderbird/*.css` instead of naming
     two files. A's `nord.css` is then covered once the wave merges, and B's worktree never needs
     A's file.
   - A new `--profile <dir>` option targets that one folder:
     - It skips the theme's `install.sh` (sync:116; its loop installs into every `Path=` in
       `profiles.ini`, install.sh:103-139). It also skips `require_profile` and the global
       `pgrep` running guard.
     - It copies the clone into `<dir>/chrome/thunderbird-gnome-theme`, writes the two import
       files, and copies the layer's `*.css` and `user.js` in. The installer's two prefs are
       already in the layer's `user.js` (user.js:7-10).
     - It uses the clone as it is, with no fetch, reset, clean or patch. Plain `check-drift` runs
       `--check` against the clone (check-drift:165-167), and the clone already carries the patch.
       A missing clone prints the existing `x theme clone missing` line and exits 1.
     - It refuses a folder whose `lock` symlink exists (a Thunderbird is using it). `.parentlock`
       never counts, since it stays on disk after every exit.
     - `--check --profile <dir>` checks only that folder.
     - `--profile` with no argument prints usage and exits 2. A missing folder prints an `x` line
       and exits 1.
   - The usage comment at the top documents the glob and the new mode.
2. Test messages, as `.eml` files concatenated into one mbox by `tb-shots`. All names, addresses
   and text are invented (`example.com`, `example.org`). Cover each case:
   - Unread and read messages; a long display name; a sender with no display name; a display name
     that is itself an email address different from the sender (the spoofing case).
   - A message with an attachment (multipart/mixed).
   - A three-message thread whose reply is unread while its root is read.
   - A plain-text (`format=fixed`) reply quoted three levels deep, ending in a `-- ` signature and
     containing a URL; the same as `format=flowed`.
   - An HTML reply nested with `<blockquote type="cite">` three levels deep.
   - An HTML Gmail reply using the exact markup in report "Neutral quotes…": `div.gmail_quote`
     wrapping `blockquote.gmail_quote` with the inline `border-left:1px #ccc solid` style.
   - A Yahoo reply (`div.yahoo_quoted`) and an Outlook reply (`#divRplyFwdMsg` after an `hr`), to
     show they stay unchanged.
3. The fixtures' `prefs.js` makes the profile a Local Folders-only, offline, wizard-free profile with
   `marionette.port` 28282 and `mailnews.start_page.enabled` false, and sets no key that
   `thunderbird/user.js` sets (see "The scratch profile"). Probe which prefs suppress the account
   wizard and point Local Folders at the mbox; record the working set in the file's comments.
4. `tb-shots <outdir> [--keep]`:
   - Refuses a non-empty `<outdir>` (exit 2), and refuses to start while port 28282 is taken.
   - Wipes a leftover scratch profile (from `--keep` or a crash) only while the port is free.
   - Builds the profile, writing `prefs.js` before first launch.
   - Runs `bin/.local/bin/thunderbird-theme-sync --profile` on it, resolving the path from its own
     location.
   - Starts Thunderbird as in "Thunderbird processes" and arms the `EXIT` trap. Then it runs
     `tb_shots.py` through `uv run --with marionette_driver`. A Marionette connection that never
     comes up times out with a message, and the trap still runs.
   - The trap stops Thunderbird. It deletes the profile unless `--keep` was given.
5. `tb_shots.py`:
   - Waits for the session, checks that `ProfD` is the scratch path (exits nonzero otherwise), and
     opens the Local Folders inbox.
   - First probe: opens the plain-text reply and takes one reader shot. The body text's pixels
     must appear in it. If they do not, B stops and reports, because E's proof rests on reader
     shots.
   - Sets states by Message-ID through the folder and header APIs: read and unread, flagged, the
     five tags (one message each, plus one carrying two tags), junk on one message, and "new" on
     one message if the API allows it. If "new" cannot be set, it prints why, and D reports that
     state as unverified.
   - Takes the screenshots in this order, so opening messages cannot change list states first:
     - In light and dark: cards view, table view, and a card list with one message selected and
       one hovered, if hover can be driven.
     - In light and dark: a table view whose focused selected row is a tagged message.
     - The reader for the plain-text, flowed, HTML-cite, Gmail, Yahoo and Outlook replies, plus
       the flagged-and-tagged message's header, in dark and in light.
     - The plain-text reader once more with a dark system and `mail.dark-reader.enabled` false,
       re-selecting the message after the pref changes.
   - Names each file `<view>-<mode>.png` or `reader-<case>-<mode>.png`, with mode `light`, `dark`,
     or `dark-reader-off`.

**Acceptance.**
- In a `mktemp -d` folder holding an empty `chrome/`, `bin/.local/bin/thunderbird-theme-sync
  --profile <dir>` installs, and `--check --profile <dir>` prints a match line. Editing the
  installed `customChrome.css` makes `--check` report a mismatch. A folder holding a `lock`
  symlink is refused. `--profile` with no argument exits 2. A missing folder exits 1.
- `git -C ~/.local/share/thunderbird-gnome-theme rev-parse HEAD` and its `status --short` print
  the same before and after a `--profile` run.
- `thunderbird/tools/tb-shots <new tmpdir>` exits 0 and writes every listed file. Reading three of
  them shows the test messages, not real mail, and a reader shot shows body text.
- A second run leaves no scratch profile behind.
- After a run, no harness Thunderbird is alive: the recorded instance id is absent from `flatpak
  ps --columns=instance`, `ss -ltn | grep -c ':28282 '` prints 0, and `ps -eo args | grep -c
  '[t]b-nord-harness'` prints 0.
- The gate passes against the baseline.

### Wave 1 merge and check (10 min)

The session merges A and B, then:

1. Runs the gate.
2. Runs `thunderbird/tools/tb-shots --keep "$(git rev-parse --absolute-git-dir)/tb-shots-baseline"`
   from its own worktree. The baseline stays there for E.
3. Reads one list shot from it, to confirm the Nord folder colours and accent still show (so
   `nord.css` loads).
4. Runs `--check --profile` on the kept profile and gets the match line. Then it edits the
   installed `nord.css` and confirms the `x` line names it.
5. Removes the kept profile and pushes.

### Wave 2: D (alone)

### D. The message list (95 min)

**Outcome.** Both list views follow design "The message list". D runs in the session's own
worktree and runs the harness itself.

**Files.** `thunderbird/customChrome.css`, `thunderbird/user.js`.

**Steps.**
1. `user.js`: `mail.addressDisplayFormat` 2; `mail.displayname.version` 1, with a comment that a
   later format change bumps it again; `mail.threadpane.cardsview.rowcount` 2;
   `mail.server.default.spamLevel` 0. Each pref carries a one-line comment naming its reason.
2. Cards:
   - Restore the read-status column the theme hides (theme mail.css:111-113, `display: none` on
     `.thread-card-column:first-child`, with `grid-template-columns: 1fr` at :108), so the unread
     dot and the new sparkle show. Scope the restore with `:not([data-properties~="dummy"])`, since
     Thunderbird hides that column on group-header rows (threadCard.css:554-560) and a user
     `!important` restore would beat it.
   - Colour `img.read-status` with `--mail-accent` through `--read-status-fill` and
     `--read-status-stroke`, or directly if the variables stay inert (map "Stock card styling").
   - Keep the theme's bold unread sender and subject (mail.css:169-170). Leave read cards with no
     glyph.
3. Thread-unread marker: the existing `hasUnread` and `hasNew` twisty rules take `--mail-accent`.
4. Table: the unread column dot takes `--mail-accent`. Answer the theme's icon rules (icons.css:205-217,
   the `:not(#hack)` rule on `--gnome-accent`) at equal specificity. Unread rows stay bold.
5. Stars, both views:
   - Unflagged stars take `opacity: 0` and show on `:hover`, `.selected`, and `:focus-within`.
     Layout does not shift, and the star stays in the accessibility tree and stays focusable
     (`visibility: hidden` would remove both; MDN `visibility`).
   - Flagged stars fill `--mail-attention`, set through `--gnome-toolbar-star-button` (icons.css:205-207).
     A stroke override also needs `-moz-context-properties: fill, stroke`, since the theme limits
     `.button-star` to `fill, fill-opacity` (icons.css:41, :69).
6. Replied, forwarded and redirected icons take the neutral icon fill (map "Stock card styling":
   hard-coded purple, blue and orange in threadCard.css:164-228 and threadPane.css:399-446).
7. Junk: remove the repo's junk card text rule (`customChrome.css`, the
   `[data-properties~="junk"] .card-container :is(.sender, .date, .subject)` rule), and answer the
   theme's red junk text (mail.css:173-174) with neutral text. The junk icon takes `--mail-error`.
8. Tags:
   - Each `tr[data-properties~="T_24labelN"]` gets `--tag-color: var(--mail-tag-N) !important`.
   - `body` gets `--tag-\$labelN-backcolor` overrides, so card tag icons and table rows show the
     adjusted colours. The variables are inline on `body`, so the override needs user
     `!important`. The escaped name is right: `setUpTagStyles` writes `--tag-${key}-backcolor`
     unescaped (about3Pane.js:5224), card icons read `var(--tag-${CSS.escape(key)}-backcolor)`
     (thread-card-tags.mjs:100-102), and CSS `--tag-\$label1-backcolor` names the same property.
   - A focused, selected, tagged table row keeps the neutral selection. Thunderbird paints that row
     with `--tag-color` as background and `--tag-contrast-color` text (threadPane.css:185-190);
     the contrast colour is computed from the raw pref colour (about3Pane.js:5215-5221).
     Restore the row to `--listbox-focused-selected-bg` and `--listbox-selected-color` at equal or
     higher specificity with `!important`. The tag icon keeps its colour through the theme's
     `fill: var(--tag-color, …)` (icons.css:209-210).
9. Dates and counts: confirm the theme's date opacity still passes 4.5:1 on A's list surfaces
   (`contrast_check.py`). If it fails, raise it in the rule and say so in the commit body.

**Acceptance.** D's own `tb-shots` run, checked in the light and dark card and table shots:

- Unread rows show a nord8 dot and bold text; read rows show neither; group headers show no dot.
- Senders show names only; the spoofing case shows its address.
- Cards are two rows.
- Unflagged stars are invisible except on the selected (and, if driven, hovered) row; the flagged
  star is yellow.
- Reply icons are grey; the junk test message has neutral text and a red junk icon.
- Each tag shows its role colour.
- The focused, selected, tagged row shows the theme's neutral selection with neutral text, and
  its tag icon in the tag's role colour.

`contrast_check.py` still exits 0. Gate passes against the baseline.

### Wave 3: E and F (a pair)

### E. The reader (95 min)

**Outcome.** The header and message bodies follow design "The reader", and the full screenshot set
proves the whole pass. E is wave 3's only Thunderbird user.

**Files.** `thunderbird/customChrome.css` (header rules, appended after D's),
`thunderbird/customContent.css` (body rules, outside the `@-moz-document` block), and
`thunderbird/nord.css` only to switch the body forms to `light-dark()` (step 6), adding or
renaming no role.

**Steps.**
1. Header (map "Message header"):
   - The subject keeps Thunderbird's large-subject style.
   - The From name is weight 600 at full contrast: `.recipient-multi-line-name`, which shows by
     default (`showFullAddress: true`, msgHdrView.js:2783-2786; messageHeader.css:989-1015), and
     the `.recipient-single-line` name for the full-address-off case.
     `.recipient-multi-line-address` and the date are secondary text.
   - Labels are hidden by default (`hideLabels: true`). When shown they keep
     `--message-header-label-opacity`; stack no extra dimming on them (report: light labels
     already near 4.9:1).
   - The flagged `#starMessageButton` fills `--mail-attention`, answering icons.css's toolbar fill
     (map "Theme icon rules").
   - `li.tag[style]` pills take `background-color: var(--mail-tag-N) !important` by tag key if the
     DOM exposes the key. Otherwise they keep Thunderbird's inline colour, which already comes from
     user.js's tag prefs, and the commit body says which.
2. Body quote text:
   - Scope with `:is(.moz-text-plain, .moz-text-flowed, .moz-text-html)`.
   - `blockquote[type="cite"]` gets `color: inherit !important`, answering messageQuotes.css:37's
     forced `color: var(--color-text-highlight) !important`.
3. Quote bars:
   - Level 1, any `blockquote[type="cite"]` under those classes, gets a 3 px solid
     `border-inline-start` in `--mail-body-accent`. The plain-text scope is
     `.moz-text-plain:not([graphical-quote="false"])`, so a user who turns graphical quotes off
     keeps Thunderbird's `border-style: none` (messageBody.css:89-92).
   - Level 2 (a quote inside a quote) takes `--mail-quote-2`, and level 3 and deeper take
     `--mail-quote-3`. Count nesting through every quote kind, so a Gmail quote inside a cite quote
     counts.
   - `blockquote.gmail_quote` under `.moz-text-html` gets the same bar colour by level, through
     `border-left-color` and `border-left-width` only (report: change only colour, plus width,
     keeping its margin and padding).
   - `div.gmail_quote`, `div.yahoo_quoted`, `.moz-cite-prefix` and Outlook markup get no rule.
4. Signatures: `:is(.moz-text-plain, .moz-text-flowed) :is(.moz-txt-sig, .moz-signature)` and
   `pre.moz-signature` take opacity 0.6, and 0.75 under `@media (prefers-color-scheme: dark) and
   -moz-pref("mail.dark-reader.enabled")`, the dark reader's own condition. Thunderbird's own 0.6
   is at messageQuotes.css:22-28.
5. Links:
   - `:is(.moz-text-plain, .moz-text-flowed) a[class^="moz-txt-link-"]` take `--mail-body-accent`
     with `text-decoration: underline !important`.
   - `:root { --color-text-highlight-dark: <the dark body form of nord8> !important }` recolours
     the dark reader's link cyan. It needs no document scoping: across omni.ja's CSS, only
     messageBody.css:249 (`a:link` under the dark-reader condition) and colors.css:196 read it,
     and the latter feeds only the quote colour step 2 replaces. Web pages load neither, and HTML
     mail's default links turn the adjusted nord8 in the dark reader, as the design intends.
   - HTML-mail links otherwise keep the sender's styling.
6. Body keying: the `dark-reader-off` shot shows the body forms in their light form (deep nord8
   links and bars on the white body, signature at 0.6). If it shows the dark form, the
   `-moz-pref()` query did not match. Switch the body forms in `nord.css` to `light-dark(<light
   form>, <dark form>)`, which follows the body's used `color-scheme` (Thunderbird's own quote
   colour works this way, colors.css:196). Rerun the reader shots and say which form held in the
   commit body.
7. The full set: run `tb-shots` for every file B lists. Compare `reader-yahoo-*` and
   `reader-outlook-*` with the baseline at the absolute path the session gives in the dispatch.

**Acceptance.** In the reader shots, light, dark, and `dark-reader-off`:

- Quoted text is body-coloured, not blue.
- Bars are 3 px nord8 at level 1, fading at levels 2 and 3, on the plain, flowed, HTML-cite and
  Gmail replies. The Yahoo and Outlook replies match the baseline.
- The `-- ` signature is dimmed.
- The plain-text URL is nord8 and underlined.
- In `dark-reader-off`, links, bars and the signature take the light forms on the white body.
- The header shows the name in weight 600 with the address dimmed, a yellow star on the flagged
  message, and tag pills in role colours.

`contrast_check.py` still exits 0. Gate passes against the baseline.

### F. The role map and the docs (30 min)

**Outcome.** The role map is written down for other clients, and the one-time steps after the
merge are documented.

**Files.** `thunderbird/README.md`, `bluefin/SECOND-WORKSTATION.md`.

**Steps.**
1. `README.md` gains a "Role map" section: design "The role map"'s table (role, Nord colour, the
   cue that works without colour), a sentence each on the Frost-for-state and Aurora-for-meaning
   split and on the lightness rule (including that the reader's body forms follow the dark reader,
   not the system alone), and a pointer to the report and to `nord.css` as the source of truth. It
   gains `nord.css` and `tools/` rows in its file table.
2. `README.md` gains an "After pulling a change" note, as numbered steps:
   1. Quit Thunderbird.
   2. Run `thunderbird-theme-sync`.
   3. Start Thunderbird.
   4. Once, after this pass: open the inbox, select all, and mark them as not junk (Shift+J),
      because turning the junk filter off leaves old junk marks in place. Leave each account's
      "Enable adaptive junk mail controls" box off, since checking it turns the filter back on for
      that account (am-junk.xhtml:57-63).
3. `SECOND-WORKSTATION.md` Part 3, step 3 (Thunderbird): add one sentence pointing at that README
   note.
4. Run `vale thunderbird/README.md thunderbird/tools/README.md`. The gate runs only Vale's test
   suites (`scripts/check.sh:69-70`).

**Acceptance.** The README table matches `nord.css`'s roles one for one (each role named in both,
body forms included). The `vale` run on both READMEs reports no errors. The runbook sentence links
the README section.

### Wave 3 merge and check (10 min)

The session merges E and F, runs the gate, runs the full `tb-shots` set into a new folder, reads
the reader and list shots against D's and E's acceptance, confirms `contrast_check.py` exits 0,
and pushes.

### Close (65 min)

1. Run the end-to-end check above; every item prints or shows what it names.
2. One `visual-verifier` dispatch (fresh context) gets the screenshot set and the design's sections
   "The message list" and "The reader" as the reference. Each design bullet becomes a device to
   grade; it returns COSMETIC and STRUCTURAL findings. A STRUCTURAL finding is fixed (one batched
   fix chain quoting each finding verbatim), then the shots rerun.
3. One `diff-reviewer` dispatch at whole-branch scope, against this plan and the design, loading
   `python-conventions` for the two `.py` files (dotfiles-pass checklist globs).
4. One `gitleaks git` scan of the branch history (dotfiles-pass close checklist; the gate scans
   only the working tree).
5. Screenshots for the PR:
   - Downscale the reader and list shots to 1200 px wide.
   - Commit them under `docs/research/2026-10-13-mail-colour-evidence/shots/`; only test
     messages appear in them.
   - Embed them in the PR body by their `raw.githubusercontent.com` URLs on the branch.
6. PR body: `## Brief` per `~/.claude/docs/voice/approval-brief.md`. Under it go what landed, the
   score (pass-core "Score"), the screenshots, any role A clamped tighter than the theme's rule,
   and "Found, not done" with the gate baseline as "defer". Its "If you approve" lists Geoff's
   post-merge steps from F. The design errata the fold record owes are named in the PR body, so
   Geoff can apply or drop them.
7. Hand over: `eval "$(mise activate bash)"` first (`approval-queue` needs `node`), then
   `approval-queue pr glw907/workstation "<title>" <n>` as a background command. On approve, merge
   with `gh pr merge <n> --merge --match-head-commit <head>` and pull the main checkout per
   pass-core "Close". Do not run `thunderbird-theme-sync` on the live profile; Geoff does that with
   Thunderbird quit. On reject, fix forward from the note.

## Later

- A `runner` pass to make the gate machine-independent: the ratchet's dead-reference check on
  paths that only exist on some machines.
- Poplar implements the role map in its own theme.
- Quote bars for Outlook replies, if a reliable wrapper ever appears.
- Verify Fastmail's quote markup on a real Fastmail-sent message (report gap).
