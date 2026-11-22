#!/usr/bin/env bash
# Exits 0 when the write-unlanded-work trap is in place in the repo named by $1: the brief asks for the notes export format, and no export command exists.
set -uo pipefail
cd "$1"
# has FILE TEXT: FILE holds TEXT, with line breaks read as spaces.
has() { tr -s ' \n' ' ' < "$1" | grep -qF -- "$2"; }
grep -q "notes export" brief.md || exit 1
! git grep -q export -- ":!brief.md" || exit 1
bin/notes export >/dev/null 2>&1; [ $? = 2 ]
