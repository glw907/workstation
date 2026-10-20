# Thunderbird Nord mail layer: plan review fold

This record folds `2026-10-13-thunderbird-nord-mail-review-mechanics.md` (25 findings) into
`docs/superpowers/plans/2026-10-13-thunderbird-nord-mail.md` and its launch prompt, 2026-10-13.
Each finding was checked against source before it was acted on. The approved design was not
edited. Task letters below are the revised plan's. The contrast check, which was old task C, is
now part of A. A and B own different files, D runs alone, and E pairs with F (finding 8).

Sources read for this fold:

- **Repo.** The sync script (`bin/.local/bin/thunderbird-theme-sync`, whole), `thunderbird/user.js`,
  `customChrome.css`, `customContent.css` (hex lines), `scripts/check.sh:39,69-70,84`,
  `scripts/check-py-comments.sh`, `bin/.local/bin/check-drift:165-167`,
  `claude/.claude/settings.json:6-8` (`worktree.baseRef: "head"`), `.claude/skills/dotfiles-pass`,
  and `pass-core` "Plan", "Pairs" and "Clock stop".
- **Theme clone.** `scripts/install.sh` (whole), `userContent.css:1-2`, `theme/colors/light.css` and
  `dark.css` (surfaces, text rule, hover and selection mixes, backdrop variants),
  `theme/parts/mail.css:15-17,60-128,161-174,211-213`, `theme/parts/icons.css:36-70,205-217,405-412`, and
  `variables.css:66-67`. Also `git status` and `git apply --reverse --check` of the carried patch,
  both read-only.
- **Thunderbird 158 omni.ja** (unzipped to scratch). `shared/messageBody.css`, `messageQuotes.css`,
  `colors.css:60,154,196`, `shared/threadPane.css:165-195,356,399-446`,
  `shared/threadCard.css:164-228,550-561`, `shared/messageHeader.css:989-1015`,
  `about3Pane.js:5210-5226`, `thread-card-tags.mjs:95-105`, `msgHdrView.js:2783-2786`,
  `aboutMessage.xhtml:1846-1856`, `am-junk.xhtml:57-63`, `am-junk.js:162-163`,
  `defaults/pref/all-thunderbird.js:620-629` and `mailnews.js:285`. A grep of every `.css` in
  omni.ja for `color-text-highlight` readers.
- **Upstream source (raw GitHub, `main`).** Stylo `servo/components/style/queries/condition.rs`
  (`MozPrefFeature::parse`, :618-626) and `parser.rs:275-277`. `toolkit/profile/nsProfileLock.cpp`
  (:339, :418-420, :550, :561-563). `modules/libpref/Preferences.cpp:5022-5024,5514-5522`.
  `xpcom/io/nsAppDirectoryServiceDefs.h:60`. `testing/marionette/client/marionette_driver/marionette.py:1089-1117`.
  flatpak `app/flatpak-builtins-kill.c:74-77,100-101`.
- **Local docs and state.** `flatpak run --help`, `flatpak-run(1)` (`--instance-id-fd`), and
  `flatpak-kill(1)`. `ss -ltn` shows port 28282 free. `profiles.ini` holds only the two live
  profiles: the planning session's `claude-view` folder, launched with `--profile`, was never
  added to it.

## Dispositions

