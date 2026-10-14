# Pass 5 plan review: mechanics and feasibility

Reviewer: `plan-reviewer`, at commit 456b409. Saved verbatim by the planning session.
Citations: `plan:N` is `docs/superpowers/plans/2026-10-13-drafter-p5-pipeline-plan.md`, `prompt:N` its executor prompt.

Context at review time: the design's rulings 5 to 7 were an uncommitted edit (Workflow opt-in, `billing_cycle_day` 1, restore). The exemplar captures have since been restored; `tellgrader` is still not installed.

## Blockers

1. Blocker, correctness. `plan:200` (P5.4 acceptance) needs `tellgrader`, absent on pavilion, on an offline task, breaking the plan's offline-first rule (`plan:50`, `plan:86-87`). Source at `~/.dotfiles/claude/.claude/skills/writing-voice/evals/tellgrader/`; `make install` puts it in `~/.local/bin` (cairn STATUS names that command; it builds offline in seconds). OWNER FORK vs design ruling 7: (a) the executor runs `make -C ~/.dotfiles/claude/.claude/skills/writing-voice/evals/tellgrader install` first; (b) keep the wait and move P5.4's tellgrader check after P5.7. Recommend (a).
2. Blocker, correctness. `plan:200`: the tellgrader proof passes vacuously in drafter; gating happens only under the `docs-register` profile, taken from the scanned repo's `.tellgrader.json`, which drafter lacks. Probe: a hinge-run paragraph exits 0 without `--profile`, 2 with `--profile docs-register` (`cmd/tellgrader/root.go`). Fold: `tellgrader --register docs --profile docs-register README.md docs/*.md`, require exit 0.

## Major

