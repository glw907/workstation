# Lean pass process: design

Approved in chat by Geoff, 2026-10-10, section by section. This spec replaces the pass machinery in
every repo on the workstation (cairn-cms, the five sites, dubplate; poplar keeps its own skills).
It supersedes the parked clock-time design
(`~/Projects/cairn-cms/docs/superpowers/specs/2026-10-10-pass-clock-time-design.md`), which stays as
evidence of the ratchet. Revised after three lens reviews and Geoff's rulings 11 to 14; the fold
record is `docs/superpowers/research/2026-10-10-lean-pass-process-fold.md`.

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
11. Each repo's adapter names its full suite's home: CI where it runs tests on PRs, else one local
    full gate at close. PR test CI for dotfiles, dubplate, xcathletes-org, ecxc-ski, 907-life, and
    cairn-pub is filed on ROADMAP.
12. dubplate's rung 14a plan is held and re-planned as a lean task list in a fresh dubplate session
    after rollout steps 1 to 3 merge.
13. A clock stop writes STATUS, sends a normal-urgency desktop notification, and waits for Geoff. It
    counts as one attended event, not a success-test failure.
14. In the docs-chain audit, a register catch on a published docs page counts as a catch that keeps a
    model seat. Internal docs and specs stay under ruling 3.

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

Each task takes a risk class (`auth-data`, `runner`, or `ordinary`) from the adapter's path map;
`runner` covers skills, agents, workflows, the gate tools, `.github/workflows`, and `scripts/checks`.
The design's class is a floor, and a pass takes its highest task's class. A `live-account` flag marks
a run that can touch a real Cloudflare, GitHub, or npm account (catch ledger S2 item 3). Effort is
medium unless stated (guidance file, section 7).

1. **Design.** Opus 5.5 at `high` brainstorms in chat. Geoff approves a design of a page or less: the
   outcome, the files and interfaces touched, what is out of scope, one end-to-end check, and the
   risk class. If the diff fits in one sentence, the work skips steps 2 to 4 (Anthropic best practices:
   "If you could describe the diff in one sentence, skip the plan").
2. **Spec.** An agent writes the approved design as a spec, at whatever length precision needs. Every
   mechanism the spec states is quoted from source or probed, never recalled.
3. **Spec review.** Three Opus lenses run in parallel: contract and criteria, mechanics and
   feasibility, and data integrity and failure risk. A fold follows, and it probes every new mechanism
   it introduces; the catch ledger found that 8 verification majors were mechanisms a fold stated from
   memory. One verification read follows, and the fold agent applies its findings; only a blocker earns
   another read. A finding that changes the approved design returns to Geoff as one batched question;
   every other finding is folded without him. The consistency and prose lenses are retired; Vale and
   `tellgrader` cover prose.
4. **Plan.** A task list. Each task carries its outcome, files, risk class, acceptance check, test, and
   a clock estimate, and never implementation code. Independent tasks are marked as pairs. The
   mechanics lens and a verification read run by default; all three lenses run for an `auth-data` or
   `runner` pass, or one with the `live-account` flag.
5. **Execute.** See the next section.
6. **Close.** The repo's full-suite home is green on the head (ruling 11). One whole-branch Opus
   review loads the checklists the adapter's globs match (the four domain reviewers; `go-conventions`
   for Go), re-derives each task's class, and gives any unread `auth-data` task its read;
   `visual-verifier` runs on rendered UI in a site or the cairn admin (catch ledger S6 item 4). One
   batched fix chain; the auth smoke on `auth-data` passes; STATUS and ROADMAP updated; a PR body with
   what landed, each `auth-data` verdict, and a one-line score of clock, tokens, and attended time.
   Geoff reads the PR and merges.

Retired from today's lifecycle: the conductor, the simplifier as a standing step, the per-task local
full gate, HISTORY entries, post-mortems, the close fold and its review, token ceilings, checkpoint
STATUS writes, and pass segmenting.

## Execution

1. **One session executes.** The planning session launches it with
   `claude --bg --model sonnet --effort medium` in the pass checkout (stowed `settings.json:11`
   already sets `auto` permissions) and records its id in STATUS. It reads, edits, writes the tests,
   and commits (Anthropic: "an agent handling a feature should also handle its tests"), and arms the
   API-drop wake-up and, if the lid may close, the lid-switch hold (`unattended-work-guards.md`).
