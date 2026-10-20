# Pass catch ledger: what each process step caught that no later step would have

Written 2026-10-10 for the process-ceremony brainstorm (`docs/STATUS.md`, "Next action"). Read-only audit; nothing committed.

## Method and what I could not establish

I took reviewer-assigned severity as the population count for every spec and plan review, from each file's "Counts" line (22 spec review files across the five S1 passes, 18 plan review files across the six S2 passes, 25 fold-verification files). I then read the bodies of about 45 findings and every plan ledger and post-mortem for the covered passes (gate economy, engine pass A, stage 2a with its two finish plans, pass 1b, theme identity pass A), plus `docs/HISTORY.md`, `git log` timestamps, and the pass B clock evidence. The unique-catch column counts only the findings I audited, each tagged U (no later step plausibly catches it), P (a later step catches it, later or at higher cost), or L (a later step catches it cheaply, with the reason given). Severity mapping: reviewer blocker is BLOCKER, major is REAL, minor is COSMETIC, a refused whole finding is FALSE. I could not establish: (1) tokens per spec or plan review, since the gate economy and pass A ceilings exclude planning and only two plans record a planning share (0.6M budgeted for the 2a plan review, about 1.0M for the unattended-finish planning, `plans/2026-09-30-draft-docs-stage-2a.md:130`, `plans/2026-10-07-2a-unattended-finish.md:87`); (2) which pass A close reviewer seat found which defect, because no seat report is archived (`docs/HISTORY.md:122-183` names only "four reviewer seats"); (3) every in-chain local gate red, because only reds that reached a ledger are visible; (4) Geoff's attended minutes reading specs; (5) a recall figure, because a defect no step caught is invisible here. Counts for S4, S5, S7, and S8 are thin (n of 5 to 13) and I say so in each verdict.

## Summary table

| Step | Passes covered | BLOCKER | REAL | COSMETIC | FALSE | Unique (audited, U of n) | Cost evidence |
|---|---|---|---|---|---|---|---|
| S1 spec review lenses, fold, verification | GE, A, 2a code-sync, 1b, theme identity | 19 | 140 (+17 from verification reads) | 137 (+39) | 6 refused whole (GE only; A refused 0 whole, 7 parts) | 6 of 11 | 5 to 8 agents per spec; wall 37 min (GE), 45 min (A); tokens unrecorded; GE spec grew 150 to 376 lines |
| S2 plan review lenses, fold, verification | GE, A, 2a plan, 2a unattended, 1b, theme A | 17 | 126 (+18) | 158 (+37) | 5 refused whole (GE only; A split 1) | 3 of 12 | 4 to 6 agents per plan; wall 50 min (GE), 40 min (A); 0.6M to 1.0M where recorded; about 215 KB of review text per pass |
| S3 per-task diff-reviewer | GE, A (20 reviewed tasks) | 2 | 5 | 2 | 1 (runner artifact) | 6 of 10 | fix on 9 of 20 tasks (45%); about 0.07M per read (GE 4a, 2a tasks 3 to 5); a fix round about 2 min (GE ledger) |
| S4 per-task local gate | GE, A, pass B S1 | 0 | 5 | 0 | 2 (flake, known drift) | 0 of 7 | per-task gate 30 to 50 min (A); 16.3 and 25.2 min on the targeted gate; heavy-lock wait 25% of a pass B chain |
| S5 CI | GE, A | 1 | 1 | 0 | 2 (hang, flake) | 1 of 5 | test job 663 s; queue up to 1,232 s; 5 of 631 runs hung about 6 h |
| S6 close: domain seats, simplifier, fold, close diff-reviewer | GE, A, theme A, 2a finish | 3 | 13 | 13 (register-labelled blockers) | 0 | 11 of 12 | A close budget 2.15M of 11.1M; GE close 0.74M actual against 0.55M; A close fix chains about 3.5 h |
| S7 human reads, smoke, escapes | A, GE, 2a, 1b, theme A | 3 strategic | 1 | 1 | 0 | 4 of 6 | each strategic catch arrived after 8M to 43M tokens or 95 min of run |
| S8 ledgers | A, GE, 2a, theme A | n/a | n/a | n/a | n/a | 2 uses against 3 repeats | HISTORY entry 60 to 110 lines per pass; friction triage of 23 to 187 entries per close |

## S1 Spec review, fold, verification

Lens yield (blockers): contract 7, mechanics 4, integrity 3, risk 2, methodology 2, consistency 1 across the five specs. Consistency found 4 to 8 majors per spec but one blocker in five specs.

