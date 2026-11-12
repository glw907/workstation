#!/usr/bin/env bash
# claude-context-budget.test.sh: prove the CLAUDE.md line cap and the rules budget against this worktree's own copy of
# claude-context-budget. The cap binds only a file whose realpath ends /claude/.claude/CLAUDE.md.
set -uo pipefail
cd "$(dirname "$0")/.." || exit 1
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

lines_file "$tree" 121
err=$("$SCRIPT" "$tree" 2>&1 >/dev/null); rc=$?
assert_eq "$rc" "2" "121 lines under claude/.claude: exit"
case "$err" in
  *"121 lines"*"120-line cap"*"claude-md-archive.md"*) ;;
  *) echo "FAIL: 121 lines: message was '$err'"; fail=1 ;;
esac

lines_file "$tree" 120
"$SCRIPT" "$tree" >/dev/null 2>&1; rc=$?
assert_eq "$rc" "0" "120 lines under claude/.claude: exit"

lines_file "$other" 250
"$SCRIPT" "$other" >/dev/null 2>&1; rc=$?
assert_eq "$rc" "0" "250 lines elsewhere, file mode: exit"
jq -nc --arg f "$other" '{tool_input: {file_path: $f}}' | "$SCRIPT" --hook >/dev/null 2>&1; rc=$?
assert_eq "$rc" "0" "250 lines elsewhere, hook mode: exit"

lines_file "$tree" 121
jq -nc --arg f "$tree" '{tool_input: {file_path: $f}}' | "$SCRIPT" --hook >/dev/null 2>&1; rc=$?
assert_eq "$rc" "2" "121 lines under claude/.claude, hook mode: exit"

# A stow-style link reaches the cap through its realpath.
mkdir -p "$root/home/.claude"
ln -s "$tree" "$root/home/.claude/CLAUDE.md"
"$SCRIPT" "$root/home/.claude/CLAUDE.md" >/dev/null 2>&1; rc=$?
assert_eq "$rc" "2" "121 lines through a stow link: exit"

# A rule file under .claude/rules is budgeted: over RULE_BUDGET tokens exits 2, under it exits 0.
rule="$root/claude/.claude/rules/big.md"
mkdir -p "$(dirname "$rule")"
head -c 4400 /dev/zero | tr '\0' 'x' >"$rule"
RULE_BUDGET=1000 "$SCRIPT" "$rule" >/dev/null 2>&1; rc=$?
assert_eq "$rc" "2" "1100-token rule over a 1000 budget: exit"
head -c 3600 /dev/zero | tr '\0' 'x' >"$rule"
RULE_BUDGET=1000 "$SCRIPT" "$rule" >/dev/null 2>&1; rc=$?
assert_eq "$rc" "0" "900-token rule under a 1000 budget: exit"

# --skill-caps: under every cap exits 0; one file over exits 1 naming it; an absent file exits 1.
caps="$root/caps"
for f in SKILL.md references/executor.md references/planner.md references/conductor.md \
  references/round.md references/round-run.md; do
  mkdir -p "$(dirname "$caps/claude/.claude/skills/pass-core/$f")"
  seq 400 >"$caps/claude/.claude/skills/pass-core/$f"
done
"$SCRIPT" --skill-caps --root "$caps" >/dev/null 2>&1; rc=$?
assert_eq "$rc" "0" "skill caps, all under: exit"
seq 1501 >"$caps/claude/.claude/skills/pass-core/SKILL.md"
err=$("$SCRIPT" --skill-caps --root "$caps" 2>&1 >/dev/null); rc=$?
assert_eq "$rc" "1" "skill caps, SKILL.md over: exit"
assert_eq "$err" "pass-core/SKILL.md has 1501 words (cap 1500)" "skill caps, SKILL.md over: message"
seq 400 >"$caps/claude/.claude/skills/pass-core/SKILL.md"
rm "$caps/claude/.claude/skills/pass-core/references/conductor.md"
err=$("$SCRIPT" --skill-caps --root "$caps" 2>&1 >/dev/null); rc=$?
assert_eq "$rc" "1" "skill caps, conductor.md absent: exit"
case "$err" in
  *"references/conductor.md is absent"*) ;;
  *) echo "FAIL: skill caps, absent: message was '$err'"; fail=1 ;;
esac
seq 400 >"$caps/claude/.claude/skills/pass-core/references/conductor.md"

# The two round files are capped at 1500 words each, and an absent one exits 1.
for f in round.md round-run.md; do
  seq 1501 >"$caps/claude/.claude/skills/pass-core/references/$f"
  err=$("$SCRIPT" --skill-caps --root "$caps" 2>&1 >/dev/null); rc=$?
  assert_eq "$rc" "1" "skill caps, $f over: exit"
  assert_eq "$err" "pass-core/references/$f has 1501 words (cap 1500)" "skill caps, $f over: message"
  seq 400 >"$caps/claude/.claude/skills/pass-core/references/$f"
done
rm "$caps/claude/.claude/skills/pass-core/references/round-run.md"
err=$("$SCRIPT" --skill-caps --root "$caps" 2>&1 >/dev/null); rc=$?
assert_eq "$rc" "1" "skill caps, round-run.md absent: exit"
case "$err" in
  *"references/round-run.md is absent"*) ;;
  *) echo "FAIL: skill caps, round-run.md absent: message was '$err'"; fail=1 ;;
esac

# The round rules: each counted list in the real tree holds the number of rules its heading
# promises. The cases pin structure only, so a reworded rule never fails them.

# section_of <file> <heading>: prints the lines between "## <heading>" and the next "## " line.
section_of() {
  awk -v h="## $2" '$0 == h { on = 1; next } on && /^## / { on = 0 } on' "$1"
}

# item_numbers <file> <heading>: prints the numbers of that section's column-0 list items, joined by spaces.
item_numbers() {
  section_of "$1" "$2" | sed -n -E 's/^([0-9]+)\. .*/\1/p' | paste -s -d ' '
}

# count_items <file> <heading>: prints how many column-0 numbered items that section holds.
count_items() {
  section_of "$1" "$2" | grep -c -E '^[0-9]+\. '
}

fixture="$root/rules.md"
printf '%s\n' '# Rules' '' '## First' '' '1. one' '   wrapped' '2. two' '3. three' '' \
  '## Second' '' '1. other' '2. another' >"$fixture"
assert_eq "$(count_items "$fixture" "First")" "3" "count helper: three items under the heading"
assert_eq "$(count_items "$fixture" "Second")" "2" "count helper: a later heading's items are counted apart"
assert_eq "$(item_numbers "$fixture" "First")" "1 2 3" "count helper: item numbers"

refs="claude/.claude/skills/pass-core/references"
assert_eq "$(count_items "$refs/round.md" "Planner rules" 2>/dev/null)" "4" "round.md: planner rules"
assert_eq "$(count_items "$refs/round.md" "Design rules" 2>/dev/null)" "4" "round.md: design rules"
assert_eq "$(item_numbers "$refs/round-run.md" "Standing answers" 2>/dev/null)" \
  "1 2 3 4 5 6 7 8 9 10 11 12" "round-run.md: standing answers, numbered 1 to 12"
tags=$(section_of "$refs/round-run.md" "Miss tags" 2>/dev/null)
for tag in mechanism file-list permission design-gap stale-fact owner-call no-answer conflict estimate ambiguous; do
  case "$tags" in
    *"\`[$tag]\`"*) ;;
    *) echo "FAIL: round-run.md: miss tag [$tag] is absent from its section"; fail=1 ;;
  esac
done

exit "$fail"
