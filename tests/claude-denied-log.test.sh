#!/usr/bin/env bash
# Checks that claude-denied-log writes one private line per denial and survives bad input.
set -u
dir=$(mktemp -d); trap 'rm -rf "$dir"' EXIT
export CLAUDE_DENIED_LOG="$dir/log.jsonl"
hook=bin/.local/bin/claude-denied-log
long=$(printf 'x%.0s' {1..300})
printf '{"session_id":"s1","cwd":"/w","tool_name":"Bash","reason":"[Self-Modification]","tool_input":{"command":"%s"}}' "$long" | "$hook" || { echo "FAIL: nonzero exit"; exit 1; }
printf 'not json' | "$hook" || { echo "FAIL: nonzero on bad input"; exit 1; }
[ "$(wc -l <"$CLAUDE_DENIED_LOG")" = 1 ] || { echo "FAIL: want one line"; exit 1; }
[ "$(jq -r .reason "$CLAUDE_DENIED_LOG")" = "[Self-Modification]" ] || { echo "FAIL: reason"; exit 1; }
[ "$(jq -r '.target | length' "$CLAUDE_DENIED_LOG")" = 200 ] || { echo "FAIL: target not cut to 200"; exit 1; }
[ "$(stat -c %a "$CLAUDE_DENIED_LOG")" = 600 ] || { echo "FAIL: mode"; exit 1; }
echo "claude-denied-log: OK"
