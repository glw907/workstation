# Lean pass cutover plan: contract, criteria, and proportionality review

Target: `docs/superpowers/plans/2026-10-10-lean-pass-cutover.md` at `ec14c1e`. Spec:
`docs/superpowers/specs/2026-10-10-lean-pass-process-design.md`. Fold dispositions read and left
standing. Every finding below was checked against files or command output on 2026-10-10. I flag
only gaps that affect correctness, a stated requirement, or a co-equal budget (tokens, attended
time, clock).

Counts: 0 blocker, 7 major (one an owner fork), 9 minor.

## What holds

- **Coverage of rollout steps 1 to 4.** Every spec table row in `~/.dotfiles` has a task (S1-T3 to
  S1-T12). Step 1 also covers the tag and merge, both probes, the ROADMAP filings, and the rung 14a
  hold before the merge. Step 2 covers `CLAUDE.md`, the fast lane with its header and doc, the
  measured peak, and the shard. Step 3 covers the sweep, dubplate's four named files, ecxc-ski's
  `ship` and rule file, the dubplate adapter, both `CLAUDE.md` caps, and the HISTORY harvest. A
  check of every repo's HISTORY confirms ecxc-ski and cairn-pub have none. Step 4 covers the audit
  under rulings 7 and 14.
- **The rules inventory is complete.** I read the headings and bold rules of `model-economy.md`,
  `pass-gate-economy.md`, and `unattended-work-guards.md`. Every rule maps to an ME, PG, or UG row
  with a named home or a named deletion.
- **Most acceptance checks are non-vacuous.** The S1-T12 greps, run now, hit 17 and 20 files, each
  one named by the plan. The S4-T2 journal glob matches 47 journals that carry the chain's labels.
  The bullet counts are right: cairn 155, dubplate 196. Every site has `check`, `test`, and `build`
  scripts.
- **Risk classes match the spec's definitions.** Nothing in steps 1 to 4 is `auth-data`, and a
  per-task class changes behavior only at `auth-data`. So the small inconsistencies stay
  immaterial: S1-T2 pushes to GitHub without the `live-account` mark, and S1-T10 or S2-T5 may touch
  a `runner` path.

## Major

**M1. The pair probe passes without `worktree.baseRef` (vacuous acceptance).** Plan lines 730-743.
The probe runs right after S1-T14's `pull --ff-only`, when local `main`, `origin/main`, and the
merge commit are the same commit. M4 says subagent worktrees without the setting branch from the
default branch. That gives the same merge base, so "merge base equal to the merge commit" passes
with the setting absent. The spec needs `"head"` because pairs launch "after the session commits",
from unpushed work. **Fold:** reorder 1c so S1-T17's dotfiles `ROADMAP.md` commit lands locally
first and stays unpushed. Then dispatch the pair and assert that each merge base equals that local
commit and differs from `origin/main`. Push afterward. This adds no dummy commit and costs 0
minutes.

**M2. Step 3's clock stop is likely inert.** Lines 959-964 and 1003-1012. The session runs from
`~/Projects`, which is not a git repository, and edits five worktrees. The hook resolves the git dir
from the tool call's `cwd` (spec Execution 6). If the session works by absolute path from
`~/Projects`, every call resolves to a non-git cwd and the hook stays silent. The plan never says
which worktree's git dir holds the task-clock file. "Clock stop on" therefore has no observable
check on the longest step (530 task-minutes). **Fold:** at each task start, the step 3 session
`cd`s into that task's worktree and writes the clock file in that worktree's git dir. S3-T9 removes
all five. A pair's clock belongs to the worktree the session sits in while it waits. Otherwise,
state that step 3 runs without a clock stop, as step 1 does. Either is about 2 lines.

**M3. Session 1a's written grant does not cover S1-T2.** Lines 282-284 and 317-319. M2 says a
session editing a checkout it did not isolate still asks before committing. The 1a prompt grants
commits and pushes on `lean-cutover` only, plus "never push `main`". S1-T2 commits and pushes
dubplate `master` in another repo's main checkout. Expect a prompt, which is one attended event and
a stalled `--bg` run, or a refusal. **Fold:** add this sentence to the 1a prompt: "and, for S1-T2
only, to commit `docs/STATUS.md` on dubplate `master` and push it". This adds 0 minutes and saves a
likely stall.

