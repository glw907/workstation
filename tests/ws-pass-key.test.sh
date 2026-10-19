#!/usr/bin/env bash
# ws-pass-key.test.sh: prove ws-pass-key reads the age key through the host's Proton agent token
# with a reason, in an isolated session directory that is gone afterward; refuses when the keyring
# holds no token; fails loudly when a token is present but bad; and that secret-set.sh and
# sync.sh get their key through it. Every run uses the fake pass-cli (tests/fixtures/pass-cli),
# stub secret-tool and zenity, a scratch store, and a scratch XDG_RUNTIME_DIR. The real
# pass-cli, keyring, and /dev/shm key cache are never touched.
set -uo pipefail
cd "$(dirname "$0")/.." || exit 1
repo="$(pwd)"
KEY_HELPER="$repo/bin/.local/bin/ws-pass-key"
SET="$repo/scripts/secrets/secret-set.sh"
SYNC="$repo/scripts/secrets/sync.sh"
fail=0
root="$(mktemp -d)"
trap 'rm -rf "$root"' EXIT

assert_eq() {
  [ "$1" = "$2" ] || { echo "FAIL: $3: got '$1', want '$2'"; fail=1; }
}

real_cache="/dev/shm/.age-key-$(id -u)"
mtime() { stat -c %Y "$1" 2>/dev/null || echo absent; }
real_cache_before=$(mtime "$real_cache")

mkdir -p "$root/bin" "$root/run" "$root/vault/Workstation/age" "$root/home/.local"
cp "$repo/tests/fixtures/pass-cli" "$root/bin/pass-cli"
age-keygen -o "$root/key.txt" 2>/dev/null
recip=$(age-keygen -y "$root/key.txt")
cp "$root/key.txt" "$root/vault/Workstation/age/key"
TOKEN='pst_fake::KEY'

# secret-tool stub: lookup prints the token (or the expiry) file when present; store saves stdin.
cat > "$root/bin/secret-tool" <<EOF
#!/usr/bin/env bash
echo "\$*" >> "$root/secret-tool.log"
case "\$1" in
  lookup) case "\$*" in
            *proton-pass-agent-expiry*) f="$root/expiry" ;;
            *) f="$root/token" ;;
          esac
          [ -s "\$f" ] && cat "\$f" || exit 1 ;;
  store)  case "\$*" in
            *proton-pass-agent-expiry*) cat > "$root/expiry" ;;
            *) cat > "$root/token" ;;
          esac ;;
esac
EOF
# zenity stub: answers the token dialog.
printf '#!/usr/bin/env bash\necho "%s"\n' "$TOKEN" > "$root/bin/zenity"
chmod +x "$root/bin/"*

reset() { rm -f "$root/cache" "$root/pass.log" "$root/token" "$root/expiry" "$root/secret-tool.log"; rm -rf "$root"/run/pass-ws.*; }
sessions_left() { ls -d "$root"/run/pass-ws.* 2>/dev/null | wc -l; }
helper() {  # helper <args...>; env: WS_HOST, CACHE point at the scratch
  env HOME="$root/home" PATH="$root/bin:$PATH" XDG_RUNTIME_DIR="$root/run" WS_HOST=testhost \
    CACHE="$root/cache" FAKE_PASS_LOG="$root/pass.log" FAKE_PASS_FIXTURE="$root/vault" \
    WS_PASS_ITEM=age WS_PASS_CALLER=test-suite bash "$KEY_HELPER" "$@" 2>&1
}
pass_calls() { [ -f "$root/pass.log" ] && wc -l < "$root/pass.log" || echo 0; }

# 1. A token in the keyring: the key lands in the cache through pass-cli, with a reason.
reset; echo "$TOKEN" > "$root/token"
out=$(helper)
assert_eq "$?" "0" "token path exits 0 ($out)"
assert_eq "$(cat "$root/cache" 2>/dev/null)" "$(cat "$root/key.txt")" "cache holds the vault's key"
assert_eq "$(stat -c %a "$root/cache" 2>/dev/null)" "600" "cache is mode 600"
grep -q 'reason=test-suite: read age key on testhost' "$root/pass.log" || { echo "FAIL: the read carries no reason naming script and host"; fail=1; }
grep -q 'item view pass://Workstation/age/key' "$root/pass.log" || { echo "FAIL: the read did not use a pass:// reference"; fail=1; }
assert_eq "$(grep -c "session=$root/run/pass-ws\.[A-Za-z0-9]* " "$root/pass.log")" "$(pass_calls)" "every call used a per-run session directory under XDG_RUNTIME_DIR"
grep -q "$TOKEN" "$root/pass.log" && { echo "FAIL: the token leaked into a recorded argument"; fail=1; }
case "$out" in *"$TOKEN"*) echo "FAIL: the token leaked into the helper's output"; fail=1 ;; esac
assert_eq "$(sessions_left)" "0" "the session directory is removed"
grep -q 'logout' "$root/pass.log" || { echo "FAIL: the helper never logged out"; fail=1; }

# 2. A cached key needs no pass-cli call at all.
before=$(pass_calls)
out=$(helper)
assert_eq "$?" "0" "cached run exits 0"
assert_eq "$(pass_calls)" "$before" "cached run makes no pass-cli call"

# 3. No token in the keyring: the helper refuses, says how to store one, and leaves no cache.
reset
out=$(helper)
rc=$?
[ "$rc" -ne 0 ] || { echo "FAIL: the no-token path exited 0"; fail=1; }
case "$out" in *"no agent token"*"--store"*) ;; *) echo "FAIL: the no-token path did not say so: $out"; fail=1 ;; esac
[ ! -s "$root/cache" ] || { echo "FAIL: the no-token path left a cache"; fail=1; }
assert_eq "$(pass_calls)" "0" "no-token path makes no pass-cli call"

