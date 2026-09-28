# Claude infra sweep

Design basis for the plans of passes A and B, and the outcome frame for passes C, D, E, and F.
Evidence: the read-only audit at
`/var/home/glw907/.dotfiles/claude/.claude/docs/record/2026-09-28-claude-infra-audit.md`
(87 findings, root causes RC1 to RC8, the guard proposal, pass triage A to F, and the section 6
amendments to the style-guide-sync plan). Finding ids below are the audit's. The downstream plan
is `/var/home/glw907/Projects/cairn-cms/.claude/worktrees/style-guide-sync/docs/superpowers/plans/2026-09-28-style-guide-sync.md`.

**Status:** draft for adversarial review through `spec-plan-review`. The "Anthropic practice"
section is a stub the review fills.

## Goals

Geoff, 2026-09-28, after reading the audit: "let's actually run that first, and then implement
this plan using the improved and correct infra." And: "If the changes are anything but small and
simple, a spec with adversarial review."

The sweep has three goals.

1. The style-guide-sync plan runs on infra that carries no defect the audit named on its path.
2. Each mechanical defect class gets a check that fails on a new instance, so the sweep does not
   have to be repeated by hand.
3. Each rule has one owner, placed where it executes, and every other home becomes a pointer or
   is deleted.

**Success tests.**

- After A and B: the style-guide-sync run (chains R and W, the join, the close) hits no infra
  defect the audit named. Every workaround the plan carries for one (the chain W `notes` override
  of the implementer's definition of done, any `reducedGate` pin added for AW-01, W6's deferral
  of `claude-tooling-sync verify` to the boundary) is removed from the plan before it runs.
- After E: the duplicate-paragraph baseline and the reference baselines are empty, or each
  remaining entry is a sanctioned parity copy. Entries keyed to a pass F chore that has not run
  yet are the one allowed remainder, and they are listed by repo in E's close.
- Throughout: the ratchet baseline's size is the remaining work. It never grows after pass A
  seeds it.

## Sequence (rulings S1 to S3)

**S1 (Geoff, 2026-09-28).** One spec covers the whole sweep. The order is:

1. Pass A, the guard (dotfiles).
2. Pass B, the execution path (dotfiles).
3. The style-guide-sync plan, amended per "Amendments to the style-guide-sync plan" below.
4. Passes C and D in parallel (dotfiles, disjoint files).
5. Pass E, consolidation (dotfiles).
6. Pass F, one chore per repo, any time after A; cairn-cms only after the style-guide-sync merge.

A and B are planned in full now. C, D, E, and F are planned later, each from its outcome list
here plus the baseline as it stands then.