**M4. S2-T3's acceptance never runs the fast lane it prints.** Lines 878-894. Line 1 runs legs
"concurrently, failing if any leg fails". The acceptance covers unit cases on the printed strings,
a line count, and CI. It never runs a printed line, and it never proves a failing leg makes line 1
fail. A concurrent wrapper that drops a child's exit status is the classic false green, and this
gate becomes every later cairn pass's per-task gate. **Fold:** add two checks. First, each printed
line run through `cairn-run-gate` on the branch prints `gate exit: 0`. Second, a unit or shell case
where one leg exits non-zero makes line 1 exit non-zero. This adds about 10 minutes.

**M5. The cairn adapter keeps a home-grown CI wait on the critical path.** Lines 436-437, 870, 890,
894, 909, and 911. S1-T6 carries "the protected paths still wait for CI green on their own commit
before the next task" into the new `cairn-pass`. S2-T2, S2-T3, and S2-T4 are all protected, so step
2 serializes three CI cycles. The spec moves CI "off the critical path" (Execution 4) and keeps a
step only on its catch record (ruling 2). Neither the spec nor the catch ledger names this rule.
Its source is the 2026-10-09 ruling in today's `pass-core:113-116`. Under the lean model, a red
already stops the line. **Fold:** drop the rule from the adapter, since CI still runs on every push
and a red stops the line. If it must stay, record it as a third departure with its evidence. S2-T2
still waits, because CI is its acceptance. Merging S2-T4 into S2-T3 also removes one commit and CI
cycle. This saves about 25 to 40 minutes in step 2, and the same on every later pass that touches
those paths.

**M6. Geoff launches steps 2 to 4, which costs attended events the spec does not budget.** Lines
784-787, 797-798, 818-826, 983-995, and 1167-1173. Spec Execution 1: "The planning session
launches it." The Success test allows attended time for the design, the PR read, and clock stops
only. The plan hands Geoff the step 2, 3, and 4 launch blocks, adding 2 to 3 events, and its clock
estimate excludes "the gaps before he launches a session". None of those blocks needs Geoff: each
is worktree setup plus `claude --bg`. **Fold:** session 1c runs the step 2 and step 3 pre-launch
blocks itself after S1-T17 and records each session id in STATUS (spec Execution 1). Step 4 follows
M7's ruling. S1-T18 shrinks to recording the ids. This saves 2 to 3 attended events and
unbudgeted launch gaps. It is also cheap at the 1b-to-1c handoff, which stays because 1c must load
the merged settings.

**M7. OWNER FORK: step 4 waits for step 2's PR and sits on the critical path.** Lines 14-17 and
809-811. By the plan's own numbers, wall clock is 665 + max(step 3 at 400, step 2 at 385 + step 4
at 210) = 1,260 minutes. Step 4 is the binding term. Step 4 writes only dotfiles, its gate runs on
the light lane at 105 MB peak (M13), and it shares no file or heavy lock with steps 2 and 3. S2-T4's
`Memory peak` comes from its own systemd unit, so another light gate does not disturb it. The only
reason to wait is reading ruling 10's "pairs by default" as a cap of two sessions.
- Option A: launch steps 2, 3, and 4 together. Wall clock becomes 665 + 400 = 1,065 minutes, and
  Geoff gets three PR streams at once.
- Option B: keep the plan as written, at 1,260 minutes.
- **Recommendation: A.** It saves about 195 minutes of wall clock and costs nothing in tokens.
  Ruling 10 sets a default, and step 4 creates no contention.

## Minor

**m1. dubplate's `--base origin/master` silently runs the full gate.** Lines 1018, 1092, and 1112.
`scripts/check.sh:274-276` accepts only a full 40-hex commit id. Any other value falls back to the
full form ("any other value runs the full form", `:142-144`). S3-T1's dry run, S3-T5's test, and
the adapter's fast lane would each run the full gate. **Fold:** omit `--base`. On a branch it
defaults to the merge base with `master` (`:300-302`). The other option is to pass `"$(git
rev-parse origin/master)"`. This saves about three dubplate full-gate runs.

**m2. S1-T8 never checks the reviewer's `auth-data` bar.** Lines 519-523. The spec row requires
`diff-reviewer` to carry the bar itself: coverage gaps block, and cosmetic citations never do. The
acceptance checks only `whole-branch`. **Fold:** add `grep -q 'auth-data'` and a check for the
coverage-gap rule on `diff-reviewer.md`.