# 4. A token that is present but bad fails loudly and leaves no cache.
reset; echo "pst_wrong::KEY" > "$root/token"
out=$(helper)
rc=$?
[ "$rc" -ne 0 ] || { echo "FAIL: a bad token exited 0"; fail=1; }
[ ! -s "$root/cache" ] || { echo "FAIL: a bad token left a cache"; fail=1; }
case "$out" in *"login failed"*) ;; *) echo "FAIL: a bad token did not say the login failed: $out"; fail=1 ;; esac
assert_eq "$(sessions_left)" "0" "a bad token leaves no session directory"
grep -q 'logout' "$root/pass.log" || { echo "FAIL: a bad token skipped the logout"; fail=1; }

# 5. A good token but a missing vault item also fails loudly.
reset; echo "$TOKEN" > "$root/token"
out=$(env WS_PASS_ITEM=age WS_PASS_VAULT=Nowhere HOME="$root/home" PATH="$root/bin:$PATH" XDG_RUNTIME_DIR="$root/run" WS_HOST=testhost \
  CACHE="$root/cache" FAKE_PASS_LOG="$root/pass.log" FAKE_PASS_FIXTURE="$root/vault" bash "$KEY_HELPER" 2>&1)
rc=$?
[ "$rc" -ne 0 ] || { echo "FAIL: a missing item exited 0"; fail=1; }
[ ! -s "$root/cache" ] || { echo "FAIL: a missing item left a cache"; fail=1; }
assert_eq "$(sessions_left)" "0" "a missing item leaves no session directory"

# 5b. A stale session planted by an earlier run is never reused: the helper always logs in.
reset; echo "$TOKEN" > "$root/token"
mkdir -p "$root/run/pass-ws.planted"; echo agent > "$root/run/pass-ws.planted/session"
out=$(helper)
grep -q '^login' "$root/pass.log" || { echo "FAIL: the helper skipped its own login"; fail=1; }

# 5c. No XDG_RUNTIME_DIR means no tmpfs for a session, so the token path refuses to run.
reset; echo "$TOKEN" > "$root/token"
out=$(env -u XDG_RUNTIME_DIR HOME="$root/home" PATH="$root/bin:$PATH" WS_HOST=testhost CACHE="$root/cache" \
  FAKE_PASS_LOG="$root/pass.log" bash "$KEY_HELPER" 2>&1)
[ "$?" -ne 0 ] || { echo "FAIL: a missing XDG_RUNTIME_DIR exited 0"; fail=1; }
[ ! -s "$root/cache" ] || { echo "FAIL: a missing XDG_RUNTIME_DIR left a cache"; fail=1; }

# 6. --status names the path and the expiry without printing the token.
reset; echo "$TOKEN" > "$root/token"; echo "2027-01-15" > "$root/expiry"
out=$(helper --status)
case "$out" in *"path=proton"*"expires=2027-01-15"*) ;; *) echo "FAIL: --status with a token: $out"; fail=1 ;; esac
case "$out" in *"$TOKEN"*) echo "FAIL: --status printed the token"; fail=1 ;; esac
reset
out=$(helper --status)
case "$out" in *"path=none"*) ;; *) echo "FAIL: --status without a token: $out"; fail=1 ;; esac

# 7. --store reads the token from the dialog into the keyring, with an expiry three months out.
reset
out=$(helper --store)
assert_eq "$?" "0" "--store exits 0 ($out)"
assert_eq "$(cat "$root/token" 2>/dev/null)" "$TOKEN" "--store saved the dialog's token"
assert_eq "$(cat "$root/expiry" 2>/dev/null)" "$(date -d '+3 months' +%F)" "--store recorded the expiry"
case "$out" in *"$TOKEN"*) echo "FAIL: --store echoed the token"; fail=1 ;; esac

# 8. secret-set.sh and sync.sh fetch the key through the helper on a cache miss.
home="$root/set-home"
mkdir -p "$home/.dotfiles/secrets" "$home/.local"
printf 'KEEP_ONE=alpha\n' > "$root/plain"
age -r "$recip" -o "$root/values.age" "$root/plain"
reset; echo "$TOKEN" > "$root/token"
export_env=(WS_PASS_ITEM=age HOME="$home" PATH="$root/bin:$PATH" XDG_RUNTIME_DIR="$root/run" WS_HOST=testhost CACHE="$root/cache"
  FAKE_PASS_LOG="$root/pass.log" FAKE_PASS_FIXTURE="$root/vault")
out=$(env "${export_env[@]}" RECIP="$recip" bash "$SET" NEW_ONE --value fresh --values "$root/values.age" --local "$root/local" 2>&1)
assert_eq "$?" "0" "secret-set.sh on the token path exits 0 ($out)"
assert_eq "$(age --decrypt -i "$root/key.txt" "$root/values.age" | cut -d= -f1 | sort | tr '\n' ' ')" "KEEP_ONE NEW_ONE " "secret-set.sh stored through the helper's key"
grep -q 'reason=secret-set.sh: read age key on testhost' "$root/pass.log" || { echo "FAIL: secret-set.sh's reason does not name it: $(cat "$root/pass.log")"; fail=1; }
rm -f "$root/cache" "$root/pass.log" "$root/local"
out=$(env "${export_env[@]}" bash "$SYNC" --values "$root/values.age" --local "$root/local" 2>&1)
assert_eq "$?" "0" "sync.sh on the token path exits 0 ($out)"
grep -q 'reason=sync.sh: read age key on testhost' "$root/pass.log" || { echo "FAIL: sync.sh's reason does not name it"; fail=1; }

assert_eq "$(mtime "$real_cache")" "$real_cache_before" "real /dev/shm cache mtime"
exit "$fail"