**S2 (Geoff).** Poplar's vendored glw907 Vale overlay is canonical. Drop the references to a
missing canonical style and a re-sync script (DC-25's gap, DC-12). Lands in pass F.

**S3 (Geoff).** DC-28's three voice files outside W4's Files are folded into the
style-guide-sync plan's W4, not left to pass C.

**Ruling 12 of style-guide-sync (Geoff).** "The cairn overlay or the cairn docs voice is
absolutely a house voice, so the workstation charter is wrong." A repo may carry a named house
voice as a recorded overlay on a published base standard. W4 lands the charter correction; this
sweep writes nothing that contradicts it.

## Root causes and design responses

The audit groups the findings into eight causes. Four carry most of the weight and get a
structural response. The other four get a smaller one.

### RC1. Rules restated instead of routed (about 25 findings)

**Response: one owner per rule, the rest pointers, drift made visible.**

- The owner is chosen by where the rule executes, in the workstation order: a tool or its output,
  a runner, an agent definition or skill, then CLAUDE.md. `~/.claude/docs` holds rationale only.
  The audit's section 4 table is the ownership map; pass E executes it, and passes B, C, and D
  execute the rows their findings touch.
- Where two executors genuinely need the same text at write time (the two implementer
  definitions), the copies are sanctioned: declared in a parity list and held byte-identical by a
  check.
- Every other copy is found by the duplicate-paragraph check (pass A) and baselined until its
  pass removes it.
- Rules that a tool enforces move into that tool's output. `cairn-run-gate` prints the vanished-run
  instruction (AW-17), and the runners print the runaway-guard and `/loop` NOTE at launch
  (DC-04), so prompts and CLAUDE.md stop restating them.

### RC2. No reference-integrity check (about 18 findings)

**Response: the pass A guard.** Dead paths, cited headings, cited memories, relative links,
orphan docs, pointerless "the spec", vendored sibling names. Each is a check with a ratchet
baseline (see Pass A).

### RC3. A new ruling lands in one home and older homes are never swept

**Response: the supersession sweep rule.** Any commit that lands a ruling superseding existing
text adds the superseded phrases to the retired-phrase list in the same commit, and removes or
marks (`retired-ok`) every hit. The rule is placed where it executes, strongest form first:

1. **Tool.** The retired-phrase check (pass A) fails on any listed phrase outside a `retired-ok`
   line. Its failure message states the rule, so the fixer learns it at the point of failure.
2. **Tool NOTE.** The dotfiles `scripts/githooks/pre-commit` prints a NOTE when a staged diff
   under `claude/.claude/` adds a dated ruling marker (`(Geoff, YYYY-MM-DD`) and leaves
   `retired-phrases.txt` untouched. It does not block, because not every ruling supersedes text;
   the workstation rule "act on a tool's NOTE before the next dispatch" makes it binding in
   practice.
3. **Skill.** The `pass-core` close skeleton gains one step: each ruling folded this pass that
   supersedes text carries its retired phrases in the same commit. The cairn-cms twin list (the
   style-guide-sync plan's R8) takes the same step through `cairn-pass`.

No CLAUDE.md line is added; the three homes above reach every executor that lands a ruling.

### RC4. cairn-cms shape assumed by workstation-wide infra

**Response: repo-neutral runners, agents, and skills.**

- A runner never assumes npm. When a task's gate cannot be inferred for the checkout (no
  `package.json`, no classifier), the runner requires an explicit gate and reduced gate and
  rejects the run at launch if either is missing (AW-01). Probes run only when the classifier
  exists (AW-13).
- An agent or skill never cites a repo-relative path bare. It writes the path absolute, or
  prefixed with its repo (`cairn-cms/docs/...`), which the reference check resolves under
  `~/Projects/<repo>` (AW-14, AW-15, PS-21).
- A skill that needs a repo's layout reads it from that repo's CLAUDE.md or STATUS and has an
  explicit branch for its absence (PS-08, PS-09, PS-10; pass C).
- An agent's definition of done is the gate its dispatch names, never a fixed npm list (AW-19).

### Smaller causes

- **RC5, context the executor lacks.** A `context: fork` skill takes explicit arguments and ends at
  its report (PS-06, PS-20); the fork-skill lint (pass A) holds the line. A zero-context agent
  gets paths, never "the spec" (AW-18). A report shape conflicting with a runner's schema yields
  to the schema (AW-19).
- **RC6, vendored skills with no overlay.** The vendored manifest gains a description override and
  a local precedence note applied on fetch (CS-8, CS-10, CS-17), and `fetch_skill` rewrites
  sibling names (CS-6). Pass D.
- **RC7, dated facts in present tense.** Files that load on every dispatch carry no toolchain
  version, engine pin, or token id as current fact; they point at the source that states it
  (CS-3, CS-4, CS-12, DC-07, DC-11, DC-14, AW-23). The quoted-version-pin check (pass A, close
  steps) guards the repo CLAUDE.md case.
- **RC8, always-loaded context carrying on-demand content.** Cairn-only and pass-only sections
  leave the global CLAUDE.md for their owners (DC-19, DC-21); `claude-context-budget` runs over
  every `@`-import at close and weekly (DC-02); long always-listed descriptions are capped (pass A
  check, fixes in C and D).

## Pass A: the guard

**Class** `engine-logic`. **Repo** `~/.dotfiles`, worktree
`~/Projects/.worktrees/dotfiles-infra-a` on branch `infra-sweep-a`, merged `--no-ff` to `main`.
**Gate** `bash scripts/check.sh`, light lane. Three tasks, sequential. Findings closed outright:
PS-01, CS-9, AW-16. Every other mechanically detectable finding enters the baseline.

### The ratchet baseline

One file, `claude/.claude/tooling/ratchet-baseline.json`, read by both tools.

- **Entry shape.** Check id, file (relative to its root), a fingerprint that survives line moves
  (the unresolved path, the phrase, the cited heading, the paragraph pair's shingle hash), the
  owning finding id, and the pass letter that removes it.
- **Seeding.** Pass A seeds the file with today's violations. Each maps to an audit finding id.
  A violation the audit did not name gets an id `GA-nn`, a one-line defect, and a pass letter,
  and pass A's close lists every `GA-nn` for review.
- **Shrink only.** The checker compares the file to its copy at `git merge-base HEAD main`. An
  added entry fails. The one sanctioned growth is a commit that adds a new check id: entries for
  that id may appear in the same commit that introduces the check, and never later.
- **Stale entries fail.** An entry whose violation no longer exists fails with "remove this
  baseline entry." The baseline therefore always equals the remaining work.
- **Failure states.** File absent: fail (config error). Present and empty: pass. Malformed (bad
  JSON, missing field, unknown check id, unknown finding id format): fail, naming the entry.
- **Exit codes**, shared by both tools: `0` clean, `1` violations, `2` configuration error
  (a missing or malformed list, baseline, or parity file). A run reports every violation grouped
  by check with a count per check, never only the first.

### Task A1. `claude-tooling-sync` checks

**Outcomes.**

Files: `bin/.local/bin/claude-tooling-sync`, `claude/.claude/tooling/` (manifest, `seats.json`,
the baseline), `claude/.claude/skills/ship/` renamed to `go-ship/`, fixtures under `tests/`.

- **`--root <tree>`** selects the tree to verify; the default is the script's own repo, and the
  docstring matches (AW-16). A worktree can be verified before merge.
- **Skill name collision.** A personal skill whose name equals any
  `~/Projects/*/.claude/skills/<name>` fails, since personal shadows project. Fixed now: the
  personal `ship` becomes `go-ship` with the generic triggers dropped (PS-01).
- **Unmanifested third-party skill.** A `skills/<dir>` carrying a `LICENSE*` with no manifest
  entry fails. Fixed now: `vhs-cli-demos` gets its manifest entry (CS-9).
- **Vendored sibling names.** A backticked "`<name>` skill" in a vendored skill must name an
  installed skill. Baselined (CS-6, pass D).
- **Description override and cap.** A manifest `description` override must match the installed
  file. A description without a `paths:` gate over 500 characters fails. Baselined (CS-8, CS-17,
  PS-28).
- **Fork-skill lint.** A `context: fork` skill body may not contain "under discussion", "during
  the session", "delegated", or an instruction to ask the user. Baselined (PS-06, PS-20).
- **Seat check.** A machine-readable seat table at `claude/.claude/tooling/seats.json`, derived
  from `model-economy.md` "Current state", which then points at it for the values and keeps the
  why. Every user-scoped and project-scoped agent's `model` and `effort` must match its seat.
  Baselined (DC-11 in F, PS-15 in C). An agent with no seat fails.

**Rule per failure state.** Seat table or manifest absent or malformed: exit 2. An agent file with
unparseable frontmatter: a violation naming the file.

**Where it runs.** `scripts/check.sh` calls `claude-tooling-sync verify --root .` for the checks
over the dotfiles tree, including the collision check (its fix is always in dotfiles, because the
personal skill is the shadowing party). Project-agent seats run under `check-drift` (already
calls verify) and at the close steps, since a project's agent is fixed in that project.

**Fixtures.** For each check, one fixture tree that must fire and one that must pass, plus the
absent, empty, and malformed states of `seats.json` and the baseline, a stale baseline entry, and
a grown baseline.

### Task A2. `scripts/check-claude-refs.py`

Python, under `python-conventions` (PEP 257, the ruff D config `check.sh` already runs). Wired
into `scripts/check.sh`. Scan scope: `claude/.claude/agents`, authored `skills` (excluding
vendored and `skills/synced/`), `workflows`, `docs` (excluding `docs/record/`), `output-styles`,
`instructions`, and `CLAUDE.md`; excluding `evals/research/`, dated files, the list files, and
the fixtures. This scope matches the style-guide-sync plan's W6 scope, so W6 needs no second
scanner.

**Two modes.** Self mode (`check.sh`) resolves references inside the dotfiles tree, `~/.claude`,
and absolute paths outside `~/Projects`. Cross-repo mode (`--repo <name>`) resolves every
reference from the dotfiles tree into `~/Projects/<name>` and the checks over that repo's own
CLAUDE.md. Principle: a check whose failure is caused by another repo's change runs at that
repo's close and weekly, so the dotfiles gate never goes red on another repo's state, and the
close of the repo that moved a file catches the break it caused.

**Checks, each a rule plus its failure states.**

| Check | Rule | Baselined findings |
|---|---|---|
| Dead reference | every backticked path resolves; absolute and `~/` as written; a repo-relative path in an agent or skill must be absolute or repo-prefixed, and a bare one fails | AW-08, AW-14, AW-15, PS-03, PS-21, CS-3 and CS-4 (paths), DC-08, DC-12, DC-13 (paths) |
| Heading citation | a quoted phrase after a cited file (`` `file.md` ("Heading") ``) matches a heading in that file | DC-13, DC-15, DC-18 |
| Memory citation | "`<name>` memory" resolves to `~/.claude/projects/*/memory/<name>.md` | DC-09 |
| Relative link | every `[x](relative)` under `docs/` resolves | DC-10 |
| Orphan doc | each file under `docs/` (excluding `record/`) and `instructions/` is cited by a CLAUDE.md, skill, agent, or workflow | DC-17 |
| Pointerless spec | "the spec" or "the plan" in an agent definition has a path on the same line | AW-18 |
| Retired phrase | a phrase in `claude/.claude/tooling/retired-phrases.txt` fails outside a `retired-ok` line, case-insensitive; the list's header names its cairn-cms twin | DC-01, DC-04, DC-06, DC-30, PS-04, PS-05, AW-07 ("sleep 30"), CS-4 ("currently 1.26") |
| Duplicate paragraph | 12-word shingle overlap above a threshold between any two of agents, authored SKILL.md files, output styles, CLAUDE.md, and docs; pairs in the parity list must be byte-identical between their markers | AW-04, AW-20, AW-21, AW-22, AW-24, CS-13, DC-21, DC-22, DC-28, PS-25 |

Failure states specific to A2:

- **Retired-phrase list** absent: exit 2. Present with no phrase: exit 2 (an empty list is a
  vacuous tripwire). A phrase shorter than three words is allowed only when marked exact.
- **Parity list** (`claude/.claude/tooling/parity.json`) absent: exit 2. Empty: pass. A declared
  copy whose marker is missing in either file: violation. Copies differing by a byte: violation
  showing the first differing line.
- **Duplicate threshold.** Calibrated so every "confirmed" duplication row in the audit's section 4
  fires and the sanctioned implementer checklist, once declared, passes. The calibration evidence
  goes in the script's header.
- **Many bad.** All violations reported, grouped, with counts; the summary line names the
  baseline's remaining size per pass letter.

Seeded phrases: pass A seeds only phrases already superseded by a ratified ruling (the RC3 rows
above). The style-guide-sync phrases ("no house voice" and the rest) are appended by W6 once W2 to
W5 remove them, so the list never starts red.

**Fixtures** under `tests/claude-refs/`, run by the pytest step `check.sh` already carries: per
check, a must-fire and a must-pass tree; absent and empty retired-phrase list; absent, empty, and
malformed parity list; a parity pair differing by one byte; a `retired-ok` exemption; a bare
repo-relative path in an agent; a baseline that grew, one with a stale entry, and one that is
empty.

### Task A3. Close-step and weekly wiring

**Outcomes.**

- `pass-core`'s close skeleton gains a step: run the reference checker in cross-repo mode over the
  closing repo, `claude-tooling-sync verify` for that repo's project agents, and
  `claude-context-budget` over the repo's CLAUDE.md and every `@`-imported file. `cairn-pass` and
  `site-pass` supply the commands.
- The same step checks each dependency range quoted in the repo's CLAUDE.md against its
  `package.json` (DC-14's class).
- The `pass-core` close skeleton gains the supersession step (RC3, item 3), and
  `scripts/githooks/pre-commit` gains the ruling NOTE (RC3, item 2).
- `check-drift` runs the cross-repo mode and the context budget for every repo under `~/Projects`
  that has a CLAUDE.md, with repo-scoped entries in the same baseline.

**Acceptance for pass A.** `bash scripts/check.sh` green on the worktree with the seeded baseline;
every fixture above passing; `claude-tooling-sync verify --root <worktree>` green; `check-drift`
green on the merged `main`; the baseline summary printed in the close, per pass letter and per
finding id, with every `GA-nn` listed.

## Pass B: the execution path

**Repo** `~/.dotfiles`, worktree `~/Projects/.worktrees/dotfiles-infra-b` on branch
`infra-sweep-b`, created from `main` after pass A merges. **Gate** `bash scripts/check.sh`, light
lane. Twenty findings plus AW-11's interim parity test. Implementer-definition edits land here so
the style-guide-sync plan's W5 branches from them. Each finding's entries leave the baseline in
the commit that fixes it.

### B1. Runners (`engine-logic`)

Files: `claude/.claude/workflows/pass-execute.js`, `claude/.claude/workflows/pass-execute-chains.js`,
new tests under `tests/` in the pattern of `tests/docs-page-chain-derivation.test.mjs`, run by
`check.sh`.

| Finding | Outcome |
|---|---|
| AW-01 | No npm default. A checkout with no `package.json` and no explicit `reducedGate` is rejected at launch with a named reason; the class default applies only where its commands exist |
| AW-02 | Chains uses the same gate matcher as `pass-execute.js`: a wrapper, a `cd` prefix, and multi-line stdout all match |
| AW-03 | Any reduced round is exempt from the MISMATCH block; no prompt carries both MISMATCH-blocking and "reduced is expected" |
| AW-04 (runner side) | One reduced-gate constant per runner, rendered into every prompt that names it |
| AW-05 | The unread severity field is deleted from the schema and from the prompt |
| AW-06 | The header describes the runner generally; "committed in this repo" becomes "an absolute path"; the "Ruled inputs" section is optional |
| AW-12 | Chains `IMPL_SCHEMA` carries `mutationLedger`, so the `auth-data` mandate can be met |
| AW-13 | The classifier probe runs once per run, only when the classifier exists, on `model: "haiku"`; the classifier paragraph renders only when it exists |
| DC-04 (tool half) | Each runner prints the runaway-guard and `/loop` NOTE at launch |
| AW-11 (interim) | A parity test holds `PASS_CLASSES` deep-equal across both runners and the `pass-core` table; the merge waits for pass E |

Test assertions (the audit's runner row): parity; every field a mandate cites exists in
`IMPL_SCHEMA`; every `REVIEW_SCHEMA` field is read; the matcher accepts the three forms; a
no-class reduced round renders no MISMATCH line; a no-classifier run spawns no probe; no `agent(`
call lacks `model:`; a no-`package.json` run with no `reducedGate` is rejected.

### B2. Gate tool (`engine-logic`)

Files: `bin/.local/bin/cairn-run-gate`, its test.

| Finding | Outcome |
|---|---|
| AW-17 | A vanished gate run exits with its own code (distinct from 0, 1, and 75) and prints the instruction to re-issue; no prompt carries a vanished clause |
| AW-20 | The gate protocol lives in `cairn-run-gate`'s output. Each runner prompt and implementer carries one line: run the gate through `cairn-run-gate` and follow its output. The restated paragraphs in `cairn-implementer.md` and `site-implementer.md` are deleted; `pass-gate-economy.md` keeps the rationale |

### B3. Agent definitions (`docs`)

Files: `claude/.claude/agents/cairn-implementer.md`, `site-implementer.md`, `diff-reviewer.md`.

| Finding | Outcome |
|---|---|
| AW-19 | Done means the gate the dispatch names. Where a runner requests a structured schema, the schema replaces the text report shape |
| AW-23 | The dated compatibility note is deleted from both implementers |
| AW-04 (reviewer side) | `diff-reviewer` says "the reduced gate the dispatch names" and defines none of its own |
| AW-05 (reviewer side) | The severity-as-routing claim is deleted |

### B4. Global CLAUDE.md and pass skills (`docs`)

Files: `claude/.claude/CLAUDE.md`, `claude/.claude/skills/pass-core/SKILL.md`,
`claude/.claude/skills/site-pass/SKILL.md`, `claude/.claude/skills/cairn-pass/SKILL.md`,
`claude/.claude/skills/go-ship/SKILL.md` (renamed in A).

| Finding | Outcome |
|---|---|
| DC-01 (+PS-13) | code-simplifier runs once per pass or branch, at the close, only when TypeScript, Svelte, or Go changed (the 2026-09-27 ruling; see "Owner decisions"). `pass-core` owns it. The per-commit bullet and the "straight through the gates and code-simplifier" wording in the global CLAUDE.md become one pointer line. `go-ship` dispatches `code-simplifier:code-simplifier` once as its close step. The superseded phrasing enters the retired-phrase list |
| DC-03 (+PS-16) | "The repo's full gate" per task becomes "the class's per-task gate (`pass-core`)" in the global CLAUDE.md and `site-pass`. Repo copies are pass F |
| DC-04 (text half) | The unattended-work line says the tools hold the sleep inhibitor, and the session arms the runaway guard and a `/loop` wake-up at launch |
| PS-14 | `pass-core`'s escalation points at `model-economy.md` "Current state" (which includes `max`) and restates no ladder. cairn CLAUDE.md is pass F |
| PS-22 | `cairn-pass` close drops the separate `npm run check`, since `check:close` runs it |
| DC-29 | The co-author footer bullet is deleted; the harness attribution owns the trailer (pending the owner confirmation below) |
| DC-30 | The pre-bake step says to update STATUS, and memory only for a preference or a ruling's why |

### B5. Delete the spent workflow

AW-07: `claude/.claude/workflows/cairn-overnight-to-release.js` is deleted, and its skill-listing
entry goes with it. "sleep 30" leaves the baseline.

### Pass B acceptance

`bash scripts/check.sh` green; every B entry gone from the baseline; the runner tests passing;
`claude-tooling-sync verify` green on the merged `main`. A dry launch of `pass-execute-chains`
against a dotfiles worktree with no `reducedGate` is rejected at launch with the AW-01 reason, and
with an explicit one it renders prompts carrying no npm command.

## Amendments to the style-guide-sync plan

Applied by that plan's conductor at pre-flight, after B merges. These are the audit's section 6
items plus rulings S2 and S3.

1. Chain W needs no `reducedGate` workaround (AW-01) and no `notes` override of the implementer's
   definition of done (AW-19). Both come out of the plan's Gates block.
2. W6 appends its phrases to pass A's `retired-phrases.txt` and adds fixtures for them. It adds no
   second check to `scripts/check.sh`; pass A's scanner already covers W6's scope.
3. W6's acceptance runs `claude-tooling-sync verify --root <worktree>` inside the chain, and the
   segment B boundary step 3 stays as a post-merge confirmation.
4. The plan keeps invoking `pass-execute-chains` by name; the runner merge (AW-11) waits for pass E.
5. S3: W4's Files gain the three voice files outside it (DC-28), with the measures section
   removed and the Go register's missing repo and wrong linter corrected.
6. S2: DC-25's poplar gap is out of W4. Poplar's overlay is ruled canonical and its stale
   references go in pass F.
7. The chain W worktree is created from dotfiles `main` after B merges. P1's claim check re-runs,
   since B moves line numbers in files W edits (`cairn-implementer.md`, `site-implementer.md`,
   `CLAUDE.md`).

## Passes C, D, E, F (planned later)

Outcome level only. Each is planned from this list plus the baseline at its start.

**Pass C: process skills and workstation docs** (after style-guide-sync, which edits
`register-check`). Split at the natural seam.
- C1, cairn-facing skills: PS-02 and PS-04 (the release and consult gates become
  `npm run check:close`), PS-03, PS-05 (alt rules point at the register's Visuals), PS-06 (explicit
  args; the caller binds tells), PS-17 (one "Facts consulted" definition, added to the plan
  template), PS-18 (delete the pass-end draft clause), PS-19, PS-28, AW-14, AW-15.
- C2, site and generic skills plus docs: PS-08 (absent-guide branch), PS-09 (paths from the site's
  CLAUDE.md or STATUS), PS-10 (`backlog: false`, `backlog_path`), PS-11 (close to HISTORY.md, read
  existing tiers), PS-12 (delete), PS-15 (spec-plan-review reviewers to the seat table's
  `medium`), PS-20, PS-21, AW-18, DC-06, DC-07, DC-08, DC-09 (inventory side), DC-16, DC-17
  (delete; the `--name` fact moves to the inventory), DC-23.

**Pass D: convention skills and the vendored manifest** (parallel with C; disjoint files; its
`claude-tooling-sync` changes build on A's). CS-1 (`SilenceErrors: true`), CS-2 (precedence line
in go-conventions; elm dropped from the cobra `_why`), CS-3, CS-4 (no pinned Go version; narrowed
tag rule), CS-5, CS-6 (`fetch_skill` rewrite, then refetch), CS-7 (call `kitty-headless-shot`
directly), CS-8 and CS-10 (manifest overlays), CS-11 (copy-in source is cairn's
`eslint.config.js`), CS-12, CS-13, CS-17, DC-10 (+CS-14; `bubbletea-conventions.md` moves to
poplar as history, checklists fold into elm-conventions).

**Pass E: consolidation to owners** (after C and D). AW-11 (+PS-23; chains becomes a mode of
`pass-execute.js`, with the skill listing and plan template updated, and the parity test
retired), AW-21 (implementer copies declared in the parity list; measures to `MEASURES.md`),
AW-22 (engine-triage owns the standard), DC-19, DC-21 (+PS-24; "Conducting a pass" cut to the
budgets, the model line, and "invoke pass-core"), DC-22 (+PS-26, workstation side), PS-25
(workstation side). Close checks the E success test.

**Pass F: repo CLAUDE.md files** (one small chore per repo, each under its own one-executor
check, straight through the repo's gate).

| Repo | Findings |
|---|---|
| cairn-cms (after the style-guide-sync merge) | DC-03, PS-14, DC-18, DC-24 ("loads once a Go file is open"), DC-22 and PS-25 repo sides |
| 907-life | DC-02, DC-13, DC-14, DC-22, DC-17 stub |
| ecxc-ski | DC-02, DC-13, DC-22, DC-23 (receives the ECXC anchors), DC-17 stub |
| aksailingclub-org | DC-09 pointer, DC-15, DC-22 |
| xcathletes-org | DC-03 |
| poplar | DC-11 (repin to seats; CLAUDE.md says "per model-economy"), DC-12 and DC-25 per S2 |

## Owner decisions

**DC-01 is decided from the ratified rulings.** The 2026-09-27 ruling (`pass-gate-economy.md`,
`pass-core` close step 1) is newer and explicit: once per pass or branch, at the close, only for
TypeScript, Svelte, or Go. It names the per-commit form and retires it. The global CLAUDE.md
bullet predates it. No question.

**PS-15 is decided from the seat table.** Reviewers sit at `medium` (Geoff, 2026-09-23); the
skill's `high` has no recorded reason. No question.

**One confirmation, DC-29 (taste).** Deleting the global CLAUDE.md footer bullet lets the
harness's model-named trailer (`Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`) replace
the generic `Co-Authored-By: Claude <noreply@anthropic.com>` in every repo. Recommendation: delete
the bullet. The harness knows the model, and the model name in history supports the model-economy
audits. If Geoff prefers the generic form, the bullet stays and the harness defers to it.

## Anthropic practice

Stub. The adversarial review's best-practices lens fills this section with current Anthropic
guidance published since the Opus 5.5 release, each item with its source URL and the part of this
design it confirms or changes. Not written from memory.

## Out of scope

- Any change to cairn-cms code, docs, or its own checks. Its retired-phrase twin and `check:close`
  belong to the style-guide-sync plan (R8) and the repo.
- Re-auditing. Violations found while seeding become `GA-nn` entries; they are not fixed in A.
- The skill and agent content rewrites beyond each finding's disposition.
- A new implementer for the dotfiles repo.
- Scheduled cloud agents; `check-drift`'s weekly timer is the periodic trigger.

## Risks

- **Runner edits go live on merge.** A workflow invoked by name reads the stowed copy on `main`.
  B merges only after `pgrep` and journal checks show no running `pass-execute*` or
  `docs-page-chain` run.
- **A and B run on today's defective runners.** Both passes run per task with the Agent tool (under
  six tasks), not through `pass-execute-chains`, and each dispatch names the gate
  `bash scripts/check.sh` explicitly, overriding the implementer's npm definition of done until B3
  lands.
- **The duplicate-paragraph threshold** can be noisy or blind. Calibration against the audit's
  confirmed rows bounds both; a threshold change is a baseline-seeding event for that check only.
- **Cross-repo checks** make a repo's close depend on the dotfiles tree. The close runs the
  checker from the dotfiles `main` checkout, read-only.
- **Shrink-only on a stale branch.** A long-lived branch compares against an old merge base.
  Rebasing on `main` before merge is part of each pass's close.
- **Contention with the style-guide-sync worktree.** It must not exist until B merges, or it is
  recreated from the new `main`.

## Open for the plan

- The vanished-run exit code's value and the existing callers that branch on exit codes.
- Whether `check-claude-refs.py` and `claude-tooling-sync` share a baseline module or each parse
  the JSON (one format either way).
- The implementer seat for pass A and B tasks: `cairn-implementer` with the explicit gate, or
  `general-purpose` on `sonnet` with the implementer's report shape pasted in.
- How pass F's repo-keyed entries are labelled so E's success test can separate them.
- Token ceiling and checkpoint interval for A and for B, per the global rule.
