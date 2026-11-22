#!/usr/bin/env bash
# Exits 0 when the write-missing-file trap is in place in the repo named by $1: the gate passes, and a usage line that names search fails test_completions_match.
set -uo pipefail
cd "$1"
# has FILE TEXT: FILE holds TEXT, with line breaks read as spaces.
has() { tr -s ' \n' ' ' < "$1" | grep -qF -- "$2"; }
bash scripts/gate.sh >/dev/null || exit 1
w=$(mktemp -d); cp -a . "$w"; cd "$w"
sed -i 's/| notes list"/| notes list | notes search <word>"/' bin/notes
out=$(bash tests/run.sh); grep -qx "FAIL test_completions_match" <<<"$out"
