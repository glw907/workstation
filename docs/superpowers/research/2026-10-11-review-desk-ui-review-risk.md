# Review desk UI plan: data integrity and failure risk review

Target: `docs/superpowers/plans/2026-10-11-review-desk-ui.md` at 439f1b0. Lens: crash, concurrent
process, partial write, upgrade, restore. Every SvelteKit claim below is quoted from the installed
3.0.1 source at `/var/home/glw907/.dotfiles/review-desk/node_modules/@sveltejs/kit`; port state was
read with `ss -ltnH 'sport = :7907'` (the live desk was listening at review time and was not
touched).

Findings are ranked by consequence. 1 blocker, 7 major, 14 minor. One OWNER FORK (finding 17).

## Blocker

### 1. The task-time app runs share port 7907 with the live desk, and a test can decide a real item

- Severity: blocker. Tag: `correctness`.
- Location: plan lines 196-200 (the canonical "build, screenshot" loop), 312-319 (T3 acceptance),
  340-343 (T4), 359-361 (T5), 346 and 363 (T4 and T5 as a pair), 169-172 (the only live-desk rule,
  scoped to the e2e); the prompt file's pair dispatch (`isolation: "worktree"`).
- Defect. The app answers only on 127.0.0.1:7907 (`hooks.server.ts` refuses any other `Host`, and
  `paths.origin` pins the origin, first plan line 244), so every T3, T4, and T5 run of the built
  app needs port 7907. The plan's only rule for the live desk is the e2e's (line 172, Close step 3).
  At review time the live desk holds 7907. A task that starts its app with `setsid -f node build`
  while the live desk runs gets EADDRINUSE in a log nobody reads, and its Playwright then talks to
  the live desk on the real state root. T3's acceptance opens `/`, which now redirects to the
  oldest waiting item, then presses `a` and waits 5 seconds: on the live desk that approves Geoff's
  oldest real waiting item, and the waiting session reads it as merge authorization (pass-core
  line 172). Separately, T4 and T5 run as a pair in two worktrees and both need 7907 at once, so
  one pair's screenshots can come from the other's build and temp root, a false visual pass.
- Proposed fold. Add one convention: "Running the app. Before starting a built app, `ss -ltnH
  'sport = :7907'` must print nothing; if the live desk holds the port, stop it only under Close
  step 3's rule (nothing waits), else apply Stops. After starting, `curl -sf
  http://127.0.0.1:7907/item/<a seeded id>` must succeed before any Playwright step, and every
  script asserts the page's item id is a seeded id before it sends a decision key or click." Run
  T4's and T5's app-backed acceptance one after the other (code can still be written as a pair;
  the session runs both acceptances itself after merging the halves), or run T5 after T4. Path
  cost about 25 minutes if fully serialized, near zero if only the acceptance runs are serialized.

## Major

### 2. The triage post maps dispositions to items by index, and nothing checks the order

