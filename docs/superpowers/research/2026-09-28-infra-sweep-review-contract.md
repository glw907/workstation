# Infra sweep spec review: contract and criteria lens

Target: `docs/superpowers/specs/2026-09-28-claude-infra-sweep-design.md` at dotfiles `3f41deb`.
Evidence read: the audit record, the style-guide-sync plan, and the live files cited below
(`pass-execute-chains.js`, `cairn-run-gate`, `claude-tooling-sync`, `claude-context-budget`,
`scripts/check.sh`, `scripts/githooks/pre-commit`, `pass-core/SKILL.md`, `model-economy.md`, the
agent frontmatter, and `~/Projects/*`). Line numbers are the spec's unless a file is named.

Counts: 2 blockers, 9 majors (one an owner fork), 9 minors. Ranked by consequence within each
tier.

Disposition reconciliation: all 87 audit ids are accounted for. 79 have a pass in the spec, which
sums correctly (A 3, B 20, C 27, D 14, E 7, F 8). Four of the eight ids the style-guide-sync plan
owns (PS-07, AW-09, AW-10, DC-27) never appear in the spec (minor m9). Nine ids are split across
two passes by half: AW-11, DC-03, PS-14, DC-09, DC-17, DC-22, PS-25, DC-23, and DC-04 (both halves
in B). Each half is labelled, so no id has two competing dispositions.

## Blockers

### X1. The AW-01 fix rejects the amended chain W at launch

- **Where:** 115-118, 298, 29-32, 358-360, and 367-368.
- **Defect:** RC4 and B1 say a checkout with no `package.json` must name both a gate and a reduced
  gate, or the run is rejected at launch. Chain W runs in the dotfiles tree, which has no
  `package.json`. The plan's Gates block (plan:36-38) sets `gate` and never sets `reducedGate`.
  The success test (31) and amendment 1 (367) remove "any `reducedGate` pin added for AW-01"
  before the run. B's own acceptance (358) confirms the rejection. As written, the amended plan
  is rejected on its first invocation, which defeats the owner goal.
- **Fold:** apply the audit's "repo-neutral default" option. When a task names an explicit `gate`
  and no `reducedGate`, the reduced gate is that full gate, never an npm string. Reject at launch
  only when neither gate can be derived. Change B's acceptance to three cases:
  - no `package.json` and no gate: rejected;
  - an explicit gate with no reduced gate: every reduced round renders that gate;
  - an explicit reduced gate: rendered as given.

  This is a method call, not an owner fork.

### X2. Every edit to a baselined duplicate paragraph fails the gate, and no move is legal

- **Where:** 155-157, 161-165, and 237.
- **Defect:** the duplicate-paragraph fingerprint is "the paragraph pair's shingle hash." Edit
  either paragraph without fixing the duplication and three things happen:
  - the hash changes;
  - the old entry goes stale ("remove this baseline entry");
  - the same duplication comes back under a new fingerprint as an added entry, which shrink-only
    forbids.

  The passes that edit these files leave the duplication in place until E:
  - B4 edits global `CLAUDE.md:169` inside the "Conducting a pass" section that DC-21 baselines
    as a duplicate of `pass-core`;
  - B4 edits `pass-core` itself (PS-14);
  - B3 and the plan's W5 edit both implementer definitions (AW-21's duplicated checklist);
  - W2 and W4 partly remove AW-24's tell copies.

  Each of those tasks goes red with no sanctioned path except fixing E's consolidation early.
  Retired-phrase and dead-reference fingerprints do not have this problem.
- **Fold:** key a duplicate entry on `(check, fileA, fileB)` with the overlap count, which may
  only fall. Separately allow a re-key in the same commit when the finding id and the file pair
  are unchanged, and when the file is renamed (see m4). Add fixtures for an edited-but-still-
  duplicate pair (passes) and a new pair (fails).

## Majors

### M1. Shrink-only passes vacuously on `main`, and "new check id" can reopen an emptied check