1. **Chains have no PR, a site-repo push deploys, a conflicted PR reads as "missing run"** (BLOCKER, U). `research/2026-10-09-gate-economy-review-contract.md:14-77` (B1, B2) and `...-review-risk.md:24-42` (B1). Runner harness tests stub agents, so the first live chain run with `ci` set would have stalled, and a `mainCheckout` chain on a site repo would have deployed per task. Folded as opt-in `ci: { pr }` (`research/2026-10-09-gate-economy-spec-fold.md`, root 5).
2. **`gh pr diff --name-only` fails above 300 files or 20,000 lines** (REAL, U). Found by the fold-verification probe: three of the last eight PRs exit 1 (`research/2026-10-09-gate-economy-fold-verification.md`, M1). Under the spec's own rule that is Unavailable, so every large pass would silently fall back to the 45-minute local full gate. Nothing but a clock reading would show it.
3. **Mechanism 2 (fact staleness) rests on four facts that were wrong when filed** (BLOCKER-class design, U). Four lenses converged (`research/2026-09-30-docs-code-sync-fold.md`, "Settled, not forked"; `...-review-consistency.md:18`). The mechanism would have passed its own tests and stamped the wrong facts green. Deferral retired 15 findings and saved a built subsystem.
4. **D1's fix never reaches an existing manifest** (BLOCKER, U). `research/2026-10-07-engine-pass-pre-2b-spec-review-integrity.md:14-43` (I-1). A gallery-only asset would still read as unreferenced and delete without the typed-slug confirm: the data loss D1 exists to fix, surviving on every site. Tests written to the old spec pass. Produced the `Consumers must: regenerate the content manifest` line.
5. **C11's head read is unordered, and `use:enhance` leaves busy state set** (REAL, P). `...-integrity.md:74-102` (I-3) and `:142-160` (I-6). The spec covered five commit paths; the close found the sixth (publish-all) with the same ordering fault (`2a06c1b2`), and the Save re-enable (I-6's neighbour) reached the close as a blocker (`9f722bb9`). The lens named the class, not every instance.
6. **Pass 1b: 6 spec blockers and 32 majors folded into a design that never reached its bar** (not a catch). The methodology lens computed that 24 plants cannot meet the rule (`research/2026-09-24-pass-1b-spec-fold.md`, "What C3 and C4 produced"); the instrument still reached recall 3 of 24 and cost about 43M tokens (`docs/HISTORY.md:1158-1172`). Lenses are told not to re-argue settled decisions, so they sharpen a doomed design.

