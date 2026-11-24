---
name: cairn-pass
description: >
  The workstation's facts for building work in cairn-cms: the lane-aware gate wrapper, the fast
  lane, the CI watch, and the repo skill, cairn-build. Use with building-from-specs
  when building, resuming, or reviewing a task in cairn-cms, when a cairn-cms session follows a
  STATUS launch prompt, or when asked how to build the next piece of work there. For a consumer
  site use site-pass.
---

# Cairn pass

Load `building-from-specs` first; it holds the process: a spec Geoff approves, a fresh session per
task under `/goal`, a fresh review, and a pull request. Then read the repo skill `cairn-build` in
the cairn-cms checkout's `.claude/skills/`. It holds what a clone needs: worktree setup, the gate,
the full-suite home, the risk-class path map, the review checklists by path, and the close
checklist. This skill adds only Geoff's workstation.

Cross-repo specs and research live in `~/Projects/initiatives/<id>/`. STATUS's next action names
the spec; trust it. Check `docs/internal/consultations/` for briefs with unrecorded verdicts first
(`engine-consult` carries the protocol).

## Gates

**Gate**: `cairn-run-gate 'npm run lane:fast -- --range <base>..HEAD'` from the task's worktree
root, after each commit. The committed fast lane is the one gate form, and its first line carries no
lane prefix, so the wrapper runs it on the heavy lane. The wrapper outlasts the shell tool's ten-minute
cap and writes the records `task-report` reads. It exits 75 when the run isn't done: re-issue the same
command until a `gate exit:` line prints.

**Worktree setup**: The launch's `.claude/worktrees/<name>`, then the setup command `cairn-build`
names.

## CI

**Full-suite home**: CI on the draft PR. Local `TIER_GATES.full` runs only on `ci-green` exit 3. The
gate runs no gitleaks scan, so there is no branch-history scan to owe.

**CI watch**: `ci-green <sha> --pr <n> --wait` as a background Bash task, re-issued on 75; exit 0
is green, 1 red, 2 missing, 3 unavailable, 4 held for approval: when the held run's triggering
actor is the repo's own `github-actions[bot]`, run the approve command it prints and re-issue the
watch. Any other actor's held run is listed under `## For Geoff`. Run it from the task's worktree
so its CI line lands under the task's branch for `--records`. A red check stops the work until its
cause is fixed.

**Show tier**: `claude-show-merge --ask-only glw907/cairn-cms` prints the globs a Show task may not touch.

**Pull request**: `building-from-specs` "The pull request" says what the body carries and when it
is marked ready.
