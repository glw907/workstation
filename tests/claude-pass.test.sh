#!/usr/bin/env bash
# claude-pass.test.sh: prove claude-pass runs one command through the host's claude agent token
# with an audit reason, in a per-run session directory that is gone afterward, and logs out; that
# the token never reaches an argument or the output; that stdin reaches `item create`; that a host
# with no token gets a clear refusal and no pass-cli call; and that --status reports both cases.
# Every run uses the fake pass-cli (tests/fixtures/pass-cli), a stub secret-tool, and a scratch
# XDG_RUNTIME_DIR. The real pass-cli and keyring are never touched.
set -uo pipefail
cd "$(dirname "$0")/.." || exit 1
repo="$(pwd)"
HELPER="$repo/bin/.local/bin/claude-pass"
fail=0
root="$(mktemp -d)"
trap 'rm -rf "$root"' EXIT

assert_eq() {
  [ "$1" = "$2" ] || { echo "FAIL: $3: got '$1', want '$2'"; fail=1; }
}

mkdir -p "$root/bin" "$root/run" "$root/vault/Workstation/thing" "$root/home"
cp "$repo/tests/fixtures/pass-cli" "$root/bin/pass-cli"
echo "fixture-value" > "$root/vault/Workstation/thing/note"
TOKEN='pst_fake::KEY'

# secret-tool stub: lookup prints the token file when present and logs its arguments.
cat > "$root/bin/secret-tool" <<EOF
#!/usr/bin/env bash
echo "\$*" >> "$root/secret-tool.log"
[ "\$1" = lookup ] && [ -s "$root/token" ] && cat "$root/token" || exit 1
EOF
chmod +x "$root/bin/"*

reset() { rm -f "$root/pass.log" "$root/pass.log.stdin" "$root/token" "$root/secret-tool.log"; rm -rf "$root"/run/pass-agent.*; }
sessions_left() { ls -d "$root"/run/pass-agent.* 2>/dev/null | wc -l; }
pass_calls() { [ -f "$root/pass.log" ] && wc -l < "$root/pass.log" || echo 0; }
helper() {  # helper <args...>; reads stdin
  env HOME="$root/home" PATH="$root/bin:$PATH" XDG_RUNTIME_DIR="$root/run" WS_HOST=testhost \
    FAKE_PASS_LOG="$root/pass.log" FAKE_PASS_FIXTURE="$root/vault" bash "$HELPER" "$@" 2>&1
}

# 1. A token in the keyring: the command runs through an agent login with a reason, then logs out.
reset; echo "$TOKEN" > "$root/token"
out=$(helper item view pass://Workstation/thing/note </dev/null)
assert_eq "$?" "0" "token path exits 0 ($out)"
assert_eq "$out" "fixture-value" "the command's output passes through"
grep -q 'service proton-pass-agent-claude host testhost' "$root/secret-tool.log" || { echo "FAIL: the token lookup did not name the claude service and host"; fail=1; }
grep -q '^login .*token=set' "$root/pass.log" || { echo "FAIL: no agent-token login"; fail=1; }
grep -q '^item view pass://Workstation/thing/note .*reason=claude-pass on testhost: item view' "$root/pass.log" || { echo "FAIL: the command carried no default reason: $(cat "$root/pass.log")"; fail=1; }
assert_eq "$(grep -c "session=$root/run/pass-agent\.[A-Za-z0-9]* " "$root/pass.log")" "$(pass_calls)" "every call used a per-run session directory under XDG_RUNTIME_DIR"
grep -q 'logout' "$root/pass.log" || { echo "FAIL: claude-pass never logged out"; fail=1; }
assert_eq "$(sessions_left)" "0" "the session directory is removed"
grep -q "$TOKEN" "$root/pass.log" && { echo "FAIL: the token leaked into a recorded argument"; fail=1; }
case "$out" in *"$TOKEN"*) echo "FAIL: the token leaked into the output"; fail=1 ;; esac

# 2. CLAUDE_PASS_REASON sets the reason, and stdin reaches item create.
reset; echo "$TOKEN" > "$root/token"
out=$(printf 'name: x\npassword: s3cret\n' | env CLAUDE_PASS_REASON="store a test login" \
  HOME="$root/home" PATH="$root/bin:$PATH" XDG_RUNTIME_DIR="$root/run" WS_HOST=testhost \
  FAKE_PASS_LOG="$root/pass.log" FAKE_PASS_FIXTURE="$root/vault" \
  bash "$HELPER" item create login --vault-name "Servers emergency" --from-template - 2>&1)
