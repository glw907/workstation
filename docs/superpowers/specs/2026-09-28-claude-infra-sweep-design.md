# Claude infra sweep

Design basis for the plans of passes A-core and B, and the outcome frame for passes A-rest, C,
D, E, and F. Evidence: the read-only audit at
`/var/home/glw907/.dotfiles/claude/.claude/docs/record/2026-09-28-claude-infra-audit.md`
(87 findings, root causes RC1 to RC8, the guard proposal, pass triage A to F, and the section 6
amendments to the style-guide-sync plan). Finding ids below are the audit's. The downstream plan
is `/var/home/glw907/Projects/cairn-cms/.claude/worktrees/style-guide-sync/docs/superpowers/plans/2026-09-28-style-guide-sync.md`.

**Status:** revised after the four-lens review (anthropic, contract, mechanics, consistency under
`docs/superpowers/research/2026-09-28-infra-sweep-review-*.md`), then a second, narrow fold
after the fold verification (`docs/superpowers/research/2026-09-28-infra-sweep-fold-verification.md`).
Fold record, both folds: `docs/superpowers/research/2026-09-28-infra-sweep-fold.md`. Ready for
Geoff's read.

## Goals

Geoff, 2026-09-28, after reading the audit: "let's actually run that first, and then implement
this plan using the improved and correct infra." And: "If the changes are anything but small and
simple, a spec with adversarial review." The sweep front-loads its complexity into
infrastructure, so the fixes hold without a repeat by hand.

1. The style-guide-sync plan runs on infra that carries no defect the audit named on its path.
2. Each mechanical defect class gets a check that fails on a new instance.
3. Each rule has one owner, placed where it executes, and every other home becomes a pointer or
   is deleted.

**Success tests.**

- After A-core and B (the concrete test is under "Pass B acceptance"): the baseline holds zero
  entries lettered `A-core` or `B`, and a dry render of a fixture built from the style-guide-sync
  plan's two-chain arguments passes its named checks.
