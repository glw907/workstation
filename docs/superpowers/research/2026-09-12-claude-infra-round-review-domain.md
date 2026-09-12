# Claude infra round, revision 1: adversarial review, DOMAIN RISK lens

Reviewer: fresh-context domain-risk lens, 2026-09-12. Read-only; nothing edited outside this
file. Plan under review: `docs/superpowers/plans/2026-09-12-claude-infra-round.md` at revision
1. Line numbers below are that file's.

Scope of this lens: what the round can break for a consumer the plan did not consider, and
what the plan gets wrong about the domain. Conductor-ruled items (site-repo deletions, the
fifth pick in principle, the reader's model pin, the dropped RESEND line, the commit footer)
are not re-litigated, except where point 1 asks whether a displaced rule is load-bearing.

Counts: 5 BLOCKER, 14 MAJOR, 9 MINOR.

## Evidence gathered live

- `/sys/class/power_supply/`: `AC` (`type=Mains`, `online=0`), `BAT0` (`type=Battery`,
  `status=Discharging`, `capacity=37`, `charge_control_end_threshold=100`), and two
  `ucsi-source-psy-USBC000:00{1,2}` (`type=USB`, each with its own `online`). **The machine is
  on battery at 37% right now.**
- The cairn overnight run is live: `wf_2d52758e-603`, last journal event
  `{"type":"started","label":"impl:2","phase":"▸ pass-execute-chains #3"}`. Its runaway guard
  (pid 546075) and its own battery watchdog (`BAT0/status` = `Discharging` and `capacity <= 15`)
  are both running. That session's cwd is `~/Projects/cairn-cms`.
- `cairn-overnight-to-release.js:210` invokes `workflow({ scriptPath: a.chainsScript })` and
  names only `pass-execute-chains.js` (`:11`). Neither workflow script requires the other.
- `~/.claude/{agents,docs,skills,instructions,workflows}` are folded symlinks into the stow
  source. Correction 1 holds.
- `claude-context-budget:18,22` confirms `CLAUDE_MD_BUDGET=6000` and `wc -c / 4`.
  `claude/.claude/CLAUDE.md` is 27,807 bytes. Arithmetic in task 6 checks out.
- `~/.dotfiles` HEAD is `603f667`, not the pre-flight's `9034fd3`; the one changed file is the
  plan itself. `git status --short` still shows only the warm `cairn-implementer.md`.
- `cairn-run-gate` behavior read in full, lines 15-60. The four behavior claims the plan makes
  are accurate. The branch at `:44-51` is not covered; see M5.

---

## BLOCKER

### BLOCKER 1. Task 1's Files range excludes the phrase that most contradicts the new rule
**Line 238-240 (Files), and criterion 1 at 268-269.**
The defect: `dubplate-implementer.md` line **67** reads "5. Run the gate once, through the
blocking runner:", and the plan's range is `:68-71`, so "Run the gate once" survives a task
whose whole point is that the caller re-issues the command, while criterion 1 bans only "blocks
to completion" and "one call gives you one result".
The fix: widen the Files range to `:67-71` and add "no file says to run the gate once" to
criterion 1.

### BLOCKER 2. The wording source is another live session's uncommitted diff, and a criterion demands it stay uncommitted
**Lines 247-250 (source), 278-279 (criterion 4).**
The defect: the round reads its template from `git -C ~/.dotfiles diff
claude/.claude/agents/cairn-implementer.md` and requires that file to still be "modified and
unstaged" when the round's first task ends, so the cairn session doing the one thing the plan
says it owns (committing its own file) both destroys the wording source and fails a blocking
criterion for reasons unrelated to task 1's work.
The fix: have task 0 snapshot the paragraph to a scratch file the plan names, source the wording
from that snapshot, and restate criterion 4 as "this round neither staged nor altered the file",
provable from `git log -1 --format=%an -- <path>` plus an unchanged diff-or-commit body.

### BLOCKER 3. Pick 5 buries two rules that are load-bearing at the moment a pass launches
**Line 569 (pick 5), 580-582 (the preserved trigger).**
The defect: the "Gate economy on a pass" section is the only home for "Gates run through
`cairn-run-gate '<string>'`" and for "the Workflow tool refuses a `~/.claude/workflows`
scriptPath (copy to the session scratchpad)"; the trigger the plan preserves ("a pass's gate is
scoped to what it can catch") fires when choosing a gate, never when launching a workflow or
reaching for a gate runner, so a session behind that pointer has no reason to read the doc
before it needs those two rules. The same section also uniquely carries "halt agents PREPEND to
STATUS" and "Task 0 takes no gate", which this plan itself depends on.
The fix: keep the orchestrator-hygiene bullet and the `cairn-run-gate` sentence inline, displace
only the per-leg economics, and re-measure the shortfall against pick 4.

### BLOCKER 4. Pick 1's preserved trigger presupposes the decision the displaced text makes
**Line 565 (pick 1), 580-582.**
The defect: the CLAUDE.md paragraph carries the arming thresholds ("Past ~30 minutes", "On
battery"), the word "mandatory", and the diagnostic "check `journalctl` for suspends before
calling it stalled"; the plan preserves only "before arming either guard", which a session
reaches only after it has already decided to arm, so the rule that produces the decision and the
rule that prevents a false stall diagnosis both go behind a pointer nothing triggers. The
2026-09-08 candidates doc's claim that the pointer "loses nothing" is the same error.
The fix: the pointer must keep, inline, the two arming triggers, the word mandatory, and the
journalctl sentence, and displace only the procedures.

### BLOCKER 5. Hoisting `ai-operational-rules.md` verbatim installs a wrong secrets rule and one repo's deploy pipeline machine-wide
**Lines 356-357 (Files), 374-379 (take ecxc-ski's body), criterion 2 at 396-397.**
The defect: `ecxc-ski/.claude/instructions/ai-operational-rules.md:83` reads "All local dev
secrets in `~/.bashrc`", which contradicts the global CLAUDE.md secrets policy (sensitive values
live in `~/.local/secrets` from the age store) and contradicts line 18 of the same file; its
`:40` manual deploy is `npm run build && npx pagefind --site .svelte-kit/cloudflare && npx
wrangler deploy`, true of ecxc-ski and 907-life and of no other repo; and its `:35` blanket ban
on `npx wrangler deploy` contradicts the global Cloudflare section, which names that command as
the route. Criterion 2 requires the hoisted file to be byte-identical to ecxc-ski's copy, so the
implementer is forbidden from fixing any of it, and criterion 3 checks only for `hugo --minify`
and `RESEND_API_KEY`.
The fix: make this task an edit, not a verbatim hoist: correct the secrets line to the age-store
policy, move the pagefind deploy command to a "for the pagefind sites" clause or to each repo's
CLAUDE.md, qualify the wrangler-deploy ban as "for an Actions-deployed site", and replace
criterion 2 with a named list of the deltas the hoist must make.

---

## MAJOR

### MAJOR 1. Task 0's live-executor check is structurally blind to the one contended writer the plan names
**Lines 220-227 (criteria 1-3), 42-47 (pre-flight).**
The defect: the check is `pgrep -f dotfiles` plus `/proc/<pid>/cwd` under `~/.dotfiles`, but the
survey's own constraint says the cairn session "writes into the stow source through the
`~/.claude` symlinks"; that session's cwd is `~/Projects/cairn-cms`, so it passes every task-0
criterion while live, exactly the failure dubplate's CLAUDE.md already names ("the live-executor
check is the lane registry, not `pgrep -f`").
The fix: add a criterion that enumerates live Claude sessions with a workflow journal newer than
five minutes (the `subagents/workflows/wf_*/journal.jsonl` under every project) and records which
`~/.claude` surfaces each may write, and treat a live run as contention on the shared tree rather
than on a cwd.

### MAJOR 2. No AC or battery precondition, on a machine that is on battery now
**Lines 204-227 (task 0), 786-807 (Risks).**
The defect: the round has a 1.0M ceiling over eight dispatched tasks and arms nothing; the global
rule requires the runaway guard past ~30 minutes and, on battery, `systemd-inhibit` plus the
battery watchdog. `AC/online` reads 0 and `BAT0` is at 37% and discharging, with a live cairn run
already drawing from the same battery and its own watchdog set to stand down at 15%.
The fix: add to task 0 a criterion that AC is online or the two battery-layer guards are armed
and named, and state that a stand-down at the floor halts this round before the cairn run.

### MAJOR 3. Correction B deletes the discharge signal outright, which is wrong in the other direction
**Lines 324-327.**
The defect: gating solely on `AC*/online` makes the watchdog silent whenever a supply is present,
including the case where an underpowered USB-C or dock supply reads online while the battery
still drains, so the guard that exists to save state by 10% stops firing in the one plugged-in
case that still reaches 0%.
The fix: keep a drain test alongside the AC test: alarm at 11% when AC is offline **or** capacity
has fallen across two consecutive polls, and say that "Not charging" alone is not a drain signal.

### MAJOR 4. The `AC*/online` glob is the wrong shape for this machine's supply set
**Lines 325-327, 337-338.**
The defect: `/sys/class/power_supply/` holds `AC` (Mains) plus `ucsi-source-psy-USBC000:001` and
`:002` (type USB), each with its own `online`; the `AC*` glob reads only the ACPI adapter, and
whether that adapter reflects USB-C PD charging on this laptop is unverified (everything reads 0
while unplugged, so it cannot be checked from this session).
The fix: write the test as "any supply whose `type` is `Mains` reads `online` 1", and add a
one-line verification step to be run once while plugged in over USB-C before the `BAT*/status`
test is removed.

### MAJOR 5. The adopted wording omits the runner's third exit path, which produces a false red
**Lines 252-256 (the behavior to carry), 125-127 (the gate loop), and task 7 item 1 at 636-639.**
The defect: `cairn-run-gate:44-51` has a branch the plan never mentions. If the detached gate dies
without writing a status (killed, OOM, harness restart), the next re-issue prints "gate process
vanished without a status; treating as failure" and then `gate exit: 1`, which satisfies the
plan's own loop condition ("re-issued on exit 75 until it prints `gate exit:`") with a failure
the gate never produced; an implementer then reports a red gate and the reviewer blocks.
The fix: add the branch to the wording in all three files: a "gate process vanished" line means
the run was lost, not that the gate failed, so start a fresh run rather than reporting red.

### MAJOR 6. The plan verifies the runner's behavior against the runner's comment header, not its code
**Lines 252 and 639, both citing `bin/.local/bin/cairn-run-gate:1-14`.**
The defect: lines 1-14 of that file are the comment block; the code is `:15-60`. The header omits
the vanished-status branch entirely, which is why MAJOR 5 exists, and it is documentation that can
drift from the script it sits on.
The fix: cite `:15-60` as the behavior source and the header as the prose precedent, and require
the implementer to reconcile the two.

### MAJOR 7. The `svelte-check` skill is wrong for three Svelte repos that never opted in, and will trigger in dubplate
**Lines 371-374 (hoist verbatim), criterion 6 at 406-407, risk note at 794-796.**
The defect: the skill's step 2 says a clean run's "output ends with `svelte-check found 0 errors
and 0 warnings`", true of `ecxc-ski` and `cairn-cms` but false of `aksailingclub-org`,
`xcathletes-org` (`check` continues into `lint:openapi`) and `cairn-pub` (`check:docs-links`), and
`907-life`, `aksailingclub-org`, `xcathletes-org` and `cairn-pub` all prefix `svelte-kit sync`,
which the skill's Notes present as a separate remedy. Separately, dubplate's `web/` is SvelteKit,
so the description that criterion 6 relies on as the mis-trigger guard is precisely what makes the
skill fire in dubplate, where the gate is `bash scripts/check.sh` and `npm run check` from the
repo root does not exist.
The fix: make the hoisted body read the repo's own `check` script and report on whatever legs it
runs, state that `svelte-kit sync` may already be part of it, and add "not for a repo whose web
app is a subdirectory of a non-Node gate" to the description; then list the five newly affected
repos in the plan's risk section.

### MAJOR 8. A workstation `documentation-standards.md` becomes a second, unrouted doc standard
**Lines 359, 362 (Files), 374-379.**
The defect: the file carries its own title, structure, and phrasing rules, which now sit at the
same altitude as the authoring charter and the `writing-voice` audience router with no precedence
rule; the two disagree in places (the charter routes developer docs to Google, this file states
house rules), and every repo on the machine gains the second one.
The fix: either state in the hoisted file that it is subordinate to
`~/.claude/docs/authoring-charter.md` and applies only where the charter names no standard, or
route its content into the charter and keep no second file.

### MAJOR 9. The instruction hoist makes the content less reachable for its only two consumers
**Lines 380-383.**
The defect: the plan's justification is that nothing references either file, so no pointer is
needed because "they are reached by an agent reading the path". That is circular. Today an agent
in `907-life` or `ecxc-ski` finds the file by listing the repo's `.claude/`; after the hoist those
two repos have nothing naming it, and the plan forbids editing their `CLAUDE.md`, so the round's
stated goal (every consumer reads one correct copy) is not achieved for either consumer.
The fix: add one line to each repo's `CLAUDE.md` naming `~/.claude/instructions/`, or keep the
hoist and record the pointer edits as owed follow-up in the handoff document.

### MAJOR 10. `go-architecture-reader` is not free of dubplate specifics
**Lines 430-432 (hoist verbatim, names nothing dubplate-specific), criterion 1 at 446-448.**
The defect: the body says "a later rung will want it", "every rung that ships around it", and "A
2.0 forward hook is named in a plan and built by the rung that consumes it". Rungs and the 2.0
forward-hooks list are dubplate's ladder and dubplate's streamer spec; poplar has phases and
passes and no 2.0 spec, so a poplar dispatch of the shared agent reads instructions about a
structure its repo does not have, and the verbatim constraint plus criterion 1 forbid the
implementer from generalizing them.
The fix: replace the three rung phrases with repo-neutral wording ("a later task", "the task that
consumes it") and require the dispatch to name the repo's forward-hook rule if it has one; adjust
criterion 1 from byte-identity to a named delta list.

### MAJOR 11. "poplar gains an agent it lacked" overstates the outcome
**Lines 426-427.**
The defect: poplar's `CLAUDE.md` "Conducting a pass" section enumerates its reviewers
(`poplar-implementer`, `diff-reviewer`, `poplar-reviewer`, `poplar-go-reviewer`) and names no
architecture reader, and the round edits no poplar file, so after the hoist poplar has a visible
agent nothing dispatches.
The fix: state the outcome as "the agent becomes available to poplar", and record the poplar
`CLAUDE.md` amendment as owed in the handoff document.

### MAJOR 12. Pick 3's destination does not carry the two sentences that matter most
**Line 567 ("No text moves"), pre-flight Correction 4 at 75-78.**
The defect: `cloudflare-estate-inventory.md` carries the account id and the ASC service-token
route (`:40-42`) but not the authority grant ("make routine changes directly; never treat
Cloudflare state as read-only") and not the caveat that the MCP token is read-only for
Access and Workers-domain writes so those go through curl. Its `:31` describes the MCP OAuth as
broad read that refuses writes, which is adjacent but is not the routing instruction. So "No text
moves" is false for pick 3 and the two operative sentences would be dropped, not displaced. Both
are load-bearing at session start: a session that does not know it holds write authority asks
Geoff or reports the estate read-only, the exact failure the paragraph was written to stop.
The fix: keep the authority grant and the curl caveat inline as the pointer's body, or move both
sentences into the inventory doc first and prove the grep hit before trimming, as constraint
586-588 already requires for picks 1, 3 and 4.

### MAJOR 13. The additive-state risk claim is false for the two tasks that delete
**Line 790, with tasks 3 and 4.**
The defect: "A half-landed round leaves additive state" does not hold for task 3 (six deletions)
or task 4 (one deletion); neither task states create-before-delete ordering, so a task that
half-lands with the deletes committed and the dotfiles create missing removes an asset from every
consumer.
The fix: mandate create-and-verify-the-symlink before any delete in both tasks, make it a
criterion, and correct the risk sentence.

### MAJOR 14. The plan's own launch shape is the one the gate-economy rule says the Workflow tool refuses
**Lines 7-9 (the agentic-workers note), 141-143 (segments A and B), task 7 item 3 at 650-659.**
The defect: the plan names `~/.claude/workflows/pass-execute.js` as what segments A and B run,
while the rule in CLAUDE.md's gate-economy section says the Workflow tool refuses a
`~/.claude/workflows` scriptPath and the script must be copied to the session scratchpad;
`pass-execute.js:8` documents the refused shape too, and task 7's skill-text item does not fix it.
The fix: state the scratchpad-copy step in the plan's execution-mode section, and add the
corrected scriptPath to task 7's header-comment changes.

---

## MINOR

### MINOR 1. Correction A risks deleting a true and load-bearing parenthetical
**Lines 315-320, criterion 1 at 333-334.**
The defect: the doc's "`journal.jsonl` only records agent starts and finishes, so a long-running
task looks idle there" is true and is the reason the guard polls the transcripts; criterion 1 ("no
longer instructs a reader to disregard `journal.jsonl`") invites an implementer to cut it.
The fix: say explicitly that the sentence stays and gains the completion-filter clause, so the
doc reads "journal for completion, transcripts for idle and size".

### MINOR 2. The working guard implementation is left unrecorded and ephemeral
**Lines 307-320.**
The defect: the correction lands as prose while the guard that actually reads the journal lives at
`~/.cache/cairn-overnight-2026-09-12/runaway-guard.sh`, a path the next session will not find and
the cache may drop.
The fix: have task 2 name that script as the reference implementation, or copy it into
`~/.dotfiles/bin/.local/bin/` as the armable form.

### MINOR 3. Task 7's precondition is unverifiable as written, and aimed at the wrong risk
**Lines 160-163, 625-627.**
The defect: verified live, the cairn run executes `pass-execute-chains.js` and
`cairn-overnight-to-release.js:210` invokes only that path, so the plan's reading is correct in
substance. But the plan gives no mechanism for "confirm no live workflow run is executing it", and
because a nested `workflow({scriptPath})` re-reads its script at each invocation, the real hazard
is a live run that invokes `pass-execute.js` later, which no point-in-time check can see.
The fix: replace the precondition with a concrete check (grep every live session's workflow
journal for `pass-execute` phases, and confirm no `chainsScript` argument points at
`pass-execute.js`), and state the re-read-per-invocation semantics as the reason.

### MINOR 4. No dubplate re-check immediately before the two dubplate commits
**Lines 264-266 (task 1 commits), 435-437 (task 4).**
The defect: dubplate is checked once in task 0 and written in tasks 1 and 4, segments apart, while
the dubplate conductor is holding a launch-ready 5b-ii lane plan; dubplate's own CLAUDE.md names
the lane registry, not `git worktree list`, as the live-executor check.
The fix: add a criterion to both tasks that re-checks the dubplate lane registry and
`git status --short` at commit time.

### MINOR 5. The pre-flight's tree state is already stale
**Lines 3, 37-41.**
The defect: `~/.dotfiles` HEAD is `603f667`, one commit past the stated `9034fd3`; the commit is
the plan itself, so nothing is affected, but the pre-flight reads as current and is not.
The fix: note that the plan's own commit is the expected delta and re-verify at task 0.

### MINOR 6. The Bash timeout has almost no margin over the runner's wait
**Lines 262-263.**
The defect: `timeout: 600000` is the Bash tool's maximum and `CAIRN_GATE_WAIT` defaults to 540
seconds plus up to 7 seconds of loop tail and process startup, so any raise of `CAIRN_GATE_WAIT`
silently turns the protocol into a tool timeout with no exit status.
The fix: say in the adopted wording that the runner's wait must stay below the Bash tool's
ten-minute cap, and that `CAIRN_GATE_WAIT` is not to be raised without lowering the wait.

### MINOR 7. Task 7 item 2 does not say where the appended argument lands
**Lines 640-649.**
The defect: `pass-execute-chains.js` appends `paintProtocol` inside the criteria line (`:75`,
`:104`), not as a separate prompt line; the plan says "appended to every task's prompt at prompt
time", which leaves the placement to the implementer and makes criterion 3's "changes no prompt
line other than the gate sentence" ambiguous.
The fix: name the placement, matching the chains precedent, in the constraint.

### MINOR 8. Pick 4's destination claim overreaches the same way pick 3's does
**Lines 76-78, 568.**
The defect: `secrets/registry.md` carries `secret-set.sh`'s three input flags and `sync.sh
--worker NAME`, but not the ASC per-project-store exception nor the worker-only
`MAGIC_LINK_SECRET`/`SESSION_SECRET` carve-out that the CLAUDE.md bullet states. Pick 4 is the
fallback rather than the applied pick, so this bites only if an earlier pick sheds less than
estimated.
The fix: record the two missing exceptions as content that must move first if pick 4 is reached.

### MINOR 9. The byte ceiling is 24,003, not 24,000
**Lines 539-542, criterion 1 at 597-598.**
The defect: `tokens_of` uses integer division, so the gate trips at 24,004 bytes; the plan's
"under 24,000" is conservative rather than wrong, but the arithmetic it states as the ceiling is
off by three bytes.
The fix: state the gate's actual trip point beside the target.
