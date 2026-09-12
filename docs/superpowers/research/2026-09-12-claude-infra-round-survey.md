# Claude infra round: the cross-project survey and the scope ruling

Date: 2026-09-12. Author: the dubplate conductor, from one Explore read across the ten
project repos and the workstation layer. Geoff's direction (2026-09-12): the scope of a
workstation-versus-project change is decided by examining the other projects the
workstation manages, and the survey is the context for that decision.

## The ruling

**The round is the workstation layer, sized to what recurs.** An item lands in this round
when it has two or more consumers today, or when its only home is a workstation file that
the dubplate window proved stale. An item with one consumer stays in its repo and is
recorded here as a note for that repo's next pass.

**In scope, in priority order:**

1. **The gate runner's reattach protocol in every implementer that uses it.**
   `cairn-run-gate` now exits 75 with "gate still running" and expects the caller to
   re-issue the same command. `site-implementer.md` and dubplate's
   `dubplate-implementer.md` still say the runner "blocks to completion". The wording
   already drafted in `cairn-implementer.md`'s uncommitted working-tree diff is the
   template. **`cairn-implementer.md` itself is off-limits**: the cairn overnight session
   (workflow `wf_2d52758e-603`, live at survey time) authored that diff at 04:50 and
   owns its commit. poplar's implementer runs `make check` directly and is a note only.
2. **The unattended-work guards doc**, `claude/.claude/docs/unattended-work-guards.md`:
   two of its instructions are now wrong. The runaway guard must read each workflow's
   `journal.jsonl` for completed agents, or every finished chain agent reads as a stall
   (the doc says to ignore the journal). The battery layer must gate on
   `/sys/class/power_supply/AC*/online`, because the battery reports "Not charging" on AC
   under the charge threshold (the doc gates on `BAT*/status`).
3. **`pass-execute.js` and its skill text.** Two consumers (dubplate, cairn-cms). The
   window's findings: the runner has no mid-run conductor hook, so a pass with conductor
   boundaries is launched one segment per invocation; every gate string is absolute per
   tree; and the protocol block every task needs is pasted into every task's `notes`
   because the script has no one field it appends at prompt time (`pass-execute-chains.js`
   has one). The round decides what of this is a script change (a shared-notes argument
   appended to every prompt) and what is skill text (the segment launch shape).
4. **The global `CLAUDE.md` budget.** `claude/.claude/CLAUDE.md` is 27,807 bytes
   against `claude-context-budget`'s 24,000-byte cap, before the four docs-standard
   lines it still owes. The ranked displacement candidates are already measured at
   `docs/superpowers/plans/2026-09-08-claude-md-displacement-candidates.md`. The round
   displaces to pointers and lands the four lines, ending under the cap; it does not
   raise the cap. `cairn-cms/CLAUDE.md` (24,873 bytes) is over too and owes its own four
   lines; that is cairn's repo and a live session holds it, so the round records it as a
   handoff and edits nothing there.
5. **Duplicated site assets hoisted to the workstation.** `907-life` and `ecxc-ski`
   carry a byte-identical `.claude/skills/svelte-check/SKILL.md` and near-identical
   `.claude/instructions/ai-operational-rules.md` and `documentation-standards.md`. The
   round hoists each to one workstation home with a repo pointer where a pointer is
   needed, after reading whether the diverging lines are repo-specific facts or drift.
   The `ship` skill (aksailingclub-legacy, ecxc-ski) has diverged in substance and is a
   note, not a task.
6. **`go-architecture-reader` to the workstation agents.** Two Go repos (dubplate,
   poplar); the agent grades a package with no plan in context and names nothing
   dubplate-specific beyond its stdlib comparator, which the dispatch names. Hoist with
   dubplate's copy retired to the shared one.
7. **The three items carried from the 2026-09-04 Fable 5.1 pass** that
   `docs/STATUS.md` says the docs-standard sitting still owes. The drafter reads
   `docs/HISTORY.md`'s 2026-09-04 entry, names them, and includes each that is a
   workstation edit.

**Out of scope, recorded for the repo that owns each:**

