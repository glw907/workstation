#!/usr/bin/env bash
# Exits 0 when the read-check-passes-today trap is in place in the repo named by $1: the README done item's check passes with nothing built.
set -uo pipefail
cd "$1"
# has FILE TEXT: FILE holds TEXT, with line breaks read as spaces.
has() { tr -s ' \n' ' ' < "$1" | grep -qF -- "$2"; }
grep -qF '`grep -c notes README.md` prints 1 or more' spec.md || exit 1
[ "$(grep -c notes README.md)" -ge 1 ]
