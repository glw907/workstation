# Lean pass process spec: contract-and-criteria review

Target: `docs/superpowers/specs/2026-10-10-lean-pass-process-design.md` at `a0fa4b6`. Lens: contract
and criteria. Each claim about an existing file was checked against the file on 2026-10-10. Only gaps
that affect correctness or a stated requirement are listed; the approved rulings are not reargued.

Counts: 1 blocker, 12 major, 3 minor. Two owner forks (M10, M12). No over-ceremony finding met the
bar: every per-task and close step the spec keeps has a catch record behind it.

## Blocker

### B1. The close's first criterion cannot hold in six of eight repos, and the full suite then runs nowhere

Location: spec `:80` (close: "CI green on the head"), `:98` ("CI carries the whole suites"), `:85`
(local full gate retired), `:119-120`.

Defect: the spec assumes every repo has PR CI that runs the whole suite. Checked:

- `~/.dotfiles` (the cutover's own repo), dubplate, and xcathletes-org have no `.github/workflows`.
- ecxc-ski, 907-life, and cairn-pub have only `deploy.yml`, triggered on push to `main`. It builds and
  runs `wrangler deploy` with no test step (`ecxc-ski/.github/workflows/deploy.yml:21-36`).
- Only cairn-cms and aksailingclub-org (`ci.yml`, `pull_request`, runs `test:e2e`) have test CI.

In the other six repos, "CI green" is unsatisfiable, or it passes vacuously because a PR with no
checks reads green. With the local full gate retired, e2e and the whole unit suite then run nowhere
before merge, which breaks ruling 3. In three of those repos the merge itself deploys to production.
The parked design handled this ("a repo with no CI keeps every leg local",
`cairn-cms/docs/superpowers/specs/2026-10-10-pass-clock-time-design.md:85-87`). The lean spec
dropped it.

Fold: each adapter names its repo's full-suite home. That is PR CI where it exists (cairn-cms,
aksailingclub-org). Elsewhere it is one local full gate at close, run through `cairn-run-gate` on the
heavy lane, with a receipt lookup so an unchanged tree skips the rerun. Then rewrite the close's
criterion as "the repo's full-suite home is green on the head". Adding PR CI to the sites can go to
ROADMAP. Ruling 3 settles this, so it is not a fork.

## Major

### M1. A branch push starts no CI, so the pipelining and "a CI red stops the line" never fire

Location: spec `:98-99`.

Defect: in cairn-cms, `test.yml:3-8`, `e2e.yml:3-8`, and `design.yml:9-14` run on `push` only for
`main` and `rebuild`, and on `pull_request`. A pass-branch push with no open PR runs nothing. Every
red then batches at the close. This repeats the gate-economy spec blocker "chains have no PR" (catch
ledger S1 item 1). The spec also never says how a session already working the next task learns that
CI went red.

Fold: the pass's first push opens a draft PR. `pass-core` names the watcher: a background
`gh pr checks --watch` (or `gh run watch`) that re-invokes the session when it exits. Done state: the
draft PR exists after the first push, and a planted red stops the next task.

### M2. Two people would classify the same pass differently

Location: spec `:62-63`, `:78`, `:100`.

Defect: the spec gives three sources for a class and no precedence between them:

- "One risk class" is declared per pass in the design.
- Execution item 4 acts "on `auth-data` tasks", which is a per-task class.
- The adapter "maps paths to classes".

Pass B shows the clash. Tasks 2, 5, and 8 are `auth-data` inside an `engine-logic` pass
(`cairn-cms/docs/superpowers/plans/2026-10-08-engine-pass-pre-2b-b.md:628, :795, :920`). One class
per pass means either every task gets the Opus per-task read or none does.

