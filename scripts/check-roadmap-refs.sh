#!/usr/bin/env bash
# check-roadmap-refs.sh [root]: fail when a skill or bin script names ROADMAP outside cairn-cms's own.
# A hit passes when its line names cairn-cms or matches an allowlist entry (path:fragment).
set -uo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
root="${1:-$here/..}"
allow="$here/roadmap-refs-allow.txt"
fail=0
dirs=()
for d in claude/.claude/skills .claude/skills bin; do
  [ -d "$root/$d" ] && dirs+=("$root/$d")
done
[ ${#dirs[@]} -gt 0 ] || exit 0
while IFS= read -r hit; do
  file="${hit%%:*}"
  rel="${file#"$root"/}"
  text="${hit#*:*:}"
  case "$text" in *cairn-cms*) continue ;; esac
  ok=0
  if [ -f "$allow" ]; then
    while IFS= read -r entry; do
      [ -n "$entry" ] || continue
      if [ "${entry%%:*}" = "$rel" ] && [[ "$text" == *"${entry#*:}"* ]]; then ok=1; break; fi
    done < "$allow"
  fi
  [ "$ok" = 1 ] && continue
  echo "$rel: $text"
  fail=1
done < <(grep -rn ROADMAP "${dirs[@]}" 2>/dev/null)
[ "$fail" = 0 ] || { echo "non-cairn ROADMAP reference found" >&2; exit 1; }