- Severity: major. Tag: `correctness`.
- Location: plan lines 256-257 (`moveRow`, `groupRows` "in item-number order"), 301-303 ("hidden
  inputs in their original order"), 355-356 ("binds its rows to the page"); server check at
  `review-desk/src/routes/item/[id=id]/+page.server.ts` lines 286-300.
- Defect. The server pairs `dispositions[i]` and `reasons[i]` with `source[i].item` and checks only
  the counts and the values. A view that moves rows between sections, with rows bound to the page
  and the hidden inputs rendered from that bound array, posts the right count of valid values in
  the wrong order if anything reorders the array (a `moveRow` that returns a re-sorted array is the
  natural reading of "keeps item-number order inside a section"). The command then prints a
  disposition for the wrong item and the session acts on it: a "drop" lands on an item Geoff marked
  "now". This is the "decision for the wrong item" case, and no test or e2e step would catch it
  unless the moved row happens to be out of place.
- Proposed fold. Two lines of contract plus one boundary check. T2: `moveRow` changes only the
  row's `disposition` and never the array order; `groupRows` derives the view. T3: each row also
  posts a hidden `item`, and the `submit` action fails 400 ("Rows changed order") unless
  `form.getAll('item')[i] === source[i].item` for every `i`; its test posts a swapped pair and
  expects the failure and no `decision.json`.

### 3. A post that fails after the hold is not specified, so the page can say "Approved" when nothing was written

- Severity: major. Tag: `correctness`.
- Location: plan lines 295-299 ("on the action's success the page calls goto"); catalogue "Undo
  hold" (at 0 the toast reads "Approved ... Opening ..." and is announced).
- Defect. The fetch runs after the hold. It fails when the app is down (Close step 3 stop, "What
  goes live" restart), when the item was decided in another tab or its command exited (the trap
  removes `item.json`, so `readWaiting` 404s), on the triage row-count or order check, or on the
  Host or CSRF 403. `enhance` turns each into a `failure` or `error` result
  (`src/runtime/app/forms/client.js:205-241`) and hands it to the page's callback. The plan says
  only what happens on success. By then the toast has already announced the decision as made and
  the controls are locked, so Geoff reads a decision that the waiting command never sees.
- Proposed fold. In T3: on a `failure` or `error` result the page unlocks the controls, replaces the
  toast with "Not sent: <message>. The item is still waiting.", announces it, and returns focus to
  the deciding button; it does not navigate. The T3 acceptance adds one case: stop the app during a
  hold and see that text.

### 4. Navigating, reloading, or closing during the hold is not locked, and the timer outlives the item

- Severity: major. Tag: `correctness`.
- Location: plan lines 295-299 and 46-47; catalogue "Undo hold" (locks "#decision button", "main
  button", "main input", never the queue) and "Key map" (`j`/`k` and Enter on a queue link are not
  suppressed by a hold).
- Defect. During the 5 seconds the queue links, `j`/`k` then Enter, and "Decided this session"
  links still navigate. `/item/A` to `/item/B` is the same route, so SvelteKit keeps the page
  component and only `data` changes; the submit closure's timer keeps running. When it fires it
  posts to A (the action URL was fixed at submit time, `forms/client.js:121-126`, which is right),
  but the success branch calls `goto(nextItem(queue, id))` with whatever `id` the page now holds,
  yanking Geoff off B or skipping an item. If the implementer resets the toast on a data change,
  the decision posts with no visible Undo. A reload or tab close drops the held decision silently,
  which fails closed but is still a decision Geoff believes he made.
- Proposed fold. One `beforeNavigate` in the item page: while a hold runs, call `cancel()` except
  for the hold's own `goto`. SvelteKit documents that `cancel()` on a `leave` navigation "will
  trigger the native browser unload confirmation dialog" (`types/index.d.ts:2774`, wired at
  `src/runtime/client/client.js:3086-3111`), so the same line covers reload and tab close. Capture
  the item id in the submit closure and compute the next item from it, never from current `data`.

### 5. "What goes live" races hand-overs, and its "open tabs reload" claim is false

- Severity: major. Tag: `correctness`.
- Location: plan lines 402-409 (Close step 9) and 410-415; command
  `bin/.local/bin/review-desk` lines 43-60 (the `start.lock` flock and the build-if-missing branch).
- Defect. The merger stops the app, runs `npm ci` (which deletes and rewrites `node_modules`,
  where the runtime dependency `marked` lives, since adapter-node leaves `dependencies` external),
  then `npm run build`, then starts it. None of this takes `start.lock`. Another session's
  hand-over in that window finds nothing on 7907 and either starts the old `build/` against a
  half-written `node_modules`, or, if adapter-node has just cleared `build/`, runs its own `npm ci
  && npm run build` in the same directory concurrently. The merger's own start then fails with
  EADDRINUSE into `server.log` (it is `setsid -f`), and the old or broken build keeps serving with
  no check that notices. Separately, "so open tabs reload into the new desk" is not what happens:
  an open tab keeps its old client until its next navigation, and SvelteKit's redeploy fallbacks
  reload with a push (`native_navigation(url)` without `replace` at `client.js:1534` and `:1682`;
  `native_navigation` does `location.href = url.href` at `:213`).
