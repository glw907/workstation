# Thunderbird Nord mail layer: implementation plan

**Design:** `docs/superpowers/specs/2026-10-13-thunderbird-nord-mail-design.md` (approved by Geoff,
2026-10-13; the "Who merges the PR" decision came back unanswered, so the recommended choice
holds: Geoff reads the screenshots before merge). It runs about a page, and the mechanisms live in
the evidence below, so no separate spec was written (`spec-plan-review` "Depth scales with risk").
**Evidence:** the research report,
`docs/superpowers/research/2026-10-13-mail-colour-evidence/reports/Mail colour readability evidence.md`
(cited as "report"); its notes in the sibling `research_notes/` folder, including
`nord_palette_measured.md` and its script `nord_measure.py` (cited as "measure"); and the styling
map of Thunderbird 158, `docs/superpowers/research/2026-10-13-mail-colour-evidence/thunderbird-css-map.md`
(cited as "map"). **Review:** the mechanics lens and the fold record,
`docs/superpowers/research/2026-10-13-thunderbird-nord-mail-{review-mechanics,plan-fold}.md`.

**Outcome.** On a machine that has pulled this pass and run `thunderbird-theme-sync`, Thunderbird's
message list and reader follow the design: a nord8 unread dot plus bold, names-only senders,
two-row cards, hidden unflagged stars, neutral quoted text with fading nord8 bars, underlined
plain-text links, mode-tuned signatures, and the local junk filter off. One palette file,
`thunderbird/nord.css`, defines every colour and role, and `thunderbird/README.md` carries the role
map. A headless screenshot harness and a contrast check under `thunderbird/tools/` prove it on test
messages, never on real mail.

