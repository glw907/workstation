# Lean pass process spec: mechanics and feasibility review

Target: `docs/superpowers/specs/2026-10-10-lean-pass-process-design.md` at `a0fa4b6`. Lens: does each
stated mechanism behave as stated. Probes ran in `/tmp/claude-1000/lean-review/` against an isolated
scratch repo (own `TMPDIR`, receipt and records dirs, `CAIRN_GATE_PARALLEL=1`), so no live lock or
record was touched. Approved rulings are not relitigated.

Counts: 3 blocker, 4 major, 2 minor. Owner forks: 2 (B1, M2).

## Blockers

### B1. Five of seven repos have no CI to carry the suites, and the local full gate is retired (OWNER FORK)

- **Where:** spec:80 ("CI green on the head"), spec:85-86 (local full gate retired), spec:98-99.
- **Defect:** Execution item 3 moves every whole suite to CI, but only cairn-cms and aksailingclub-org
  run CI on a pull request. ecxc-ski, 907-life, and cairn-pub carry only `deploy.yml` (`push:
  branches: [main]`), which runs `npm ci`, `build`, and `wrangler deploy` with no test or type check.
  xcathletes-org and dubplate have no workflows. `ci-green` needs `.github/ci-green.json`, which only
  cairn-cms has. So in five repos the whole suites never run before merge, "CI green on the head" has
  no meaning, and on a site the merge itself deploys to production.
- **Evidence:** trigger scan of every `.github/workflows/*.yml`; `ls ~/Projects/*/.github/ci-green.json`
  returns only cairn-cms. The parked design had the rule this spec dropped: "a repo with no CI keeps
  every leg local" (cairn-cms `specs/2026-10-10-pass-clock-time-design.md:85-87`).
- **Options:** (a) each adapter declares its whole-suite proof: CI where it exists, otherwise one
  local full gate through `cairn-run-gate` at close, its receipt cited in the PR body; (b) add PR CI
  to the five repos as part of rollout step 3. **Recommendation:** (a) now, since it costs one gate
  per pass. File (b) on ROADMAP.

### B2. Pair subagents' worktrees branch from `origin/main`, not from the pass branch

- **Where:** spec:93 ("two subagents with worktree isolation through the Agent tool"), spec:43.
- **Defect:** Claude Code creates a subagent worktree from the remote default branch unless
  `worktree.baseRef` is `"head"`. No settings file on the workstation sets it, and every target repo
  has `origin/HEAD` cached. So each pair agent starts without the pass's earlier commits. Its diff
  then runs against the wrong base and its gate proves the wrong tree. The spec also leaves out
  three other steps:
  - How the two worktree branches get back onto the pass branch, and who merges them before the push.
  - The fresh-checkout setup. cairn needs `npm ci` at the root (802M) and in `examples/showcase` (365M)
    in each worktree. That cost is missing from the price table, and the catch ledger counts worktree
    setup among the three lessons re-hit inside 48 hours.
  - A disjointness rule. Generated outputs such as the emitted template, the surface snapshot, and
    the norms manifest collide even when the hand-written files are disjoint.
- **Evidence:** worktrees docs: "Subagent worktrees use the same base branch as `--worktree`, so they
  branch from your repository's default branch unless `worktree.baseRef` is set to `"head"`."
  Sub-agents docs: "branched by default from your default branch rather than the parent session's
  `HEAD`." Settings probe: `worktree` key absent from `~/.claude/settings*.json` and every
  `~/Projects/*/.claude/settings*.json`. `git symbolic-ref refs/remotes/origin/HEAD` resolves in all
  eight repos. The docs also warn that a command is refused "when it can't verify from the command
  text that any git the command runs stays inside the worktree." Nobody has run a pair agent that
  calls `cairn-run-gate` under those checks.
- **Fold:**
  - Set `"worktree": {"baseRef": "head"}` in the stowed global settings.
  - The session commits before it spawns a pair. When both agents return, it merges their branches
    and then pushes.
  - Each adapter names its worktree setup command.
  - Pair only tasks whose Files lists, including generated outputs, are disjoint.
  - Rollout step 1 runs one live pair probe that calls `cairn-run-gate` in its worktree.

### B3. The cairn fast lane as stated runs a browser suite concurrently, off the heavy lane