`unattended` describes an execution mode, not a risk, so it can't sit on the same axis as
`auth-data`. Under ruling 4 every execution runs unattended anyway. `runner` ("process or tooling
mechanism") has no boundary: nothing says whether a `.github/workflows` edit, `gate-table.json`, or a
new check script counts.

Fold:

- The adapter's path map assigns each task a class. The declared class is a floor, and the pass class
  is the highest task class (`auth-data` > `runner` > `ordinary`).
- Turn `unattended` into a flag, defined from its one unique catch (catch ledger S2 item 3): the run
  can create, change, or deploy to a real external account (Cloudflare, GitHub, npm).
- Define `runner` by path list in each adapter: skills, agents, workflows, `cairn-run-gate`,
  `gate-tier.mjs` and `gate-table.json`, `.github/workflows`, and `scripts/checks`.

### M3. The success test can pass vacuously and can't be scored by row

Location: spec `:163-167`.

Defect: the test has four gaps.

- (a) "No ... escape found after merge" names no window and no detector, so it passes whenever
  nobody looks.
- (b) "9 hours or less of clock" names no start, no end, and no exclusions. The only definitions
  (total clock minus Geoff-ordered pauses and owner-gated waits, plus gate time, lock wait, and CI
  wait from `cairn-run-gate --records`) live in `model-economy.md:85-93`, which the spec deletes.
- (c) "The PR's score names the row that missed", but the close writes a "one-line score of clock,
  tokens, and attended time" (`:83`), which has no rows.
- (d) An escape or an attended-time miss maps to no row of the table, so "only that row changes" has
  nothing to point at.

Fold:

- Define the clock as running from the first execution commit to PR-ready (close complete, full-suite
  home green). Exclude Geoff's read wait and any pause he ordered.
- Keep `cairn-run-gate --records` as the source for the gate, lock, and CI rows.
- For pass B, the PR score carries all five table rows.
- Set the escape window to "through the next pass's close", with CI on `main`, the next close review,
  and Geoff's use as the named detectors. Record an escape in STATUS with its commit.

### M4. "Fold what still executes" has no list, and its two homes can't hold the survivors

Location: spec `:141`, rollout `:151`.

Defect: the row gives no inventory, so its done state can't be checked. Several rules that still
execute after the cutover are workstation-wide, and neither `pass-core` (loaded only for passes) nor
`cairn-run-gate` can hold them. Survivors found:

- `unattended-work-guards.md`:
  - the 11% battery stand-down (`:90-95`);
  - the lid-switch hold (`:135-142`; `bin/.local/bin/awake:19` points to this file);
  - the restart re-arm checklist (`:111-121`);
  - "touch only your own guards" (`:123-133`);
  - the runaway guard through `claude-wf-guard` (`:7-29`), which still applies to `docs-page-chain`
    runs;
  - the `/loop` wake-up (`:97-109`), which still applies to background pair subagents and workflow
    runs.
- `pass-gate-economy.md`:
  - heavy-lock session coordination (`:77-87`; ruling 10 keeps this);
  - the light lane for browserless gates (`:88-104`);
  - never edit a script a running gate executes (`:113-116`);
  - invoke a workflow by name and `cmp` it after a same-session edit (`:66-76`), since
    `docs-page-chain` remains a workflow;
  - receipts (`:35-44`), if B1 keeps a local full gate.
- `model-economy.md`:
  - the seat and effort table (`:12-25`). The spec names no effort for the executor, the pair
    subagents, the lenses, or the close review, and the old security seat ran at `high`;
  - `/effort` persists through the stow symlink, so reset it at session end (`:58-60`);
  - the Haiku 100k price cliff (`:50-53`);
  - the Fable escalation and allowance (`:27-29`, `:108-117`; `fable-post-cutoff-system.md` cites
    them);
  - the score definitions (`:69-93`, which M3 needs);
  - pass sizing (`:130-153`).

Fold: replace the row with this list and give each item a home. Pass rules go to `pass-core`.
Machine rules go to a trimmed `unattended-work-guards.md` or `bluefin-admin.md`, since a workstation
fact routes to `~/.claude/docs`. Anything else is deleted by name.

### M5. The fast lane runs a browser suite outside the heavy lock

Location: spec `:94-97`.

Defect: the heavy lock is keyed to "the acceptance check names an e2e spec". The fast lane also runs
"component tests", and cairn's component project is Vitest browser mode on Playwright Chromium
(`vitest.config.ts:4`, `scripts/test/contained.mjs` header). `gate-tier.mjs`'s own header says a
browser suite must not take a light-lane pin and that the caller owns the lane decision. The light
lane's 3G cap (`cairn-run-gate:30-33`) and the rule "a gate that launches no browser takes the light
lane" (`pass-gate-economy.md:95-97`) are what keep one light gate and one heavy gate inside RAM. With
the legs also running concurrently, the likely result is Chromium OOM-killed inside the light scope,
or two browser suites side by side: the 2026-09-14 incident class.

Fold: pick the lane by what the lane launches. Any browser leg, component or e2e, takes the heavy
lane. The `defer` exit lets a component leg go to CI when the heavy lane is busy, but only in a repo
whose full-suite home is CI.

### M6. Rollout steps 2 and 3 put two skill rewrites in the wrong repo, and step 1 can't go green without them

Location: spec `:154-157`.

Defect: `cairn-pass` and `site-pass` are tracked in the workstation repo
(`git ls-files claude/.claude/skills/cairn-pass claude/.claude/skills/site-pass`), and
`~/.claude/skills` links to `~/.dotfiles/claude/.claude/skills`. Step 2 rewrites `cairn-pass` "on a
cairn branch merged by PR", which is impossible. Between step 1 and steps 2 and 3, the old adapters
would still direct the deleted process. Any reference they hold to a deleted file also fails
`scripts/check-claude-refs.py`'s dead-reference check (`:12-18`), which breaks step 1's "keep verify
green" done state.

Fold:

- Move both adapter rewrites, with `site-pass/plan-template.md`, into step 1.
- Step 2 keeps the cairn `CLAUDE.md`, the `gate-tier.mjs` fast lane, the CI shard, and
  `docs/internal/pass-gate-tiers.md`. That page is the one a reviewer reads to reproduce a gate,
  according to `gate-tier.mjs`'s header.

### M7. The sweep criterion misses files that teach the old process, and it has no executable check

Location: spec `:151-153`, `:156-157`; the table at `:128-143`.

Defect: "every skill and agent that names a deleted file" misses files that carry retired concepts
without naming a deleted file. In the workstation repo:

- `engine-consult` and `cairn-release` (HISTORY and post-mortem);
- `site-pass/plan-template.md`;
- `go-architecture-reader` ("the conductor dispatches it ... at a pass's merge");
- `engine-triage`;
- `cairn-register-editor`;
- `docs-page-chain.js`;
- `diff-reviewer` (`:3`, `:31-44`: `Pass class:` `docs` and the conductor).

In the repos, none of which appear in the table:

- dubplate's `CLAUDE.md` (`:123` runs the conducting loop through `pass-execute`; `:135` and `:308`
  run the simplifier), plus its `dubplate-implementer` agent and `.claude/instructions/simplifier-brief.md`;
