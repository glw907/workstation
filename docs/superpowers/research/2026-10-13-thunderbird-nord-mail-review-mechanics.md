# Mechanics and feasibility review: Thunderbird Nord mail layer plan

Target: `docs/superpowers/plans/2026-10-13-thunderbird-nord-mail.md` at `34eae55`. Lens:
mechanics and feasibility (`plan-reviewer`), 2026-10-13. Probed against the plan's inputs, the
installed theme and its clone (`~/.local/share/thunderbird-gnome-theme`), Thunderbird 158 omni.ja
files, comm-central (searchfox, hg-edge), Gecko Stylo source, the Claude Code docs, and MDN; plus a
Flatpak kill probe (Flatseal running `sleep`) and contrast computed with the research notes'
`nord_measure.py`. Thunderbird was not launched and no profile was written.

Summary: four blockers (the harness cannot run on pavilion as written), six majors, risk class
`ordinary` confirmed, no owner forks.

Planning-session note, added when this file was saved: blocker 1's orphan (Flatpak instance
`3098975677`, the planning session's `claude-view` run) was stopped with `flatpak kill 3098975677`
before the fold; port 28282 is free and only Geoff's instance `160493088` remains.

## Blockers

1. **A leftover planning Thunderbird holds port 28282** [blocker, correctness]. plan.md:96-97,
   :57-67. Instance `3098975677` (sandbox pid 27740, thunderbird pid 27741, profile `claude-view`,
   since deleted) listened on 127.0.0.1:28282 and trips `thunderbird-theme-sync`'s running guard
   (`pgrep -f '/app/lib/thunderbird/thunderbird'`, sync line 90), as does Geoff's instance.
   Fold: kill that numeric instance before launch; launch check `ss -ltn | grep -c ':28282 '`
   prints 0; `tb-shots` refuses to start if the port is taken; `tb_shots.py` checks after
   connecting that `Services.dirsvc.get("ProfD", Ci.nsIFile).path` is the harness path.
