# Plan review: infra sweep A-core and B, contract and criteria lens

Plan: `docs/superpowers/plans/2026-09-28-infra-sweep-a-core-b.md` at `62c5e6d`. Spec:
`docs/superpowers/specs/2026-09-28-claude-infra-sweep-design.md`. Rules: `pass-core` SKILL.md.
Lens: does each spec outcome map to a task with checkable acceptance, can any acceptance pass
vacuously, and do classes, gates, upshifts, and owner time fit the risk.

**Verdict:** sound in shape. Every AC and B id maps to a task, the header carries class, ceiling,
and checkpoints, and tasks stay outcome-only. Six majors, all cheap folds, and no blocker. Two
majors are factual errors about how edits go live or what writes into a stow package. The rest
are acceptance criteria that a green run could satisfy without the check ever firing.

Counts: 0 blocker, 6 major, 5 minor, 0 owner fork.

## Majors

**M1. B3 says implementer dispatches may drop the override "from this commit". That is false
until B merges.** Plan:126-127. `~/.claude/agents` symlinks to `~/.dotfiles/claude/.claude/agents`
on `main` (verified). B3's commit lands on `infra-sweep-b`, so the Agent tool keeps loading the old
`cairn-implementer.md` with its npm definition of done. If B4's dispatch drops the override, the
implementer runs the npm list in a repo that has no `package.json`, and that costs a fix round.
The plan's own Global constraints line 46 states the live-on-merge rule.
*Fold:* replace the sentence with "The definition-of-done override stays on every dispatch
through B close; stowed agent definitions go live only at the B merge."

**M2. The failure-state table moved from the plan into the task report.** Plan:91-92 against
spec:148-149, which says "The plan carries one failure-state table (state, tool, exit code,
report line) with one fixture per row." When the implementer authors the table, the reviewer
checks the report against itself, so "every fixture passes" holds for whatever fixture set the
implementer picked. The plan also never lists AC3's fixture states. The spec's list semantics
(spec:208-209) include "list absent: exit 2" and "no phrase: exit 2". Other untested states are a
`retired-ok` line passing, a vendored skill scanned for phrases but not dead references,
`skills/synced/` excluded, and the `~/.local/bin` rewrite. Only Review focus 3 is named.
*Fold:* put the table in the plan, one row per state, across AC1, AC2, and AC3. The rows are the
spec's AC1 fixture list, the baseline failure states (absent, empty, malformed per field,
unregistered id, bad finding-id format), the many-bad run with per-check counts, and the
no-read-outside-root fixture. AC2 adds manifest absent and manifest malformed. AC3 adds its
list, scope, and rewrite rows. Each task's acceptance then reads "the plan's table rows for this
tool, each a passing fixture".

**M3. "Zero entries labelled A-core or B" passes vacuously if AC3 mislabels.** B close step 2 at
plan:135-136 queries labels, but nothing checks that seeding gave the right label to each entry
B must clear. If an entry B should clear is labelled `C` or `E`, B's close passes while the defect
stays. A related gap: "the retired phrases have no hit" (plan:131, and B3 through the spec) can
pass because a baseline entry suppresses the hit, not because the text left.
*Fold:* (a) AC3 acceptance adds a check. Every audit id in the spec's B1 to B4 tables that seeds
an entry (DC-01, DC-03, DC-04, DC-30, PS-04, PS-05, AW-07, and the rest) carries label `B`. Every
seeded id that A-core fixes carries label `A-core`. The seeded-count table shows the label column.
(b) Define "no hit" in B3 and B4 as the scanner reporting zero matches for the phrase *and* the
baseline holding no entry with that phrase as its fingerprint.

**M4. AC2's two new checks have no failing fixture.** Plan:100-101 takes "the spec's AC2
acceptance", which is `lint --root` green, `verify` green on `main`, and manifest absent or
malformed exit 2. Once `ship` is renamed and `vhs-cli-demos` is manifested, both green results
also hold for a collision check or an unmanifested-skill check that never fires. The rename makes
the real tree clean, so only a fixture can show the check works.
*Fold:* add two rows to M2's table. A fixture projects root with `.claude/skills/<name>` equal to
a personal skill makes `verify` exit 1 and name the pair. A fixture `skills/<dir>` with a
`LICENSE` and no manifest entry makes `lint --root` exit 1. The collision check reads the
injected projects root, not `~/Projects`, which follows spec:140-141.

**M5. Pass B has no pre-flight, and A-core moves the ground under it.** P1 (plan:79-81) checks
only the AC1 to AC3 claims. `pass-core` says "Before each segment, dispatch one `haiku` or `sonnet`
pre-flight". B's tasks cite line numbers in files that A-core touches or that exist only after
A-core: `pass-execute.js:246`, `:164`, `pass-execute-chains.js:249`, `:238`,
`docs-page-chain.js:198`, `cairn-implementer.md:58`, `site-implementer.md:51`, `CLAUDE.md:68`,
`commit-and-pr.md:93`, `model-economy.md:38`, and the `skills/go-ship/` path that AC2 creates.
*Fold:* add P2 before B1: one `haiku` pre-flight over B1 to B4's claims, run on `main` after the
A-core merge, amending the plan before dispatch.

