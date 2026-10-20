# Infra sweep, passes A-core and B

> **For agentic workers:** seven tasks in two passes, run per task with the Agent tool (not a
> `pass-execute` runner, whose defects pass B fixes). Each task is a chain: `cairn-implementer`
> on `sonnet`, then `diff-reviewer`, then the gate inside the chain. Every implementer dispatch
> carries the dispatch overrides below. **The conductor never reads a diff, a test log, or a gate
> transcript.** One re-dispatch on `fix`; a second `fix` is the conductor's decision. Tasks state
> outcomes and acceptance, never code.

**Date:** 2026-09-28. **Goal:** land the guard's core and fix every infra defect the
style-guide-sync run would hit, so that plan runs on corrected infra (Geoff, 2026-09-28: "let's
actually run that first, and then implement this plan using the improved and correct infra").

**Spec:** `~/.dotfiles/docs/superpowers/specs/2026-09-28-claude-infra-sweep-design.md` (rulings
S1 to S7; sections "The ratchet baseline", "Pass A-core", "Pass B"). Task ids AC1 to AC3 and B1
to B4 are the spec's; each task's outcomes are that section's, in full. Evidence: the audit at
`~/.dotfiles/claude/.claude/docs/record/2026-09-28-claude-infra-audit.md`; reviews and folds under
`~/.dotfiles/docs/superpowers/research/2026-09-28-infra-*`.

**Pass class:** `engine-logic` for AC1, AC2, AC3, B1, B2 (test-first with fixtures); `sweep` for
B3 and B4 (grep post-conditions, existing tests stay green, no register chain). Two cells are
overridden for this repo: the per-task gate is always `check.sh` (dotfiles has no type check or
component project), and B4's reviewer is upshifted to Opus for the `0a2e391` repair.

**Token ceiling:** 5M (A-core 2M, B 3M). **Checkpoints:** after AC3 (A-core merge) and after B4
(B merge); STATUS written at each, at any split, and before any question. At 80% (4M) finish the
task in flight, write STATUS, ask one combined question at the next boundary.

**Models:** implementer `cairn-implementer` (`sonnet`; its frontmatter sets effort `high`, and
effort has no per-dispatch override); upshift AC1 and B4 to `model: opus`. Reviewer
`diff-reviewer` on `claude-opus-5-5`, except B3 on `sonnet` per the `sweep` row. Close:
`code-simplifier:code-simplifier` over B's JavaScript only (S5). Conductor `claude-opus-5-5` at
`medium`, **session working directory `~/.dotfiles`**.

**Owner time:** none planned. One optional batched question at the A-core boundary (the `GA-nn`
triage); a ruling question stops only its task.

## Dispatch overrides (every dispatch through the B merge)

Every dispatch names `<wt>`, the absolute worktree path, and works only there: implementers,
each `diff-reviewer` read (per task, the merge read, and the B3 and B4 grep post-conditions, all
run against `<wt>`, never `~/.dotfiles`), and the B-close `code-simplifier`, whose changes an
implementer then commits under override 1's gate. Items 1 to 6 below apply to implementers.

Agent definitions load from `~/.claude/agents`, a symlink into `~/.dotfiles` `main`, so B3's
edits go live only at the B merge. Until then each dispatch carries this list, stated as
overriding the agent file:

1. **Gate:** `cd <wt> && CAIRN_GATE_LANE=light cairn-run-gate 'bash <wt>/scripts/check.sh'`, with
   `<wt>` the absolute worktree path. Re-issue the identical string on exit 75 until it prints
   `gate exit:`. This replaces the file's definition of done: no npm scripts, no `check:facts`.
2. Stage the task's paths (`git add <paths>`) before the gate; ruff and `bash -n` read `git
   ls-files` and skip untracked files.
3. Tests live under `<wt>/tests/`, not `src/tests/`.
4. Commits carry the model-named trailer the harness's attribution reminder gives, never the
   generic footer.
5. Do not read or write agent memory.
6. `git commit --no-verify` is forbidden; a hook failure is a task failure, reported.

## Global constraints

- **The in-flight probe.** (1) No live gate: no `${TMPDIR:-/tmp}/cairn-gate-$(id -u)/*/pid` whose
  pid passes `kill -0`, and `systemd-inhibit --list` shows no `cairn-gate` hold. (2) No live
  agent in another session: `find ~/.claude/projects -path '*/subagents/*' -name 'agent-*.jsonl'
  -mmin -25 -not -path "*/$CLAUDE_CODE_SESSION_ID/*"` prints nothing. (3) `git -C ~/.dotfiles
  status --porcelain` is empty. (4) `pgrep -f` with a bracket pattern that cannot match its own
  shell (`'/Projects/.worktrees/[d]otfiles-infra-a'`, `-b` for pass B) is empty. Before a pass, (3) and (4) block and (1)
  and (2) are recorded; before a merge, all four block. On a positive, wait and re-probe; one
  still positive after an hour goes into STATUS as the question. `0a2e391` is why.
- **Mixed-version guarantee.** A run the probe misses survives a merge: an in-flight workflow keeps
  the runner text it launched with and picks up new agent definitions and the new
  `cairn-run-gate` on its next call. B1 rejects no plan for a missing `reducedGate`, B3's agents
  run whatever gate the dispatch names, and B2's script reads a state directory the old script
  wrote.
- Worktrees live outside `~/.dotfiles`: A-core at `~/Projects/.worktrees/dotfiles-infra-a`
  (branch `infra-sweep-a`), B at `~/Projects/.worktrees/dotfiles-infra-b` (branch
  `infra-sweep-b`, created from `main` after A-core merges).
- **Merge integration**, at each boundary: (1) the probe; (2) an implementer merges `main` into
  the pass branch in the worktree, keeps every main-side line the task outcomes do not replace,
  lists each resolved hunk, and runs the gate (skipped when `main` has not moved); (3)
  `diff-reviewer` reads that merge commit against "no main-side line lost"; (4) the probe again,
  then the conductor runs `git merge --no-ff --no-commit` in `~/.dotfiles`, conflict-free by
  construction (if `main` moved again, `git merge --abort` and back to step 2); (5) on that
  uncommitted merge tree, `CAIRN_GATE_LANE=light cairn-run-gate 'bash
  ~/.dotfiles/scripts/check.sh'` and `claude-tooling-sync verify`. Green: `git commit` (which runs
  the ratchet hook on the merge) and record the SHA. Red: `git merge --abort`, never a revert,
  since a reverted merge cannot be re-merged; the red cause goes to an implementer on the pass
  branch, then back to step 2.
- **Boundary records.** At each boundary, the merge-integration implementer (step 2) writes the
  pass's `docs/HISTORY.md` and `docs/STATUS.md` entries on the pass branch, so they merge with it.
- **Rollback** is plain `git revert -m 1 <merge sha>`, never `--no-commit` then `git commit`
  (a plain commit runs the ratchet hook). Reverting A-core after B merged requires reverting B's
  merge first; STATUS records both SHAs and the order.
- Every commit passes the per-commit ratchet hook once AC1 lands. A task that fixes a baselined
  finding removes its entries in the same commit; a task that retires text appends its phrase in
  that commit (RC3). A retired phrase has **no hit** when the scanner reports zero matches and
  the baseline holds no entry with that phrase as its fingerprint.
- Fixtures inject home, projects, and memory roots; no fixture reads outside its root.
- Python follows `python-conventions` (PEP 257, the ruff D config `check.sh` runs); JavaScript
  comments follow TSDoc and the no-em-dash rule; commits are path-limited.
- The chain W dotfiles worktree of the style-guide-sync plan must not exist during this plan.

## Review focus

1. **The pre-commit hook losing gitleaks' fail-closed exit** when the ratchet step is added
   before `exec gitleaks`. Table rows H1 to H4.
2. **The ratchet's own bootstrap commit** failing its own rule. Row R12; AC1 registers no check
   id whose tool is absent (row R9).
3. **A worktree run resolving through `~/.claude` symlinks to `main`** and passing falsely. Row
   F1.
4. **B1's reduced-gate change repealing the 2026-09-09 ruling** by rendering the full gate on a
   comment-only round. B1 test: a named gate with no `reducedGate` renders the class default;
   chain W renders its explicit `reducedGate`.
5. **B4's `0a2e391` repair dropping deliberate slimming, or reverting a later ruling.** B4's
   report labels each hunk, and `diff-reviewer` checks the labels against the diff.

## Failure-state table (AC1 to AC3)

One passing fixture per row. Tools: **hook** is the real `scripts/githooks/pre-commit` run in a
temporary repo; **ratchet** is the shared module as `check.sh` runs it; **sync** is
`claude-tooling-sync`; **refs** is `scripts/check-claude-refs.py`. Report lines name the check id,
the file, and the fingerprint unless stated.

| Row | State | Tool | Exit | Report line |
|---|---|---|---|---|
| R1 | staged entry added under a registered id | hook | 1 | new entry under the id |
| R2 | staged entry added under an emptied registered id | hook | 1 | new entry under the id |
| R3 | new id registered with its entries in one commit | hook | 0 | none |
| R4 | staged entry under a retired id | hook | 1 | retired id admits no entries |
| R5 | registry id removed | hook | 1 | registry is append-only |
| R6 | re-key across a heavily edited move, count unchanged | hook | 0 | none |
| R7 | overlap count rises | hook | 1 | the pair and both counts |
| R8 | removals and a falling count | hook | 0 | none |
| R9 | registered id no tool implements | ratchet | 2 | the id |
| R10 | entry no violation matches | ratchet | 1 | "remove this baseline entry" |
| R11 | violation no entry matches | ratchet | 1 | the violation |
| R12 | HEAD with no baseline, seeded file staged | hook | 0 | none |
| R13 | baseline absent | ratchet | 2 | config error |
| R14 | baseline present and empty | ratchet | 0 | none |
| R15 | malformed: bad JSON; missing field; unregistered id; bad finding-id format (one fixture each) | ratchet | 2 | names the entry |
| R16 | many-bad run | ratchet | 1 | every violation, grouped, a count per check |
| R17 | working-tree growth against HEAD | ratchet | 1 | the grown entry |
| H1 | staged secret, clean baseline | hook | 1 | gitleaks finding |
| H2 | staged ratchet violation | hook | 1 | the ratchet line; gitleaks not reached |
| H3 | `gitleaks` absent from `PATH` | hook | 1 | gitleaks missing |
| H4 | unrelated staged file, malformed working-tree baseline | hook | 0 | none (fast path) |
| M1 | worktree copy run with `HOME` at a fixture home holding no module | ratchet | 0 | none |
| M2 | any run that reads outside the fixture root | all | fixture fails | the path read |
| S1 | manifest absent | sync | 2 | config error |
| S2 | manifest malformed | sync | 2 | names the entry |
| S3 | personal skill named as a fixture project's `.claude/skills/<name>` | sync `verify` | 1 | the pair |
| S4 | `skills/<dir>` with a `LICENSE` and no manifest entry | sync `lint --root` | 1 | the dir |
| S5 | unknown argument | sync | 2 | usage |
| F1 | doc deleted only in the fixture tree, cited as `~/.claude/docs/...` | refs | 1 | the dead path |
| F2 | `~/.local/bin/<x>` cited, present in the fixture's `bin/.local/bin` | refs | 0 | none |
| F3 | retired phrase in an authored file | refs | 1 | the phrase and file |
| F4 | retired phrase on a `retired-ok` line | refs | 0 | none |
| F5 | phrase list absent | refs | 2 | config error |
| F6 | phrase list with only comments | refs | 2 | vacuous list |
| F7 | vendored skill with a retired phrase and a dead path | refs | 1 | the phrase only |
| F8 | retired phrase under `skills/synced/`, dead path under `docs/record/` | refs | 0 | none |

---

## Pre-bake (conductor, before AC1)

- Commit this plan; point dotfiles `docs/STATUS.md` at it, replacing the stale next action and
  dropping the owed aksailingclub-org pointer line (spec, Pass A-core). Append the erratum to the
  audit record: its section 1 line "code-simplifier per commit (global CLAUDE.md) against once per
  pass" reads "reverted by `0a2e391`", and the audit missed the superpowers-yield loss.
- **P1.** One `haiku` pre-flight lists every checkable claim in AC1 to AC3 (paths, line numbers,
  the hook's last line, `check.sh`'s steps, `claude-tooling-sync`'s subcommands, the manifest
  path, the `ship` collisions) and checks each at HEAD. Amend, then run the probe and dispatch.

## Pass A-core

**AC1. The ratchet.** Class `engine-logic`, `model: opus`. Files:
`claude/.claude/tooling/ratchet-baseline.json`, one shared Python module both tools import (under
`claude/.claude/tooling/`, located through `Path(__file__).resolve()` of the importing script,
never through `~/.claude`, with `sys.dont_write_bytecode = True` before the import),
`scripts/githooks/pre-commit`, `scripts/check.sh`, fixtures under `tests/`.
Outcomes: the spec's "The ratchet baseline" section in full. The hook's ratchet step takes a fast
path to `exec gitleaks` when the baseline is not staged, reads only the index and HEAD copies,
and runs system `python3` on the standard library alone.
Acceptance: rows R1 to R17, H1 to H4, M1, M2 pass; after the hook, `check.sh`, and `verify` have
run, no `__pycache__` exists under `claude/` or `bin/`; the gate is green.

**AC2. `claude-tooling-sync`.** Class `engine-logic`. Files: `bin/.local/bin/claude-tooling-sync`,
`claude/.claude/tooling/` (manifest), `claude/.claude/skills/ship/` renamed `go-ship/`,
`scripts/check.sh`, fixtures.
Outcomes: the spec's AC2 (`lint --root`, `verify` with the collision check reading the injected
projects root, the unmanifested third-party check, `go-ship` with
`disable-model-invocation: true`, `vhs-cli-demos` manifested). Closes PS-01, CS-9, AW-16.
Acceptance: rows S1 to S5 pass; `lint --root <wt>` green; the gate is green.

**AC3. `scripts/check-claude-refs.py`, self mode.** Class `engine-logic`. Files: the script,
`claude/.claude/tooling/retired-phrases.txt`, `scripts/check.sh`, baseline entries, fixtures.
Outcomes: the spec's AC3 (scan scope, self-mode path rewriting, dead-reference and
retired-phrase checks, list semantics, seeded phrases each with a witness `file:line`).
Acceptance: rows F1 to F8 pass; the spec's A-core acceptance (seeded-count table with a label
column, per-label summary, `GA-nn` summary). Labels are checked: DC-01, DC-03, DC-04, DC-30, and
AW-07 each seed at least one entry labelled `B`; no audit id in the spec's B1 to B4 tables
carries any other label; every seeded id A-core fixes carries `A-core`.

**A-core boundary.** Merge integration; record the SHA. `docs/HISTORY.md` entry, including one
line on the `ship` rename's effect: `/ship` in ecxc-ski and both aksailingclub repos now resolves
to the project skill (which pushes, and in ecxc-ski deploys), and in poplar "ship it" no longer
auto-fires. STATUS carries any `GA-nn` entry with no plausible owning pass as one batched
question that does not block B.

## Pass B

**P2 (before B1).** One `haiku` pre-flight on `main` after the A-core merge checks every claim in
B1 to B4 (line numbers in the runners, `docs-page-chain.js`, the implementer files, `CLAUDE.md`,
`commit-and-pr.md`, `model-economy.md`, and the `skills/go-ship/` path). Amend, then run the probe
and dispatch.

**B1. Runners.** Class `engine-logic`. Files and outcomes: the spec's B1 table and test
assertions, including the style-guide-sync fixture from "Pass B acceptance" (chains R and W in
one invocation, W with `classifier: false` and `reducedGate: "bash scripts/check.sh"`) inside
B1's harness. The harness runs the runner body with `agent`, `parallel`, and `log` stubbed; the
probe-count assertions depend on it.
Acceptance: all B1 test assertions pass; Review focus 4.

**B2. Gate tool.** Class `engine-logic`. Files: the spec's B2, plus `scripts/check.sh`,
`claude/.claude/agents/site-implementer.md` (the vanished clause near `:101`), and
`claude/.claude/workflows/pass-execute.js` (near `:336`), which B1 also edits, so B2 runs after
B1's commit. Outcomes:
the spec's B2; the poll interval and grace period are injectable through the environment.
Acceptance: B2's test assertions, run by `check.sh` with short injected sleeps; a state directory
written by the old script (no vanish counter; a live pid, a finished run, a dead pid without
status) resolves correctly; no runner prompt or implementer file carries a vanished clause.

**B3. Agent definitions.** Class `sweep`, reviewer `sonnet`. Files and outcomes: the spec's B3
table; AW-19 adds a fallback: a dispatch that names no gate runs the repo's documented gate from
its `CLAUDE.md`. Acceptance: the spec's B3 mechanical acceptance; each table row carries a grep
post-condition in the report, and `diff-reviewer` runs it. The dispatch overrides stay through
the B merge.

**B4. Global CLAUDE.md, pass skills, the spent workflow.** Class `sweep`, `model: opus`,
reviewer `claude-opus-5-5`. Files and outcomes: the spec's B4 table and retired phrases. For the
`0a2e391` repair, before restoring a region the implementer runs `git log -L` over it from
`0a2e391` to HEAD, and labels each hunk "restored ruling" (with its source commit), "kept
slimming", or "superseded after `0a2e391` (`<sha>`)".
Acceptance: the hunk list; `diff-reviewer` confirms no line added by a commit after `0a2e391`
leaves in B4's diff; the retired phrases have no hit; each table row's grep post-condition in the
report, run by `diff-reviewer`; `docs/HISTORY.md` carries the incident.

**B close.**
1. `code-simplifier:code-simplifier` over B1's runners and `.mjs` tests and B2's
   `docs-page-chain.js`; refinements applied; gate green.
2. The spec's "Pass B acceptance": a baseline query returns zero entries labelled `A-core` or `B`.
3. Merge integration; record the SHA and the rollback order.
4. dotfiles STATUS and HISTORY; score both budgets against 5M.
5. STATUS names the next action: re-baseline the style-guide-sync plan (apply the spec's ten
   amendments, replace its P0 and boundary in-flight wording with this plan's probe, run its
   verification read, then execute). The dispatch overrides lapse here.
