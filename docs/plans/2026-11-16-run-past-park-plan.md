# Run past a parked pass: plan

Initiative: unattended-rounds

Design: `~/Projects/initiatives/.claude/worktrees/unattended-rounds/unattended-rounds/specs/2026-11-16-run-past-a-parked-pass-design.md`
("the design"). Geoff approved it in the Approval Queue on 2026-11-16 at 19:01Z (document
`20261116-163931-082d9d`), with no notes, and picked "The running round takes it now". The approval
covers unattended planning for this pass. This is a one-pass round: no conductor, no round id, no
order table, and the executor closes the pass. The ruling for the running `dubplate` round is the
desk's to deliver, never this pass's.

Class `runner`: every path is under `claude/.claude/skills/**` or `claude/.claude/tooling/**`
(`.claude/skills/dotfiles-pass/SKILL.md`, "Risk-class path map"). No path is `auth-data`. Worktree
`~/.dotfiles/.claude/worktrees/run-past-park` on branch `run-past-park`, cut from `origin/main` at
`8822220`. The planner commits this plan, its prompt, and the patch on the branch before launch.
Push target `glw907/workstation`, PR base `main`. Executor `workstation-run-past-park`
(Sonnet at `medium`, Fable advisor). The design gives 75 path minutes. This plan's path is 70
("Tasks"); a path over 150 would have parked.

The pass edits rule text only. It changes no setting, hook, permission rule, tool, or script, and
it edits no round's design or prompt in `~/Projects/initiatives`. Rule files follow
`~/.claude/docs/voice/agent-facing.md`. The PR's opening, and any document the pass sends Geoff,
follow `~/.claude/docs/voice/written-for-people.md`.

## Pre-flight

Geoff has no step in this pass: no sign-in, secret, dialog, setting, hook, or permission rule, and
no value from any store.

Permissions checked: the planner read all 110 rows of `~/.local/state/claude-denials.jsonl`
(2026-11-01T00:55:05Z to 2026-11-16T07:43:05Z, all inside the 30-day window) against each task's
commands. The Self-Modification rows target `claude/.claude/settings.json`, which this pass
never touches. Refused shapes that match this pass's commands, and the alternative for each:

- `claude stop <id>` inside a chained or piped command (2026-11-10, 11-13, 11-16). Run it alone.
- A chained `git commit ... -- BACKLOG.md && ...` (Modify Shared Resources, 2026-11-15). Run
  `git commit` alone, naming its files.
- `gh pr merge`, and `gh pr checks` chained into a merge (Merge Without Review). Land only through
  `approval-queue land` or `merge`, per `approval-packet` step 1.
- `git push origin HEAD:main` (2026-11-08, 11-10). Push the branch `run-past-park` only.
- `git commit --no-verify` (Safety Bypass Flag). Never.
- Classifier-unavailable `Edit` and `Bash` rows (2026-11-16). Retry the same call once after the
  next step; a second refusal follows "Stops".

Reviewed: one `standards:plan-reviewer` read (Opus 5.5 at `medium`), folded. See "Review".

Evidence: the "Mechanisms" table, the seven recorded searches under "Searches", and the planner's
reader pre-runs under "Acceptance".

## What changes

Four rule files in `claude/.claude/skills/pass-core/references/` and one data file. The exact text
is `docs/plans/2026-11-16-run-past-park.patch` beside this plan, which the planner proved under
the caps and through the reader checks (M1 to M5). Task 1 applies it as it stands.

- `round-run.md`. Standing answer 5 drops "The pass parks too and never launches." and says a
  pass whose "Depends on" entry is marked `(order)` runs past its parked parent as `conductor.md`
  "Run" says, while an unmarked entry builds on it and that pass waits. Answer 1 launches "the
  next pass `conductor.md` "Run" names", so the two files pick the same pass. The line under "The
  order table" says "builds on" where it said "depends on". The opening's executor "merges no PR"
  in place of "merges nothing", since the new merge steps merge branches.
