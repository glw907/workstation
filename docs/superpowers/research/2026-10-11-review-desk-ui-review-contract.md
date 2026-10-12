# Review desk UI plan: contract and criteria review

Reviewer lens: contract and criteria. Target: `docs/superpowers/plans/2026-10-11-review-desk-ui.md`
at `439f1b0`, read against the approved design, the a11y review record, the catalogue, the first desk
plan's conventions, the current `review-desk/` app, `bin/.local/bin/review-desk`, pass-core "Close",
and the dotfiles-pass adapter. Every claim below was checked against source or a live `gh` read on
2026-10-11.

Verdict: fix. No blocker. Eight majors, most of them criteria whose fixture cannot exercise the
promise they check, so they would pass with the promise unbuilt. No finding needs to change the
design; one design sentence wants citing (minor 2).

## Major

### M1. No fixture exercises the design's color and warning promises, or the checks list

- Severity: major. Tag: `correctness`.
- Location: plan lines 40-43 (judgment call 3), 340-344 (T4 acceptance), 57-58 and 372-373 (the
  e2e PR); design lines 25-27.
- Defect: the design promises color "only where it means something: a failing check, a blocking
  verdict, diff signs" and "A `## Before merge` section stays a warning above Approve". T4 seeds
  workstation #13. A `gh` read shows #13 has no `## Before merge`, a Review section ending in
  `accept`, and an empty `statusCheckRollup`. The e2e PR is this pass's own draft, whose body is the
  step 9 skeleton, in a repo with no CI, so it has no checks and no Before merge either. No task or
  close step ever renders a failing check, a `fix` or `escalate` verdict, the guard-slot warning, or
  a non-empty checks list. T4's "show each device ... (content aside)" and the close's 16-render
  grade would both pass with all four unbuilt. The visual-verifier has no Checks list to grade
  against `pr-b`'s 12-check two-column list. The plan also never says what the Checks figure shows
  for an empty rollup, though that is the only case its own fixtures produce.
- Proposed fold: (a) T4 seeds a second PR item: #13's body with a `## Before merge` section
  appended and a last Review verdict of `fix`, plus a `pr.json` holding one `FAILURE` and one
  `SUCCESS` CheckRun. T4's acceptance asserts the `alert alert-warning` in `#guard` beside Approve,
  and that the failed check's row and the Review figure compute to `--cairn-error-ink`. (b) The
  close e2e's first-round PR is `glw907/cairn-cms` #113, a read-only `gh` fetch and the mockup's own
  subject (auth-data, 12 checks with one skipped, `accept`), so the 16 renders differ from the
  references mostly in content. The pass's own draft stays the PR that step 10 hands over. (c)
  Interfaces names the empty-rollup display (for example, "No checks"), and the T2 `checksSummary`
  test covers it.

### M2. The a11y carry-over is gated on "no blocker", so 12 of the 15 findings can drop out

- Severity: major. Tag: `correctness`.
- Location: plan lines 78-79 and 387-388 (close step 5); design line 43.
- Defect: the design says every finding of the a11y review carries into the build. The only gate
  that reads them all is `daisyui-a11y-reviewer` finding "no blocker". Findings 4 to 15 are
  warnings and suggestions, so the gate passes with any of them missing. Most of them have no
  acceptance check anywhere else either: the `sr-only` status text (4), `aria-current` staying put
  under `j`/`k` (6), roving `tabindex` and `aria-describedby` on triage rows (7), the toast clearing
  the scroll padding, which the catalogue measured at 142 px against 136 px (8), and the drawer's
  focus and Escape at 390 px (9).
- Proposed fold: close step 5's a11y dispatch returns a 15-row table, one row per finding: carried
  (with file:line) or not. Any "not" row joins the batched fix chain as a finding, quoted verbatim.
  This adds one instruction, not a reviewer.

### M3. Blockers 1 and 3 of the a11y review have no check in the real page

- Severity: major. Tag: `correctness`.
- Location: plan lines 61-69 (e2e step 3), 312-319 (T3 acceptance); a11y review findings 1 and 3;
  design lines 19-23.
- Defect: the single-key switch (finding 1, WCAG 2.1.4) and the auto-close setting and Keep (finding
  3, 2.2.1) are the review's two remaining blockers, and the design names both ("a saved switch in
  the sheet", "a saved setting turns auto-close off"). Only the pure `keyAction` unit test touches
  either one. Nothing checks that `?` opens the sheet, that the switch is saved and read on load,
  that with it off `a` does nothing in the page, that Escape or Keep stops the countdown, or that
  the empty page loaded with `desk.autoClose=off` neither counts nor focuses Keep. If the wiring
  breaks (the switch writes, but the handler reads a stale value), every listed check still passes.
