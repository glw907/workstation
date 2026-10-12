# Review desk UI plan: fold verification

A fresh read of the folded plan at `bc91f01`
(`docs/superpowers/plans/2026-10-11-review-desk-ui.md`, its prompt
`docs/superpowers/plans/2026-10-11-review-desk-ui-prompt.txt`, and the fold record) against the three
reviews, the approved design, the first desk plan's inherited conventions, pass-core, and
`bin/.local/bin/review-desk`. 2026-10-11.

Count: 0 blockers, 3 majors (one an OWNER FORK), 9 minors.

## What was checked and holds

**Every blocker and major closed at its cited location.**

- Mechanics 1 and risk 1: "Running the app" (plan:255-271), with T5 folded into T4 (plan:427-471).
- Mechanics 2 and risk 5: "What goes live" runs under the lock, after both commands exit
  (plan:505-517, 521; prompt:60-61).
- Mechanics 3 and contract M5: the hand-over sequencing (plan:79-81) and the tie-break (plan:242).
- Mechanics 4 and contract M1: #113 in the e2e (plan:76-78) and in T4 (plan:455-464), and the
  empty texts (plan:44-45).
- Mechanics 5: T4 lists the item page (plan:451).
- M2: the 15-row a11y table (plan:488-490). M3: plan:414-418. M4: plan:56-58, 397-398. M6:
  plan:327-331, 353-354.
- M7 and risk 4: plan:63-65, 388, 408-409. M8 and risk 3: plan:65-68, 383, 410-411.
- M9 and risk 2: plan:90-99. With the `now`, `now`, `defer` fixture, a post in DOM order prints row
  2 as `defer`, so the order bug is caught end to end.
- Risk 6: closed by the lock, but finding 2 below reopens part of it. Risk 7: plan:449, 467-468,
  91-92. Risk 8: plan:243-245, 395, 421-423.

**Deadlock and order.** No step waits inside the live lock for something that needs that lock.

- The e2e's hand-overs set a temp `XDG_STATE_HOME`, so they take
  `$tmp/review-desk/start.lock` (command line 11 and line 43), never the live one. They serialize
  only among themselves, and the 1-second spacing guarantees distinct `created` and `id` values.
- T3 and T4 seed their own items, and "Running the app" step 3 starts the worktree app on a temp
  root. That is the correct start.
- "What goes live" leaves the lock when an item waits (plan:507-509). The reasoning is right: the
  command writes `item.json` before it takes the lock (command lines 35-44).
- Close step 9 hands over with the main checkout's command, takes no lock of its own, and finds
  the live app already stopped by the e2e. It starts the old build, which matches the old command.

**New mechanisms are sourced or probed.**

- `flock -o`: the fold's probe script and output are in `jobs/ebc278e8/tmp/fold/` and reproduce the
  claims. The `man flock` text matches.
- `beforeNavigate`: `types/index.d.ts:2771-2780` matches the quote.
- `enhance`: `forms/client.js:132` builds `FormData`, `:147-156` awaits `submit` and checks
  `cancelled`, and `:205-241` hands `failure`, `error`, and a thrown fetch to the callback.
- The `goto` options: `replace` and `refreshAll` match `index.d.ts:2557-2582`.
- `applyAction` pushes on a redirect (`client.js:2980-2981`). A link click uses
  `replace: options.replace_state ?? !changed` (`:3249`).
- The `gh` fields: re-run read-only. #113 is MERGED with 12 CheckRuns (11 `SUCCESS`, 1 `SKIPPED`),
  `workflowName` present, ``Risk class `auth-data` `` in the body, a Review section whose last
  backticked token is `accept`, and 161 files.
- The binary diff format is the fold's own read. `/usr/bin/firefox` is a non-Flatpak binary, and
  Playwright is 1.63.0 at the cited path.

**Budget.** 20 + 35 + 60 + 55 + 70 = 240 task-minutes: at twice the design's 2 hours, not over it.

**Launch prompt.**

- It meets pass-core's Launch prompt rule. It waits for the desk (prompt:58) and merges only on
  Geoff's desk approve with `--match-head-commit` and the decision's head (prompt:58-60).
- It ends after acting on the decision ("and finish", prompt:63-65).
- It contains no "never merge" and no bare "end".

**Scope.** No fold builds a feature the design leaves out. Two folds add copy outside the mockups:
"Not sent: <message>" and the guard-variant alert. Each is a failure or guard state the design's
own promises need, and each is recorded as a judgment call. The design-meaning question is
finding 3.

## Findings, ranked by consequence

### 1. major, correctness: per-item page state survives a move to the next item

