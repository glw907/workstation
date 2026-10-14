#!/usr/bin/env bash
# claude-memory-write-check.test.sh: prove the memory-write hook fires on a memory file, stays
# silent elsewhere, and no longer routes initiative state to ROADMAP.
set -uo pipefail
cd "$(dirname "$0")/.."
SCRIPT="$(pwd)/bin/.local/bin/claude-memory-write-check"
fail=0

assert() { [ "$1" = "$2" ] || { echo "FAIL: $3: got '$1', want '$2'"; fail=1; }; }

mem_out=$(jq -nc --arg p "$HOME/.claude/projects/x/memory/note.md" '{tool_input: {file_path: $p}}' | "$SCRIPT")
msg=$(jq -r '.hookSpecificOutput.additionalContext' <<<"$mem_out")
case "$msg" in *"Memory write check"*) ;; *) echo "FAIL: no message on a memory file"; fail=1 ;; esac
case "$msg" in *ROADMAP*) echo "FAIL: message names ROADMAP"; fail=1 ;; esac
case "$msg" in *"initiative record"*) ;; *) echo "FAIL: message omits the initiative record"; fail=1 ;; esac

other=$(jq -nc '{tool_input: {file_path: "/tmp/other.md"}}' | "$SCRIPT")
assert "$other" "" "silent outside memory"
index=$(jq -nc --arg p "$HOME/.claude/projects/x/memory/MEMORY.md" '{tool_input: {file_path: $p}}' | "$SCRIPT")
assert "$index" "" "silent on MEMORY.md"
exit "$fail"
