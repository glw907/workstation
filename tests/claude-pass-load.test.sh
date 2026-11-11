#!/usr/bin/env bash
# claude-pass-load.test.sh: prove claude-pass-load's limit, its outside-file figures, its
# presence check, and its fence-aware heading count against a temp tree and a temp HOME.
set -uo pipefail
cd "$(dirname "$0")/.." || exit 1
SCRIPT="$(pwd)/bin/.local/bin/claude-pass-load"
fail=0
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
root="$tmp/tree"
home="$tmp/home"

assert_eq() {
  [ "$1" = "$2" ] || { echo "FAIL: $3: got '$1', want '$2'"; fail=1; }
}

# words_file <path> <n>: writes a file holding n words, creating its directory.
words_file() {
  mkdir -p "$(dirname "$1")"
  seq "$2" | sed 's/^/w/' >"$1"
}

register() {
  mkdir -p "$root/claude/.claude/docs/voice"
  cat >"$root/claude/.claude/docs/voice/approval-brief.md" <<'EOF'
# Register
## The four rules
one two
## The brief contract
three four
## Exemplars
### The brief skeleton
five six
```markdown
# inside a fence
## also inside
seven eight
```
nine
### A PR with nothing to decide (PR #40)
ten
## Off-voice contrast
eleven
EOF
}

build() {
  rm -rf "$root" "$home"
  for f in CLAUDE.md skills/pass-core/SKILL.md skills/pass-core/references/executor.md \
    skills/pass-core/references/planner.md skills/pass-core/references/conductor.md \
    skills/cairn-pass/SKILL.md skills/approval-packet/SKILL.md; do
    words_file "$root/claude/.claude/$f" 10
  done
  register
  for f in cairn-cms/CLAUDE.md cairn-cms/.claude/skills/cairn-running-passes/SKILL.md \
    standards/plugins/standards/skills/running-passes/SKILL.md \
    standards/plugins/standards/skills/brainstorming/SKILL.md \
    standards/plugins/standards/skills/backlog-sweep/SKILL.md \
    standards/plugins/standards/skills/spec-plan-review/SKILL.md; do
    words_file "$home/Projects/$f" 10
  done
}

run() { HOME="$home" "$SCRIPT" "$@" --root "$root"; }

# Under the limit: exits 0.
build
run --check >/dev/null 2>&1; rc=$?
assert_eq "$rc" "0" "under the limit: exit"

# A "#" line inside a fence does not end the skeleton's section: 4 heading words, 2, the fence
# (1 + 4 + 3 + 2 + 1 words), and "nine" make 18.
out=$(run)
line=$(printf '%s\n' "$out" | grep -m1 'The brief skeleton')
case "$line" in
  *" 18  "*) ;;
  *) echo "FAIL: fenced heading: line was '$line'"; fail=1 ;;
esac

# Over the limit: exits 1 with the message.
words_file "$root/claude/.claude/CLAUDE.md" 9500
err=$(run --check 2>&1 >/dev/null); rc=$?
assert_eq "$rc" "1" "over the limit: exit"
case "$err" in
  *"claude-pass-load: executor loads "*" words (limit 9000)"*) ;;
  *) echo "FAIL: over the limit: message was '$err'"; fail=1 ;;
esac

# An absent outside file counts at its recorded figure.
build
rm "$home/Projects/cairn-cms/CLAUDE.md"
out=$(run 2>&1)
case "$out" in
  *"1091  ~/Projects/cairn-cms/CLAUDE.md (not found, counted at 1091)"*) ;;
  *) echo "FAIL: absent outside file: output was '$out'"; fail=1 ;;
esac
run --check >/dev/null 2>&1; rc=$?
assert_eq "$rc" "0" "absent outside file under --check: exit"

# An absent inside file exits 1 under --check, naming it.
build
rm "$root/claude/.claude/skills/pass-core/references/executor.md"
err=$(run --check 2>&1 >/dev/null); rc=$?
assert_eq "$rc" "1" "absent inside file: exit"
case "$err" in
  *"references/executor.md is absent"*) ;;
  *) echo "FAIL: absent inside file: message was '$err'"; fail=1 ;;
esac
run >/dev/null 2>&1; rc=$?
assert_eq "$rc" "0" "absent inside file without --check: exit"

[ "$fail" -eq 0 ] && echo "claude-pass-load test OK"
exit "$fail"