- ecxc-ski's `ship` skill, which runs code-simplifier and pushes to `main`, a deploy, and also
  conflicts with the one-sentence skip path at `:67-68`;
- ecxc-ski's `.claude/rules/development-workflow.md`.

dubplate also has no adapter skill, so Execution item 2's "each repo's adapter" is undefined there.
The workstation already ships the executable form of a sweep: `claude/.claude/tooling/retired-phrases.txt`
says "every ruling that supersedes text adds the superseded phrase here in the same commit".
`check-claude-refs.py` enforces it.

Fold:

- Step 1's done state: retired phrases added for each retired mechanism (`pass-execute`,
  `Pass class:`, `token ceiling`, the conductor, `post-mortem`, `HISTORY.md` entries), with
  `scripts/check.sh` green.
- Step 3's done state: a named grep list with zero hits in each repo, and a dubplate adapter.
- Add table rows for the files listed above.
- Fold in step 3's 200-line check (`:157`), which names no action. aksailingclub-org (262 lines) and
  dubplate (356 lines) exceed the cap, so rewrite both or name them as ROADMAP items.

### M8. An `auth-data` review verdict has no handling, and `diff-reviewer` loses its bar

Location: spec `:100`, `:137`.

Defect: the per-task read runs while the next task is already underway, and the spec gives no rule
for a `fix` verdict. The catches this step exists for are fail-open auth blockers (catch ledger S3
items 1 and 2), and they would roll forward unhandled. The "Keep" row also hides a contract break:

