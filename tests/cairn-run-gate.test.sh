#!/usr/bin/env bash
# cairn-run-gate.test.sh: prove the vanish handling (AW-17), the old-script state directory
# compatibility, and the receipts (2026-10-08), against this worktree's own copy of the script, never the live
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
# Receipts go to the fixture root too, never the real ~/.local/state store.
export CAIRN_GATE_RECEIPT_DIR="$fixture_root/receipts"
# A caller that exports a lane would change every fingerprint and the lane cases below.
unset CAIRN_GATE_LANE
gatedir="$TMPDIR/cairn-gate-$(id -u)"
# Run records go to the fixture root too, never ~/.local/state; a case that reads them points the
# variable at a directory of its own.
export CAIRN_GATE_RECORDS_DIR="$fixture_root/records"

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

# --- receipts: a finished run writes a receipt that --receipt finds for the exact gate string on
# the same tree; an untracked file, another lane, or another gate string misses; a failing run's
# receipt records its exit code and never counts as a pass; a tree changed mid-run gets none.
rrepo="$work_dir/receipt-repo"
mkdir -p "$rrepo"
git -C "$rrepo" init -q
echo a >"$rrepo/a.txt"
git -C "$rrepo" add a.txt
git -C "$rrepo" -c user.email=t@t -c user.name=t commit -qm init
out=$(cd "$rrepo" && CAIRN_GATE_LANE=light CAIRN_GATE_POLL_INTERVAL=1 "$SCRIPT" 'true')
assert_contains "$out" "gate exit: 0" "receipt: the run itself is unchanged"
out=$(cd "$rrepo" && CAIRN_GATE_LANE=light "$SCRIPT" --receipt 'true')
rc=$?
assert_eq "$rc" "0" "receipt: lookup on the same tree exits 0"
assert_contains "$out" "receipt: exit 0 (log: " "receipt: lookup prints the record"
out=$(cd "$rrepo" && "$SCRIPT" --receipt 'true')
assert_eq "$?" "1" "receipt: another lane misses"
out=$(cd "$rrepo" && CAIRN_GATE_LANE=light "$SCRIPT" --receipt 'true ')
assert_eq "$?" "1" "receipt: another gate string misses"
touch "$rrepo/untracked.txt"
out=$(cd "$rrepo" && CAIRN_GATE_LANE=light "$SCRIPT" --receipt 'true')
assert_eq "$?" "1" "receipt: an untracked file misses"
assert_contains "$out" "receipt: none" "receipt: miss line"
rm -f "$rrepo/untracked.txt"
out=$(cd "$rrepo" && CAIRN_GATE_LANE=light CAIRN_GATE_POLL_INTERVAL=1 "$SCRIPT" 'false')
assert_eq "$?" "1" "receipt: a failing run keeps its exit code"
out=$(cd "$rrepo" && CAIRN_GATE_LANE=light "$SCRIPT" --receipt 'false')
assert_eq "$?" "1" "receipt: a failing receipt never counts as a pass"
assert_contains "$out" "exited 1" "receipt: the miss names the recorded exit"
out=$(cd "$rrepo" && CAIRN_GATE_LANE=light CAIRN_GATE_POLL_INTERVAL=1 "$SCRIPT" 'sleep 1; echo x >>a.txt')
out=$(cd "$rrepo" && CAIRN_GATE_LANE=light "$SCRIPT" --receipt 'sleep 1; echo x >>a.txt')
assert_eq "$?" "1" "receipt: a tree changed during the run gets no receipt"
git -C "$rrepo" checkout -q a.txt

# --- receipts survive a commit: a gate passed on a dirty tree matches after that exact content is
# committed, and one changed byte misses.
echo dirty >>"$rrepo/a.txt"
echo new >"$rrepo/b.txt"
out=$(cd "$rrepo" && CAIRN_GATE_LANE=light CAIRN_GATE_POLL_INTERVAL=1 "$SCRIPT" 'true')
git -C "$rrepo" add a.txt b.txt
git -C "$rrepo" -c user.email=t@t -c user.name=t commit -qm dirty
out=$(cd "$rrepo" && CAIRN_GATE_LANE=light "$SCRIPT" --receipt 'true')
assert_eq "$?" "0" "receipt: committing the gated content keeps the match"
echo x >>"$rrepo/b.txt"
out=$(cd "$rrepo" && CAIRN_GATE_LANE=light "$SCRIPT" --receipt 'true')
assert_eq "$?" "1" "receipt: one changed byte misses"
git -C "$rrepo" checkout -q b.txt