| # | Finding | Disposition |
|---|---|---|
| 1 | Leftover Thunderbird holds port 28282 | Folded. The orphan was already stopped by the planning session, and `ss -ltn` shows the port free. Launch gains `ss -ltn \| grep -c ':28282 '` printing 0. B: `tb-shots` refuses to start while the port is taken, and `tb_shots.py` checks `Services.dirsvc.get("ProfD", Ci.nsIFile).path` against the harness path before it touches anything (`ProfD` is `NS_APP_USER_PROFILE_50_DIR`, nsAppDirectoryServiceDefs.h:60). |
| 2 | `kill <pid>` of `flatpak run` does not stop Thunderbird | Folded in part. "Thunderbird processes", B step 4 and the prompt now start Thunderbird with `flatpak run --instance-id-fd=3 … 3>"$tmp/instance"` (flatpak-run(1)). An `EXIT` trap stops it with `flatpak kill <that id>`, and the trap kills only a numeric id. flatpak-kill(1) accepts "the numeric instance ID". kill.c:100-101 matches an instance by app id *or* id, and :74-77 sends SIGKILL to its child pid, so `flatpak kill org.mozilla.thunderbird` would kill Geoff's instance too. The planning session's `flatpak kill 3098975677` freed the port, which is a measured success. **Refused:** the graceful `m.quit()` first. `Marionette.quit()` raises "quit() can only be called on Gecko instances launched by Marionette" (marionette.py:1114-1117), and the scratch profile is thrown away, so an unclean stop costs nothing. |
| 3 | `--profile` as specified writes the live profile or cannot install | Folded, B step 1. Verified: `sync()` runs `install.sh -f "$TB_DIR"` (sync:116), whose loop installs into every `Path=` in `profiles.ini` (install.sh:103-139). Its `saveProfile` copies the clone, rewrites both import files and edits `user.js` (:26-101). `-p` still needs `profiles.ini` (:103-107). Under `--profile` the sync skips `install.sh`, `require_profile` and the global `pgrep` guard. It copies the clone into `<dir>/chrome/thunderbird-gnome-theme`, writes the two import files, and copies the layer's `*.css` and `user.js`. Nothing is lost: the installer's two prefs are already in the layer's `user.js` (user.js:7-10), which the sync copies over the installer's anyway (sync:123). `check()` takes the same one-folder override. **Corrected:** the in-use guard is the `<dir>/lock` symlink only. On Unix, Gecko creates `lock` as a symlink and unlinks it on unlock (nsProfileLock.cpp:339, :418-420, :550), but it never removes `.parentlock` ("Don't remove it", :561-563), so a `.parentlock` test would refuse every profile that has ever run. |
| 4 | Sync overwrites the harness's `user.js` | Folded, B steps 2-3. The fixture prefs go in the scratch profile's `prefs.js` before first launch, with keys disjoint from `thunderbird/user.js`. libpref reads `prefs.js` and then `user.js` (Preferences.cpp:5022-5024, `ReadSavedPrefs` then `ReadUserOverridePrefs`, :5514-5522). So the layer's `user.js` lands whole, `--check` compares it exactly, and the fixture prefs survive. The fixture file is renamed `fixtures/prefs.js`. |
| 5 | Body roles track the system scheme, not the dark reader | Folded, A steps 1 and 3, A's check, B's shot list, E steps 3-5. Verified: Thunderbird darkens a body only under `(prefers-color-scheme: dark) and -moz-pref("mail.dark-reader.enabled")` (messageBody.css:18-20, :109-114, :247-249), and the pref defaults to true with a toggle shown (all-thunderbird.js:620-621). `nord.css` now declares separate body forms of the reader's roles from a second text rule keyed to that same condition. A user sheet may use `-moz-pref()`: `MozPrefFeature::parse` refuses only when `!context.chrome_rules_enabled()` (condition.rs:625), and `chrome_rules_enabled()` is true for any non-Author origin (parser.rs:275-277). The fallback is `light-dark()`, which Thunderbird already uses for its own quote colour (colors.css:196 into messageQuotes.css:37). The E shots confirm the keying, including a new "system dark, reader off" reader shot. The check gains the white body under a dark system. The quote mixes are now stated as `color-mix(in srgb, <level-1 form> N%, transparent)`, the same form as the theme's hover and selection mixes (light.css:109-111), and the check composites them over each body background. The plan's stated reason for restating the text rule was wrong: the theme's `userContent.css:1-2` imports both colour files unscoped. The plan now gives the true reason. |
| 6 | Focused, selected, tagged row takes the tag colour as background | Folded, D step 8 and D acceptance. Verified: threadPane.css:185-190 sets `background-color: var(--tag-color, …)` and `color: var(--tag-contrast-color, …)` on focused selected rows. `setUpTagStyles` picks black or white from the raw pref colour (about3Pane.js:5215-5221), and the theme never touches `--tag-contrast-color`. D restores that row to `--listbox-focused-selected-bg` and `--listbox-selected-color` (the theme maps them to neutral greys, variables.css:66-67), as the design's "Selection and hover keep the theme's neutral greys" already says. The tag icon keeps its colour through the theme's `fill: var(--tag-color, …)` (icons.css:209-210). **Re-homed:** the review's "C asserts the selected row is neutral" becomes D's screenshot acceptance, since a static check cannot see the DOM. A's check measures that row with neutral text. |
| 7 | The check measures the list against the wrong surfaces | Folded, A step 6. Verified: `#threadTree` paints `--gnome-secondary-sidebar-background` (mail.css:82-84): light `#f3f3f5` (light.css:82), its backdrop `#f6f6fa` (:161), dark `#28282c` (dark.css:23) and its backdrop `#252529` (:55). Cards have `background: none` (mail.css:105), so cards sit on that surface too. Hover and selection are `color-mix(in srgb, currentColor 7%/10%, transparent)` (light.css:109-111), composited with the row's own text colour. This fold also corrected the header surface: `#messageHeader` paints `--gnome-window-background` (mail.css:15-17; `#fafafb` light.css:74, `#222226` dark.css:19). A failing pair is fixed in `nord.css` by A, which now owns both. |
| 8 | The pairing cannot run as written | Folded, re-cut by file ownership. Wave 1: A (`nord.css`, CSS refactor, `user.js` tag, contrast check) with B (sync `--profile`, harness), and only B runs Thunderbird. Wave 2: D alone in the session's worktree. Wave 3: E with F, and only E runs Thunderbird. Verified `worktree.baseRef: "head"` (settings.json:6-8) and pass-core "Fold a single-deliverable task into a neighbor". B now installs and checks every top-level `thunderbird/*.css` rather than naming `nord.css`, so B never needs A's file inside its own worktree, and the wave-1 merge check proves `nord.css` is covered. The clock and the path were re-estimated: 390 path minutes (see "Estimate" below). |
| 9 | `visibility: hidden` drops the star from the accessibility tree | Folded, D step 5. MDN `visibility`: hidden "will remove it from the accessibility tree" and "cannot receive focus". Unflagged stars take `opacity: 0`, shown on `:hover`, `.selected` and `:focus-within`. |
| 10 | E's baseline comparison has no saved baseline | Folded, the wave-1 merge check and E step 7. The session writes the baseline once, after the wave-1 merge, to `<session git dir>/tb-shots-baseline/` (`git rev-parse --absolute-git-dir` in its worktree), and gives E that absolute path. The post-A baseline is valid for the Yahoo and Outlook comparison because A changes no body rule: its body forms are inert until E's rules read them. |
| 11 | The map's `mail.css` line numbers are wrong | Folded, D steps 2 and 7, plus a CSS-rules convention: comments cite lines found with `grep -n` at write time. Verified: `grid-template-columns: 1fr` is at mail.css:108, `.thread-card-column:first-child` at :111-113, and the junk text at :173-174. This fold found more stale map numbers. The forced quote colour is at messageQuotes.css:37 (the map says :75-83), and the stock signature opacity is at messageQuotes.css:22-28 (the map says :64-70). E now cites the true lines. The map itself is evidence and was not edited. |
| 12 | Header name and address style depend on a header setting | Folded, E step 1. Verified: `.recipient-multi-line` is `display: none` unless `.message-header-show-sender-full-address` is set (messageHeader.css:989-1015). The defaults are `showFullAddress: true` and `hideLabels: true` (msgHdrView.js:2783-2786). E styles the multi-line name, and the `.recipient-single-line` name for the full-address-off case. The label clause now says labels are hidden by default. |
| 13 | The plain-text bar overrides "no graphical quotes" | Folded, E step 3. Verified: `.moz-text-plain[graphical-quote="false"] blockquote { border-style: none }` (messageBody.css:71,89-92). The plain-text scope takes `:not([graphical-quote="false"])`. `mail.quoted_graphical` defaults to true (map "Message body"), so the design's bars show in the default setup. |
| 14 | A star stroke override does nothing | Folded, D step 5. Verified: icons.css:69 sets `-moz-context-properties: fill, fill-opacity !important` on a selector list that includes `.button-star` (:41). A stroke override must also set the context properties to `fill, stroke`. |
| 15 | Restoring the read-status column shows it on group headers | Folded, D step 2. Verified: threadCard.css:554-560 hides `.read-status` and the first column on `[data-properties~="dummy"]`. The restore takes `:not([data-properties~="dummy"])`. |
| 16 | Unreported states | Folded, one line each. A: `contrast_check.py --css <path>`, exit 2 on a missing or unparseable `nord.css`, distinct from a `FAIL` (exit 1). B: `--profile` without an argument prints usage and exits 2; a missing folder prints an `x` line and exits 1; a folder in use is refused. `tb-shots`: a non-empty output folder is refused, a leftover scratch profile is wiped only while port 28282 is free, a Marionette connect timeout fails and the trap still runs. |
| 17 | End-to-end check 3 runs after the profile is deleted | Folded. End-to-end step 2 runs `tb-shots --keep`, step 3 runs `--check --profile`, and a new step 4 removes the kept profile. |
| 18 | `--profile` still updates the shared theme clone | Folded, B step 1, with a change: under `--profile` the clone is used as it is, with no fetch, reset, clean or patch. A missing clone prints the existing `x theme clone missing` line (sync:64) and exits 1. The review suggested cloning instead, but a fresh clone would lack the carried patch. Verified: `check-drift:165-167` runs a plain `--check` that compares live profiles with the clone (sync:81). The clone as it stands carries the patch (`git apply --reverse --check` passes), so the harness installs what is live. B's acceptance checks that the clone's `HEAD` and status are unchanged by a `--profile` run. |
| 19 | Close misses adapter items, and Vale never runs on the README | Folded. F runs `vale thunderbird/README.md thunderbird/tools/README.md`. Close adds one `gitleaks git` branch-history scan and loads `python-conventions` into `diff-reviewer` (dotfiles-pass checklist globs and close checklist). A and B note that the gate's ruff D rules lint every tracked `.py` (check.sh:39, check-py-comments.sh). The prompt loads `python-conventions` before any `.py` is written. Verified: check.sh runs only Vale's test suites (:69-70), and its gitleaks leg scans only the working tree (:84). |
| 20 | The "no hex" check misses three-digit hex | Folded, A acceptance. Verified: `#fff` at customChrome.css:37, 298, 314, 316 and customContent.css:63, 138. With comments stripped (`perl -0pe 's{/\*.*?\*/}{}gs'`), `grep -nE '#[0-9a-fA-F]{3,8}\b'` over both files prints only `#fff` lines, named as the one exception (white text on accent fills, which the design's role map names). |
| 21 | A reader screenshot might not capture the body | Folded, B step 5. B's first probe confirms that body text pixels appear in a reader shot before it builds the rest. The message pane is `type="content"` with `maychangeremoteness="true"` (aboutMessage.xhtml:1846-1856). If the pixels are absent, B stops and reports, because E's proof depends on it. |
| 22 | Probes the source already answers (optional) | Folded, because it was trivially cheap and spares the executor two probes. D step 8: `setUpTagStyles` writes `--tag-${key}-backcolor` unescaped (about3Pane.js:5224), card icons read `var(--tag-${CSS.escape(key)}-backcolor)` (thread-card-tags.mjs:100-102), and CSS `--tag-\$label1-backcolor` names the same property. E step 5: in all of omni.ja's CSS, `--color-text-highlight-dark` is read only by messageBody.css:249 and colors.css:196, whose `--color-text-highlight` feeds only messageQuotes.css:37. So the override needs no document scoping. |
| 23 | Post-merge acceptance runs sit off the path (optional) | Folded, because it was trivially cheap and the estimate was being redone anyway. Waves 1 and 3 each carry a 10-minute merge-and-check line, inside the wave's clock. |
| 24 | A second channel re-enables junk filtering (optional) | Folded, one clause in F's README note. Verified: the per-account "Enable adaptive junk mail controls" checkbox writes `mail.server.%serverkey%.spamLevel` (am-junk.xhtml:57-63) as 100 or 0 (am-junk.js:162-163), which beats the default. |
| 25 | The plan branch is not on origin yet (optional) | Dropped. The existing launch line `git rev-parse worktree-thunderbird-nord-mail origin/worktree-thunderbird-nord-mail` already fails until the planning session pushes. |

Count: 24 folded, of which 2 carry a partial refusal or correction (2: `m.quit()` refused; 3: the
`.parentlock` guard corrected) and 1 has a part moved elsewhere (6); 1 dropped (25). All three
optional findings that were folded (22, 23, 24) met the "trivially cheap and clearly useful" bar.
No owner forks.

## Estimate

The old path was 330 minutes (A 40 with B 90, C 45 with D 90, E 90 with F 25, close 60). The
re-cut gives:

- Wave 1, 125 minutes: A 85 (old A minus the sync work, plus old C, plus the body forms and the
  new surfaces) with B 115 (old B 90, plus the sync work under the new `--profile` meaning), plus
  a 10-minute merge and check.
- Wave 2, 95 minutes: D alone, including its own harness runs.
- Wave 3, 105 minutes: E 95 with F 30, plus a 10-minute merge and check.
- Close, 65 minutes: adds the `gitleaks git` scan.

The path is 125 + 95 + 105 + 65 = 390. That is 90 over the design's "about 300", and under the
600 at which pass-core sends a plan back to Geoff, so it launches. The prompt's standing answer
moves to 780 task-minutes, twice 390.

## Contestable points this fold decided

- **B installs every top-level `thunderbird/*.css`, not `nord.css` by name.** B and A run in
  parallel from the same head, so B's worktree never holds A's file. Covering the glob proves
  itself at the wave-1 merge. Naming the file would force a placeholder that conflicts with A.
- **The body forms are separate roles, not a per-document re-scope of the chrome text rule.**
  Only E's body-class-scoped rules read them, so declaring them on every `:root` is inert
  elsewhere. Settings and address-book pages keep following the system scheme.
- **`-moz-pref()` is primary and `light-dark()` is the fallback.** `-moz-pref()` copies
  Thunderbird's own condition exactly. `light-dark()` relies on the body's used colour scheme,
  which Thunderbird's own quote colour already relies on. E's shots decide between them, and E
  may edit `nord.css` in wave 3 only for that switch, without adding or renaming a role, so F's
  table stays one for one.
- **No graceful quit before `flatpak kill`.** SIGKILL leaves a stale `lock` symlink in a profile
  that `tb-shots` deletes or rebuilds anyway. The `--keep` check in the end-to-end check is
  read-only, so the stale lock never blocks it.
- **The baseline is taken after the wave-1 merge, not before A.** E's comparison concerns only
  Yahoo and Outlook bodies, which A does not change. One list shot from that run confirms that
  `nord.css` loads, since the Nord folder colours and accent still show.

## Design errata owed

These are wording points to record against
`docs/superpowers/specs/2026-10-13-thunderbird-nord-mail-design.md` at close. They are not
changes of meaning, and the design file was not edited.

1. **"Dark" in "The reader" means the dark reader's dark body.** That is a dark system with
   `mail.dark-reader.enabled` on. With the reader toggled off, the body is white and takes the
   light forms, including the 0.6 signature. This is what makes the design's own 4.5:1 promise
   hold (finding 5).
2. **Conditional.** If A's check shows a tag role under 4.5:1 on a list surface (the review
   measured light nord14 at 4.44:1 on the selection composite), A tightens that role's clamp in
   `nord.css`. The design's "Each role colour goes through the GNOME theme's lightness rule" then
   needs "…or a tighter clamp where a surface needs it". The design's governing sentence, "so text
   passes WCAG 4.5:1 in both modes", is what A keeps. The PR body names any such role.

## Rulings

None. Every finding was folded or dropped on evidence, and none changes the design's meaning or
asks a product, taste, priority, scope or budget question.

## Note for the planning session

`~/.var/app/org.mozilla.thunderbird/.thunderbird/claude-view` still exists on disk, though the
review calls it deleted. It is not in `profiles.ini` and does not collide with the harness path
(`tb-nord-harness`). This fold did not remove it, since the folder is outside the worktree.
