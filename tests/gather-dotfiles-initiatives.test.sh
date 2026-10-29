#!/usr/bin/env bash
# gather-dotfiles-initiatives.test.sh: prove the initiatives section of the SessionStart hook
# (claude/.claude/gather-dotfiles.sh). Each case runs the hook from a temporary repo against the
# fixture initiatives tree. The hook also prints bashrc exports, so assertions grep for lines.
set -uo pipefail
cd "$(dirname "$0")/.."
SCRIPT="$(pwd)/claude/.claude/gather-dotfiles.sh"
FIXTURES="$(pwd)/tests/fixtures/initiatives"
fail=0
root="$(mktemp -d)"
trap 'rm -rf "$root"' EXIT

has() { grep -qxF -- "$2" <<<"$1" || { echo "FAIL: $3: missing line '$2'"; fail=1; }; }
lacks() { ! grep -qF -- "$2" <<<"$1" || { echo "FAIL: $3: unexpected '$2'"; fail=1; }; }
assert_eq() { [ "$1" = "$2" ] || { echo "FAIL: $3: got '$1', want '$2'"; fail=1; }; }

# mkrepo <dir> <origin url>: a repo with one commit and an origin remote.
mkrepo() {
  git init -q "$1"
  git -C "$1" -c user.email=t@t -c user.name=t commit -q --allow-empty -m init
  [ -z "$2" ] || git -C "$1" remote add origin "$2"
}

# run <cwd> <initiatives dir>: leaves the hook's stdout in $out and its exit code in $rc.
run() {
  out=$(cd "$1" && INITIATIVES_DIR="$2" FRESH_CHECKOUTS="" bash "$SCRIPT" 2>/dev/null </dev/null)
  rc=$?
}

mkrepo "$root/ws" "git@github.com:glw907/workstation.git"
mkrepo "$root/lonely" "https://github.com/glw907/lonely"
mkrepo "$root/noorigin" ""
mkdir -p "$root/plain"

# match: active and proposed print, paused and done do not, other repos' records do not.
run "$root/ws" "$FIXTURES"
assert_eq "$rc" "0" "match: exit 0"
has "$out" "## Initiatives (workstation)" "match: header"
has "$out" "- alpha-run: Runs the alpha work." "match: active"
has "$out" "- beta-plan: Plans the beta work." "match: proposed"
lacks "$out" "gamma-hold" "match: paused hidden"
lacks "$out" "delta-ship" "match: done hidden"
lacks "$out" "epsilon-other" "match: other repo hidden"
has "$out" "## Shell Environment (drift check; canonical inventory is CLAUDE.md)" "match: existing output kept"

# no clone
run "$root/ws" "$root/missing"
assert_eq "$rc" "0" "no clone: exit 0"
has "$out" "initiatives: no clone at ~/Projects/initiatives" "no clone: line"
has "$out" "## Shell Environment (drift check; canonical inventory is CLAUDE.md)" "no clone: existing output kept"

# unreadable record: reported, and the valid records still print.
cp -r "$FIXTURES" "$root/bad"
mkdir "$root/bad/broken"
printf 'id: broken\nsummary: [unclosed\n  status: : active\n' >"$root/bad/broken/initiative.yaml"
run "$root/ws" "$root/bad"
assert_eq "$rc" "0" "unreadable: exit 0"
has "$out" "initiatives: unreadable $root/bad/broken/initiative.yaml" "unreadable: line"
has "$out" "- alpha-run: Runs the alpha work." "unreadable: valid record still prints"
has "$out" "- beta-plan: Plans the beta work." "unreadable: second valid record still prints"

# no match: nothing at all, not even a header.
run "$root/lonely" "$FIXTURES"
assert_eq "$rc" "0" "no match: exit 0"
lacks "$out" "Initiatives" "no match: no header"
lacks "$out" "initiatives:" "no match: no failure line"
lacks "$out" "alpha-run" "no match: no records"

# not a repo, and a repo with no origin: nothing, exit 0.
run "$root/plain" "$FIXTURES"
assert_eq "$rc" "0" "no repo: exit 0"
lacks "$out" "Initiatives" "no repo: no header"
run "$root/noorigin" "$FIXTURES"
assert_eq "$rc" "0" "no origin: exit 0"
lacks "$out" "Initiatives" "no origin: no header"

# worktree: a linked worktree resolves to its parent repo.
git -C "$root/ws" worktree add -q "$root/ws-wt" -b wt
run "$root/ws-wt" "$FIXTURES"
assert_eq "$rc" "0" "worktree: exit 0"
has "$out" "## Initiatives (workstation)" "worktree: header"
has "$out" "- alpha-run: Runs the alpha work." "worktree: record"

# a checkout directory named .dotfiles whose origin is workstation.
mkrepo "$root/.dotfiles" "git@github.com:glw907/workstation.git"
run "$root/.dotfiles" "$FIXTURES"
assert_eq "$rc" "0" ".dotfiles: exit 0"
has "$out" "## Initiatives (workstation)" ".dotfiles: header"
has "$out" "- beta-plan: Plans the beta work." ".dotfiles: record"

# yq missing: a PATH of symlinks to the other tools the hook needs.
mkdir "$root/bin"
for tool in git grep sed cat hostname basename dirname; do
  p=$(command -v "$tool") && ln -s "$p" "$root/bin/$tool"
done
out=$(cd "$root/ws" && PATH="$root/bin" INITIATIVES_DIR="$FIXTURES" "$(command -v bash)" "$SCRIPT" 2>/dev/null)
rc=$?
assert_eq "$rc" "0" "no yq: exit 0"
has "$out" "initiatives: yq not found" "no yq: line"
has "$out" "## Shell Environment (drift check; canonical inventory is CLAUDE.md)" "no yq: existing output kept"

exit "$fail"
