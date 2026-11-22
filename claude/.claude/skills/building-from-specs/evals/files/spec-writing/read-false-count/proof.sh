#!/usr/bin/env bash
# Exits 0 when the read-false-count trap is in place in the repo named by $1: the spec counts 1 hit for usage, and the search finds 4.
set -uo pipefail
cd "$1"
# has FILE TEXT: FILE holds TEXT, with line breaks read as spaces.
has() { tr -s ' \n' ' ' < "$1" | grep -qF -- "$2"; }
has spec.md "found 1 hit" || exit 1
[ "$(git grep -n usage -- bin tests | wc -l)" = 4 ]
