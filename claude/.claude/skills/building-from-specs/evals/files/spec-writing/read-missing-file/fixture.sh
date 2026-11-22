#!/usr/bin/env bash
# Builds the read-missing-file repo in the folder named by $1.
set -euo pipefail
here=$(cd "$(dirname "$0")" && pwd)
cd "$1"
source "$here/../lib.sh"
notes_base
add_completions
cp "$here/spec.md" spec.md
commit_fixture
