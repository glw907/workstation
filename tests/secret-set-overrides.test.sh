#!/usr/bin/env bash
# secret-set-overrides.test.sh: prove secret-set.sh --delete reaches only the paths its four
# overrides name (VALUES, LOCAL_SECRETS, RECIP, CACHE). The run uses a temp HOME holding a fixture
# main-checkout store, a generated age key pair, and a failing stub `op` first on PATH. The
# fixture main store must stay byte-identical, and the real ~/.local/secrets and the real
# /dev/shm key cache must keep their mtimes.
set -uo pipefail
cd "$(dirname "$0")/.."
SCRIPT="$(pwd)/scripts/secrets/secret-set.sh"
fail=0
root="$(mktemp -d)"
trap 'rm -rf "$root"' EXIT

assert_eq() {
  [ "$1" = "$2" ] || { echo "FAIL: $3: got '$1', want '$2'"; fail=1; }
}

real_home="$HOME"
real_cache="/dev/shm/.age-key-$(id -u)"
mtime() { stat -c %Y "$1" 2>/dev/null || echo absent; }
real_secrets_before=$(mtime "$real_home/.local/secrets")
real_cache_before=$(mtime "$real_cache")

home="$root/home"
mkdir -p "$home/.dotfiles/secrets" "$home/.local" "$root/wt" "$root/bin"
age-keygen -o "$root/key.txt" 2>/dev/null
recip=$(age-keygen -y "$root/key.txt")
printf 'KEEP_ONE=alpha\nRETIRED_ONE=beta\nKEEP_TWO=gamma\n' > "$root/plain"
age -r "$recip" -o "$home/.dotfiles/secrets/values.age" "$root/plain"
cp "$home/.dotfiles/secrets/values.age" "$root/wt/values.age"
cp "$root/key.txt" "$root/cache"
chmod 600 "$root/cache"
main_sum=$(sha256sum "$home/.dotfiles/secrets/values.age" | cut -d' ' -f1)

# A stub that fails and leaves a marker, so a run that reaches 1Password is caught.
printf '#!/usr/bin/env bash\ntouch "%s/op-called"\nexit 1\n' "$root" > "$root/bin/op"
chmod +x "$root/bin/op"

out=$(HOME="$home" PATH="$root/bin:$PATH" \
  VALUES="$root/wt/values.age" LOCAL_SECRETS="$home/.local/secrets" \
  RECIP="$recip" CACHE="$root/cache" \
  bash "$SCRIPT" RETIRED_ONE --delete 2>&1)
rc=$?
assert_eq "$rc" "0" "delete exits 0 ($out)"

names=$(age --decrypt -i "$root/key.txt" "$root/wt/values.age" | cut -d= -f1 | sort | tr '\n' ' ')
assert_eq "$names" "KEEP_ONE KEEP_TWO " "worktree store drops only the retired name"
assert_eq "$(sha256sum "$home/.dotfiles/secrets/values.age" | cut -d' ' -f1)" "$main_sum" \
  "fixture main store is byte-identical"
assert_eq "$(grep -c '^export ' "$home/.local/secrets" 2>/dev/null)" "2" "temp local secrets rewritten from the override store"
assert_eq "$(grep -c RETIRED_ONE "$home/.local/secrets" 2>/dev/null)" "0" "temp local secrets lacks the retired name"
[ ! -e "$root/op-called" ] || { echo "FAIL: the run reached 1Password"; fail=1; }
assert_eq "$(mtime "$real_home/.local/secrets")" "$real_secrets_before" "real ~/.local/secrets mtime"
assert_eq "$(mtime "$real_cache")" "$real_cache_before" "real /dev/shm cache mtime"

exit "$fail"