# --- a start fingerprint left by another run (an old-script launch finished by this one) never
# yields a receipt: it is keyed by the pid that wrote it.
gate6="true # case6"
key6=$(key_for "$rrepo" "$gate6")
state6="$gatedir/$key6"
mkdir -p "$state6"
echo 999999 >"$state6/pid"
echo 0 >"$state6/status"
: >"$state6/gate.log"
printf '%s %s\n' 12345 "$(cd "$rrepo" && CAIRN_GATE_LANE=light bash -c 'source <(sed -n "/^gate_tree()/,/^}/p;/^gate_fingerprint()/,/^}/p" "$1"); gate="$2"; gate_fingerprint' _ "$SCRIPT" "$gate6")" >"$state6/fingerprint"
out=$(cd "$rrepo" && CAIRN_GATE_LANE=light "$SCRIPT" "$gate6")
out=$(cd "$rrepo" && CAIRN_GATE_LANE=light "$SCRIPT" --receipt "$gate6")
assert_eq "$?" "1" "receipt: a stale start fingerprint from another run writes none"
out=$(cd "$rrepo" && CAIRN_GATE_LANE=light "$SCRIPT" --receipt 'sleep 1; echo x >>a.txt')
assert_eq "$?" "1" "receipt: nor does the reverted start tree match it"

# --- run records: one gate line per run, written by the detached run, so an abandoned caller still
# leaves one and a reattaching caller adds none.
rec_lines() { [ -f "$1/runs.jsonl" ] && wc -l <"$1/runs.jsonl" || echo 0; }
wait_for_lines() {
  local dir="$1" want="$2" i
  for i in $(seq 1 100); do
    [ "$(rec_lines "$dir")" -ge "$want" ] && return 0
    sleep 0.1
  done
  return 1
}

rec1="$fixture_root/rec-reattach"
gate7="sleep 3; echo rec7"
out=$(cd "$rrepo" && CAIRN_GATE_RECORDS_DIR="$rec1" CAIRN_GATE_LANE=light CAIRN_GATE_WAIT=1 CAIRN_GATE_POLL_INTERVAL=1 "$SCRIPT" "$gate7")
assert_eq "$?" "75" "records: the first call of a slow gate exits 75"
wait_for_lines "$rec1" 1 || { echo "FAIL: records: an abandoned caller left no record"; fail=1; }
for i in 1 2 3 4 5 6; do
  out=$(cd "$rrepo" && CAIRN_GATE_RECORDS_DIR="$rec1" CAIRN_GATE_LANE=light CAIRN_GATE_WAIT=2 CAIRN_GATE_POLL_INTERVAL=1 "$SCRIPT" "$gate7")
  [ "$?" -ne 75 ] && break
done
assert_contains "$out" "gate exit: 0" "records: the reattached call completes"
assert_eq "$(rec_lines "$rec1")" "1" "records: a re-issued gate leaves exactly one line"
assert_eq "$(jq -r '.kind + " " + .outcome + " " + (.exit|tostring) + " " + .gate' "$rec1/runs.jsonl")" "gate exit 0 $gate7" "records: the gate line names kind, outcome, exit, gate"
assert_eq "$(jq -r '.lane + " " + .toplevel' "$rec1/runs.jsonl")" "light $rrepo" "records: lane and toplevel"
assert_eq "$(jq -r '[.head, .tree, .branch, .start, .end] | map(length > 0) | all' "$rec1/runs.jsonl")" "true" "records: head, tree, branch, start, end present"

