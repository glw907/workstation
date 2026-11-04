#!/usr/bin/env bash
# pass-access.test.sh: prove pass-access prints this host's grant rows as agent<TAB>vault<TAB>role,
# sorted, from each local agent's own share list (claude-pass for <host>-claude, ws-pass-key for
# <host>-scripts); that an item share prints as "(item share)" and never as its title; that the
# list parses as a bare array or as {"shares": [...]} in either key case; and that a failed
# sign-in exits nonzero with nothing on stdout. Both readers are stubs; no pass-cli, keyring, or
# network is touched. The share lists are SYNTHETIC, modeled on the pass-cli docs' fields.
set -uo pipefail
cd "$(dirname "$0")/.." || exit 1
ACCESS="$(pwd)/bin/.local/bin/pass-access"
fail=0
root="$(mktemp -d)"
trap 'rm -rf "$root"' EXIT

assert_eq() {
  [ "$1" = "$2" ] || { echo "FAIL: $3: got '$1', want '$2'"; fail=1; }
}
assert_has() {  # assert_has <output> <fragment> <label>
  case "$1" in *"$2"*) ;; *) echo "FAIL: $3: no '$2' in: $1"; fail=1 ;; esac
}

# A stub reader prints the file named by its env var and exits with the code in the other.
for name in claude-pass ws-pass-key; do
  cat > "$root/$name" <<'EOF'
#!/usr/bin/env bash
echo "$*" >> "$STUB_LOG"
[ "${STUB_FAIL:-}" = "$(basename "$0")" ] && exit 1
case "$(basename "$0")" in
  claude-pass) cat "$STUB_CLAUDE_SHARES" ;;
  ws-pass-key) cat "$STUB_SCRIPTS_SHARES" ;;
esac
EOF
  chmod +x "$root/$name"
done

access() {  # access [env...]; prints stdout then "rc=N"
  local out rc
  out=$(env CLAUDE_PASS="$root/claude-pass" WS_PASS_KEY="$root/ws-pass-key" WS_HOST=testhost \
    STUB_LOG="$root/log" STUB_CLAUDE_SHARES="$root/claude.json" STUB_SCRIPTS_SHARES="$root/scripts.json" \
    "$@" bash "$ACCESS" 2>/dev/null)
  rc=$?
  printf '%s\nrc=%s' "$out" "$rc"
}

cat > "$root/claude.json" <<'EOF'
{"shares":[
 {"id":"s1","share_type":"Vault","name":"Projects","share_role":"Editor"},
 {"id":"s2","share_type":"Vault","name":"Age key","share_role":"Editor"},
 {"id":"s3","share_type":"Item","name":"A Secret Item Title","share_role":"Viewer"}
]}
EOF
printf '%s\n' '[{"shareType":"Vault","vaultName":"Age key","role":"viewer"}]' > "$root/scripts.json"
: > "$root/log"

want=$(printf 'testhost-claude\t(item share)\tviewer\ntesthost-claude\tAge key\teditor\ntesthost-claude\tProjects\teditor\ntesthost-scripts\tAge key\tviewer\nrc=0')
out=$(access)
assert_eq "$out" "$want" "rows are this host's, lowercase roles, sorted, with the item share anonymous"
case "$out" in *"Secret Item Title"*) echo "FAIL: an item title reached stdout"; fail=1 ;; esac
grep -q '^share list --output json$' "$root/log" || { echo "FAIL: claude-pass was not asked for share list --output json: $(cat "$root/log")"; fail=1; }
grep -q '^--shares$' "$root/log" || { echo "FAIL: ws-pass-key was not asked for --shares: $(cat "$root/log")"; fail=1; }

# A share with no type field, or an unrecognized one, never prints its name.
printf '%s\n' '{"shares":[{"name":"A Secret Item Title","share_role":"Viewer"},{"share_type":"Mystery","name":"Another Title","share_role":"Editor"}]}' > "$root/claude.json"
out=$(access)
assert_has "$out" "testhost-claude	(item share)	viewer" "an untyped share prints anonymously"
assert_has "$out" "testhost-claude	(item share)	editor" "an unrecognized type prints anonymously"
case "$out" in *"Title"*) echo "FAIL: a title leaked from an untyped share: $out"; fail=1 ;; esac

# A sign-in that fails exits nonzero with nothing on stdout, even when the other agent answered.
for who in claude-pass ws-pass-key; do
  out=$(access STUB_FAIL="$who")
  assert_eq "$out" "
rc=1" "a failed $who sign-in exits 1 with an empty stdout"
done

exit "$fail"
