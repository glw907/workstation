# Infra sweep spec: fold record

Target: `docs/superpowers/specs/2026-09-28-claude-infra-sweep-design.md`, revised in place from
dotfiles `9c0f2d0`. Reviews: `2026-09-28-infra-sweep-review-{anthropic,contract,mechanics,consistency}.md`
in this directory. One fold agent (`claude-opus-5-5`, high). Each finding was checked against the
files before its disposition. Owner rulings of 2026-09-28 (S4 to S7 in the spec) settled the
review's forks before the fold.

Prefixes: `A-` anthropic, `C-` contract, `K-` mechanics, `S-` consistency.

**Counts.** 73 findings (70 numbered, two unnumbered anthropic notes, one anthropic owner fork).
66 folded (two carry a partial refusal), 3 refused, 4 resolved by owner ruling (C-M9, S-m4, A-m6, A-fork). Duplicates fold once and list every id. New
owner forks: none.

## Verification notes

Checked against the tree before folding:

- `pass-execute.js:37-40` and `:57-58` state the runner has no filesystem or exec access;
  `:246` holds the repo-neutral reduced default; `pass-execute-chains.js:164` and `:249`
  hardcode npm. The AW-01 rejection design could not be built as written.
- `cairn-run-gate:107-108` prints "vanished" then falls through to `gate exit: 1`; `:47` already
  exits 2; `:129` passes the gate's status through. `scripts/githooks/pre-commit` ends in
  `exec gitleaks`.
- `git show a7dd5ad` carries all three rulings; `git diff a7dd5ad 0a2e391` shows the per-commit
  bullet restored, "the repo's full gate" restored, and the superpowers-yield sentence dropped.
  A grep over `skills/`, `docs/`, `agents/`, and `CLAUDE.md` finds no "write-first" anywhere.
