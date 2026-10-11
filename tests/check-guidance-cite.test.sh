#!/usr/bin/env bash
# check-guidance-cite.test.sh: prove scripts/check-guidance-cite.sh against this worktree's own
# copy, using temporary repos whose `main` branch stands in as the base.
set -uo pipefail
cd "$(dirname "$0")/.."
SCRIPT="$(pwd)/scripts/check-guidance-cite.sh"
fail=0
root="$(mktemp -d)"
trap 'rm -rf "$root"' EXIT

assert_eq() {
  [ "$1" = "$2" ] || { echo "FAIL: $3: got '$1', want '$2'"; fail=1; }
}

TRAILER='Co-Authored-By: Claude <noreply@anthropic.com>'

# repo <name> <path> <message>: a repo with an empty main commit and a branch `b` that adds <path>
# in a commit with <message>. The script is copied in so its cd lands in the temp repo.
repo() {
  local d="$root/$1"
  mkdir -p "$d/scripts"
  cp "$SCRIPT" "$d/scripts/"
  git -C "$d" init -q -b main
  git -C "$d" -c user.email=t@t -c user.name=t commit -q --allow-empty -m init
  git -C "$d" checkout -q -b b
  mkdir -p "$d/$(dirname "$2")"
  echo x >"$d/$2"
  git -C "$d" add "$2"
  git -C "$d" -c user.email=t@t -c user.name=t commit -q -m "$3"
}
# run <name> [base]: leaves stdout in $out and the exit code in $rc.
run() { out=$(bash "$root/$1/scripts/check-guidance-cite.sh" "${2:-main}"); rc=$?; }
warns() { case "$out" in WARNING:*) return 0 ;; *) return 1 ;; esac; }

SK=claude/.claude/skills/x/SKILL.md

repo nourl "$SK" "T1: Add x"
run nourl; assert_eq "$rc" 0 "no URL: exit"; warns || { echo "FAIL: no URL: no warning"; fail=1; }
case "$out" in *"$SK"*) ;; *) echo "FAIL: warning does not name the path: $out"; fail=1 ;; esac

repo cited "$SK" "$(printf 'T1: Add x\n\nhttps://code.claude.com/docs/en/skills')"
run cited; assert_eq "$out" "" "code.claude.com URL: silent"; assert_eq "$rc" 0 "cited: exit"

repo settings claude/.claude/settings.json "$(printf 'T3: Hook\n\nhttps://platform.claude.com/docs/x')"
run settings; assert_eq "$out" "" "platform.claude.com URL: silent"

repo claudemd claude/.claude/CLAUDE.md "$(printf 'T2: Rule\n\nhttps://www.anthropic.com/engineering/x')"
run claudemd; assert_eq "$out" "" "anthropic.com URL: silent"

repo agents claude/.claude/agents/a.md "T2: Agent"
run agents; warns || { echo "FAIL: agents path: no warning"; fail=1; }

repo other "$SK" "$(printf 'T1: Add x\n\nhttps://example.com/claude.com')"
run other; warns || { echo "FAIL: other host: no warning"; fail=1; }
assert_eq "$rc" 0 "other host: exit"

repo lookalike "$SK" "$(printf 'T1: Add x\n\nhttps://anthropic.com.evil.com/x')"
run lookalike; warns || { echo "FAIL: lookalike host: no warning"; fail=1; }

repo docs docs/note.md "T5: Note"
run docs; assert_eq "$out" "" "docs only: silent"; assert_eq "$rc" 0 "docs only: exit"

repo trailer "$SK" "$(printf 'T1: Add x\n\n%s' "$TRAILER")"
run trailer; warns || { echo "FAIL: trailer only: no warning"; fail=1; }
assert_eq "$rc" 0 "trailer only: exit"

run nourl nosuchbase
assert_eq "$rc" 0 "missing base: exit"
case "$out" in *skipped*) ;; *) echo "FAIL: missing base: no skip line: $out"; fail=1 ;; esac

git -C "$root/nourl" checkout -q --orphan unrelated
git -C "$root/nourl" -c user.email=t@t -c user.name=t commit -q --allow-empty -m orphan
git -C "$root/nourl" checkout -q b
run nourl unrelated
assert_eq "$rc" 0 "orphan base: exit"
case "$out" in *skipped*) ;; *) echo "FAIL: orphan base: no skip line: $out"; fail=1 ;; esac

[ "$fail" -eq 0 ] && echo "ok"
exit "$fail"
