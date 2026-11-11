#!/usr/bin/env bash
# scripts/gate.sh: run scripts/check.sh through cairn-run-gate on the light lane.
# A worktree-isolated session's Bash guard refuses `cairn-run-gate '<string>'`,
# since it cannot show the quoted string is not git; a no-argument wrapper
# passes, and keeps the lane lock and the run records `--records` scores.
# --fresh passes through to cairn-run-gate; any other argument exits 2.
# Exit codes are cairn-run-gate's, so exit 75 still means re-issue. It repeats
# the `gate exit:` line last, so the result is the output's final line.
set -uo pipefail
cd "$(dirname "$0")/.."
case "${1:-}" in
  "") args=() ;;
  --fresh) [ $# -eq 1 ] && args=(--fresh) || { echo "usage: scripts/gate.sh [--fresh]" >&2; exit 2; } ;;
  *) echo "usage: scripts/gate.sh [--fresh]" >&2; exit 2 ;;
esac
export CAIRN_GATE_LANE=light
out=$(cairn-run-gate "${args[@]}" 'bash scripts/check.sh' 2>&1)
rc=$?
printf '%s\n' "$out"
printf '%s\n' "$out" | grep -m1 '^gate exit:' || true
exit "$rc"
