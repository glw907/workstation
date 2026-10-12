# Review desk UI plan: fold record

Folds the three lenses on `docs/superpowers/plans/2026-10-11-review-desk-ui.md` at `439f1b0`
(mechanics, contract, risk) into the plan and its launch prompt, 2026-10-11. Each finding was
checked against source, a probe, or a read before its disposition. Optional findings are dropped
per `spec-plan-review` ("flag only gaps that affect correctness or the stated requirements, and
treat the rest as optional", https://code.claude.com/docs/en/best-practices). The task minutes stay
at the 240 limit: T1 20, T2 35, T3 60, T4 55 (T4 and T5 merged), close 70.

Tally: 59 findings. 40 folded (four of them with a part refused: risk 1, 2, 4, and 6), 1
refused, 18 dropped as optional. No owner fork.

## The port blocker (mechanics 1, risk 1, risk 6, contract m6)

Verified: 7907 is fixed in the command (`bin/.local/bin/review-desk:15`), `paths.origin`, and the
`Host` hook, the live desk held it at review time, and the plan stopped it only at Close step 3.
Two root folds were weighed.

- (a) Stop the live desk before T3 and leave it stopped. Refused as the root: the command starts the
  main checkout's app whenever nothing answers (`:45-52`), so any other session's hand-over in a
  multi-hour window restarts it and stops the executor. Worse, a hand-over that lands while a
  worktree app holds 7907 fails its `curl -sf $base/item/$id` check and prints "stop it with pkill
  -f 'review-desk/[b]uild'", a pattern that also kills the worktree app (risk 6).
- (b) Run every worktree app inside `flock` on the live root's `start.lock`. Taken. The command
  writes `item.json` before it takes that lock (`:35-44`), so a hand-over that arrives during a run
  blocks with its item already visible, and after the release it finds nothing on 7907 and starts
  the live app itself. The waiting-item check under the lock also covers a hand-over that released
  the lock just before the run began, since its `item.json` has no `decision.json` yet. The probe
  below showed that `flock -o` keeps the lock's fd out of the command and out of a `setsid` child.

Folded as the plan's "Running the app" convention, which also names the one sanctioned exception to
the inherited "Stopping an app" rule (contract m6). T5 folds into T4 under pass-core's "Fold a
single-deliverable task into a neighbor" (T5 was one file), so no two tasks need the port at once
and no pair runs an app. Risk 1's "assert the page's item id is a seeded id" and risk 6's "E2E" title
prefix are refused as redundant: under the lock no other app can take 7907 and no hand-over can see
the worktree app. The readiness check `curl -sf .../item/<seeded id>` is kept as the start wait.

## Mechanics

1. blocker, correctness. Folded at the root above: "Running the app" convention; T5 merged into T4;
   prompt's pair lines updated.
2. major, correctness. Folded with risk 5: "What goes live" runs after both hand-over commands
   exit (Close steps 8 and 9, prompt), under `flock -o` on `start.lock` with no item waiting, and
   ends with `curl -sf`. The "open tabs reload" claim is replaced; the full-page push after a
   rebuild joins the first "Later" item. The optional `updated.check()` fix is not taken.
3. major, correctness. Folded with contract M5: e2e hand-overs start only after the previous
   `item.json` exists plus one second, and the script asserts queue order first; Interfaces adds the
   `id` tie-break.
4. major, correctness. Folded with contract M1: e2e round 1 hands over cairn-cms #113 (verified:
   merged, 12 checks, a Review section), and the 16 renders come from it; T4 seeds #113 too; empty
   texts "No checks" and "Not stated" in judgment call 2 with a T2 test.
5. major, correctness. Folded: with T5 merged and T4 sequential, the remaining gap is the meta line,
   so T4 lists `src/routes/item/[id=id]/+page.svelte`.
6. minor, correctness. Folded with contract m8 and risk 10 (source `client.js:3146-3150`, `:3166`
   confirmed): the meta-line link carries `target="_blank" rel="noopener noreferrer"` (T4).
7. minor, correctness. Folded with contract m4's verdict cases: only backticked verdict tokens
   count (judgment call 2), and T2 tests prose "fix chain" after a backticked `accept`.
8. minor, correctness. Folded with contract M8 and risk 3 as judgment call 6 ("Not sent", controls
   unlocked, no navigation); T3 acceptance adds the decided-behind-the-page case.
9. minor, correctness. Folded: each e2e hand-over writes stdout, stderr, and exit status to files.
10. minor, correctness. Folded with contract M9: triage fixture `now`, `now`, `defer`; round 2 moves
    row 1 to Defer; T1 sets `decision.json` mtimes with `utimes` and flips the existing
    `items.test.ts:22` test (verified: "lists newest first").