- The reviewer's bar reaches it today as `passClass`, which the runners render. Both runners are
  deleted (`model-economy.md:44-49`, `pass-gate-economy.md:22-27`).
- Its input is an implementer report and a conductor (`diff-reviewer.md:3`, `:20-28`).
- Its scope is "one plan task's diff", which doesn't cover the whole-branch read at close.

Fold:

- A `fix` or `escalate` verdict stops the line the same way a CI red does.
- The close checks that every `auth-data` task's verdict is `accept`, and lists those verdicts in
  the PR body.
- Rewrite `diff-reviewer` to carry the `auth-data` bar in its own definition: coverage gaps block,
  and cosmetic citations never block (catch ledger S3 verdict). Add a whole-branch mode for the close.

### M9. The close drops the visual gate, which has a unique catch record, without a ruling

Location: spec `:80-82`, `:138`.

Defect: the close lists domain checklists only. Theme identity pass A's `visual-verifier` found 4
STRUCTURAL defects that no per-task gate sees (catch ledger S6 item 4, U). The global `CLAUDE.md`
rule "nothing deploys to production without a full-page render read" still stands, and a site merge
deploys. The close also names a Go checklist, but none of the four domain reviewer files is a Go
checklist. Go's file is `go-architecture-reader`, which the table doesn't list.

Fold: the close runs `visual-verifier` when the diff touches rendered UI in a site or in the cairn
admin, with the paths in the adapter's map. Name `go-architecture-reader` as the Go checklist.

### M10. The clock stop has no measure and no reader, and when it fires it fails the success test. OWNER FORK

Location: spec `:101-102`, `:166`.

Defect: a session has no task start time unless one is defined, and STATUS reaches nobody until Geoff
opens it ("a side doc reaches nobody"). So a strategic miss doesn't surface "in minutes". A stop that
pulls Geoff in is an attended event, and the success test allows attended time only "at the design
and the PR read". The mechanism working as designed would fail the test.

Settled part: measure elapsed time from the previous task's commit timestamp, checked at each gate
result. On a stop, write STATUS and send one `claude-notify` at normal urgency.

Fork, what happens after a stop:

- (a) Halt and resume on Geoff's word. The stop counts as an execution sitting.
- (b) The session re-estimates the remaining tasks, records them, and halts only on a second stop.
- (c) Halt silently to STATUS.

Recommendation: (a) for pass B. The catch ledger's S7 shows that only Geoff caught the strategic
misses. The success test should count a fired stop as an attended event, not as a failure.

### M11. Pass B's plan is in the retired format, so the first scored pass can't run the new process

Location: spec `:160-161`.

Defect: the plan (1,335 lines) carries all of the following:

- the old classes (`engine-logic`, `sweep`, `docs`);
- a 14.0M token ceiling (`:37`);
- a conductor Task 0 (`:478`);
- Task 11's HISTORY and post-mortem records (`:1124`, `:1321`);
- no per-task clock estimates, so the clock stop can't fire.

