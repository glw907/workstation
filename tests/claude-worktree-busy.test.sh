#!/usr/bin/env bash
# claude-worktree-busy.test.sh: prove each check of claude-worktree-busy against a temp git repo and a stub claude.
set -uo pipefail
cd "$(dirname "$0")/.." || exit 1
SCRIPT="$(pwd)/bin/.local/bin/claude-worktree-busy"
fail=0
root="$(realpath "$(mktemp -d)")"
sleeper=
trap '[ -z "$sleeper" ] || kill "$sleeper" 2>/dev/null; rm -rf "$root"' EXIT

assert_eq() {
  [ "$1" = "$2" ] || { echo "FAIL: $3: got '$1', want '$2'"; fail=1; }
}

repo="$root/refinement-3"
mkdir -p "$repo" "$root/bin"
git -C "$repo" init -q
git -C "$repo" -c user.name=t -c user.email=t@t commit -q --allow-empty -m init

# Stub claude: one row shaped like a real `claude agents --json` row, ids and paths replaced. STUB_CWD sets its
# cwd, STUB_STATE its state (default working), and STUB_NOSTATE prints the interactive shape: no state, no id.
cat >"$root/bin/claude" <<'STUB'
#!/usr/bin/env bash
if [ -n "${STUB_NOSTATE:-}" ]; then
cat <<JSON
[
  {"pid": 4243, "cwd": "${STUB_CWD:-/nowhere}", "kind": "interactive", "status": "idle"}
]
JSON
else
cat <<JSON
[
  {"pid": 4242, "id": "aaaa1111", "cwd": "${STUB_CWD:-/nowhere}", "kind": "background", "startedAt": 1794000000000,
   "sessionId": "aaaa1111-0000-0000-0000-000000000000", "name": "fake-session", "status": "idle", "state": "${STUB_STATE:-working}"}
]
JSON
fi
STUB
chmod +x "$root/bin/claude"
export PATH="$root/bin:$PATH"

# check <want rc> <label> <path> [message prefix]: free cases must also print nothing, busy cases must name the check.
check() {
  out=$("$SCRIPT" "$3" 2>/dev/null); rc=$?
  assert_eq "$rc" "$1" "$2: exit"
  [ "$1" != 0 ] || assert_eq "$out" "" "$2: output"
  [ -z "${4:-}" ] || assert_eq "${out:0:${#4}}" "$4" "$2: message"
}

# wait_cmd <pid> <prefix> <label>: a fixture's command line is the test's own until its exec lands.
wait_cmd() {
  local c
  for _ in $(seq 40); do
    c=$({ tr '\0' ' ' <"/proc/$1/cmdline"; } 2>/dev/null)
    case "$c" in "$2"*) return 0 ;; esac
    sleep 0.05
  done
  echo "FAIL: $3: process $1 never showed '$2'"; fail=1
}

# stop_fixture: end the fixture process the last case started.
stop_fixture() { kill "$sleeper" 2>/dev/null; wait "$sleeper" 2>/dev/null; sleeper=; }

aq="$root/approval-queue"
mkdir -p "$aq/approval-queue"
git -C "$aq" init -q
printf 'sleep 6; true\n' >"$aq/approval-queue/build"
cp "$aq/approval-queue/build" "$aq/approval-queue/build.old"
git -C "$aq" add approval-queue/build approval-queue/build.old
git -C "$aq" -c user.name=t -c user.email=t@t commit -q -m init
printf 'sleep 6; true\n' >"$root/daemon"

check 0 "free" "$repo"

bash -c 'sleep 30; true' "$repo" &
sleeper=$!
wait_cmd "$sleeper" "bash -c sleep 30" "process holds path"
check 1 "process holds path" "$repo" "busy: process"
stop_fixture

bash -c 'sleep 30; true' "${repo}0" &
sleeper=$!
wait_cmd "$sleeper" "bash -c sleep 30" "process holds only a prefix of the path"
check 0 "process holds only a prefix of the path" "$repo"
stop_fixture

bash -c 'sleep 30; true' "/elsewhere$repo" &
sleeper=$!
wait_cmd "$sleeper" "bash -c sleep 30" "process holds a longer path that ends in the path"
check 0 "process holds a longer path that ends in the path" "$repo"
stop_fixture

(cd "$root" && exec -a "$root/bin/claude" bash daemon run --origin transient --spawned-by "{\"label\":\"claude\",\"cwd\":\"$repo\",\"pid\":1}") &
sleeper=$!
wait_cmd "$sleeper" "$root/bin/claude daemon run" "daemon process holds path"
check 0 "daemon process holds path" "$repo"
kill -0 "$sleeper" 2>/dev/null || { echo "FAIL: daemon process holds path: fixture ended early"; fail=1; }
stop_fixture

(cd "$root" && exec -a node bash "$aq/approval-queue/build") &
sleeper=$!
wait_cmd "$sleeper" "node $aq/approval-queue/build" "queue server holds path"
check 0 "queue server holds path" "$aq"
STUB_CWD="$aq" STUB_STATE="done" check 0 "queue server and a finished row" "$aq"
kill -0 "$sleeper" 2>/dev/null || { echo "FAIL: queue server cases: fixture ended early"; fail=1; }
stop_fixture

(cd "$root" && exec -a node bash -c 'sleep 6; true' "$repo/other.js") &
sleeper=$!
wait_cmd "$sleeper" "node -c sleep" "other node process holds path"
check 1 "other node process holds path" "$repo" "busy: process"
stop_fixture

(cd "$root" && exec -a node bash "$aq/approval-queue/build.old") &
sleeper=$!
wait_cmd "$sleeper" "node $aq/approval-queue/build.old" "node process with a longer file name"
check 1 "node process with a longer file name" "$aq" "busy: process"
stop_fixture

(cd "$root" && exec -a claude bash daemon status "$repo") &
sleeper=$!
wait_cmd "$sleeper" "claude daemon status" "claude process that is not daemon run"
check 1 "claude process that is not daemon run" "$repo" "busy: process"
stop_fixture

ln -s "$root" "$root/link"
STUB_CWD="$root/link/refinement-3" check 1 "session cwd reaches the path through a symlink" "$repo" "busy: claude session"
STUB_CWD="$repo/sub" check 1 "session cwd under path" "$repo" "busy: claude session"
STUB_CWD="${repo}0" check 0 "session cwd shares only a prefix" "$repo"
STUB_CWD="$repo" STUB_STATE="done" check 0 "finished session row" "$repo"
STUB_CWD="$repo" STUB_STATE=stopped check 0 "stopped session row" "$repo"
STUB_CWD="$repo" STUB_STATE=failed check 0 "failed session row" "$repo"
STUB_CWD="$repo" STUB_NOSTATE=1 check 1 "session row with no state" "$repo" "busy: claude session"

echo x >"$repo/new.txt"
check 1 "fresh uncommitted file" "$repo" "busy: uncommitted file"
touch -d '2 hours ago' "$repo/new.txt"
check 0 "uncommitted file aged past 60 minutes" "$repo"

mkdir "$root/plain"
check 0 "plain directory outside git" "$root/plain"

[ "$fail" = 0 ] && echo "OK: claude-worktree-busy"
exit "$fail"
