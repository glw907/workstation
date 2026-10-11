# Lean pass process spec: fold verification

Target: `docs/superpowers/specs/2026-10-10-lean-pass-process-design.md` at `38ffcb2`, against its
pre-fold text at `a0fa4b6`, the fold record
`docs/superpowers/research/2026-10-10-lean-pass-process-fold.md`, and the three lens reviews beside
it. Probes ran in `/tmp/claude-1000/fold-verify/` on 2026-10-10. Only gaps that affect correctness or
a stated requirement are listed.

Counts: 0 blocker, 3 major, 5 minor.

## Probes

| Mechanism | Result | Evidence |
|---|---|---|
| `worktree.baseRef: "head"` for Agent-tool subagent worktrees | Holds as stated | code.claude.com/docs/en/worktrees: "Subagent worktrees use the same base branch as `--worktree`, so they branch from your repository's default branch unless `worktree.baseRef` is set to `"head"`." Under "Choose the base branch": `"head"` branches "from your current local `HEAD` ... Use this when isolating subagents that need to operate on in-progress work. Inside a worktree, `"head"` resolves to that worktree's `HEAD`, not the main checkout's." No stowed or repo settings file sets `worktree` today. |
| PostToolUse `additionalContext` | Holds as stated | code.claude.com/docs/en/hooks: context from PostToolUse lands "next to the tool result". Plain stdout reaches Claude only for `UserPromptSubmit`, `UserPromptExpansion`, `SessionStart`, and `PostModelSwitch`. The cap is 10,000 characters. Hooks from settings "also run inside subagents", and the input carries `session_id`, `cwd`, and, inside a subagent, `agent_id`. |
| How the hook learns a task's estimate and start time | Partly specified | The spec says the session writes a task-clock file, but it never says where the file lives (minor m5). |
| `claude --bg` and its flags | Flags hold; behavior differs from the spec | `claude --help` (2.1.296) lists `--bg`, `--model` (accepts `sonnet`), `--effort` (low to max), `--permission-mode`, and `--settings`. code.claude.com/docs/en/agent-view says a `--bg` session moves itself into a new worktree before its first edit (major M2). The same page says it "starts the way a new `claude` session in that directory would", so `defaultMode: "auto"` at stowed `settings.json:11` applies. No pass repo's project settings override it (only healthy-diet and poplar set `defaultMode`). |
| cairn-cms CI triggers and draft PRs | Hold as stated | `test.yml:3-8`, `e2e.yml`, `design.yml`, `scaffold.yml`, and `create-site.yml` run on `push` to `[main, rebuild]` and on `pull_request`. `tool.yml` and `tool-conditions.yml` are path-filtered. `gh pr view 111` gives `isDraft: true` and 7 checks, all `SUCCESS`, so a draft PR runs CI. |
| `ci-green` | Holds | Usage reads `ci-green <sha> --pr <n> [--wait]`, and exit 75 means pending. |
| `gh pr checks` flags | Hold | `--watch` and `--fail-fast` exist; exit 8 means checks pending. |
| `cairn-run-gate` line cites | All accurate | `:5-8`: default wait 540. `:29-34`: light lane at 2G high, 3G max. `:119`: no flag check on the gate string. `:333`: nominal `waited` counting. `:390`: result files deleted after one print. The script's state is "keyed by the gate string and the working directory" (`:5`), and `gate_fingerprint` already exists (`:138`). |
| `gate-tier.mjs:71-76` | Accurate | The component stall comment is at `:72-76`. |
| `scripts/check.sh:44` | Accurate | It runs the pass-execute runners test. |
| Stow links | As the record states | `~/.claude/{skills,agents,docs,workflows,tooling}` and `settings.json` link into `~/.dotfiles/claude/.claude/`. `~/.local/bin/cairn-run-gate` links into `~/.dotfiles/bin/.local/bin/`. Both resolve to the main checkout, never to a dotfiles worktree. |

## Question 1: did each blocker and major close where the record says?