**Pass class:** `ordinary`. Every path is `thunderbird/**`, `bin/.local/bin/thunderbird-theme-sync`
(not in the adapter's runner or auth-data lists), `bluefin/SECOND-WORKSTATION.md`, or
`docs/superpowers/**`. No `live-account` flag: nothing calls a Cloudflare, GitHub (beyond the PR),
or npm account, and the harness runs Thunderbird offline against a scratch profile.

**Out of scope:** the design's list (the sender's HTML design, Outlook and Yahoo quote bars, the
compose window, the calendar, folder-pane changes beyond the colours already on `main`, layout
changes other than two-row cards, poplar's own implementation). Also out: any change to Geoff's
live Thunderbird profile, any edit to `scripts/**` or `tests/**`, and the gate's machine-state
failures (see "Gate").

**End-to-end check.** On the close head:

1. `python3 thunderbird/tools/contrast_check.py` exits 0 and prints every role against every
   background in both modes, with no `FAIL` line.
2. `thunderbird/tools/tb-shots` builds the scratch profile, installs the theme with
   `bin/.local/bin/thunderbird-theme-sync --profile <scratch>`, and writes the screenshot set listed
   in task E. Each screenshot shows what E's acceptance names, read by the session and by a
   fresh-context `visual-verifier` dispatch.
3. `bin/.local/bin/thunderbird-theme-sync --check --profile <scratch>` prints a match line that
   covers `nord.css`.
4. `bash scripts/gate.sh` prints `gate exit:` with no failure beyond the pavilion baseline below.

**Clock estimate:** 330 path minutes. A 40 with B 90 (pair), C 45 with D 90 (pair), E 90 with F 25
(pair), close 60: the path is 90 + 90 + 90 + 60 = 330, under the design's 300 plus its margin.

## Launch

Prompt file: `docs/superpowers/plans/2026-10-13-thunderbird-nord-mail-prompt.txt`. The plan lives
on branch `worktree-thunderbird-nord-mail` (planning commits). The executor continues that branch:
its first act after `EnterWorktree` (name `thunderbird-nord-mail-build`) is `git merge --no-edit
worktree-thunderbird-nord-mail`. Launch from the main checkout after every check prints what its
comment names:

```bash
git -C ~/.dotfiles fetch origin
git -C ~/.dotfiles branch --show-current                # must print main
git -C ~/.dotfiles rev-list --count HEAD..origin/main   # must print 0
git -C ~/.dotfiles rev-list --count origin/main..HEAD   # must print 0
git -C ~/.dotfiles status --porcelain                   # must print nothing
git -C ~/.dotfiles rev-parse worktree-thunderbird-nord-mail origin/worktree-thunderbird-nord-mail   # two equal lines
claude agents --json                                    # no live session named dotfiles-thunderbird-nord-mail
cd ~/.dotfiles && claude --bg --model sonnet --effort medium --name dotfiles-thunderbird-nord-mail \
  "$(git -C ~/.dotfiles show worktree-thunderbird-nord-mail:docs/superpowers/plans/2026-10-13-thunderbird-nord-mail-prompt.txt)"
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
  baseline under "Found, not done" with a proposed "defer" (fixing it is a `runner` pass).
- **Live profile untouched.** Geoff's Thunderbird and its profile
  (`~/.var/app/org.mozilla.thunderbird/.thunderbird/jqkfj0f7.default-release`) are never written,
  launched, or killed. `thunderbird-theme-sync` runs only with `--profile <scratch>` (task A adds
  the flag). Only `bin/.local/bin/thunderbird-theme-sync` from the worktree is run, never the bare
  name, which is the stowed main-checkout copy.
- **The scratch profile.** The Flatpak sandbox sees only `~/.var/app/org.mozilla.thunderbird/` of
  the home directory, so the scratch profile lives at
  `~/.var/app/org.mozilla.thunderbird/.thunderbird/tb-nord-harness` (the path inside the sandbox
  is `/var/home/glw907/.thunderbird/tb-nord-harness`). The harness creates and deletes it.
- **Thunderbird processes.** The harness starts Thunderbird with `flatpak run
  --env=MOZ_HEADLESS=1 org.mozilla.thunderbird --profile /var/home/glw907/.thunderbird/tb-nord-harness
  --no-remote --marionette -remote-allow-system-access`, keeps its PID, and stops it with `kill
  <pid>`. Never `pkill -f` or `flatpak kill`: a pattern can match the session's own shell, and
  `flatpak kill` would stop Geoff's Thunderbird. Marionette listens on port 28282 (the profile's
  `marionette.port` pref), so it never collides with another Thunderbird.
- **Probed facts this plan relies on** (planning session, 2026-10-13, Thunderbird 158.0 Flatpak):
  - Chrome-context Marionette needs the single-dash flag `-remote-allow-system-access`; without it
    `set_context("chrome")` raises "System access is required". The client is
    `uv run --with marionette_driver python …`.
  - Headless screenshots of the main window work: `m.set_context(m.CONTEXT_CHROME)`,
    `m.set_window_rect(width=1600, height=1000)`, `m.screenshot(format="base64")`.
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
- **Commits.** One commit per task, subject starting with the task letter (`A: Add nord.css and
  install it with the theme`), imperative mood, specific files only.
- **Clock.** At each wave's start the session writes `pass-task-clock` in its own worktree's git
  dir with `task=<ids>`, `start=<epoch>`, and `estimate=<the wave's longer task>`, checks the
  overrun when both return, then removes the file (pass-core "Clock stop"). Pair worktrees hold
  no clock file.
- **Pairs.** Each pair goes to two Agent-tool subagents (`subagent_type: "general-purpose"`,
  `isolation: "worktree"`, model `sonnet`, effort `medium`) after the session's last commit, each
  with its task's full text and this section verbatim. Each commits and never pushes. The session
  merges both, runs the gate, and pushes. A merge conflict is a stop. A pair subagent that needs
  Thunderbird runs the harness only after the session says so: two harness runs at once would
  share the scratch path and port.
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
  override answers, with its file and line from the map.

## Tasks

### Wave 1: A and B (a pair)

### A. The palette file, wired into the theme install (40 min)

**Outcome.** `thunderbird/nord.css` defines the palette and the roles; `customChrome.css` and
`customContent.css` import it and take their Nord values from it; `thunderbird-theme-sync`
installs it, checks it, and can target one profile.

**Files.** `thunderbird/nord.css` (new), `thunderbird/customChrome.css`,
`thunderbird/customContent.css`, `thunderbird/user.js`, `bin/.local/bin/thunderbird-theme-sync`.

**Steps.**
1. `nord.css` declares `--nord0` to `--nord15` on `:root` with the official hex values (measure,
   "Official Nord roles"; nordtheme.com/docs/colors-and-palettes). It then declares its own text
   lightness rule, `--mail-oklab-text`, as `max(l, 0.85) a b` under `@media (prefers-color-scheme:
   dark)` and `min(l, 0.5) a b` otherwise. That is the GNOME theme's rule (map "Current repo
   overrides"; measure confirms 0.85 and 0.5 upstream), restated so message bodies, which the theme
   never reaches, get it too.
2. The roles, on `:root`, from the design's role map: `--mail-accent-fill` (raw nord10, for fills
   with white text); `--mail-accent` (nord8 through the text rule: unread dot, new sparkle,
   thread-unread marker, links, quote bar level 1); `--mail-attention` (nord13: flagged, To Do);
   `--mail-error` (nord11); `--mail-success` (nord14); `--mail-tag-1` to `--mail-tag-5` (nord11,
   nord12, nord14, nord13, nord15, each through the text rule); `--mail-quote-2` and
   `--mail-quote-3` (`--mail-accent` mixed toward the surface, two steps, values set so level 1
   meets 3:1 and each step reads lighter; C measures them). Text-rule roles use
   `oklab(from var(--nordN) var(--mail-oklab-text))`.