- `conductor.md` "Run". One new paragraph: on a stop, which pass launches, what its branch is cut
  from, and the two merge steps after Geoff answers. It replaces the old sentence "launches the
  next pass that doesn't wait for the parked one".
- `round.md`. The sentence counting `BACKLOG.md` and `docs/STATUS.md` as shared files says that
  sharing only those two, with none of the other pass's result used, makes the entry `2 (order)`,
  and that an unmarked entry builds on that pass. The entry "is marked, as in `2 (order)`", so
  the number reads as an example.
- `advisor.md` line 7 to 8: "parks every pass that depends on it" becomes "builds on it".
- `claude/.claude/tooling/retired-phrases.txt`: appends "parks too and never launches", with its
  ruling comment, as the supersession sweep rule asks (header of that file).

Trims that make room are listed under "Decisions", each with the file where its rule still stands.

## Mechanisms

| # | Mechanism | Probe or source | Result |
| --- | --- | --- | --- |
| M1 | Word caps | `bin/.local/bin/claude-context-budget` lines 28 to 36, `SKILL_CAPS`: `conductor.md 610`, `round.md 1500`, `round-run.md 1500`; counted by whole-file `wc -w` | Today: conductor 610, round 1499, round-run 1499. Patched copy: 610, 1499, 1493; `--skill-caps --root .` exit 0. `conductor.md` sits at its cap |
| M2 | Role loads | `claude-pass-load --check --root .` on a full copy of the worktree with the patch applied | Exit 0. Executor 8611, conductor 4640, planner 9618 |
| M3 | What a conductor reads | M2's conductor row: `CLAUDE.md`, `SKILL.md`, `conductor.md`, `round-run.md`. No `round.md` | The `(order)` meaning has to be readable from `round-run.md`, so answer 5 defines it |
| M4 | Retired-phrase scan | `scripts/check-claude-refs.py`, `scan_files`: `.md` and `.js` under `claude/.claude`, dated paths and `docs/record` excluded. Run on the patched copy | Exit 0. `grep -c "parks too and never launches"` on `round-run.md` prints 0 |
| M5 | Reader pre-runs | Five fresh `general-purpose` agents, `sonnet` at `medium`, each given only the staged files and a neutral prompt ("Acceptance") | Checks 2 to 5 pass on the patched text. Check 2 on today's files launched nothing |
| M6 | Gate legs | `scripts/check.sh` lines 205 to 208: `skill-caps` and `pass-loads` run when a skills file changes; `claude-refs` runs on any `claude/.claude/*.md` or the phrase list | The close gate runs all three |
| M7 | Patch applies | `git -C <worktree> apply --check docs/plans/2026-11-16-run-past-park.patch` at `8822220`; the four base files `cmp` equal to the worktree's | Applies cleanly |

## Searches

Each search ran on 2026-11-16. Old copies of these same files in this repo's other worktrees
(`.claude/worktrees/agent-a11fcc70215ad8976`, reached also through the `~/Projects/workstation`
symlink to `~/.dotfiles`) are dismissed in every row: they are not live.

