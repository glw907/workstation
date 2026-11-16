#!/usr/bin/env bash
# desk.test.sh: prove each branch of the desk launcher against a temp HOME and a stub claude.
set -uo pipefail
cd "$(dirname "$0")/.." || exit 1
SCRIPT="$(pwd)/bin/.local/bin/desk"
fail=0
root="$(realpath "$(mktemp -d)")"
trap 'rm -rf "$root"' EXIT

assert_eq() {
  [ "$1" = "$2" ] || { echo "FAIL: $3: got '$1', want '$2'"; fail=1; }
}

mkdir -p "$root/bin" "$root/home/Projects" "$root/home/.claude/projects/p" "$root/home/.claude/jobs"
log="$root/calls.log"

# Stub claude: `agents --json` prints $STUB_ROWS, `--bg` prints the backgrounded line and writes state.json
# (unless STUB_NOSTATE), and every call is logged with its arguments and cwd.
cat >"$root/bin/claude" <<'STUB'
#!/usr/bin/env bash
echo "claude $* | cwd=$PWD" >>"$STUB_LOG"
case "$1" in
  agents) printf '%s\n' "${STUB_ROWS:-[]}" ;;
  --bg)
    echo "backgrounded · cafe0001 · desk"
    if [ -z "${STUB_NOSTATE:-}" ]; then
      mkdir -p "$HOME/.claude/jobs/cafe0001"
      printf '{"needs": %s}\n' "${STUB_NEEDS:-null}" >"$HOME/.claude/jobs/cafe0001/state.json"
    fi ;;
esac
exit 0
STUB
chmod +x "$root/bin/claude"

midnight="$(date -d 'today 00:00' +%s)"
today=$(( (midnight + 3600) * 1000 ))
yesterday=$(( (midnight - 3600) * 1000 ))

row() { # id kind startedAt sessionId
  printf '{"pid":1,"id":"%s","kind":"%s","startedAt":%s,"sessionId":"%s","name":"desk","status":"idle","state":"done"}' "$1" "$2" "$3" "$4"
}

# run <rows> [env...]: run the launcher with no TTY, output in $out, status in $rc.
run_desk() {
  local rows="$1"; shift
  : >"$log"
  out="$(env HOME="$root/home" PATH="$root/bin:$PATH" STUB_LOG="$log" STUB_ROWS="$rows" DESK_STATE_WAIT=1 "$@" bash "$SCRIPT" 2>&1)"
  rc=$?
}
calls() { grep -c "$1" "$log" || true; }

# 1. No row: one launch from ~/Projects.
run_desk '[]'
assert_eq "$out" "desk cafe0001" "1 prints the new id"
assert_eq "$(calls ' --bg ')" 1 "1 one launch"
grep -q "cwd=$root/home/Projects" "$log" || { echo "FAIL: 1 launch cwd"; fail=1; }
grep -q -- '--model fable --effort high --name desk' "$log" || { echo "FAIL: 1 launch flags"; fail=1; }

# 2. A background row from today: no launch, its id printed.
run_desk "[$(row aaaa1111 background "$today" s1)]"
assert_eq "$out" "desk aaaa1111" "2 prints the row id"
assert_eq "$(calls ' --bg ')" 0 "2 no launch"

# 3. Two rows: the newer id.
run_desk "[$(row aaaa1111 background "$today" s1),$(row bbbb2222 background $((today + 5000)) s2)]"
assert_eq "$out" "desk bbbb2222" "3 newer id"

# 4. An interactive row: the message, no launch.
run_desk "[$(row aaaa1111 interactive "$today" s1)]"
assert_eq "$out" "desk is open in another terminal (session s1)" "4 message"
assert_eq "$(calls ' --bg ')" 0 "4 no launch"

# 5. Yesterday's row ending in end_turn: a stop, then a launch.
printf '%s\n' '{"type":"user","message":{"content":"hi"}}' \
  '{"type":"assistant","message":{"stop_reason":"end_turn"}}' '{"type":"system"}' >"$root/home/.claude/projects/p/s5.jsonl"
run_desk "[$(row dddd5555 background "$yesterday" s5)]"
assert_eq "$(calls 'stop dddd5555')" 1 "5 stop"
assert_eq "$(calls ' --bg ')" 1 "5 launch"
assert_eq "$out" "desk cafe0001" "5 new id"

# 6. Yesterday's row ending mid-turn: no stop, its id printed.
printf '%s\n' '{"type":"user","message":{"content":"hi"}}' \
  '{"type":"assistant","message":{"stop_reason":"tool_use"}}' >"$root/home/.claude/projects/p/s6.jsonl"
run_desk "[$(row eeee6666 background "$yesterday" s6)]"
assert_eq "$(calls 'stop ')" 0 "6 no stop"
assert_eq "$out" "desk eeee6666" "6 prints the row id"

# 7. A launch whose state.json holds the needs value: a stop, exit 1.
rm -rf "$root/home/.claude/jobs/cafe0001"
run_desk '[]' STUB_NEEDS='"send a prompt to start"'
assert_eq "$rc" 1 "7 exit status"
assert_eq "$(calls 'stop cafe0001')" 1 "7 stop"

# 8. A launch whose state.json never appears: exit 0, id printed after the wait.
rm -rf "$root/home/.claude/jobs/cafe0001"
run_desk '[]' STUB_NOSTATE=1
assert_eq "$rc" 0 "8 exit status"
assert_eq "$out" "desk cafe0001" "8 prints the id"

# 9. The TTY branch: attach is logged.
rm -rf "$root/home/.claude/jobs/cafe0001"
: >"$log"
env HOME="$root/home" PATH="$root/bin:$PATH" STUB_LOG="$log" STUB_ROWS="[$(row aaaa1111 background "$today" s1)]" \
  script -qec "bash $SCRIPT" /dev/null >/dev/null 2>&1
assert_eq "$(calls 'attach aaaa1111')" 1 "9 attach"

[ "$fail" = 0 ] && echo "desk: all cases passed"
exit "$fail"