2. **`kill <pid>` of `flatpak run` does not stop Thunderbird** [blocker, correctness].
   plan.md:92-97; B acceptance :245-246; prompt.txt. Probe: `flatpak run --command=sleep
   com.github.tchx84.Flatseal 60 &`, `kill $!`: `bwrap --args 80 -- sleep 60` re-parented to pid
   2685 and kept running; SIGTERM to the bwrap pid did not end it either. Fold: start with
   `flatpak run --instance-id-fd=3 … 3>"$tmp/instance"`; stop with Marionette `m.quit()`, then
   `flatpak kill "$(cat "$tmp/instance")"` (`flatpak-kill(1)`: INSTANCE may be "the numeric
   instance ID"); wrap both in `trap … EXIT`; the convention and prompt ban only `flatpak kill
   org.mozilla.thunderbird` (the app id) and `pkill -f`.
3. **`--profile` as specified writes Geoff's live profile or cannot install** [blocker,
   correctness]. plan.md:179-190, :85-87. `sync()` runs `./scripts/install.sh -f "$TB_DIR"`
   (sync :116). The theme's `install.sh` reads every `Path=` in `$TB_DIR/profiles.ini`
   (:103-124) and for each, `saveProfile` (:26-101) copies the theme, rewrites
   `userChrome.css`/`userContent.css`, backs up and edits `user.js`; both live profiles are listed.
   `-p <name>` still needs `profiles.ini` in the `-f` folder (:103-107, exit 1), which a
   `mktemp -d` folder lacks. `sync()` refuses whenever any Thunderbird runs (:90); Geoff's runs.
   `require_profile` (:55-59) reads `profiles.ini`. Fold: under `--profile`, skip `install.sh`,
   `require_profile`, and the global running guard; copy `$CLONE` into
   `<dir>/chrome/thunderbird-gnome-theme`, write the two import files, copy the layer files and
   `nord.css`, copy `user.js`; guard only that `<dir>` is not in use (`<dir>/lock` symlink or
   `.parentlock`); `check()` accepts the same single-folder override.
4. **Sync overwrites the harness's `user.js`; end-to-end check 3 then disagrees** [blocker,
   correctness]. plan.md:200-201, :218-224, :42-43. Sync does `cp "$LAYER/user.js"
   "$p/user.js"` (:123), deleting the fixture prefs (Marionette falls back to 2828,
   greprefs.js:1460; the wizard returns); appending after sync makes `--check` report "user.js
   differs" (:75-76). Fold: fixture prefs go in the scratch profile's `prefs.js` before first
   launch, with keys disjoint from `thunderbird/user.js`; say so in B step 2.

## Major

5. **Body roles track the system scheme, not the dark reader** [major, correctness].
   plan.md:159-172, :363-383. Bodies go dark only under `@media (prefers-color-scheme: dark) and
   -moz-pref("mail.dark-reader.enabled")` (shared/messageBody.css:18-20 `color-scheme: dark`,
   :109-114 `html` background `#18181b`, :247-249 `a:link`), and the reader has a visible toggle
   (all-thunderbird.js:620-621). With the system dark and the reader off, dark-adjusted nord8 on
   `#ffffff` is 1.56:1 (links and every quote bar fail); the signature rule has the same keying
   problem. The plan's reason for restating the lightness rule is also wrong: the theme's
   `userContent.css:1-2` imports `theme/colors/light.css` and `dark.css` unscoped, so
   `--gnome-standalone-color-oklab` and the `--gnome-*` surfaces exist in message bodies. Fold:
   key body roles to the same condition (Stylo allows `-moz-pref()` in user sheets:
   `servo/components/style/parser.rs:275-276`, `chrome_rules_enabled()` true when origin is not
   Author), or use `light-dark(<light role>, <dark role>)`, which follows the body's used
   `color-scheme`; the harness confirms which. C adds "system dark, reader off" (body roles on
   `#ffffff`). State the colour space and mix target for `--mail-quote-2/3`
   (e.g. `color-mix(in oklab, var(--mail-accent) N%, transparent)`) so C can model them.
6. **A selected, focused, tagged table row gets the adjusted tag colour as background with
   contrast computed from the raw colour** [major, correctness]. plan.md:315-320; design
   "Selection and hover keep the theme's neutral greys". threadPane.css:185-190 sets
   `background-color: var(--tag-color, …)` and `color: var(--tag-contrast-color, …)` on focused
   selected rows; `setUpTagStyles` (about3Pane.js:5215-5221) picks black/white from the raw pref
   colour; the theme does not touch `tag-contrast`. With adjusted roles: light black on nord13
   3.46:1, nord11 3.30:1; dark white on nord11 1.77:1, nord8 1.56:1. Fold: D restores the
   focused selected tagged row to `--listbox-focused-selected-bg` / `--listbox-selected-color`
   (`!important`, equal or higher specificity), matching the design; the tag icon carries the
   cue; C asserts the selected row is neutral.
7. **C measures the list against the wrong surfaces** [major, correctness]. plan.md:266-271. The
   list paints `--gnome-secondary-sidebar-background` (mail.css:82-84): light `#f3f3f5`
   (light.css:82, variant `#f6f6fa` :161), dark `#28282c` (dark.css:23, variant `#252529` :55).
   Selection is `color-mix(in srgb, currentColor 10%, transparent)` (light.css:111), about 8% of
   `rgba(0,0,6,0.8)` over `#f3f3f5`; measured, light-adjusted nord14 (Personal, table text) is
   4.44:1 and nord8 4.45:1, under 4.5. In a tagged table row `currentColor` is the tag colour.
   Fold: C's backgrounds become the four secondary-sidebar values plus selection and hover
   composited over them with the row's own text colour; a failure is fixed in `nord.css`.
8. **The pairing cannot run as written** [major, correctness]. plan.md:126-131, :147-247,
   :281-283. B's harness needs A's `--profile` flag, built in parallel, and B's probes need a
   running Thunderbird; an Agent-tool subagent runs to completion and cannot wait for "the session
   says so"; D's and E's probes also need Thunderbird; C is a single deliverable (pass-core: fold
   it into a neighbour) and cannot fix `nord.css`. `worktree.baseRef: "head"` is set
   (`~/.claude/settings.json:178`), so pair worktrees branch from HEAD. Fold: re-cut by file
   ownership. Wave 1: A = `nord.css`, the CSS refactor, `user.js`, and C's contrast check (one
   owner of `nord.css` and its proof, about 85 min); B = the sync `--profile` change and the
   harness, so B can run what it builds. Wave 2: D alone. Wave 3: E with F (only E uses
   Thunderbird). One harness user per wave holds by construction; the path stays about 330 min.