- **Location:** plan:204-205 (the fold's own fact: "The item page stays mounted across items"),
  plan:382-394 (T3 item page), plan:443-449 (TriageView binds its rows to the page).
- **Defect:** SvelteKit's load docs say that rerunning a `load` function "will update the `data`
  prop ... it does _not_ cause the component to be recreated. As a result, internal state is
  preserved. If this isn't what you want, you can reset whatever you need to reset inside an
  `afterNavigate` callback, and/or wrap your component in a `{#key ...}` block."
  - The plan moves between items by `goto` and by queue links on one route. Nothing resets the
    page's state: the note's open flag and its text, the "Not sent" message, the toast, the path
    filter, and the triage rows bound to the page.
  - Two triage items in a row with the same row count would show and post the first item's
    dispositions and reasons for the second item's rows. The server's count check passes, and the
    command prints a decision Geoff did not make for that item.
  - Two PRs in a row would carry an open reject note and its text to the second.
  - Neither T3's acceptance (two seeded items of unnamed kinds) nor the e2e (one triage per round)
    reaches the case.
- **Proposed fold:**
  - T3: the bar, the note, and the view sit inside `{#key data.meta.id}`. The `beforeNavigate`
    hold cancel stays outside the key, in the page script that stays mounted. Triage rows start
    from `data.rows` per item.
  - T3's acceptance seeds a second triage item with the same row count. Move a row on the first,
    then press `j` and Enter: the second shows its own proposals, the status line reads 0 changed,
    and the reject note is closed and empty after a PR-to-PR move.

### 2. major, correctness: "Running the app" stops the worktree app only on success

- **Location:** plan:262-271 (steps 2 to 4, and the claim that a waiting hand-over "starts the
  live app itself"), plan:85-99 (the e2e's background hand-overs), command lines 62-64.
- **Defect:** step 4 stops the worktree app after the browser steps, and the plan names no cleanup
  for a script that fails partway.
  - In the screenshot loop and the e2e, a Playwright assertion that fails is the common case. It
    exits the script, `flock` releases the live lock, and the worktree app keeps 7907 on a temp
    root.
  - Any hand-over then finds 7907 answering and fails the item check. It exits 1 and tells its
    session to `pkill -f 'review-desk/[b]uild'`, a pattern that matches the worktree app too.
    This is risk 6's failure, which the fold says the lock removed.
  - The next run's step 2 kills only the main-checkout path, so its "curl must fail" check fails
    against the leftover worktree app.
  - The e2e's background hand-over commands also outlive a failed run, polling a temp root
    forever.
  - The same leak follows if the Bash tool's 600-second ceiling kills the foreground `flock`.
- **Proposed fold:**
  - The script's first line after step 1 sets `trap` on EXIT. The trap stops the worktree app by
    its worktree path in bracket form and kills the e2e's own hand-over PIDs, which the script
    records.
  - The e2e runs as a `run_in_background` Bash task, so no tool timeout kills `flock`.

### 3. major, correctness, OWNER FORK: the design says the server and the command do not change

- **Location:** design:39-40 ("Undo holds a decision in the page for 5 seconds before it posts, so
  the server and the `review-desk` command do not change."); plan:30-37 (judgment call 1);
  plan:236-245, 292-299, 395.
- **Defect:** the plan changes both.
  - The command gains `gh` fields, `pr.json`, `number`, and `file`.
  - The server gains `listDecided`, a layout load, and actions that now return `{ next }`.
  - Judgment call 1 reads the sentence as scoped to undo and justifies only the command change, by
    the Checks figure. The `{ next }` change came from risk 8, a fold, and is not named as a
    departure anywhere.
  - pass-core step 1 says "a finding that changes the design stops" unattended planning. Whether
    this reading changes the design is the owner's call, not the fold's. The fold ruled it "not a
    design change" and recorded no fork.
- **Options:**
  - (a) Keep the reading, and launch. Extend judgment call 1 to name the server changes (the
    layout load, `listDecided`, and `{ next }`) with their reasons: the queue and "Decided this
    session" need a list, and a client-side next item can target a gone or decided item. Geoff
    sees it at the PR read.
  - (b) Hold the launch for one STATUS question to Geoff before execution.
  - (c) Keep the server unchanged: compute the next item in the client and drop "Decided this
    session". This reopens risk 8 and departs from the mockups.
- **Recommendation:** (a). The design's own Checks figure and queue have no source without these
  changes. The decision protocol, the command's arguments, its stdout, and its exit codes stay
  fixed, which is what the out-of-scope line guards. The judgment call should name every departure,
  not one.

### 4. minor, correctness: "by 6 seconds the command has exited" can fail on a correct build

- **Location:** plan:87-89; command line 69 (`sleep 1` poll).
- **Defect:**
  - The hold fires at 5.0 s. The post, the write, and the next poll wake follow, and the poll
    alone can add up to 1 s.
  - The command can therefore exit at about 6.1 s on a correct build, and the e2e is the close
    gate.
- **Proposed fold:** "by 8 seconds". Keep the 4-second "no decision, command running" check.

### 5. minor, correctness: round 2's state root is unnamed

- **Location:** plan:96-99 ("sequenced the same way"); command lines 62-64.
- **Defect:**
  - Round 1's app serves round 1's temp root.
  - A round 2 that sets a fresh `XDG_STATE_HOME` makes each hand-over fail the item check and
    exit 1.
- **Proposed fold:** "Round 2 uses round 1's temp `XDG_STATE_HOME` and app."

### 6. minor, correctness: step 2 does not say what happens when 7907 still answers after the `pkill`

- **Location:** plan:262-264.
- **Defect:**
  - If something other than the main-checkout app holds 7907 (another session's worktree app, or
    the leftover from finding 2), the "checks that curl fails" check fails.
  - The plan names no action for that failure. An executor may go on and test against the wrong
    app.
- **Proposed fold:** "if it answers, the script exits nonzero and the session applies Stops."

### 7. minor, correctness: the Close clock can fire while the session waits on the desk

- **Location:** plan:518-525 (step 9 waits with no bound; Close estimate 70); pass-core "Clock
  stop" and "Score" ("the clock runs from the first execution commit to PR-ready").
- **Defect:**
  - Nothing says when the Close clock file is removed.
  - Left in place through step 9's wait, `claude-clock-stop` fires at 140 minutes. It stops a
    session that is correctly waiting on Geoff.
- **Proposed fold:** Close step 8 ends by removing the clock file when the PR is marked ready.

### 8. minor, correctness: the new exceptions contradict inherited conventions without naming them

- **Location:**
  - plan:262 ("the one sanctioned exception").
  - plan:505-517: "What goes live" runs a second `pkill` of the main path, plus `npm ci` and a
    build in `~/.dotfiles/review-desk`.
  - plan:518: a bare `review-desk`.
  - First plan:256-260: "No command writes `~/.dotfiles` outside `.claude/worktrees/`", and every
    tool runs "never as a bare name".
- **Defect:**
  - The prompt resolves the bare name (prompt:57-58), but the plan does not.
  - "The one sanctioned exception" is false as written: "What goes live" is a second.
- **Proposed fold:**
  - In the conventions, list the post-merge exceptions together: the main-path `pkill` and
    rebuild in "What goes live", and the main checkout's `review-desk` in Close step 9.
  - Change "the one" to "a".

### 9. minor, optional: an orphaned live item parks every app run until the clock stop

- **Location:** plan:259-261.
- **Defect:**
  - A SIGKILL orphan (ROADMAP hardening, plan:536-538) reads as a waiting item.
  - "Running the app" then waits until the clock stop, and the STATUS question cannot tell Geoff
    that the item is an orphan.
- **Proposed fold:** when step 1 exits nonzero, the session names the waiting ids, and whether a
  `review-desk` command process exists for them (`pgrep -f 'review-desk (pr|design|triage) '`), in
  the STATUS question.

### 10. minor, optional: the build step's place relative to the lock is unstated

- **Location:** plan:265-266 (T3 and T4 "start the worktree app"), plan:272-275 ("build,
  screenshot").
- **Defect:**
  - A `npm run build` inside the lock holds the live lock for the build's length, blocking every
    other session's hand-over for that time.
  - Nothing says to build first.
- **Proposed fold:** "Build before taking the lock; the script only starts `review-desk/build`."

### 11. minor, optional: the PR guard slot's default text is unspecified

- **Location:** plan:46-49 and 59-60 (judgment calls 3 and 5); catalogue:126 and 639 (`#guard`
  "Checks passed. Nothing is blocking.").
- **Defect:**
  - Judgment call 5 drops only the design page's guard text.
  - The PR guard sentence has a data source (`checksSummary`), but no task says whether it renders.
    The visual grade will see a missing device or an improvised one.
- **Proposed fold:** T4 renders the PR guard line from `checksSummary` and the verdict when no
  `## Before merge` exists, or "Later" records it as left out.

### 12. minor, optional: the close carries the fold's growth with no change in its estimate

- **Location:** plan:111-115, 473-525.
- **Defect:**
  - The folds added e2e work to the close: the #113 fetch, the 4-second and 6-second probes, the
    real-Firefox step, the 15-row a11y table, and the guard-variant reruns. Close stays at 70, and
    the total sits exactly on the 240 limit.
  - The first desk pass ran far under its plan, so this is not evidence of understatement. But the
    close has the least margin, and it holds the only waits outside the session's control.
- **Proposed fold:** none required. If the close overruns, the clock stop handles it. Over-ceremony:
  none found. The two e2e rounds, the 16 renders, and the real-Firefox step each answer a line of
  the design's end-to-end check.