- **Where:** spec:94-97; spec:143.
- **Defect:** cairn's component project is Vitest browser mode on real Chromium
  (`vitest.config.ts:211-215`). The spec runs it concurrently with the other legs and keeps it off the
  heavy lock. Two sources say that fails:
  - `gate-tier.mjs:71-76` records that running the component project in parallel with the node
    projects "stalls on the maintainer's workstation". It also records that the local gate serializes
    it with `--no-file-parallelism` for that reason.
  - `cairn-run-gate`'s own rule (lines 29-34) puts a browser-bearing gate on the heavy lane. The light
    lane caps the scope at 2G high and 3G max. svelte-check, the node projects, and Chromium together
    exceed that, so the scope throttles or is OOM-killed, and the caller reads that as "gate vanished".

  The machine has 15 GB and 8 cores, so two pairs each running this lane repeat the 2026-09-14 failure
  that cost the GNOME session. Separately, the spec does not say whether `gate-tier.mjs` or
  `cairn-run-gate` owns the concurrency ("fast-lane mode", spec:105).
- **Evidence:** the quoted source lines; `free -g` reports 15 total.
- **Fold:**
  - `npm run package` runs first, since `unit-dist-spawn` and the surface checks read `dist`.
  - The non-browser legs run concurrently on the light lane: the type check, the selected static
    checks, the docs gate, and the node projects.
  - The narrowed component leg then runs alone, under the heavy cap and lock. Reword spec:96-97 to
    "the heavy lock for any browser leg: component tests or a named e2e spec."
  - `cairn-run-gate` owns concurrency as a legs mode. It records each leg's exit and duration, which
    also closes friction-log entry 77 (per-leg timing).

## Majors

### M1. The `cairn-run-gate` fixes miss the real duplicate-run mechanism and the real cap cause

- **Where:** spec:103-105.
- **Defect 1: a concurrent-waiter race.** When the Bash tool moves a gate call to the background,
  that copy keeps waiting. The agent then re-issues, so two waiters share one state directory. The
  first waiter to see the status file deletes it. The second sees a dead pid and no status, takes the
  vanish branch, and prints "gate vanished; re-issue starts a fresh run". The exit-75 protocol then
  re-runs the whole gate and writes a false `vanished` record. "Reprints a finished result to a repeat
  call" covers a sequential repeat, so this race survives the fix as worded.
- **Probe:** gate `sleep 6`, two waiters one second apart. Waiter 1 got `gate vanished` and exit 75.
  Waiter 2 got `gate exit: 0`. A third call started a fresh run.
- **Defect 2: the overrun has a different cause.** The script already waits 540 s, under 600. The
  overrun comes from its loop counting nominal seconds (`waited=$((waited + poll_s))`, line 333).
  Wall-clock time is not measured, and each iteration forks `sleep` on a machine under gate load.
  Pass B's transcript shows three plain calls with `timeout: 600000` moved to the background at
  21:21, 21:38, and 22:14.
- **Defect 3: the timeout instruction disappears.** The Bash tool's default timeout is 120 s, and
  callers get 600 s only because the implementer definitions say `timeout: 600000`
  (`cairn-implementer.md:109`, `site-implementer.md:95`). The spec drops that "gate protocol"
  (spec:136). A Sonnet session that omits the parameter has every gate call moved to the background
  at 120 s.
- **Fold:**
  - Reprint from a per-run result file. The finishing waiter leaves it in place until a new run
    starts, and both the reattach path and the vanish path read it before declaring a loss.
  - Keyed by tree fingerprint, the reprint suppresses a legitimate flake rerun on the same tree, so
    add `--fresh`.
  - Measure the deadline with `$SECONDS` and default the wait to 480 s.
  - Put "call with Bash `timeout: 600000`" in the tool's own exit-75 and usage text, where it executes.
  - An argument starting with `-` that is not a known flag exits 2. Probe: `cairn-run-gate --pin`
    and `--help` today run `bash -c --…` and return `gate exit: 2`. On the default heavy lane that
    happens only after queuing for the lock.

### M2. The executing session's launch, and the clock stop's trigger and recipient, are unspecified (OWNER FORK on recipient)

- **Where:** spec:91 and spec:101-102.
- **Defect:** The spec never says how the Sonnet session starts: who launches it, with what model,
  effort, and permission mode. An unattended session in default permission mode blocks on prompts,
  which costs Geoff time outside his two touchpoints. The clock stop has no trigger. A model checks
  the time only when told to, and the cases that need the stop are exactly where it would forget, as
  in pass B S1's 87 minutes of gate loops. "Reports to STATUS" also names nobody who reads it.
