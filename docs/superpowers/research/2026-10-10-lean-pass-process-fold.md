# Lean pass process spec: fold record

Target: `docs/superpowers/specs/2026-10-10-lean-pass-process-design.md`, revised in place from
`a02ba89`. Reviews: `2026-10-10-lean-pass-process-review-{contract,mechanics,risk}.md` beside this
file. IDs: `C-` contract, `X-` mechanics, `R-` risk. 35 findings in 22 roots. Owner rulings 11 to 14
(Geoff, 2026-10-10) are recorded in the spec's Rulings list.

## What the fold verified before acting

Each mechanism the revision states was read or probed on 2026-10-10:

- CI triggers: only cairn-cms and aksailingclub-org run tests on `pull_request`; ecxc-ski, 907-life,
  and cairn-pub carry only `deploy.yml` on push to `main`; dubplate, xcathletes-org, and dotfiles have
  no workflows. cairn's `test.yml:3-8`, `e2e.yml:3-8`, and `design.yml:9-14` run on push only to
  `main` and `rebuild`. Probe: draft PR #111 (`isDraft: true`) shows seven passing checks, so a draft
  PR runs CI. Only cairn-cms has `.github/ci-green.json`, so `ci-green` cannot watch the other repos;
  `gh pr checks --help` lists `--watch` and `--fail-fast`.
- Background Bash: the harness's Bash tool description says `run_in_background` "re-invokes you when
  it exits", and gives the default timeout as 120000 ms with a 600000 maximum.
- Worktrees (code.claude.com/docs/en/worktrees, fetched): "Subagent worktrees use the same base branch
  as `--worktree`, so they branch from your repository's default branch unless `worktree.baseRef` is
  set to `"head"`"; `"head"` is for "isolating subagents that need to operate on in-progress work";
  "A worktree is a fresh checkout, so initialize your development environment there." No settings
  file sets `worktree` today (grep of the stowed `settings.json`).
- Hooks (code.claude.com/docs/en/hooks, fetched): `additionalContext` in `hookSpecificOutput` "passes
  a string from your hook into Claude's context window", placed for PostToolUse "next to the tool
  result"; plain stdout from PostToolUse does not reach Claude. The stowed `settings.json` already
  runs PostToolUse hooks (`vale-hook`, `tellgrader --hook`).
- Launch: `claude --help` lists `--bg`, `--model` (accepts the `sonnet` alias), `--effort`, and
  `--permission-mode`; stowed `settings.json:11` sets `"defaultMode": "auto"`.
- `cairn-run-gate`: default wait 540 s (`:5-8`); light lane 2G high, 3G max (`:29-34`); the wait loop
  counts nominal seconds (`:333`); a finished result is deleted after one print (`:390`); the first
  argument is taken as the gate string with no flag check (`:119`). `notify-send --help` lists
  `-u normal`.
- cairn: `gate-tier.mjs` already runs `npm run package` first (header, leg 1) and records the
  component project stalling beside the node projects (`:71-76`); `npm run check` in a worktree needs a
  6G heap (cairn `docs/HISTORY.md:219`).
- Workstation: `~/.claude/{skills,agents,docs,workflows}`, `settings.json`, and `CLAUDE.md` resolve
  into `~/.dotfiles/claude/.claude/`; `cairn-pass` and `site-pass` (with `plan-template.md`) are
  tracked there; `scripts/check.sh:44` runs `tests/pass-execute-runners.test.mjs`;
  `retired-phrases.txt` and `check-claude-refs.py` scan agents, skills, workflows, and docs, and judge
  a worktree on its own tree.
- Repos: dubplate has `dubplate-implementer.md` and `simplifier-brief.md`, and its `CLAUDE.md:123`,
  `:135`, `:305`, and `:308` run the conducting loop, simplifier, and `go-architecture-reader`;
  ecxc-ski has a `ship` skill and `development-workflow.md`; aksailingclub-org's `CLAUDE.md` is 262
  lines and dubplate's 356.

## Dispositions