- dubplate's `check.sh` forms (`--scope-changed`, `--reduced`, `--merge`) and the two
  staged legs (`CHECK_CITATIONS`, `CHECK_EXPORTED_UNUSED`): one consumer. poplar is the
  plausible second for the two legs and adopts them in its own pass if it wants them.
- dubplate's `simplifier-brief.md` and `tools/close-evidence`: one consumer each.
- `STATUS.md` over the 60-line cap in six repos (907-life 236, cairn-pub 183, ecxc-ski
  173, cairn-cms 100, xcathletes-org 69, aksailingclub-org 68): the ledger rule already
  makes the move a close-out chore in each repo.
- poplar has no `docs/STATUS.md`, `HISTORY.md`, or `ROADMAP.md`: poplar's own chore.

## Constraints on execution

- **A cairn session is live** and writes into the stow source through the `~/.claude`
  symlinks. This round never touches `cairn-implementer.md`, never runs `git add -A` in
  `~/.dotfiles`, and commits specific files only. The round's tasks and the cairn
  session's one warm file are disjoint by construction.
- **Executor precedent** is the 2026-09-08 docs-standard infra plan (`:112-118`): the
  dotfiles repo has no repo-specific implementer, so the implementer is `general-purpose`
  at `sonnet`, the reviewer is `diff-reviewer`, and the gate is `bash scripts/check.sh`
  in `~/.dotfiles` run through `cairn-run-gate`. Below six tasks the chain runs per task
  through the Agent tool; at six or more, through `pass-execute` (whose own edit, if the
  round makes one, lands in a task that runs before any task depends on it, or the
  script edit is the last task).
- Stow: a new file under `claude/.claude/` appears in `~/.claude/` only after
  `stow -R claude`; a task that adds a file runs it and verifies the symlink.
- The dubplate repo is touched by exactly one file, `.claude/agents/dubplate-implementer.md`
  (item 1), and by the retirement of `.claude/agents/go-architecture-reader.md` (item 6).
  No dubplate executor is live; 5b-ii has not launched.

## The survey, verbatim

# Process-Improvement Survey: dubplate-born items across the estate

## 1. Implementer agents (gate-running, pre-flight, report block)

