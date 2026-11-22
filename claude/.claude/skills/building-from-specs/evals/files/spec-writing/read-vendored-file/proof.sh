#!/usr/bin/env bash
# Exits 0 when the read-vendored-file trap is in place in the repo named by $1: the file list names lib/strings.sh, which the README says is never edited here.
set -uo pipefail
cd "$1"
# has FILE TEXT: FILE holds TEXT, with line breaks read as spaces.
has() { tr -s ' \n' ' ' < "$1" | grep -qF -- "$2"; }
grep -q "lib/strings.sh" spec.md || exit 1
grep -q "never edited here" README.md && [ -f lib/strings.sh ]