3. `customChrome.css`'s existing Nord block (`--gnome-accent-bg` and the four semantic `-bg`
   values) takes its values from the palette variables instead of hex, and its folder colours from
   `--nord*`. Same for the block inside `customContent.css`. `@import "nord.css";` is each file's
   first rule.
4. `user.js`: the To Do tag (`$label4`) becomes nord13 `#ebcb8b` with its comment updated; the
   other four tag colours stay.
5. `thunderbird-theme-sync`:
   - `LAYER` comes from the script's own real path (`readlink -f "$0"`, then `../../../thunderbird`
     relative to `bin/.local/bin/`), so a worktree copy installs its own files.
   - It copies `nord.css` beside `customChrome.css` and `customContent.css`, and `--check` compares
     it too.
   - A new `--profile <dir>` option installs into, or checks, that one profile directory instead
     of every profile in `profiles.ini`. With `--profile`, the theme clone update still runs.
   - The usage comment at the top documents both changes.

**Acceptance.** In a scratch directory laid out like a profile (`mktemp -d`, holding an empty
`chrome/`): `bin/.local/bin/thunderbird-theme-sync --profile <dir>` installs, and `--check
--profile <dir>` prints a match line; editing the installed `nord.css` makes `--check` report a
mismatch. `grep -c '#[0-9a-fA-F]\{6\}' thunderbird/customChrome.css` drops to 0 outside comments
(every colour comes from `nord.css`). Gate passes against the baseline.

### B. The screenshot harness and test messages (90 min)

**Outcome.** One command builds a scratch Thunderbird profile from tracked test messages, runs
Thunderbird headless, sets each message's state, and writes the screenshot set E needs.

**Files.** `thunderbird/tools/tb-shots` (new, executable bash entry point),
`thunderbird/tools/tb_shots.py` (new, the Marionette driver), `thunderbird/tools/fixtures/` (new:
the test messages and the scratch profile's `user.js`), `thunderbird/tools/README.md` (new, short:
what each tool does and how to run it).

**Steps.**
1. Test messages, as `.eml` files concatenated into one mbox by `tb-shots`. All names, addresses
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
2. The fixtures' `user.js` makes the profile a Local Folders-only, offline, wizard-free profile with
   `marionette.port` 28282 and `mailnews.start_page.enabled` false. Probe which prefs suppress the
   account wizard and point Local Folders at the mbox; record the working set in the file's
   comments.
3. `tb-shots <outdir> [--keep]`:
   - Builds the profile.
   - Runs `bin/.local/bin/thunderbird-theme-sync --profile` on it, resolving the path from its own
     location.
   - Starts Thunderbird as in "Thunderbird processes" and runs `tb_shots.py` through `uv run --with
     marionette_driver`.
   - Stops Thunderbird and deletes the profile unless `--keep`.
