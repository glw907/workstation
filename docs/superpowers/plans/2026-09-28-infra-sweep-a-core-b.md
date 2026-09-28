# Infra sweep, passes A-core and B

> **For agentic workers:** seven tasks in two passes, run per task with the Agent tool (not a
> `pass-execute` runner, whose defects pass B fixes). Each task is a chain: `cairn-implementer`
> on `sonnet` at effort `high`, then `diff-reviewer` on `claude-opus-5-5`, then the gate inside
> the chain. Every implementer dispatch names its gate as `bash scripts/check.sh` and says this
> overrides the definition of done in its agent file (the npm list), until B3 lands. **The
> conductor never reads a diff, a test log, or a gate transcript.** One re-dispatch on `fix`; a
> second `fix` is the conductor's decision. Tasks state outcomes and acceptance, never code.

**Date:** 2026-09-28. **Goal:** land the guard's core and fix every infra defect the
style-guide-sync run would hit, so that plan runs on corrected infra (Geoff, 2026-09-28: "let's
actually run that first, and then implement this plan using the improved and correct infra").

**Spec:** `~/.dotfiles/docs/superpowers/specs/2026-09-28-claude-infra-sweep-design.md` (rulings
S1 to S7; sections "The ratchet baseline", "Pass A-core", "Pass B"). Task ids AC1 to AC3 and B1
to B4 are the spec's; each task's outcomes are that section's, in full. Evidence: the audit at
`~/.dotfiles/claude/.claude/docs/record/2026-09-28-claude-infra-audit.md`; review and folds under
`~/.dotfiles/docs/superpowers/research/2026-09-28-infra-sweep-*`.

**Pass class:** `engine-logic` for AC1, AC2, AC3, B1, B2 (test-first with fixtures); `docs` for
B3 and B4, which take mechanical acceptance (retired phrases, grep post-conditions) and
`diff-reviewer`, not the register chain. Per-task gate `bash scripts/check.sh` on the light lane
(`CAIRN_GATE_LANE=light cairn-run-gate 'bash scripts/check.sh'`).

**Token ceiling:** 5M (A-core 2M, B 3M). **Checkpoints:** after AC3 (A-core merge) and after B4
(B merge); STATUS written at each, at any split, and before any question. At 80% (4M) finish the
task in flight, write STATUS, ask one combined question at the next boundary.

**Models:** implementer `cairn-implementer` (`sonnet`, `high`); upshift AC1 to `model: opus`,
since the ratchet's growth, re-key, and bootstrap rules are correctness-critical and novel.
Reviewer `diff-reviewer` (`claude-opus-5-5`). Close: `code-simplifier:code-simplifier` over B's
JavaScript only (S5). Conductor `claude-opus-5-5` at `medium`.

**Owner time:** none planned. Nothing here needs taste; a ruling question stops only its task.

## Global constraints

- One executor per worktree: before each pass, `pgrep -f` on the worktree path, `git status` on
  dotfiles `main`, and no running `pass-execute*` or `docs-page-chain` workflow (journal mtimes).
  Warm uncommitted changes on dotfiles `main` stop the pass. `0a2e391` is why.
- Worktrees live outside `~/.dotfiles`: A-core at `~/Projects/.worktrees/dotfiles-infra-a`
  (branch `infra-sweep-a`), B at `~/Projects/.worktrees/dotfiles-infra-b` (branch
  `infra-sweep-b`, created from `main` after A-core merges). Each merges `--no-ff` to `main`;
  the merge SHA goes in STATUS as the `git revert -m 1` rollback.
- Runner and agent edits go live on merge (stowed symlinks). Merge only when no workflow run is
  in flight.
- Every commit passes the per-commit ratchet hook once AC1 lands. A task that fixes a baselined
  finding removes its entries in the same commit; a task that retires text appends its phrase in
  that commit (RC3).
- Fixtures inject home, projects, and memory roots; no fixture reads outside its root.
- Python follows `python-conventions` (PEP 257, the ruff D config `check.sh` runs); JavaScript
  comments follow TSDoc and the no-em-dash rule; commits are path-limited and carry the harness's
  model-named trailer.
- The chain W dotfiles worktree of the style-guide-sync plan must not exist during this plan.

## Review focus

1. **The pre-commit hook losing gitleaks' fail-closed exit** when the ratchet step is added
   before `exec gitleaks`. AC1 fixture: a staged secret still fails the hook with a clean
   baseline.
2. **The ratchet's own bootstrap commit** failing its own rule. AC1 fixture: a HEAD with no
   baseline admits the seeded file; AC1 registers no check id whose tool is absent.
3. **A worktree run resolving through `~/.claude` symlinks to `main`** and passing falsely. AC3
   fixture: a doc deleted only in the fixture tree fails the dead-reference check.
4. **B1's reduced-gate change repealing the 2026-09-09 ruling** by rendering the full gate on a
   comment-only round. B1 test: a named gate with no `reducedGate` renders the class default.
5. **B4's `0a2e391` repair dropping deliberate slimming** along with restoring rulings. B4's
   report lists each hunk as "restored ruling" or "kept slimming", and `diff-reviewer` checks the
   list against the diff.

---

## Pre-bake (conductor, before AC1)

- Commit this plan; point dotfiles `docs/STATUS.md` at it, replacing the stale next action and
  dropping the owed aksailingclub-org pointer line (spec, Pass A-core). Add the erratum note on
  the audit record the fold owes.
- **P1.** One `haiku` pre-flight lists every checkable claim in AC1 to AC3 (paths, line numbers,
  the hook's last line, `check.sh`'s steps, `claude-tooling-sync`'s subcommands, the manifest
  path, the `ship` collisions) and checks each at HEAD. Amend, then dispatch.

## Pass A-core

**AC1. The ratchet.** Class `engine-logic`, `model: opus`. Files:
`claude/.claude/tooling/ratchet-baseline.json`, one shared Python module both tools import
(decided here: one module, under `claude/.claude/tooling/`, resolved from the tree under test,
not through `~/.claude`), `scripts/githooks/pre-commit`, `scripts/check.sh`, fixtures under
`tests/`.
Outcomes: the spec's "The ratchet baseline" section in full, and AC1's fixture list.
Acceptance: every fixture passes, including Review focus 1 and 2; one failure-state table (state,
tool, exit code, report line) in the task report with one fixture per row; the gate is green.

**AC2. `claude-tooling-sync`.** Class `engine-logic`. Files: `bin/.local/bin/claude-tooling-sync`,
`claude/.claude/tooling/` (manifest), `claude/.claude/skills/ship/` renamed `go-ship/`,
`scripts/check.sh`, fixtures.
Outcomes: the spec's AC2 (`lint --root`, `verify` with the collision check, the unmanifested
third-party check, `go-ship` with `disable-model-invocation: true`, `vhs-cli-demos` manifested,
unknown arguments exit 2). Closes PS-01, CS-9, AW-16.
Acceptance: the spec's AC2 acceptance; `claude-tooling-sync verify` is run by the conductor on
`main` after the merge.

