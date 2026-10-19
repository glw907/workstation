#!/usr/bin/env bash
# check-drift-proton.test.sh: prove `check-drift --proton-only` reports the pass-cli version brew
# holds and the host's age-key path and agent-token expiry, from stub brew and ws-pass-key
# commands. No real brew, keyring, or pass-cli is touched.
set -uo pipefail
cd "$(dirname "$0")/.." || exit 1
DRIFT="$(pwd)/bin/.local/bin/check-drift"
fail=0
root="$(mktemp -d)"
trap 'rm -rf "$root"' EXIT

assert_has() {  # assert_has <output> <fragment> <label>
  case "$1" in *"$2"*) ;; *) echo "FAIL: $3: no '$2' in: $1"; fail=1 ;; esac
}

printf '#!/usr/bin/env bash\n[ -n "${STUB_NO_BREW:-}" ] && exit 1\necho "proton-pass-cli 2.4.2"\n' > "$root/brew"
printf '#!/usr/bin/env bash\necho "$STUB_STATUS"\n' > "$root/ws-pass-key"
chmod +x "$root/brew" "$root/ws-pass-key"

drift() {  # drift <STUB_STATUS> [env...]; prints output, then "rc=N"
  local status="$1"; shift
  local out rc
  out=$(env BREW="$root/brew" WS_PASS_KEY="$root/ws-pass-key" STUB_STATUS="$status" "$@" bash "$DRIFT" --proton-only 2>&1)
  rc=$?
  printf '%s\nrc=%s' "$out" "$rc"
}

out=$(drift "path=proton host=h expires=2999-01-01 days=900")
assert_has "$out" "pass-cli: 2.4.2" "version line"
assert_has "$out" "age key path: Proton Pass agent token" "proton path line"
assert_has "$out" "agent token expires in 900 days" "expiry line"
assert_has "$out" "rc=0" "healthy host exits 0"

out=$(drift "path=op host=h")
assert_has "$out" "age key path: 1Password" "op path line"
assert_has "$out" "rc=0" "a host still on op warns without failing"

out=$(drift "path=proton host=h expires=2026-11-01 days=14")
assert_has "$out" "expires in 14 days (renew it)" "near-expiry warning"
assert_has "$out" "rc=0" "near expiry warns without failing"

out=$(drift "path=proton host=h expires=2026-10-01 days=-17")
assert_has "$out" "expired 17 days ago" "expired token line"
assert_has "$out" "rc=1" "an expired token fails"

out=$(drift "path=proton host=h expires=unknown")
assert_has "$out" "expiry unknown" "unknown expiry warning"

out=$(drift "path=op host=h" STUB_NO_BREW=1)
assert_has "$out" "proton-pass-cli is not installed" "missing package line"
assert_has "$out" "rc=1" "a missing package fails"

exit "$fail"