- **Where:** 161-163.
- **Defect, part one:** "compares the file to its copy at `git merge-base HEAD main`" compares
  `main` with itself whenever HEAD is `main`. Dotfiles `main` takes mostly direct commits:
  626 commits, including this spec (`3f41deb`) and the audit (`0413e39`). `check-drift` also runs
  on `main`. Any direct commit can grow the baseline and still pass.
- **Defect, part two:** "may appear in the same commit that introduces the check" cannot be
  verified by a merge-base comparison, which sees the branch, not the commit. If "new" is read as
  "no entries at the merge base," a check whose entries all get fixed becomes "new" again and can
  regrow.
- **Fold:**
  1. The pre-commit hook compares the staged baseline with HEAD's copy. This covers direct
     commits and branch commits alike.
  2. `check.sh` keeps the merge-base comparison off `main`, and on `main` compares with `HEAD^1`.
  3. A check id is new only when it is absent from the checker's registry (a `CHECK_IDS`
     constant) at the comparison point, never when it merely has no entries.
  4. Fixtures cover growth on `main` (fails), growth under an emptied existing id (fails), and
     growth under an id new to the registry (passes).

### M2. Pass B's success test has no concrete check

- **Where:** 29-32 and 357-360.
- **Defect:** "the style-guide-sync run hits no infra defect the audit named" has no procedure.
  B's acceptance tests a generic dotfiles worktree, not the plan's actual arguments. It also
  never asserts that nothing lettered B remains.
- **Fold:** B's acceptance gains four checks.
  1. A baseline query: zero entries lettered A or B.
  2. A dry render of both style-guide-sync segments with the amended plan's real arguments
     (chains R and W in one invocation). The render asserts five things:
     - W's prompts name no npm command;
     - every reduced round renders the single constant;
     - no reduced round carries a MISMATCH-blocking line;
     - W spawns no classifier probe;
     - R's probe runs once, on `haiku`.
  3. A grep of the amended plan confirming the three named workarounds are gone. This is the
     success test's second sentence, made checkable.
  4. At the style-guide-sync close, every runner halt, escalation, or `fix` reason is mapped to an
     audit id or to "not infra." The pass succeeds when zero reasons map to an audit id. Record
     this in that plan's close.

### M3. A finding can be "baselined" in name only

- **Where:** 228-237, 252-254, and 277-280.
- **Defect:** nothing asserts that each id in a "Baselined findings" column gets at least one
  seeded entry. The phrases for DC-01, DC-04, DC-06, DC-30, PS-04, and PS-05 are never named.
  Line 252 cites "the RC3 rows above," but RC3 (92-109) lists no phrases. Only "sleep 30" and
  "currently 1.26" are given. A seeding that picks non-matching phrases produces no entries and no
  stale failure, and the finding silently loses its guard.
