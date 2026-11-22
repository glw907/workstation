#!/usr/bin/env bash
# Exits 0 when the write-gate-red trap is in place in the repo named by $1: the gate fails today, and the one failure is test_export_csv.
set -uo pipefail
cd "$1"
# has FILE TEXT: FILE holds TEXT, with line breaks read as spaces.
has() { tr -s ' \n' ' ' < "$1" | grep -qF -- "$2"; }
out=$(bash scripts/gate.sh) && exit 1
[ "$(grep -c "^FAIL" <<<"$out")" = 1 ] && grep -qx "FAIL test_export_csv" <<<"$out"