rec2="$fixture_root/rec-vanish"
gate8="echo case8 $$"
key8=$(key_for "$work_dir" "$gate8")
mkdir -p "$gatedir/$key8"
dead_pid >"$gatedir/$key8/pid"
: >"$gatedir/$key8/gate.log"
out=$(cd "$work_dir" && CAIRN_GATE_RECORDS_DIR="$rec2" CAIRN_GATE_POLL_INTERVAL=1 CAIRN_GATE_GRACE=1 "$SCRIPT" "$gate8")
assert_eq "$?" "75" "records: a vanished run still exits 75"
assert_eq "$(rec_lines "$rec2")" "1" "records: a vanished run leaves one line"
assert_eq "$(jq -r '.kind + " " + .outcome' "$rec2/runs.jsonl")" "gate vanished" "records: the line is outcome vanished"

rec3="$fixture_root/rec-receipt"
out=$(cd "$rrepo" && CAIRN_GATE_RECORDS_DIR="$rec3" CAIRN_GATE_LANE=light CAIRN_GATE_POLL_INTERVAL=1 "$SCRIPT" 'echo rec9')
out=$(cd "$rrepo" && CAIRN_GATE_RECORDS_DIR="$rec3" CAIRN_GATE_LANE=light "$SCRIPT" --receipt 'echo rec9')
assert_eq "$?" "0" "records: the receipt lookup still hits"
assert_eq "$(rec_lines "$rec3")" "2" "records: a run and a receipt hit leave two lines"
assert_eq "$(jq -r '.outcome' "$rec3/runs.jsonl" | paste -sd, -)" "exit,receipt" "records: the second line is outcome receipt"

# A second run queued behind a held machine lock records the wait.
rec4="$fixture_root/rec-wait"
mkdir -p "$gatedir"
flock "$gatedir/machine-light.lock" sleep 3 &
holder=$!
sleep 0.5
out=$(cd "$rrepo" && CAIRN_GATE_RECORDS_DIR="$rec4" CAIRN_GATE_LANE=light CAIRN_GATE_POLL_INTERVAL=1 "$SCRIPT" 'echo rec10')
wait "$holder" 2>/dev/null
assert_eq "$(jq -r '.lockWaitSeconds > 0' "$rec4/runs.jsonl")" "true" "records: a run queued behind a held lock records a wait above zero"
rec5="$fixture_root/rec-nowait"
out=$(cd "$rrepo" && CAIRN_GATE_RECORDS_DIR="$rec5" CAIRN_GATE_LANE=light CAIRN_GATE_POLL_INTERVAL=1 "$SCRIPT" 'echo rec11')
# Stamps are whole seconds, so an unqueued run can straddle one second boundary.
assert_eq "$(jq -r '.lockWaitSeconds <= 1' "$rec5/runs.jsonl")" "true" "records: an unqueued run records no real wait"

# The summary sums only the matching lines and counts the malformed one.
rec6="$fixture_root/rec-summary"
mkdir -p "$rec6"
{
  jq -nc '{kind:"gate",gate:"g",toplevel:"/t",branch:"b",start:"2026-10-10T10:00:00Z",end:"2026-10-10T10:10:00Z",lockWaitSeconds:60,exit:0,outcome:"exit"}'
  jq -nc '{kind:"gate",gate:"g",toplevel:"/t",branch:"b",start:"2026-10-10T11:00:00Z",end:"2026-10-10T11:05:00Z",lockWaitSeconds:0,exit:1,outcome:"exit"}'
  jq -nc '{kind:"ci",sha:"s",pr:1,task:null,toplevel:"/t",branch:"b",start:"2026-10-10T12:00:00Z",end:"2026-10-10T12:20:00Z",queueSeconds:30,outcome:"green",retried:[]}'
  jq -nc '{kind:"gate",gate:"g",toplevel:"/t",branch:"other",start:"2026-10-10T10:00:00Z",end:"2026-10-10T20:00:00Z",lockWaitSeconds:999,exit:0,outcome:"exit"}'
  jq -nc '{kind:"ci",sha:"s",pr:1,task:null,toplevel:"/other",branch:"b",start:"2026-10-10T12:00:00Z",end:"2026-10-10T18:00:00Z",queueSeconds:1,outcome:"green",retried:[]}'
  echo '{"kind":"gate","broken'
} >"$rec6/runs.jsonl"
out=$(CAIRN_GATE_RECORDS_DIR="$rec6" "$SCRIPT" --records /t b)
assert_eq "$?" "0" "records: the summary exits 0"
assert_eq "$out" "gate 840s (2 runs), lock wait 60s, ci wait 1200s (1 waits), malformed 1" "records: the summary sums only the matching lines"
out=$(CAIRN_GATE_RECORDS_DIR="$fixture_root/rec-absent" "$SCRIPT" --records /t b)
assert_eq "$?" "0" "records: an absent file exits 0"
assert_eq "$out" "gate 0s (0 runs), lock wait 0s, ci wait 0s (0 waits), malformed 0" "records: an absent file prints zero sums"

