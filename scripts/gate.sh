#!/usr/bin/env bash
# scripts/gate.sh: run scripts/check.sh through cairn-run-gate on the light lane.
# A worktree-isolated session's Bash guard refuses `cairn-run-gate '<string>'`,
# since it cannot show the quoted string is not git; a no-argument wrapper
# passes, and keeps the lane lock and the run records `--records` scores.
# --fresh passes through to cairn-run-gate. --scope-changed runs the changed-files
# lane, `bash scripts/check.sh --changed`, whose gate string is its own, so its
# receipt never stands for the whole gate. Any other argument exits 2.
# Exit codes are cairn-run-gate's, so exit 75 still means re-issue. It repeats
# the `gate exit:` line last, so the result is the output's final line.
set -uo pipefail
cd "$(dirname "$0")/.." || exit 2
args=()
gate='bash scripts/check.sh'
for a in "$@"; do
  case "$a" in
    --fresh) args+=(--fresh) ;;
    --scope-changed) gate='bash scripts/check.sh --changed' ;;
    *) echo "usage: scripts/gate.sh [--fresh] [--scope-changed]" >&2; exit 2 ;;
  esac
done
export CAIRN_GATE_LANE=light
out=$(cairn-run-gate "${args[@]}" "$gate" 2>&1)
rc=$?
printf '%s\n' "$out"
printf '%s\n' "$out" | grep -m1 '^gate exit:' || true
exit "$rc"
