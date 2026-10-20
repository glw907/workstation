# Infra sweep A-core and B plan: fold record

Target: `docs/superpowers/plans/2026-09-28-infra-sweep-a-core-b.md`, revised in place from
dotfiles `7ce3297`. Narrow spec edit: `docs/superpowers/specs/2026-09-28-claude-infra-sweep-design.md`,
amendment 1 and "Pass B acceptance" only. Reviews:
`2026-09-28-infra-a-core-b-plan-review-{contract,mechanics,domain}.md` in this directory. One fold
agent (`claude-opus-5-5`, high). Each finding was checked against the tree before its disposition.

Prefixes: `C-` contract, `K-` mechanics, `D-` domain; `OC` is an over-ceremony item.

**Counts.** 33 findings (C: 6 major, 5 minor, 3 over-ceremony; K: 3 major, 7 minor; D: 4 major,
5 minor). 32 folded (two carry a partial refusal), 1 refused. New owner forks: none.

## Verification notes

- `pass-core` SKILL.md:89 gives `sweep` a Sonnet review bar with grep post-conditions and the
  "existing tests stay green" mandate, so B3 and B4 fit `sweep`, and a Sonnet `diff-reviewer` on
  B3 is within the table. `docs` (:90) takes the register chain, which the spec rules out.
- `cairn-implementer.md` carries `memory: project` (:7), the npm definition of done (:30-32), the
  generic footer (:58), `src/tests/` (:75), and `check:facts` (:122, :130). Every one conflicts
  with a dotfiles task.
- `.gitignore:29-30` already ignores `__pycache__/` and `*.pyc`, so C-M6's "not ignored" is wrong.
  The stow concern stands: `~/.claude/tooling` is a folded symlink, so bytecode written there is
  live in `$HOME`. Folded as asked.
- `cairn-run-gate:29` puts state under `${TMPDIR:-/tmp}/cairn-gate-$(id -u)`; `:87` and `:93-95`
  hardcode the 5-second poll and 15-second grace.
- `git log 0a2e391..HEAD -- claude/.claude/CLAUDE.md` lists six commits (`32d00a6`, `2ad8c21`,
  `4f1ed96`, `68a8af8`, `2d9e562`, `89cbe40`), as D-M3 states.
- The sweep fold record's "Owed errata" names the audit-record erratum the pre-bake owes.
- Session transcripts live at `~/.claude/projects/<project>/<session-uuid>/subagents/`, so the
  probe's "outside this session's directory" filter is a path test.

## Roots folded once

| Root | Finding ids | Where folded |
|---|---|---|
| Agent definitions go live only on merge; implementer clauses conflict | C-M1, K-M2, K-M3, D-m2, K-m2 | "Dispatch overrides" section: absolute gate, staging, `tests/`, model-named trailer, no agent memory, no `--no-verify`; carried through the B merge; B3's "may drop the override" removed. `cairn-implementer` kept |
| Relative gate path runs `main`'s gate | K-M1 | Override 1 names `<wt>` absolute; header states the conductor's cwd is `~/.dotfiles` |
| In-flight detection blind to other sessions | D-M1, K-m6, D-m5 | "The in-flight probe" and "Mixed-version guarantee" in Global constraints; B2 old-state-dir fixture; B close step 5 carries the probe into the style-guide-sync plan's P0 and boundary |
| Merge into live `main` has no integration or gate | D-M2, K-m4 | "Merge integration" in Global constraints, used at both boundaries: implementer merges `main` in, `diff-reviewer` reads the merge, conflict-free `--no-ff`, `check.sh` and `verify` on `main`, red reverts |
| Rollback order and form | K-m5 | "Rollback" in Global constraints; B close step 3 records the order |
| B4 repair blind to later edits | D-M3 | B4: `git log -L` per region, third label "superseded after `0a2e391` (`<sha>`)", `diff-reviewer` confirms no later line lost; Review focus 5 |
| Chain W's reduced round runs nothing | D-M4 | Spec amendment 1 sets `reducedGate: "bash scripts/check.sh"` (step 1 of the resolution order); spec Pass B acceptance and plan B1 assert W renders it; Review focus 4 |
| Failure-state table in the report, not the plan | C-M2, C-M4, K-m7, D-m1 | "Failure-state table" section, 36 rows across AC1 to AC3, including H2 and H3 (hook-level ratchet and missing gitleaks), H4 (fast path), S3 and S4 (collision and unmanifested must-fire), F5 to F8 (list and scope); each task's acceptance names its rows |
| Vacuous close acceptance | C-M3 | AC3 label check (DC-01, DC-03, DC-04, DC-30, AW-07 seed `B`; no B-table id carries another label); "no hit" defined in Global constraints |
| No Pass B pre-flight | C-M5 | P2 before B1, on `main` after the A-core merge |
| Bytecode in the stow package; module resolution unnamed | C-M6, K-m1 | AC1 Files name `Path(__file__).resolve()` and `sys.dont_write_bytecode`; row M1; AC1 acceptance: no `__pycache__` under `claude/` or `bin/` |

## Single findings

| Id | Disposition |
|---|---|
| C-m1 | Folded: B2 Files add `scripts/check.sh`; acceptance "run by `check.sh`" |
| C-m2 | Folded: B3 and B4 acceptance require a grep post-condition per table row, run by `diff-reviewer` |
| C-m3 | Folded: A-core boundary puts unowned `GA-nn` entries in STATUS as one batched, non-blocking question; header "Owner time" names it |
| C-m4 | Folded: A-core boundary writes a HISTORY entry |
| C-m5 | Folded: B3 and B4 are `sweep`; the header names the two overridden cells (gate, B4's Opus reviewer) |
| C-OC1 | Folded: B3's `diff-reviewer` runs on `sonnet`, per the `sweep` row |
| C-OC2 | Refused: effort comes from agent frontmatter only (K's verification, code.claude.com sub-agents docs); no per-dispatch effort exists to lower |
| C-OC3 | Folded: pre-bake names the erratum text from the sweep fold's "Owed errata" |
| K-m3 | Folded: B2 makes poll and grace injectable; its test runs with short sleeps |
| D-m3 | Folded: A-core boundary's HISTORY entry records the `ship` rename's effect on ecxc-ski, both aksailingclub repos, and poplar |
| D-m4 | Folded: B3's AW-19 outcome adds the fallback to the repo `CLAUDE.md`'s documented gate |

## Partial refusals

- **D-M2, optional `pre-merge-commit` hook.** Refused: merge integration runs `check.sh` on both
  the pass branch and `main`, which covers the merge commit. A new hook is scope beyond A-core;
  A-rest can take it if the style-guide-sync W merges show the need.
- **D-M4, first option (make the class default fall back to the named gate in non-npm repos).**
  Refused in favor of the explicit `reducedGate` the conductor directed: it touches no runner
  semantics and leaves the ruled class default as the spec states it.

## Rulings for Geoff

None.