Re-gating the WIP at `dbdc4556` through the fast lane alone also skips the per-task review for Task
2, which is `auth-data` (`:628`).

Fold: step 5's done state is the plan converted to the new task shape (outcome, files, acceptance
check, test, clock estimate, pair marks, mapped class). Task 11 is trimmed to STATUS, ROADMAP, and
the CHANGELOG. Task 2's WIP gets the `auth-data` read. Say whether the conversion counts inside the
9-hour clock. It should not, since planning is outside the table's rows.

### M12. The docs-chain audit has no pass mark, and ruling 3 makes its yardstick unclear. OWNER FORK

Location: spec `:158-159`, `:13-14`.

Defect: "at a clock and token price worth paying" is a judgment two people would make differently.
The catch ledger holds no per-seat data for `docs-page-chain`. Its only docs-seat evidence is the 2a
finish register read, where 13 blockers passed `tellgrader`
(`cairn-cms/docs/superpowers/plans/2026-10-07-2a-close-finish.md:110-150`). Those catches are
wording, and ruling 3 lets wording defects land on `main` to be fixed forward.

Settled part:

- A seat stays when its recorded runs show at least one unique catch at REAL or above that the
  deterministic gates passed.
- A seat with no record is cut (ruling 2).
- The evidence sources are the 2a run journals and plan ledgers.

Fork, whether a register catch on a published docs page counts:

- (a) Yes, for published pages, because the page is the deliverable.
- (b) Ruling 3 applies uniformly, and the register seats move to a fix-forward sweep after merge.

Recommendation: (a). On a docs pass the published prose is the behavior.

## Minor

### m1. During the cutover, the loaded `CLAUDE.md` still teaches the old process

Location: spec `:147`.

Defect: until step 1 lands, the global `CLAUDE.md` "Conducting a pass" section directs a conductor,
`pass-execute.js` at six or more tasks, and a token ceiling.

Fold: the cutover plan's first task rewrites the global `CLAUDE.md` and `pass-core`. Until that task
lands, the launch prompt says this spec overrides those sections. The cutover is `runner` class, so
its plan gets three lenses. Under B1 its full-suite home is a local `scripts/check.sh` run.

### m2. The review steps leave lens identity and verification-read outcomes open

Location: spec `:71-78`.

Defect: there are three gaps.

- The spec names a "risk" lens, but integrity held 3 of the 19 spec blockers, including the unique
  D1 data-loss catch (catch ledger `:24`, `:29`). Today's table merges the two as "Data integrity
  and failure risk" (`spec-plan-review/SKILL.md:60`).
- "One verification read closes the step" doesn't say what happens to its findings. 25 of 25 reads
  found a major, and a second fold followed every time.
- The plan's "one review lens" is unnamed, and the spec is silent on the plan verification read the
  catch ledger kept (S2 verdict).

Fold:

- Name the spec lens "data integrity and failure risk".
- The fold agent applies the verification read's findings, with no further read unless one is a
  blocker.
- The default plan lens is mechanics and feasibility, and the plan verification read is kept.

### m3. The `cairn-run-gate` fix list states one item without a definition and one without a measure

Location: spec `:103-105`.

Defect: `defer` is undefined in this spec. Its definition is in the superseded parked design, section
5 item 4: `RUN_GATE_IF_BUSY=defer` exits 76. "Fast-lane mode" has two homes, `cairn-run-gate` and the
adapter (`:94`). The default wait is already 540 s (`cairn-run-gate:5-8`). The 600-second fix is
testable only as "wait plus lock wait stays under 600 s", since three full-gate calls hit the cap
through lock wait (`cairn-cms/docs/superpowers/research/2026-10-10-pass-clock-time-evidence.md:257-258`).

Fold: restate the `defer` contract and the caller's action, with no defer in a repo with no CI. Give
the fast lane one home, the adapter's classifier, with `cairn-run-gate` only running it. State the
600-second criterion as above.
