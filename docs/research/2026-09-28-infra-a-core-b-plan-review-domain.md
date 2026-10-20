# Plan review, domain-risk lens: infra sweep A-core and B

**Plan:** `docs/superpowers/plans/2026-09-28-infra-sweep-a-core-b.md` at `62c5e6d`. **Lens:** live
workstation infra that every Claude session on this machine loads (runners, agents,
`cairn-run-gate`, the global `CLAUDE.md`, the dotfiles pre-commit hook). Reviewer: Opus 5.5, high
effort, read-only.

**Counts:** 0 blockers, 4 major, 5 minor. No owner fork.

Evidence gathered at HEAD, 2026-09-28:

- A live cairn-cms pass is running now: `vite preview` and `workerd` processes under
  `~/Projects/cairn-cms/.claude/worktrees/theme-identity-a/`. That pass uses the runners, the
  implementer definitions, and `cairn-run-gate` this plan edits.
- `~/.claude/{CLAUDE.md,agents,skills,workflows,docs,tooling}` are whole-directory symlinks into
  the `~/.dotfiles` main working tree, and `~/.local/bin/*` are per-file symlinks. A merge to
  `main` is live the moment `git merge` writes the files.
- `core.hooksPath` is the relative `scripts/githooks`, so each worktree runs its own copy of the
  hook. `scripts/githooks/` holds only `pre-commit`, with no `pre-merge-commit`.
- Six commits touched `claude/.claude/CLAUDE.md` after `0a2e391`: `32d00a6`, `2ad8c21`, `4f1ed96`,
  `68a8af8`, `2d9e562`, `89cbe40`. Two of them landed today, directly on `main`, from other
  sessions.
- The personal `ship` skill is the only personal and project skill-name collision
  (`ecxc-ski`, `aksailingclub-sveltekit`, `aksailingclub-legacy`). No doc, script, or manifest
  names the personal skill by path, so the rename to `go-ship` is complete as scoped.

## Major

### M1. The no-run-in-flight check cannot see runs in other sessions

**Where:** plan:39-40 (one-executor check), plan:46-47 (merge only with no run in flight),
plan:138 (B close step 3).

**Defect:** Each named probe misses a run in another session.

- `pgrep -f <worktree path>` only matches processes whose command line names the dotfiles worktree.
  The theme-identity pass that is running now lives in a cairn-cms worktree and would not match.
- "Journal mtimes" names no path and no freshness window. `claude-wf-guard:19-21` records that
  `journal.jsonl` writes only when an agent completes, so a workflow in a long step reads as
  idle.
- Agent-tool chains write no workflow journal at all. That covers this plan's own execution mode
  and every pass under six tasks, yet those chains still dispatch `cairn-implementer` and call
  `cairn-run-gate` between tasks.

The spec's rollback (`git revert -m 1`) is sound. The detection that gates the merge is not.

**Proposed fold:** Replace the prose check with one concrete probe, run before each pass and again
immediately before each merge.

1. **Live gates.** Any `/tmp/cairn-gate-$(id -u)/*/pid` whose pid is alive (`kill -0`), plus
   `systemd-inhibit --list | grep cairn-gate`.
2. **Live agents.** Any `~/.claude/projects/*/*/subagents/**/agent-*.jsonl` modified within about
   25 minutes that does not belong to this session. This covers workflows and Agent-tool chains
   alike.
3. **Clean main.** `git -C ~/.dotfiles status --porcelain` is empty.

On a positive probe, wait and re-probe; do not ask Geoff. Also state in the plan the
mixed-version guarantee that makes a missed run survivable. An in-flight workflow keeps the runner
text it launched with, but it picks up new agent definitions and a new `cairn-run-gate` on its
next call. B1 already requires "no plan is rejected for a missing `reducedGate`". B2 should add
one fixture: a state directory written by the old script, with no vanish counter and a live or
finished run, resolves correctly under the new script.

The style-guide-sync plan's P0 and its boundary step 2 carry the same vague wording. Add the
probe to amendment 10's pre-flight as well.

### M2. The merge into live `main` has no integration step, no conflict owner, and no gate

**Where:** plan:44-45, plan:110-111 (A-core boundary), plan:138-139 (B close).

**Defect:** Other sessions commit to dotfiles `main` several times a day, and the global
`CLAUDE.md` is the most-edited file (six commits since `0a2e391`, two today). B4 rewrites that
file on a branch, so its `--no-ff` merge can conflict. The plan has four gaps here:

- **No conflict owner.** The plan does not say who resolves a conflict, and the thin conductor
  may not read the diff.
- **No hook on clean merges.** A clean `git merge` does not run `pre-commit`: git runs
  `pre-merge-commit`, and this repo has none. Neither the ratchet nor gitleaks sees the merge
  commit.
- **No gate on merged `main`.** After the merge the plan runs only `claude-tooling-sync verify`,
  never `bash scripts/check.sh`.
- **Main goes red silently.** A main-side commit made during the pass can add a dead reference or
  a retired phrase. It can also fix a baselined item, and the stale entry then fails the gate. In
  every case, merged `main` goes red, and the next unrelated session to run the repo gate finds
  it.

**Proposed fold:**

1. At each boundary, one implementer dispatch merges `main` into the pass branch inside the
   worktree. It resolves conflicts and keeps every main-side ruling, lists each resolved hunk,
   and runs `bash scripts/check.sh`. `diff-reviewer` then reads the merge commit against "no
   main-side line lost."
