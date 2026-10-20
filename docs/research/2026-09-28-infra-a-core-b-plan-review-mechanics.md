# Plan review: infra sweep A-core and B, mechanics and feasibility lens

Plan: `docs/superpowers/plans/2026-09-28-infra-sweep-a-core-b.md` at dotfiles `62c5e6d`.
Reviewer: Opus 5.5, high effort. Lens: whether the tools can do what the plan asks.

**Counts:** 0 blockers, 3 majors, 7 minors.

The plan is executable once the three majors are folded. None needs a spec change, and each
fold is a line or two in the plan.

## Verified sound (no finding)

- **`cairn-run-gate` outside a cairn repo.** The script contains nothing specific to cairn. It
  keys state on `$PWD` plus the gate string and runs `bash -c "$gate"`. Run empirically from a
  scratch clone of dotfiles with `CAIRN_GATE_LANE=light`, it started the gate, printed
  `gate exit:`, and every `check.sh` step ran inside the light lane's 3G cap. The only red step
  was tellgrader's `posthook` tests, and my clone caused it: `posthook.go:73` skips every path
  under `/tmp/`, and my scratch directory is under `/tmp`. A worktree at
  `~/Projects/.worktrees/` is not affected.
- **`check.sh` from a worktree.** `check.sh:12` runs `cd "$(dirname "$0")/.."`. Every step uses a
  repo-relative path or `git ls-files`, and none of them depends on stow.
- **Hooks in a worktree.** `core.hooksPath` is the relative value `scripts/githooks`, set in the
  common `.git/config`. I tested this empirically in a scratch repo with a worktree. The
  worktree ran its own working-tree copy of the hook, uncommitted edits included, and the main
  checkout ran its own copy. AC1's hook is therefore live in the A worktree as soon as it is
  written, and live on `main` from the moment of the merge.
- **Shared module import.** `~/.local/bin/claude-tooling-sync` is a per-file symlink into
  `~/.dotfiles/bin/.local/bin/`, and the script is Python. `Path(__file__).resolve()` therefore
  reaches the tree that holds the script: the worktree when the script is invoked by its
  repo-relative path, and `~/.dotfiles` (main) in verify mode. The same holds for
  `scripts/check-claude-refs.py` via `parents[1]`. `~/.claude/tooling` is a folded directory
  symlink, so a new module under it needs no restow. No new file lands in `bin/.local/bin`, so
  no `stow -R bin` is needed either.
- **AC2's live state.** `claude-tooling-sync verify` exits 0 today. The collision scan finds
  exactly the three `ship` collisions the spec names. The only `LICENSE*` skills are
  `vale-setup` (already manifested) and `vhs-cli-demos` (the CS-9 fix).
- **B1 harness.** `pass-execute-chains.js` ends in `return main();`, where `main` is async and
  reads `args`, `agent`, `parallel`, and `log`. An `AsyncFunction` built over the body with those
  names stubbed is feasible.
- **Seats.** The `cairn-implementer` frontmatter says "pass model:opus to upshift a task with
  novel correctness-critical logic", and `model-economy.md:17` sets Sonnet at `high`. AC1 fits
  that description. B4 on Opus is a judgment upshift the table neither requires nor forbids,
  and it is defensible. Effort comes from frontmatter only. The docs say "there is no
  per-invocation effort parameter" (code.claude.com/docs/en/sub-agents), so the plan's
  "`high`" is delivered by `cairn-implementer.md`'s `effort: high`, and nothing more is needed.
  The docs resolve the model in this order: per-invocation `model`, then frontmatter, then
  `CLAUDE_CODE_SUBAGENT_MODEL`. The `diff-reviewer` frontmatter pin (`claude-opus-5-5`) holds
  when the dispatch passes no model or passes `opus`.
- **Rollback.** Tested empirically: neither `git merge --no-ff` nor `git revert -m 1` runs
  `pre-commit`. The ratchet cannot block a rollback, and it cannot block the merge commit.

## Majors

### M1. The relative gate string can run `main`'s gate and pass falsely

`plan:6`, `plan:24`. The gate is `CAIRN_GATE_LANE=light cairn-run-gate 'bash scripts/check.sh'`.
A subagent's Bash cwd resets to the session cwd between calls, and the plan never names that
cwd. If an implementer or `diff-reviewer` issues the gate without first changing into the
worktree, one of two things happens:

- From a conductor session in `~/.dotfiles`, the gate runs `main`'s `check.sh` against `main`
  and reports green. This is Review focus 3's false pass, at the gate level.
- From a conductor session in cairn-cms, the gate fails with file-not-found.

`cairn-run-gate` keys on `$PWD`, so a re-issue from a different cwd also starts a second run
instead of reattaching.

**Fold:** name the gate by absolute path, for example
`CAIRN_GATE_LANE=light cairn-run-gate 'bash ~/Projects/.worktrees/dotfiles-infra-a/scripts/check.sh'`
and the same for `-infra-b`. `check.sh` changes into its own root, so this works from any cwd.
Also state that the conductor session runs from `~/.dotfiles`.

### M2. B3's "from this commit, dispatches may drop the override" is false until B merges

`plan:125-126`. Dispatches resolve `cairn-implementer` from `~/.claude/agents`, which is a
symlink to `~/.dotfiles/claude/.claude/agents`, the `main` checkout. B3 commits to
`infra-sweep-b` in the worktree, so the live definition keeps the npm definition-of-done list
through B4.

