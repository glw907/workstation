#!/usr/bin/env bash
# secret-receive-pass.test.sh: prove `secret-receive --pass REF` logs in to a throwaway tmpfs
# session, reads REF, stores it, and logs out and removes the session on every exit; and that
# claude-sudo-setup takes the sudo password from a zenity dialog. Every run uses the fake
# pass-cli (tests/fixtures/pass-cli), stub zenity, a scratch store, and a scratch cache path. The
# real pass-cli and /dev/shm sudo cache are never touched.
set -uo pipefail
cd "$(dirname "$0")/.." || exit 1
repo="$(pwd)"
RECEIVE="$repo/bin/.local/bin/secret-receive"
SUDO_SETUP="$repo/bin/.local/bin/claude-sudo-setup"
fail=0
root="$(mktemp -d)"
trap 'rm -rf "$root"' EXIT

assert_eq() {
  [ "$1" = "$2" ] || { echo "FAIL: $3: got '$1', want '$2'"; fail=1; }
}

real_sudo="/dev/shm/claude-sudo-$(id -u)"
mtime() { stat -c %Y "$1" 2>/dev/null || echo absent; }
real_sudo_before=$(mtime "$real_sudo")

home="$root/home"
mkdir -p "$home/.dotfiles/secrets" "$home/.dotfiles/scripts" "$home/.local" "$root/bin" "$root/run" "$root/vault/Personal/Item"
ln -s "$repo/scripts/secrets" "$home/.dotfiles/scripts/secrets"
age-keygen -o "$root/key.txt" 2>/dev/null
recip=$(age-keygen -y "$root/key.txt")
printf 'KEEP_ONE=alpha\n' > "$root/plain"
age -r "$recip" -o "$root/values.age" "$root/plain"
cp "$root/key.txt" "$root/cache"
chmod 600 "$root/cache"
printf 'pulled-from-proton' > "$root/vault/Personal/Item/password"

cp "$repo/tests/fixtures/pass-cli" "$root/bin/pass-cli"
printf '#!/usr/bin/env bash\necho "$*" >> "%s/zenity.log"\ncat "%s/dialog" 2>/dev/null || exit 1\n' "$root" "$root" > "$root/bin/zenity"
chmod +x "$root/bin/"*

recv() {  # recv <args...>
  env HOME="$home" PATH="$root/bin:$PATH" XDG_RUNTIME_DIR="$root/run" RECIP="$recip" CACHE="$root/cache" \
    FAKE_PASS_LOG="$root/pass.log" FAKE_PASS_FIXTURE="$root/vault" "$@" 2>&1
}
stored() { age --decrypt -i "$root/key.txt" "$root/values.age" | grep -c "^$1=pulled-from-proton\$"; }
reset() { cp "$root/values.age" "$root/values.bak" 2>/dev/null; rm -f "$root/pass.log" "$root/local"; rm -rf "$root/run/pass-recv."*; }

# 1. --pass logs in on the web, reads the reference, stores the value, and leaves no session.
reset
out=$(recv bash "$RECEIVE" PULLED_ONE --pass pass://Personal/Item/password --values "$root/values.age" --local "$root/local")
assert_eq "$?" "0" "--pass exits 0 ($out)"
assert_eq "$(stored PULLED_ONE)" "1" "--pass stored the value read from the vault"
grep -q '^login | session=' "$root/pass.log" || { echo "FAIL: no web login recorded"; fail=1; }
grep -q 'login | .* token=none' "$root/pass.log" || { echo "FAIL: --pass logged in with a token, not the web flow"; fail=1; }
grep -q 'item view pass://Personal/Item/password' "$root/pass.log" || { echo "FAIL: --pass did not read the reference"; fail=1; }
grep -q '^logout' "$root/pass.log" || { echo "FAIL: --pass never logged out"; fail=1; }
assert_eq "$(grep -vc "session=$root/run/pass-recv\." "$root/pass.log")" "0" "every call used a throwaway session under XDG_RUNTIME_DIR"
assert_eq "$(ls -d "$root/run/pass-recv."* 2>/dev/null | wc -l)" "0" "the throwaway session directory is removed"
case "$out" in *pulled-from-proton*) echo "FAIL: --pass printed the value"; fail=1 ;; esac

