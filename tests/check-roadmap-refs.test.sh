#!/usr/bin/env bash
# check-roadmap-refs.test.sh: prove scripts/check-roadmap-refs.sh fails on a planted ROADMAP
# reference, passes on a clean tree, and passes on the real repo.
set -uo pipefail
cd "$(dirname "$0")/.."
CHECK="$(pwd)/scripts/check-roadmap-refs.sh"
fail=0
root="$(mktemp -d)"
trap 'rm -rf "$root"' EXIT

mkdir -p "$root/bad/claude/.claude/skills/x" "$root/good/claude/.claude/skills/x"
printf 'File a ROADMAP line for it.\n' > "$root/bad/claude/.claude/skills/x/SKILL.md"
printf 'See cairn-cms ROADMAP.md for the engine.\nFile it in BACKLOG.md.\n' > "$root/good/claude/.claude/skills/x/SKILL.md"

bash "$CHECK" "$root/bad" >/dev/null 2>&1 && { echo "FAIL: planted ROADMAP reference passed"; fail=1; }
bash "$CHECK" "$root/good" >/dev/null 2>&1 || { echo "FAIL: clean fixture failed"; fail=1; }
bash "$CHECK" >/dev/null 2>&1 || { echo "FAIL: real repo has a non-cairn ROADMAP reference"; fail=1; }
exit "$fail"
