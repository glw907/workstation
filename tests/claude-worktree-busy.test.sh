#!/usr/bin/env bash
# claude-worktree-busy.test.sh: prove each check of claude-worktree-busy against a temp git repo and a stub claude.
set -uo pipefail
cd "$(dirname "$0")/.."
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

# Stub claude: one row shaped like a real `claude agents --json` row, ids and paths replaced; STUB_CWD sets its cwd.
cat >"$root/bin/claude" <<'STUB'
#!/usr/bin/env bash
cat <<JSON
[
  {"pid": 4242, "id": "aaaa1111", "cwd": "${STUB_CWD:-/nowhere}", "kind": "background", "startedAt": 1794000000000,
   "sessionId": "aaaa1111-0000-0000-0000-000000000000", "name": "fake-session", "status": "idle", "state": "done"}
]
JSON
STUB
chmod +x "$root/bin/claude"
export PATH="$root/bin:$PATH"

# check <want rc> <label> <path>: free cases must also print nothing.
check() {
  out=$("$SCRIPT" "$3" 2>/dev/null); rc=$?
  assert_eq "$rc" "$1" "$2: exit"
  [ "$1" != 0 ] || assert_eq "$out" "" "$2: output"
}

check 0 "free" "$repo"

bash -c 'sleep 30; true' "$repo" &
sleeper=$!
check 1 "process holds path" "$repo"
kill "$sleeper"; wait "$sleeper" 2>/dev/null; sleeper=

bash -c 'sleep 30; true' "${repo}0" &
sleeper=$!
check 0 "process holds only a prefix of the path" "$repo"
kill "$sleeper"; wait "$sleeper" 2>/dev/null; sleeper=

bash -c 'sleep 30; true' "/elsewhere$repo" &
sleeper=$!
check 0 "process holds a longer path that ends in the path" "$repo"
kill "$sleeper"; wait "$sleeper" 2>/dev/null; sleeper=

ln -s "$root" "$root/link"
STUB_CWD="$root/link/refinement-3" check 1 "session cwd reaches the path through a symlink" "$repo"
STUB_CWD="$repo/sub" check 1 "session cwd under path" "$repo"
STUB_CWD="${repo}0" check 0 "session cwd shares only a prefix" "$repo"

echo x >"$repo/new.txt"
check 1 "fresh uncommitted file" "$repo"
touch -d '2 hours ago' "$repo/new.txt"
check 0 "uncommitted file aged past 60 minutes" "$repo"

mkdir "$root/plain"
check 0 "plain directory outside git" "$root/plain"

[ "$fail" = 0 ] && echo "OK: claude-worktree-busy"
exit "$fail"