Fold-verification (S1 and S2 together, 25 files): every read found at least one major (parseable counts total about 61 majors) and one found a blocker (harvest). Eight majors were mechanisms stated from memory that fail: `vitest list --related` does not exist (`...-gate-economy-fold-verification.md`, M2, L: Task 3's build would fail at first run); pass A's single-flight mint repeats a hazard the engine's own incident record names (`...-spec-fold-verification.md:15`, V-M1). A second fold followed every time.

## S2 Plan review, fold, verification

Plans fared worse than specs: GE plan review returned 0 blockers and 18 majors, and the pass then drew five diff-review fix rounds and one CI red that no plan finding predicted.

1. **Outcome blocks and cited Decisions never reach the implementer or the reviewer** (BLOCKER, U). `research/2026-10-08-engine-pass-pre-2b-a-plan-review-mechanics.md:37-67` (B1). The agents are told not to read the plan, so S3 would have reviewed against an incomplete criteria list for all 12 tasks. Nothing later can observe what an agent was not told.
2. **Gate that certifies itself** (REAL, U). `research/2026-10-09-gate-economy-plan-review-risk.md:27-49` (M1) and `...-mechanics.md:13-45` (M1: the trigger canary cannot see the trigger list). A selection test that exercises only its own classifier passes by construction.
3. **Unattended re-test reaches real Cloudflare and GitHub accounts** (REAL, U). `research/2026-10-07-2a-unattended-finish-review-risk.md:120-134` (M7). With a token present it would create a real Worker and repository; no gate or stop clause covers it.
4. **R2 and R3 acceptance cannot go green before R4** (BLOCKER, P). `...-2a-unattended-finish-review-mechanics.md:17-47` (B1). The run would have halted itself at R2, so the catch saved one stalled unattended night, not a wrong merge.
5. **Theme A: pinned gate string trips MISMATCH on every task; stale `dist` sheet gives false mutation evidence; checked switch loses its focus ring** (BLOCKER, REAL, REAL; L, P, P). `research/2026-09-26-theme-identity-pass-a-review-risk.md:10-90`. The first would fail at task 1 for one or two wasted rounds; the third is a WCAG 2.4.7 failure the close a11y seat plausibly finds.
6. **A6 premise was wrong in both the plan and its review** (REAL, P). `...-a-plan-review-risk.md:74-102` names `type: 'error'`; Task 8 found the guard's login redirect arrives as a `redirect` result (`plans/2026-10-08-engine-pass-pre-2b-a.md:1549-1565`). The implementer corrected it, so S3 absorbed a plan miss.

Misses: GE Task 4a's fixed light gate ran no type check and CI went red on `d2c5164d` (`plans/2026-10-09-gate-economy.md:1137-1140`); theme A set no pass class and Geoff re-scoped to `paint` after 8.7M of 15.8M (`docs/HISTORY.md:835-888`); the 1b plan's 10M ceiling was flagged blocker B1 and the pass spent 20.07M.

Pre-flights (4 haiku runs in pass A, about 0.1M each): found moved line numbers and two scope amendments (Task 12's removed-option grep would have swept 14 internal planning files); no outcome-changing false claim. Mostly COSMETIC.

## S3 Per-task diff-reviewer

Population: GE 9 reviewed tasks (5 fix), pass A 11 (4 fix); pass 1b Tasks 1 to 6 drew about 44 blocking findings, each recorded as a real defect (`docs/HISTORY.md:1201-1208`, not individually audited).

1. **Six dist-surface checks swapped for three, dropping engine inheritance** (BLOCKER-class, U). `plans/2026-10-09-gate-economy.md:1095` (Task 3). A surface break could pass the gate. CI never exercises classifier choices, so it would not catch this.
2. **Empty file list read as green** (BLOCKER-class, U). Task 4b, `:1097`. The first live call then returned "missing" for five existing runs (short SHA), a defect only the live call caught.
3. **An explicit `--reporter` dropped Vitest's `github-actions` reporter** (REAL, U). Task 4a: retries would have been invisible with CI still green.
4. **Untested paths** (REAL, U). Pass A Task 1: `createAdminAction` never run for the steward, and the guard's identity-branch attach site tested only with an empty map (`research/2026-10-08-pass-a-s1-reports.json`, `review:task-1`). GE Task 5 (no test on the `CI_MAX_WAITS` cap fall-through, `plans/2026-10-09-gate-economy.md:1098`) and pass A Task 6 (key that fails signing skips the mint, `a8156613`) are the same coverage class.
5. **`nested` placement kind reached two admin dialogs under the wrong label** (REAL, P). Task 11 (`plans/...pre-2b-a.md:1582-1597`); an a11y or copy read plausibly finds it later.
6. **Over-blocking**: Task 2's block was four off-by-one fact citations (COSMETIC, L: the R7-style fact read catches them); Task 3's lone blocker was a runner artifact (FALSE, `:1471-1481`); Task 6b's was doc forecasts. Task 8's S3 boundary note passed "Save re-enables briefly" to the close's reviewers instead of blocking, and the close made it a blocker (`plans/2026-10-08-engine-pass-pre-2b-a.md:1549-1565`).

## S4 Per-task local gate

Seven reds are visible: GE Task 2 first heavy gate (svelte-check types); pass B S1 R1 (`check:facts`) and R2 (component test `own-tree-and-guidance.test.ts:121`) (`research/2026-10-10-pass-clock-time-evidence.md` section 1); pass A S2 boundary reds on `check:self-use` and showcase `format:check` (`plans/...pre-2b-a.md:1524-1547`); and two false reds (Firefox `page.goto` timeout, 20 known `site-visual` drift tests, `:1432-1450`). All five true reds are the kind CI reports too (L), so none is unique while CI shadows the pass. The gate also missed twice: the per-task engine tier ran no static list (the two S2 reds) and GE 4a's fixed light gate ran no type check.

Cost: pass B S1's 87-minute chain spent 61% in gate run, 25% waiting on the machine-wide heavy lock, 9% on implementer work; two of the three full runs were reds (`...clock-time-evidence.md` section 3). Pass A estimates: 30 to 50 min per task gate, about 45 min per boundary gate (`research/2026-10-09-gate-economy-pass-inputs.md:13-20`).

## S5 CI

1. **`tool` workflow red on every push since `5549fda8`** (BLOCKER for `main`, U). `setup-go` took a preinstalled go1.26.8 with nine open stdlib advisories; `main` "would have failed the same way" (`plans/...pre-2b-a.md:1549-1565`, fix `8f2fe6da`). No local gate reproduces a runner's toolchain.
2. **GE `d2c5164d`**: four implicit-any errors in `scripts/ci/retries-notice.mjs`; the local gate missed them, CI caught them, fixed in `8695229d` under Task 3 (REAL, P: the close's CI read would also have caught it).
3. **False reds and hangs**: five of 631 runs hung about 6 h (`research/2026-10-09-gate-economy-spec-fold.md`, "Measures" item 3); `edit-save-failure.spec.ts:207` failed three attempts then passed on rerun (`docs/HISTORY.md:122-183`). Job timeouts and one automatic rerun shipped in GE. CI also surfaced the retried-test list for the first time (`plans/2026-10-09-gate-economy.md:1148-1168`).
4. Pass A's `check:template`, `format:check`, and `check:self-use` reds were caught first by the local boundary gate (L).

## S6 Close: domain seats, simplifier, close diff-reviewer

1. **Two pass A blockers no gate saw** (BLOCKER x2). Publish-all could revert `main` by reading branches before the head (`2a06c1b2`, U); Save and Publish re-enabled during a successful save's reload, so a second click posted again (`9f722bb9`, P). The plan had briefed the security seat on head-before-snapshot order (`plans/...pre-2b-a.md:1311-1325`), so S1 steered S6 to the right place.
2. **Authorization and data-loss REAL fixes** (U). Undeclared role reachable through a leftover roster row (`ce4b60d7`, `c495ed11`, `8e2b7d29`); nested images beyond one level (`31a08ea4`); health verdict, timer, and signing memo (`54465876`); role CHECK matching and missing condition id (`aab0b719`, found by the live smoke, `~/.cache/engine-pre-2b-a/close-smoke-evidence.md`).
3. **GE dotfiles close read**: the documented `pass-execute` args template omitted `ci`, so every CI wait was skipped (BLOCKER for the deliverable, U). **GE cairn-cms close read**: simplifier dropped the `^npm run` guard (REAL, introduced by step 1 of the close), workflow pins missed a `pull_request`-skipping `if:` and `|| true` (REAL, U) (`docs/HISTORY.md:44-68`).
4. **Theme A visual-verifier**: 4 STRUCTURAL items at 320 and in the kit modal that no per-task gate sees (REAL, U); close a11y seat: soft-primary hover outside the modality gate (REAL, U) (`plans/2026-09-26-theme-identity-pass-a.md:1702-1730`).
5. **2a finish (no spec or plan review ran)**: diff review found a consumer site named in shipped `migrations/0002_audit.sql` and a missing CHANGELOG entry; the register read found 13 blockers tellgrader passed; the verification read found one more (`plans/2026-10-07-2a-close-finish.md:110-150`).
6. **code-simplifier and smoke**: simplifier changed 4 files (43 added, 29 removed, `a4c5e4b9`) in A and 3 files (37, 29, `4a1663f3`) in GE; no defect caught, one introduced. The live smoke confirmed 6 behaviors and found 1 minor gap.

Cost: A close fix chains about 3.5 h, each paying a full gate and a 14 to 33 min lock queue; GE close 0.74M against a 0.55M line.

## S7 Human reads, live smoke, escapes

1. **Pilot read**: Geoff read the six pilot pages and ruled they "read as atoms" (`plans/2026-09-30-draft-docs-stage-2a.md:681`), which drove tasks 7a to 7c and about 25M tokens of rework after about 8M spent (U, strategic).
2. **R7 rulings** overturned the run plan's next action (no release, engine pass first) (`docs/HISTORY.md:253-353`; U).
3. **Stops**: Geoff closed the 1b line at about 43M tokens ("cut our losses"); stopped pass B S1 at 95 minutes with no commit (`...clock-time-evidence.md` section 1) (U, both).
4. **Sitting counts**: GE 3 pull-ins, 0 defects; A 4 sittings (one cosmetic: "please" in two notices, `8483ca5b`); theme A S3 produced 16 corrections that were taste, not defects, and are not counted in the table.

## Escapes (found after the pass closed or after the step that should have caught them)

| Escape | Found by | Step that should have caught it |
|---|---|---|
| Pass-execute classifier probe: a haiku agent answered `{"exists": false}` 228 ms before its own `test -f` returned, so pass B S1 ran the 36-minute full gate on every task (`...clock-time-evidence.md` section 2) | Geoff's stop, pass B | S6 and replay: the probe is unchanged code, no diff touched it, and Task 7's replay never ran the runner end to end |
| GE deliverable `--pin` drops the three `auth-data` e2e specs; documented in pass-core, fix filed as ROADMAP follow-up (`docs/HISTORY.md:80-108`) | S6 | none (known, filed) |
| `tail` and `grep` cut `gate exit:`, forcing duplicate 16 to 36 min runs: GE simplifier gate, then pass B R4 hours later | Pass B run | S8 (recorded in the GE post-mortem the same morning) |
| Pass A plan premise on `use:enhance` (`error` vs `redirect`) | S3 Task 8 | S1 I-6 and S2 risk M2 both named the class, both wrong on the result type |
| Publish-all head ordering, sixth commit path | S6 | S1 I-3 listed five paths |
| GE projection 14.8 to 19.0 h against a 9 h target, recorded as a miss (`docs/HISTORY.md:69-79`) | Task 7 replay | S1 contract M3 had flagged "no threshold"; the fold set 9 h but the design could not reach it |
| Pass A post-merge: CI install hangs (PR #109), pending-dictionary e2e flake filed (`2733881c`) | CI | S5 (timeouts shipped only after) |
| 2a lanes broke 3 facts and about 45 pointers `check:facts` cannot see | R7 scoped fact read | S2 risk M5 flagged L2a's gate lacking `check:facts`; the R7 read was the net |

## Verdicts

- **S1 spec review: SHRINK.** 19 blockers and 140 majors across five specs, 6 of 11 audited unique, 37 to 45 min wall per cycle, so clock is cheap and the yield is real. The counts support three changes: run contract, mechanics, and risk or integrity lenses (they hold 16 of 19 blockers; consistency holds 1 and mostly citation drift, which a mechanical cite check covers); require the fold to quote or probe every new mechanism, since 8 of the verification majors were mechanisms from memory; keep the verification read (25 of 25 found a major). Thin: token cost unrecorded, and pass 1b shows no lens catches strategic infeasibility.
- **S2 plan review: SHRINK.** 17 blockers and 126 majors, but 3 of 12 audited unique and 8 of 12 were P or L; the GE plan drew 18 majors and still shipped 5 fix rounds and a CI red. Keep one lens by default and three only for `auth-data`, new runner mechanism, or unattended runs (the unique catches above were agent visibility, self-certifying gates, real accounts). Keep the verification read.
- **S3 diff-reviewer: KEEP.** 45% of reviewed tasks drew a fix, 6 of 10 audited unique, 2 fail-open blockers, 1 false blocker in 10, about 0.07M per read. Tighten the bar so cosmetic citations and doc forecasts do not block (2 of 10).
- **S4 per-task local gate: SHRINK.** 0 of 7 reds unique, 2 false, 25% of a chain lost to lock wait. Keep a local leg of type check, static list, and the selected tests; leave the rest to CI and run the local full gate only on `ci-green` exit 3. Thin: in-chain reds are not logged.
- **S5 CI: KEEP.** 1 of 5 unique, an environment red that would have broken `main`; the other four were P, L, or false reds. Near-zero clock when pipelined behind review, and it is what S4 shrinks into. Keep timeouts and the single rerun.
- **S6 close seats and whole-branch read: KEEP; code-simplifier: CUT as a standing step.** 11 of 12 audited catches unique, 3 BLOCKERs, at 17 to 19% of tokens. The simplifier caught nothing in 2 runs and introduced 1 regression (thin, n=2). The auth-data live smoke found 1 minor gap in 1 run, so keep it for `auth-data` only.
- **S7 human reads: KEEP, earlier.** 4 of 6 unique (the other two are taste and cosmetic), but each strategic catch arrived after 8M to 43M tokens or 95 minutes; a one-page pilot read before the six-page run, and a 20-minute checkpoint on a runner chain, would have cut the loss. Thin: n=6.
- **S8 ledgers: SHRINK.** HISTORY's "wrong to rediscover" bullets were re-hit three times inside 48 hours (worktree setup and `NODE_OPTIONS`, fixed gate strings skipping the type check, `gate exit:` cut by a pipe) against two clear uses (the static-list rule gave green S3 and S4 boundaries; the 187-entry friction log scoped pass A). Keep STATUS and friction-to-ROADMAP; land lessons as tool changes, not HISTORY prose. Thin: n=5.
