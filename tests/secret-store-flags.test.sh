#!/usr/bin/env bash
# secret-store-flags.test.sh: prove the --values and --local flags on secret-set.sh, secret-receive,
# and sync.sh reach only the paths they name; two concurrent stores both survive; a store that
# would drop a name fails and leaves the store alone; and --delete removes only its own name. Every
# run uses a temp HOME holding a fixture main-checkout store, a generated age key pair, a failing
# stub `op`, and an `age` wrapper that can slow or corrupt an encrypt. The fixture main store must
# stay byte-identical, and the real ~/.local/secrets and /dev/shm key cache keep their mtimes.
set -uo pipefail
cd "$(dirname "$0")/.." || exit 1
repo="$(pwd)"
SET="$repo/scripts/secrets/secret-set.sh"
SYNC="$repo/scripts/secrets/sync.sh"
RECEIVE="$repo/bin/.local/bin/secret-receive"
real_age="$(command -v age)"
fail=0
root="$(mktemp -d)"
trap 'rm -rf "$root"' EXIT

assert_eq() {
  [ "$1" = "$2" ] || { echo "FAIL: $3: got '$1', want '$2'"; fail=1; }
}

real_cache="/dev/shm/.age-key-$(id -u)"
mtime() { stat -c %Y "$1" 2>/dev/null || echo absent; }
real_secrets_before=$(mtime "$HOME/.local/secrets")
real_cache_before=$(mtime "$real_cache")

home="$root/home"
mkdir -p "$home/.dotfiles/secrets" "$home/.dotfiles/scripts" "$home/.local" "$root/wt" "$root/bin" "$root/run"
ln -s "$repo/scripts/secrets" "$home/.dotfiles/scripts/secrets"
age-keygen -o "$root/key.txt" 2>/dev/null
recip=$(age-keygen -y "$root/key.txt")
printf 'KEEP_ONE=alpha\nKEEP_TWO=gamma\n' > "$root/plain"
age -r "$recip" -o "$home/.dotfiles/secrets/values.age" "$root/plain"
cp "$root/key.txt" "$root/cache"
chmod 600 "$root/cache"
main_sum=$(sha256sum "$home/.dotfiles/secrets/values.age" | cut -d' ' -f1)

# An op stub that fails and leaves a marker, so a run that reaches 1Password is caught.
printf '#!/usr/bin/env bash\ntouch "%s/op-called"\nexit 1\n' "$root" > "$root/bin/op"
# An age wrapper: AGE_SLOW sleeps before an encrypt, and AGE_DROP_FIRST drops the plaintext's first
# line before encrypting, the way a buggy writer would lose a name.
cat > "$root/bin/age" <<EOF
#!/usr/bin/env bash
if [[ " \$* " == *" -r "* ]]; then
  [[ -n "\${AGE_SLOW:-}" ]] && sleep "\$AGE_SLOW"
  if [[ -n "\${AGE_DROP_FIRST:-}" ]]; then
    in="\${@: -1}"; tmp="\$(mktemp)"; sed 1d "\$in" > "\$tmp"
    args=("\${@:1:\$#-1}" "\$tmp"); "$real_age" "\${args[@]}"; rc=\$?; rm -f "\$tmp"; exit \$rc
  fi
fi
exec "$real_age" "\$@"
EOF
# A zenity stub that answers the dialog with a fixed value.
printf '#!/usr/bin/env bash\necho "dialog-value"\n' > "$root/bin/zenity"
chmod +x "$root/bin/op" "$root/bin/age" "$root/bin/zenity"

fresh_store() { cp "$home/.dotfiles/secrets/values.age" "$root/wt/values.age"; rm -f "$root/local-secrets" "$root/op-called"; }
names() { age --decrypt -i "$root/key.txt" "$1" | cut -d= -f1 | sort | tr '\n' ' '; }
run_set() {  # run_set <env assignments...> -- <args...>
  local envs=()
  while [ "$1" != "--" ]; do envs+=("$1"); shift; done
  shift
  env HOME="$home" PATH="$root/bin:$PATH" XDG_RUNTIME_DIR="$root/run" RECIP="$recip" CACHE="$root/cache" \
    "${envs[@]}" bash "$SET" "$@" 2>&1
}