# 2. A failed login stores nothing, says so, and still removes the session directory.
reset
out=$(recv FAKE_PASS_WEB_FAIL=1 bash "$RECEIVE" FAILED_ONE --pass pass://Personal/Item/password --values "$root/values.age" --local "$root/local")
rc=$?
[ "$rc" -ne 0 ] || { echo "FAIL: a failed login exited 0"; fail=1; }
assert_eq "$(age --decrypt -i "$root/key.txt" "$root/values.age" | grep -c '^FAILED_ONE=')" "0" "a failed login stores nothing"
assert_eq "$(ls -d "$root/run/pass-recv."* 2>/dev/null | wc -l)" "0" "a failed login leaves no session directory"

# 3. A reference that does not resolve stores nothing and logs out.
reset
out=$(recv bash "$RECEIVE" MISSING_ONE --pass pass://Personal/Nothing/password --values "$root/values.age" --local "$root/local")
rc=$?
[ "$rc" -ne 0 ] || { echo "FAIL: a missing reference exited 0"; fail=1; }
grep -q '^logout' "$root/pass.log" || { echo "FAIL: a missing reference skipped the logout"; fail=1; }
assert_eq "$(age --decrypt -i "$root/key.txt" "$root/values.age" | grep -c '^MISSING_ONE=')" "0" "a missing reference stores nothing"

# 4. The retired --op mode is refused as an unknown option.
reset
out=$(recv bash "$RECEIVE" OP_ONE --op op://a/b/c --values "$root/values.age" --local "$root/local")
rc=$?
[ "$rc" -ne 0 ] || { echo "FAIL: --op exited 0"; fail=1; }

# 5. claude-sudo-setup caches the dialog's password, mode 600.
printf 'hunter2-sudo' > "$root/dialog"
out=$(env HOME="$home" PATH="$root/bin:$PATH" XDG_RUNTIME_DIR="$root/run" CLAUDE_SUDO_CACHE="$root/run/sudo-cache" bash "$SUDO_SETUP" 2>&1)
assert_eq "$?" "0" "claude-sudo-setup exits 0 ($out)"
assert_eq "$(cat "$root/run/sudo-cache" 2>/dev/null)" "hunter2-sudo" "the dialog's password is cached"
assert_eq "$(stat -c %a "$root/run/sudo-cache" 2>/dev/null)" "600" "the sudo cache is mode 600"
grep -q -- '--hide-text' "$root/zenity.log" || { echo "FAIL: the sudo dialog does not hide its text"; fail=1; }
out2=$(env HOME="$home" PATH="$root/bin:$PATH" XDG_RUNTIME_DIR="$root/run" CLAUDE_SUDO_CACHE="$root/disk-cache" bash "$SUDO_SETUP" 2>&1)
[ "$?" -ne 0 ] || { echo "FAIL: a cache path off tmpfs exited 0"; fail=1; }
[ ! -e "$root/disk-cache" ] || { echo "FAIL: the password was cached off tmpfs"; fail=1; }
case "$out" in *hunter2-sudo*) echo "FAIL: claude-sudo-setup printed the password"; fail=1 ;; esac

# 6. A cancelled or empty dialog caches nothing and fails, leaving an earlier cache alone.
rm -f "$root/dialog"
out=$(env HOME="$home" PATH="$root/bin:$PATH" XDG_RUNTIME_DIR="$root/run" CLAUDE_SUDO_CACHE="$root/run/sudo-cache" bash "$SUDO_SETUP" 2>&1)
rc=$?
[ "$rc" -ne 0 ] || { echo "FAIL: a cancelled dialog exited 0"; fail=1; }
assert_eq "$(cat "$root/run/sudo-cache" 2>/dev/null)" "hunter2-sudo" "a cancelled dialog leaves the earlier cache alone"
: > "$root/dialog"
out=$(env HOME="$home" PATH="$root/bin:$PATH" XDG_RUNTIME_DIR="$root/run" CLAUDE_SUDO_CACHE="$root/run/sudo-cache" bash "$SUDO_SETUP" 2>&1)
[ "$?" -ne 0 ] || { echo "FAIL: an empty dialog exited 0"; fail=1; }

assert_eq "$(mtime "$real_sudo")" "$real_sudo_before" "real /dev/shm sudo cache mtime"
exit "$fail"