| Root | IDs | Disposition |
|---|---|---|
| 1. Full suite runs nowhere in six repos | C-B1, X-B1, R-B1 | Owner ruling 11. Folded into Rulings and Close ("full-suite home is green"); the retired list now says "per-task local full gate". |
| 1a. Success test scores only cairn | R-B1 (compounding) | Refused: Geoff set the success test at approval; every close's PR score still records each pass's numbers. |
| 2. Branch push runs no CI; no red reaches the session | C-M1, X-M3, R-M3 (CI part) | Folded, Execution 4: draft PR at first push, adapter watch command as a background Bash task, red stops the line. `gh pr checks` where `ci-green` has no config. |
| 3. One class per pass versus per-task reads | C-M2, R-M2 | Folded, Lifecycle preamble: per-task class from the adapter path map, declared class a floor, `runner` by path list, `unattended` becomes the `live-account` flag; Close re-derives classes. R-M2's scripted classifier with a fail-closed path table refused: new machinery with no published source, and the close re-derivation catches a misclassed task before merge. |
| 4. Success test vacuous and unscorable by row | C-M3 | Folded, Success test: clock start, end, and exclusions; `--records` source; escape window and detectors; five rows; an escape names its step. |
| 5. Process-doc fold has no inventory | C-M4, R-M5 (guards) | Folded, table row: step 1's plan lists every rule with a home or a deletion. The API-drop wake-up and lid-switch hold are named in Execution 1; effort defaults in the Lifecycle preamble. R-M5's retargeting of `claude-wf-guard` refused: it still guards `docs-page-chain` workflow runs, and the inventory decides its home. |
| 6. Fast lane runs a browser off the heavy lock and overcommits memory | C-M5, X-B3, R-M6 | Folded, Execution 3 and rollout step 2: a browser leg runs alone on the heavy lane; non-browser legs go light only if a measured peak fits the 3G cap. Correction: all three reviews put non-browser legs or the type check on the light lane, but cairn's type check takes a 6G heap, so the lane follows a measurement. X-B3's package-first step needs no change (already leg 1). X-B3's per-leg records in `cairn-run-gate` refused: new machinery; the classifier is the fast lane's one home (also C-m3). |
| 7. Adapters in the wrong repo; edits go live mid-cutover; runner test reddens the gate | C-M6, X-m2 (repo, test), R-B2, R-m1 | Folded, Rollout preamble and step 1: adapters move into step 1; step 1 works in a dotfiles worktree and lands as one merge with a `pre-lean-process` tag for rollback; the runner test and its `check.sh:44` line go with the runners (table). R-B2's additive-first reorder refused: the atomic merge plus "no pass runs until its repo's step merges" closes the same windows with no extra step. |
| 8. Sweep misses concept-carrying files; no executable check; CLAUDE.md caps unactioned | C-M7, R-m2, X-m2 (caps) | Folded, steps 1 and 3: sweep includes docs and retired concepts, superseded phrases join `retired-phrases.txt`, `scripts/check.sh` green; per-repo grep list, dubplate and ecxc-ski files named, dubplate adapter, two CLAUDE.md files to the cap. |
| 9. `auth-data` verdict unhandled; `diff-reviewer` loses its bar | C-M8, X-M4 (reviewer part) | Folded, Execution 5 (a `fix` or `escalate` stops the line), Close (verdicts in the PR body), table row (`diff-reviewer` rewritten). |
| 10. Checklists have no loader; Go has no checklist; visual gate dropped | C-M9, X-M4 | Folded, Close: adapter glob table, `go-conventions` for Go, `visual-verifier` on rendered UI. C-M9's `go-architecture-reader` as the Go checklist refused: no catch-ledger record (ruling 2); it leaves the process with `code-simplifier` (table) and dubplate's dispatch is swept (step 3). |
| 11. Clock stop has no trigger and no reader | C-M10, X-M2 (trigger, recipient), R-M5 (self-enforced) | Recipient: owner ruling 13. Trigger folded, Execution 6: a PostToolUse hook over a task-clock file. C-M10's commit-timestamp check at each gate result and R-M5's `/loop` enforcement refused: both depend on a check the session or a between-turn tick runs, while the hook fires on the tool calls a stuck gate loop keeps making. |
| 12. Executing session's launch unspecified | X-M2 (launch) | Folded, Execution 1: launch command and session id in STATUS. |
| 13. Pair worktrees branch from `origin/main`; no merge-back, setup, or disjointness | X-B2, R-M3 (merge), R-M4 (setup) | Folded, Execution 2, table settings row, step 1 pair probe. |
| 14. Lessons frozen in HISTORY | R-M4 (harvest) | Folded, step 3: "wrong to rediscover" bullets move to executing homes in steps 2 and 3. |
| 15. `cairn-run-gate` fixes miss the race, the overrun cause, and the timeout | X-M1, C-m3 (600 s) | Folded, Execution 7: persistent result, `--fresh`, `$SECONDS` deadline, unknown flag exits 2, timeout in the exit-75 text. C-m3's "wait plus lock wait under 600 s" refused: the caller's loop waits on a status file, and the overrun comes from nominal counting (`:333`), not lock wait. X-M1's 480 s default refused as tuning the plan can make once `$SECONDS` bounds the wait. |
| 16. `defer` undefined | C-m3 (defer), X-m1 | Folded, Execution 7: defined from the parked design, section 5 item 4; never where the full-suite home is local or on `auth-data`. |
| 17. Fast-lane mode has two homes | C-m3 (home) | Folded, Execution 3: the classifier selects legs and `cairn-run-gate` runs them; "fast-lane mode" leaves `cairn-run-gate`'s list. |
| 18. Pass B's plan is in the retired format; Task 2 skips its read | C-M11, X-m2 (pass B), R-M2 (Task 2) | Folded, step 5: re-planned as a lean task list outside the clock, merges `main` after step 2, Task 2 gets the `auth-data` read. Pass B's plan is not edited here. |
| 19. Docs-chain audit has no pass mark | C-M12 | Owner ruling 14; settled pass mark folded into step 4. |
| 20. dubplate rung 14a rides deleted machinery | R-M1 | Owner ruling 12; the hold is recorded in dubplate's STATUS before step 1 merges (Rollout preamble), and dubplate gets an adapter (step 3). |
| 21. Loaded CLAUDE.md teaches the old process during the cutover | C-m1 | Folded, Rollout preamble: the launch prompt names this spec as overriding; the cutover is `runner` class, and its full-suite home is `scripts/check.sh` (step 1). |
| 22. Lens identity and verification-read outcome open | C-m2 | Folded, Lifecycle 3 and 4: the third lens is "data integrity and failure risk"; the fold agent applies the read's findings, and only a blocker earns another read; the default plan lens is mechanics, with a verification read. |

