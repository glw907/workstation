#!/usr/bin/env bash
# cairn-docs-cycle.test.sh: prove the launcher refuses any argument but a lone --dry-run. It runs
# this worktree's copy of the script against a nonexistent checkout, so a broken guard exits 1 at
# "no checkout" and starts nothing.
set -uo pipefail
cd "$(dirname "$0")/.."
SCRIPT="$(pwd)/bin/.local/bin/cairn-docs-cycle"
fail=0

assert_eq() {
  [ "$1" = "$2" ] || { echo "FAIL: $3: got '$1', want '$2'"; fail=1; }
}

usage="usage: cairn-docs-cycle [--dry-run]"

for args in "--help" "--dry-run --x" "--x" "--dry-run --dry-run"; do
  # shellcheck disable=SC2086
  err=$(CAIRN_DOCS_CYCLE_REPO=/nonexistent "$SCRIPT" $args 2>&1 >/dev/null)
  rc=$?
  assert_eq "$rc" "2" "exit for '$args'"
  assert_eq "$err" "$usage" "usage line for '$args'"
done

# A lone --dry-run and no argument pass the guard and stop at the missing checkout.
for args in "" "--dry-run"; do
  # shellcheck disable=SC2086
  CAIRN_DOCS_CYCLE_REPO=/nonexistent "$SCRIPT" $args >/dev/null 2>&1
  assert_eq "$?" "1" "exit for '${args:-no argument}'"
done

exit $fail
