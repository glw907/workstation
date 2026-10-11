#!/usr/bin/env bash
# claude-context-budget.test.sh: prove the CLAUDE.md line cap against this worktree's own copy of
# claude-context-budget. The cap binds only a file whose realpath ends /claude/.claude/CLAUDE.md.
set -uo pipefail
cd "$(dirname "$0")/.."
SCRIPT="$(pwd)/bin/.local/bin/claude-context-budget"
fail=0
root="$(mktemp -d)"
trap 'rm -rf "$root"' EXIT

assert_eq() {
  [ "$1" = "$2" ] || { echo "FAIL: $3: got '$1', want '$2'"; fail=1; }
}

# lines_file <path> <n>: writes an n-line file, creating its directory.
lines_file() {
  mkdir -p "$(dirname "$1")"
  seq "$2" | sed 's/^/line /' >"$1"
}

tree="$root/claude/.claude/CLAUDE.md"
other="$root/other/CLAUDE.md"

lines_file "$tree" 201
err=$("$SCRIPT" "$tree" 2>&1 >/dev/null); rc=$?
assert_eq "$rc" "2" "201 lines under claude/.claude: exit"
case "$err" in
  *"201 lines"*"200-line cap"*"claude-md-archive.md"*) ;;
  *) echo "FAIL: 201 lines: message was '$err'"; fail=1 ;;
esac

lines_file "$tree" 200
"$SCRIPT" "$tree" >/dev/null 2>&1; rc=$?
assert_eq "$rc" "0" "200 lines under claude/.claude: exit"

lines_file "$other" 250
"$SCRIPT" "$other" >/dev/null 2>&1; rc=$?
assert_eq "$rc" "0" "250 lines elsewhere, file mode: exit"
jq -nc --arg f "$other" '{tool_input: {file_path: $f}}' | "$SCRIPT" --hook >/dev/null 2>&1; rc=$?
assert_eq "$rc" "0" "250 lines elsewhere, hook mode: exit"

lines_file "$tree" 201
jq -nc --arg f "$tree" '{tool_input: {file_path: $f}}' | "$SCRIPT" --hook >/dev/null 2>&1; rc=$?
assert_eq "$rc" "2" "201 lines under claude/.claude, hook mode: exit"

# A stow-style link reaches the cap through its realpath.
mkdir -p "$root/home/.claude"
ln -s "$tree" "$root/home/.claude/CLAUDE.md"
"$SCRIPT" "$root/home/.claude/CLAUDE.md" >/dev/null 2>&1; rc=$?
assert_eq "$rc" "2" "201 lines through a stow link: exit"

exit "$fail"