# A record failure never changes the gate's printed exit or its receipt, and warns once.
count_warn() { grep -c "cairn-run-gate: record" <<<"$1"; }
rrepo2="$work_dir/record-fail-repo"
mkdir -p "$rrepo2"
git -C "$rrepo2" init -q
echo a >"$rrepo2/a.txt"
git -C "$rrepo2" add a.txt
git -C "$rrepo2" -c user.email=t@t -c user.name=t commit -qm init
good=$(cd "$rrepo2" && CAIRN_GATE_RECORDS_DIR="$fixture_root/rec-ok" CAIRN_GATE_LANE=light CAIRN_GATE_POLL_INTERVAL=1 "$SCRIPT" 'echo rec12' 2>&1)
good_rc=$?
good_exit=$(grep -o '^gate exit: [0-9]*' <<<"$good")
assert_eq "$(count_warn "$good")" "0" "records: no warning with records on"
(cd "$rrepo2" && CAIRN_GATE_LANE=light "$SCRIPT" --receipt 'echo rec12' >/dev/null)
assert_eq "$?" "0" "records: the receipt exists with records on"

echo file >"$fixture_root/afile"
bad=$(cd "$rrepo2" && CAIRN_GATE_RECORDS_DIR="$fixture_root/afile/sub" CAIRN_GATE_LANE=light CAIRN_GATE_POLL_INTERVAL=1 "$SCRIPT" 'echo rec13' 2>&1)
assert_eq "$?" "$good_rc" "records: an unwritable directory leaves the exit unchanged"
assert_eq "$(grep -o '^gate exit: [0-9]*' <<<"$bad")" "$good_exit" "records: an unwritable directory leaves the printed exit unchanged"
assert_eq "$(count_warn "$bad")" "1" "records: an unwritable directory warns once"
(cd "$rrepo2" && CAIRN_GATE_LANE=light "$SCRIPT" --receipt 'echo rec13' >/dev/null)
assert_eq "$?" "0" "records: an unwritable directory leaves the receipt"

# A PATH holding the tools the script needs and no jq (jq lives under Homebrew in the live
# environment, which a detached run need not inherit).
nojq_bin="$fixture_root/nojq-bin"
mkdir -p "$nojq_bin"
for tool in bash env git sha256sum cut sed grep date cat mkdir rm mv cp sleep flock tail wc find mktemp \
  realpath id kill tr head sort dirname touch ln; do
  ln -sf "$(command -v "$tool")" "$nojq_bin/$tool"
done
safe_path="$nojq_bin"
if PATH="$safe_path" command -v jq >/dev/null; then
  echo "FAIL: records: jq is on the stripped PATH, the case proves nothing"; fail=1
fi
nojq=$(cd "$rrepo2" && PATH="$safe_path" CAIRN_GATE_RECORDS_DIR="$fixture_root/rec-nojq" CAIRN_GATE_LANE=light CAIRN_GATE_POLL_INTERVAL=1 "$SCRIPT" 'echo rec14' 2>&1)
assert_eq "$?" "$good_rc" "records: jq off PATH leaves the exit unchanged"
assert_eq "$(grep -o '^gate exit: [0-9]*' <<<"$nojq")" "$good_exit" "records: jq off PATH leaves the printed exit unchanged"
assert_eq "$(count_warn "$nojq")" "1" "records: jq off PATH warns once"
(cd "$rrepo2" && CAIRN_GATE_LANE=light "$SCRIPT" --receipt 'echo rec14' >/dev/null)
assert_eq "$?" "0" "records: jq off PATH leaves the receipt"
assert_eq "$(rec_lines "$fixture_root/rec-nojq")" "0" "records: jq off PATH writes no line"

