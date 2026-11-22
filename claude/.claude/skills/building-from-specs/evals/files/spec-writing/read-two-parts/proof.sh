#!/usr/bin/env bash
# Exits 0 when the read-two-parts trap is in place in the repo named by $1: one section says no match exits 1, and a done item says exit 0.
set -uo pipefail
cd "$1"
# has FILE TEXT: FILE holds TEXT, with line breaks read as spaces.
has() { tr -s ' \n' ' ' < "$1" | grep -qF -- "$2"; }
has spec.md "No match prints nothing and exits 1" && has spec.md "empty stdout and exit 0"
