#!/usr/bin/env bash
# cairn-run-gate.test.sh: prove the vanish handling (AW-17) and the old-script state directory
# compatibility, against this worktree's own copy of the script, never the live
# ~/.local/bin/cairn-run-gate. Each case isolates TMPDIR to a fresh fixture root and drives the
# script's own key derivation (sha256sum of PWD + gate string) so a case can pre-stage the exact
# state directory the script will read. CAIRN_GATE_POLL_INTERVAL and CAIRN_GATE_GRACE are set
# short throughout, so a dead-pid case resolves in about a second instead of the 5s/15s default.
set -uo pipefail
cd "$(dirname "$0")/.."
REPO_ROOT="$(pwd)"
SCRIPT="$REPO_ROOT/bin/.local/bin/cairn-run-gate"
fail=0

fixture_root="$(mktemp -d)"
work_dir="$(mktemp -d)"
trap 'rm -rf "$fixture_root" "$work_dir"' EXIT

# The gatedir the script computes as "${TMPDIR:-/tmp}/cairn-gate-$(id -u)". Point TMPDIR at the
# fixture root so no case touches a real gate's state.
export TMPDIR="$fixture_root"
gatedir="$TMPDIR/cairn-gate-$(id -u)"

key_for() {
  # Mirror the script's own key: sha256sum of "$PWD\n$gate", first 16 hex chars.
  printf '%s\n%s' "$1" "$2" | sha256sum | cut -c1-16
}

dead_pid() {
  ( exit 0 ) &
  local p=$!
  wait "$p" 2>/dev/null
  echo "$p"
}

assert_contains() {
  local haystack="$1" needle="$2" label="$3"
  if ! grep -qF "$needle" <<<"$haystack"; then
    echo "FAIL: $label: expected output to contain: $needle"
    fail=1
  fi
}

assert_not_contains() {
  local haystack="$1" needle="$2" label="$3"
  if grep -qF "$needle" <<<"$haystack"; then
    echo "FAIL: $label: expected output NOT to contain: $needle"
    fail=1
  fi
}

assert_eq() {
  local got="$1" want="$2" label="$3"
  if [ "$got" != "$want" ]; then
    echo "FAIL: $label: got '$got', want '$want'"
    fail=1
  fi
}

# --- AW-17: a staged state directory with a dead pid and no status file exits 75 with the
# vanish line, and prints no "gate exit:" (that marker is reserved for a terminal result).
gate1="echo case1 $$"
key1=$(key_for "$work_dir" "$gate1")
state1="$gatedir/$key1"
mkdir -p "$state1"
dead_pid > "$state1/pid"
: > "$state1/gate.log"
out=$(cd "$work_dir" && CAIRN_GATE_POLL_INTERVAL=1 CAIRN_GATE_GRACE=1 "$SCRIPT" "$gate1")
rc=$?
assert_eq "$rc" "75" "vanish (first): exit code"
assert_contains "$out" "gate vanished; re-issue starts a fresh run" "vanish (first): vanish line"
assert_not_contains "$out" "gate exit:" "vanish (first): no terminal gate exit line"
assert_eq "$(cat "$state1/vanished" 2>/dev/null)" "1" "vanish (first): counter at 1"
[ ! -e "$state1/pid" ] || { echo "FAIL: vanish (first): pidfile not cleared"; fail=1; }

# --- three consecutive vanishes: the third prints the terminal "gate exit: 1 (vanished 3
# times)" and exits 1. Each call restages a fresh dead pid (a re-issued cairn-run-gate would
# start a real gate run once the first call clears the pidfile; staging models three separate
# stuck runs under the same gate key).
gate2="echo case2 $$"
key2=$(key_for "$work_dir" "$gate2")
state2="$gatedir/$key2"
for i in 1 2 3; do
  mkdir -p "$state2"
  dead_pid > "$state2/pid"
  : > "$state2/gate.log"
  out=$(cd "$work_dir" && CAIRN_GATE_POLL_INTERVAL=1 CAIRN_GATE_GRACE=1 "$SCRIPT" "$gate2")
  rc=$?
  if [ "$i" -lt 3 ]; then
    assert_eq "$rc" "75" "vanish (call $i of 3): exit code"
    assert_contains "$out" "gate vanished; re-issue starts a fresh run" "vanish (call $i of 3): vanish line"
    assert_eq "$(cat "$state2/vanished" 2>/dev/null)" "$i" "vanish (call $i of 3): counter"
  else
    assert_eq "$rc" "1" "vanish (call 3 of 3): exit code"
    assert_contains "$out" "gate exit: 1 (vanished 3 times)" "vanish (call 3 of 3): terminal line"
    [ ! -e "$state2/vanished" ] || { echo "FAIL: vanish (call 3 of 3): counter not reset"; fail=1; }
  fi