- S1, the old rule, as `ready.md` "A retired form" sets out: `grep -rn "parks too and never
  launches"` in `~/.dotfiles/claude`, in each repo's `.claude/` and `skills/` under `~/Projects`,
  and in `~/Projects/initiatives`.
  - `~/.dotfiles/claude/.claude/skills/pass-core/references/round-run.md:23`: edit (Task 1).
  - `~/Projects/*/.claude` and `~/Projects/*/skills`, worktrees excluded: 0 hits.
  - The initiatives main checkout: 0 hits.
  - The initiatives worktree `unattended-rounds`: the approved design itself (lines 30, 89, 103),
    `specs/2026-11-11-unattended-rounds-design.md:142` (an approved design), and
    `plans/run-past-park-planning-prompt.txt:55` (this planner's own prompt). They stay as they
    are, and the PR names them.
  - Packet snapshots `ur-ws-close-1/snapshot/glw907-workstation-232.patch`,
    `ur-ws-close-2/snapshot/...-233.patch` and `-234.patch`, and
    `ur-ws-w5-stop/snapshot/...-233.patch`: historical copies of past PRs, dismissed.
- S2, `depend` in `pass-core`: `advisor.md:8` (edit), `advisor.md:112` (keep),
  `round-run.md:14` (edit), `round-run.md:32` (keep: answer 9's "Passes that depended on it
  follow in order" reads true under the new rule), `round-run.md:59` (edit), `round.md` lines 20,
  21, 23, 30, 33, 36, and 100 (keep, apart from the line 30 to 32 sentence).
- S3, `parked` and `parks` in `pass-core`: `conductor.md:38` (edit), `desk.md:29` and `:96`
  (keep), `advisor.md:7` (edit), `advisor.md:107` (keep), `round-run.md:23` (edit), `:51` and
  `:79` (keep; `:79` is trimmed, see "Decisions").
- S4, `shares a file` and `shared files`: `round.md:20` (keep) and `:30` to `:32` (edit);
  `approval-packet/references/model-close-packet.md:45`, a model of a past document, dismissed.
- S5, `answer 5` anywhere in `~/.dotfiles/claude`: 0 hits, so no cross-reference breaks.
- S6, `parent` as a whole word in `pass-core`: `advisor.md:117` (keep), `round.md:103` (keep),
  `round-run.md:23` (edit), `round-run.md:55` (keep; `conductor.md` names the run-ahead base).
- S7, `parent is parked` and `parks too` in `~/Projects/initiatives` `*.txt` and `*.md`: only the
  S1 hits. Conductor-prompt hits for `park` were `packet`. The `dubplate` cleanup conductor prompt
  (`dubplate-server/plans/2026-11-15-cleanup-conductor-prompt.txt`, line 9, the order table's
  "Depends on" header) is an approved prompt and stays; the desk delivers its ruling.

## Acceptance

Each item is copied verbatim from the design's "How the pass is checked". The planner ran items 1
to 5 on 2026-11-16 against the staged patched text and, for item 2, against today's text.

| # | Item | Task | Evidence the PR carries |
| --- | --- | --- | --- |
| 1 | `grep -c "parks too and never launches" claude/.claude/skills/pass-core/references/round-run.md` prints 0. Today it prints 1. | 1 | The command and its output |
| 2 | A fresh reader gets `conductor.md`, `round-run.md`, and an order table of four passes in which pass 3 depends on `2 (order)` and pass 4 depends on 2. Pass 1 has merged and pass 2 has just parked. The reader names pass 3 as the next launch, the default branch as its base, and pass 4 as waiting. Today's reader launched nothing. | 2 | Prompt A and the reader's answer |
| 3 | The same reader gets the same table with no `(order)` mark. It launches nothing. | 2 | Prompt B and the answer |
| 4 | The same reader is told that you answered pass 2's question while pass 3 was in flight. It finishes pass 3, relaunches pass 2 with the default branch merged in first, and has pass 3 take in pass 2's branch before a merge document goes. | 2 | Prompt C and the answer |
| 5 | A second fresh reader gets `round.md` and three passes with their file lists, where the second and third share only `BACKLOG.md`. It writes the third pass's dependence as `2 (order)`. | 2 | Prompt D and the answer |
| 6 | `claude-context-budget --skill-caps --root .` exits 0, so both files are within their word caps. | 3 | The command, its exit code, and `wc -w` of the three capped files |
| 7 | `bash scripts/gate.sh` and `claude-tooling-sync verify` pass. | 3 | Both commands and their last lines |

"The readers' answers go in the pull request." (design)

The planner's pre-run answers, kept for comparison with the executor's:

- Item 2 on today's files: "The conductor launches nothing." It quoted "A pass's parent is
  parked. The pass parks too and never launches." and said `(order)` "is not defined in my two
  files". Fails, as the design says.
- Item 2 on the folded patch: pass 3 "is the one launch", its worktree cut from `origin/main`;
  "Pass 4 waits. Its "Depends on" entry is an unmarked `2`, so it builds on pass 2."
- Item 3 on the folded patch, three fresh readers: two answered "The conductor launches nothing"
  from their first line. The first opened by naming a pass 3 launch and then concluded "launches
  nothing". The two clean reruns were sent because of that wobble.
- Item 4 on the folded patch: pass 2 "relaunches the pass once the one in flight finishes", its
  executor "merges `origin/main` first", and pass 3, if it hasn't merged, "gets a `## Rulings` line
  to merge in the resumed branch and rerun the gate, and relaunches before any `merge` document
  goes."
- Item 5 on the folded patch: pass 2 `1`, pass 3 `1, 2 (order)`.

### Reader prompts

Each prompt goes to its own fresh Agent call, `subagent_type: general-purpose`, `model: sonnet`,
`effort: medium`, with nothing else in it. `<R>` is the absolute path of a reader folder under
`$CLAUDE_JOB_DIR/tmp` that holds copies of the named files from the worktree after Task 1 and
nothing else. A rewrite of the rule gets new Agent calls, never a `SendMessage` to an old reader.

Prompt A (item 2). Prompt B is the same text with row 3's "Depends on" cell reading `2` in place
of `2 (order)`.

```
You are a conductor session in a round of passes. Read only these two files and nothing else on disk: <R>/conductor.md and <R>/round-run.md. Don't search for or open any other file. Where a rule names a file you don't have, say so and go on with what you have.

The repo's default branch is `main`. The conductor prompt's order table:

| Pass | Planner prompt | Depends on | Path minutes | Waits for Geoff |
| --- | --- | --- | --- | --- |
| 1 | plans/p1-prompt.txt | none | 60 | no |
| 2 | plans/p2-prompt.txt | 1 | 90 | no |
| 3 | plans/p3-prompt.txt | 2 (order) | 70 | no |
| 4 | plans/p4-prompt.txt | 2 | 50 | no |

State now: pass 1's PR has merged into `main`. Pass 2's executor has just stopped on a question only Geoff can answer: its branch's STATUS holds a `## Stop`, and its draft PR is open. Nothing else is running.

Say what the conductor does next. If it launches a pass, name the pass and the branch its worktree is cut from. Name each pass that waits, and why.

Quote the rule text you rely on for each step.
```

Prompt C (item 4), in full:

```
You are a conductor session in a round of passes. Read only these two files and nothing else on disk: <R>/conductor.md and <R>/round-run.md. Don't search for or open any other file. Where a rule names a file you don't have, say so and go on with what you have.

The repo's default branch is `main`. The conductor prompt's order table:

| Pass | Planner prompt | Depends on | Path minutes | Waits for Geoff |
| --- | --- | --- | --- | --- |
| 1 | plans/p1-prompt.txt | none | 60 | no |
| 2 | plans/p2-prompt.txt | 1 | 90 | no |
| 3 | plans/p3-prompt.txt | 2 (order) | 70 | no |
| 4 | plans/p4-prompt.txt | 2 | 50 | no |

State now: pass 1's PR has merged into `main`. Pass 2's executor has just stopped on a question only Geoff can answer: its branch's STATUS holds a `## Stop`, and its draft PR is open. Nothing else is running.

First say what the conductor does next. If it launches a pass, name the pass and the branch its worktree is cut from. Name each pass that waits.

Then: Geoff answers pass 2's `decide` document while the pass you launched (if any) is still in flight. List, in order, what the conductor and the executors do from that moment until a `merge` document goes to Geoff.

Quote the rule text you rely on for each step.
```

Prompt D (item 5), with `<R>` holding `round.md` alone:

```
You are a designing session writing a round design. Read only this file and nothing else on disk: <R>/round.md. Don't search for or open any other file. Where a rule names a file you don't have, say so and go on with what you have.

The round has three passes in one repo. Every pass edits `BACKLOG.md` to close its own item.

- Pass 1 adds a parser function in `lib/parse.ts` and its test `lib/parse.test.ts`, and edits `BACKLOG.md`.
- Pass 2 changes the CLI in `cli/main.ts` and `cli/main.test.ts` to call the parser that pass 1 adds, and edits `BACKLOG.md`.
- Pass 3 changes the web view in `web/view.ts` and `web/view.test.ts` to call the parser that pass 1 adds, and edits `BACKLOG.md`. It uses nothing pass 2 makes.

Write the round's order table with its "Depends on" column filled in for each pass, exactly as you would put it in the design. Quote the rule text you rely on for each entry.
```

An answer passes when it says what the item says. Item 5 passes when pass 3's entry
for pass 2 reads `2 (order)`, and the entries for pass 1 in rows 2 and 3 carry no mark: both
passes use pass 1's parser. A reader that marks every entry fails.

## Tasks

The path is the sum, 70 minutes: the tasks run in sequence.

### Task 1: apply the rule text (15 min)

Outcome: the five files carry the patch's text. Files: the four references and
`claude/.claude/tooling/retired-phrases.txt`. Class `runner`.

Run `git apply docs/plans/2026-11-16-run-past-park.patch` from the worktree root. If it doesn't
apply, `main` moved under one of the files: follow "Stops". Then run
`bash scripts/gate.sh --scope-changed` bare, and item 1's grep. Commit the five files by path, with
`git commit` alone, a subject such as "Let a round run past a parked pass", and a body that cites
<https://code.claude.com/docs/en/features-overview> (the design's home decision). The plan, prompt,
and patch are already committed; leave them as they are.

Acceptance: item 1 prints 0, and the fast lane passes.

### Task 2: the reader checks (25 min)

Outcome: items 2 to 5 pass on the committed text. Class `runner`.

Stage the reader folders from the worktree's committed files, then send Prompts A, B, C, and D,
each in its own fresh Agent call, in one message. Copy each answer, or the part that settles the
item, into the PR body under `## Acceptance`.

A failed check is a wording problem. Rewrite the sentence the reader misread, inside the caps, and
send that prompt again in a new Agent call. Every other check is rerun as well if the rewrite
touched a sentence it reads. Two rewrites is the cap ("Stops"). Each rewrite gets a line in
`## Decisions` with the reader's misreading.

### Task 3: close (30 min)

Run `bash scripts/gate.sh` bare on the close head, then `claude-tooling-sync verify`, then one
`gitleaks git` scan of the branch history. Item 6: `bin/.local/bin/claude-context-budget
--skill-caps --root .` and `wc -w` of `conductor.md`, `round.md`, and `round-run.md`.

One whole-branch `standards:diff-reviewer` reads the branch against the design and this plan. One
batched fix chain follows, then the gate again. A second review runs only on a blocker.

Open the PR against `main` with `gh pr create`. Its body:

1. An opening paragraph per `written-for-people.md` steps 1 to 3: what approving it changes, in
   plain words. While a pass waits for Geoff's answer, its round launches the next pass that
   doesn't build on it, and a round design marks a dependence that is order alone as `2 (order)`.
2. What landed, file by file.
3. `## Decisions`: the lines under "Decisions" below, the `[advisor]` lines, and any Task 2
   rewrite.
4. `## Planning misses`: the line under "Planning misses" below.
5. `## Acceptance`: every item verbatim with its evidence, the readers' answers included.
6. The S1 hits that stay: the approved design, the 2026-11-11 initiative design, and the
   planner's prompt, each named, with the reason it stays.
7. The evidence lines `Pass: run-past-park`, `Review: <verdict>, open findings <n>`, and
   `Calls: none` or `Calls: <n>` with each call under `## Calls for Geoff`. No `Round:` line.
8. The attribution line.

Land per `approval-packet` step 1. With `Calls: none`, an `accept` review, no open finding, and no
`## Before merge`, run `approval-queue land glw907/workstation#<n> "<one sentence on what it
does>"` in the background. Otherwise send one `merge` document through `approval-packet`, all four
steps of `written-for-people.md`. After the land, or Geoff's approve and `approval-queue merge
<id>`, in this order:

1. `ExitWorktree` with `action: "keep"`. The worktree was entered by path, so the tool won't
   remove it.
2. `git -C /var/home/glw907/.dotfiles pull --ff-only`, under the "Close" conditions in
   `pass-core`.
3. `grep -c "parks too and never launches"
   /var/home/glw907/.dotfiles/claude/.claude/skills/pass-core/references/round-run.md` prints 0:
   the rule is live.
4. `git -C /var/home/glw907/.dotfiles worktree remove .claude/worktrees/run-past-park`, then
   `git -C /var/home/glw907/.dotfiles branch -d run-past-park`, each alone, no force flag.

No `stow` or `claude-tooling-sync apply` runs: the pass adds no script and doesn't touch
`settings.json`.

## Stops

Each stop has a standing answer; any other open question goes through `advisor.md`.

- The path passes 150 minutes: the pass parks and asks Geoff (design).
- `git apply` fails at Task 1: `main` moved under a rule file. Fetch, merge `origin/main` into the
  branch, and apply the patch's intent by hand with `Edit`, hunk by hunk. Rerun M1 and Task 2 on
  the result, and say so under `## Decisions`.
- The new wording can't fit under a word cap without dropping a rule. The design's answer, "moves
  the new text into `conductor.md`, which has no cap", rests on a false fact: `conductor.md` is
  capped at 610 (M1). The replacement answer: trim only a sentence whose rule still stands in a
  file the same role loads, name it under `## Decisions`, and never raise a cap, because the caps
  live in a script this pass doesn't edit. If no such trim exists, the pass parks with the word
  counts as the question (`round-run.md` "Stops").
- A reader check fails after two rewrites of the rule: the pass parks with the reader's answer as
  the question (design).
- A task needs a setting, hook, or permission rule changed: the pass doesn't do it (`round-run.md`
  standing answer 3).
- `claude stop` or `git commit` is refused: don't retry the same shape. Run it alone if it was
  chained; a second refusal follows `round-run.md` standing answer 2.
- The gate fails on a leg this pass didn't touch: trace it. A cause outside the pass's files is
  filed through `standards:log-issue` and named in the PR, and the pass goes on once the same leg
  fails on `origin/main` in a scratch copy under `$CLAUDE_JOB_DIR/tmp`.
- `git -C /var/home/glw907/.dotfiles ...` is refused after `ExitWorktree`: report the checkout as
  stale, per `pass-core` "Close", and don't retry.

## Decisions

Trims. Each sentence left its file only because the same rule stands in another file the same
role loads (M2 lists the loads).

- `conductor.md`: "A round of two or more passes has a conductor." It stands in `SKILL.md` line
  108, which the conductor loads.
- `conductor.md`: "The conductor launches each pass's planner (`round-run.md` "The order table")"
  became "Each pass's planner launches its executor." The planner launch stands in `round-run.md`
  "The order table", "Launch the pass's planner from its committed prompt."
- `conductor.md`: "Its first step checks its own row in `claude agents --json` and stops if the
  name is not `conductor-<project>`." became one shorter sentence with the same check.
- `conductor.md`: "An executor takes its conductor's messages as instructions (Geoff,
  2026-10-20)." The rule binds the executor and stands in `executor.md` line 31, with its date.
