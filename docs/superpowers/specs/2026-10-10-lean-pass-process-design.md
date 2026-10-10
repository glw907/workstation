# Lean pass process: design

Approved in chat by Geoff, 2026-10-10, section by section. This spec replaces the pass machinery in
every repo on the workstation (cairn-cms, the five sites, dubplate; poplar keeps its own skills).
It supersedes the parked clock-time design
(`~/Projects/cairn-cms/docs/superpowers/specs/2026-10-10-pass-clock-time-design.md`), which stays as
evidence of the ratchet.

## Goal

Cut the pass process to what earns its cost. The base standard is Anthropic's current published
guidance for agentic development with Claude Code, sized for a solo developer with small repos. A
home-grown step stays only where the catch ledger shows it caught a defect that no later step would
have, at a clock and token price worth paying.

## Evidence

- Anthropic guidance, quotes verified against the pages on 2026-10-10:
  `docs/superpowers/research/2026-10-10-anthropic-agentic-guidance.md`.
- Catch ledger over gate economy, engine pass A, stage 2a, pass 1b, and theme identity:
  `docs/superpowers/research/2026-10-10-pass-catch-ledger.md`.
- Clock evidence from pass B's stopped S1 run, and Fable's critique of the parked design:
  `~/Projects/cairn-cms/docs/superpowers/research/2026-10-10-pass-clock-time-evidence.md`,
  `~/Projects/cairn-cms/docs/superpowers/research/2026-10-10-pass-clock-time-review-fable.md`.
- Prior art for gates and shared capacity:
  `~/Projects/cairn-cms/docs/superpowers/research/2026-10-10-pass-clock-time-prior-art.md`.

## Rulings (Geoff, 2026-10-10)

1. Scope is the whole lifecycle, from brainstorm to close.
2. Zero-based: start from Anthropic's baseline and add a current step back only on its catch record.
3. Behavioral, security, and contract defects are caught before merge. Wording and cosmetic defects
   may land on `main` and are fixed forward.
4. Geoff's touchpoints are the design in chat and the PR. He never needs to read a plan or a spec.
5. One cutover across every repo, no pilot. Anthropic's practice is presumed better than the
   home-grown one.
6. Both the global and the cairn CLAUDE.md are rewritten to 200 lines or fewer.
7. `docs-page-chain` falls under the same rule: deterministic checks stay, and each model-judged seat
   keeps its place only on its catch record.
8. Written state is STATUS and ROADMAP, with git and PR bodies as history. HISTORY and per-plan
   post-mortems stop growing. A lesson lands where it executes. The friction log stays in cairn only.
9. Planning may spend more time and tokens when that produces a better result.
10. Carried from earlier the same day: independent items run in pairs by default; projects coordinate
    shared resources; the posture is workstation-wide; adopt the published method for each
    sub-problem and invent nothing already solved.

## Departures from the base standard

Two departures, each with its evidence.

- **Multi-lens spec review.** Anthropic publishes nothing for or against it. It stays because spec
  review produced 19 blocker-level catches across five passes, 6 of 11 audited ones unique, at 37 to
  45 minutes of wall clock and no attended time (catch ledger, S1), and because ruling 9 welcomes
  planning spend.
- **Reviewer subagents.** The Sonnet 5.5 prompting page says "don't launch reviewer sub-agents unless
  the user asked for a review." The process makes that ask in two places only: per task on `auth-data`
  work, and once over the whole branch at close. The per-task read caught two fail-open auth blockers,
  and the close seats had 11 of 12 audited catches unique (catch ledger, S3 and S6).

## Lifecycle

Every pass declares one risk class in its design: `auth-data`, `runner` (process or tooling
mechanism), `unattended`, or `ordinary`. Each repo's adapter skill maps paths to classes.

1. **Design.** Opus 5.5 at `high` brainstorms in chat. Geoff approves a design of a page or less: the
   outcome, the files and interfaces touched, what is out of scope, one end-to-end check, and the
   risk class. If the diff fits in one sentence, the work skips steps 2 to 4 (Anthropic best practices:
   "If you could describe the diff in one sentence, skip the plan").
2. **Spec.** An agent writes the approved design as a spec, at whatever length precision needs. Every
   mechanism the spec states is quoted from source or probed, never recalled.
3. **Spec review.** Three Opus lenses run in parallel: contract, mechanics, and risk. A fold follows,
   and it probes every new mechanism it introduces; the catch ledger found that 8 verification majors
   were mechanisms a fold stated from memory. One verification read closes the step. A finding that
   changes the approved design returns to Geoff as one batched question; every other finding is
   folded without him. The consistency and prose lenses are retired; Vale and `tellgrader` cover prose.
4. **Plan.** A task list. Each task carries its outcome, files, acceptance check, test, and a clock
   estimate, and never implementation code. Independent tasks are marked as pairs. One review lens runs
   by default; three run for `auth-data`, `runner`, and `unattended` passes.
5. **Execute.** See the next section.
6. **Close.** CI green on the head; one whole-branch Opus review whose domain checklists load by the
   paths the diff touched (Svelte, Workers, auth, DaisyUI and accessibility, Go); one batched fix
   chain; the auth smoke on `auth-data` passes; STATUS and ROADMAP updated; a PR body that carries what
   landed and a one-line score of clock, tokens, and attended time. Geoff reads the PR and merges.

Retired from today's lifecycle: the conductor, the simplifier as a standing step, the local full gate,
HISTORY entries, post-mortems, the close fold and its review, token ceilings, checkpoint STATUS writes,
and pass segmenting.