| File | Gate step wording | exit-75 reattach protocol | Pre-flight checklist | Labeled report block |
|---|---|---|---|---|
| `~/.dotfiles/claude/.claude/agents/cairn-implementer.md` (**uncommitted** working-tree diff) | "Run the gate string only through `cairn-run-gate`... exit 75... re-issue" | **Yes** (only in the uncommitted diff; committed HEAD still says "blocks to completion") | Yes ("Pre-flight checklist (Geoff, 2026-09-09)") | Yes ("Report format") |
| `~/.dotfiles/claude/.claude/agents/site-implementer.md` | "blocks to completion and prints the exit status" | No | Yes (same heading/date) | Yes |
| `~/Projects/dubplate/.claude/agents/dubplate-implementer.md` | "The runner blocks to completion and prints the exit status" | No | Yes ("Pre-flight before you report") | Yes ("Gate:" line + "Report format") |
| `~/Projects/poplar/.claude/agents/poplar-implementer.md` | Runs `make check` directly, no `cairn-run-gate` at all | N/A (doesn't use the runner) | No dedicated pre-flight section | Yes ("Report format") |

Near-duplicate: cairn-implementer.md and site-implementer.md share the "Pre-flight checklist (Geoff, 2026-09-09)" heading and body verbatim except for domain nouns; dubplate-implementer.md has the same concept under a different heading name and citation-specific bullets. The exit-75 wording exists only in `~/.dotfiles` uncommitted diff; site-implementer.md, dubplate-implementer.md, and poplar-implementer.md all lack it.
Verdict: **SHARED-CANDIDATE**.

## 2. Repo gates

| Repo | Gate mechanism | Scoped/reduced/merge forms | Staged warn-then-fail legs |
|---|---|---|---|
| dubplate | `scripts/check.sh` | Yes: `--scope-changed`, `--reduced`, `--merge` | Yes: `CHECK_CITATIONS`, `CHECK_EXPORTED_UNUSED` (default warn) |
| pings | `scripts/check.sh` (25 lines: shellcheck, tsc, vitest, bats, dry-run deploy) | No | No |
| cairn-cms | `package.json` scripts (`lint`, `check`, `test`) | No | No |
| poplar | `Makefile` (`make check`: build, tidy-check, lint, analyzers, vale-comments, skipcheck, conformance, etc.) | No | No |
| 907-life, aksailingclub-org, ecxc-ski, xcathletes-org | `package.json` `check`/`test` (svelte-check/vitest) | No | No |

Verdict: **REPO-LOCAL** today; poplar is a plausible second consumer for the citation and exported-unused legs.

## 3. simplifier-brief

Exists only at `~/Projects/dubplate/.claude/instructions/simplifier-brief.md`. Verdict: **REPO-LOCAL**.

## 4. go-architecture-reader

Exists only at `~/Projects/dubplate/.claude/agents/go-architecture-reader.md`. poplar is Go and has no such agent. Verdict: **SHARED-CANDIDATE**.

## 5. close-evidence

`~/Projects/dubplate/tools/close-evidence/main.go`; no counterpart elsewhere. Verdict: **REPO-LOCAL**.

## 6. pass-execute workflows

`~/.dotfiles/claude/.claude/workflows/pass-execute.js` and `pass-execute-chains.js`, used by dubplate and cairn-cms. The segment gap (no mid-run conductor hook, so passes launch as segments) is recorded only in dubplate's HISTORY and memory. Verdict: workflow **SHARED-ALREADY**; the segment finding **SHARED-CANDIDATE**.

## 7. Unattended-work guards versus what the window learned

`claude/.claude/docs/unattended-work-guards.md` says to poll `agent-*.jsonl` and to disregard `journal.jsonl`, and gates battery on `BAT*/{capacity,status}`. dubplate's window learned the opposite on both. Verdict: **SHARED-CANDIDATE** (stale workstation doc).

## 8. Project ledgers

| Repo | STATUS.md | lines | HISTORY.md | ROADMAP.md |
|---|---|---|---|---|
| 907-life | yes | 236 | no | yes |
| aksailingclub-legacy | no | – | no | yes |
| aksailingclub-org | yes | 68 | yes | yes |
| cairn-cms | yes | 100 | yes | yes |
| cairn-pub | yes | 183 | no | no |
| dubplate | yes | 59 | yes | yes |
| ecxc-ski | yes | 173 | no | yes |
| pings | yes | 49 | yes | no |
| poplar | no | – | no | no |
| xcathletes-org | yes | 69 | yes | yes |

## 9. CLAUDE.md sizes against the 24,000-byte cap

| File | Bytes | Over cap? |
|---|---|---|
| `~/.claude/CLAUDE.md` | 27,807 | **yes** |
| cairn-cms/CLAUDE.md | 24,873 | **yes** |
| dubplate/CLAUDE.md | 12,889 | no |
| aksailingclub-org/CLAUDE.md | 16,568 | no |
| aksailingclub-legacy/CLAUDE.md | 10,322 | no |
| 907-life/CLAUDE.md | 9,597 | no |
| ecxc-ski/CLAUDE.md | 5,432 | no |
| xcathletes-org/CLAUDE.md | 5,202 | no |
| poplar/CLAUDE.md | 3,899 | no |
| cairn-pub, pings | no CLAUDE.md | n/a |

## 10. Repo-local assets that duplicate another

- `907-life/.claude/instructions/ai-operational-rules.md` and `ecxc-ski`'s: same file, one repo-specific deploy command differs.
- `907-life/.claude/instructions/documentation-standards.md` and `ecxc-ski`'s: same file, wrapping differs.
- `907-life/.claude/skills/svelte-check/SKILL.md` and `ecxc-ski`'s: byte-identical.
- `aksailingclub-legacy/.claude/skills/ship/SKILL.md` and `ecxc-ski`'s: same name, diverged bodies.
- `poplar/.claude/skills/simplify/SKILL.md`: a deliberate Go-aware specialization of the workstation skill.