9. **`visibility: hidden` removes the star from the accessibility tree** [major, correctness].
   plan.md:305-307. MDN: "Using a `visibility` value of `hidden` on an element will remove it from
   the accessibility tree", "The element cannot receive focus." Fold: `opacity: 0`, revealed on
   `:hover`, `.selected`, and `:focus-within`.
10. **E's "matches B's baseline" has no saved baseline** [major, correctness]. plan.md:243-244,
    :390-391. B writes to a throwaway `<tmpdir>`. Fold: B writes to a named persistent path
    (e.g. `$(git rev-parse --absolute-git-dir)/tb-shots-baseline/`); E compares `reader-yahoo-*`
    and `reader-outlook-*` against it by image diff or side-by-side reading.

## Minor

11. **The map's `mail.css` line numbers are wrong** [minor, correctness]. Installed copy (same as
    the clone): `grid-template-columns: 1fr` at 108; `.thread-card-column:first-child` at
    111-113; labels rule about 121-124; `--color-red-60` junk at 174. `icons.css` 205-217 is
    right. Fold: comments cite lines found with `grep -n` at write time.
12. **The header name/address style depends on a header setting** [minor, correctness].
    plan.md:350-353. `.recipient-multi-line` is `display: none` unless `#messageHeader` has
    `.message-header-show-sender-full-address` (shared/messageHeader.css:989-1015); defaults are
    `showFullAddress: true`, `hideLabels: true` (msgHdrView.js:2783-2786), so labels are hidden by
    default and the label-opacity clause is moot. Fold: name the `.recipient-single-line` case, or
    record the dependency in the commit body and README.
13. **The plain-text bar overrides "no graphical quotes"** [minor, correctness]. plan.md:363-365.
    User `!important` beats `.moz-text-plain[graphical-quote="false"] blockquote { border-style:
    none }` (shared/messageBody.css:89-92). Fold: `:not([graphical-quote="false"])` in the
    plain-text scope.
14. **A star stroke override does nothing** [minor, correctness]. plan.md:308-309. `icons.css`
    sets `-moz-context-properties: fill, fill-opacity !important` on `.button-star` (selector list
    :39, declaration ~:66-67). Fold: if a stroke is needed, also override the context properties
    to `fill, stroke`.
15. **Restoring the read-status column shows it on group headers** [minor, correctness].
    plan.md:296-298. threadCard.css:556-560 hides it on `[data-properties~="dummy"]`. Fold: scope
    the restore with `:not([data-properties~="dummy"])`.
16. **Unreported states** [minor, correctness]. `contrast_check.py`: missing or unparseable
    `nord.css` exits 2 (distinct from a `FAIL` exit 1); add `--css <path>` for the scratch-copy
    test. `thunderbird-theme-sync`: `--profile` without an argument prints usage and exits 2; a
    missing folder prints an `x` line and exits 1. `tb-shots`: a leftover scratch profile (from
    `--keep` or a crash) is refused or wiped; Marionette never connecting times out and the
    cleanup trap runs; an existing output folder is handled. Fold: one line each in A, B, C.
17. **End-to-end check 3 runs after `tb-shots` deleted the profile** [minor, correctness].
    plan.md:38-43. Fold: step 2 runs with `--keep`, step 3 checks, then a cleanup step removes it.