- Proposed fold: T3's acceptance adds four Playwright steps on the seeded pair: `?` opens the
  sheet; with the switch off, `a` writes no hold and no toast, and after a `page.reload()` the switch
  still reads off; on the empty state, Escape stops the count (no `close` event after 35 s, and the
  close line reads "This tab stays open."); with `desk.autoClose` set to `off`, the empty state shows
  no count and does not focus Keep.

### M4. Following the DaisyUI countdown guide breaks a11y finding 4

- Severity: major. Tag: `correctness`.
- Location: plan lines 48-49 (judgment call 4), 202-204 (DaisyUI first), 305-306 (T3 empty state).
- Defect: the plan has the executor read each component's guide in the `daisyui` skill, and it
  adopts `countdown` for finding 14. That guide
  (`~/.claude/skills/daisyui/components/countdown.md:19`) says "Add `aria-live="polite"` and
  `aria-label="{number}"`". That restores the per-second announcements finding 4 removed ("keep the
  visible countdown outside the live region"), and the catalogue records it that way too: "`#secs`,
  which is not a live region".
- Proposed fold: one clause in T3: the countdown carries no `aria-live` or `aria-label`, because
  finding 4 overrides the guide; the one announcement goes through the `sr-only` region.

### M5. Queue order can tie, so the e2e's item sequence is not deterministic

- Severity: major. Tag: `correctness`.
- Location: plan lines 57-69 (e2e steps 2 and 3), 184-186 (Interfaces: queue order and next item);
  `bin/.local/bin/review-desk:13,23-39`; `review-desk/src/lib/server/items.ts:64`.
- Defect: `created` has one-second resolution (`date -u +%Y-%m-%dT%H:%M:%SZ`). The PR branch writes
  `item.json` only after two `gh` calls, while the design and triage branches write it at once. So
  three hand-overs started in sequence can produce design and triage items older than the PR item,
  or in the same second as each other. In a tie, order falls to `readdir` order, which the
  filesystem does not guarantee. The e2e asserts PR, then design, then triage, then empty. The
  "oldest other" fallback covers the PR's position, but a design and triage tie in either order
  sends the by-key round's `r` to the wrong page.
- Proposed fold: Interfaces names a tie-break: `created`, then `id`. The e2e waits at least 1 s
  after each hand-over's `item.json` appears before it starts the next, and asserts the queue's row
  order before it decides anything.

### M6. A binary file in the diff has no fixture, and this pass's own PR carries 16

- Severity: major. Tag: `correctness`.
- Location: plan lines 245-249 (T2 `fileGroups`), 266-268 (its test).
- Defect: `git diff --stat origin/main...HEAD` on this branch lists 16 binary PNG renders (`Bin 0 ->
  226362 bytes`, and so on). GitHub's diff renders each as a `diff --git` header, `new file mode`,
  and a `Binary files /dev/null and b/... differ` line, with no `---`/`+++` lines and no hunk. The
  `fileGroups` fixture has a top-level file, a new file, a deleted file, and a two-hunk file, but no
  binary file and no rename. A parser that takes paths from `+++ b/` drops or misnames all 16 files,
  and the test still passes. The step 10 hand-over of this very PR, and every later design pass
  with renders, hits that case.
- Proposed fold: add a binary new file and a rename to the `fileGroups` fixture. Take each path
  from the `diff --git a/... b/...` header. A binary file lists with no rows and counts of 0.

### M7. Leaving the item during the hold is unspecified, and client navigation keeps the timer alive

- Severity: major. Tag: `correctness`.
- Location: plan lines 47 (judgment call 4: a held decision ignores `a`, `r`, `1`, `2`, `3`) and
  295-299 (T3's hold and `goto`); catalogue "Undo hold" (the lock covers `#decision` buttons and
  `#note` only).
- Defect: during the 5-second hold, the queue links, `j`/`k` plus Enter, and the drawer still work.
  In the mockup a queue click is a full page load, which kills the timer, so nothing posts. In the
  build it is a client navigation, so the awaited `startHold` survives: the decision posts for the
  item Geoff left, and then `goto(next, { replace: true })` pulls him off the item he chose. No
  criterion covers it.
- Proposed fold: T3 adds a `beforeNavigate` that cancels the hold and announces "Undone. Nothing
  was sent.", matching the mockup's behavior. T3's acceptance adds: hold with `a`, then `j` and
  Enter within the hold; the other item loads, and no `decision.json` appears after 6 s. This
  follows the mockup's own behavior, so it is a routine call, not an owner fork.

