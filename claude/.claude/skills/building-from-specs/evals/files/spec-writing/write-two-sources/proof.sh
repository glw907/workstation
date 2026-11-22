#!/usr/bin/env bash
# Exits 0 when the write-two-sources trap is in place in the repo named by $1: the brief's no-match exit of 1 breaks the README's rule that a command that runs exits 0.
set -uo pipefail
cd "$1"
# has FILE TEXT: FILE holds TEXT, with line breaks read as spaces.
has() { tr -s ' \n' ' ' < "$1" | grep -qF -- "$2"; }
grep -q "No match prints nothing and exits 1" brief.md || exit 1
grep -q "Every command exits 0 when it runs, even when it prints nothing" README.md