Yes, with two exceptions. Every blocker and major in the three reviews maps to a row in the record,
and each cited spec location carries the fold. The two exceptions:

- X-M1 closed only in part. The fold dropped the review's tree-fingerprint condition on the reprint,
  which opens a new defect (major M1).
- X-B2 closed in the text. Its acceptance probe cannot test the mechanism in the order the rollout
  gives (major M3).

## Question 2: contradictions and rollout order

The rollout has one order defect (major M3). Two cross-section mismatches are minor (m1, m2).
Deletions create no dangling-link window: the stowed links are whole-directory links into the main
checkout, and step 1 lands as one merge.

## Question 3: mechanisms stated from memory

Every mechanism the fold record cites probed true (see Probes). The fold missed two behaviors of
mechanisms it adopted: `--bg` worktree relocation (major M2) and the reprint's lost tree condition
(major M1).

## Question 4: changes beyond defects and rulings 11 to 14

- **`live-account` flag replacing the `unattended` class.** A proven defect forces it, so it is fine.
  Under ruling 4 and Execution 1 every run is unattended, so the approved class would put every pass
  under three-lens plan review. The flag keeps exactly the one unique catch the class existed for,
  real Cloudflare and GitHub accounts (catch ledger S2 item 3 and the S2 verdict).
- **`visual-verifier` at close.** Ruling 2 forces it, so it is fine. The step has a REAL, U catch
  record (catch ledger S6 item 4), and the global `CLAUDE.md` render-read rule still stands. Dropping
  it would break the design's own zero-based test. It is a new reviewer seat, so the Departures
  section needs a one-line fix (minor m1).
- **Per-task risk classes.** A proven defect forces it, so it is fine. The approved text contradicted
  itself: it set "one risk class" per pass, yet Execution acted "on `auth-data` tasks". Pass B's Task
  2 is the live case. Taking the highest task class as the pass class is the smallest reconciliation
  that keeps both approved behaviors.
- **The plan verification read by default (Lifecycle 4) and `go-architecture-reader` leaving the
  process.** The approved design was silent on both. Both follow the ledger: the S2 verdict says "Keep
  the verification read", and `go-architecture-reader` has no catch record (ruling 2). Fine; worth one
  line in the PR body so Geoff sees it.

## Question 5: over-folding

No finding at minor or above. Of the 54 added lines, 11 are rulings and the revision note. Most of
the rest closes a blocker or major with a cited defect: the full-suite home, the draft PR and its
watcher, the pair base and merge-back, the lane rule, the inventory, and the success-test window. The
`defer` exit now carries two exclusions and applies only in cairn-cms and aksailingclub-org. Cutting
it is optional, but the approved design named it, so it stays.

## Majors

### M1. The persistent reprint has no tree condition, so a rerun after an edit reprints the stale result

- **Where:** spec `:136-137`.
- **Defect:** "A finished result stays until a new run starts ... `--fresh` forces a rerun." The run
  state is keyed by gate string and working directory (`cairn-run-gate:5`). As written, the same call
  made after a fix edit reprints the previous run's result until someone passes `--fresh`. That
  reprint can be a false green on a broken tree. X-M1's fold keyed the reprint "by tree fingerprint",
  and the spec dropped that condition.
- **Fix:** add one clause. A finished result reprints only while the tree fingerprint matches the
  run's start fingerprint (`gate_fingerprint`, `cairn-run-gate:138`). A changed tree starts a new
  run, and `--fresh` reruns the same tree after a flake.

### M2. A `claude --bg` session moves itself into a new worktree unless launched in a linked worktree

- **Where:** spec `:110-114`.
- **Defect:** code.claude.com/docs/en/agent-view, "How file edits are isolated": a session started
  with `claude --bg` "starts in your working directory. Before editing files, Claude moves the session
  into an isolated git worktree under `.claude/worktrees/`". It skips this step when "the session is
  already inside a linked git worktree". Pass B's checkout is a linked worktree, so pass B is safe. A
  pass launched from a repo's main checkout, the usual site-repo case, is not. Its commits land on a
  new `worktree-*` branch instead of the pass branch that carries the draft PR. Without
  `baseRef: "head"`, that branch starts from `origin/main`. The new worktree also lacks
  `node_modules`, and only pairs run a setup command (Execution 2).