3. `plan:296-297` (P5.8): committing only plan and framing leaves the tree dirty; the chain's front half also writes `docs/internal/option-map.json` and the facts files (`docs-page-chain.js:106-120`), and drafter refuses a dirty tree. Fold: commit every path in `git status --porcelain` on the scratch branch, assert empty before `drafter page`.
4. `plan:92-94` (P5.1 stage 1) mismatches the chain's `drafter check-plan --facts … --outline <outline>` (`docs-page-chain.js:146-147`). Counting only the run's pages as listed makes a part 2 plan linking another unwritten outline page escalate `plan`. Also `plan.Outline` has only an unexported `paths` map built by `LoadOutline(s)`; P5.1's Files omit `internal/plan`. Fold: stage 1 loads the project's outline files plus the run's pages, via a new `plan` constructor or a temp outline JSON; name the outlines by a project setting (e.g. `plan.outlines`) or the handoff's `context.args`. Test: a link to an outline-listed page not on disk warns, doesn't escalate.
5. `plan:216` and P5.1: the round-2 baseline blob is never written. `git hash-object` without `-w` then `git cat-file blob` fails (exit 128); the chain uses `git hash-object -w` (`docs-page-chain.js:198`). Fold: P5.1 states `git hash-object -w -- <snapshot>`; test that a round-2 request inlines a real two-sided diff.
6. `plan:301-303`, `plan:310` (P5.8): "accepted, or escalated with empty faults" passes on a stage-1 `plan`, `cap`, or `unreadable draft` escalation, so pilot-ready could rest on a run that never reached the back half. OWNER FORK: (a) keep; (b) also require the record show the round-1 reads ran; an earlier escalation means one rerun if the meter allows, else the PR says "not pilot-ready" with the reason. Recommend (b).
7. `plan:302` reads every fault as a drafter defect, but the spec puts model-caused events in `faults` (a failed coverage quote, an empty read). Fold: classify faults; fix forward only drafter-caused ones (a refusal the answer didn't cause, a parse failure of a schema-valid answer); record model-caused faults in the PR. The design's "empty faults" bar needs the same reading (part of fork 6).
8. `plan:271-276` (P5.7): production request shapes never run live if pass 2 ran its smoke. Fold: P5.7 always runs `make smoke` after P5.6, meter check first.
9. `plan:298-300`, `plan:271-273`: long blocking runs in the foreground Bash tool (max 600000 ms). Fold: `run_in_background`; on exit 3 follow the printed `--resume` line.
10. `plan:259-262` (P5.7): the batch discount key is never named. `config.Prices.BatchDiscount float64` (pass 1:68) has no stated meaning (fraction off or multiplier); left at 0 as a multiplier, every batch cost and `Worst` is $0 and no cap trips. Fold: P5.7 names the key and value from the pricing page, citing pass 2's documented meaning; acceptance shows a nonzero batch estimate (`ledger.Worst` check or a `--dry-run` before the live run).
11. `plan:22-23`: risk class. The money-deciding code (P5.1 reserve before submit, cap escalation; P5.2 resume's "no second create", settle-once) is `ordinary`, though the design raised pass 2 for exactly this. Also the `runner` reason is wrong: cairn-pass maps `scripts/docs-review/**` to `ordinary`. OWNER FORK: (a) raise P5.1's reserve/settle path and P5.2 to `auth-data` (test-first, `diff-reviewer` per task); (b) keep `ordinary`. Recommend (a) for P5.2 at least. Either way restate the `runner` reason as the design's per-pass ruling and the P5.8 Workflow run.

## Minor

12. `plan:107-111`, `plan:149-155`: the index file the `index_link_command` edits (`docs/extend/README.md`) is outside restore and resume. Fold: snapshot and hash it around each link command; restore on escalation; list it among drafter's own files on resume. (P5.8 and the pilot don't hit it: all 10 part 2 pages are on disk and linked.)
13. `plan:177-182` (P5.3): the dirty-tree exit-2 test passes vacuously on a non-git fixture. Fold: temp copy of `e2e/testdata/project`, `git init` and commit; clean dry run exits 0, touched file exits 2 naming it; set the key env with `t.Setenv`.
14. `plan:282-287` (P5.8 preconditions): passes 2 to 4 must be on drafter `main` before `EnterWorktree`; and no rule for zero or several matching Workflow run files (layout unverified on this machine). Fold: pre-launch check that passes 1 to 4's interfaces are on `origin/main`; none means stop and notify, several means newest by mtime, recorded.
15. `prompt:33-37`: "the setup appearing on disk resumes you" has no mechanism. Fold: a `run_in_background` until-loop on the disk checks; the workspace ID resumes only on Geoff's message.
16. `plan:304-307` vs `design:65`: the 5% check moves to Geoff. Fold: the PR states pilot-ready conditional on that comparison, listed as the one open acceptance item.
17. `plan:298-300`, `plan:46`: which `drafter` binary the meter and run use, and when it's built. Fold: `make -C <worktree> build`, use that binary for both.
18. `plan:92`: `plan.CheckOptions` needs `Root`, and callers confirm a facts dir with `CheckFactsDir` first. Fold: one clause.
19. `plan:152`: adoption skips the spec's "waits for each to end"; `batch.Batch` has no `custom_id`s, which come only from `Results`. Fold: `List`, then `Get` until ended, then `Results` and match.
20. Optional. `plan:279-311`: P5.8's 90 minutes is tight. Fold: 120 (path 495, under the 720 line), or treat batch polling like the Geoff wait.
21. Optional. `plan:328`: `billing_cycle_day` is settled by ruling 6. Fold: drop the item.
22. Optional. `plan:186-204`: P5.4 documents `drafter page` before P5.3 builds it. Fold: pair P5.4 with P5.3, P5.2 with P5.6.
23. Optional. `plan:218`: `register.<track>` in cairn's `drafter.toml` duplicates the chain and nothing reads it. Fold: leave unset.
24. Optional. Pair dispatches name no model, effort, or description. Fold: one line under Tasks (Sonnet medium, `description: "<pass> task <n>"`).
25. Optional. `prompt:8`: the plan path isn't on `main` yet. Fold: the conductor launches after the plan branch merges.
26. Optional. `plan:206-228` (P5.5): cairn `docs/STATUS.md` may conflict with cairn's drafting sessions. Fold: rebase the STATUS edit onto `origin/main` at close.

## Checked and sound

Consumed interfaces in `plan:59-65` all exist in passes 1 to 4 or `internal/plan`; the batch method set (`plan:69-71`) matches pass 2. Path 465 = 1.9x 240. `secret-receive` writes `^export NAME=` lines, so `plan:251`'s check is valid. `DRAFTER_CYCLE_CEILING` matches pass 1's env rule. cairn's docs gate skips tellgrader when absent (`check-tellgrader.mjs:14,71`). Three figure-free task guides with YAML plans exist: `restrict-admin-access`, `add-a-second-sign-in-group`, `rotate-the-github-app-key`. P5.7's local config matches source.
