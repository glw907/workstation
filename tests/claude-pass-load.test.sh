#!/usr/bin/env bash
# claude-pass-load.test.sh: prove claude-pass-load's limit, its outside-file figures, its
# presence check, and its mark count against a temp tree and a temp HOME. SCRIPT may name
# another copy of the loader to run the cases against.
set -uo pipefail
cd "$(dirname "$0")/.." || exit 1
SCRIPT="${SCRIPT:-$(pwd)/bin/.local/bin/claude-pass-load}"
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

# packet: writes the approval-packet skill with 3 words before its marks, 5 between, and 2 after.
packet() {
  mkdir -p "$root/claude/.claude/skills/approval-packet"
  cat >"$root/claude/.claude/skills/approval-packet/SKILL.md" <<'EOF2'
one two three
<!-- executor-load start -->
four five six
seven eight
<!-- executor-load end -->
nine ten
EOF2
}

build() {
  rm -rf "$root" "$home"
  for f in CLAUDE.md skills/pass-core/SKILL.md skills/pass-core/references/executor.md \
    skills/pass-core/references/planner.md skills/pass-core/references/conductor.md \
    skills/pass-core/references/round.md skills/pass-core/references/round-run.md \
    skills/cairn-pass/SKILL.md; do
    words_file "$root/claude/.claude/$f" 10
  done
  packet
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

# A mark row counts only the words strictly between its two lines: 5 for the executor, while the
# planner counts the whole file (3 + 4 + 5 + 4 + 2 = 18).
out=$(run)
exec_line=$(printf '%s\n' "$out" | sed -n '/^executor$/,/^planner$/p' | grep -F 'approval-packet/SKILL.md')
plan_line=$(printf '%s\n' "$out" | sed -n '/^planner$/,/^conductor$/p' | grep -F 'approval-packet/SKILL.md')
case "$exec_line" in
  *"     5  "*"executor-load marks"*) ;;
  *) echo "FAIL: executor mark row: line was '$exec_line'"; fail=1 ;;
esac
case "$plan_line" in
  *"    18  "*) ;;
  *) echo "FAIL: planner whole-file row: line was '$plan_line'"; fail=1 ;;
esac

# The executor and planner sections each list approval-packet/SKILL.md exactly once.
exec_n=$(printf '%s\n' "$out" | sed -n '/^executor$/,/^planner$/p' | grep -c -F 'approval-packet/SKILL.md')
plan_n=$(printf '%s\n' "$out" | sed -n '/^planner$/,/^conductor$/p' | grep -c -F 'approval-packet/SKILL.md')
assert_eq "$exec_n" "1" "executor approval-packet rows"
assert_eq "$plan_n" "1" "planner approval-packet rows"

# A skill missing its end mark fails --check, naming the mark.
sed -i '/executor-load end/d' "$root/claude/.claude/skills/approval-packet/SKILL.md"
err=$(run --check 2>&1 >/dev/null); rc=$?
assert_eq "$rc" "1" "missing end mark: exit"
case "$err" in
  *"approval-packet/SKILL.md is missing its executor-load start or end line"*) ;;
  *) echo "FAIL: missing end mark: message was '$err'"; fail=1 ;;
esac

# Over the limit: exits 1 with the message.
build
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

# The round files count in the roles that load them: round-run.md for the executor and the
# conductor, round.md for the planner.
build
out=$(run)
assert_eq "$(printf '%s\n' "$out" | grep -c -F 'references/round-run.md')" "2" "round-run.md rows"
assert_eq "$(printf '%s\n' "$out" | grep -c -F 'references/round.md')" "1" "round.md rows"
rm "$root/claude/.claude/skills/pass-core/references/round-run.md"
err=$(run --check 2>&1 >/dev/null); rc=$?
assert_eq "$rc" "1" "absent round-run.md: exit"
case "$err" in
  *"references/round-run.md is absent"*) ;;
  *) echo "FAIL: absent round-run.md: message was '$err'"; fail=1 ;;
esac

[ "$fail" -eq 0 ] && echo "claude-pass-load test OK"
exit "$fail"