- **Fix:** state that the pass checkout is a linked worktree on the pass branch. A `--bg` session
  launched there skips its own isolation, and the adapter's setup command runs there once at launch.
  The alternative, `worktree.bgIsolation: "none"`, would change every background session on the
  machine.

### M3. Rollout step 1 runs on, and gates on, machinery that goes live only at its merge

- **Where:** spec `:184-195`, with `:115-119` and `:178`.
- **Defect:** step 1 works "on a branch in a worktree" so that edits stay off the live tree. The
  rollout preamble gives that reason, and it is right. The consequence is that
  `~/.claude/settings.json` and `~/.local/bin/cairn-run-gate` keep resolving to the main checkout
  until the merge (Probes, stow links). Three statements then fail.
  - "The cutover runs on the new process from its first task." A pair spawned during step 1 gets a
    `"fresh"` base, so it branches from `origin/main` without step 1's earlier commits: the X-B2
    defect, during the cutover itself.
  - The clock-stop hook is not installed during step 1, so the cutover runs with no clock stop.
  - Done criterion: "one live pair probe ran `cairn-run-gate` in its worktree" before the merge. That
    probe runs the old settings, with no `baseRef`, and the old `cairn-run-gate`. It cannot prove
    either change it exists to prove. R-B2's additive-first order would have avoided this; the fold
    refused it for the deletion windows only.
- **Fix:** state that step 1 runs serially, with no pairs and no clock stop. Move the pair probe to the
  first act after the merge, on the merged `main`, with `pre-lean-process` as the rollback. The
  alternative is to run the probe before the merge from a session launched with
  `--settings <worktree>/claude/.claude/settings.json` and `PATH` led by the worktree's
  `bin/.local/bin`.

## Minors

### m1. Departures still says reviewer subagents run in "two places only"

- **Where:** spec `:65-68` against `:99`.
- **Defect:** the close now also dispatches `visual-verifier`, a fresh-context grader.
- **Fix:** count the visual read inside the close's whole-branch ask, or say "three places".

### m2. The score's shape and the clock's end point are each stated twice and differently

- **Where:** spec `:101` ("a one-line score") against `:220` ("carries the table's five rows"), and
  `:215` ("PR-ready", never defined).
- **Fix:** make Close say the score carries the five rows, and define PR-ready as the close complete
  with the full-suite home green. C-M3 proposed exactly that.

### m3. "Elsewhere `gh pr checks`" reads as covering repos with no PR CI

- **Where:** spec `:127-129`.
- **Defect:** in the four repos whose full-suite home is local (ruling 11), a draft PR has no checks
  to watch. There `gh pr checks --watch` reports none and exits nonzero, which Execution 4 would read
  as a red. This was not probed on a no-CI repo, but the reading defect stands on its own.
- **Fix:** "elsewhere with PR CI (aksailingclub-org) ...; a repo whose full-suite home is local has no
  watch command."

### m4. Ruling 11's ROADMAP filing has no rollout home

- **Where:** spec `:48-49` against `:190-204`.
- **Fix:** add "file the PR test CI items on each named repo's ROADMAP" to step 1 or step 3.

### m5. The task-clock file has no location rule, and the hook is machine-wide

- **Where:** spec `:132-135` and `:178`.
- **Defect:** the hook goes into the stowed global `settings.json`, so it fires in every session and
  subagent on the machine. A fixed path would push stop lines into Geoff's other sessions. A file in
  the work tree would change `cairn-run-gate`'s tree fingerprint (`git add -A` on a scratch index,
  `:122-125`) at every task start.
- **Fix:** key the file by the executing session's id or by the checkout's git dir. The id is
  `$CLAUDE_CODE_SESSION_ID` in the session's shell and `session_id` in the hook's input. The git dir
  is resolved from the hook's `cwd`. Never use a fixed path or the work tree.