# A lock that stays held past the wait is a warning, not a failure.
rec7="$fixture_root/rec-locked"
mkdir -p "$rec7"
flock "$rec7/runs.lock" sleep 4 &
holder=$!
sleep 0.3
locked=$(cd "$rrepo2" && CAIRN_GATE_RECORDS_DIR="$rec7" CAIRN_GATE_RECORDS_LOCK_WAIT=1 CAIRN_GATE_LANE=light CAIRN_GATE_POLL_INTERVAL=1 "$SCRIPT" 'echo rec15' 2>&1)
assert_eq "$?" "$good_rc" "records: a lock timeout leaves the exit unchanged"
assert_eq "$(count_warn "$locked")" "1" "records: a lock timeout warns once"
wait "$holder" 2>/dev/null

# --- lean cutover (spec Execution item 7): a finished result persists for repeat calls and
# concurrent waiters while the tree matches, a changed tree or --fresh reruns, the deadline holds
# under a slow poll, an unknown flag exits 2, and RUN_GATE_IF_BUSY=defer leaves a busy heavy leg.
lrepo="$work_dir/lean-repo"
mkdir -p "$lrepo"
git -C "$lrepo" init -q
echo a >"$lrepo/a.txt"
git -C "$lrepo" add a.txt
git -C "$lrepo" -c user.email=t@t -c user.name=t commit -qm init
recL="$fixture_root/rec-lean"
lean() { (cd "$lrepo" && CAIRN_GATE_RECORDS_DIR="$recL" CAIRN_GATE_LANE=light CAIRN_GATE_POLL_INTERVAL=1 "$SCRIPT" "$@"); }

# Two concurrent waiters both print the result; the run happens once.
gateL1="sleep 2; echo lean1"
lean "$gateL1" >"$fixture_root/waiter1.out" 2>&1 &
w1=$!
sleep 1
lean "$gateL1" >"$fixture_root/waiter2.out" 2>&1 &
w2=$!
wait "$w1" "$w2"
assert_contains "$(cat "$fixture_root/waiter1.out")" "gate exit: 0" "persist: the first waiter prints gate exit"
assert_contains "$(cat "$fixture_root/waiter2.out")" "gate exit: 0" "persist: the second waiter prints gate exit"
assert_not_contains "$(cat "$fixture_root/waiter2.out")" "vanished" "persist: no false vanish"
assert_eq "$(rec_lines "$recL")" "1" "persist: two waiters leave one run record"

# A repeat call on an unchanged tree reprints without a new run.
out=$(lean "$gateL1")
assert_eq "$?" "0" "persist: a repeat call exits with the stored status"
assert_contains "$out" "gate exit: 0" "persist: a repeat call reprints gate exit"
assert_not_contains "$out" "gate started" "persist: a repeat call starts no run"
assert_eq "$(rec_lines "$recL")" "1" "persist: a repeat call adds no exit line"

# A changed tree starts a new run.
echo b >>"$lrepo/a.txt"
out=$(lean "$gateL1")
assert_contains "$out" "gate started" "persist: a changed tree starts a new run"
wait_for_lines "$recL" 2 || { echo "FAIL: persist: the changed-tree run left no record"; fail=1; }
assert_eq "$(rec_lines "$recL")" "2" "persist: a changed tree adds one run"

# --fresh reruns the same tree.
out=$(lean --fresh "$gateL1")
assert_contains "$out" "gate started" "fresh: --fresh starts a new run on the same tree"
assert_contains "$out" "gate exit: 0" "fresh: the rerun finishes"
assert_eq "$(rec_lines "$recL")" "3" "fresh: --fresh adds one run"
git -C "$lrepo" checkout -q a.txt