**AC3. `scripts/check-claude-refs.py`, self mode.** Class `engine-logic`. Files: the script,
`claude/.claude/tooling/retired-phrases.txt`, `scripts/check.sh`, baseline entries, fixtures.
Outcomes: the spec's AC3 (scan scope, self-mode path rewriting, dead-reference and
retired-phrase checks, list semantics, seeded phrases each with a witness `file:line`).
Acceptance: the spec's A-core acceptance (seeded-count table, per-pass summary, `GA-nn`
summary); Review focus 3's fixture.

**A-core boundary.** Merge `--no-ff`, record the SHA, run `claude-tooling-sync verify` on
`main`, write STATUS. Verify no `infra-sweep-a` edits are left unmerged.

## Pass B

**B1. Runners.** Class `engine-logic`. Files and outcomes: the spec's B1 table and test
assertions, including the style-guide-sync fixture from "Pass B acceptance" (chains R and W in
one invocation, W with `classifier: false`) inside B1's harness. The harness runs the runner body
with `agent`, `parallel`, and `log` stubbed; the probe-count assertions depend on it.
Acceptance: all B1 test assertions pass; Review focus 4.

**B2. Gate tool.** Class `engine-logic`. Files and outcomes: the spec's B2. Acceptance: B2's test
assertions; no runner prompt or implementer file carries a vanished clause.

**B3. Agent definitions.** Class `docs`. Files and outcomes: the spec's B3 table. Acceptance: the
spec's B3 mechanical acceptance. From this commit, implementer dispatches may drop the
definition-of-done override.

**B4. Global CLAUDE.md, pass skills, the spent workflow.** Class `docs`, `model: opus` for the
`0a2e391` repair (it separates rulings from deliberate slimming). Files and outcomes: the spec's
B4 table and retired phrases. Acceptance: Review focus 5's hunk list; each restored ruling named
with its source commit; the retired phrases have no hit; `docs/HISTORY.md` carries the incident.

**B close.**
1. `code-simplifier:code-simplifier` over B1's runners and `.mjs` tests and B2's
   `docs-page-chain.js`; refinements applied; gate green.
2. The spec's "Pass B acceptance": a baseline query returns zero entries labelled `A-core` or
   `B`.
3. Merge `--no-ff` after the no-run-in-flight check; record the SHA; `claude-tooling-sync
   verify` on `main`.
4. dotfiles STATUS and HISTORY; score both budgets against 5M.
5. STATUS names the next action: re-baseline the style-guide-sync plan (apply the spec's ten
   amendments, run its verification read, then execute).
