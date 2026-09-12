# Gate economy on a pass

This holds CLAUDE.md's "Gate economy on a pass" section; CLAUDE.md keeps a pointer to it.

Clock time on a pass is the per-task gate and the fix rounds, not the implementer. Rules, all
approved, all cheap in tokens:
- **The slow suite runs only where it can catch something.** A browser e2e or visual suite
  joins the per-task gate only for tasks that move rendered paint; paint-neutral tasks run the
  check suite and unit tests, and the pass-end gate plus CI on every push run the full suite.
  Across B2's eight tasks the per-task e2e caught nothing the checks, the diff reviewer, and CI
  did not, at a third of each task's hour.
- **Comment-only fix rounds run a reduced gate** (the comment linters, the doc link gate, and
  the touched files' unit tests). The reviewer marks each blocking finding `commentOnly`; the
  chains scripts route on it.
- **Scope the engine test suite to the blast radius.** A task whose Files touch nothing under
  the engine's source runs the consumer's own unit suite, not the engine's.
- **A pre-flight checklist in every task's notes prevents the fix rounds** B2 kept paying for:
  no comment claims what its assertion does not prove; the labeled report block verbatim;
  no process citations in shipped comments; counts found, changed, deferred; re-emit before
  the gate.
- **Task 0 takes no gate** (Geoff, 2026-09-12): a read-only staleness pre-task runs none, and
  the lane's baseline is the conductor's own one `cairn-run-gate` call at lane launch, quoted
  to the reviewer as Task 0's gate evidence.
- **The cross-lane review fires on a disjunction** (Geoff, 2026-09-12): the merge ritual's
  `diff-reviewer` over the merged range runs when the rebase was not a fast-forward **or**
  when the two lanes touched a shared package or contested surface.
- **A scoped gitleaks leg owes a branch-history scan** (Geoff, 2026-09-12): where the gate
  scopes gitleaks to the change set, the merge ritual's in-tree gate adds one `gitleaks
  detect` over the branch's commit range, without `--no-git`.
- **Gates run through `cairn-run-gate '<string>'`** (dotfiles bin; generic despite the name):
  it blocks to completion and prints the tail, so an implementer never polls a log and its
  transcript stays small for the reviewer.
- **Parallel chains where Files are disjoint**, one worktree each, with any shared port made
  an environment variable; overlap a CI baseline regen with the diff review; fold
  single-deliverable tasks into a neighbor (each task pays about thirty minutes of fixed
  overhead).
- **Orchestrator hygiene:** halt agents PREPEND to STATUS, never rewrite it; a merge step brings
  `main` in first with fixed resolution rules (STATUS takes main's, HISTORY keeps both); the
  Workflow tool refuses a `~/.claude/workflows` scriptPath (copy to the session scratchpad);
  repeated protocol text in args goes in one field the chains script appends at prompt time.