- The memory docs page (fetched 2026-09-28) directs commit rules to "set the attribution text
  with [`attribution`](/docs/en/settings-reference#attribution)". `claude/.claude/settings.json`
  has no `attribution` key. `cairn-implementer.md:58` and `site-implementer.md:51` hardcode the
  generic footer.
- The style-guide-sync plan's Gates block sets `gate` and no `reducedGate` for chain W, and its
  `notes` carry the spec path plus the definition-of-done override.
- `spec-plan-review/SKILL.md:95,124` are reviewer lines at `high`; `:99` is the fold agent.

## Roots folded once

| Root | Finding ids | Where folded |
|---|---|---|
| AW-01 cannot be built; amendment 1 contradicted B | C-X1, K-M1, S-M3, C-m7, S-m10 (first bullet) | RC4; B1 AW-01 and AW-04 rows; amendment 1; B acceptance. Reduced gate resolves explicit, then named gate, then repo-neutral default; nothing rejected; `notes` keep the spec path |
| Ratchet enforcement | C-M1, K-X1, C-X2, K-X2, S-M4, S-m8, C-m4, K-m6, C-M7 | "The ratchet baseline" (registry, pre-commit per-commit check against HEAD, one growth event, re-key rule, file-pair keying with falling count); amendment 8; "sanctioned parity copy" dropped from E's test; merge-base clause and stale-branch risk removed |
| The `0a2e391` regression | S-M1, S-M2 | RC3 evidence paragraph; B4's repair row, DC-01 and DC-03 rows, superpowers-yield row, History row; Owner decisions rewritten |
| Pass E routing | S-M5, A-M1, A-M2, S-m5, A-m1 (Git Conventions trim) | E's routing ledger, Anthropic order, 200-line target, `omitClaudeMd` in `seats.json`, DaisyUI placement, `claude-tooling.md` citation |
| `/doctor prompt-audit` | A-M3 | A0 before AC3 seeds; E close; each F chore; "input, never a gate" |
| Pass B concrete success test | C-M2 | Goals; "Pass B acceptance" (zero A/B entries, dry render with named checks, workaround grep); item 4 of C-M2 as amendment 9 |
| Repo scope of cross-repo and `check-drift` | C-M4, K-M5, S-m7 | A-rest cross-repo mode (explicit repo list, `--repo-root`, stale cross-repo entry as NOTE, context budget as a baselined check id) |

## Dispositions

### Anthropic

| Id | Disposition |
|---|---|
| A-M1 | Folded: RC1, RC8, E, A-rest budget cap, E success test. The combined budget across the chain is refused: Claude Code already warns natively on a combined limit at session start |
| A-M2 | Folded: RC8, A-rest seat check, E |
| A-M3 | Folded (root above) |
| A-m1 | Folded: S7, B3, B4, E trim of Git Conventions |
| A-m2 | Folded: A-rest seat check (cite `seats.json` directly); B4 PS-14 points at "Current state" until then |
| A-m3 | Folded: D (reference file, both skills under 500 lines). The optional 500-line check is refused: two instances, both fixed by hand in D, no recurrence evidence |
| A-m4 | Folded: C and D trigger checks for the five named skills (DC-24 shows trigger loss is live here) |
| A-m5 | Refused: closes and the weekly run already catch the same defects; a write-time hook adds latency to every edit under `.claude/`. Recorded in Out of scope |
| A-m6 | Owner ruling S6 |
| A-m7 | Folded: B4 DC-04 row tool-neutral; B1 NOTE names the guards doc's wake-up; C2 evaluates `/goal` |
| A-m8 | Folded: B5 merged into B4 |
| A-m9 | Folded: `seats.json` `why` field; effort sweep filed to dotfiles `ROADMAP.md` (owed, A-rest) |
| A-note collision direction | Refused: no agent or workflow collision exists today; cheap to add when one appears |
| A-note `claude plugin validate` | Refused as spec text: an implementation method, left to the AC2 implementer |
| A-fork | Owner ruling S6 |

### Contract

| Id | Disposition |
|---|---|
| C-X1 | Folded (AW-01 root) |
| C-X2 | Folded (ratchet root) |
| C-M1 | Folded (ratchet root); the registry lives in the baseline file, append-only, with each id tied to an implementing tool, so an emptied check cannot regrow |
| C-M2 | Folded (B success test root) |
| C-M3 | Folded: AC3 names seeded phrases with witnesses; A-core close prints per-id seed counts, zero only with a named reason |
| C-M4 | Folded (repo scope root) |
| C-M5 | Folded: "Roots" bullet in the ratchet section |
| C-M6 | Folded: A-core per-task line (one failure-state table, one fixture per row); AC1 fixture list. The pre-commit NOTE row is moot (NOTE dropped) |
| C-M7 | Folded: amendment 8 |
| C-M8 | Folded as a drop: the pointerless-spec check is removed; C fixes AW-18 by hand |
| C-M9 | Owner ruling S4 |
| C-m1 | Folded: A-rest calibration against self-mode ids plus a named negative set; new-`GA-nn` count as noise measure |
| C-m2 | Folded: B intro (each row that retires text appends its phrase), B3 mechanical acceptance, B4 phrases, `model-economy.md:38` in B4 |
| C-m3 | Folded: B2 AW-17 (exit 75, no `gate exit:` line, bounded counter; a gate exiting 75 is told apart by its `gate exit:` line) |
| C-m4 | Folded (ratchet root, re-key rule) |
| C-m5 | Folded: A-rest cross-repo quoted-version check, DC-14 lettered F |
| C-m6 | Folded: ratchet section (runs before `exec gitleaks`, fail-closed kept) |
| C-m7 | Folded (AW-01 root, amendment 1) |
| C-m8 | Folded: per-task gate, review bar, and test mandate stated for A-core and B; B3 and B4 take mechanical acceptance |
| C-m9 | Folded: B1 asserts the launch NOTE; B2 asserts no vanished clause; the eight sync-owned ids are mapped in the amendments preamble |

### Mechanics

| Id | Disposition |
|---|---|
| K-X1 | Folded (ratchet root) |
| K-X2 | Folded (ratchet root); N-way clusters and N-way parity groups in A-rest |
| K-M1 | Folded (AW-01 root) |
| K-M2 | Folded: AC2 `lint --root` by repo-relative path in `check.sh`; machine checks and collisions in `verify`; unknown args exit 2 |
| K-M3 | Folded: AC3 self mode rewrites `~/.claude/<dir>` and `~/.local/bin/<x>` to the tree under test |
| K-M4 | Folded: RC4 and A-rest cross-repo bare-path rule (one repo or none fails; multi-repo and placeholders pass) |
| K-M5 | Folded (repo scope root) |
| K-M6 | Folded: A-rest `check-drift --only claude`; A-core acceptance uses `claude-tooling-sync verify` directly |
| K-M7 | Folded: B2 AW-17; the "Open for the plan" exit-code item is resolved and removed |
| K-M8 | Folded: B1 AW-13 (optional `args.classifier`; else one cached `haiku` existence probe per chain repo) |
| K-m1 | Folded: A-rest heading citation accepts both house forms |
| K-m2 | Folded as a drop (with C-M8) |
| K-m3 | Folded: `GA-nn` per-check and per-file-pair summary; Geoff sees only ownerless entries |
| K-m4 | Folded: B1 parity via markers and `new Function`, helpers included, `pass-core` held to class names, reviewer model, and lane |
| K-m5 | Folded: A-rest `seats.json` agent-to-seat map; a missing `effort:` is a violation |
| K-m6 | Folded: the registry resolves cross-tool ids; the open item narrows to module-or-parsers |
| K-m7 | Folded as a drop: the pre-commit ruling NOTE is removed from RC3 |
| K-m8 | Folded: A-rest fails any quoted version range (with C-m5) |
| K-m9 | Folded: A-core and B record merge SHAs; Risks names `git revert -m 1` |
| K-m10 | Folded: B2 Files and AW-20 row include `docs-page-chain.js:198`; amendment 7 lists the file |
| K-m11 | Folded as moot: the short-phrase rule is dropped (with S-M6) |

### Consistency

| Id | Disposition |
|---|---|
| S-M1 | Folded (regression root) |
| S-M2 | Folded (regression root): the rule stays in CLAUDE.md for branch work outside passes |
| S-M3 | Folded (AW-01 root) |
| S-M4 | Folded (ratchet root, amendment 8) |
| S-M5 | Folded (E routing root) |
| S-M6 | Folded: no length rule; literal case-insensitive substring semantics shared with the R8 twin; amendment 2 gives R8 the dotfiles path |
| S-m1 | Folded: B4 `go-ship` runs the repo's `simplify` skill when one exists, else `code-simplifier` |
| S-m2 | Folded: B3 DC-29 agent-side row |
| S-m3 | Folded: PS-15 removed from the seat check's baselined list; C2 scoped to `:95` and `:124`, `:99` stays `high`; Owner decisions updated |
| S-m4 | Owner ruling S5 |
| S-m5 | Folded (E routing root) |
| S-m6 | Folded: C2 DC-17 cites the 2026-09-12 task 4 as superseded; A-core pre-bake repoints STATUS and drops the owed pointer line |
| S-m7 | Folded (repo scope root) |
| S-m8 | Folded (ratchet root): one growth event; threshold change is a new id; "sanctioned parity copy" dropped |
| S-m9 | Folded: the retired-phrase check scans vendored skills, matching W6; the other checks keep excluding them |
| S-m10 | Folded: amendment 1 keeps the spec path; amendment 2 drops W6's test-first mandate; amendment 5 covers all five voice files |
| S-m11 | Folded (with C-m8) |

## Refusals, in one place

Three findings refused outright: the write-time hook (A-m5), the agent and workflow collision
direction (A-note), and `claude plugin validate` as spec text (A-note). Two folds carry a partial
refusal: the combined context budget (A-M1) and the 500-line check (A-m3). Three folds are drops
the owner's brief named as low-value unless a finding showed otherwise, and none did: the
pointerless-spec check (C-M8, K-m2; about one true defect in 13 hits) and the pre-commit ruling
NOTE (K-m7; the retired-phrase tool and the `pass-core` step cover supersession).

## Owner rulings recorded

S4 (split A), S5 (simplifier languages), S6 (`disable-model-invocation` on `go-ship` only), S7
(DC-29, with the `attribution` route verified). Each is dated 2026-09-28 and attributed in the
spec's "Sequence and rulings".

## Rulings for Geoff

None. One consequence of the AW-01 fold (reduced gate defaults to the named gate) is recorded as a risk, not a fork: a task that names
its gate and no `reducedGate` now runs the full named gate on a reduced round. A cairn plan that
wants the cheaper round sets `reducedGate`.

## Owed errata

- `docs/HISTORY.md` (dotfiles): `0a2e391` reverted three `a7dd5ad` rulings, a one-executor-rule
  incident. Lands in B4.
- The audit record's section 1 line "code-simplifier per commit (global CLAUDE.md) against once
  per pass" should read "reverted by `0a2e391`"; the audit also missed the superpowers-yield loss.
  Append an erratum note to the record at A-core's pre-bake.
- The 2026-09-12 infra round plan, task 4 (`instructions/ai-operational-rules.md`), is superseded
  by DC-17. Cited in C2.
- `claude-tooling.md:95-96` cites a CLAUDE.md heading that E moves. Fixed in E's commit.
- `model-economy.md` "Current state" keeps its heading when its values move to `seats.json`.
  A-rest.
- The effort sweep (Sonnet implementers at `high`, the unmeasured `xhigh`/`max` ladder) is filed
  to the dotfiles `ROADMAP.md` for `model-economy.md`'s owner. A-rest.
- dotfiles `docs/STATUS.md` still names docs-standard plan two as the next action and owes an
  aksailingclub-org pointer line. A-core pre-bake.
- The spec's first draft stated the DC-01 CLAUDE.md bullet "predates" the ruling; it is a
  regression. Corrected in this revision.
