#!/usr/bin/env bash
# pass-sitting.test.sh: prove pass-sitting against the fake pass-cli (tests/fixtures/pass-cli) and
# the invented replies in tests/fixtures/pass-sitting. A dry run makes no call; --apply logs in
# once and lists each named vault once; a title that matches none or several fails its line while
# the next line still runs; a note lands above the old one and the old text never reaches stdout
# or the results file; revoke passes the share id on its line; the audit prints the
# grant map's shape; and the session directory is gone after a success, a failed login, and a
# TERM. pass-sitting never runs against real Proton: this is the only place it runs for Claude.
set -uo pipefail
cd "$(dirname "$0")/.." || exit 1
repo="$(pwd)"
SITTING="$repo/bin/.local/bin/pass-sitting"
FIX="$repo/tests/fixtures/pass-sitting"
fail=0
root="$(mktemp -d)"
trap 'rm -rf "$root"' EXIT

assert_eq() {
  [ "$1" = "$2" ] || { echo "FAIL: $3: got '$1', want '$2'"; fail=1; }
}
assert_has() {  # assert_has <text> <fragment> <label>
  case "$1" in *"$2"*) ;; *) echo "FAIL: $3: no '$2' in: $1"; fail=1 ;; esac
}
assert_lacks() {
  case "$1" in *"$2"*) echo "FAIL: $3: '$2' leaked into: $1"; fail=1 ;; esac
}

mkdir -p "$root/bin" "$root/run"
cp "$repo/tests/fixtures/pass-cli" "$root/bin/pass-cli"
cp -r "$FIX" "$root/vault"
cp "$FIX/ops.jsonl" "$root/ops.jsonl"

reset() { rm -f "$root/pass.log" "$root/ops.jsonl.results.tsv"; rm -rf "$root"/run/pass-sitting.*; }
sessions_left() { ls -d "$root"/run/pass-sitting.* 2>/dev/null | wc -l; }
calls() { [ -f "$root/pass.log" ] && { grep -c "^$1" "$root/pass.log" || true; } || echo 0; }
sitting() {  # sitting [env...] -- <args...>; stdout and stderr together
  local envs=()
  while [ "$1" != "--" ]; do envs+=("$1"); shift; done
  shift
  env PATH="$root/bin:$PATH" XDG_RUNTIME_DIR="$root/run" HOME="$root/home" FAKE_PASS_LOG="$root/pass.log" \
    FAKE_PASS_FIXTURE="$root/vault" "${envs[@]}" bash "$SITTING" "$@" 2>&1
}

# 1. A dry run prints each operation and makes no call at all.
reset
out=$(sitting -- "$root/ops.jsonl")
assert_eq "$?" "0" "the dry run exits 0"
assert_has "$out" "rename	vault=Alpha	title=Old name	new_title=New name" "the dry run prints a rename"
assert_has "$out" "revoke	agent=x-scripts	share_id=sid-9" "the dry run prints a revoke by share id"
assert_has "$out" "Dry run only" "the dry run says so"
[ ! -e "$root/pass.log" ] || { echo "FAIL: the dry run called pass-cli: $(cat "$root/pass.log")"; fail=1; }
assert_eq "$(sessions_left)" "0" "the dry run makes no session directory"

# 1b. A bad line stops the run before any sign-in.
printf '{"op":"trash","vault":"Alpha"}\n{"op":"explode"}\n' > "$root/bad.jsonl"
out=$(sitting -- "$root/bad.jsonl")
[ "$?" -ne 0 ] || { echo "FAIL: a bad file exited 0"; fail=1; }
printf '%s\n' '{"op":"grant","agent":"a-claude","vault":"V","to":"viewer","role":"manager"}' \
    '{"op":"rename","vault":"V","title":"T","new_title":"U","all":true}' \
    '{"op":"revoke","agent":"a-claude","vault":"V","share_id":"s"}' \
    '{"op":"grant","agent":"-bad","vault":"V"}' > "$root/fields.jsonl"
out3=$(sitting -- "$root/fields.jsonl")
[ "$?" -ne 0 ] || { echo "FAIL: a file with unknown fields exited 0"; fail=1; }
assert_has "$out3" "an agent name must start" "a bad agent name is refused"
sed -i '$d' "$root/fields.jsonl"
out3=$(sitting -- "$root/fields.jsonl")
assert_has "$out3" "line 1: unknown field to" "an unknown field is named, so the dry run cannot hide it"
assert_has "$out3" "line 2: unknown field all" "all is refused on a rename"
assert_has "$out3" "line 3: unknown field vault" "a revoke by vault is refused: only the agent-side share_id works"
printf '%s\n' '{"op":"revoke","agent":"a-claude"}' '{"op":"revoke","agent":"a-claude","share_id":""}' > "$root/norevoke.jsonl"
out3=$(sitting -- "$root/norevoke.jsonl")
assert_has "$out3" "line 1: revoke needs share_id" "a revoke without a share id is refused"
assert_has "$out3" "line 2: revoke needs a non-empty share_id" "an empty share id is refused in the dry run"
printf 'not json\n' > "$root/notjson.jsonl"
out2=$(sitting -- "$root/notjson.jsonl")
[ "$?" -ne 0 ] || { echo "FAIL: a non-JSON file exited 0"; fail=1; }
assert_has "$out2" "not JSON lines" "a non-JSON file is named"
assert_has "$out" "line 1: trash needs title" "a missing field is named"
assert_has "$out" "line 2: not an operation" "an unknown op is named"
[ ! -e "$root/pass.log" ] || { echo "FAIL: a bad file reached pass-cli"; fail=1; }