### M8. A failed action and the decided state are unspecified, and the one-tab-per-hand-over model hits both daily

- Severity: major. Tag: `correctness`.
- Location: plan lines 293-303 (T3 item page); `review-desk/src/routes/item/[id=id]/+page.svelte:35-36`
  (the existing "Decided" state); `+page.server.ts:39-42` (a decided id is a 404 to an action).
- Defect: the design keeps one tab per hand-over (out of scope: one shared tab), so a close that
  hands over a PR and a triage list opens two tabs, and the queue lets Geoff decide both from the
  first. The second tab then shows a stale form, and its Approve gets a 404. The plan says what
  happens "on the action's success" only. It does not say what the custom `enhance` callback does
  with a failure or error result: today's default would show the error page, but a callback that
  handles only success leaves the page locked with no message. T3 also never carries forward the
  existing "Decided" display that replaces the form for a decided item.
- Proposed fold: T3 says that a non-success result falls to `enhance`'s default (`applyAction`) and
  unlocks the controls, and that a decided item still shows "Decided" in place of the bar. The load
  test keeps its decided case.

### M9. The triage e2e fixture is unnamed, and round 2's assertions check only that a decision printed

- Severity: major. Tag: `correctness`.
- Location: plan lines 57-59, 66-68, 70-72 (e2e steps 2 to 4), 302 (hidden inputs in original order).
- Defect: the server maps `disposition` and `reason` to rows by position
  (`+page.server.ts:84-99`), so the hidden inputs must stay in source order while the visible rows
  reorder by section. The "three-row triage list" is unnamed. If row 2's move to Drop does not
  change the rows' DOM order, a build that emits inputs in DOM order still prints row 2 as `drop`.
  Round 2 asserts only "Each command prints its decision". It does not check the note text, the
  disposition the menu set, or that an edited reason reaches the JSON, and nothing else checks an
  edited reason end to end.
- Proposed fold: name the fixture as three rows proposed `now`, `now`, `defer`. Moving row 2 to Drop
  then puts it after row 3 in the DOM, and a DOM-order bug would print row 2 as `defer`. Round 2
  asserts the reject's note text, the menu-chosen disposition on its row, and a reason edited in
  place, all read from each command's stdout JSON.

## Minor

### m1. Judgment call 3 contradicts itself on the figure labels

- Severity: minor. Tag: `optional`.
- Location: plan lines 40-43; design line 24.
- Defect: the call opens "Where the mockup and the design disagree, the design wins", then has the
  labels follow the mockup (Risk, Changes) where the design says class and files.
- Proposed fold: state it as a mockup-wins exception, with the reason: the design lists what the
  figures hold, and the mockup sets their wording.

### m2. The design says the command and server do not change; cite that in judgment call 1

- Severity: minor. Tag: `correctness`.
- Location: plan lines 29-33; design lines 39-40.
- Defect: the design says "Undo holds a decision in the page ... so the server and the `review-desk`
  command do not change." The plan changes both (new `gh` fields, `pr.json`, `number`, `file`,
  `listDecided`). In context the sentence describes undo's cost, and the Checks figure the design
  asks for has no other data source, so this does not change the design. But the PR read will see a
  literal contradiction.
- Proposed fold: judgment call 1 quotes the sentence and says the plan reads it as scoped to undo.
  The Checks figure needs `statusCheckRollup`, which only `gh` can supply.

### m3. "Sends nothing" and "posts after 5 seconds" name no observation

- Severity: minor. Tag: `correctness`.
- Location: plan lines 63-66 (e2e step 3).
- Defect: an implementation that posts as soon as the button is pressed would pass "`a` again posts
  after 5 seconds" if the check runs only after 5 s. "Sends nothing" names no file to check.
- Proposed fold: assert no `decision.json` and a live command at 4 s, then `decision.json` present
  by 6 s. After `z`, assert no `decision.json` at 6 s, and `#sr-status` reading "Undone. Nothing was
  sent."

### m4. Gaps in the T2 unit criteria

- Severity: minor. Tag: `correctness`.
- Location: plan lines 239-244 and 262-274.
- Defect: `keyAction` has no case for plain Enter on triage returning null (a11y finding 2).
  `reviewVerdict` has no case for `fix` (the error-ink trigger) or for "Not stated".
  `checksSummary` has no case for the `StatusContext` shape or an empty rollup. Its outcome says
  it returns counts and rows, but its test asserts the string "11 passed, 1 skipped", so the
  contract is split.