# 1. --values and --local write only their paths.
fresh_store
out=$(run_set -- NEW_ONE --value fresh --values "$root/wt/values.age" --local "$root/local-secrets")
assert_eq "$?" "0" "store with flags exits 0 ($out)"
assert_eq "$(names "$root/wt/values.age")" "KEEP_ONE KEEP_TWO NEW_ONE " "flagged store gains the name"
assert_eq "$(sha256sum "$home/.dotfiles/secrets/values.age" | cut -d' ' -f1)" "$main_sum" "main store is byte-identical"
assert_eq "$(grep -c '^export ' "$root/local-secrets" 2>/dev/null)" "3" "flagged local secrets written"
[ ! -e "$home/.local/secrets" ] || { echo "FAIL: the default local secrets path was written"; fail=1; }
[ ! -e "$root/op-called" ] || { echo "FAIL: the run reached 1Password"; fail=1; }

# 2. Two concurrent stores both survive, though each encrypt is slow enough to overlap.
fresh_store
run_set AGE_SLOW=1 -- ALPHA_ONE --value a --values "$root/wt/values.age" --local "$root/local-secrets" >/dev/null &
p1=$!
run_set AGE_SLOW=1 -- BRAVO_TWO --value b --values "$root/wt/values.age" --local "$root/local-secrets" >/dev/null &
p2=$!
wait "$p1"; r1=$?; wait "$p2"; r2=$?
assert_eq "$r1$r2" "00" "both concurrent stores exit 0"
assert_eq "$(names "$root/wt/values.age")" "ALPHA_ONE BRAVO_TWO KEEP_ONE KEEP_TWO " "both concurrent names survive"

# 3. A store that would drop a name fails and leaves the store alone.
fresh_store
before=$(sha256sum "$root/wt/values.age" | cut -d' ' -f1)
out=$(run_set AGE_DROP_FIRST=1 -- NEW_ONE --value fresh --values "$root/wt/values.age" --local "$root/local-secrets")
rc=$?
[ "$rc" -ne 0 ] || { echo "FAIL: a store that dropped a name exited 0"; fail=1; }
case "$out" in *"would drop"*) ;; *) echo "FAIL: dropping store failed for another reason: $out"; fail=1 ;; esac
assert_eq "$(sha256sum "$root/wt/values.age" | cut -d' ' -f1)" "$before" "dropping store leaves the file untouched"

# 4. --delete removes only its own name, and is the one allowed drop.
fresh_store
out=$(run_set -- KEEP_TWO --delete --values "$root/wt/values.age" --local "$root/local-secrets")
assert_eq "$?" "0" "delete exits 0 ($out)"
assert_eq "$(names "$root/wt/values.age")" "KEEP_ONE " "delete removes only its name"

# 5. secret-receive passes both flags through and checks the --local path.
fresh_store
out=$(env HOME="$home" PATH="$root/bin:$PATH" XDG_RUNTIME_DIR="$root/run" RECIP="$recip" CACHE="$root/cache" \
  bash "$RECEIVE" RECV_ONE --values "$root/wt/values.age" --local "$root/local-secrets" 2>&1)
assert_eq "$?" "0" "secret-receive with flags exits 0 ($out)"
assert_eq "$(names "$root/wt/values.age")" "KEEP_ONE KEEP_TWO RECV_ONE " "receive stores into the flagged store"
assert_eq "$(grep -c '^export RECV_ONE=' "$root/local-secrets" 2>/dev/null)" "1" "receive checks and finds the flagged local path"
[ ! -e "$home/.local/secrets" ] || { echo "FAIL: secret-receive wrote the default local secrets path"; fail=1; }

# 6. sync.sh --values and --local PATH write only their paths.
fresh_store
out=$(env HOME="$home" PATH="$root/bin:$PATH" XDG_RUNTIME_DIR="$root/run" CACHE="$root/cache" \
  bash "$SYNC" --values "$root/wt/values.age" --local "$root/local-secrets" 2>&1)
assert_eq "$?" "0" "sync with flags exits 0 ($out)"
assert_eq "$(grep -c '^export ' "$root/local-secrets" 2>/dev/null)" "2" "sync writes the flagged local path"
[ ! -e "$home/.local/secrets" ] || { echo "FAIL: sync wrote the default local secrets path"; fail=1; }
assert_eq "$(sha256sum "$home/.dotfiles/secrets/values.age" | cut -d' ' -f1)" "$main_sum" "main store untouched by sync"

assert_eq "$(mtime "$HOME/.local/secrets")" "$real_secrets_before" "real ~/.local/secrets mtime"
assert_eq "$(mtime "$real_cache")" "$real_cache_before" "real /dev/shm cache mtime"

exit "$fail"