- `conductor.md`: the busy-check sentence and "It also runs the planner reference's launch
  checks" became "Each launch follows the planner reference's "Launch"." The busy check stands in
  `round-run.md` "The order table" and standing answer 6. The `state.json` sentence stays, three
  words shorter, because the conductor doesn't load `planner.md` (review finding 2).
- `conductor.md`: "in the queue" left "A message never stands in for Geoff's approve in the
  queue". The rule stands in `SKILL.md` line 123, "A PR merges only through the queue: on Geoff's
  approve, or by a landing step 1 allows", which the conductor loads.
- `conductor.md`: "On a stop ... After Geoff answers, it follows standing answer 9 there." moved
  into the new paragraph, which keeps both rules.
- `round-run.md`: the queue-rules bullet "A stop goes to Geoff as a `decide` document. A parked
  pass with no PR opens a draft holding the stop, which the conductor reads." Answer 1 sends the
  `decide` document, "Stops" opens the draft PR, and "Reading a pass" parks on a plan-only draft.
- `round-run.md`: "goes on with the rest" became "goes on" in answer 2.
- `round.md`: "A conductor and an executor read `references/round-run.md` in its place." It
  stands in `SKILL.md` line 23, which the planner loads.
- `round.md`: "The design and planner seats take the models `SKILL.md` "Models" names." The seats
  stand in `SKILL.md` "Models".