4. `tb_shots.py`:
   - Waits for the session and opens the Local Folders inbox.
   - Sets states by Message-ID through the folder and header APIs: read and unread, flagged, the
     five tags (one message each, plus one carrying two tags), junk on one message, and "new" on
     one message if the API allows it. If "new" cannot be set, it prints why, and E reports that
     state as unverified.
   - Takes the screenshots in this order, so opening messages cannot change list states first.
     In light and dark: cards view, table view, and a card list with one message selected and one
     hovered if hover can be driven. Then the reader for the plain-text, flowed, HTML-cite, Gmail,
     Yahoo and Outlook replies, plus the flagged-and-tagged message's header, in dark and in
     light.
   - Names each file `<view>-<mode>.png` or `reader-<case>-<mode>.png`.

**Acceptance.** B depends on A's `--profile` flag, so the session runs this after merging the
pair: `thunderbird/tools/tb-shots <tmpdir>` exits 0 (before C to E change anything visible) and
writes every listed file. These shots are the baseline E compares against; reading three of them shows the test
messages, not real mail. A second run leaves no scratch profile behind, and no Thunderbird process
from the run is alive afterwards (`ps -eo args | grep -c '[t]b-nord-harness'` prints 0). Gate
passes against the baseline.

### Wave 2: C and D (a pair)

### C. The contrast check (45 min)

**Outcome.** A script proves every role meets its threshold on every background in both modes,
from the values in `nord.css` itself.

**Files.** `thunderbird/tools/contrast_check.py` (new).

**Steps.**
1. Parse `thunderbird/nord.css` for the `--nordN` hex values and each role's source palette entry
   and adjustment (text rule, raw, or a mix step). A role whose line the parser cannot read is an
   error, not a skip.
