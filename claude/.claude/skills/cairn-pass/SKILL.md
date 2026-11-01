---
name: cairn-pass
description: >
  The workstation's overlay on the cairn-cms pass process: the lane-aware gate wrapper, the CI watch,
  and Geoff's launch conventions. Use when planning, executing, resuming, or closing a cairn-cms
  pass, or when a fresh cairn-cms session follows a STATUS launch prompt. For a consumer site's
  pass use site-pass.
---

# Cairn pass

Load `pass-core` first, then the repo's own `cairn-running-passes` skill (in the cairn-cms
checkout's `.claude/skills/`). The repo skill holds what a clone needs: worktree setup, the fast
lane, the full-suite home, the risk-class path map, the review checklists by path, and the close
checklist. This skill adds only Geoff's operation. Cross-repo specs, plans, and research live in
`~/Projects/initiatives/<id>/`. STATUS's next action names the plan; trust it. Check
`docs/internal/consultations/` for briefs with unrecorded verdicts first (`engine-consult` carries
the protocol).

**Gate**: `cairn-run-gate '<string>'` from the pass worktree, per `pass-core` "Gates". It wraps the
committed fast lane with the shared lanes.

**Fast lane**: `node scripts/checks/gate-tier.mjs --fast --range <base>..HEAD` prints the legs.
Run them in order, each through `cairn-run-gate` with a leading `CAIRN_GATE_LANE=<lane>` lifted onto
the call (`CAIRN_GATE_LANE=light cairn-run-gate '<rest>'`), since the tool reads the lane from its
own environment. The `tool` class gate is `make -C tool check` on the light lane; a Node-only
workspace suite such as `npm test -w packages/create-cairn-site` is light, and the engine's root
`npm test` drives Chromium and is never light.

**Full-suite home**: CI on the draft PR. Local `TIER_GATES.full` runs only on `ci-green` exit 3. The
gate runs no gitleaks scan, so there is no branch-history scan to owe.

**CI watch**: `ci-green <sha> --pr <n> --wait` as a background Bash task, re-issued on 75; exit 0
is green, 1 red, 2 missing, 3 unavailable, 4 held for approval: when the held run's triggering
actor is the repo's own `github-actions[bot]`, run the approve command it prints and re-issue the
watch; any other actor's held run stops the line for Geoff. Run it from the pass worktree so its CI
line lands under the pass branch for `--records`. No task waits for CI before the next; a red stops
the line.

**Packet**: an `auth-data` or `runner` pass sends its packet through `approval-packet`; an
`ordinary` pass merges its own PR per `pass-core` "Close".