- `round.md`: "The `Evidence:` line of `## Pre-flight` names the mechanism table and the recorded
  searches." It stands in `planner.md` line 52.

Other calls:

- The `round.md` bullets for the pass table and the order table aren't edited. The sentence the
  patch changes sits under the order rules both tables follow, and the item 5 reader wrote the mark
  from it.

- `round-run.md` line 59 now reads "A pass that builds on another starts once that pass's PR is
  ready". A run-ahead pass is launched by `conductor.md` "Run", so the line needs no exception.
- `advisor.md` lines 7 to 8 change "depends on" to "builds on", so its reason for consulting the
  advisor matches the new rule. A method call within the design's scope.
- The phrase list gets "parks too and never launches", as its header's supersession sweep rule
  asks. It is a check's data file, not the check.
- The `(order)` meaning is defined in `round-run.md` answer 5 as well as `round.md`, because a
  conductor never loads `round.md` (M3).
- The two merge steps travel as `## Rulings` lines and an executor relaunch, as standing answer 9
  already does. `executor.md` is unchanged.
- `[advisor]` The cap on `conductor.md` stays at 610. Raising it would edit a script and falls
  under "What always stops".

## Planning misses

- `[stale-fact]` The design's second stop says `conductor.md` "has no cap". It is capped at 610 in
  `claude-context-budget` `SKILL_CAPS` and held 610 words. The planner wrote the replacement
  answer under "Stops" and proved the fit (M1).

## Review

One `standards:plan-reviewer` read, Opus 5.5 at `medium`, on 2026-11-16. Eight findings, all
folded:

1. Blocker: the plan, prompt, and patch were untracked. The planner commits them before launch.
2. The conductor lost its `state.json` check. The sentence stays ("Decisions").
3. Item 5's bar passed a reader that marks every entry. The bar now checks the unmarked entries.
4. Answer 1 and `conductor.md` "Run" picked the next pass differently. Answer 1 now points to
   "Run".
5. `round-run.md` line 7 said an executor "merges nothing". It now says "merges no PR".
6. The `round.md` sentence read as if every entry were `2 (order)`. It now says "is marked, as
   in".
7. Prompt C is written out in full.
8. Pre-flight is cut to the refused shapes that touch this pass.

The planner reran M1, M2, M4, M7, both load and budget test suites, and the four reader checks
on the folded text, with item 3 run three times. A grep of `tests`, `scripts`, `bin`, and both
skill trees for "merges nothing", "doesn't build on it", and "approve in the queue" found only
the approval-packet lines about a stop packet's approve, a different rule.

## Later

- Running a pass that does build on the parked one, and redoing it if the answer changes its
  ground (design, "What is left out").
