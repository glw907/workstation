# Infra sweep A-core and B plan: fold verification

Target: `docs/superpowers/plans/2026-09-28-infra-sweep-a-core-b.md` at dotfiles `5a35388`, against
the pre-fold `62c5e6d`, the fold record, the three reviews, and the spec. One fresh reader
(`claude-opus-5-5`, high), read-only. Every mechanism claim below was run on this machine.

**Counts:** 0 blocker, 4 major, 4 minor.

The fold is sound in shape. All 33 findings land where the record says. The fold's own new
mechanics carry the defects: the rollback path in merge integration, and two of the four probe
clauses. Each defect was reproduced on this machine. Each fold is one or two lines.

## 1. Did each major close where the fold record says?

| Major | Closed? | Where |
|---|---|---|
| C-M1, K-M2 (overrides until merge) | Yes | plan:38-53, B3 plan:222-223 |
| C-M2, C-M4, K-m7, D-m1 (failure table) | Yes | plan:105-149, 36 rows; each task's acceptance names its rows |
| C-M3 (vacuous close) | Yes | AC3 label check plan:189-191; "no hit" plan:84-85. The seeded phrases' hits sit only in `CLAUDE.md` and `cairn-overnight-to-release.js`, both in B4's Files, so the "no other label" rule is satisfiable |
| C-M5 (Pass B pre-flight) | Yes | P2 plan:201-204 |
| C-M6, K-m1 (bytecode) | Yes | plan:166-174, row M1 |
| K-M1 (relative gate) | **Implementer half only** | Override 1 covers implementers. `diff-reviewer` and the B-close simplifier get no worktree path (V4) |
| K-M3 (four more clauses) | Yes | Overrides 3 to 5. `cairn-implementer.md:7, :58, :75, :122` confirmed |
| D-M1 (in-flight probe) | Folded, but two clauses misfire | plan:57-63 (V2, V3) |
| D-M2 (merge integration) | Folded, but the red path breaks | plan:72-78 (V1) |
| D-M3 (`0a2e391` later edits) | Yes | B4 plan:227-231. `git log 0a2e391..HEAD -- claude/.claude/CLAUDE.md` still lists the six commits |
| D-M4 (chain W reduced gate) | Yes | Spec amendment 1 and Pass B acceptance (diffed); plan B1 and Review focus 4 |

## 2 and 3. Findings (contradictions, order, mechanisms from memory)

### V1. major. plan:77-78. The red path "reverts the merge and returns to step 2" loses the pass

**Defect.** After `git revert -m 1 <merge>`, the pass branch's commits are already ancestors of
`main`. A re-merge is "Already up to date" and brings back none of the reverted content. Step 2
then merges `main` into the pass branch, so the revert lands on the branch and deletes the pass's
work from the worktree. This is git's documented behavior (`Documentation/howto/revert-a-faulty-merge.txt`).

I reproduced it in a scratch repo. After the revert, `git merge --no-ff br` printed "Already up
to date" and left the file at its pre-pass content. `git merge main` on `br` then removed the
branch's line. The same test confirmed that `git revert` runs no `pre-commit` hook, so plan:79-80
is correct.

**Fold.** Gate before the merge commit exists, so nothing needs a revert. Step 4 becomes:

1. Run `git merge --no-ff --no-commit <branch>` in `~/.dotfiles`.
2. Run step 5's gate and `verify` on that tree.
3. On green, run `git commit`, which also runs the ratchet and gitleaks hook on the merge. That
   closes the D-M2 hook gap the fold refused to address with a new hook.
4. On red, run `git merge --abort` and return to step 2.

Keep `git revert -m 1` for rollback only, where re-landing is out of scope. If re-landing after a
rollback is ever wanted, the plan must name "revert the revert" as the first step.

### V2. major. plan:61. Probe clause (4) `pgrep -f <wt>` always matches its own shell

**Defect.** The Bash tool runs each command as `/bin/bash -c '... eval '\''pgrep -af <path>
...'\'''`. The wrapping shell's command line contains the path, so `pgrep -f` matches it. The
probe returns positive every time, even for a path that does not exist. I verified this with a
made-up `.../dotfiles-infra-zzz` path, which returned the invoking shell's pid. Clause (4) blocks
every pass start and every merge. The conductor waits an hour and then files a false STATUS
question.

**Fold.** Use a bracket pattern that cannot match itself:
`pgrep -af '/Projects/.worktrees/[d]otfiles-infra-a'` (and `-b`). An alternative is to filter
the shell's own pid out of the result.

### V3. major. plan:58-60. Probe clause (2)'s glob misses every Agent-tool transcript

**Defect.** The Agent tool writes its transcripts as direct children:
`<project>/<session>/subagents/agent-*.jsonl`. This machine has 2,185 of them. Only workflow
transcripts sit one level deeper. The pattern `subagents/**/agent-*.jsonl` misses the direct
children in the two ways a conductor would run it:

| Run as | Files matched |
|---|---|
| `find -path` (`**` requires a `/` before `agent-`) | 2,655 of 4,840 |
| bash glob without `globstar` | 0 |
| bash glob with `globstar` | 4,840 |

In the first two cases, the Agent-tool chains, which are the reason D-M1 gave for the clause,
stay invisible. "This session's directory" also names no mechanism.