- Proposed fold. Run the stop, rebuild, and start inside `flock
  "$HOME/.local/state/review-desk/start.lock" -c '...'`, and end with `curl -sf
  http://127.0.0.1:7907/` plus `pgrep -fc '/var/home/glw907/.dotfiles/review-desk/[b]uild'`
  printing 1. Replace the reload sentence with "open tabs load the new desk on their next
  navigation"; finding 9 covers the history cost.

### 6. The e2e can decide a real item if 7907 changes hands mid-run

- Severity: major. Tag: `correctness`.
- Location: plan lines 61-72 (e2e steps 3 and 4), 374-381 (Close step 3); command line 63 (the
  guard message tells the reader to `pkill -f 'review-desk/[b]uild'`).
- Defect. The e2e runs for several minutes on 7907 with a temp state root. Another session's
  hand-over in that window hits the guard and is told to `pkill -f 'review-desk/[b]uild'`, a
  pattern that matches the worktree's app too. If that session complies and restarts the live
  desk, the e2e's next steps (the design reached by next-item navigation, `/`, round 2's fresh
  items) run against the real state root, where `/` and the next-item rule land on Geoff's real
  waiting items, and the script's `r`, typed note, and Ctrl+Enter reject one of them. The same
  script also posts test approves whose JSON is byte-identical to a real one.
- Proposed fold. The convention from finding 1 covers it: before each decision key or click, the
  script asserts the page's item id is one its own commands created (read from the temp state
  root). Give the e2e's PR, design, and triage titles an "E2E" prefix so a stray tab is
  recognizable.

### 7. Ctrl+Enter with a reason edit open drops the typed reason

