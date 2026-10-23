#!/usr/bin/env bash
# secret-set-quoting.test.sh: prove the ~/.local/secrets file secret-set.sh writes gives every
# value back byte-exact when a shell sources it, including spaces, $, backticks, quotes, a
# backslash, and trailing "=". The run uses a generated age key and fake values only.
set -uo pipefail
cd "$(dirname "$0")/.."
SCRIPT="$(pwd)/scripts/secrets/secret-set.sh"
fail=0
root="$(mktemp -d)"
trap 'rm -rf "$root"' EXIT

assert_eq() {
  [ "$1" = "$2" ] || { echo "FAIL: $3: got '$1', want '$2'"; fail=1; }
}

age-keygen -o "$root/key.txt" 2>/dev/null
recip=$(age-keygen -y "$root/key.txt")
cp "$root/key.txt" "$root/cache"
chmod 600 "$root/cache"

nasty='a b $HOME `id` $(id) "dq" '"'sq'"' back\slash ;|&<>*? #x ~ pad=='
plain='plainvalue123'
printf 'PLAIN_ONE=%s\nNASTY_ONE=%s\n' "$plain" "$nasty" > "$root/plain"
age -r "$recip" -o "$root/values.age" "$root/plain"

out=$(VALUES="$root/values.age" LOCAL_SECRETS="$root/local-secrets" RECIP="$recip" CACHE="$root/cache" \
  XDG_RUNTIME_DIR="$root" bash "$SCRIPT" --sync 2>&1)
assert_eq "$?" "0" "sync exits 0 ($out)"

# Source in a clean subshell and print each value; a lone sentinel proves nothing ran.
got_nasty=$(env -i bash -c '. "$1" && printf %s "$NASTY_ONE"' _ "$root/local-secrets")
got_plain=$(env -i bash -c '. "$1" && printf %s "$PLAIN_ONE"' _ "$root/local-secrets")
assert_eq "$got_nasty" "$nasty" "special-character value round-trips"
assert_eq "$got_plain" "$plain" "plain value round-trips"

# A --value write goes through the same path.
VALUES="$root/values.age" LOCAL_SECRETS="$root/local-secrets" RECIP="$recip" CACHE="$root/cache" \
  XDG_RUNTIME_DIR="$root" bash "$SCRIPT" ADDED_ONE --value "$nasty" >/dev/null 2>&1
assert_eq "$?" "0" "value write exits 0"
got_added=$(env -i bash -c '. "$1" && printf %s "$ADDED_ONE"' _ "$root/local-secrets")
assert_eq "$got_added" "$nasty" "a value written with --value round-trips"
assert_eq "$(grep -c '^export ' "$root/local-secrets")" "3" "three exports written"

exit "$fail"
