# Claude infra round, revision 1: adversarial review, mechanics and feasibility lens

Reviewer: fresh-context read, 2026-09-12. Read-only; nothing was edited.
Lens: can each task be executed as written by a `general-purpose` sonnet implementer with zero
prior context, gated by `bash scripts/check.sh` through `cairn-run-gate`, and reviewed by
`diff-reviewer` from the diff alone.

Inputs read: the plan, the survey, `claude/.claude/workflows/pass-execute.js`,
`scripts/check.sh`, `bin/.local/bin/cairn-run-gate`, `bin/.local/bin/claude-context-budget`,
`bluefin/stow-packages.txt`, the `~/.claude` symlink layout, both site repos' `.claude` trees
and git indexes, dubplate's implementer and architecture-reader agents, the guards doc, the
two wording-source plans, and the displacement destinations.

Out of scope by the conductor's standing rulings, not raised below: the site-repo file
deletions, the fifth displacement pick, the hoisted model pin, the dropped RESEND example, the
commit footer's model line.

**Verified sound, for the record.** Correction 1 holds: `agents`, `docs`, `skills`,
`instructions`, `workflows` and `CLAUDE.md` are each a symlink into
`../.dotfiles/claude/.claude/`, so no task needs `stow -R claude` and no deletion can leave a
dangling link. Correction 2 holds: `check.sh:37-42` has six legs and no shellcheck leg, and only
the gitleaks leg reads repository markdown. No name collision exists at either hoist
destination (`instructions/` holds `fastmail-api.md` only; `skills/` has no `svelte-check`).
Every byte count in the plan re-measures exactly (27,807; 5,260; 1,748; 2,658/2,684;
4,748/4,710). Every cited line number resolves except the two named in MINOR 5. All three
target repos track the files the tasks write, so each deletion produces a real commit.

---

## BLOCKER

**B1. Lines 7-12, 129-143, 218-745: the dispatch carries no route to the plan, so every Global
constraint is invisible to the implementer.** `pass-execute.js`'s `implementPrompt` (`:128-149`)
emits only `repo`, task id, title, `criteria`, `files`, `notes` and the gate string, and the
plan never states the args mapping, so a zero-context `general-purpose` implementer never learns
the plan file exists and never sees the off-limits `cairn-implementer.md` rule, the
specific-file staging rule, the two-line footer, the em-dash ban, the exit-75 re-issue, or Task
0's baseline gate line. Fix: add an "Args mapping" block to the plan giving the literal
`pass-execute` args for each segment, with the plan's absolute path and the whole Global
constraints block pasted into every task's `notes` (this round predates task 7's shared-notes
field, so the paste is unavoidable), and repeat the baseline gate line in each task's notes for
the reviewer.

**B2. Lines 125, 287, 344, 410, 456, 519, 611, 689: the gate string is relative, and the
implementer's working directory is not `~/.dotfiles`.** `cairn-run-gate` runs `bash -c "$gate"`
in `$PWD` and keys its state on `$PWD`, a subagent's cwd resets to the session's primary
working directory on every Bash call, and `~/Projects/dubplate` has its own `scripts/check.sh`,
so `cairn-run-gate 'bash scripts/check.sh'` will silently run dubplate's Go gate and report a
false green for a dotfiles task. Fix: make every gate string absolute and self-contained, for
example `cairn-run-gate 'cd /var/home/glw907/.dotfiles && bash scripts/check.sh'`, and state
once that no gate string in this round may be relative.

**B3. Lines 96-99, 247-251, 278-280: task 1's wording source is another session's uncommitted
diff, which that session owns and may commit at any moment.** The plan both directs task 1 to
read `git diff claude/.claude/agents/cairn-implementer.md` for its template and requires
(criterion 4) that the file still be modified and unstaged, so the cairn session doing the thing
the plan says it owns (committing) destroys the template and fails an acceptance criterion
through no act of the implementer. Fix: have Task 0 snapshot the diff to a scratchpad file, name
that file as task 1's wording source, and restate criterion 4 to accept either state (warm, or
committed with the same replacement paragraph reachable at that commit).

---

## MAJOR