- **Evidence:** `claude --help` offers `--bg`, `--model`, `--effort`, and `--permission-mode`
  (choices include `auto`). Anthropic: "Unlike CLAUDE.md instructions which are advisory, hooks are
  deterministic" (research file section 6).
- **Fold:**
  - The design session launches `claude --bg --model sonnet --effort medium --permission-mode auto`
    in the pass checkout and records the session id in STATUS.
  - The clock stop is a `PostToolUse` hook. It reads a task-clock file that the session writes at
    each task start (task id, start time, estimate) and prints a stop line into context once elapsed
    time passes twice the estimate.
- **Options for the recipient:** (a) STATUS plus a normal-urgency `notify-send`, then the session
  waits for Geoff; (b) the session dispatches one Opus re-plan read and continues, and notifies Geoff
  only on a second stop. **Recommendation:** (a). The catch ledger's strategic catches (S7) were all
  Geoff's, and the stop exists to bring them forward.

### M3. Nothing tells the session about a CI red while it works the next task, and cairn CI needs an open PR

- **Where:** spec:98-99.
- **Defect:** cairn's workflows trigger on `push` only for `main` and `rebuild`. Any other branch
  gets CI only through `pull_request`. A pass branch without an open PR therefore runs no CI per
  push. The spec opens a PR only at close (spec:83). Pass B works today only because draft PR #111
  exists. The spec also gives no channel for a red to reach the session mid-task.
- **Evidence:** the `on:` blocks of `test.yml`, `e2e.yml`, `create-site.yml`, `design.yml`, and
  `scaffold.yml`. `ci-green` requires `--pr <n>` and returns 75 while runs are pending.
- **Fold:**
  - The first push opens a draft PR.
  - After each push the session starts
    `until ci-green <sha> --pr <n> --wait; [ $? -ne 75 ]; do :; done` as a background Bash task. The
    harness re-invokes the session when it exits, and exit 1 stops the line.

### M4. No mechanism loads the close review's domain checklists, and two of them have no source

- **Where:** spec:80-81 and spec:137-138.
- **Defect:** "Checklists load by the paths the diff touched" has no implementation. Nothing maps a
  path glob to a file. Of the five domains named, only four have files: the svelte, Workers,
  DaisyUI-a11y, and auth reviewers. Go has no checklist, and the table says "four". `diff-reviewer.md`
  is written for one task's diff and a conductor, and the spec keeps it unchanged for a whole-branch
  read. The close seats hold 11 of 12 audited unique catches (ledger S6), so a reviewer that never
  loads a checklist loses the step's yield.
- **Fold:**
  - Each adapter carries a glob-to-checklist table, and the close dispatch passes the matched files'
    paths.
  - Go maps to the `go-conventions` skill.
  - `diff-reviewer.md` moves to the trim list: per-task or whole-branch scope, no conductor.

## Minor

### m1. The `defer` exit has no definition and no consumer

- **Where:** spec:105.
- **Defect:** The lean spec has no targeted lane that defers.
- **Fold:** Drop the defer exit. The other option is to define it as the parked design's semantics:
  `flock -n` on the held heavy lock, a distinct exit code, a `deferred` record, and that push's CI run
  as the acceptance proof. Under that option, `auth-data` tasks wait instead of deferring.

### m2. Rollout points at the wrong repo and misses three breakages

- **Where:** spec:150-161.
- **Defects:**
  - `cairn-pass` lives at `~/.dotfiles/claude/.claude/skills/cairn-pass/`, not in cairn-cms, so
    step 2's "on a cairn branch" is the wrong repo.
  - Deleting the runners reddens the dotfiles repo gate, because `scripts/check.sh:44` runs
    `tests/pass-execute-runners.test.mjs`. The step 1 sweep covers only skills and agents.
  - Pass B's branch gains the fast lane only after it merges `main` once step 2 lands. Its plan
    carries no clock estimates, pair marks, or risk class, so the clock stop cannot fire until the
    plan is re-cut.
  - Step 3 says only "check" the cap. aksailingclub-org (262 lines) and dubplate (356) are over it, and
    the spec gives no action.
- **Evidence:** all line counts in spec:130-141 match `wc -l`. The research file quotes both caps,
  and the 500-line skill cap was re-read on the skill best-practices page.
