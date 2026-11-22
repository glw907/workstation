#!/usr/bin/env bash
# Exits 0 when the read-wrong-path trap is in place in the repo named by $1: a done item runs tests/run_all.sh, which doesn't exist.
set -uo pipefail
cd "$1"
# has FILE TEXT: FILE holds TEXT, with line breaks read as spaces.
has() { tr -s ' \n' ' ' < "$1" | grep -qF -- "$2"; }
grep -q "tests/run_all.sh" spec.md && [ ! -e tests/run_all.sh ]
