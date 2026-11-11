#!/usr/bin/env bash
# claude-clock-stop.test.sh: prove the clock-stop hook (lean pass process spec, Execution item 6)
# against this worktree's own copy of the script. Each case feeds hook input JSON on stdin and
# runs against temporary repos and linked worktrees.
set -uo pipefail
cd "$(dirname "$0")/.."
SCRIPT="$(pwd)/bin/.local/bin/claude-clock-stop"
fail=0
root="$(mktemp -d)"
trap 'rm -rf "$root"' EXIT

assert_eq() {
  [ "$1" = "$2" ] || { echo "FAIL: $3: got '$1', want '$2'"; fail=1; }
}

main="$root/main"
mkdir -p "$main"
git -C "$main" init -q
git -C "$main" -c user.email=t@t -c user.name=t commit -q --allow-empty -m init
git -C "$main" worktree add -q "$root/wt" -b wt
gitdir=$(git -C "$root/wt" rev-parse --absolute-git-dir)
clock="$root/wt/.pass-task-clock"
old_clock="$gitdir/pass-task-clock"

export XDG_STATE_HOME="$root/state"

# run_keep <cwd>: feeds the hook input, prints stdout, leaves the exit code in $rc and the time in $ms.
# run <cwd> does the same from a clean state directory, so each case sees a first stop.
run() { rm -rf "$XDG_STATE_HOME"; run_keep "$1"; }
run_keep() {
  local t0 t1
  t0=$(date +%s%N)
  out=$(jq -nc --arg cwd "$1" '{hook_event_name: "PostToolUse", tool_name: "Bash", cwd: $cwd}' | "$SCRIPT")
  rc=$?
  t1=$(date +%s%N)
  ms=$(( (t1 - t0) / 1000000 ))
}
write_clock() { printf 'task=%s\nstart=%s\nestimate=%s\n' "$1" "$2" "$3" >"$clock"; }
under_a_second() { [ "$ms" -lt 1000 ] || { echo "FAIL: $1: took ${ms}ms"; fail=1; }; }

rm -f "$clock"
run "$root/wt"
assert_eq "$out" "" "no file: silent"; assert_eq "$rc" "0" "no file: exit 0"; under_a_second "no file"

write_clock S9-T1 "$(( $(date +%s) - 90 * 60 ))" 60
run "$root/wt"
assert_eq "$out" "" "under twice the estimate: silent"; assert_eq "$rc" "0" "under: exit 0"; under_a_second "under"

write_clock S9-T1 "$(( $(date +%s) - 130 * 60 ))" 60
run "$root/wt"
assert_eq "$rc" "0" "over twice: exit 0"; under_a_second "over"
assert_eq "$(jq -s 'length' <<<"$out")" "1" "over twice: exactly one JSON object"
assert_eq "$(jq -r '.hookSpecificOutput.hookEventName' <<<"$out")" "PostToolUse" "over twice: event name"
case "$(jq -r '.hookSpecificOutput.additionalContext' <<<"$out")" in
  *S9-T1*"130 minutes"*"60-minute"*) ;;
  *) echo "FAIL: over twice: additionalContext does not name the task and times: $out"; fail=1 ;;
esac

printf 'garbage\n' >"$clock"
run "$root/wt"; assert_eq "$out" "" "malformed file: silent"; assert_eq "$rc" "0" "malformed: exit 0"
printf 'task=T\nstart=abc\nestimate=5\n' >"$clock"
run "$root/wt"; assert_eq "$out" "" "non-numeric start: silent"
printf 'task=T\nstart=1\nestimate=0\n' >"$clock"
run "$root/wt"; assert_eq "$out" "" "zero estimate: silent"

write_clock S9-T1 "$(( $(date +%s) - 130 * 60 ))" 60
mkdir -p "$root/plain"
run "$root/plain"; assert_eq "$out" "" "non-git cwd: silent"; assert_eq "$rc" "0" "non-git: exit 0"
run "$main"; assert_eq "$out" "" "main checkout while the file sits in a linked worktree: silent"
run "$root/wt"; [ -n "$out" ] || { echo "FAIL: the worktree still stops"; fail=1; }
run "$root/does-not-exist"; assert_eq "$out" "" "missing cwd: silent"; assert_eq "$rc" "0" "missing cwd: exit 0"
out=$(printf 'not json' | "$SCRIPT"); assert_eq "$out" "" "bad input: silent"

mkdir -p "$root/wt/sub/dir"
run "$root/wt/sub/dir"; [ -n "$out" ] || { echo "FAIL: a cwd below the worktree root still stops"; fail=1; }

rm -f "$clock"
printf 'task=OLD\nstart=%s\nestimate=60\n' "$(( $(date +%s) - 130 * 60 ))" >"$old_clock"
run "$root/wt"
case "$out" in *OLD*) ;; *) echo "FAIL: the old git-dir home still stops: $out"; fail=1 ;; esac
write_clock NEW "$(date +%s)" 60
run "$root/wt"; assert_eq "$out" "" "the worktree-root file wins over the old home"
rm -f "$old_clock"

# Once per task: a repeat past the threshold is silent, a new start prints again, state stays out of the worktree.
write_clock S9-T2 "$(( $(date +%s) - 130 * 60 ))" 60
rm -rf "$XDG_STATE_HOME"
run_keep "$root/wt"; [ -n "$out" ] || { echo "FAIL: once: first run prints"; fail=1; }
run_keep "$root/wt"; assert_eq "$out" "" "once: second run silent"
write_clock S9-T2 "$(( $(date +%s) - 140 * 60 ))" 60
run_keep "$root/wt"; [ -n "$out" ] || { echo "FAIL: once: a new start prints again"; fail=1; }
[ -d "$XDG_STATE_HOME/claude-clock-stop" ] || { echo "FAIL: once: no record under the state dir"; fail=1; }
assert_eq "$(git -C "$root/wt" status --porcelain)" "" "once: nothing new in the worktree"

# The file must stay out of `git add -A`, or each clock write would change the gate fingerprint.
excludes="$(pwd)/bluefin/git-excludes"
git -C "$root/wt" -c core.excludesFile="$excludes" check-ignore -q .pass-task-clock \
  || { echo "FAIL: bluefin/git-excludes does not ignore .pass-task-clock"; fail=1; }
assert_eq "$(git config --file git/.gitconfig core.excludesFile)" "~/.dotfiles/bluefin/git-excludes" \
  "the tracked gitconfig names the excludes file"

[ "$fail" -eq 0 ] && echo "claude-clock-stop: OK" || echo "claude-clock-stop: FAILED"
exit "$fail"
