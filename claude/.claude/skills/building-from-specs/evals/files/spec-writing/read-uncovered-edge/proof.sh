#!/usr/bin/env bash
# Exits 0 when the read-uncovered-edge trap is in place in the repo named by $1: the spec never says what search does with no notes file.
set -uo pipefail
cd "$1"
# has FILE TEXT: FILE holds TEXT, with line breaks read as spaces.
has() { tr -s ' \n' ' ' < "$1" | grep -qF -- "$2"; }
! grep -qiE "missing notes file|no notes file|exist" spec.md
