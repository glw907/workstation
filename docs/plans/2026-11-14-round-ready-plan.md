# Round ready plan: a round is ready to run before its design reaches Geoff

Initiative: none applies (a workstation process rule; the evidence is
`~/Projects/initiatives/cairn-setup/research/tui-language-round-log.md`).
Design: `docs/specs/2026-11-14-round-ready-design.md`, approved by Geoff in the Approval Queue on
2026-11-14 (document `20261114-183833-107bf3`). His answer to its one question: "Send it, and say
so first", so rule 2 goes in as the design words it.

A one-pass round: no conductor, no order table, no round id. Class `runner`
(`claude/.claude/skills/**`, `bin/.local/bin/claude-context-budget`, `claude-pass-load`, and
`tests/**` are on the adapter's `runner` list). Worktree `~/.dotfiles/.claude/worktrees/round-ready`,
branch `round-ready`, cut from `origin/main` at `9d1420c`. Push target `glw907/workstation`, PR base
`main`. The executor is the interactive session that wrote the design, so nothing launches. The
design gives 45 path minutes; this plan's path is 65, under the 90 that would return it to Geoff.

## Pre-flight

Geoff has no step before or during this pass: no sign-in, secret, dialog, or permission rule.

Permissions checked: read `~/.local/state/claude-denials.jsonl`, 66 rows from 2026-11-01 to
2026-11-14. Classes in it: Self-Modification 10 (every row a `settings.json` edit or a `stow -R
claude`), Interfere With Workloads 9, classifier unavailable or unjudged 16, Merge Without Review 3
(bare `gh pr merge` or a merge-shaped `gh pr` read), Auto-Mode Bypass 3, Destructive or Unwanted
Actions 3, and six classes of 2 or fewer (local destruction, destructive git, public surface,
deletion scope, source provenance). This pass edits no `settings.json`, runs no `stow`, stops no
session, and merges only through `approval-queue land`. No task's command falls in a refused class,
so no alternative is needed.
Reviewed: one `standards:plan-reviewer` read before code (class `runner`); its verdict is recorded
under "Review" below.
Evidence: the mechanism table and the "Searches" list below.

## Mechanism table

| Mechanism | Probe or source |
| --- | --- |
| `round.md` and `planner.md` have word caps | `bin/.local/bin/claude-context-budget` lines 28 to 35: `round.md 1500`, `planner.md 940`. `wc -w` today: 1459 and 939. |
| The caps leave no room for the new section | The design's section is about 300 words; `round.md` has 41 spare and `planner.md` has 1. |
| A test pins four items under "Design rules" and "Planner rules" | `tests/claude-context-budget.test.sh` lines 127 and 128. |
| `claude-pass-load` lists each file a role loads and fails `--check` on an absent one | `bin/.local/bin/claude-pass-load` lines 25 to 50; its test builds each listed file (`tests/claude-pass-load.test.sh` lines 38 to 43). |
| A merged skill is live once the main checkout pulls | `.claude/skills/dotfiles-pass/SKILL.md`: "`~/.claude` and `~/.local/bin` link into the main checkout". |
| The launch guard reads no reference file | `grep -n "references/" bin/.local/bin/claude-launch-guard` prints nothing. |
| The round's files as first sent exist in git | `git -C ~/Projects/initiatives show 68bd8e1 --stat` lists the design's prompts; the conductor prompt at that commit has one `--round`. |
| The queue lands a PR with `land <owner/repo#n> <sentence>` | `approval-queue --help`, run 2026-11-14. |

## Searches

- `grep -rn "full sweep" claude/ .claude/ docs/*.md`: 1 hit, `planner.md` line 22. Edited in task 1.
- `grep -rn "four rules\|rules 2 and 3\|These four apply" claude/.claude/skills .claude/skills`: 6
  hits. Four are in `round.md` (lines 48, 65, 66, 70) and stay true, since neither list grows. One is
  the model close packet and one is Survey's approval brief; both are about other rules. Dismissed.
- `grep -rln "round.md\|planner.md" claude/.claude .claude tests scripts bin`: 13 files. The two
  tools and their two tests are edited in task 2. `SKILL.md`, `advisor.md`, `conductor.md`,
  `round-run.md`, `unattended-work-guards.md`, `written-for-people.md`, and the model close packet
  name the files and no content this pass moves. Dismissed.

## Decisions

- D-1. The "Ready to run" section goes in a new file, `pass-core/references/ready.md`, with a
  pointer from `round.md`, since the word cap leaves no room in `round.md`. The alternative was to
  raise the cap, which loads every planner with more words for a rule only a designer needs. The
  approved words are unchanged.
- D-2. The search rule and the full-sweep rule sit in `ready.md` too, each behind a pointer from
  the sentence the design named (`round.md` planner rule 2, `planner.md` "Design").
- D-3. `ready.md` gets a cap of 500 words and a row in the planner's load, so the tools that guard
  the pass skill's size see it.

## Planning misses

- `[mechanism]` The design named `round.md` as the section's home without reading the word caps.
  The plan's first probe found them. The design should have carried the `wc -w` figures.

## Acceptance

Copied from the design, each with its task and evidence.

1. "A fresh reader gets the changed rules and the terminal round's design and prompts as they stood
   on 2026-11-13, and nothing else. Asked what must change before the design is sent, it names all
   three faults: the start condition that is a merge, the copied queue commands, and the full sweep
   in the start. The reader's answer goes in the pull request." Task 3; the reader's answer.
2. "The same reader, given this design, finds the start line and the launch checks." Task 3; the
   reader's answer.
3. "`bash scripts/gate.sh` and `claude-tooling-sync verify` pass in the workstation repo." Close;
   both outputs.
4. "The launch guard is unchanged, so no prompt that launches today is refused." Close;
   `git diff origin/main --stat -- bin/.local/bin/claude-launch-guard` prints nothing.

## Tasks

1. **Write the rules** (`runner`, 25 min). Files: new `claude/.claude/skills/pass-core/references/ready.md`;
   `references/round.md`; `references/planner.md`. `ready.md` holds the design's four numbered rules
   under `## Ready to run`, the search rule under `## A retired form`, and the full-sweep rule under
   `## A due full sweep`. `round.md` gains a pointer to it, the builder check's third question in
   design rule 3, and a pointer in planner rule 2. `planner.md`'s full-sweep sentence points at it.
   Acceptance: `claude-context-budget --skill-caps --root .` exits 0, and
   `bash tests/claude-context-budget.test.sh` passes with both lists still at four.
2. **Teach the size tools the new file** (`runner`, 15 min). Files: `bin/.local/bin/claude-context-budget`
   (cap `pass-core/references/ready.md 500`), `bin/.local/bin/claude-pass-load` (planner row),
   `tests/claude-context-budget.test.sh` (the fixture loop, and a pin of four items under "Ready to
   run"), `tests/claude-pass-load.test.sh` (the fixture's file list). Acceptance: both test files
   pass, and `claude-pass-load --check --root .` exits 0. Test: the two test files.
3. **Run the fresh reader** (`runner`, 15 min). One Sonnet reader at `medium` gets the three changed
   rule files from this worktree and the design, conductor prompt, and start prompt from
   `initiatives` at `68bd8e1`, by path to a scratch copy, and the question in acceptance item 1; then
   this pass's design for item 2. A miss on any of the three faults is a red: fix the rule's words
   and rerun, twice at most, then stop as below.
4. **Close** (10 min). The gate, `claude-tooling-sync verify`, one `gitleaks git` scan of the
   branch, the whole-branch `standards:diff-reviewer`, a backlog item in the `standards` repo for
   its full-sweep sentence, an entry in the round log, the PR, and the landing.

Path: 25 + 15 + 15 + 10 = 65 minutes. No pairs: tasks 1 and 2 share the test files' expectations.

## Stops

- The reader still misses a fault after two rewordings. Standing answer: the PR waits for Geoff as
  a `merge` document that quotes the reader's answers, since acceptance item 1 can't be met as
  written.
- The closing review ends on `escalate`, or a second read is short of `accept`. Standing answer:
  the same `merge` document.
- The main checkout holds a live session at the landing. Standing answer: land, report the
  checkout as stale, and pull once the session has gone (`pass-core` "Close").

## Review

Pending.
