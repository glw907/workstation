# Infra sweep spec review: consistency lens

Target: `docs/superpowers/specs/2026-09-28-claude-infra-sweep-design.md` at dotfiles `3f41deb`.
Evidence: `claude/.claude/docs/record/2026-09-28-claude-infra-audit.md` (`0413e39`). Lens: does the
spec contradict a ratified document or ruling? Every claim below was checked against the files
and git history at HEAD, not from memory.

Anthropic warning (https://code.claude.com/docs/en/best-practices): "A reviewer prompted to find
gaps will usually report some, even when the work is sound, because that is what it was asked to
do. Chasing every finding leads to over-engineering." Findings are ranked by consequence.

**Counts:** 0 blockers, 6 majors, 10 minors (one minor is an OWNER FORK).

## Direct answers to the brief

**DC-01: does the 2026-09-27 ruling cover commits outside a pass?** Yes. Retiring the
per-commit form is not a contradiction. The ratified text is broader than the spec says. The
ruling first landed in the global CLAUDE.md at `a7dd5ad` (2026-09-27 13:39), in Git Conventions,
a section that governs every commit:

> **`code-simplifier` runs once per pass or branch, at the close,** over changed TS, Svelte, or
> Go; never per commit or at an intermediate boundary, never for docs.

The same commit also took code-simplifier off the small-task line, which became "goes straight
through the gates". `pass-gate-economy.md:72-75` repeats the scope: "It no longer runs before every
commit." So non-pass branches and small tasks are both covered. The per-commit bullet at
`CLAUDE.md:64` and the small-task wording at `:261` are not older text that predates the ruling.
They are a regression (M1). The spec has two faults here. Its rationale is wrong, and its fold
("one pointer line" to `pass-core`) would narrow the ruling to passes (M2).

**Rulings quoted.**
- DC-01: `pass-gate-economy.md:72` "code-simplifier runs once per pass or branch, at the close
  (Geoff, 2026-09-27), and only when the pass changed TypeScript, Svelte, or Go."
  `pass-core/SKILL.md:156-159` "Simplify, once per pass ... It never runs at a segment or task
  boundary, whatever the class." Also the `a7dd5ad` CLAUDE.md text quoted above.
- DC-03: `pass-core/SKILL.md:77` "## Pass class (Geoff, 2026-09-27)", with the per-task gate
  column at `:84-91`. `CLAUDE.md:170-171` carries the pointer: "A plan header's `Pass class:` sets
  the per-task gate ... (table in the `pass-core` skill; Geoff, 2026-09-27)." At `a7dd5ad`, the
  chain sentence read "the pass class's gate runs inside the chain". `0a2e391` reverted it to
  "the repo's full gate" (M1).
- PS-15: `model-economy.md:10,18` "Seats, per Anthropic's model guidance (Geoff, 2026-09-23)" |
  "Reviewers (`diff-reviewer`, domain reviewers, verifiers, graders) | `claude-opus-5-5` |
  `medium`", plus `:27` "Reviewer effort is `medium`". `spec-plan-review/SKILL.md:95,124` carry
  `high` with no reason. That `high` was written in `8c53329`, the commit that created the skill
  on 2026-09-23. The decision is sound, with a scope caveat (m3).
- DC-29: no ratified ruling covers it. The spec correctly treats it as a taste confirmation. The
  harness attribution reminder defers to a CLAUDE.md rule on the trailer, as the spec states.

**Style-guide-sync amendments against rulings 1 to 14 and the fold.** None of them contradicts a
ruling. Amendment 1 contradicts the spec's own pass B (M3). Amendment 2 contradicts the plan
fold's literal-phrase decision (M6). The amendments also omit the baseline edits that chain W
needs (M4). Amendments 1, 2, and 5 need smaller wording changes (m10).

**Citations.** I spot-checked every `file:line` the spec and the audit cite for the passes (the
CLAUDE.md, pass-core, site-pass, cairn-pass, ship, spec-plan-review, diff-reviewer, both
implementers, both runners, `cairn-run-gate`, and `claude-tooling-sync`). All resolve to the
stated text. The finding counts per pass match the audit: B 20, C 27, D 14, E 7. PS-22 is
confirmed, because cairn-cms `check:close` begins with `npm run check`.

## Majors

### M1. DC-01 and DC-03 are regressions from `0a2e391`, which also deleted a third ruling

- **Location:** spec `:427-430` ("The global CLAUDE.md bullet predates it"); `CLAUDE.md:64`,
  `:169`, `:261`.
- **Defect:** `a7dd5ad` (13:39:54) landed three rulings in the global CLAUDE.md: the simplifier
  once per pass, "the pass class's gate runs inside the chain", and "Superpowers skills yield to
  it: TDD's write-first applies to `engine-logic` and `auth-data` only, and plans stay
  outcome-only." Five minutes later, `0a2e391` ("Slim the global CLAUDE.md", 13:44:48) was written
  from a pre-`a7dd5ad` base. `d48cea9` touched the same file at 13:39:36. That points to two
  sessions editing one file at once. `0a2e391` restored the per-commit bullet (`:64`), the
  "repo's full gate" chain sentence (`:169`), and "gates and code-simplifier" (`:261`), and it
  dropped the superpowers-yield sentence. That sentence now exists nowhere: a grep over `skills/`,
  `docs/`, `agents/`, and `claude-md-archive.md` finds no "yield" or "write-first". The audit
  missed the third loss. The spec's rationale misstates the history, which matters because the
  sweep's whole premise is RC3 (a ruling that lands in one home while older homes survive). This is
  a stronger case than RC3. A later rewrite reverted the ruling's own home.
- **Proposed fold:**
  1. Rewrite the DC-01 owner-decision paragraph to cite `a7dd5ad` as the ruling's CLAUDE.md
     home and `0a2e391` as the regression.
  2. B4 restores the `a7dd5ad` wording for DC-01 and DC-03 rather than composing new text.
  3. Add a `GA-nn` finding: the superpowers-yield ruling is restored in `pass-core`, where the TDD
     skill conflict executes (strongest form first), with one line in CLAUDE.md if wanted.
  4. Record `0a2e391` as RC3 evidence. Seed "the repo's full gate runs inside the chain" into the
     retired-phrase list with the DC-03 row.
  5. Have B4's implementer diff `a7dd5ad` against `0a2e391` over `claude/.claude/CLAUDE.md` and
     confirm that no fourth ruling was lost.

### M2. The DC-01 pointer line would narrow a ruling that covers non-pass work

- **Location:** spec `:342` ("`pass-core` owns it. The per-commit bullet and the 'straight through
  the gates and code-simplifier' wording in the global CLAUDE.md become one pointer line").
- **Defect:** `pass-core` loads only in a pass, and its step reads "Simplify, once per pass". The
  ruling's scope is "per pass **or branch**", and it covers Git Conventions for every commit. A
  pointer that says only "see `pass-core`" leaves a non-pass branch, a site-docs branch, or a
  `go-ship` or `ecxc-ski` `ship` landing with no stated rule. Those are the cases where an agent
  would otherwise fall back to the superpowers default or to habit. The ruling's meaning changes
  silently.
- **Proposed fold:** The CLAUDE.md Git Conventions line keeps the rule itself in one line (the
  `a7dd5ad` text: once per pass or branch at its close, TS, Svelte, or Go, never per commit, never
  for docs) and points at `pass-core` for the pass procedure. The small-task line reads "straight
  through the gates". The retired phrase is "Before committing code changes, dispatch".

### M3. Amendment 1 and the success test contradict pass B's AW-01 outcome

- **Location:** spec `:30-32`, `:367-368` ("Chain W needs no `reducedGate` workaround"); `:117-118`
  and `:298`; B acceptance at `:358-360`.
- **Defect:** RC4 and B1 make a no-`package.json` checkout with no explicit `reducedGate` a
  launch rejection. B's own acceptance tests exactly that for a dotfiles worktree. Chain W runs
  in a dotfiles worktree. The plan's Gates block (`style-guide-sync.md:36-38`) sets `gate` and
  `gateLane` but no `reducedGate`. After B, the amended plan's segment A launch is therefore
  rejected. The success test also demands that "any `reducedGate` pin added for AW-01" be
  removed. The spec asks for the pin to be both required and absent.
- **Proposed fold:** Amendment 1 says that chain W sets `reducedGate: "bash scripts/check.sh"`
  (or the per-task equivalent) as the explicit declaration AW-01 requires. The success test
  removes only the `notes` override. Alternatively, B1 infers the reduced gate as the full gate
  when no class default's commands exist. Pick one and make the success test and B acceptance
  agree.

### M4. Chain W's tasks will trip the ratchet's stale-entry and fingerprint rules

- **Location:** spec `:155-165` (fingerprints, shrink-only, "Stale entries fail"); amendments
  `:362-380`.
- **Defect:** Chain W fixes baselined findings: W3 fixes AW-08, and W4 fixes AW-24 and DC-28
  duplicates. Each fix leaves a stale entry, and `bash scripts/check.sh` fails with "remove this
  baseline entry". `ratchet-baseline.json` is in no W task's Files. W5 edits both implementers,
  whose duplicated checklist is an AW-21 pair. B3 and B4 also edit duplicated text. An edit inside
  a duplicated paragraph changes the pair's shingle hash. That makes the old entry stale and
  creates a new violation that shrink-only forbids adding back. The ratchet goes red in a way no
  task may legally fix. B's rule "each finding's entries leave the baseline in the commit that
  fixes it" covers only B's own findings.
- **Proposed fold:** Add an eighth amendment: every chain W task's Files include
  `ratchet-baseline.json`, and the task removes the entries for findings it fixes. For the
  fingerprint problem, either key duplicate-pair entries on the file pair plus finding id (not on
  a content hash), or allow an entry to be re-keyed (not added) in the commit that edits the pair,
  with the count unchanged. State the same allowance for B.

### M5. Pass E's DC-21 cut would delete ratified rules that `pass-core` does not carry

- **Location:** spec `:409-410` ("'Conducting a pass' cut to the budgets, the model line, and
  'invoke pass-core'").
- **Defect:** `CLAUDE.md:145-185` holds rulings that are absent from `pass-core/SKILL.md`. A grep
  for each shows none of them there:
  - "Parallelize genuinely independent tasks (Geoff, 2026-09-03)"
  - "Segment a pass at three to four tasks, every boundary on a green commit; override only for
    an irreversible task, a second `fix` verdict, or a disjoint Files seam (Geoff, 2026-09-12)"
  - the 80%-of-ceiling procedure
  - "One fold agent authors the close, with one independent `diff-reviewer` read"
  - "anything load-bearing lives in an artifact"
  - "Close the session rather than re-prime it after an idle gap"
  - "one caught reading diffs ... flags itself"

  The audit's section 4 row names only "per-task chain, thin conductor, below-six rule, ceiling
  and checkpoint". Cutting to the named remainder silently repeals the rest.
- **Proposed fold:** E's outcome for DC-21 becomes: every sentence of the section is either
  moved verbatim or near-verbatim into `pass-core`, or kept. A meaning ledger (sentence to new
  home) is part of E's close, and the reviewer checks it. Any sentence dropped outright is an
  owed erratum for Geoff, not a silent deletion.

### M6. A2's short-phrase rule conflicts with the plan fold's literal seeds and twin lists

- **Location:** spec `:241-242` ("A phrase shorter than three words is allowed only when marked
  exact"); amendment 2 at `:369-370`.
- **Defect:** The plan's Ruled inputs (`style-guide-sync.md:74-78`) fix nine literal strings for
  "both lists", case-insensitive. The plan fold (`...-plan-fold.md:41-42`) deliberately made the
  descriptive seeds literals ("25-40-word", "admin walkthroughs"). Four of the nine fall under
  three words: "academic introduction", "slightly academic", "25-40-word", and "admin
  walkthroughs". W6 appending them to pass A's list would be a config error unless it invents an
  "exact" marker that the cairn twin (`scripts/checks/retired-phrases.json`, R8) lacks. The twins
  would then diverge in format and semantics. Pass A's own seeds ("sleep 30", "CI-only", "currently
  1.26") hit the same rule. R8's list header must name the dotfiles twin, and amendment 2 does not
  give R8 the new path.
- **Proposed fold:** Define "exact" as a line syntax (for example, a leading `=`) and state that
  the cairn twin honors it, or drop the length rule and rely on the fixtures. Amendment 2 adds:
  R8's header names `claude/.claude/tooling/retired-phrases.txt`.

## Minors

### m1. `go-ship` switching to `code-simplifier` drops the poplar carve-out

- **Location:** spec `:342`; `CLAUDE.md:66`.
- **Defect:** `ship/SKILL.md:31` invokes `/simplify`, which in poplar resolves to poplar's
  project `simplify` skill (`poplar/.claude/skills/simplify`). The carve-out "(poplar keeps its own
  Go-aware `simplify` skill.)" survives in both the old text and the `a7dd5ad` text. B4's switch
  bypasses it in the one Go repo that uses `ship` most.
- **Proposed fold:** `go-ship` runs the repo's `simplify` skill when one exists, and
  `code-simplifier:code-simplifier` otherwise.

### m2. DC-29 leaves the generic footer hardcoded in the implementers

- **Location:** spec B3 `:325-332`.
- **Defect:** `cairn-implementer.md:58` and `site-implementer.md:51` hardcode `Co-Authored-By:
  Claude <noreply@anthropic.com>`. The audit's section 4 row deletes those copies, but B3 does not
  list them. Whichever way Geoff confirms, they contradict or duplicate the owner.
- **Proposed fold:** B3 reduces both to "the repo's commit conventions" (the chains prompt at
  `pass-execute-chains.js:238` already says this).

### m3. PS-15 cannot be baselined by the seat check, and the fold agent is not a reviewer

- **Location:** spec `:196`, `:395`, `:432-433`.
- **Defect:** The seat check reads agent frontmatter. PS-15 is dispatch text in a skill, so the
  seat check cannot see it. The audit's own wording is "PS-15 (if the seat is recorded)". The fold
  agent at `spec-plan-review/SKILL.md:99` authors a revision, which is the plan-authorship seat
  (`high`), not a reviewer seat.
- **Proposed fold:** Remove PS-15 from A1's baselined list. Scope C2's PS-15 to lines 95 and 124
  (reviewers and the verification reader) and leave line 99 at `high`.

### m4. OWNER FORK: which languages the simplifier ruling covers

- **Location:** spec `:342`; plan `style-guide-sync.md:406`.
- **Defect:** The ruling reads "TypeScript, Svelte, or Go". Passes A and B change Python, JS,
  and bash, so under the letter of the ruling they take no simplifier. The style-guide-sync close
  (step 1) runs it over `.mjs`, `.js`, and Vale YAML, which exceeds the letter. The spec says
  nothing, so each executor will guess.
- **Options:** (a) the letter: TS, Svelte, and Go only; (b) read TypeScript as including
  JavaScript; (c) any code language, skipping docs, CSS, and config.
- **Recommendation:** (b). JS shares TS's toolchain and the reviewer's competence, and the
  dotfiles runners are the code the sweep most wants tidied. Python and bash stay out unless Geoff
  says otherwise. State the answer in the `pass-core` step.

### m5. DC-19 must not narrow the DaisyUI-first rule to cairn-cms

- **Location:** spec E `:409`.
- **Defect:** The DaisyUI-first rule covers every cairn-family admin, including consumer sites'
  admin screens (`claude-tooling.md:95-98`: "the same audit over the consumer sites' admin
  screens"). `claude-tooling.md:95-96` cites the CLAUDE.md heading by name. The same section's
  first sentence (manifests and `claude-tooling-sync`) is workstation-wide, not cairn-only.
- **Proposed fold:** E moves the DaisyUI sentence to cairn-cms and each site's CLAUDE.md (or
  `site-pass`), keeps the manifest sentence global, and updates the `claude-tooling.md` heading
  citation in the same commit.

### m6. DC-17 reverses a ratified 2026-09-12 decision without saying so

- **Location:** spec C2 `:396`, F `:419-420`.
- **Defect:** Task 4 of the 2026-09-12 infra round (plan `:699-703`, ratified at `1ec5c0a`,
  HISTORY "Task 4 hoisted and supplemented the two instruction files") deliberately created
  `instructions/ai-operational-rules.md` with site supplements. Deleting it is a supersession
  with no citation. Dotfiles `docs/STATUS.md` still owes "whether aksailingclub-org ... wants a
  `CLAUDE.md` pointer at `~/.claude/instructions/`". STATUS's "Immediate next action" also still
  names docs-standard plan two, not this sweep.
- **Proposed fold:** C2's DC-17 row cites the 2026-09-12 task as superseded and seeds its
  phrasing per RC3. Pass A's pre-bake points dotfiles STATUS at the sweep and drops the owed
  pointer line.

### m7. `check-drift`'s repo scope exceeds the audit and pass F

- **Location:** spec `:274-275`, F table `:416-423`, E success test `:33-35`.
- **Defect:** `~/Projects/*/CLAUDE.md` matches ten repos: dubplate, healthy-diet,
  aksailingclub-legacy, and aksailingclub-sveltekit in addition to F's six. Violations there would
  seed entries with no pass letter, and E's success test cannot account for them.
- **Proposed fold:** Scan an explicit repo list (the audit's in-scope set), or add F rows for
  the others.

### m8. The baseline growth rules contradict each other, and so does the E success test

- **Location:** spec `:36-37`, `:162-163`, `:465-466`, `:33-34`.
- **Defect:** The success test says the baseline "never grows after pass A seeds it". The
  shrink-only rule allows growth for a new check id. The Risks section makes a threshold change a
  reseeding event for an existing check id, which shrink-only forbids. E's success test counts
  "a sanctioned parity copy" as an allowed baseline entry, but under A2 parity pairs pass and are
  never baselined.
- **Proposed fold:** Name the two sanctioned growth events (a new check id, and a threshold
  recalibration commit that also carries its calibration evidence) in one place. Drop "sanctioned
  parity copy" from E's test.

### m9. A2's scope is not the same as W6's

- **Location:** spec `:213-217`.
- **Defect:** A2 adds `instructions` and excludes vendored skills. W6 (`style-guide-sync.md:320-321`)
  excludes only `skills/synced/`, so it covers vendored skills such as `daisyui` and the vale
  skills. The spec's claim that the scopes match is inaccurate.
- **Proposed fold:** Say "a superset except vendored skills", or include vendored skills in the
  retired-phrase check alone.

### m10. Amendment wording

- **Location:** spec `:367-376`.
- **Defect and fold:**
  - Amendment 1 strips `notes` wholesale, but those notes also carry the absolute spec path that a
    zero-context implementer needs (RC5). Remove only the definition-of-done sentence.
  - After amendment 2, W6 writes no check, so its class `engine-logic` (test-first) no longer
    fits. Make it `docs` or `sweep`, and drop the acceptance lines that A's fixtures already prove.
  - Amendment 5 does not say whether W4's original two files (`technical-doc-web.md`, `editor.md`)
    also lose their measures sections (DC-28 names five). State all five, each keeping one pointer
    line to `MEASURES.md`, and add the acceptance line.

### m11. The `docs` class on B3 and B4 routes to the wrong review chain

- **Location:** spec `:323`, `:334`.
- **Defect:** Under `pass-core:90` and close step 3, the `docs` class takes "the docs tier" gate
  and "the register chain". Neither applies to agent definitions in a repo with no docs tier.
- **Proposed fold:** As the style-guide-sync spec did for W2 to W5, state that agent-facing
  definitions take `diff-reviewer` against their outcomes, with `bash scripts/check.sh` as the
  gate.

## Owed errata (record, do not edit)

- The global CLAUDE.md at `0a2e391` reverted three `a7dd5ad` rulings (M1). Restoring them is a
  fix, but the history belongs in HISTORY as a one-executor-rule incident.
- The 2026-09-12 infra round plan, task 4 (`instructions/ai-operational-rules.md` hoist), is
  superseded by DC-17 (m6).
- The audit's section 1 statement "code-simplifier per commit (global CLAUDE.md) against once per
  pass" should read "reverted by `0a2e391`".
- `claude-tooling.md:95-96` cites a CLAUDE.md heading that pass E will move (m5).
- `model-economy.md` "Current state" moves its values to `seats.json`. Keep the heading, because
  the global CLAUDE.md and `pass-core` cite it by name.
