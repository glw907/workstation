#!/usr/bin/env bash
# check-drift-initiatives.test.sh: prove check-drift's initiatives leg against temporary repos.
# Each case runs `check-drift --initiatives-only` with INITIATIVES_DIR on a fixture and expects
# its line and exit 0, because a missing, stale, or unreachable clone never fails the run.
set -uo pipefail
cd "$(dirname "$0")/.."
SCRIPT="$(pwd)/bin/.local/bin/check-drift"
fail=0
root="$(mktemp -d)"
trap 'rm -rf "$root"' EXIT

assert_has() {
  case "$1" in *"$2"*) ;; *) echo "FAIL: $3: output lacks '$2': $1"; fail=1 ;; esac
}
assert_eq() {
  [ "$1" = "$2" ] || { echo "FAIL: $3: got '$1', want '$2'"; fail=1; }
}

# run <dir>: leaves stdout in $out and the exit code in $rc.
run() {
  out=$(INITIATIVES_DIR="$1" INITIATIVES_TIMEOUT=5 "$SCRIPT" --initiatives-only 2>&1)
  rc=$?
}
commit() { git -C "$1" -c user.email=t@t -c user.name=t commit -q --allow-empty -m "$2"; }

origin="$root/origin"
git init -q "$origin"
commit "$origin" one

run "$root/absent"
assert_eq "$rc" "0" "missing clone: exit 0"
assert_has "$out" "no clone at" "missing clone"

git clone -q "$origin" "$root/clone"
run "$root/clone"
assert_eq "$rc" "0" "current clone: exit 0"
assert_has "$out" "clone is current" "current clone"

commit "$origin" two
run "$root/clone"
assert_eq "$rc" "0" "behind clone: exit 0"
assert_has "$out" "clone is behind" "behind clone"

git -C "$root/clone" remote set-url origin "file://$root/does-not-exist"
run "$root/clone"
assert_eq "$rc" "0" "unreachable remote: exit 0"
assert_has "$out" "remote unreachable" "unreachable remote"

exit "$fail"