- Proposed fold: add the four cases, and name the module that formats the summary string.

### m5. T5's acceptance says "match the catalogue's description" without naming what to check

- Severity: minor. Tag: `optional`.
- Location: plan lines 359-361.
- Proposed fold: name the checks. The menu opens with `aria-expanded="true"` and focus on the
  checked item. Escape returns focus to "Move to". A pick puts the row in item-number order in its
  new section, focuses it, sets "was X", and updates the counts and the status line. In the reason
  input, Enter keeps the edit and Escape restores it.

### m6. Stopping the main checkout's app departs from an inherited convention without saying so

- Severity: minor. Tag: `correctness`.
- Location: plan lines 193-194 and 374-377; first desk plan "Stopping an app" ("Only by its
  worktree path").
- Proposed fold: list it among "Conventions every task follows" as the one sanctioned exception,
  with the waiting-item check as its guard.

### m7. Close runs two fix chains and an unbounded visual loop, where pass-core says one batched chain

- Severity: minor. Tag: `correctness`.
- Location: plan lines 382-394; pass-core SKILL.md lines 151-155.
- Defect: step 4 runs its own fix-and-reverify loop, which "exits only on a fresh PASS", and step 5
  runs a second chain. pass-core says the whole-branch review and `visual-verifier` feed "One
  batched fix chain".
- Proposed fold: run the step 4 and step 5 reviewers together, then one batched chain, then one
  fresh visual grade. A second FAIL is a "Stops" event.

### m8. The plan's own GitHub link breaks the empty-state close

- Severity: minor. Tag: `correctness`.
- Location: plan lines 332-333 (T4 adds the link) and 423-424 (Later item 1).
- Defect: the plan adds a GitHub link to the PR header. Opened in the same tab, it adds a history
  entry, and the empty state can no longer close the tab. Later defers rendered-body links, but this
  link is new in this pass.
- Proposed fold: the header's GitHub link opens in a new tab (`target="_blank" rel="noopener"`).
  Body links stay in Later.

### m9. Nothing checks the queue after a client navigation

- Severity: minor. Tag: `correctness`.
- Location: plan lines 281-288 and 312-317.
- Defect: the mockup reloads the whole page. The build relies on `refreshAll` to rerun the layout
  load. No check confirms that the decided item leaves the queue, that it appears under "Decided this
  session", or that `aria-current` moves to the item now open.
- Proposed fold: one assertion in T3's acceptance, after the first decision loads the other item.

### m10. Small e2e ambiguities

- Severity: minor. Tag: `optional`.
- Location: plan lines 70 and 73-74.
- Defect: step 4's "a fresh PR" does not say which PR (only one exists unless M1(b) is taken). Step 5
  runs real `firefox`, but step 2 puts a stub first on `PATH`.
- Proposed fold: step 4 hands over the same PR again as a new item; step 5 runs with the stub
  removed from `PATH`.

## Over-ceremony (ranked by clock and token cost)

### o1. Rerunning the whole e2e and the 16-render grade after any fix that touches `review-desk/`

- Severity: minor. Tag: `optional`.
- Location: plan lines 393-394 and 413-414.
- Defect: nearly every fix touches `review-desk/`, so this always triggers. A rerun costs two
  30-second countdowns, a 60-second Firefox run, the `gh` fetches, and a fresh 16-image verifier: an
  estimated 15 to 20 minutes and the verifier's tokens.
- Proposed fold: rerun the by-key round, and retake and regrade only the screens the chain touched.

### o2. Per-task screenshots at four configurations, repeated in full at close

- Severity: minor. Tag: `optional`.
- Location: plan lines 317-318, 341-343, 359-361.
- Defect: T3, T4, and T5 each self-grade four configurations that the close regrades with a fresh
  verifier. The canonical loop is worth keeping, but the self-grade's "no structural difference the
  session can see" is not evidence, and the close grade is.
- Proposed fold: each task's loop checks 1440 light and 390 dark, and the 16-config grade stays at
  close.

## Scope check

The plan promises nothing the approved mockups do not show, apart from judgment calls 1 to 5, each
of which it records. "Decided this session", the meta line, the GitHub link, and the read time are
mockup devices, which the design takes in by "matches the approved mockups". Each design promise
maps to a task: the queue and drawer (T3), the keys (T2 and T3), the PR, design, and triage views
(T4 and T5), the undo (T2 and T3), same-tab loading (T3), the empty state (T3), and the merge-time
rebuild (close step 9). The gaps are in the criteria, not in what gets built.