2. The `--no-ff` merge into `~/.dotfiles` is then conflict-free by construction.
3. Run `bash scripts/check.sh` on `main` after the merge, alongside `claude-tooling-sync verify`.
4. Optionally, AC1 adds `scripts/githooks/pre-merge-commit`, which execs `pre-commit`. This is
   git's own sample idiom, and it closes the hook bypass on every future `--no-ff` landing,
   including the style-guide-sync W merges.

### M3. B4's `0a2e391` repair ignores the six later edits to the same file

**Where:** plan:128-131, spec B4 row "`0a2e391` repair" (spec:392).

**Defect:** The repair diffs `a7dd5ad` against `0a2e391`, then restores lost rulings into HEAD.
Six commits edited `CLAUDE.md` after `0a2e391`. `68a8af8` rewrites the routing rule, and
`32d00a6` touches the pass-conduct text. A restoration that pastes `a7dd5ad` text over a region
one of those commits edited reverts a deliberate later ruling. That is the `0a2e391` failure
class, run in reverse. Review focus 5 has two labels, "restored ruling" and "kept slimming," and
neither catches this case.

**Proposed fold:**

- Add a third label, "superseded after `0a2e391` (`<sha>`)".
- Require the implementer to run `git log -L` over each restored region from `0a2e391` to HEAD
  before restoring it.
- Have `diff-reviewer` confirm that no line added by those six commits disappears from B4's diff.

### M4. Chain W's reduced rounds in the style-guide-sync run get a gate dotfiles cannot run

**Where:** plan:115-119 (B1). Spec B1 AW-01 row, and the Pass B acceptance fixture (spec:411-420).

**Defect:** AW-01 makes a reduced round with no `reducedGate` render the repo-neutral class
default, which reads "the repo's type check plus only the test files this fix round touched"
(`pass-execute.js:246`). Amendment 1 sets no `reducedGate` on chain W. Dotfiles has no separate
type check, and W2 to W5 are `docs` tasks that touch no test file. A W docs fix round can
therefore read as "run nothing," report green, and skip the retired-phrase and dead-reference
scans in `check.sh`. Those scans are exactly what W's edits must pass. The planned fixture
asserts only "class default, no npm," so it would pass on this defect. The close's full gate
catches the problem late, but it shows up as a runner halt that maps to an audit id. That result
is the first-goal failure the sweep exists to prevent.

**Proposed fold:** Make the class default repo-neutral in substance as well as wording. For
example: "the repo's type check plus only the test files this fix round touched; where the repo
names no separate type check, the named gate." Add a B1 fixture assertion that W's reduced round
renders `bash scripts/check.sh`, the light-lane gate, which is cheap on dotfiles. The alternative
is to amend amendment 1 so chain W sets `reducedGate: "bash scripts/check.sh"`. The first option
fixes every non-npm repo at once.

## Minor

### m1. Keep the stricter hook off unrelated commits

**Where:** plan:85-92 (AC1).

Other sessions commit Brewfile, layered-package, and `bluefin/` manifest records to `main` under
the "same session" install rule. After AC1, each of those commits runs the ratchet step first.
Specify three things:

- A fast path: when `git diff --cached --quiet -- claude/.claude/tooling/ratchet-baseline.json`
  succeeds, go straight to `exec gitleaks`.
- The hook reads only the index and HEAD copies, never the working-tree baseline.
- The hook uses system `python3` with the standard library only, with no `uv` and no network, so
  an interpreter or dependency fault can never block an unrelated commit.

Add one fixture: an unrelated staged file with a malformed working-tree baseline passes.

### m2. The worktree runs its own evolving hook

**Where:** plan:48-50.

The relative `core.hooksPath` means AC1's intermediate commits run AC1's half-built hook, and a
broken hook invites `git commit --no-verify`. State in every dispatch that `--no-verify` is
forbidden, and that a hook failure is reported as a task failure.

### m3. Record the `ship` rename's behavior change where Geoff will see it

**Where:** plan:94-99 (AC2).

After the rename, "ship it" or `/ship` in ecxc-ski resolves to the project skill, which pushes to
`main` and deploys production (`ecxc-ski/.claude/skills/ship/SKILL.md:82`). Both aksailingclub
repos' skills push as well. In poplar, "ship it" stops auto-firing (S6). All of this is intended
(PS-01, S6), but the A-core STATUS or HISTORY entry should say it in one line.

### m4. B3 should give the implementer a fallback when a dispatch names no gate

**Where:** plan:124-126, spec B3 AW-19.

"Done means the gate the dispatch names" leaves done undefined for an ad-hoc Agent-tool dispatch
that names no gate. A conductor in another session still working from pre-B habits could send
exactly that. Add a fallback: when the dispatch names no gate, run the repo's documented gate from
its `CLAUDE.md`.

### m5. Say the A-core boundary check includes the full probe

**Where:** plan:110-111.

A-core merges the new hook and the new `check.sh` steps, and it does not repeat the one-executor
probe. Nothing is at risk for runners here, but a warm uncommitted edit on `main` would mix into
the merge. Apply M1's probe item 3 at this boundary too.

## Questions answered

- **In-flight runs:** partly covered; see M1. Compatibility carries most of the safety today, and
  the plan should state it and test it.
- **B4 concurrency:** the worktree isolates edits from live-file races. It does not protect the
  merge (M2) or the later history of the file (M3). The one-executor check at pass start cannot
  cover a file that every session edits all day.
- **Stricter hook:** it does not block unrelated commits if m1's fast path is specified. As
  written, the plan leaves that to the implementer.
- **`ship` to `go-ship`:** every caller is covered, and the whole-directory skills symlink needs
  no re-stow. See m3 for the behavior note.
- **Style-guide-sync gaps:** M4 is the one path defect found. P0's detection weakness is shared
  with M1.