assert_eq "$?" "0" "item create exits 0 ($out)"
grep -q '^item create login --vault-name Servers emergency --from-template - .*reason=store a test login' "$root/pass.log" || { echo "FAIL: item create did not carry the given reason: $(cat "$root/pass.log")"; fail=1; }
assert_eq "$(cat "$root/pass.log.stdin" 2>/dev/null)" "$(printf 'name: x\npassword: s3cret')" "stdin reached item create"
grep -q 's3cret' "$root/pass.log" && { echo "FAIL: the value from stdin landed in an argument"; fail=1; }
assert_eq "$(sessions_left)" "0" "item create leaves no session directory"

# 3. No token in the keyring: exit 1 with the message, and no pass-cli call at all.
reset
out=$(helper item list </dev/null)
assert_eq "$?" "1" "the no-token path exits 1"
case "$out" in *"no agent token for testhost"*"proton-pass-agent-claude"*) ;; *) echo "FAIL: the no-token path did not say so: $out"; fail=1 ;; esac
assert_eq "$(pass_calls)" "0" "the no-token path makes no pass-cli call"
assert_eq "$(sessions_left)" "0" "the no-token path makes no session directory"

# 4. A bad token fails the login loudly and still cleans up.
reset; echo "pst_wrong::KEY" > "$root/token"
out=$(helper item list </dev/null)
[ "$?" -ne 0 ] || { echo "FAIL: a bad token exited 0"; fail=1; }
case "$out" in *"login failed"*) ;; *) echo "FAIL: a bad token did not say the login failed: $out"; fail=1 ;; esac
grep -q '^item list' "$root/pass.log" && { echo "FAIL: the command ran after a failed login"; fail=1; }
assert_eq "$(sessions_left)" "0" "a bad token leaves no session directory"

# 4b. A command that fails after a good login keeps its exit code, and cleanup still runs.
reset; echo "$TOKEN" > "$root/token"
out=$(helper item edit pass://Workstation/thing/note </dev/null)
assert_eq "$?" "2" "a failing command's exit code is preserved ($out)"
grep -q 'logout' "$root/pass.log" || { echo "FAIL: a failing command skipped the logout"; fail=1; }
assert_eq "$(sessions_left)" "0" "a failing command leaves no session directory"

# 4c. A subcommand off the allowlist is refused before the token is read: no lookup, no call.
for sub in run login agent ssh-agent share; do
  reset; echo "$TOKEN" > "$root/token"
  out=$(helper "$sub" -- true </dev/null)
  assert_eq "$?" "1" "'$sub' is refused with exit 1"
  case "$out" in *"subcommand '$sub' is not allowed"*) ;; *) echo "FAIL: '$sub' refusal did not say so: $out"; fail=1 ;; esac
  [ -s "$root/secret-tool.log" ] && { echo "FAIL: '$sub' read the keyring"; fail=1; }
  assert_eq "$(pass_calls)" "0" "'$sub' makes no pass-cli call"
done

# 4d. A reason over 300 characters is refused before the token is read.
reset; echo "$TOKEN" > "$root/token"
long=$(printf 'x%.0s' $(seq 301))
out=$(env CLAUDE_PASS_REASON="$long" HOME="$root/home" PATH="$root/bin:$PATH" XDG_RUNTIME_DIR="$root/run" \
  WS_HOST=testhost FAKE_PASS_LOG="$root/pass.log" bash "$HELPER" item list 2>&1 </dev/null)
assert_eq "$?" "1" "an over-long reason exits 1"
case "$out" in *"1 to 300 characters"*) ;; *) echo "FAIL: an over-long reason did not say so: $out"; fail=1 ;; esac
assert_eq "$(pass_calls)" "0" "an over-long reason makes no pass-cli call"

# 5. --status names the path without printing the token or calling pass-cli.
reset; echo "$TOKEN" > "$root/token"
out=$(helper --status)
assert_eq "$out" "path=proton host=testhost" "--status with a token"
assert_eq "$(pass_calls)" "0" "--status makes no pass-cli call"
reset
out=$(helper --status)
assert_eq "$out" "path=none host=testhost" "--status without a token"

exit "$fail"
