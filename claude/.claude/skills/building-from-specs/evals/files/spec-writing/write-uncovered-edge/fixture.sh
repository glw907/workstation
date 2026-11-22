#!/usr/bin/env bash
# Builds the write-uncovered-edge repo in the folder named by $1.
set -euo pipefail
here=$(cd "$(dirname "$0")" && pwd)
cd "$1"
source "$here/../lib.sh"
notes_base
cp "$here/brief.md" brief.md
workstation_standins
commit_fixture