- **Fold:** A's acceptance prints a table with one row per Baselined id and its seeded entry
  count. A zero passes only with a named reason (for example, "cross-repo only, checked in
  mode X"). The plan names each seeded phrase with a witness `file:line`.

### M4. A's `check-drift` acceptance cannot pass as scoped

- **Where:** 274-275, 196, and 279.
- **Defect, the context budget:** `claude-context-budget` has no baseline, and DC-02 is red today.
  The 907-life `docs/STATUS.md` is about 4,504 tokens against a 4,000-token budget, and pass F
  fixes it.
- **Defect, the repo scope:** "every repo under `~/Projects` that has a CLAUDE.md" is 10 repos.
  Four of them are outside the audit (`dubplate`, `healthy-diet`, `aksailingclub-legacy`, and
  `aksailingclub-sveltekit`). Their project agents (`dubplate-implementer`,
  `healthy-diet-implementer`, and the rest) have no seat, and "an agent with no seat fails."
  No pass owns them.
- **Fold:** list the in-scope repos explicitly in a tooling config file, with other repos opting
  in by a later edit. Route context-budget results through a baselined check id so DC-02 is a
  known entry lettered F.

### M5. The fixtures read live machine state

- **Where:** 206-208 and 256-260.
- **Defect:** `claude-tooling-sync` hardcodes `HOME`, `TOOLING`, and `SKILLS` to
  `~/.dotfiles` (`claude-tooling-sync:26-30`). The collision check reads `~/Projects/*`. Memory
  citations read `~/.claude/projects/*/memory`. Cross-repo mode reads `~/Projects/<name>`. The
  must-fire fixtures for these checks either exercise live state, which is flaky, or cannot be
  built at all, which leaves them vacuous. The collision check also contradicts the spec's own
  rule (222-224) that the dotfiles gate never goes red on another repo's state.
- **Fold:** make every root injectable (home, projects root, memory root) and have each fixture
  set them. Add one fixture that asserts no read happens outside the fixture root.

### M6. The failure-state matrix is incomplete

- **Where:** 166-170, 198-199, 206-208, 241-250, and 256-260.
- **Defect:** the spec states these rules but gives several of them no fixture:
  - **Many bad.** Neither tool has a many-bad fixture proving every violation reports, grouped,
    with counts.
  - **Malformed baseline.** A2 has none: bad JSON, an unknown check id, a bad finding-id format.
    The baseline is "read by both tools," and whether they share a parser is still open (477).
  - **Manifest.** Absent or malformed should exit 2; there is no fixture.
  - **Seats.** "An agent with no seat fails" has no fixture.
  - **Retired list.** A phrase under three words without the exact marker has no stated result
    (exit 2 or a violation?) and no fixture.
  - **Pre-commit NOTE.** No fixture.
- **Fold:** the plan carries one table of state, tool, exit code, and report line, and adds one
  fixture per row.

### M7. The style-guide-sync amendments omit the ratchet's effect on chain W

- **Where:** 364-380.
- **Defect:** several W tasks clear baselined findings:
  - W3 clears AW-08, a dead reference;
  - W2 and W4 clear AW-24's duplicates;
  - W4 clears DC-28's duplicates.

  Under "stale entries fail" (164), each of those tasks must also edit `ratchet-baseline.json`,
  which is not in any W task's Files. The implementer either stalls or trips the diff-reviewer's
  out-of-Files check.
- **Fold:** add amendment 8. Each W task that clears a baselined finding removes its entries in
  the same commit, and the baseline file joins that task's Files.

### M8. The "pointerless spec" rule is mostly false positives

- **Where:** 235.
- **Defect:** "the spec" or "the plan" appears 13 times across the agents. About 12 of those are
  correct text, such as "you do not read the plan file yourself" (`cairn-implementer.md:16`,
  `diff-reviewer.md:11`, `go-architecture-reader.md:11`). Only AW-18 (`site-implementer.md:110`)
  is the defect. The baseline would absorb about 12 `GA-nn` entries, and pass C would then have
  to reword correct sentences.
- **Fold:** fire only on an instruction to consult an unnamed document ("per the spec", "the
  spec's", "follow the plan's") with no path on the line. Add must-not-fire fixtures for the
  negations.

### M9. OWNER FORK: pass A carries work that serves passes C to F, not the sync run

- **Where:** 144-280 against the owner goal: "fix what the style-guide-sync run would hit first."
- **Defect:** the sync run needs only a few A outcomes:
  - the retired-phrase check and the baseline mechanics (for W6);
  - `--root` (amendment 3);
  - the `ship` rename (PS-01).

  The rest guards findings that C to F fix after the run. Ranked by cost:
  1. The duplicate-paragraph check with threshold calibration and the parity list. This is the
     most research, and the source of X2.
  2. Cross-repo mode, `check-drift` over every repo, and context-budget integration. This is the
     source of M4.
  3. The seat table and seat check.
  4. The orphan, memory, heading, description-cap, fork-lint, and sibling-name checks.
- **Recommendation:** split A. A-core runs before B: the baseline mechanics, the retired phrase,
  dead references, `--root`, collision, and unmanifested skills. A-rest runs after the sync, ahead
  of C and D, with the items above. This cuts the attended wait for the sync run and moves X2's
  risk off its path. Keep a single pass if Geoff values guarding B's own edits against regression
  more than reaching the sync run sooner.

## Minors

- **m1 (246-248). Calibration has positives only.** "Every confirmed row in section 4 fires"
  includes rows that are not paragraph duplicates: divergent strings (the four reduced-gate
  definitions) and hand lists (`check:close`). It also includes rows reachable only in cross-repo
  mode (DC-22, PS-25), and it names no negative control. **Fold:** calibrate against the
  Duplicate-paragraph Baselined ids that are in self-mode scope. Add a named negative set, such as
  shared frontmatter, the template headings, and the implementer report block. Report the count of
  new `GA-nn` entries as a noise measure.
- **m2 (92-109, 334-348). RC3 is applied to DC-01 only.** DC-03, DC-29, PS-14, AW-17's vanished
  clause, AW-20, and AW-23 also retire text but add no phrase, so B's fixes have no regression
  guard. DC-03's phrasing also survives outside its disposition list at `model-economy.md:38`. A
  bare "the repo's full gate" phrase would false-fire on `pass-core/SKILL.md:86-87,160`.
  **Fold:** each B row that retires text names its phrase, specific enough to spare the class
  table ("the repo's full gate runs inside the chain"). Add `model-economy.md:38` to DC-03.
- **m3 (320, 476). The vanished-run exit code can collide.** `cairn-run-gate` passes the gate's
  own status through (`cairn-run-gate:129`) and already uses 2 for a lane error (`:47`), so any
  fixed code can collide with a gate's real exit. **Fold:** make the contract output-keyed (a line
  distinct from `gate exit:`), with the code secondary. The new test covers a gate that itself
  exits with the chosen code.
- **m4 (155-157). No rule for renames.** Path-keyed entries go stale and reappear as new when a
  file is renamed: A's own `ship` to `go-ship`, and D's move of `bubbletea-conventions.md`.
  **Fold:** a same-commit rename re-keys, covered by the X2 fold.
- **m5 (271). The quoted-version-pin check (DC-14) has no tool home.** It is a close-step sentence
  only: not in `check-drift`, with no check id and no fixture. **Fold:** make it a cross-repo-mode
  check id, baselined DC-14 (F).
- **m6 (100-104, 273). The hook ends in `exec gitleaks`.** `scripts/githooks/pre-commit` exits
  through `exec gitleaks git --staged`, so the NOTE and M1's comparison must run before it without
  losing its fail-closed exit. **Fold:** state this in A3's outcome.
- **m7 (367-368). Amendment 1 drops the `notes` override without saying what stays.** The W
  `notes` also carry the absolute spec path (plan:36-38), which zero-context implementers need.
  **Fold:** remove only the definition-of-done sentence.
- **m8 (146, 290, 323, 334). The pass classes misfit this repo.** `engine-logic` is "TypeScript
  behavior." `docs` means "the docs tier" gate with "the register chain" review and no test
  mandate (`pass-core/SKILL.md:87,90`). Neither fits Python and bash tooling or agent definitions.
  B3's AW-19 changes agent behavior under a class that has no mandate. **Fold:** state the gate
  (`check.sh`, light lane) and the review bar (`diff-reviewer` against acceptance) per task. Give
  B3 a mechanical acceptance, such as retired phrases for the npm done-list.
- **m9 (309-312, 306, 321). Some promises have no test.** B1's test list omits the DC-04 launch
  NOTE. AW-20's "no prompt carries a vanished clause" is not asserted. The spec never names PS-07,
  AW-09, AW-10, or DC-27. **Fold:** add both assertions. Add one line mapping the eight
  sync-owned ids to their W tasks, so the 87 reconcile inside the spec.

## Confirmed sound

- Stale-entry failure rules out fingerprints that never match.
- The exit-code split (0, 1, 2) and the "empty retired list exits 2" rule avoid a vacuous
  tripwire.
- The B finding count (20) and the whole pass arithmetic match the audit.
- The retired phrases the plan names all sit inside W2 to W4's Files (grep-verified), so W6
  appending them never starts red.
