# drafter F1 plan: format additions from cairn's 11-plan test

Design: approved by Geoff on 2026-10-12 in session `drafter-conductor` ("yes, launch F1"). While
drafter Pass 0 ran, cairn-cms wrote 11 real page plans against plan format v1 and sent eight
batches of findings. The conductor triaged them. The accepted additions that the installed
`check-plan` refuses are this pass. The rest were answered as conventions in the interim sheet,
`~/.local/share/drafter/plan-format-v1.md`, which this pass folds into the reference so the sheet
can retire.

Every change is an optional addition. `version: 1` and the stability rule hold, and every plan
valid under Pass 0 stays valid.

## Shape

Risk class: `ordinary` for every task. No `live-account` flag. One repo is changed:
`~/Projects/drafter` (`glw907/drafter`, public), on a branch `f1` cut from `main` (`140bc00`). Gate:
`bash scripts/drafter-gate.sh` from the session's dotfiles worktree, which runs `make check` on
the drafter checkout. Full-suite home: that same gate, once on the close head. There is no CI.

The dotfiles worktree exists only to hold the clock file and the session's working directory. The
pass changes nothing in dotfiles and opens no dotfiles PR.

Estimate: 175 task-minutes. The pass is `ordinary`, so it merges its own PR after a green close
gate and an accepted whole-branch review, when its "Found, not done" list is empty. Otherwise it
stops at PR-ready.

Out of scope, recorded under "Later" in the amendments file: a crossLinks check, a `drafter
anchors` command, raw `<a id>` anchors, a cross-plan anchor check, and the mirror check on
`failure.from`.

## Tasks

### F1.1 Decode the new fields (45 min, ordinary)

- Outcome: `internal/plan` types, the strict decoder, and `schema/plan.schema.json` accept these:
  1. `introduction.facts`: an optional list of fact ids.
  2. `code.facts`: an optional list of fact ids.
  3. `step.optional`: an optional boolean, default `false`.
  4. `link.text`: optional prose.
  5. `section.anchor`: an optional plain string.
  6. `code.source` may be an `http(s)://` URL as well as a repo path.
  7. A level-2 section's `items` may be empty when the next section in the list is level 3. Any
     other empty `items` stays a finding.
  8. `reason.facts`: an optional list of fact ids.
  9. `code.source` becomes optional, for an illustrative snippet with no model file.
- Files: `internal/plan/plan.go`, `decode.go`, `decode_test.go`, `schema/plan.schema.json`,
  `internal/plan/testdata/`.
- Acceptance: one failing row and one clean twin per addition, with the expected line. The
  failing rows are a wrong type for 1 to 5 and 8, and for 7 an empty level-2 `items` followed by another
  level-2 section. The schema sync test passes.
- Test: `go -C ~/Projects/drafter test ./internal/plan/...`.

### F1.2 Check the new fields (60 min, ordinary)

- Outcome, in `internal/plan/check.go` and `facts.go`:
  1. The `facts` of an introduction, a code item, and a reason item resolve and must be citable under
     `--facts`, like a sentence's `facts`. Without `--facts`, each list gets the no-facts warning.
  2. Id integrity, with or without `--facts`: an id in any `facts` list (sentence, code item, reason
     item, or introduction) that the plan disposes is an error. The fix is to cite a placed fact or to place
     this one.
  3. A section's `anchor`, when present, must equal the GitHub slug of its `heading`, taken with
     the same slugger as the same-page anchor check. A mismatch is an error naming both values.
  4. The reader-state walk warns when a non-optional step `requires` a token that only optional
     steps produce, earlier in page order, and that no precondition supplies.
  5. A `code.source` that is an `http(s)://` URL, or absent, isn't checked.
- Files: `internal/plan/check.go`, `facts.go`, `check_test.go`, `facts_test.go`, fixtures under
  `internal/plan/testdata/repo/`.
- Acceptance: a failing fixture and a clean twin for each of 1 to 5. For 4 the twin has the token
  also produced by a required step, or listed in `preconditions`.
- Test: `go -C ~/Projects/drafter test ./internal/plan/...`.

### F1.3 Repeatable `--outline` (15 min, ordinary)

- Outcome: `check-plan` accepts `--outline` more than once. A target counts as outline-listed when
  any of the outlines lists it. Each outline's load errors still exit 2 and name that outline's
  path.
- Files: `cmd/drafter/checkplan.go`, `internal/plan/outline.go`, their tests, `e2e/`.
- Acceptance: an e2e row with two outlines, where a missing target listed only in the second gives
  the warning, not an error.
- Test: `bash scripts/drafter-gate.sh`.

### F1.4 Fold the sheet into the reference (30 min, ordinary)

- Outcome: `docs/plan-format.md` documents every F1 addition, and every convention in the interim
  sheet (`~/.local/share/drafter/plan-format-v1.md`) that the reference doesn't already state. That
  includes item order, how failures, handoffs, and links are used, restrictive `use`, tokens that
  name states (shared tokens for either-or routes, summary tokens), where facts behind opens,
  steps, and the introduction go, and that a fact may be placed anywhere on the page. It also says
  that a failure renders where its item sits, while `from` only links it to a step for the walk.
  Its example shows a restricting `use` that starts with "only". It also covers what the format leaves out on purpose (tables,
  form, negatives, rework input, exemplars and cross-links) and `friction` as the list a run
  surfaces. Write it fresh in the reference's Google developer style. Cairn's page names in the
  sheet stay out of this public repo, and so does every workstation path.
- Files: `docs/plan-format.md`, `internal/plan/docs_test.go` if a new field name needs coverage.
- Acceptance: the reference test passes with the new fields. `tellgrader --register docs
  docs/plan-format.md` reports no gating finding.
- Test: `bash scripts/drafter-gate.sh`.

### Close (15 min)

`bash scripts/drafter-gate.sh` once on the close head. One whole-branch `diff-reviewer` run, `f1`
against `main`, with go-conventions for `*.go`. `gitleaks git` on the branch history. Then push
`f1` to `glw907/drafter` and open the PR. The body carries what landed, the review verdict, the
score rows pass-core names, and "Found, not done" with a disposition for each item.

If the list is empty and the review accepted, merge with `gh pr merge <n> -R glw907/drafter
--merge`. Then run `git -C ~/Projects/drafter switch main`, `git -C ~/Projects/drafter pull
--ff-only`, and `make -C ~/Projects/drafter install`, and check that `drafter check-plan --help`
exits 0. If the list isn't empty, stop at PR-ready, write the PR number in the final message, and
end. The conductor puts it on Geoff's desk.