Counts over the 35 findings: folded 30 (some in part), owner ruling 5 (C-B1, X-B1, R-B1 under 11;
R-M1 under 12; C-M12 under 14; C-M10 and X-M2 also take ruling 13 for their recipient half), refused
whole 0. Refused parts: 10, each named in its row.

## Owed errata

None. The revision changes no ratified document's meaning silently. Every document whose practice
changes (global `CLAUDE.md`, `pass-core`, dubplate `CLAUDE.md:305`, the two adapters) is named in the
spec's table or rollout as rewritten. The STATUS resume prompts in dotfiles and cairn-cms cite
"Lifecycle step 4", "Rollout steps 1 to 4", and "rollout step 5", which keep their subjects.

## Open for Geoff

None. Rulings 11 to 14 settle every fork the reviews raised; the remaining calls are method calls.

## Measures

- New-mechanism findings: 1 folded, 4 refused.
  - Folded: the PostToolUse clock-stop hook (X-M2). Source: Anthropic, "Unlike CLAUDE.md
    instructions which are advisory, hooks are deterministic" (guidance file, section 6), with the
    hooks docs for `additionalContext`. Measured defect: pass B S1 ran 95 minutes with no stop until
    Geoff stopped it (catch ledger S7 item 3).
  - Refused: the scripted fail-closed classifier (R-M2), `/loop` clock enforcement (R-M5),
    `cairn-run-gate` per-leg records (X-B3), and the `claude-wf-guard` retarget (R-M5).
  - Not counted as new: `worktree.baseRef: "head"` (a documented setting that makes the approved pair
    mechanism branch from the right commit), the `defer` definition and the `--fresh` override (both
    complete mechanisms the approved spec already named), the draft PR and the rollback tag
    (conventional practice), and the watch commands (existing tools).
- Spec length: 167 lines before, 221 after (+32%). Rulings 11 to 14 and the revision note account
  for 11 of the 54 added lines; the rest is +26%.