done

# --- a gate that itself exits 75 is distinguishable by its own "gate exit:" line: a real
# completed run always prints that marker, whatever the gate's exit status.
gate3="exit 75"
out=$(cd "$work_dir" && CAIRN_GATE_WAIT=5 CAIRN_GATE_POLL_INTERVAL=1 "$SCRIPT" "$gate3")
rc=$?
assert_eq "$rc" "75" "real gate exit 75: wrapper exit code matches the gate's own"
assert_contains "$out" "gate exit: 75" "real gate exit 75: terminal line present"

# --- old-script state directory, live pid: the script waits and reports "still running," never
# treating a live pid as vanished.
gate4="echo case4 $$"
key4=$(key_for "$work_dir" "$gate4")
state4="$gatedir/$key4"
mkdir -p "$state4"
( sleep 30 ) &
live_pid=$!
echo "$live_pid" > "$state4/pid"
: > "$state4/gate.log"
out=$(cd "$work_dir" && CAIRN_GATE_WAIT=2 CAIRN_GATE_POLL_INTERVAL=1 "$SCRIPT" "$gate4")
rc=$?
kill "$live_pid" 2>/dev/null
wait "$live_pid" 2>/dev/null
assert_eq "$rc" "75" "old-format live pid: exit code"
assert_contains "$out" "still running" "old-format live pid: still-running line"
assert_not_contains "$out" "vanished" "old-format live pid: not treated as vanished"

# --- old-script state directory, a finished run (statusfile already present, no vanish
# counter): resolves immediately from the existing status, no new run started.
gate5="echo case5 $$"
key5=$(key_for "$work_dir" "$gate5")
state5="$gatedir/$key5"
mkdir -p "$state5"
echo 999999 > "$state5/pid"
echo 0 > "$state5/status"
echo "finished-run-marker" > "$state5/gate.log"
out=$(cd "$work_dir" && "$SCRIPT" "$gate5")
rc=$?
assert_eq "$rc" "0" "old-format finished run: exit code from the existing status"
assert_contains "$out" "gate exit: 0" "old-format finished run: terminal line"
assert_contains "$out" "finished-run-marker" "old-format finished run: reports the existing log"

# --- no runner prompt or implementer file carries a vanished clause: the protocol lives only in
# cairn-run-gate's own output now.
hits=$(grep -rniI "vanish" \
  "$REPO_ROOT/claude/.claude/agents/cairn-implementer.md" \
  "$REPO_ROOT/claude/.claude/agents/site-implementer.md" \
  "$REPO_ROOT/claude/.claude/workflows/docs-page-chain.js" || true)
[ -z "$hits" ] || { echo "FAIL: a vanished clause remains: $hits"; fail=1; }
chains_hits=$(grep -n "vanish" "$REPO_ROOT/claude/.claude/workflows/pass-execute.js" \
  "$REPO_ROOT/claude/.claude/workflows/pass-execute-chains.js" 2>/dev/null || true)
[ -z "$chains_hits" ] || { echo "FAIL: a vanished clause remains in the runners: $chains_hits"; fail=1; }

# --- neither runner restates the exit-75 protocol (AW-20): both defer to cairn-run-gate's own
# output for whether to re-issue.
restated_hits=$(grep -ni -e "exit 75 means" -e "reattaches and waits again" \
  "$REPO_ROOT/claude/.claude/workflows/pass-execute.js" \
  "$REPO_ROOT/claude/.claude/workflows/pass-execute-chains.js" 2>/dev/null || true)
[ -z "$restated_hits" ] || { echo "FAIL: a restated exit-75 clause remains in the runners: $restated_hits"; fail=1; }

[ "$fail" -eq 0 ] && echo "cairn-run-gate: OK" || echo "cairn-run-gate: FAILED"
exit "$fail"
