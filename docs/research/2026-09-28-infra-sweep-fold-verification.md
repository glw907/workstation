# Infra sweep spec: fold verification

Target: `docs/superpowers/specs/2026-09-28-claude-infra-sweep-design.md` at dotfiles `cd70c30`,
against the pre-fold `3f41deb`, the fold record, and the four reviews. Fresh reader, no part in
the fold. Line numbers are the spec's unless a file is named. Downstream plan: cairn-cms
`style-guide-sync` worktree at `2fd8eea8`.

Anthropic's warning applies: "Chasing every finding leads to over-engineering." The fold is
sound on the whole. Every blocker in the reviews closed. The four majors below are places where
the spec, executed as written, would stop a pass or quietly change a ratified rule.

**Counts:** 0 blockers, 4 majors, 10 minors.

## Q1. Did each review blocker and major close where the fold record says?

Yes, with two closures that introduced a new defect (M1 and M2 below).

| Review item | Closed at | Verdict |
|---|---|---|
| C-X1, K-M1, S-M3 (AW-01 rejection) | :149-153, :323, amendment 1 | Closed; the added "else the named gate" step creates M1 |
| C-X2, K-X2 (duplicate fingerprints) | S4 moves the check to A-rest; :190-191, :205-207, :445-449 | Closed |
| K-X1, C-M1 (ratchet no-op on `main`) | :185-187, :196-204 | Closed; hook placement confirmed against `scripts/githooks/pre-commit:10` |
| C-M2 (B success test) | :28-32, :395-405, amendment 9 | Closed in content; sequencing defect M3 |
| C-M3 (baselined in name only) | :290-300 | Closed |
| C-M4, K-M5, K-M6 (repo scope, `check-drift`) | :455-462, :479-480, :263-264 | Closed; `claude-tooling-sync verify` exits 0 today (probe) |
| C-M5, C-M6 (roots, failure table) | :217-218, :225-226, :239-242 | Closed |
| C-M7, S-M4 (chain W and the baseline) | amendment 8 | Closed |
| C-M8 (pointerless spec) | dropped; AW-18 by hand in C | Closed |
| C-M9 (split A) | S4 | Closed |
| K-M2, K-M3, K-M4 | :249-252, :276-280, :458-460 | Closed |
| K-M7 (vanish exit code) | :347 | Closed; consistent with `cairn-run-gate:101-129` |
| K-M8 (classifier probe) | :330 | Closed in form; per-chain gap M2 |
| S-M1, S-M2 (`0a2e391` regression) | :136-142, :379-382, :550-555 | Closed; `git show a7dd5ad` carries all three rulings at :74, :215, :350 |
| S-M5 (DC-21 cut) | :518-524 | Closed |
| S-M6 (short-phrase rule) | :288 | Closed |
| A-M1, A-M2, A-M3 | :175-179, :529-533, :230-231 | Closed |

## Q3. Mechanisms: quoted, probed, or from memory?

| Mechanism | Evidence | Verdict |
|---|---|---|
| Hook ordering before `exec gitleaks` | `scripts/githooks/pre-commit:6-10`; `core.hooksPath` = `scripts/githooks` | Grounded |
| Registry growth rule | mechanics X1's design; no probe | Sound except m1 (retired ids) |
| Re-key on rename | not probed | Depends on git's rename heuristic (m2) |
| `lint --root` | `claude-tooling-sync:152-164`: unknown command already returns 2 | Grounded |
| Reduced-gate resolution order | `pass-execute.js:257-268`, `:305-306` (`args.gate is required`) | The order's third step is unreachable (M1) |
| Cached `haiku` probe | `pass-execute-chains.js:336-352` probes carry `effort: "low"` and no `model` | Feasible; must be per chain (M2) |
| Exit 75 and vanish counter | `cairn-run-gate:101-108`, `:126-129` | Grounded. The vanish path must also clear `pidfile`, or each re-issue sees the same dead pid. "Re-issue starts a fresh run" implies this |
| `disable-model-invocation` | skills.md: "Set to `true` to prevent Claude from automatically loading this skill"; best-practices.md:277 "for workflows with side effects" | Quoted, verified by curl |
| `attribution` default | settings-reference `attribution.commit`: "unset, so Claude Code adds `Co-Authored-By: <name> <noreply@anthropic.com>`. The name is the model in use"; `settings.json` has no key | Quoted, verified |
| `/doctor prompt-audit` | memory.md:94 quote matches the spec's; requires v2.1.283 and the bundled `claude-api` skill | Quoted, verified |
| 200 lines, 500 lines, 1,536 characters, `omitClaudeMd` | memory.md:82, skills.md:492 and :355, features-overview | Verified |