18. **`--profile` still updates the shared theme clone** [minor, correctness]. plan.md:185.
    `check-drift:165-167` checks the live profiles against the clone, so a harness `fetch` and
    `reset --hard` makes live `check-drift` report a difference until Geoff syncs. Fold: under
    `--profile`, use the clone as is (clone only if missing).
19. **Close misses adapter items; Vale never runs on the README** [minor, correctness].
    plan.md:420, :423-443. `check.sh` runs only Vale's tests (:69-70); Vale runs as a PostToolUse
    hook. The dotfiles-pass close checklist needs a `gitleaks git` branch-history scan and
    `python-conventions` for `*.py`; the gate's ruff D rules (`check-py-comments.sh`) need
    docstrings on both new `.py` files. Fold: F runs `vale thunderbird/README.md
    thunderbird/tools/README.md`; Close adds `gitleaks git` and names `python-conventions` for
    `diff-reviewer`; B and C note the docstring rule.
20. **A's "no hex" acceptance misses three-digit hex** [minor, correctness]. plan.md:191-192.
    `#fff` remains at customChrome.css:37, 298, 315 and customContent.css:63, 138; "outside
    comments" is not checkable by the given grep. Fold: `#[0-9a-fA-F]{3,8}\b` over non-comment
    lines, or name `#fff` as an allowed exception.
21. **A reader screenshot might not capture the body** [minor, correctness]. plan.md:102-103,
    :237-239. Only main-window shots were proven; `messagepane` is `type="content"` with
    `maychangeremoteness="true"` (aboutMessage.xhtml:1846-1856). Fold: B's first probe confirms
    body text pixels appear in a `reader-*` shot before the rest of B.
22. **Probes the source already answers** [minor, optional, over-ceremony]. D step 8: 
    `setUpTagStyles` writes `--tag-${key}-backcolor` unescaped (about3Pane.js:5224); card icons
    read `var(--tag-${CSS.escape(key)}-backcolor)` (thread-card-tags.mjs:100-102); CSS
    `--tag-\$label1-backcolor` unescapes to the same name. E step 5: `--color-text-highlight-dark`
    is read only by messageBody.css's `a:link` (:247-249) and colors.css:196, so web pages are
    unaffected; the override also recolours HTML mail's default links in the dark reader, as the
    design intends. Fold: record these facts and drop the two probes.
23. **Post-merge acceptance runs sit off the path** [minor, optional]. plan.md:46-47. About 10
    minutes per wave of harness and gate runs. Fold: add them or note the slack.
24. **A second channel re-enables junk filtering** [minor, optional]. plan.md:115-117,
    :411-416. The per-account "Enable adaptive junk mail controls" checkbox writes
    `mail.server.%serverkey%.spamLevel` (am-junk.xhtml:57-63, am-junk.js:162-163), which beats the
    default. The live profile has none today. Fold: the README note names that checkbox.
25. **The plan branch is not on origin yet** [minor, optional]. plan.md:63. Expected before the
    push; run the launch check after it.

## Checked and sound

- `persistent=.thunderbird` confirms the sandbox path mapping.
- Pref defaults: `spamLevel` 100 (mailnews.js:285), 0 disables (nsMsgDBFolder.cpp:2180-2181);
  `cardsview.rowcount` 3 (all-thunderbird.js:629), 2 adds `cards-row-compact`
  (about3Pane.js:5275); `marionette.port` 2828; the two display prefs in StaticPrefList.yaml;
  `NoSpoofingSender` as stated (nsMsgDBView.cpp:284-321).
- Specificity and origin as the map describes; user `!important` beats messageQuotes.css's author
  `!important`; `oklab(from … var(…))` already works in customChrome.css:108-117; `@import
  "nord.css"` resolves beside customChrome.css (theme userChrome.css:8).
- `readlink -f` on the stowed sync script resolves into `~/.dotfiles/bin/.local/bin/`, so
  `../../../thunderbird` is right.
- The repo is public, so `raw.githubusercontent.com` image links render.
- The ratchet's dead-reference check scans only `claude/.claude`, so new `thunderbird/` paths add
  no lines.
