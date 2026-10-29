#!/usr/bin/env bash
# gather-dotfiles-checkouts.test.sh: prove the checkouts section of the SessionStart hook
# (claude/.claude/gather-dotfiles.sh). Each case clones a local bare origin, pushes ahead of the
# clone, and runs the hook with FRESH_CHECKOUTS naming the clones and a fake session listing.
set -uo pipefail
cd "$(dirname "$0")/.." || exit
SCRIPT="$(pwd)/claude/.claude/gather-dotfiles.sh"
fail=0
root="$(mktemp -d)"
trap 'rm -rf "$root"' EXIT

has() { grep -qxF -- "$2" <<<"$1" || { echo "FAIL: $3: missing line '$2'"; fail=1; }; }
lacks() { ! grep -qF -- "$2" <<<"$1" || { echo "FAIL: $3: unexpected '$2'"; fail=1; }; }
assert_eq() { [ "$1" = "$2" ] || { echo "FAIL: $3: got '$1', want '$2'"; fail=1; }; }

g() { git -c user.email=t@t -c user.name=t "$@"; }

# mkpair <name>: a bare origin at $root/<name>.git with one commit on main, a clone at
# $root/<name>, and a pusher clone at $root/<name>-up that later commits go through.
mkpair() {
  git init -q --bare -b main "$root/$1.git"
  git clone -q "$root/$1.git" "$root/$1-up" 2>/dev/null
  g -C "$root/$1-up" commit -q --allow-empty -m init
  git -C "$root/$1-up" push -q origin HEAD:main
  git clone -q "$root/$1.git" "$root/$1"
}

# ahead <name> <n> [file]: pushes n commits to the origin, the last one adding file if given.
ahead() {
  local i
  for ((i = 1; i <= $2; i++)); do g -C "$root/$1-up" commit -q --allow-empty -m "c$i"; done
  if [ -n "${3:-}" ]; then
    mkdir -p "$root/$1-up/$(dirname "$3")"
    echo x >"$root/$1-up/$3"
    git -C "$root/$1-up" add "$3"
    g -C "$root/$1-up" commit -q -m "add $3"
  fi
  git -C "$root/$1-up" push -q origin HEAD:main
}

# run <session json> <repos...>: the hook's stdout in $out, its exit code in $rc. The session
# listing is a file the fake agents command prints.
run() {
  local json=$1
  shift
  printf '%s' "$json" >"$root/agents.json"
  out=$(cd "$root" && FRESH_CHECKOUTS="$*" CLAUDE_AGENTS_CMD="cat $root/agents.json" \
    INITIATIVES_DIR="$root/none" bash "$SCRIPT" 2>/dev/null <<<'{"session_id":"self"}')
  rc=$?
}

mkpair fresh
mkpair behind
mkpair branch
mkpair busy
mkpair mine
mkpair store
ahead behind 3
ahead branch 2
git -C "$root/branch" checkout -q -b topic
ahead busy 1
ahead mine 1
ahead store 0 secrets/values.age

agents='[{"sessionId":"other","cwd":"'"$root/busy"'"},{"sessionId":"self","cwd":"'"$root/mine"'"}]'
run "$agents" "$root/fresh" "$root/behind" "$root/branch" "$root/busy" "$root/mine" "$root/store"
assert_eq "$rc" "0" "exit 0"
has "$out" "## Checkouts" "header"
lacks "$out" "- fresh:" "a current checkout is not named"
has "$out" "- behind: pulled 3 commits" "a behind checkout is pulled"
assert_eq "$(git -C "$root/behind" rev-parse HEAD)" "$(git -C "$root/behind" rev-parse origin/main)" "the pull reached origin/main"
has "$out" "- branch: 2 behind origin/main, not pulled: the checkout is on another branch" "another branch"
has "$out" "- busy: 1 behind origin/main, not pulled: another session is live in it" "a live session"
has "$out" "- mine: pulled 1 commit" "this session's own checkout is pulled"
has "$out" "- store: the secret store changed; run scripts/secrets/secret-set.sh --sync" "a changed store is named"
has "$out" "## Shell Environment (drift check; canonical inventory is CLAUDE.md)" "existing output kept"

# Every checkout current: no section.
run '[]' "$root/fresh" "$root/behind"
lacks "$out" "## Checkouts" "no section when all are current"

# A failed fetch is named and never fails the hook.
git -C "$root/fresh" remote set-url origin "$root/missing.git"
run '[]' "$root/fresh"
assert_eq "$rc" "0" "fetch failure: exit 0"
has "$out" "- fresh: the fetch failed, so it may be behind" "fetch failure: named"

# An empty list turns the section off.
run '[]' ""
lacks "$out" "## Checkouts" "empty list: no section"

[ "$fail" -eq 0 ] && echo "gather-dotfiles-checkouts: all passed"
exit "$fail"