## Majors

### M1. The named-gate step removes the reduced gate from every plan and repeals a ratified ruling

- **Where:** :151-153, :323, :655-658; fold record "Rulings for Geoff: None".
- **Defect:** the order is "explicit `reducedGate`, else the named gate, else the class default."
  A gate is always named: `pass-execute.js:305-306` throws without `args.gate`, and every prompt
  renders `t.gate || a.gate`. The third step can never run. Every plan that sets no
  `reducedGate` (all of them: `grep -rl reducedGate ~/Projects/*/docs/superpowers/plans` returns
  0) now runs its full gate on every comment-only or test-only fix round. That repeals the
  ratified 2026-09-09 ruling ("Comment-only fix rounds run a reduced gate",
  `pass-gate-economy.md:12`) and the 2026-09-27 class ruling (":19-21"). Those rulings exist
  because the full engine gate costs 7 to 11 minutes per round. Chain R's engine-logic tasks
  would re-run `SCRIPTS_GATE` with Chromium on each reduced round. The fold records this change
  as a risk, not a fork. It changes a Geoff ruling, so it is his decision.
- **Fold:** take the mechanics review's M1 as written. The order becomes explicit `reducedGate`,
  else the repo-neutral class default (`pass-execute.js:246`). Delete the "named gate" step
  and the Risks bullet at :655-658. B's acceptance replaces "every W reduced round renders
  `bash scripts/check.sh`" with "every W reduced round renders no npm command and names the
  class default." Amendment 1 stands. If Geoff prefers the named gate, record it as ruling S8.

### M2. `args.classifier` is run-wide, but one invocation carries a classifier chain and a chain without one

- **Where:** :330, :403-404; amendments 1 to 9.
- **Defect:** the style-guide-sync segments run chains R and W in one invocation. R's repo has
  `scripts/checks/gate-tier.mjs` (present), and W's has none. With the flag absent, B1 runs "one
  existence probe per chain repo," so W spawns a probe and the acceptance line "W spawns no
  classifier probe" fails. With the flag set to `false`, R's probe is skipped, and "R's existence
  probe runs once" fails. No amendment sets the flag. B's acceptance cannot pass as written.
- **Fold:** make `classifier` a chain-level field (a chain's value, else `args.classifier`, else
  one probe for that chain's repo). Amendment 1 sets `classifier: false` on chain W. B1's test
  asserts the per-chain case.

### M3. B's acceptance needs the amended plan, which B cannot produce

- **Where:** :28-32, :400-405, :409, :637.
- **Defect:** the dry render uses "the amended plan's real arguments," and the grep "of the
  amended plan" confirms the workarounds are gone. The amendments are applied "by that plan's
  conductor at pre-flight, after B merges" (:409). The plan is a cairn-cms file, and "Any change
  to cairn-cms code, docs" is out of scope (:637). B's close therefore depends on an artifact
  that exists only after B merges, in a repo B may not touch. B cannot close honestly.
- **Fold:** split the test at the merge. B's acceptance renders a fixture built from the plan's
  Gates block plus amendments 1 and M2, committed under `tests/`, and runs the five assertions
  on it. The grep and a re-run of the same render against the real amended plan move into the
  style-guide-sync pre-flight as a P-step before segment A dispatches, with amendment 9. Goal 1's
  first test (:28-32) names that P-step.

### M4. B3's retired footer string has hits no B3 task can clear

- **Where:** :365-368, :391-393.
- **Defect:** B3 retires the generic footer string and requires "no hit." The string also
  appears at `CLAUDE.md:68` and `workflows/cairn-overnight-to-release.js:76`, which B4 removes
  only after B3 lands. It also appears at `docs/voice/commit-and-pr.md:93`, which no B task
  owns. S3 hands that file to W4 after B. Growth under the registered retired-phrase id fails the
  hook, so these hits cannot be baselined, and B3 goes red with no legal fix.
- **Fold:** retire the footer string in B4, not B3. Add `claude/.claude/docs/voice/commit-and-pr.md`
  to B4's Files, and change its example to the model-named trailer (S7). Amendment 7 then lists
  that file among the ones B moved.

## Minors

- **m1. :185-187, :199, :202-204. A retired check id cannot be represented.** The registry is
  append-only, removing an id fails the hook, and a registered id no tool implements is a config
  error. A changed rule becomes a new id whose predecessor must stay registered with no
  implementer. Fold: a registry entry may carry `retired: true`, meaning no entries and no
  implementer required. Deleting the entry still fails.
- **m2. :205-207. Re-key depends on git's rename detection.** A move with heavy edits, such as
  D's `go-conventions` split or E's routing moves, stages as a delete plus an add, and the entry
  then reads as growth. Fold: allow a re-key when the old `file` is absent from the staged tree
  and the fingerprint is unchanged.
- **m3. :128-129, :288-289. Line-based matching misses a wrapped phrase.** The global CLAUDE.md
  hard-wraps at 100 columns, so a retired phrase can reappear across a line break. Fold: match
  on whitespace-normalized paragraphs and report the first line. Alternatively, state the limit
  and accept it.
- **m4. Amendment 2 against plan:319.** Amendment 2 drops W6's test-first mandate. W6 stays
  class `engine-logic`, and the runner renders test-first from the class. Fold: the amendment
  also sets W6's `passClass` (to `tool` or `docs`).
- **m5. :31, :405.** "Any `reducedGate` pin added for AW-01" is vacuous: the plan has none
  (plan:36-39). Drop it from the three workarounds.
- **m6. :317-319, :400.** Probe counts need the whole async runner run under a stubbed `agent`,
  not only the helpers that the markers and `new Function` extract. The chains runner also
  carries `export const meta`. Fold: state that the harness strips `export` and runs the body
  with stubbed `agent`, `parallel`, and `log`.
- **m7. :365.** The spec quotes `pass-execute-chains.js:238` as "the repo's commit conventions."
  The actual text reads "the repo's git conventions (imperative mood, specific files, the repo's
  co-author footer)". Fold: B3 uses the file's actual wording.