## Execution

1. **One session executes.** A fresh Sonnet 5.5 session runs the plan task by task. It reads, edits,
   writes the tests, and commits (Anthropic: "an agent handling a feature should also handle its
   tests"). Tasks marked as a pair go to two subagents with worktree isolation through the Agent tool.
2. **A fast inner gate.** Each repo's adapter emits a fast lane per task: the type check, the selected
   unit and component tests, the static checks the diff touches, and the docs gate when docs changed.
   The lane's legs run concurrently. It takes the machine-wide heavy lock only when the task's
   acceptance check names an e2e spec.
3. **CI carries the whole suites, off the critical path.** The task pushes and the next task starts.
   A CI red stops the line: the session fixes forward in the next commit or reverts.
4. **Review beside CI.** On `auth-data` tasks an Opus diff review reads the commit while CI runs.
5. **A clock stop.** A task past twice its estimate stops and reports to STATUS, so a strategic miss
   surfaces in minutes.
6. **`cairn-run-gate` fixes.** It reprints a finished result to a repeat call, rejects an unknown flag
   instead of queuing it as a gate, returns before the harness's 600-second tool cap, and gains a
   `defer` exit and the fast-lane mode.

Pass B priced on the evidence (11 tasks, minutes):

| Row | Today | Lean |
|---|---|---|
| Gates on the critical path | 203 plus 44 lock wait | 55 to 90 |
| Work and review | 220 | 130 to 170 |
| CI waits on the path | 46 to 252 | 0 to 25 |
| Fix rounds and reds | 0 to 93 | 40 to 90 |
| Close | 217 | 90 to 150 |
| Total | 11.4 to 17.2 h | 5.2 to 8.8 h |

The per-task fix rate of 45% came from per-task review, so most of those catches move to the
whole-branch review, and the close budget is sized for that. The local full gate caught 0 of 7
unique reds in the record, so moving it to CI costs an 11-minute CI cycle per red.

## Instruction surface

A sentence stays only if it changes what the model would otherwise do (harness-design post: strip
what is "no longer load-bearing"). Caps: CLAUDE.md under 200 lines (memory docs), a skill body under
500 (skill authoring best practices).

| File | Fate |
|---|---|
| Global `CLAUDE.md` (301 lines) | Rewrite to 200 or fewer. Pass, gate, sizing, conductor, model-seat, and ledger sections leave for `pass-core`. |
| cairn `CLAUDE.md` (335) | Rewrite to 200 or fewer. Charter, docs tracks, releases, admin design, and gotchas stay as short pointers. |
| `pass-core` (312) | Rewrite to about 120: the lifecycle, execution, risk classes, and the clock stop. |
| `cairn-pass` (170), `site-pass` (65) | Rewrite as thin adapters: gate command, fast lane, risk-class path map, close checklists. |
| `spec-plan-review` (169) | Rewrite to the three spec lenses, the probing fold, the verification read, and risk-scaled plan review. |
| `pass-execute.js` (1,265), `pass-execute-chains.js` (931) | Delete. |
| `cairn-implementer` (173), `site-implementer` (155) | Trim to pair-subagent definitions; drop the chain report shape and gate protocol. |
| `diff-reviewer` (91) | Keep, for the `auth-data` read and the close read. |
| Four domain reviewers | Keep as files; the close review loads them as checklists. |
| `code-simplifier` | Remove from the process; the plugin stays for on-request use. |
| `docs-page-chain.js` (2,025) | Keep the deterministic gates; audit each model seat (rollout step 4). |
| `model-economy.md`, `pass-gate-economy.md`, `unattended-work-guards.md` | Fold what still executes into `pass-core` or `cairn-run-gate`; delete the rest. |
| `cairn-run-gate` | Keep, with the fixes in Execution item 6. |
| cairn `gate-tier.mjs` and CI | Add the fast lane with concurrent legs; shard the CI e2e job. |

## Rollout

The cutover runs on the new process from its first task. Its sessions launch in `~/.dotfiles`, the
canonical path for the workstation repo (`~/Projects/workstation` is a convenience link).

1. **Workstation repo.** Rewrite the global `CLAUDE.md`, `pass-core`, and `spec-plan-review`. Delete
   the two runners and fold the three process docs. Land the `cairn-run-gate` fixes. Trim the
   implementers. Sweep every skill and agent that names a deleted file, and keep
   `claude-tooling-sync verify` green.
2. **cairn-cms.** Rewrite its `CLAUDE.md` and `cairn-pass`, add the fast lane to `gate-tier.mjs`, and
   shard the CI e2e job, on a cairn branch merged by PR.
3. **Site repos and dubplate.** Rewrite `site-pass` as an adapter, sweep references to deleted
   machinery, and check each repo's CLAUDE.md against the 200-line cap.
4. **Docs-chain audit.** Score each model seat in `docs-page-chain` against the catch-ledger test
   before docs stage 2b starts, and cut the seats that fail.
5. **Pass B resumes** as the first scored pass on the new process. Its unreviewed WIP for Tasks 1 and
   2 (`dbdc4556` in `.claude/worktrees/engine-pre-2b-b`) is re-gated through the fast lane.

## Success test

Pass B lands in 9 hours or less of clock, with no behavioral, security, or contract escape found after
merge, and Geoff's attended time stays at the design and the PR read. On a miss, the PR's score names
the row that missed, and only that row changes.