# 2. --apply: one login, each named vault listed once, a failed line does not stop the next.
reset
out=$(sitting FAKE_PASS_NOISE=1 -- --apply "$root/ops.jsonl")
assert_eq "$?" "0" "--apply exits 0 ($out)"
assert_eq "$(calls login)" "1" "--apply logs in once"
assert_eq "$(calls 'item list')" "1" "--apply lists the one named vault once"
assert_has "$out" "FAILED: trash Alpha / Dup matched 2 items" "an ambiguous title fails its line"
assert_has "$out" "FAILED: trash Alpha / Missing matched 0 items" "a title with no match fails its line"
assert_has "$out" "FAILED: rename Alpha / Dup matched 2 items" "an ambiguous rename edits nothing"
assert_has "$out" "could not read the old note" "a note whose old text cannot be read fails"
assert_has "$out" "done: 7 ok, 4 failed" "the bad lines are counted and the rest ran"
if grep -q -- '--item-id=a7 --field note=\|--item-id=a2\|--item-id=a3' "$root/pass.log"; then echo "FAIL: a failed line still edited an item"; fail=1; fi
assert_lacks "$out" "Error opening share" "the share noise is filtered"
grep -q '^item move --from-vault-name=Alpha --item-id=a5 --to-vault-name=Beta' "$root/pass.log" || { echo "FAIL: the move after a failed line did not run"; fail=1; }
grep -q '^item update --vault-name=Alpha --item-id=a4 --field title=New name' "$root/pass.log" || { echo "FAIL: the rename did not run"; fail=1; }
grep -q '^agent access grant x-claude --vault-name Beta --role editor' "$root/pass.log" || { echo "FAIL: the grant did not run"; fail=1; }
assert_eq "$(calls 'item trash')" "0" "an ambiguous trash touches nothing"

# 2b. A note goes above the old one, which is read and never printed or recorded.
grep -q '^item update --vault-name=Alpha --item-id=a1 --field note=For: the router\.' "$root/pass.log" || { echo "FAIL: the note was not written to a1"; fail=1; }
[ "$(grep -c 'OLDSECRETNOTE' "$root/pass.log")" -ge 1 ] || { echo "FAIL: the old note was not kept below the new one"; fail=1; }
assert_lacks "$out" "OLDSECRETNOTE" "stdout"
assert_lacks "$(cat "$root/ops.jsonl.results.tsv")" "OLDSECRETNOTE" "the results file"
assert_eq "$(stat -c %a "$root/ops.jsonl.results.tsv")" "600" "the results file is mode 600"

# 2c. A revoke takes the agent-side share id on its line (the owner's id from vault list is refused by pass-cli).
grep -q '^agent access revoke x-claude --share-id sid-agent-claude' "$root/pass.log" || { echo "FAIL: revoke did not pass the line's agent-side share id"; fail=1; }
grep -q '^agent access revoke x-scripts --share-id sid-9' "$root/pass.log" || { echo "FAIL: revoke did not pass the line's share id"; fail=1; }

# 2d. The audit prints agent, vault, role, expiry, and says when a field could not be read.
assert_has "$out" "x-claude	Alpha	editor	2027-01-20" "the audit row for an agent with an expiry"
assert_has "$out" "geoff	Alpha	owner	unknown" "the audit row for a member with no expiry"
assert_has "$out" "unknown	Alpha	viewer	unknown" "a member with no name shows as unknown"
assert_has "$out" "some fields could not be read" "the audit says it could not read every field"

# 2e. Every call used the per-run session directory; the default-session refusal never fired.
assert_eq "$(grep -c "session=$root/run/pass-sitting\.[A-Za-z0-9]* " "$root/pass.log")" "$(grep -c " | session=" "$root/pass.log")" "every call used a pass-sitting session directory"
assert_lacks "$out" "refusing the default session" "output"
grep -q 'logout' "$root/pass.log" || { echo "FAIL: pass-sitting never logged out"; fail=1; }
assert_eq "$(sessions_left)" "0" "the session directory is gone after a success"

# 3. A failed login ends the run with no change and no session directory left.
reset
out=$(sitting FAKE_PASS_WEB_FAIL=1 -- --apply "$root/ops.jsonl")
[ "$?" -ne 0 ] || { echo "FAIL: a failed login exited 0"; fail=1; }
assert_eq "$(calls 'item update')" "0" "a failed login changes nothing"
assert_eq "$(sessions_left)" "0" "a failed login leaves no session directory"

# 4. TERM mid-run still logs out and removes the session directory.
reset
FAKE_PASS_SLEEP=2 sitting FAKE_PASS_SLEEP=2 -- --apply "$root/ops.jsonl" > "$root/term.out" &
bg=$!
for _ in $(seq 40); do grep -q '^item list' "$root/pass.log" 2>/dev/null && break; sleep 0.1; done
pkill -TERM -f "bash $SITTING --apply $root/ops.jsonl"
wait "$bg" 2>/dev/null
sleep 3
case "$(cat "$root/term.out")" in *"done:"*) echo "FAIL: the TERM never landed; the run finished"; fail=1 ;; esac
assert_eq "$(sessions_left)" "0" "TERM leaves no session directory"
grep -q 'logout' "$root/pass.log" || { echo "FAIL: TERM skipped the logout"; fail=1; }

exit "$fail"