- **m8. :380.** `go-ship` "runs the repo's own `simplify` skill when one exists." The bundled
  `/simplify` always resolves, so the skill's existence cannot be observed by name. Fold: test
  for `<repo>/.claude/skills/simplify/`.
- **m9. :308-309.** The close simplifies "B1's JavaScript" only. B2 edits `docs-page-chain.js`,
  and B1 adds `.mjs` tests. Fold: "B's changed JavaScript."
- **m10. :190, :400.** With A split, "the pass letter" A is ambiguous. Fold: name the letters
  (`A-core`, `A-rest`, `B` to `F`); B's test reads "zero entries lettered A-core or B."

## Q2. Order and internal consistency

- **A-core before B before sync before A-rest:** builds. The sync needs only A-core's retired
  phrases, `--root`, the baseline, and the `ship` rename (amendments 2, 3, 8). No sync task
  needs an A-rest check. PS-14's move to `seats.json` and the RC3 skill step both land in A-rest
  and are consistent.
- **Ratchet bootstrap:** builds. AC1 introduces the file against a HEAD with no baseline (all
  new). AC2 and AC3 each register their ids and seed them in the same commit. AC1 must register
  no id without its implementing tool, or `check.sh` exits 2. The plan should state this.
  Worktree hooks run the branch's copy, because `core.hooksPath` is relative.
- **B under the per-commit hook:** builds, except for M4. No duplicate check runs before A-rest,
  so the fingerprint churn in B2, B3, and B4 is off the path.
- **The nine amendments:** they agree with the plan's rulings 1 to 14 and its tasks, except for
  M2 (no classifier setting for W), M3 (who applies them), and m4 (W6's class).

## Q4. Can the success tests fail?

- **A-core:** yes. The per-id seed counts, with a zero allowed only for a named reason, and the
  fixture table make the test falsifiable. `verify` is green today, so the merged-`main` check is
  reachable.
- **Pass B:** the baseline query and the render assertions can fail, and M2 means they will as
  written. The grep cannot run before B closes (M3). A `GA-nn` on the sync path lettered C would
  escape the zero-A-or-B query. The plan could letter every `GA-nn` in a file W edits as B.
- **Amendment 9:** falsifiable, and cheap.

## Q5. Does the spec meet the goal? Over-ceremony by cost

With M1 to M4 folded, the spec meets the goal. The work the sync would hit first comes first,
Anthropic practice is quoted and verified, and nothing lands on the sync's path that it does not
use. Over-ceremony, ranked by cost:

1. **A0 (`/doctor prompt-audit` in A-core).** A model-judged triage step on the sync's critical
   path, and its outputs become `GA-nn`, C, or D items the sync never touches. Move it to
   A-rest's seeding; E and F already run it.
2. **The dry render as a separate harness.** After M3 it duplicates most of B1's own assertions.
   Keep it as one fixture through B1's harness, not as a second test file.
3. **B1's interim parity test including `pass-core`'s table.** Cheap, and it guards B's own
   edits. Keep it.

Nothing else is material.