**Fold.** State the command:
`find ~/.claude/projects -path '*/subagents/*' -name 'agent-*.jsonl' -mmin -25 -not -path "*/$CLAUDE_CODE_SESSION_ID/*"`.
`$CLAUDE_CODE_SESSION_ID` is set in the conductor's shell and names its transcript directory
(verified).

### V4. major. plan:38-53, 221-222, 230-231, 75, 235. `diff-reviewer` dispatches carry no worktree

**Defect.** The overrides bind "every implementer dispatch". The session cwd is `~/.dotfiles`,
which is `main`. The following dispatches are therefore issued without the worktree path, and a
bare `git diff`, grep, or gate call reads `main`:

- `diff-reviewer`, which runs per task, on the merge read at step 3, and on the B3 and B4 grep
  post-conditions.
- The B-close `code-simplifier`.

An absence grep, such as "the phrase has no hit", can pass falsely against `main`. Other checks
cost a `fix` or an escalation round. K-M1's review named the reviewer explicitly. B close step 1
also names no owner for committing the simplifier's refinements or running the gate afterward.

**Fold.** Add one line under the overrides: every `diff-reviewer` and `code-simplifier`
dispatch names `<wt>` absolutely, uses `git -C <wt>`, and uses override 1's gate string. B close
step 1 then reads: the simplifier edits in `<wt>`, and an implementer dispatch commits the
refinements and runs the gate.

### Minor

- **m1. plan:213-217.** B2's acceptance requires that no runner prompt or implementer file
  carries a "vanished" clause. Today the clause lives at `site-implementer.md:101` and
  `pass-execute.js:336`, which are B3's and B1's files. B2's Files, which are the spec's B2 plus
  `check.sh`, cover neither. The spec's B2 Files list is narrower than its own AW-20 outcome, and
  the plan inherits that gap. *Fold:* B2's Files add both runners and both implementer files for
  the AW-20 lines. The alternative is to move the implementer half to B3 and scope B2's
  acceptance to runners and `docs-page-chain.js`.
- **m2. plan:139 against plan:86 and row M2.** S3 exercises the collision check through
  `verify`. `verify` also runs the machine checks: `~/.claude.json` and `claude plugin list`. The
  latter shells out to the real CLI and reads the real home. That contradicts "no fixture reads
  outside its root". *Fold:* S3 puts a stub `claude` first on `PATH` and a fixture
  `.claude.json` in the injected home. The alternative is to name a way to run only the
  collision check.
- **m3. plan:77.** Step 5 runs `bash scripts/check.sh` bare. The workstation rule routes every
  gate through `cairn-run-gate`. *Fold:*
  `CAIRN_GATE_LANE=light cairn-run-gate 'bash ~/.dotfiles/scripts/check.sh'`. With V1's fold,
  this command runs on the uncommitted merge.
- **m4. plan:193-197.** The plan names no writer or branch for the A-core boundary's HISTORY and
  STATUS entry. By contrast, B4 writes HISTORY on its branch. *Fold:* the conductor commits both
  on `main` after the merge. They are docs-only, and the new hook fast-paths them.

## Mechanisms spot-checked and sound

- The gate state directory is `${TMPDIR:-/tmp}/cairn-gate-$(id -u)/<key>/pid`
  (`cairn-run-gate:29, :33`). `TMPDIR` is unset here, and the directory exists with keyed
  subdirectories.
- `systemd-inhibit --list` shows `cairn-gate-<lane>` as WHO. `cairn-run-gate:73` wraps the gate
  in `awake --who "cairn-gate-$lane"`, and `awake:56` calls `systemd-inhibit --who=...`.
  Grepping for `cairn-gate` matches it.
- The standard library defines `sys.dont_write_bytecode = True` for this purpose. Setting it in
  the importing script before the import stops the module's `__pycache__`. `check.sh:10` exports
  `PYTHONDONTWRITEBYTECODE=1` for the test path. `.gitignore:29-30` ignores `__pycache__/`.
- `git log -L <range>:claude/.claude/CLAUDE.md 0a2e391..HEAD` is valid. The six later commits
  match the fold record.
- `~/.claude/agents` and `~/.claude/tooling` are folded symlinks into `~/.dotfiles` `main`.
  `core.hooksPath` is the relative `scripts/githooks`. The hook's last line is
  `exec gitleaks git --staged ...`. `check.sh:33` reads `git ls-files`, so override 2 holds.
- The `pass-core` table at :89 sets `sweep` to a Sonnet reviewer, grep post-conditions, and
  "existing tests stay green". The plan overrides the gate cell and B4's reviewer and says so.
  B3 on `sonnet` fits the table, and `diff-reviewer`'s frontmatter pins `claude-opus-5-5` for
  everything else.
- The only personal/project skill collision is `ship`, in ecxc-ski and both aksailingclub repos,
  which matches AC2 and the A-core boundary's HISTORY line.
- Review focus 4 does not repeal the 2026-09-09 ruling. The fixture pins the class default, and
  W's `reducedGate` is an explicit per-chain choice.

## 4. Executable by a thin conductor?

Yes, once V1 to V4 are folded. V2 alone would stall the first probe. V1 matters only on a red
`main` gate, but when it fires it destroys the pass branch's content. With the four one-line
folds, no open reading remains that needs a judgment call from the conductor. The minors can
be folded or left for the implementer to settle.