- At the style-guide-sync pre-flight (amendment 10): the same render over the amended plan's real
  arguments passes, and the two workarounds (the chain W `notes` override of the implementer's
  definition of done, and W6's deferral of the tooling check to the boundary) are absent from
  the amended plan.
- After the style-guide-sync close: every runner halt, escalation, or `fix` reason maps to "not
  infra" (amendment 9).
- After E: the duplicate-paragraph and reference baselines are empty. Entries keyed to a pass F
  chore that has not run yet are the one allowed remainder, listed by repo in E's close. The
  global CLAUDE.md and each in-scope repo CLAUDE.md is at or under 200 lines, or carries a
  recorded reason.
- Throughout: the ratchet baseline's size is the remaining work. It grows only in a commit that
  registers a new check id.

## Sequence and rulings

**S1 (Geoff, 2026-09-28), as amended by S4.** One spec covers the whole sweep. The order is:

1. Pass A-core, the guard's mechanics (dotfiles).
2. Pass B, the execution path (dotfiles).
3. The style-guide-sync plan, amended per "Amendments to the style-guide-sync plan" below.
4. Pass A-rest, the guard's remaining checks (dotfiles).
5. Passes C and D in parallel (dotfiles, disjoint files).
6. Pass E, consolidation (dotfiles).
7. Pass F, one chore per repo, any time after A-rest; cairn-cms only after the style-guide-sync
   merge.

A-core and B are planned in full now. A-rest, C, D, E, and F are planned later, each from its
outcome list here plus the baseline as it stands then.

**S2 (Geoff).** Poplar's vendored glw907 Vale overlay is canonical. Drop the references to a
missing canonical style and a re-sync script (DC-25's gap, DC-12). Lands in pass F.

**S3 (Geoff).** DC-28's three voice files outside W4's Files are folded into the
style-guide-sync plan's W4, not left to pass C.

**S4 (Geoff, 2026-09-28). Pass A splits.** A-core runs before B and carries the baseline
mechanics (per-commit enforcement against HEAD and a checks registry), retired phrases, dead
references, `--root`, skill-name collisions, and unmanifested licensed skills. A-rest runs after
style-guide-sync, before C and D, and carries the duplicate-paragraph check (file-pair keying
with a falling overlap count), cross-repo mode, the seat check with `seats.json`, and the rest.
The duplicate-paragraph check, and the fingerprint problems it brings, leave the sync's path.

**S5 (Geoff, 2026-09-28). Simplifier languages.** The code-simplifier ruling's "TypeScript"
includes JavaScript (`.js`, `.mjs`). Python and bash stay out. `pass-core`'s simplify step
states it.

**S6 (Geoff, 2026-09-28). Model invocation.** `disable-model-invocation: true` goes on `go-ship`
only. `cairn-release` stays model-invocable.

**S7 (Geoff, 2026-09-28). DC-29.** The global CLAUDE.md co-author bullet is deleted, and the
model-named trailer applies. The trailer's documented owner is the `attribution` setting in
`settings.json` (verified: the memory page directs commit rules to "set the attribution text
with [`attribution`](/docs/en/settings-reference#attribution)"). `claude/.claude/settings.json`
sets no `attribution` key today, so Claude Code's default, the model-named trailer, applies once
the bullet goes; nothing is written there. The hardcoded generic footers in
`cairn-implementer.md:58` and `site-implementer.md:51` go in B3.

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
  Within CLAUDE.md-class text, Anthropic's order routes the rest: a procedure to a skill, a rule
  that matters only for certain files to `.claude/rules/` with `paths:`, and only facts every
  session needs to a CLAUDE.md. The audit's section 4 table is the ownership map; pass E
  executes it, and passes B, C, and D execute the rows their findings touch.
- Where two executors genuinely need the same text at write time (the two implementer
  definitions), the copies are sanctioned: declared in a parity list and held byte-identical by a
  check.
- Every other copy is found by the duplicate-paragraph check (A-rest) and baselined until its
  pass removes it.
- Rules that a tool enforces move into that tool's output. `cairn-run-gate` prints the vanished-run
  instruction (AW-17), and the runners print the runaway-guard NOTE at launch (DC-04), so prompts
  and CLAUDE.md stop restating them.

### RC2. No reference-integrity check (about 18 findings)

**Response: the guard.** Dead paths and retired phrases in A-core; cited headings, cited
memories, relative links, orphan docs, vendored sibling names, and cross-repo references in
A-rest. Each is a check with a ratchet baseline. `/doctor prompt-audit` is an input to the
guard, never a gate (see "Anthropic practice").

### RC3. A new ruling lands in one home and older homes are never swept

**Response: the supersession sweep rule.** Any commit that lands a ruling superseding existing
text adds the superseded phrases to the retired-phrase list in the same commit, and removes or
marks (`retired-ok`) every hit. Two homes carry it, strongest first:

1. **Tool.** The retired-phrase check (A-core) fails on any listed phrase outside a `retired-ok`
   line. Its failure message states the rule, so the fixer learns it at the point of failure.
2. **Skill.** The `pass-core` close skeleton gains one step: each ruling folded this pass that
   supersedes text carries its retired phrases in the same commit. The cairn-cms twin list (the
   style-guide-sync plan's R8) takes the same step through `cairn-pass`.

No CLAUDE.md line and no commit-hook NOTE are added.

The strongest evidence for RC3 is a regression. `a7dd5ad` (2026-09-27 13:39) landed three
rulings in the global CLAUDE.md: the simplifier once per pass or branch, "the pass class's gate
runs inside the chain", and "Superpowers skills yield to it: TDD's write-first applies to
`engine-logic` and `auth-data` only, and plans stay outcome-only." Five minutes later `0a2e391`
("Slim the global CLAUDE.md"), written from a pre-`a7dd5ad` base, restored the per-commit
simplifier bullet and "the repo's full gate", and dropped the superpowers-yield sentence, which
now exists nowhere. Two sessions edited one file at once: a one-executor-rule failure. B4
repairs it.

### RC4. cairn-cms shape assumed by workstation-wide infra

**Response: repo-neutral runners, agents, and skills.**

- A runner never assumes npm and never rejects a plan for a missing `reducedGate`. The runners
  have no filesystem access (`pass-execute.js:37-40`, `:57-58`), so they cannot probe for a
  `package.json`. A reduced round's gate resolves as an explicit `reducedGate`, else the
  repo-neutral class default `pass-execute.js:246` already holds: "the repo's type check plus
  only the test files this fix round touched" (AW-01). It never falls back to the named full
  gate, since every plan names one and that fallback would repeal two rulings: the
  2026-09-09 "Gate economy on a pass" ruling, "Comment-only fix rounds run a reduced gate"
  (`pass-gate-economy.md:12`), and the 2026-09-27 class ruling, "a fix round whose findings are
  all `commentOnly` or `testOnly` runs the reduced gate" (`pass-gate-economy.md:19-21`). Probes
  for the classifier run only when it exists (AW-13).
- An agent or skill never cites a repo-relative path that resolves in exactly one repo bare. It
  writes the path absolute, or prefixed with its repo (`cairn-cms/docs/...`). A generic
  convention path that resolves in several repos, or a placeholder path, stays bare (AW-14,
  AW-15, PS-21).
- A skill that needs a repo's layout reads it from that repo's CLAUDE.md or STATUS and has an
  explicit branch for its absence (PS-08, PS-09, PS-10; pass C).
- An agent's definition of done is the gate its dispatch names, never a fixed npm list (AW-19).

### Smaller causes

- **RC5, context the executor lacks.** A `context: fork` skill takes explicit arguments and ends at
  its report (PS-06, PS-20); the fork-skill lint (A-rest) holds the line. A zero-context agent
  gets paths, never "the spec" (AW-18, fixed by hand in C). A report shape conflicting with a
  runner's schema yields to the schema (AW-19).
- **RC6, vendored skills with no overlay.** The vendored manifest gains a description override and
  a local precedence note applied on fetch (CS-8, CS-10, CS-17), and `fetch_skill` rewrites
  sibling names (CS-6). Pass D.
- **RC7, dated facts in present tense.** Files that load on every dispatch carry no toolchain
  version, engine pin, or token id as current fact; they point at the source that states it
  (CS-3, CS-4, CS-12, DC-07, DC-11, DC-14, AW-23). A-rest's quoted-version check fails any quoted
  version range in a repo CLAUDE.md.
- **RC8, always-loaded context carrying on-demand content.** Cairn-only and pass-only sections
  leave the global CLAUDE.md, routed by Anthropic's order (DC-19, DC-21); the context budget
  gains a 200-line cap per file (DC-02); long always-listed descriptions are capped (A-rest
  check, fixes in C and D). Every subagent loads the CLAUDE.md chain unless its definition sets
  `omitClaudeMd`; E decides the field per agent.

## The ratchet baseline (A-core)

One file, `claude/.claude/tooling/ratchet-baseline.json`, read by both tools.

- **Registry.** The file's `checks` map lists every check id and the tool that implements it.
  Each tool reports the ids it implements; a registered id no tool implements, or an entry under
  an unregistered id, is a configuration error. The registry is append-only: an id leaves use by
  taking the `retired` state, which requires no implementing tool and admits no entries, and
  deleting a registry id fails.
- **Entry shape.** Check id, file (relative to its root), a fingerprint that survives edits and
  line moves (the phrase, the unresolved path, the cited heading; a duplicate-pair entry is keyed
  on its sorted file pair and stores its overlap count), the owning finding id, and the pass
  label that removes it (`A-core`, `A-rest`, `B`, `C`, `D`, `E`, or `F`). A cross-repo entry also
  carries its repo.
- **Seeding.** Each seeded entry maps to an audit finding id. A violation the audit did not name
  gets an id `GA-nn`, a one-line defect, and a pass label. The seeding pass's close prints a
  summary of `GA-nn` counts per check (and per file pair for duplicates); Geoff sees only entries
  with no plausible owning pass.
- **Per-commit enforcement.** `scripts/githooks/pre-commit` compares the staged baseline with
  HEAD's copy, before its `exec gitleaks` line and without losing gitleaks' fail-closed exit. This
  behaves the same on `main`, on a branch, and in a worktree. It fails on an added entry under an
  id already in HEAD's registry or retired there, on a rising overlap count, and on a removed
  registry id. It passes removals, falling counts, re-keys, and entries under an id absent from
  HEAD's registry. A HEAD with no baseline counts as all-new, which covers A-core's own bootstrap.
- **One growth event.** A commit that registers a new check id may add that id's entries. A
  changed rule or threshold for an existing check is a new check id; the old id turns `retired`
  and its entries leave in the same commit.
- **Re-key.** A same-commit remove-and-add of the same check id and fingerprint, with the count
  unchanged, counts as a re-key, whatever git's rename detection reports. Duplicate-pair entries
  are keyed on the file pair, so an edit inside a still-duplicated pair keeps its entry.
- **The gate.** `scripts/check.sh` fails on a violation no entry matches (new), on an entry no
  violation matches ("remove this baseline entry"), and on working-tree growth against HEAD under
  the hook's rules.
- **Failure states.** File absent: fail (config error). Present and empty: pass. Malformed (bad
  JSON, missing field, unregistered id, bad finding-id format): fail, naming the entry.
- **Exit codes**, shared by both tools: `0` clean, `1` violations, `2` configuration error (a
  missing or malformed list, baseline, registry, manifest, or parity file, or an unknown
  argument). A run reports every violation grouped by check with a count per check, never only
  the first.
- **Roots.** Home, the projects root, and the memory root are injectable in both tools; every
  fixture sets them, and one fixture asserts no read outside the fixture root.

## Pass A-core: the guard's mechanics

**Repo** `~/.dotfiles`, worktree `~/Projects/.worktrees/dotfiles-infra-a` on branch
`infra-sweep-a`, merged `--no-ff` to `main`; the merge SHA is recorded for `git revert -m 1`.
**Per task:** gate `bash scripts/check.sh`, light lane; `diff-reviewer` against the task's
acceptance; test-first with fixtures. The plan carries one failure-state table (state, tool, exit
code, report line) with one fixture per row. No simplifier at close (Python and bash, S5).
Findings closed outright: PS-01, CS-9, AW-16. The pre-bake points dotfiles STATUS at this sweep
and drops the owed aksailingclub-org pointer line.

### AC1. The ratchet

Files: `claude/.claude/tooling/ratchet-baseline.json`, the shared baseline logic (one module or
two parsers of one format; the plan decides), `scripts/githooks/pre-commit`, `scripts/check.sh`,
fixtures under `tests/`.

Outcomes: everything in "The ratchet baseline" above. Fixtures cover growth on HEAD under a
registered id (fails), growth under an emptied registered id (fails), growth under a newly
registered id (passes), growth under a retired id (fails), a removed registry id (fails), a
re-key across a heavily edited move (passes), a stale entry, a
grown count, an empty baseline, the malformed states, and a many-bad run.

### AC2. `claude-tooling-sync`

Files: `bin/.local/bin/claude-tooling-sync`, `claude/.claude/tooling/` (manifest),
`claude/.claude/skills/ship/` renamed to `go-ship/`, `scripts/check.sh`, fixtures.

- **`lint --root <tree>`**, a tree-only subcommand: the manifest checks and the unmanifested
  third-party skill check. `check.sh` calls it by repo-relative path
  (`bin/.local/bin/claude-tooling-sync lint --root .`), so a worktree runs its own copy against
  its own tree (AW-16). Unknown arguments exit 2.
- **`verify`** keeps the machine checks (`~/.claude.json`, `claude plugin list`) and gains the
  skill-name collision check. `check-drift` runs it; A-rest wires it into closes.
- **Skill name collision.** A personal skill whose name equals any
  `~/Projects/*/.claude/skills/<name>` fails, since personal shadows project. Fixed now: the
  personal `ship` becomes `go-ship`, its generic triggers dropped and
  `disable-model-invocation: true` set (PS-01, S6). This clears the three `ship` collisions
  (ecxc-ski, aksailingclub-sveltekit, aksailingclub-legacy).
- **Unmanifested third-party skill.** A `skills/<dir>` carrying a `LICENSE*` with no manifest
  entry fails. Fixed now: `vhs-cli-demos` gets its manifest entry (CS-9).

Acceptance: `bin/.local/bin/claude-tooling-sync lint --root <worktree>` green;
`claude-tooling-sync verify` green on the merged `main`; manifest absent and malformed fixtures
exit 2.

### AC3. `scripts/check-claude-refs.py`, self mode

Python, under `python-conventions` (PEP 257, the ruff D config `check.sh` already runs). Wired
into `scripts/check.sh`. Scan scope: `claude/.claude/agents`, authored `skills` (excluding
vendored and `skills/synced/`), `workflows`, `docs` (excluding `docs/record/`), `output-styles`,
`instructions`, and `CLAUDE.md`; excluding `evals/research/`, dated files, the list files, and
the fixtures. The retired-phrase check alone also scans vendored skills, which matches W6's
scope (only `skills/synced/` excluded).

**Self mode** resolves inside the tree under test. A `~/.claude/<stowed dir>/...` path is
rewritten to `<root>/claude/.claude/<dir>/...` and a `~/.local/bin/<x>` path to
`<root>/bin/.local/bin/<x>` before resolving, so a worktree that deletes or adds a doc is judged
on its own tree. Other absolute paths outside `~/Projects` resolve as written. Paths into
`~/Projects` and bare repo-relative paths belong to cross-repo mode (A-rest).

| Check | Rule | Baselined findings |
|---|---|---|
| Dead reference (self mode) | every backticked path in self-mode reach resolves | PS-03, CS-3 and CS-4 (paths), DC-08, and whichever of AW-08 falls in self-mode reach; the cross-repo ids seed in A-rest |
| Retired phrase | a phrase in `claude/.claude/tooling/retired-phrases.txt` fails outside a `retired-ok` line | DC-01, DC-03, DC-04, DC-06, DC-30, PS-04, PS-05, AW-07 ("sleep 30"), CS-4 ("currently 1.26") |

**Retired-phrase list.** One literal phrase per line, matched as a case-insensitive substring,
`#` comments allowed, no length rule. Absent: exit 2. No phrase: exit 2 (a vacuous tripwire).
The header names its cairn-cms twin (the style-guide-sync plan's R8), which uses the same
semantics. A-core seeds only phrases already superseded by a ratified ruling; the plan names each
with a witness `file:line`, including "Before committing code changes, dispatch" (DC-01) and "the
repo's full gate runs inside the chain" (DC-03, specific enough to spare `pass-core`'s class
table). The style-guide-sync phrases are appended by W6 once W2 to W5 remove them, so the list
never starts red.

**Acceptance for A-core.** `bash scripts/check.sh` green on the worktree with the seeded
baseline; every fixture passing; `claude-tooling-sync verify` green on the merged `main`. The
close prints one row per baselined audit id with its seeded entry count; a zero passes only with
a named reason (for example, "cross-repo, seeds in A-rest"). The close also prints the baseline
summary per pass label and the `GA-nn` summary.

## Pass B: the execution path

**Repo** `~/.dotfiles`, worktree `~/Projects/.worktrees/dotfiles-infra-b` on branch
`infra-sweep-b`, created from `main` after A-core merges; the merge SHA is recorded for
`git revert -m 1`. **Per task:** gate `bash scripts/check.sh`, light lane; `diff-reviewer`
against the task's acceptance. B1 and B2 are test-first; B3 and B4 take mechanical acceptance
(retired phrases and grep post-conditions), with no register chain. The close runs the
simplifier over B's changed JavaScript: B1's runners and `.mjs` tests and B2's
`docs-page-chain.js` (S5). Each task that fixes a baselined finding removes its
entries in the same commit, and each row that retires text appends its phrase in that commit
(RC3). Implementer-definition edits land here so the style-guide-sync plan's W5 branches from
them.

### B1. Runners

Files: `claude/.claude/workflows/pass-execute.js`, `claude/.claude/workflows/pass-execute-chains.js`,
new tests under `tests/` in the pattern of `tests/docs-page-chain-derivation.test.mjs` (tables and
helpers extracted through markers and `new Function`, since the runners carry a top-level
`return`), run by `check.sh`.

| Finding | Outcome |
|---|---|
| AW-01 | Both runners resolve a reduced round's gate as an explicit `reducedGate`, else the repo-neutral class default (`pass-execute.js:246`), never the named full gate (RC4). Chains drops its npm constant (`:164`). No plan is rejected for a missing `reducedGate` |
| AW-02 | Chains uses the same gate matcher as `pass-execute.js`: a wrapper, a `cd` prefix, and multi-line stdout all match |
| AW-03 | Any reduced round is exempt from the MISMATCH block; no prompt carries both MISMATCH-blocking and "reduced is expected" |
| AW-04 (runner side) | The hardcoded npm sentence in the no-class comment-only round (`pass-execute-chains.js:249`) goes; that round renders the gate resolved above |
| AW-05 | The unread severity field is deleted from the schema and from the prompt |
| AW-06 | The header describes the runner generally; "committed in this repo" becomes "an absolute path"; the "Ruled inputs" section is optional |
| AW-12 | Chains `IMPL_SCHEMA` carries `mutationLedger`, so the `auth-data` mandate can be met |
| AW-13 | `classifier` is a per-chain boolean: a chain's own value, else `args.classifier`, else one cached existence probe on `model: "haiku"` for that chain's repo. `false` skips the probe; per-task tier probes run only when the classifier exists; the classifier paragraph renders only then |
| DC-04 (tool half) | Each runner prints the runaway-guard NOTE at launch, naming the wake-up the guards doc names |
| AW-11 (interim) | A parity test holds `PASS_CLASSES`, the reduced-gate default, and the gate matcher equal across both runners, and holds `pass-core`'s table to the class-name set, the reviewer model, and the gate lane; the runner merge waits for pass E |

Test assertions: the parity above; every field a mandate cites exists in `IMPL_SCHEMA`; every
`REVIEW_SCHEMA` field is read; the matcher accepts the three forms; a no-class reduced round
renders no MISMATCH line and no npm command; the two-step reduced-gate resolution, with a named
gate and no `reducedGate` rendering the class default; per chain, a chain with
`classifier: false` spawns no probe and a chain without the field spawns exactly one, in the same
invocation; no `agent(` call lacks `model:`; the launch NOTE prints.

### B2. Gate tool

Files: `bin/.local/bin/cairn-run-gate`, its test, `claude/.claude/workflows/docs-page-chain.js`
(the exit-75 restatement at `:198`).

| Finding | Outcome |
|---|---|
| AW-17 | A vanished gate run exits 75 with the line "gate vanished; re-issue starts a fresh run" and prints no `gate exit:`, so the existing "on 75, re-issue until `gate exit:`" instruction covers it. A vanish counter in the state directory bounds the loop: the third consecutive vanish prints `gate exit: 1 (vanished 3 times)` and exits 1 |
| AW-20 | The gate protocol lives in `cairn-run-gate`'s output. Each runner prompt and implementer carries one line: run the gate through `cairn-run-gate` and follow its output. The restated paragraphs in `cairn-implementer.md`, `site-implementer.md`, and `docs-page-chain.js:198` go; `pass-gate-economy.md` keeps the rationale |

Test assertions: a staged state directory with a dead pid and no status file exits 75 with the
vanish line; three consecutive vanishes print the terminal `gate exit: 1`; a gate that itself
exits 75 is distinguishable by its `gate exit:` line; no runner prompt carries a vanished
clause.

### B3. Agent definitions

Files: `claude/.claude/agents/cairn-implementer.md`, `site-implementer.md`, `diff-reviewer.md`.

| Finding | Outcome |
|---|---|
| AW-19 | Done means the gate the dispatch names. Where a runner requests a structured schema, the schema replaces the text report shape |
| AW-23 | The dated compatibility note is deleted from both implementers |
| AW-04 (reviewer side) | `diff-reviewer` says "the reduced gate the dispatch names" and defines none of its own |
| AW-05 (reviewer side) | The severity-as-routing claim is deleted |
| DC-29 (agent side) | The hardcoded `Co-Authored-By: Claude <noreply@anthropic.com>` footers (`cairn-implementer.md:58`, `site-implementer.md:51`) take the wording `pass-execute-chains.js:238` already uses: "the repo's git conventions (imperative mood, specific files, the repo's co-author footer)" |

Mechanical acceptance: the fixed npm definition-of-done list and the dated note enter the
retired-phrase list with their witnesses and have no hit. The generic footer string retires in
B4, where its last hits leave.

### B4. Global CLAUDE.md, pass skills, and the spent workflow

Files: `claude/.claude/CLAUDE.md`, `claude/.claude/skills/pass-core/SKILL.md`,
`claude/.claude/skills/site-pass/SKILL.md`, `claude/.claude/skills/cairn-pass/SKILL.md`,
`claude/.claude/skills/go-ship/SKILL.md`, `claude/.claude/docs/model-economy.md`,
`claude/.claude/docs/voice/commit-and-pr.md`,
`claude/.claude/workflows/cairn-overnight-to-release.js` (deleted), `docs/HISTORY.md`.

| Finding | Outcome |
|---|---|
| `0a2e391` repair | The implementer diffs `a7dd5ad` against `0a2e391` over `claude/.claude/CLAUDE.md` and separates deliberate slimming from lost rulings. Each lost ruling is restored to its owning home; the report lists every one found |
| DC-01 (+PS-13) | The Git Conventions bullet restores `a7dd5ad`'s text, so the rule stays in CLAUDE.md for branch work outside passes: code-simplifier runs once per pass or branch at its close over changed TypeScript (including JavaScript, S5), Svelte, or Go; never per commit or at an intermediate boundary; never for docs. It points at `pass-core` for the pass procedure. The small-task line reads "straight through the gates". `pass-core`'s simplify step names the S5 languages. `go-ship` runs the repo's own `simplify` skill when `<repo>/.claude/skills/simplify/` exists (poplar) and `code-simplifier:code-simplifier` otherwise, once, as its close step; the path check is the test, since the bundled `/simplify` always resolves by name |
| Superpowers yield (`GA` id assigned at seeding) | "Superpowers skills yield to the pass class: TDD's write-first applies to `engine-logic` and `auth-data` only, and plans stay outcome-only" is restored in `pass-core` beside the class table |
| DC-03 (+PS-16) | The global CLAUDE.md chain sentence restores `a7dd5ad`'s "the pass class's gate runs inside the chain" with its `pass-core` pointer; `site-pass` and `model-economy.md:38` say the same. Repo copies are pass F |
| DC-04 (text half) | The unattended-work line says the tools hold the sleep inhibitor and the session arms the runaway guard and the wake-up the guards doc names at launch. It names no mechanism, so C2's `/goal` evaluation needs no edit here |
| PS-14 | `pass-core`'s escalation points at `model-economy.md` "Current state" (which includes `max`) and restates no ladder; A-rest repoints it at `seats.json`. cairn CLAUDE.md is pass F |
| PS-22 | `cairn-pass` close drops the separate `npm run check`, since `check:close` runs it |
| DC-29 | The co-author footer bullet is deleted (S7). The example trailer at `commit-and-pr.md:93` becomes the model-named form, `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>` |
| DC-30 | The pre-bake step says to update STATUS, and memory only for a preference or a ruling's why |
| AW-07 | `cairn-overnight-to-release.js` and its skill-listing entry are deleted; "sleep 30" leaves the baseline |
| History | `docs/HISTORY.md` records `0a2e391` as a one-executor-rule incident: two sessions edited the global CLAUDE.md at once, and the later commit reverted three rulings |

Retired phrases appended here: "Before committing code changes, dispatch" and "the repo's full
gate runs inside the chain" are already seeded by A-core; B4 adds "straight through the gates and
code-simplifier" and the generic footer string `Co-Authored-By: Claude <noreply@anthropic.com>`,
whose last hits (`CLAUDE.md:68`, `cairn-overnight-to-release.js:76`, `commit-and-pr.md:93`) leave
in B4's commits.

### Pass B acceptance

- `bash scripts/check.sh` green; the runner and gate tests passing;
  `claude-tooling-sync verify` green on the merged `main`.
- A baseline query returns zero entries lettered `A-core` or `B`.
- One fixture in B1's harness, not a second test file, carries the style-guide-sync plan's
  chain arguments as amendment 1 sets them: chains R and W in one invocation, W with
  `classifier: false` and `reducedGate: "bash scripts/check.sh"`. It asserts: W's prompts
  name no npm command; every W reduced round renders `bash scripts/check.sh` and no npm
  command; no reduced round carries a MISMATCH-blocking line; W spawns no classifier probe; R's existence probe runs once, on `haiku`.

## Amendments to the style-guide-sync plan

Applied by that plan's conductor at pre-flight, after B merges. The audit's section 6 items plus
S2, S3, and the ratchet's effect on chain W. The plan owns eight audit ids: PS-07 (W4), DC-25
(W4 per ruling 12; the poplar gap goes to F per S2), AW-09 (W1, W3), AW-08 (W3), AW-10 (W1),
DC-27 (W4), DC-28 (W4 per S3), and AW-24 with DC-26 and CS-15 (W2, W4).

1. The Gates block drops only the `notes` sentence overriding the implementer's definition of
   done (AW-19); the notes keep the absolute spec path. Chain W sets
   `reducedGate: "bash scripts/check.sh"`, in the same form as its named `gate` (AW-01). This
   is step 1 of the resolution order, so both rulings hold: dotfiles has no separate type
   check and W's docs rounds touch no test file, so the class default would run nothing, and
   the light-lane gate is cheap. Chain W sets `classifier: false` (AW-13).
2. W6 appends its phrases to `claude/.claude/tooling/retired-phrases.txt` and adds fixtures for
   them. It adds no second check to `scripts/check.sh`; A-core's scanner covers W6's scope for
   retired phrases. W6's class changes from `engine-logic` to `sweep`, whose mandate ("existing
   tests stay green, and add no new test unless the plan names one") fits fixtures that prove
   phrases, not new logic; the plan names the fixtures. R8's list header names
   `claude/.claude/tooling/retired-phrases.txt`, and R8 matches as a literal, case-insensitive
   substring, like its twin.
3. W6's acceptance runs `bin/.local/bin/claude-tooling-sync lint --root <worktree>` inside the
   chain. The segment B boundary step 3 (`claude-tooling-sync verify`) stays as a post-merge
   confirmation of the machine checks.
4. The plan keeps invoking `pass-execute-chains` by name; the runner merge (AW-11) waits for pass E.
5. S3: W4's Files gain the three voice files outside it (DC-28). All five voice files drop their
   measures sections and keep one pointer line to `MEASURES.md`, and the Go register's missing
   repo and wrong linter are corrected. W4's acceptance checks all five.
6. S2: DC-25's poplar gap is out of W4. Poplar's overlay is ruled canonical and its stale
   references go in pass F.
7. The chain W worktree is created from dotfiles `main` after B merges. P1's claim check re-runs,
   since B moves line numbers in files W edits (`cairn-implementer.md`, `site-implementer.md`,
   `CLAUDE.md`, `docs-page-chain.js`, `docs/voice/commit-and-pr.md`).
8. Each W task that clears a baselined entry (a retired phrase or a self-mode dead reference, for
   example AW-08 in W3) removes that entry in the same commit, and
   `claude/.claude/tooling/ratchet-baseline.json` joins that task's Files.
9. The close maps every runner halt, escalation, or `fix` reason to an audit id or to "not
   infra". The sweep's first goal holds when none maps to an audit id.
10. A pre-flight step after P1, before segment A dispatches, re-runs B1's style-guide-sync
    fixture render against the amended plan's real Gates-block arguments and greps the amended
    plan for the two workarounds named under "Success tests". Either failing halts the pass
    before dispatch.

## Pass A-rest: the guard's remaining checks (planned later)

Outcome level. After style-guide-sync, before C and D. Same repo, gate, and per-task shape as
A-core. Each new check registers its id and seeds its entries in the same commit.

- **Duplicate paragraph.** 12-word shingle overlap above a threshold between any two of agents,
  authored SKILL.md files, output styles, CLAUDE.md, and docs. Entries keyed on the sorted file
  pair with the count of over-threshold paragraph pairs, which may only fall; an N-way copy is one
  cluster. `claude/.claude/tooling/parity.json` declares sanctioned copies, pairs or N-way groups,
  held byte-identical between markers (absent: exit 2; empty: pass; a missing marker or a differing
  byte: violation showing the first differing line). Calibrated against the self-mode
  duplicate-paragraph ids (AW-04, AW-20, AW-21, AW-22, CS-13, DC-21) plus a named negative set
  (shared frontmatter, template headings, the implementer report block); the calibration evidence
  and the new-`GA-nn` count go in the script header. A threshold change is a new check id.
  Baselined: AW-04, AW-20, AW-21, AW-22, CS-13, DC-21, DC-22, PS-25.
- **Cross-repo mode.** `--repo <name>` with `--repo-root <path>`, so a close checks its own
  worktree. Scope is an explicit repo list in the tooling config (the six pass F repos); any other
  repo is reported, never baselined. A stale cross-repo entry is a NOTE, pruned by the next
  dotfiles commit. Checks: a bare repo-relative path fails when it resolves in exactly one repo
  (prefix it) or in none (dead); a multi-repo path or a placeholder (`<`, `{`, `YYYY`) passes
  (AW-14, AW-15, PS-21, DC-12, DC-13). A quoted version range in a repo CLAUDE.md fails (DC-14).
  The context budget becomes a baselined check id with a 200-line cap per CLAUDE.md, lettered E
  for the global file and F per repo (DC-02).
- **Seat check.** `claude/.claude/tooling/seats.json` maps each agent to its seat: `model`,
  `effort` (a missing `effort:` is a violation), a one-line `why` for each non-default effort, and
  `omitClaudeMd` (decided in E). `model-economy.md` "Current state" keeps its heading and the why,
  and points at `seats.json` for values; `pass-core` and the global CLAUDE.md model line cite
  `seats.json` directly. Seats in in-scope repos run under `check-drift` and at closes. Baselined:
  DC-11 (F), and the project agents lacking `effort` (F).
- **The remaining `claude-tooling-sync` checks.** Description override matches the installed file;
  a description with no `paths:` gate over 500 characters fails (CS-8, CS-17, PS-28); the
  fork-skill lint (PS-06, PS-20); vendored sibling names (CS-6).
- **The remaining reference checks.** Heading citation in both house forms, `` `file.md`
  ("Heading") `` and `` `file.md` "Heading" `` (DC-13, DC-15, DC-18); memory citation (DC-09);
  relative link (DC-10); orphan doc (DC-17).
- **`/doctor prompt-audit` before seeding.** The conductor runs it once over `~/.claude` before
  A-rest's first seed. Each finding the checks do not cover becomes a `GA-nn` entry or a C or D
  item, listed in the close.
- **Wiring.** `pass-core`'s close gains one step: the reference checker in cross-repo mode over the
  closing worktree, `claude-tooling-sync verify` for that repo's agents, and the context budget;
  `cairn-pass` and `site-pass` supply the commands; the supersession step (RC3) lands in the same
  skeleton. `check-drift` gains `--only claude`, runs cross-repo mode and the context budget over
  the repo list, and both passes' acceptances use `check-drift --only claude`, since machine drift
  keeps the full `check-drift` red for reasons outside this sweep.

## Passes C, D, E, F (planned later)

Outcome level only. Each is planned from this list plus the baseline at its start.

**Pass C: process skills and workstation docs** (after A-rest). Split at the natural seam.
- C1, cairn-facing skills: PS-02 and PS-04 (the release and consult gates become
  `npm run check:close`), PS-03, PS-05 (alt rules point at the register's Visuals), PS-06 (explicit
  args; the caller binds tells), PS-17 (one "Facts consulted" definition, added to the plan
  template), PS-18 (delete the pass-end draft clause), PS-19, PS-28, AW-14, AW-15.
- C2, site and generic skills plus docs: PS-08 (absent-guide branch), PS-09 (paths from the site's
  CLAUDE.md or STATUS), PS-10 (`backlog: false`, `backlog_path`), PS-11 (close to HISTORY.md, read
  existing tiers), PS-12 (delete), PS-15 (`spec-plan-review`'s reviewer and verification-reader
  lines, `:95` and `:124`, to `medium`; the fold agent at `:99` authors and stays `high`), PS-20,
  PS-21, AW-18, DC-06, DC-07, DC-08, DC-09 (inventory side), DC-16, DC-17 (delete, citing the
  2026-09-12 infra round's task 4 as superseded and retiring its phrasing; the `--name` fact moves
  to the inventory), DC-23. C2 also evaluates `/goal`, with the pass acceptance as its condition,
  against the `/loop` wake-up, and records the result in the guards doc.
- Trigger checks: each skill whose description C trims and that a CLAUDE.md rule depends on
  (`dependency-upgrade`, `visual-fidelity`, `cairn-release`) gets three should-trigger and two
  should-not prompts in fresh `claude -p` sessions, before and after the trim.

**Pass D: convention skills and the vendored manifest** (parallel with C; disjoint files). CS-1
(`SilenceErrors: true`), CS-2 (precedence line in go-conventions; elm dropped from the cobra
`_why`), CS-3, CS-4 (no pinned Go version; narrowed tag rule), CS-5, CS-6 (`fetch_skill` rewrite,
then refetch), CS-7 (call `kitty-headless-shot` directly), CS-8 and CS-10 (manifest overlays), CS-11
(copy-in source is cairn's `eslint.config.js`), CS-12, CS-13, CS-17, DC-10 (+CS-14;
`bubbletea-conventions.md` moves to poplar as history, and its checklists land in a reference file
under `elm-conventions/`, one level from SKILL.md). `go-conventions` and `elm-conventions` each end
under 500 body lines, reference material moved one level down. Trigger checks as in C for
`go-conventions` and `tui-visual-verify`.

**Pass E: consolidation to owners** (after C and D).
- AW-11 (+PS-23; chains becomes a mode of `pass-execute.js`, with the skill listing and plan
  template updated, and the parity test retired), AW-21 (implementer copies declared in the parity
  list; measures to `MEASURES.md`), AW-22 (engine-triage owns the standard), DC-22 (+PS-26,
  workstation side), PS-25 (workstation side).
- DC-19 and DC-21 (+PS-24) are routed sentence by sentence. E's close carries a ledger mapping
  every sentence of each moved section to its new home: a procedure to a skill (the pass rules to
  `pass-core`, including the 2026-09-03 parallelize ruling, the 2026-09-12 segmentation ruling, the
  80%-of-ceiling procedure, the fold-agent close, "anything load-bearing lives in an artifact", the
  idle-gap close, and the thin-conductor self-flag); a file-specific rule to `.claude/rules/` with
  `paths:`; an every-session fact to a CLAUDE.md. A sentence dropped outright is an owed erratum
  for Geoff, never a silent deletion; the reviewer checks the ledger. The DaisyUI-first sentence
  goes to cairn-cms and each site (their CLAUDE.md or `site-pass`), the manifest sentence stays
  global, and the `claude-tooling.md:95-96` heading citation updates in the same commit. The Git
  Conventions section is trimmed against Claude Code's built-in git instructions.
- `claude-tooling-sync` and the reference checker learn `.claude/rules/` (a new artifact kind here).
- `omitClaudeMd` is decided per agent and recorded in `seats.json`. Candidates: the drafter,
  `diff-reviewer`, `visual-verifier`, and `figure-verifier`, whose dispatches carry their inputs.
- The close runs `/doctor prompt-audit` as a confirmation read and checks E's success test,
  including the 200-line target.

**Pass F: repo CLAUDE.md files** (one small chore per repo after A-rest, each under its own
one-executor check, straight through the repo's gate). Each chore runs `/doctor prompt-audit` and
the `/doctor` trim proposal over that repo's CLAUDE.md and triages them, and brings the file to
200 lines or a recorded reason.

| Repo | Findings |
|---|---|
| cairn-cms (after the style-guide-sync merge) | DC-03, PS-14, DC-18, DC-24 ("loads once a Go file is open"), DC-22 and PS-25 repo sides |
| 907-life | DC-02, DC-13, DC-14, DC-22, DC-17 stub |
| ecxc-ski | DC-02, DC-13, DC-22, DC-23 (receives the ECXC anchors), DC-17 stub |
| aksailingclub-org | DC-09 pointer, DC-15, DC-22 |
| xcathletes-org | DC-03 |
| poplar | DC-11 (repin to seats; CLAUDE.md says "per model-economy"), DC-12 and DC-25 per S2 |

## Owner decisions

**DC-01 is decided from the ratified rulings.** The 2026-09-27 ruling first landed in the global
CLAUDE.md at `a7dd5ad`, in Git Conventions, which governs every commit: "`code-simplifier` runs
once per pass or branch, at the close, over changed TS, Svelte, or Go; never per commit or at an
intermediate boundary, never for docs." `pass-gate-economy.md:72` and `pass-core`'s close step 1
carry it. The per-commit bullet is `0a2e391`'s regression, not older text (RC3). S5 settles the
languages.

**PS-15 is decided from the seat table.** Reviewers sit at `medium` (Geoff, 2026-09-23); the
skill's reviewer `high` has no recorded reason. The fold agent is an authoring seat and stays
`high`.

**DC-29, S6, and S5** are Geoff's rulings of 2026-09-28, recorded under "Sequence and rulings".

## Anthropic practice

Fetched 2026-09-28 against Claude Code v2.1.284. Full quotes and grading:
`docs/superpowers/research/2026-09-28-infra-sweep-review-anthropic.md`. Items marked **scope**
widen a pass; none adds a pass.

**Confirmed.**

- One owner per rule, tool output first. "If a rule must hold every time, make it a hook rather
  than a prompt instruction." "Hook output lands in context."
  (<https://code.claude.com/docs/en/features-overview>) RC1 and RC3 stand.
- No contradicting homes. "If two rules contradict each other, Claude may pick one
  arbitrarily." (<https://code.claude.com/docs/en/memory>) RC3's supersession sweep stands.
- No dated facts. "Don't include information that will become outdated."
  (<https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices>) RC7
  stands.
- Description cap. The native listing truncates at 1,536 characters and drops the
  least-invoked descriptions first on overflow (<https://code.claude.com/docs/en/skills>). The
  500-character cap stands.
- Reviewers at `medium`. Opus 5.5 "at its default `medium` effort ... matched or beat Claude
  Opus 5 at `high`."
  (<https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5-5>)
  PS-15 stands.
- Emphasis. "If you emphasize many lines, none of them stands out."
  (<https://code.claude.com/docs/en/best-practices>) The infra carries two `MANDATORY` lines.
  No trimming pass.

**Changed.**

1. CLAUDE.md size (E, F; **scope**). "Target under 200 lines per CLAUDE.md file"; imports
   "still load and enter the context window at launch"; a procedure or file-specific rule
   moves "to a skill or a path-scoped rule instead" (<https://code.claude.com/docs/en/memory>).
   E routes DC-19 and DC-21 content by that order, using `.claude/rules/` with `paths:` where
   content is file-specific. E's success test adds: each in-scope CLAUDE.md at or under 200
   lines, or a recorded reason. A-rest's budget check gains the 200-line cap. The tools learn
   `.claude/rules/`.
2. Subagent context (A-rest, E; **scope**). Subagents load the CLAUDE.md chain unless the
   definition sets `omitClaudeMd` (<https://code.claude.com/docs/en/features-overview>). E
   decides the field per agent and records it in `seats.json`, which the seat check reads.
3. Anthropic's audit (A-rest, E, F). `/doctor prompt-audit` finds "instructions written for
   older models, references to files or commands that don't exist, and files that contradict
   each other" (<https://code.claude.com/docs/en/memory>). A-rest runs it once before seeding
   and turns its uncovered findings into `GA-nn` entries or C and D items. E runs it at close.
   Each F chore runs it and the `/doctor` trim proposal. It is an input, never a gate.
4. Attribution (B3, B4). CLAUDE.md commit rules compete with built-in guidance; "set the
   attribution text with `attribution`" (<https://code.claude.com/docs/en/memory>). The footer
   bullet goes, and the default model-named trailer applies (S7).
5. Reference depth (A-rest). "Keep references one level deep"
   (<https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices>).
   `pass-core` and CLAUDE.md cite `seats.json` for values and `model-economy.md` for the why.
6. Skill size (D). "Keep `SKILL.md` under 500 lines" (<https://code.claude.com/docs/en/skills>).
   D lands DC-10's checklists in a reference file under `elm-conventions/` and splits
   `go-conventions`.
7. Trigger checks (C, D; **scope**). "Seeing a skill trigger tells you Claude found it, not
   that it did what you intended" (<https://code.claude.com/docs/en/skills>). Each trimmed
   skill that a CLAUDE.md rule depends on gets three should-trigger and two should-not prompts
   in fresh `claude -p` sessions, before and after the trim.
8. Delegation (B). "Do not delegate work you can finish yourself in a handful of tool calls"
   (<https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5>).
   B5 merged into B4.
9. Unattended completion (B4, C2). `/goal` defers evaluation while a subagent or background
   command runs and issues check-ins (<https://code.claude.com/docs/en/goal>). B4's DC-04
   text stays tool-neutral. C2 evaluates `/goal` against the `/loop` wake-up and records the
   result in the guards doc.
10. Effort record (A-rest). Current guidance starts well-specified Sonnet 5.5 coding at `medium`
    and reserves `xhigh` and `max` for measured gains
    (<https://platform.claude.com/docs/en/build-with-claude/effort>). `seats.json` carries a
    one-line `why` per non-default effort. The effort sweep itself is filed to the dotfiles
    `ROADMAP.md` for `model-economy.md`'s owner.
11. Side-effect skills. `disable-model-invocation: true` for workflows with side effects
    (<https://code.claude.com/docs/en/best-practices>): set on `go-ship` only (S6).

## Out of scope

- Any change to cairn-cms code, docs, or its own checks. Its retired-phrase twin and `check:close`
  belong to the style-guide-sync plan (R8) and the repo.
- Re-auditing. Violations found while seeding become `GA-nn` entries; they are not fixed in the
  seeding pass.
- The skill and agent content rewrites beyond each finding's disposition.
- A new implementer for the dotfiles repo.
- A write-time `PostToolUse` hook for the reference checks; closes and the weekly run catch the
  same defects.
- Scheduled cloud agents; `check-drift`'s weekly timer is the periodic trigger.

## Risks

- **Runner edits go live on merge.** A workflow invoked by name reads the stowed copy on `main`.
  B merges only after `pgrep` and journal checks show no running `pass-execute*` or
  `docs-page-chain` run. Rollback is `git revert -m 1` on the recorded merge SHA.
- **A-core and B run on today's defective runners.** Both passes run per task with the Agent tool
  (under six tasks), not through `pass-execute-chains`, and each dispatch names the gate
  `bash scripts/check.sh` explicitly, overriding the implementer's npm definition of done until
  B3 lands.
- **The duplicate-paragraph threshold** can be noisy or blind. Calibration with positives and a
  named negative set bounds both; a threshold change is a new check id.
- **Cross-repo checks** make a repo's close depend on the dotfiles tree. The close runs the
  checker from the dotfiles `main` checkout, read-only, against its own worktree through
  `--repo-root`.
- **Concurrent edits to one file.** `0a2e391` is the precedent. Each pass runs the one-executor
  check before dispatch, and the per-commit ratchet catches a baseline regrown by a stale base.
- **Contention with the style-guide-sync worktree.** The chain W dotfiles worktree must not exist
  until B merges, or it is recreated from the new `main`.

## Open for the plan

- Whether `check-claude-refs.py` and `claude-tooling-sync` share a baseline module or each parse
  the JSON (one format and one registry either way).
- The implementer seat for A-core and B tasks: `cairn-implementer` with the explicit gate, or
  `general-purpose` on `sonnet` with the implementer's report shape pasted in.
- Token ceiling and checkpoint interval for A-core and for B, per the global rule.