Hot reload does not help here. The docs say "Claude Code watches `~/.claude/agents/` ... the
next delegation uses the updated definition". The watcher sees `main`, and the edit is not on
`main` yet.

**Fold:** keep the override on every dispatch through B4 and the B close. It may drop only after
the B merge, which is also when the new definition becomes live without a restart.

### M3. The override covers only the definition of done, but four more cairn clauses bind

`plan:5-7`. `cairn-implementer.md` also carries these clauses, and each one conflicts with this
plan:

- **The hardcoded footer:** "the repo's standard `Co-Authored-By: Claude <noreply@anthropic.com>`
  footer". This conflicts with `plan:53-54`, which requires the model-named trailer.
- **The facts container** ("runs `npm run check:facts`").
- **The test location** ("Tests live at `src/tests/...`").
- **`memory: project`.** Per the docs, this is `.claude/agent-memory/<name>/` under the session's
  project, and the prompt tells the agent to write it. From a `~/.dotfiles` session, the
  implementer writes to `~/.dotfiles/.claude/agent-memory/cairn-implementer/`, which is
  untracked and not gitignored. The plan's own precondition at `plan:39-41`, "warm uncommitted
  changes on dotfiles main stop the pass", then halts pass B. `gitleaks dir .` also scans the
  new file. From a cairn-cms session, the implementer writes dotfiles notes into cairn-cms's
  memory instead.

`general-purpose` on Sonnet is the worse seat. It drops the test mandate, the report shape, the
pre-flight checklist, and the gate protocol. It also holds the Agent tool, so it can
re-delegate.

**Fold:** keep `cairn-implementer`, and make the override a named list: the gate (absolute
path), the model-named trailer, no facts container, tests under `tests/`, and "do not read or
write agent memory". Carry the list until the B merge (M2).

## Minors

### m1. The module resolution mechanism is unnamed, and bytecode lands in the stow package

`plan:86-88`. "Resolved from the tree under test" admits `Path.home()/.claude/tooling`. The
current `claude-tooling-sync:27` hardcodes `~/.dotfiles/...`, and that would import `main`'s
module during a worktree lint. Separately, the hook and the `~/.local/bin` invocation run
without `check.sh`'s `PYTHONDONTWRITEBYTECODE`. They would write `__pycache__/` into
`claude/.claude/tooling/`. That directory is gitignored, and the folded symlink keeps it out of
`$HOME`, but it is avoidable noise.

**Fold:** name the mechanism, `Path(__file__).resolve()` plus `sys.dont_write_bytecode = True`
before the import. Add one fixture: the worktree copy imports with `HOME` pointed at a fixture
home that has no module.

### m2. The gate skips new, untracked files

`check-py-comments.sh:13` uses `git ls-files -- '*.py'`, and `check.sh:33` uses `git ls-files`
for `bash -n`. A new module, `check-claude-refs.py`, or a new test is invisible to ruff and
`bash -n` until it is staged. An implementer who runs the gate before committing gets a green
that never looked at the new code.

**Fold:** in the dispatch, say to stage the task's files with `git add <paths>` before the gate.

### m3. The B2 vanish test adds about a minute to every gate

`cairn-run-gate` hardcodes `sleep 5` and a 15-iteration grace loop. A staged dead pid therefore
costs about 20 seconds per call, and the three-vanish assertion needs three or four calls, on
every `check.sh` run from then on.

**Fold:** B2 makes the poll interval and grace injectable through the environment, and the test
sets them to 0 or 1.

### m4. No gate runs on `main` after either merge

`plan:110-111`, `plan:138-139`. A merge commit bypasses `pre-commit` (tested), and `main` can
move between the branch cut and the merge, for example with STATUS commits. Only `verify` runs
after the merge.

**Fold:** add `bash scripts/check.sh` on `main` after each merge, beside `verify`.

### m5. The rollback order is unstated

`plan:44-45`. B edits the baseline, `check.sh`, and the hook's inputs. After B merges,
`git revert -m 1 <A-core merge>` conflicts.

**Fold:** STATUS records that A-core's rollback requires reverting B's merge first. Also say
`git revert -m 1` directly, not `--no-commit` followed by `git commit`, because a plain commit
does run the ratchet hook.

### m6. The no-run-in-flight check has no command

`plan:39-40`, `plan:46-47`, `plan:138`. The journals live at
`~/.claude/projects/*/*/subagents/workflows/wf_*/journal.jsonl`, and there are 250 today. An
mtime alone cannot tell a finished run from a live one.
`~/.claude/docs/unattended-work-guards.md:11-21` already defines the journal-then-transcript
test.

**Fold:** name that test, or `find ... -name journal.jsonl -mmin -30` followed by a check for an
unfinished agent, as the concrete check.

### m7. Hook-level fixtures cover the gitleaks half only

`plan:59-61`. Review focus 1 asserts that a staged secret still fails the hook. Nothing asserts
two other cases at the hook level:

- A ratchet violation fails the hook. A `python3 ...; exec gitleaks` that drops the ratchet's
  exit would pass every unit fixture.
- A missing `gitleaks` still exits 1 once the ratchet step sits before it.

AC1 on Opus reviewed by an Opus `diff-reviewer` also forgoes the model diversity the cairn
CLAUDE.md counts as part of the gate. That makes the hook-level fixtures the stronger
backstop.

**Fold:** add both fixtures, each running the real hook in a temporary repo.
