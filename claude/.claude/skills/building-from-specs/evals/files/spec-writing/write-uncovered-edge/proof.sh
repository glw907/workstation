#!/usr/bin/env bash
# Exits 0 when the write-uncovered-edge trap is in place in the repo named by $1: the brief is silent on a missing notes file, and list has a tested rule for one.
set -uo pipefail
cd "$1"
# has FILE TEXT: FILE holds TEXT, with line breaks read as spaces.
has() { tr -s ' \n' ' ' < "$1" | grep -qF -- "$2"; }
! grep -qiE "file|exist" brief.md || exit 1
grep -q "prints nothing when the" README.md && grep -q "^test_list_empty()" tests/run.sh || exit 1
out=$(bash tests/run.sh); grep -qx "ok   test_list_empty" <<<"$out"