**M1. Lines 279-281, 446-447, 606: acceptance criteria pinned to `HEAD` and `HEAD~1` in a repo
another session commits into.** Task 1 criterion 5, task 4 criterion 1 and task 6 criterion 4
all resolve content through `HEAD` or `HEAD~1` in `~/.dotfiles`, and a cairn-session commit
landing between the implementer's commit and the reviewer's read makes each one name the wrong
object. Fix: require the implementer to report its commit SHA per repo and have every criterion
resolve content through `<reported SHA>` and `<reported SHA>^` rather than `HEAD`.

**M2. Lines 446-448: task 4's byte-identity proof is not runnable as written.** The criterion
reads `git -C ~/Projects/dubplate show HEAD:.claude/agents/go-architecture-reader.md` "at the
parent commit", but after the retirement commit `HEAD:` no longer contains that path, so the
reviewer's only content proof errors. Fix: state the command as `git -C ~/Projects/dubplate show
<the reported deletion SHA>^:.claude/agents/go-architecture-reader.md | diff -
claude/.claude/agents/go-architecture-reader.md`.

**M3. Lines 380-383: the two hoisted instruction files lose their only discovery path.** Neither
`907-life/CLAUDE.md` nor `ecxc-ski/CLAUDE.md` names `instructions/` at all (grepped, zero hits),
so the plan's reasoning cuts the other way: an agent that reached these files by typing
`.claude/instructions/ai-operational-rules.md` finds nothing after the deletion, and nothing
anywhere points at the workstation copy, making the hoist a net loss of reachability. Fix:
require a one-line pointer in each site repo's `CLAUDE.md` naming
`~/.claude/instructions/<name>.md`, or hold the two instruction files in scope and hoist only
the skill.

**M4. Lines 224-227, 265, 389, 432-435: no per-task live-executor re-check in the three
non-dotfiles repos, and no gate ruling for their commits.** Task 0's check runs once at launch
while dubplate's 5b-ii lane is pending launch, and the plan never says whether tasks 1 and 4
must run dubplate's own `scripts/check.sh` (dubplate's `CLAUDE.md` orders it before every
commit) or whether task 3 runs either site repo's `npm run check`. Fix: give tasks 1, 3 and 4 a
pre-write step re-running the live-executor and clean-tree check in the target repo, and rule
explicitly that a `.claude/**` markdown-only commit in those repos runs no repo gate, naming why.

**M5. Lines 160-163, 625-627: task 7's precondition names no executable check.** "Confirm no
live workflow run is executing `pass-execute.js`" cannot be established by a subagent: a
Workflow run lives inside the harness process, so `pgrep` shows nothing distinguishable and the
implementer has no visibility into another session's runs. Fix: move the precondition to the
conductor, stated as a Task 0-style pre-dispatch check over `~/.claude/tasks` and the workflow
journal directories, and reduce the task's own step to "the dispatch asserts the conductor
cleared this".

**M6. Lines 7-8, 139-143, 194-196: the named invocation path is the one the Workflow tool
refuses.** The global orchestrator-hygiene rule is that the Workflow tool refuses a
`~/.claude/workflows` `scriptPath` and the runner is invoked by name, and a scratchpad copy
would also make task 7's edit invisible to any later run. Fix: state that segments A and B are
launched as `Workflow({ name: "pass-execute", args: {...} })`, and that no copy of the script is
made.

**M7. Lines 165-179, 804-807: the 1.0M ceiling rests on a circular rate.** The 0.086M per task
is derived from the previous plan's *ceiling*, not from any measured spend (the plan says so),
while the only measured datum on this machine is 0.55M per task, and this round's tasks are not
small: task 3 touches nine files across three repos, task 5 reads a 46KB source plan plus a
network fetch, and task 6 iteratively re-measures a 27.8KB file and writes two new docs, each
with an Opus reviewer read on top. Fix: raise the ceiling to 1.5M or split the round at the
segment-B boundary, and re-cut the reserve to cover segment C's two main-loop chains, whose
implementer and reviewer reports land in the conductor's own context rather than a workflow's.

---

## MINOR

**MIN1. Lines 552-555, 580-585: nothing forbids writing a displacement pointer as an
`@`-import.** `claude/.claude/CLAUDE.md` uses no `@`-imports today, and
`claude-context-budget:33-51` treats an `@`-referenced `*.md` as a context-loaded import, so a
pointer written as `@docs/pass-gate-economy.md` would load the displaced text at session start
and nullify the displacement while still passing criterion 1. Fix: add a constraint that every
pointer is a plain path reference, never an `@`-import.

**MIN2. Lines 563-569, 586-588: pick 3's destination does not carry the displaced content.**
`cloudflare-estate-inventory.md` carries the account id and the ASC Access route but not the
"make routine changes directly" stance or the "MCP token is read-only for Access and
Workers-domain writes, use curl" rule (grepped), so criterion 3's grep for pick 3 will fail and
the implementer will fall to pick 4. Fix: name the applied set as picks 1, 2, 4 and 5 (which
re-measures to about 22,500 bytes) and keep pick 3 as the fallback, or add the missing two
clauses to the inventory as part of the task.

**MIN3. Lines 37-41, 220-221: the pre-flight's tree state is already stale.** The plan records
HEAD at `9034fd3`, but committing the plan itself moved HEAD to `603f667`, so Task 0's criterion
1 ("state matches this plan's pre-flight") is false as written before the round starts. Fix:
have Task 0 assert the warm-file set and the absence of any task's Files, not a specific HEAD.

**MIN4. Line 18 with survey lines 86-87: the plan's named Spec contains an instruction its own
Correction 1 disproves.** The survey says a new file under `claude/.claude/` appears only after
`stow -R claude` and that a task adding a file runs it; an implementer pointed at the survey as
the Spec would follow that rather than the `readlink` proof. Fix: add a line to the survey, or to
the plan's Spec reference, marking that bullet superseded by Correction 1.

**MIN5. Line 238 and line 393: two citations do not resolve as written.** The gate paragraph in
`site-implementer.md` is at `:89-91` (correct) but `dubplate-implementer.md`'s step 5 is at
`:67-70`, not `:68-71`; and task 3 criterion 1's command carries an unexpanded placeholder,
`diff <hoisted> <either retired repo copy at its parent commit>`. Fix: correct the line range and
write criterion 1 as a literal `git -C ~/Projects/ecxc-ski show <SHA>^:.claude/skills/svelte-check/SKILL.md | diff -`
command.

**MIN6. Lines 596-598: the context-budget hook will fire on every intermediate write to
`CLAUDE.md`.** `claude-context-budget --hook` is registered as a PostToolUse hook
(`settings.json:87`) and exits 2 with blocking stderr while the file is over budget, so task 6's
implementer is told it is over budget after each pick until the last one lands. Fix: note the
expected hook feedback in the task, and restate that the budget is never to be raised to silence
it (the plan already forbids the edit; it does not warn about the prompt).

**MIN7. Lines 640-649, 682-684: task 7's new argument is never named.** The plan requires the
header comment to document the argument "by name and shape" while leaving the name to the
implementer, so the reviewer has nothing deterministic to check and a future plan author has no
key to pass. Fix: name it in the plan (`sharedNotes` is the natural counterpart to
`paintProtocol`) and state that it is appended to the criteria line in both prompt builders.

**MIN8. Lines 404-405: criterion 5's `ls` failure depends on the deletion method.** `git rm`
prunes the emptied `svelte-check` directory, but a plain `rm` of the file leaves it, so the
criterion passes or fails on an unstated choice. Fix: require `git rm` for every deletion in
tasks 3 and 4, and check the directory's absence rather than the file's.

**MIN9. Line 194: segment A's stated end is ambiguous.** Task 3 makes three commits in three
repos in an unspecified order, so "task 3's dotfiles commit, gate green" does not identify the
boundary commit unless the dotfiles commit is last. Fix: state that in a multi-repo task the
dotfiles commit lands last, and that the boundary is that commit.

---

## Counts

BLOCKER 3, MAJOR 7, MINOR 9.

The segment table itself holds: three, three and two tasks, each boundary on a gated dotfiles
commit, task 6's dependence on task 2 respected across the A-to-B boundary, and the
`pass-execute.js` edit in segment C, which no earlier task in the run depends on and which runs
outside the runner. The two-task segment C is overridden by a named rule. Task 4's byte-identity
mechanics, the `node --check` proof (node v24.20.0 on PATH), and the three-repo commit-footer
form (both site repos already use the two-line form) all check out.