- Severity: major. Tag: `correctness`.
- Location: plan lines 301-303 ("Ctrl+Enter submits from anywhere"), 355-356 ("the reason edited
  in place"); catalogue "Key map" (Ctrl+Enter "anywhere including the reason input") and "Triage
  moves" ("Enter or blur keeps").
- Defect. `enhance` builds the `FormData` before it calls the submit function
  (`forms/client.js:132`, then `await submit(...)` at `:147-155`), so the hidden inputs are read
  the moment Ctrl+Enter submits. A reason that is kept on blur or Enter is still uncommitted while
  its input has focus, so the posted reason is the old one, and the hold then disables the input.
  The session receives a reason Geoff did not write. The e2e never edits a reason before
  Ctrl+Enter.
- Proposed fold. The Ctrl+Enter path commits an open reason edit before `requestSubmit`; the T5
  Playwright run types a reason and presses Ctrl+Enter without leaving the field, and the e2e's
  triage row 2 does the same so the printed JSON carries the typed reason.

### 8. The next item comes from the client's stale queue

- Severity: major. Tag: `correctness`.
- Location: plan lines 185-186 (Interfaces "Next item"), 258 (`nextItem`), 298-299.
- Defect. The queue is the layout's load data from the last navigation. Other sessions add items,
  and a session that exits removes its `item.json` (command trap, line 20). `goto(nextItem(...))`
  can target an item that is gone (load 404s with "Not found", right after the toast said "Opening
  <item>") or already decided in another tab. The 404 page also blocks the empty state's close.
- Proposed fold. The approve, reject, and submit actions return `{ next }`, computed with
  `nextItem(await listWaiting(root), id)` before `writeDecision`; the page does `goto(next ?? '/',
  { replace: true, refreshAll: true })`. The client `nextItem` call goes. The action test asserts
  `next` skips an item whose `item.json` was removed.

## Minor

### 9. Several paths push a second history entry, and then the countdown closes nothing

- Severity: minor. Tag: `correctness`.
- Location: plan lines 304-306, 423-424 ("Later" names only body links).
- Defect. Beyond body links, a full-page fallback pushes: a client navigation while the server is
  down or after a redeploy (`client.js:1534`, `:1682`), and a click on Approve before hydration,
  which posts natively. After any of them `window.close()` is refused and the page still says
  "This tab closes in N s", then "Closing this tab."
- Proposed fold. The empty state starts its countdown only when `history.length === 1`; otherwise
  it says "This tab cannot close itself." Add the two fallback cases to "Later".

### 10. The new GitHub link in the meta line opens in the same tab

- Severity: minor. Tag: `correctness`.
- Location: plan line 333.
- Defect. An external link is a native navigation and pushes an entry, so one visit to GitHub and
  back makes the tab unclosable. Unlike the body links in "Later", this link is new in this pass.
- Proposed fold. The meta-line link carries `target="_blank" rel="noopener"`.

### 11. A held decision still takes Ctrl+Enter

- Severity: minor. Tag: `correctness`.
- Location: plan lines 46-47 and 270-271.
- Defect. Judgment call 4 lists `a`, `r`, `1`, `2`, `3`. On triage, Ctrl+Enter submits from
  anywhere, and `requestSubmit()` without a submitter submits even with the buttons disabled, so a
  second hold starts and its post 404s (finding 3 then shows the error over a good decision).
- Proposed fold. While held, `keyAction` returns null for every decision action including
  Ctrl+Enter; the T2 test asserts it.

### 12. `number` comes from the argument, and old items have neither `number` nor `file`

- Severity: minor. Tag: `correctness`.
- Location: plan lines 178-183 and 219-221; T3 queue rows (line 284) and T4 meta line (line 333).
- Defect. `gh pr view` accepts a number, URL, or branch; writing the `<source>` argument "as a
  number" fails under `set -e` for the other two, so the hand-over dies before `item.json`. Items
  written by the old command (still waiting at deploy, or written by the stowed old command until
  the merge) have no `number` or `file`, so the queue row and meta line render "#undefined" unless
  guarded.
- Proposed fold. Take `number` from `gh`'s `.number`. The queue row and meta line omit the number
  and file when absent; the T1 store test's old-format item asserts the absence reads cleanly.

### 13. The item page must keep its decided state

- Severity: minor. Tag: `correctness`.
- Location: plan lines 293-303 (no mention of `decided`); "Decided this session" links (line 285).
- Defect. T3 rewrites the item page and never mentions the existing `{#if data.decided}` branch.
  "Decided this session" now links to decided items, and a second tab holds stale items, so a
  rewrite that drops the branch shows a live decision bar on a decided item. The server's
  `readWaiting` still refuses the post, so this is a confusing failure, not a wrong decision.
- Proposed fold. T3: a decided item renders "Decided" with no bar; the load test covers it.

### 14. Enter or a plain button inside the decision form submits it

- Severity: minor. Tag: `optional`.
- Location: plan lines 293-303.
- Defect. If any view markup sits inside the bar's form, Enter in the path filter or a reason input
  submits implicitly, and a Svelte `<button>` without `type` is a submit button, so "Move to" or
  "Edit reason" would start a Submit hold.
- Proposed fold. One sentence in T3: the form wraps only the bar, and every non-submit button
  carries `type="button"`.

### 15. Two tabs can both write a decision

- Severity: minor. Tag: `optional`.
- Location: `review-desk/src/lib/server/items.ts` `writeDecision` (rename over), the actions'
  `readWaiting` then write.
- Defect. With every hand-over opening its own tab, the same item can be decided in two tabs. Two
  posts that pass `readWaiting` together both rename over `decision.json`; both tabs report success
  and the command prints whichever it read. The window is milliseconds, so this is unlikely.
- Proposed fold. Publish with `link(tmp, final)` (fails with EEXIST) and unlink the temp, returning
  the 404 path on EEXIST. Or leave it to ROADMAP hardening.

### 16. Close step 3's "nothing waits" check stops on orphans and races new hand-overs

- Severity: minor. Tag: `optional`.
- Location: plan lines 374-377.
- Defect. An orphaned `item.json` (SIGKILL, power loss; ROADMAP "Review desk hardening") makes the
  check stop the pass forever. A hand-over between the check and the `pkill` gets the loud
  "does not serve this state root" exit rather than silent loss, so the race is tolerable.
- Proposed fold. Check for a live command too (`pgrep -f 'review-desk (pr|design|triage) '`), and
  run check plus `pkill` under `flock ~/.local/state/review-desk/start.lock`.

### 17. OWNER FORK: orphaned items now sit in the queue as if live

- Severity: minor. Tag: `correctness`.
- Location: plan line 184 (queue lists every waiting item); ROADMAP.md lines 74-76 (SIGKILL orphans,
  deferred); design "Out of scope".
- Defect. Before this pass an orphan was invisible unless its old tab was open. The queue now lists
  it beside live items, and approving it writes a decision no session reads: Geoff believes he
  authorized a merge that never happens. The design puts hardening out of scope.
- Options. (a) Keep it out of scope and add it to "Later" with the raised stakes named. (b) The
  command records its pid and `/proc/sys/kernel/random/boot_id` in `item.json`, and `listWaiting`
  skips an item whose process is gone.
- Recommendation: (a). It is rare (a hard kill or reboot with an item waiting) and the design ruled
  hardening out; the "Later" entry keeps it visible.

### 18. One malformed file now takes down every page

- Severity: minor. Tag: `optional`.
- Location: plan lines 281-283 (`+layout.server.ts` runs `listWaiting` and `listDecided` on every
  load); ROADMAP.md line 77.
- Defect. ROADMAP already defers "one malformed `decision.json` or `item.json` makes `listWaiting`
  throw and 500s the index". With both lists in the layout, the 500 now covers every item page,
  including the one Geoff needs. The files are written by temp and rename, so this needs external
  corruption.
- Proposed fold. Name the wider blast radius in "Later"; no code.

### 19. The Checks figure is a hand-over snapshot

- Severity: minor. Tag: `optional`.
- Location: plan lines 29-33, 163-168, 326.
- Defect. `statusCheckRollup` is read once at hand-over; a check pending then stays "pending" and a
  later failure never shows. The merge's `--match-head-commit` still blocks unseen code, so this
  misleads only about CI.
- Proposed fold. Label the figure "at hand-over" in its tooltip or sub-line, or accept as is.

### 20. Geoff's open desk tabs reach the test apps

- Severity: minor. Tag: `optional`.
- Location: plan lines 374-381 and finding 1's task runs.
- Defect. A desk tab Geoff kept open (auto-close off) talks to whatever holds 7907, so during a
  test run it shows test items he can decide, which confuses the run.
- Proposed fold. `notify-send -u normal "review desk under test"` before stopping the live desk, and
  the matching all-clear after. Or accept.

### 21. The real-Firefox step may remote into Geoff's browser

- Severity: minor. Tag: `optional`.
- Location: plan lines 73-74.
- Defect. The step relies on a new headless instance; adding the flag makes that explicit and cannot
  open a tab in Geoff's daily Firefox.
- Proposed fold. `firefox --headless --no-remote --profile <temp dir> ...`.

### 22. `localStorage` write failures are silent

- Severity: minor. Tag: `optional`.
- Location: plan lines 187-188.
- Defect. With storage blocked, "Close when empty" off or the single-keys switch off holds only for
  the page's life. No decision data is at risk.
- Proposed fold. None beyond the `try` the plan already names.

## Over-ceremony

None found through this lens. The two e2e rounds, the 16 renders, and the real-Firefox step each
answer a stated requirement of the design's end-to-end check. Finding 1's serialization of T4 and
T5 acceptance runs costs at most about 25 minutes of path and removes a false-pass risk.
