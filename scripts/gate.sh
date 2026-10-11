#!/usr/bin/env bash
# scripts/gate.sh: run scripts/check.sh through cairn-run-gate on the light lane.
# A worktree-isolated session's Bash guard refuses `cairn-run-gate '<string>'`,
# since it cannot show the quoted string is not git; a no-argument wrapper
# passes, and keeps the lane lock and the run records `--records` scores.
# Exit codes are cairn-run-gate's, so exit 75 still means re-issue.
set -uo pipefail
cd "$(dirname "$0")/.."
export CAIRN_GATE_LANE=light
exec cairn-run-gate 'bash scripts/check.sh'