**m3. The sweep's acceptance cannot see two named concepts, and it misses one file.** Lines 605-634.
The greps carry no `code-simplifier` or HISTORY term. So `cairn-release:79-100,165`, `log-project`,
and the simplifier wording can survive a green acceptance. `skills/go-ship/SKILL.md:30-34` makes
the simplifier a standing pipeline step and is not named. It is user-invoked
(`disable-model-invocation`), so "on request" may cover it, but the executor needs the call.
**Fold:** add `code-simplifier:code-simplifier` and `docs/HISTORY.md` checks scoped to the named
files. Name `go-ship` with a keep-as-on-request disposition.

**m4. The harvest estimates look starved against a clock stop.** Lines 937 and 1142. 120 minutes
for 155 cairn bullets is 46 seconds a bullet, and for 196 dubplate bullets it is 37 seconds,
including writing each moved lesson into its home. The clock stop fires at 240 minutes, which
counts as one attended event. **Fold:** estimate 180 minutes each, or let the plan triage stale
bullets by heading first.

**m5. The per-bullet PR tables bloat Geoff's one touchpoint.** Lines 927, 1054, 1070, and 1138.
About 380 rows across the step 2 and step 3 PRs. **Fold:** put counts by disposition (moved, owed,
dropped) in the PR body, list moved bullets with their homes, and put the full table in a
`<details>` block.

**m6. Pass B's start gate contradicts the spec and the plan's own order.** Lines 786-787, 945-947,
and 1264-1266, against lines 809-811. The spec says pass B's branch merges `main` after step 2, and
that "No pass runs until its repo's step merges". The plan's Order section says step 5 needs step
2. S1-T18, S2-T6, and the last line instead wait for steps 3 and 4, which ties the success-test
pass to five site PR reads. **Fold:** gate pass B on steps 1 and 2 merged.

**m7. Repeated checks catch nothing new.** S1-T17's one-executor re-run (lines 771-772) comes
minutes after S1-T14's. S1-T18 is a STATUS-only task (lines 782-793). S3-T1 baselines four site
gates (lines 1016-1024) that each task's fast lane re-runs anyway, and a red there can be compared
against `origin/main` on demand. **Fold:** drop the S1-T17 re-run, fold S1-T18 into S1-T17, and cut
S3-T1 to dubplate's dry run plus the grep counts. This saves about 30 minutes in all.

**m8. The `dotfiles-pass` project skill sits outside the gate's scan set.** Lines 450-459.
`check-claude-refs.py` scans only `claude/.claude`, so the new `.claude/skills/dotfiles-pass` gets
no retired-phrase or dead-reference check. **Fold:** add `.claude/skills` to the scan set in S1-T6,
or accept the gap and say so.

**m9. Small unverifiable outcomes.** S2-T2's `update_snapshots` path and its retries notice have no
check (lines 865-867). **Fold:** run `actionlint`, or read the dispatch job's `if:` in the diff
review. Several launches never record the session id in STATUS (spec Execution 1). M6's fold covers
steps 2 and 3. The S2 launch prompt's "after your first commit" (line 836) is ambiguous when S2-T1
is the first task. **Fold:** say "from the branch head".

## Proportionality

The 1,266 lines are mostly load-bearing. The spec mandates the rules inventory (about 65 lines) and
the audit map (about 35). The launch blocks replace a conductor. M2, M4, M6, and M7 quote the fold
record. Citing the fold record for them instead would save about 30 lines, roughly 1k tokens per
session read across six sessions, which is optional. No task carries implementation code. The task
grain fits the work, the estimates are plausible apart from m4, and the closes (265 minutes across
four steps) are not padded.

What the plan costs beyond its own goal:
- Step 4's serialization: about 195 minutes of wall clock (M7).
- The protected-path CI waits: about 25 to 40 minutes, plus every future pass that touches those
  paths (M5).
- Repeated checks: about 30 minutes (m7).
- dubplate's full-gate fallback: about three full runs (m1).
- Two to three launch events for Geoff (M6).

Against those cuts, m4 adds about 120 task-minutes. On the critical path that is about 60 minutes
once step 4 no longer binds.

**Verdict:** proportionate in substance, but about 4 hours of wall clock can be cut, roughly 250
minutes gross and 190 net of m4. Most of it comes from launching step 4 alongside steps 2 and 3.