# A poll that sleeps twice its argument still returns inside the wait budget plus one interval.
shim="$fixture_root/slow-sleep-bin"
mkdir -p "$shim"
real_sleep="$(command -v sleep)"
printf '#!/usr/bin/env bash\nexec %s "$(awk -v n="$1" "BEGIN{print n*2}")"\n' "$real_sleep" >"$shim/sleep"
chmod +x "$shim/sleep"
gateL2="$real_sleep 12; echo lean2"
t0=$(date +%s)
(cd "$lrepo" && PATH="$shim:$PATH" CAIRN_GATE_RECORDS_DIR="$recL" CAIRN_GATE_LANE=light CAIRN_GATE_WAIT=4 CAIRN_GATE_POLL_INTERVAL=1 "$SCRIPT" "$gateL2") >"$fixture_root/slow.out" 2>&1
rc=$?
t1=$(date +%s)
out=$(cat "$fixture_root/slow.out")
assert_eq "$rc" "75" "deadline: the slow-poll call exits 75"
[ $((t1 - t0)) -le 6 ] || { echo "FAIL: deadline: slow-poll call took $((t1 - t0))s, want 6s or less"; fail=1; }
assert_contains "$out" "timeout: 600000" "exit 75 text names the Bash timeout"
for i in 1 2 3 4 5 6; do
  out=$(lean "$gateL2")
  [ "$?" -ne 75 ] && break
done
assert_contains "$out" "gate exit: 0" "deadline: the run finishes after the slow-poll call"

# An unknown flag exits 2 and starts nothing.
before=$(ls "$gatedir" | wc -l)
out=$(lean --bogus 'echo bogus' 2>&1)
assert_eq "$?" "2" "flags: an unknown flag exits 2"
assert_contains "$out" "usage: cairn-run-gate" "flags: the usage line prints"
assert_eq "$(ls "$gatedir" | wc -l)" "$before" "flags: an unknown flag creates no state"
assert_eq "$(rec_lines "$recL")" "4" "flags: an unknown flag starts no run"

# RUN_GATE_IF_BUSY=defer: a busy heavy lock exits 76 and starts nothing.
recD="$fixture_root/rec-defer"
heavy() { (cd "$lrepo" && CAIRN_GATE_RECORDS_DIR="$recD" CAIRN_GATE_POLL_INTERVAL=1 "$@"); }
flock "$gatedir/machine.lock" "$real_sleep" 4 &
holder=$!
sleep 0.5
out=$(heavy env RUN_GATE_IF_BUSY=defer "$SCRIPT" 'echo defer1' 2>&1)
assert_eq "$?" "76" "defer: a busy heavy lock exits 76"
assert_contains "$out" "push's CI" "defer: the line leaves the leg to CI"
assert_not_contains "$out" "gate started" "defer: nothing starts"
assert_eq "$(rec_lines "$recD")" "0" "defer: nothing is recorded"
# The light lane ignores the variable.
out=$(heavy env RUN_GATE_IF_BUSY=defer CAIRN_GATE_LANE=light "$SCRIPT" 'echo defer2' 2>&1)
assert_eq "$?" "0" "defer: the light lane ignores the variable"
wait "$holder" 2>/dev/null
# A call that reattaches to its own in-flight heavy run never defers.
gateL3="$real_sleep 7; echo lean3"
# (Output goes to a file: the detached run holds a command substitution's pipe open until it ends.)
heavy env CAIRN_GATE_WAIT=1 "$SCRIPT" "$gateL3" >"$fixture_root/own1.out" 2>&1
assert_eq "$?" "75" "defer: the own run starts and is still running"
heavy env RUN_GATE_IF_BUSY=defer CAIRN_GATE_WAIT=1 "$SCRIPT" "$gateL3" >"$fixture_root/own2.out" 2>&1
assert_eq "$?" "75" "defer: a re-issue reattaches to its own run and never exits 76"
for i in 1 2 3 4 5 6; do
  out=$(heavy env RUN_GATE_IF_BUSY=defer CAIRN_GATE_WAIT=8 "$SCRIPT" "$gateL3" 2>&1)
  [ "$?" -ne 75 ] && break
done
assert_contains "$out" "gate exit: 0" "defer: the own run finishes"

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