2. Port the OKLab conversion, the WCAG 2.2 ratio, and APCA 0.0.98G-4g from
   `research_notes/…/nord_measure.py` (it carries self-tests: black on white 21:1, APCA +106.04 /
   -107.88; keep them as the script's `--self-test`). Apply the same sRGB clipping that script
   tabulates.
3. Backgrounds: the theme's dark `#222226`, `#1e1e1e`, `#28282c`, `#2e2e32`, the dark card
   (`rgba(255,255,255,0.08)` over `#1e1e1e`), and light `#fafafb`, `#ffffff`, `#ebebed`,
   `#f2f2f4` (report, measurement tables); the dark message body `#18181b` (map "Message body",
   dark reader); and the selected-row and hover backgrounds the theme derives (`--gnome-selected-color`
   10% and `--gnome-hover-color` 7% of the view colour over the view background, map "Theme
   variables"), each in both modes.
4. Thresholds: text roles (`--mail-accent` as link text, the tag colours as table-row text) need
   WCAG 4.5:1; non-text roles (unread dot, sparkle, flag, tag icons, quote level 1) need 3:1. Quote
   levels 2 and 3 are reported but not gated, since indentation carries depth (design, "The
   reader"). APCA Lc is printed beside every pair and never gates (report: no standing as a
   standard). Exit 1 on any gated failure, printing `FAIL` lines.

**Acceptance.** `python3 thunderbird/tools/contrast_check.py --self-test` passes;
`python3 thunderbird/tools/contrast_check.py` exits 0 against A's `nord.css`. Changing
`--mail-accent` in a scratch copy to raw nord10 makes it exit 1 with a `FAIL` line on a light
background. `ruff check thunderbird/tools/` is clean. If a role fails on a background, the fix
goes into `nord.css` (task A's file) only by stopping and asking the session, since D owns no part
of `nord.css`. Report the failing pairs instead.

### D. The message list (90 min)

**Outcome.** Both list views follow design "The message list".

**Files.** `thunderbird/customChrome.css`, `thunderbird/user.js`.

**Steps.**
1. `user.js`: `mail.addressDisplayFormat` 2; `mail.displayname.version` 1, with a comment that a
   later format change bumps it again; `mail.threadpane.cardsview.rowcount` 2;
   `mail.server.default.spamLevel` 0. Each pref carries a one-line comment naming its reason.
2. Cards:
   - Restore the read-status column the theme hides (map: mail.css:145-147 `display:none` on
     `.thread-card-column:first-child`, and `grid-template-columns: 1fr` at :137-143) so the
     unread dot and the new sparkle show.
   - Colour `img.read-status` with `--mail-accent` through `--read-status-fill` and
     `--read-status-stroke`, or directly if the variables stay inert (map "Stock card styling").
   - Keep the theme's bold unread sender and subject. Leave read cards with no glyph.
3. Thread-unread marker: the existing `hasUnread` and `hasNew` twisty rules take `--mail-accent`.
4. Table: the unread column dot takes `--mail-accent`. Answer map "Theme icon rules" (icons.css
   :205-217 `:not(#hack)` rule on `--gnome-accent`) at equal specificity. Unread rows stay bold.
5. Stars, both views:
   - Unflagged stars hide unless the row is hovered or selected. Use `visibility: hidden`, so
     layout does not shift and the star stays in the accessibility tree.
   - Flagged stars fill and stroke `--mail-attention`, set through `--gnome-toolbar-star-button`
     (map "Theme icon rules"), plus a stroke override if the stroke stays the theme's.
6. Replied, forwarded and redirected icons take the neutral icon fill (map "Stock card styling":
   hard-coded purple, blue and orange in threadCard.css:164-228 and threadPane.css:399-446).
7. Junk: remove the repo's junk card text rule (`customChrome.css`, the
   `[data-properties~="junk"] .card-container :is(.sender, .date, .subject)` rule), and answer the
   theme's red junk text (mail.css:207-209) with neutral text. The junk icon takes `--mail-error`.
8. Tags:
   - Each `tr[data-properties~="T_24labelN"]` gets `--tag-color: var(--mail-tag-N) !important`.
   - `body` gets `--tag-\$labelN-backcolor` overrides (map "Tags": inline on `body`, so user
     `!important`), so card tag icons and table rows show the adjusted colours.
   - Probe that the escaped custom-property name matches what `setUpTagStyles` writes, by reading
     `document.body.style` in the harness.
9. Dates and counts: confirm the theme's date opacity still passes 4.5:1 on the card backgrounds
   (C's backgrounds). If it fails, raise it in the rule and say so in the commit body.

**Acceptance.** `tb-shots` (run by the session after merging the pair, per "Pairs"), checked in the
light and dark card and table shots:

- Unread rows show a nord8 dot and bold text; read rows show neither.
- Senders show names only; the spoofing case shows its address.
- Cards are two rows.
- Unflagged stars are invisible except on the selected (and, if driven, hovered) row; the flagged
  star is yellow.
- Reply icons are grey; the junk test message has neutral text and a red junk icon.
- Each tag shows its role colour.

Gate passes against the baseline.

### Wave 3: E and F (a pair)

### E. The reader (90 min)

**Outcome.** The header and message bodies follow design "The reader", and the full screenshot set
proves the whole pass.

**Files.** `thunderbird/customChrome.css` (header rules, appended after D's), `thunderbird/customContent.css`
(body rules, outside the `@-moz-document` block).

**Steps.**
1. Header (map "Message header"):
   - The subject keeps Thunderbird's large-subject style.
   - `.recipient-multi-line-name` in the From row is weight 600 at full contrast;
     `.recipient-multi-line-address` and the date are secondary text.
   - Labels keep `--message-header-label-opacity`; stack no extra dimming on them (report: light
     labels already near 4.9:1).
   - The flagged `#starMessageButton` fills `--mail-attention`, answering icons.css's toolbar fill
     (map "Theme icon rules").
   - `li.tag[style]` pills take `background-color: var(--mail-tag-N) !important` by tag key if the
     DOM exposes the key. Otherwise they keep Thunderbird's inline colour, which already comes from
     user.js's tag prefs, and the commit body says which.
2. Body quote text:
   - Scope with `:is(.moz-text-plain, .moz-text-flowed, .moz-text-html)`.
   - `blockquote[type="cite"]` gets `color: inherit !important`, answering messageQuotes.css:75-83's
     forced `--color-text-highlight`.
3. Quote bars:
   - Level 1, any `blockquote[type="cite"]` under those classes, gets a 3 px solid
     `border-inline-start` in `--mail-accent`.
   - Level 2 (a quote inside a quote) takes `--mail-quote-2`, and level 3 and deeper take
     `--mail-quote-3`. Count nesting through every quote kind, so a Gmail quote inside a cite quote
     counts.
   - `blockquote.gmail_quote` under `.moz-text-html` gets the same bar colour by level, through
     `border-left-color` and `border-left-width` only (report: change only colour, plus width,
     keeping its margin and padding).
   - `div.gmail_quote`, `div.yahoo_quoted`, `.moz-cite-prefix` and Outlook markup get no rule.
4. Signatures: `:is(.moz-text-plain, .moz-text-flowed) :is(.moz-txt-sig, .moz-signature)` and
   `pre.moz-signature` take opacity 0.6, and 0.75 under `@media (prefers-color-scheme: dark)`.
   Probe in the dark shots that the media query matches inside message bodies. If it does not, use
   the dark reader's `:root` colour-scheme instead and say which in the commit body.
5. Links:
   - `:is(.moz-text-plain, .moz-text-flowed) a[class^="moz-txt-link-"]` take `--mail-accent` with
     `text-decoration: underline !important`.
   - In dark mode, `:root { --color-text-highlight-dark: <adjusted nord8> !important }` inside
     message documents recolours the dark reader's link cyan (map "Message body"). Scope it so web
     pages are untouched. Probe the scoping, for example with `:root:has(> body > .moz-text-html)`
     or the body classes, and record it.
   - HTML-mail links otherwise keep the sender's styling.
6. The full set: run `tb-shots` for every file B lists.

**Acceptance.** In the reader shots, light and dark:

- Quoted text is body-coloured, not blue.
- Bars are 3 px nord8 at level 1, fading at levels 2 and 3, on the plain, flowed, HTML-cite and
  Gmail replies. The Yahoo and Outlook replies match how they looked in B's baseline run.
- The `-- ` signature is dimmed.
- The plain-text URL is nord8 and underlined.
- The header shows the name in weight 600 with the address dimmed, a yellow star on the flagged
  message, and tag pills in role colours.

`contrast_check.py` still exits 0. Gate passes against the baseline.

### F. The role map and the docs (25 min)

**Outcome.** The role map is written down for other clients, and the one-time steps after the
merge are documented.

**Files.** `thunderbird/README.md`, `bluefin/SECOND-WORKSTATION.md`.

**Steps.**
1. `README.md` gains a "Role map" section: design "The role map"'s table (role, Nord colour, the
   cue that works without colour), a sentence each on the Frost-for-state and Aurora-for-meaning
   split and on the lightness rule, and a pointer to the report and to `nord.css` as the source of
   truth. It gains `nord.css` and `tools/` rows in its file table.
2. `README.md` gains an "After pulling a change" note, as numbered steps:
   1. Quit Thunderbird.
   2. Run `thunderbird-theme-sync`.
   3. Start Thunderbird.
   4. Once, after this pass: open the inbox, select all, and mark them as not junk (Shift+J),
      because turning the junk filter off leaves old junk marks in place.
3. `SECOND-WORKSTATION.md` Part 3, step 3 (Thunderbird): add one sentence pointing at that README
   note.

**Acceptance.** The README table matches `nord.css`'s roles one for one (each role named in both).
The README's new section passes the gate's Vale leg. The runbook sentence links the README section.

### Close (60 min)

1. Run the end-to-end check above; every item prints or shows what it names.
2. One `visual-verifier` dispatch (fresh context) gets the screenshot set and the design's sections
   "The message list" and "The reader" as the reference. Each design bullet becomes a device to
   grade; it returns COSMETIC and STRUCTURAL findings. A STRUCTURAL finding is fixed (one batched
   fix chain quoting each finding verbatim), then the shots rerun.
3. One `diff-reviewer` dispatch at whole-branch scope, against this plan and the design.
4. Screenshots for the PR:
   - Downscale the reader and list shots to 1200 px wide.
   - Commit them under `docs/superpowers/research/2026-10-13-mail-colour-evidence/shots/`; only test
     messages appear in them.
   - Embed them in the PR body by their `raw.githubusercontent.com` URLs on the branch.
5. PR body: `## Brief` per `~/.claude/docs/voice/approval-brief.md`. Under it go what landed, the
   score (pass-core "Score"), the screenshots, and "Found, not done" with the gate baseline as
   "defer". Its "If you approve" lists Geoff's post-merge steps from F.
6. Hand over: `eval "$(mise activate bash)"` first (`approval-queue` needs `node`), then
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