11. minor, correctness. Folded (verified: no `src/routes/page.server.test.ts` exists): T3 lists it
    as new.
12. optional. Dropped (contract M7 and risk 4 carry the same gap as correctness; folded there).
13. optional. Dropped; T3 moved to 60 anyway, from the folds it now carries.
14. optional. Dropped.
15. optional. Dropped.
16. optional. Dropped.

## Contract

- M1, major, correctness. Folded with mechanics 4, plus part (a): T4 seeds a guard variant of #113
  (a `## Before merge` section, a last backticked `fix`, one `FAILURE` check) and asserts the
  warning alert beside Approve and `--cairn-error-ink` on the failed row and the Review figure.
- M2, major, correctness. Folded (design line 43: every a11y finding carries): Close step 4's
  `daisyui-a11y-reviewer` returns 15 rows, carried with file:line or not, and a "not" row is a
  finding in the batched chain. One instruction, no new reviewer.
- M3, major, correctness. Folded: T3's acceptance adds the sheet, the single-keys switch off and
  persisted across a reload, Escape stopping the count, and `desk.autoClose=off`.
- M4, major, correctness. Folded (verified `countdown.md:19` and the catalogue's "`#secs`, which is
  not a live region"): judgment call 4 and T3 say the countdown takes no `aria-live` or
  `aria-label`; the DaisyUI-first convention says a finding beats a guide.
- M5, major, correctness. Folded with mechanics 3.
- M6, major, correctness. Folded (probe below: git's binary format): `fileGroups` takes paths from
  the `diff --git` header's `b/` side, lists a binary file with no rows, and its fixture adds a
  binary new file and a rename.
- M7, major, correctness. Folded with risk 4 in this form: a `beforeNavigate` cancels a hold still
  counting and announces "Undone. Nothing was sent." (judgment call 6, T3), matching the mockup,
  where a queue click is a full load that drops the hold. T3's acceptance adds `a` then `j` and
  Enter with no `decision.json` after 6 seconds. Source quoted below.
- M8, major, correctness. Folded with mechanics 8, risk 3, and risk 13: judgment call 6, and T3
  keeps the "Decided" state with its load-test case.
- M9, major, correctness. Folded with mechanics 10, and round 2 now asserts the note text and the
  menu-set disposition. The edited-reason check runs once, in round 1 through the Ctrl+Enter path
  (risk 7), the harder of the two.
- m1, optional. Dropped.
- m2, minor, correctness. Folded: judgment call 1 quotes the design sentence and says why the plan
  reads it as scoped to undo. Not a design change: the design's out-of-scope line limits only the
  command's protocol, and its Checks figure has no other source.
- m3, minor, correctness. Folded: e2e step 3 checks at 4 seconds (no `decision.json`, command
  running) and 6 seconds, and after `z` reads `#sr-status`.
- m4, minor, correctness. Folded: T2 tests plain Enter on triage, `fix`, "Not stated", a
  `StatusContext`, and `[]`; `checksSummary` owns the figure's text.
- m5, optional. Dropped (the T4 triage checks it names are folded anyway as T5's acceptance moved).
- m6, minor, correctness. Folded at the root above.
- m7, minor, correctness. Folded (pass-core lines 150-155: "One batched fix chain follows"): Close
  step 4 runs the visual grade with the other reviewers, then one chain, then one fresh grade; a
  second FAIL is a "Stops" event. Steps renumbered.
- m8, minor, correctness. Folded with mechanics 6.
- m9, minor, correctness. Folded: T3's acceptance checks the queue, "Decided this session", and
  `aria-current` after the first decision.
- m10, optional. Dropped. Round 2 now names this pass's draft PR, which settles its first half.
- o1, optional. Dropped.
- o2, optional. Dropped.

## Risk

1. blocker, correctness. Folded at the root above; the seeded-id assertion is refused as redundant.
2. major, correctness. Folded in part: T2 says `moveRow` never reorders the array and `groupRows`
   derives the view, and the e2e's `now`, `now`, `defer` fixture catches a DOM-order post. The
   server-side "Rows changed order" check with a hidden `item` per row is refused: it is a new
   validator with no measured defect behind it, and the fixture now exercises the order end to end.
3. major, correctness. Folded with mechanics 8 (judgment call 6). Source: `forms/client.js:205-241`
   passes `failure` and `error`, a down app included, to the callback.
4. major, correctness. Folded with contract M7. Its "cancel the navigation" form is refused: it
   departs from the mockup, where leaving drops the hold, and on a reload it raises the browser's
   unload dialog (`types/index.d.ts:2774`).
5. major, correctness. Folded with mechanics 2.
6. major, correctness. Folded at the root above; the "E2E" title prefix is refused as redundant.
7. major, correctness. Folded (`enhance` builds `FormData` before `submit`, `forms/client.js:121-155`):
   T4 commits an open reason edit before Ctrl+Enter submits, and both T4's acceptance and e2e round
   1 press Ctrl+Enter from the reason field.
8. major, correctness. Folded: the actions return `{ next }` computed from the server's waiting list
   (Interfaces, T3), with an action test that skips an item whose `item.json` was removed.
9. minor, correctness. Refused: a `history.length` gate and a new "This tab cannot close itself"
   state would add copy and a screen outside the approved mockups, more than the risk it removes (a
   stale "Closing" label in a tab Geoff closes by hand). The cases join the first "Later" item.
10. minor, correctness. Folded with mechanics 6.
11. minor, correctness. Folded: judgment call 4 adds Ctrl+Enter to the held keys, with a T2 test.
12. minor, correctness. Folded: `number` comes from `gh`'s `.number` (T1, Interfaces), and an
    old-format item without `number`, `file`, or `pr.json` reads cleanly (T1 test, T3, T4).
13. minor, correctness. Folded with contract M8.
14. optional. Dropped.
15. optional. Dropped.
16. optional. Dropped (the root fold puts its check and `pkill` under the lock anyway).
17. minor, correctness, raised as an owner fork. Not a fork: the approved design rules the desk
    hardening out of scope, so building option (b) would change the design, and the reviewer's own
    recommendation is (a). Folded as a "Later" item that names the raised stakes. Nothing wrong
    merges either way: a decision on an orphan reaches no session.
18. optional. Dropped.
19. optional. Dropped.
20. optional. Dropped.
21. optional. Dropped.
22. optional. Dropped.

## Probes and reads

- **`flock(1)` and the lock fd** (script and output under
  `/var/home/glw907/.claude/jobs/ebc278e8/tmp/fold/`, util-linux 2.42.4, scratch lock only). A
  `setsid -f sleep` started under `flock <lock> -c` kept the lock after `flock` exited: a second
  `flock -w 2` exited 1. With `-o` the second `flock` exited 0. The command run under `flock -o`
  held no fd on the lock, and under plain `flock` it held one. The command's `exec 9>"$lock"; flock
  9` waited 2.5 s behind `flock -o <lock> -c 'sleep 3'` and then took the lock. `man flock`: "-o,
  --close: Close the file descriptor on which the lock is held before executing command. This is
  useful if command spawns a child process which should not be holding the lock."
- **`beforeNavigate`** (`@sveltejs/kit` 3.0.1, `types/index.d.ts:2772-2780`): runs "before we
  navigate to a URL, whether by clicking a link, calling `goto(...)`, or using the browser
  back/forward controls", and "remains active as long as the component is mounted"; link clicks go
  through `_before_navigate` at `client.js:3176`.
- **`enhance` results** (`src/runtime/app/forms/client.js:205-241`): `failure` and `error` results
  reach the callback, and a thrown fetch becomes `{ type: 'error', ... }`.
- **cairn-cms #113** (`gh pr view 113 -R glw907/cairn-cms --json ...`, read only): merged, 12 checks
  (11 `SUCCESS`, 1 `SKIPPED`), a `## Review` section, no `## Before merge`; `gh pr diff` lists 161
  files.
- **Binary diff format** (`git diff origin/main...HEAD` on one render): `diff --git`, `new file
  mode`, `index`, `Binary files /dev/null and b/... differ`, no `+++` line. 16 renders on this
  branch.
- **The live root, read only**: no `item.json` without a `decision.json` under
  `~/.local/state/review-desk/items/` at fold time, so "Running the app" would not wait today.
- **Reads**: `countdown.md:19`, the catalogue's `#secs` lines (`:548-550`), `items.test.ts:22`, the
  item actions (they return nothing today), and pass-core's "Fold a single-deliverable task" (line
  63) and "One batched fix chain" (line 153).

No probe touched port 7907, the live desk, Geoff's Firefox, or `~/.local/state/review-desk` beyond
listing it.

## Owner forks

None.

## Planning session edits after the fold

- Contract m10, mechanics 14, and risk 21 were dropped as optional, but m10 is a vacuous pass: e2e
  step 5 could run against step 2's `firefox` stub. Folded as `correctness`: step 5 now calls
  `/usr/bin/firefox --headless --no-remote`, which skips the stub and stays out of Geoff's running
  Firefox.
- "What goes live" said "only when no item waits"; it now says what happens when one waits. The
  merger leaves the lock at once and retries a minute later, because a hand-over blocked on the
  lock has already written its `item.json`, so waiting inside the lock would deadlock.
