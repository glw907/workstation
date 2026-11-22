---
name: cairn-pass
description: >
  The workstation's facts for building work in cairn-cms: the lane-aware gate wrapper, the fast
  lane, the CI watch, and where the repo's own process skill lives. Use with building-from-specs
  when building, resuming, or reviewing a task in cairn-cms, when a cairn-cms session follows a
  STATUS launch prompt, or when asked how to build the next piece of work there. For a consumer
  site use site-pass.
---

# Cairn pass

Load `building-from-specs` first; it holds the process: a spec Geoff approves, a fresh session per
task under `/goal`, a fresh review, and a pull request. Then read the repo's own process skill in
the cairn-cms checkout's `.claude/skills/`. That skill holds what a clone needs: worktree setup, the
fast lane, the full-suite home, the risk-class path map, the review checklists by path, and the
close checklist. This skill adds only Geoff's workstation.

Cross-repo specs and research live in `~/Projects/initiatives/<id>/`. STATUS's next action names
the spec; trust it. Check `docs/internal/consultations/` for briefs with unrecorded verdicts first
(`engine-consult` carries the protocol).

## Gates

**Gate**: `cairn-run-gate '<string>'` from the task's worktree. It wraps the committed fast lane
with the shared lanes.

**Fast lane**: `node scripts/checks/gate-tier.mjs --fast --range <base>..HEAD` prints the legs.
Run them in order, each through `cairn-run-gate` with a leading `CAIRN_GATE_LANE=<lane>` lifted onto
the call (`CAIRN_GATE_LANE=light cairn-run-gate '<rest>'`), since the tool reads the lane from its
own environment. The `tool` class gate is `make -C tool check` on the light lane; a Node-only
workspace suite such as `npm test -w packages/create-cairn-site` is light, and the engine's root
`npm test` drives Chromium and is never light.

**Worktree setup**: The launch's `.claude/worktrees/<name>`, then the setup command the repo's
process skill names.

## CI

**Full-suite home**: CI on the draft PR. Local `TIER_GATES.full` runs only on `ci-green` exit 3. The
gate runs no gitleaks scan, so there is no branch-history scan to owe.

**CI watch**: `ci-green <sha> --pr <n> --wait` as a background Bash task, re-issued on 75; exit 0
is green, 1 red, 2 missing, 3 unavailable, 4 held for approval: when the held run's triggering
actor is the repo's own `github-actions[bot]`, run the approve command it prints and re-issue the
watch. Any other actor's held run is listed under `## For Geoff`. Run it from the task's worktree
so its CI line lands under the task's branch for `--records`. A red check stops the work until its
cause is fixed.

**Pull request**: `building-from-specs` "The pull request" says what the body carries and when it
is marked ready.