2. **Pairs.** Two tasks whose files, generated outputs included, are disjoint go to two Agent-tool
   subagents with worktree isolation, after the session commits. `worktree.baseRef: "head"` makes
   their worktrees branch from that commit, not the remote default (code.claude.com/docs/en/worktrees,
   "Choose the base branch"), and each runs the adapter's setup command first. Pair agents commit and
   never push; the session merges both, runs the fast lane, and pushes. A conflict stops the line.
3. **A fast inner gate.** The adapter's classifier (cairn: `gate-tier.mjs`) selects the legs: the type
   check, the selected unit and component tests, the static checks the diff touches, and the docs gate
   when docs changed; `cairn-run-gate` runs them. Non-browser legs run concurrently, on the light lane
   only if their measured peak fits its 3G cap (`cairn-run-gate:29-34`). A browser leg runs alone on
   the heavy lane after them (`gate-tier.mjs:71-76`).
4. **CI carries the whole suites, off the critical path,** where it runs on PRs. The first push opens
   a draft PR, since cairn CI runs on `pull_request` and on push only to `main` and `rebuild`
   (`test.yml:3-8`). After each push the adapter's watch command (cairn: `ci-green <sha> --pr <n>
   --wait`, re-issued on 75; elsewhere `gh pr checks <n> --watch --fail-fast`) runs as a background
   Bash task, which re-invokes the session on exit. A red stops the line: fix forward or revert.
5. **Review beside CI.** On `auth-data` tasks an Opus diff review reads the commit while CI runs. A
   `fix` or `escalate` verdict stops the line as a red does.
6. **A clock stop.** The session writes a task-clock file (task, start, estimate) at each task start.
   A PostToolUse hook returns a stop line as `additionalContext` once elapsed time passes twice the
   estimate (code.claude.com/docs/en/hooks), and stays silent with no file. On a stop the session
   writes STATUS, sends `notify-send -u normal`, and waits for Geoff (ruling 13).
7. **`cairn-run-gate` fixes.** A finished result stays until a new run starts, so a repeat call or a
   concurrent waiter reprints it, never a false vanish; `--fresh` forces a rerun. The deadline uses
   `$SECONDS`, so a call returns inside the 600-second cap. An unknown flag exits 2. The exit-75 text
   names the Bash `timeout: 600000`. With `RUN_GATE_IF_BUSY=defer`, a heavy-lane gate whose lock is
   held exits 76 and leaves that leg to the push's CI; never where the full-suite home is local, and
   never on `auth-data`.

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
unique reds in the record, so where CI exists, moving it there costs an 11-minute CI cycle per red.

## Instruction surface

A sentence stays only if it changes what the model would otherwise do (harness-design post: strip
what is "no longer load-bearing"). Caps: CLAUDE.md under 200 lines (memory docs), a skill body under
500 (skill authoring best practices).

| File | Fate |
|---|---|
| Global `CLAUDE.md` (301 lines) | Rewrite to 200 or fewer. Pass, gate, sizing, conductor, model-seat, and ledger sections leave for `pass-core`. |
| cairn `CLAUDE.md` (335) | Rewrite to 200 or fewer. Charter, docs tracks, releases, admin design, and gotchas stay as short pointers. |
| `pass-core` (312) | Rewrite to about 120: the lifecycle, execution, risk classes, launch, pairs, the clock stop, and the score definitions. |
| `cairn-pass` (170), `site-pass` (65) with `plan-template.md` | Rewrite as thin adapters: gate command, fast lane, full-suite home, worktree setup, CI watch command, risk-class path map, checklist globs, close checklists. |
| `spec-plan-review` (169) | Rewrite to the three spec lenses, the probing fold, the verification read, and risk-scaled plan review. |
| `pass-execute.js` (1,265), `pass-execute-chains.js` (931) | Delete, with `tests/pass-execute-runners.test.mjs` and its `scripts/check.sh:44` line. |
| `cairn-implementer` (173), `site-implementer` (155) | Trim to pair-subagent definitions; drop the chain report shape and gate protocol. |
| `diff-reviewer` (91) | Rewrite: it carries the `auth-data` bar itself (coverage gaps block, cosmetic citations never do), takes a task or whole-branch scope, and drops the conductor and report inputs. |
| Four domain reviewers | Keep as files; the close review loads them as checklists. |
| `code-simplifier`, `go-architecture-reader` | Remove from the process (no catch record); both stay for on-request use. |
| `docs-page-chain.js` (2,025) | Keep the deterministic gates; audit each model seat (rollout step 4). |
| `model-economy.md`, `pass-gate-economy.md`, `unattended-work-guards.md` | Step 1's plan lists every rule in the three and gives each a home or a deletion by name. Pass rules go to `pass-core`; machine rules (the guards, heavy-lock coordination, the light lane, never edit a script a running gate executes) go to a trimmed `unattended-work-guards.md` or `bluefin-admin.md`. |
| Stowed `settings.json` | Add `worktree.baseRef: "head"` and the clock-stop hook. |
| `cairn-run-gate` | Keep, with the fixes in Execution item 7. |
| cairn `gate-tier.mjs` and CI | Add the fast lane; shard the CI e2e job. |

## Rollout

The cutover runs on the new process from its first task, as a `runner` pass. Its sessions launch in
`~/.dotfiles` (`~/Projects/workstation` is a convenience link), and the launch prompt names this spec
as overriding the loaded pass sections until step 1 merges. `~/.claude` resolves through stow into
that working tree, so an edit there is live machine-wide at once. No pass runs until its repo's step
merges; rung 14a's hold is recorded in dubplate's STATUS before step 1 merges.

1. **Workstation repo,** on a branch in a worktree: every row above that lives in `~/.dotfiles`, both
   adapters included. The sweep covers skills, agents, workflows, and docs that name a deleted file or
   teach a retired mechanism, and each superseded phrase joins `tooling/retired-phrases.txt`. Done
   when `scripts/check.sh` is green, one live pair probe ran `cairn-run-gate` in its worktree, and the
   one-executor check is clear in every repo. It lands as one merge commit whose parent is tagged
   `pre-lean-process`, so rollback is one revert.
2. **cairn-cms,** on a branch merged by PR: its `CLAUDE.md`, the fast lane in `gate-tier.mjs` with its
   header and `docs/internal/pass-gate-tiers.md`, one measured fast-lane peak to set its lanes, and
   the CI e2e shard.
3. **Site repos and dubplate.** Sweep retired machinery to zero hits on a named grep list per repo,
   including dubplate's conducting loop, merge-time `go-architecture-reader` dispatch,
   `dubplate-implementer`, and simplifier brief, and ecxc-ski's `ship` skill and
   `development-workflow.md` rule. Give dubplate an adapter; bring aksailingclub-org (262) and
   dubplate (356) CLAUDE.md to the cap. In steps 2 and 3, HISTORY's "wrong to rediscover" bullets
   move into executing homes; the ledger counts three re-hit inside 48 hours.
4. **Docs-chain audit.** Before docs stage 2b, a `docs-page-chain` model seat stays when its recorded
   runs (2a run journals, plan ledgers) show a unique catch at REAL or above that the deterministic
   gates passed, a published-page register catch included (ruling 14). A seat with no record is cut.
5. **Pass B resumes** as the first scored pass, re-planned as a lean task list outside the clock, its
   branch merging `main` after step 2. Its WIP for Tasks 1 and 2 (`dbdc4556` in
   `.claude/worktrees/engine-pre-2b-b`) is re-gated through the fast lane; Task 2 gets the
   `auth-data` read.

## Success test

Pass B lands in 9 hours or less of clock, from its first execution commit to PR-ready, excluding
Geoff's read wait and pauses he orders (`cairn-run-gate --records` gives gate, lock, and CI time). No
behavioral, security, or contract escape surfaces through the next pass's close, from CI on `main`,
that close's review, or Geoff's use; an escape goes into STATUS with its commit. Attended time stays
at the design, the PR read, and one event per fired clock stop (ruling 13). The PR score carries the
table's five rows; a miss names its row, or an escape the step that should have caught it, and only
that changes.