**M6. The plan puts a Python module in a stow package, and nothing stops `__pycache__`.**
Plan:86-88 decides "one module, under `claude/.claude/tooling/`". That directory is stowed as
`~/.claude/tooling`. `check.sh` exports `PYTHONDONTWRITEBYTECODE=1`, but the pre-commit hook and
`check-drift`'s `claude-tooling-sync verify` do not. `claude/` has no `.stow-local-ignore`, and
`.gitignore` does not ignore `__pycache__`. This is the 2026-08-30 incident class (HISTORY:203-206:
"anything a tool generates inside a package will be stowed").
*Fold:* AC1's Files and acceptance add a check that no `__pycache__` exists under `claude/` or
`bin/` after the hook, `check.sh`, and `verify` have run. The implementer chooses the mechanism
(a `claude/.stow-local-ignore`, the env var in each caller, or `sys.dont_write_bytecode` in the
module). Alternatively, move the module out of the stowed payload, for example to `scripts/lib/`,
with both tools resolving it from their own tree.

## Minors

**m1. B2's new test is not wired into the gate.** No `cairn-run-gate` test exists today, and
`check.sh` does not list one. B2's Files (spec:265-266) omit `scripts/check.sh`. Pass B
acceptance says "the runner and gate tests passing", but if the gate never runs the test, the
vanish counter has no regression guard. *Fold:* add `scripts/check.sh` to B2's Files, with
acceptance "run by `check.sh`".

**m2. Most B3 and B4 rows have no mechanical post-condition.** B4's acceptance (plan:130-131)
covers the hunk list, the retired phrases, and HISTORY. The DC-04 text, PS-14, PS-22, DC-30, the
`go-ship` simplify path check, the S5 languages in `pass-core`, and the `commit-and-pr.md:93`
trailer rest on `diff-reviewer` alone. The same holds for B3's AW-04, AW-05, and AW-19 rows. This
is acceptable for `docs`, but a one-line grep per row is cheap. *Fold:* the plan states "each
table row carries a grep post-condition in the task report, and `diff-reviewer` runs it".

**m3. The owner touch in `GA-nn` triage is not scheduled.** Spec:117-118 says "Geoff sees only
entries with no plausible owning pass". The plan says "Owner time: none planned" (plan:35).
*Fold:* "Any `GA-nn` entry without a plausible owning pass goes into the A-core checkpoint STATUS
as one batched question and does not block B."

**m4. The A-core boundary writes no HISTORY entry.** Plan:110-111. `pass-core` close step 6 puts
each pass's entry in `docs/HISTORY.md`. Only B close (plan:140) writes one. *Fold:* add "HISTORY
entry" to the A-core boundary.

**m5. The `docs` class misfits B3 and B4.** `pass-core` defines `docs` as "the docs tier" gate
with "the register chain". The plan overrides both (plan:21-23). The spec's shape (grep
post-conditions, no register chain, existing tests green) is `sweep`'s row. B4's ruling repair
still justifies Opus. *Fold:* declare B3 and B4 `sweep` with the check.sh gate, or keep `docs`
and say explicitly that the two cells are overridden. The plan already half does the second, so
this is cosmetic.

## Checked and sound

- Mapping: AC1 to AC3 and B1 to B4 each point at the spec section "in full". The spec's Pass B
  acceptance fixture sits in B1 (plan:116-118). The A-core acceptance items (seeded-count,
  per-label, and `GA-nn` summaries) sit in AC3 (plan:107-108). `verify` on merged `main` sits at
  both boundaries.
- Review focus 1 to 4 each name a fixture state (a staged secret with a clean baseline, a HEAD
  with no baseline, a doc deleted only in the fixture tree, a named gate with no `reducedGate`).
  Review focus 5 cannot take a fixture and uses a reviewer-checked hunk list instead.
- `core.hooksPath` is the relative `scripts/githooks`, so the worktree exercises its own hook.
  Global constraints line 48 holds.
- Upshifts: AC1 at Opus fits novel ratchet semantics, and B4 at Opus fits the rulings-versus-
  slimming judgment. AC2, AC3, B1, and B2 are specified tightly enough for Sonnet.
- Header: class declared per task, 5M ceiling split by pass, checkpoints at 3 and 4 tasks (inside
  the default four), the 80% rule, and conductor model and effort. Tasks are outcome-only.
- The spec's three "Open for the plan" items are decided: one module, `cairn-implementer` with
  an explicit gate, and the ceilings.

## Over-ceremony, by cost

Little to cut. In descending cost:

1. `diff-reviewer` on `claude-opus-5-5` for B3's three-file agent-definition edit. The `sweep`
   bar is Sonnet. Saving one Opus review is small, so keep it only if B3 stays `docs`.
2. The `sonnet` implementer at effort `high` on B3. Medium would do for deletions and one
   wording swap.
3. The erratum note in pre-bake (plan:77-78) has no stated content or acceptance. It is cheap,
   but name the erratum or drop it.
