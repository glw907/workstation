#!/usr/bin/env bash
# pass-count.test.sh: prove pass-count prints per-vault, per-category counts and, in --hashes mode,
# one SHA-256 per item of Servers emergency, without ever printing an item's value; and that it
# logs in to a throwaway session that is gone afterward. Runs against the fake pass-cli
# (tests/fixtures/pass-cli) and fixture JSON only.
set -uo pipefail
cd "$(dirname "$0")/.." || exit 1
COUNT="$(pwd)/bin/.local/bin/pass-count"
fail=0
root="$(mktemp -d)"
trap 'rm -rf "$root"' EXIT

assert_eq() {
  [ "$1" = "$2" ] || { echo "FAIL: $3: got '$1', want '$2'"; fail=1; }
}

mkdir -p "$root/bin" "$root/run" "$root/vault"
cp "$(pwd)/tests/fixtures/pass-cli" "$root/bin/pass-cli"

cat > "$root/vault/_vaults.json" <<'EOF'
{"vaults":[{"name":"Personal","share_id":"sh1"},{"name":"Servers emergency","share_id":"sh2"}]}
EOF
cat > "$root/vault/_items-sh1.json" <<'EOF'
{"items":[
 {"id":"a","content":{"title":"One","content":{"Login":{"password":"p-one"}}}},
 {"id":"b","content":{"title":"Two","content":{"Login":{"password":"p-two"}}}},
 {"id":"c","content":{"title":"Three","content":{"Note":null}}},
 {"id":"d","content":{"title":"Four","content":{"Alias":null}}}
]}
EOF
cat > "$root/vault/_items-sh2.json" <<'EOF'
{"items":[
 {"id":"e","content":{"title":"restic media","content":{"Login":{"password":"hush-media"}}}},
 {"id":"f","content":{"title":"stalwart admin","content":{"Login":{"password":"hush-admin"}}}}
]}
EOF

run() {  # run <args...>
  env PATH="$root/bin:$PATH" XDG_RUNTIME_DIR="$root/run" HOME="$root" FAKE_PASS_LOG="$root/pass.log" \
    FAKE_PASS_FIXTURE="$root/vault" bash "$COUNT" "$@" 2>&1
}

out=$(run)
assert_eq "$?" "0" "counts exit 0 ($out)"
case "$out" in *"Personal"*"Login"*"2"*) ;; *) echo "FAIL: Personal logins not counted: $out"; fail=1 ;; esac
assert_eq "$(grep -c 'Personal	Login	2$' <<< "$out")" "1" "Personal has 2 logins"
assert_eq "$(grep -c 'Personal	Note	1$' <<< "$out")" "1" "Personal has 1 note"
assert_eq "$(grep -c 'Personal	Alias	1$' <<< "$out")" "1" "Personal has 1 alias"
assert_eq "$(grep -c 'Servers emergency	Login	2$' <<< "$out")" "1" "Servers emergency has 2 logins"
case "$out" in *p-one*|*hush-*) echo "FAIL: counts printed an item value"; fail=1 ;; esac
assert_eq "$(ls -d "$root/run/pass-count."* 2>/dev/null | wc -l)" "0" "the throwaway session is removed"
grep -q '^logout' "$root/pass.log" || { echo "FAIL: no logout"; fail=1; }
assert_eq "$(grep -vc "session=$root/run/pass-count\." "$root/pass.log")" "0" "every call used the throwaway session"

# --hashes prints one title<TAB>sha256 line per Servers emergency item, and never the value.
out=$(run --hashes)
assert_eq "$?" "0" "--hashes exit 0 ($out)"
want_media=$(printf '%s' 'hush-media' | sha256sum | cut -d' ' -f1)
want_admin=$(printf '%s' 'hush-admin' | sha256sum | cut -d' ' -f1)
assert_eq "$(grep -c "^restic media	$want_media\$" <<< "$out")" "1" "restic media hash"
assert_eq "$(grep -c "^stalwart admin	$want_admin\$" <<< "$out")" "1" "stalwart admin hash"
assert_eq "$(grep -vc "^pass-count:" <<< "$out")" "2" "one line per item"
case "$out" in *hush-*) echo "FAIL: --hashes printed a value"; fail=1 ;; esac

# A vault the script cannot parse fails loudly instead of printing zero counts.
echo 'not json' > "$root/vault/_items-sh1.json"
out=$(run)
[ "$?" -ne 0 ] || { echo "FAIL: unparseable list exited 0"; fail=1; }

exit "$fail"
