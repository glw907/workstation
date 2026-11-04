#!/usr/bin/env bash
# check-drift-proton.test.sh: prove `check-drift --proton-only` reports the pass-cli version brew
# holds, the host's age-key path and agent-token expiry, and whether Claude's own agent is there,
# from stub brew, ws-pass-key, and claude-pass commands. No real brew, keyring, or pass-cli is
# touched.
set -uo pipefail
cd "$(dirname "$0")/.." || exit 1
DRIFT="$(pwd)/bin/.local/bin/check-drift"
fail=0
root="$(mktemp -d)"
trap 'rm -rf "$root"' EXIT

assert_eq() { [ "$1" = "$2" ] || { echo "FAIL: $3: got '$1', want '$2'"; fail=1; }; }
assert_has() {  # assert_has <output> <fragment> <label>
  case "$1" in *"$2"*) ;; *) echo "FAIL: $3: no '$2' in: $1"; fail=1 ;; esac
}

printf '#!/usr/bin/env bash\n[ -n "${STUB_NO_BREW:-}" ] && exit 1\necho "proton-pass-cli 2.4.2"\n' > "$root/brew"
printf '#!/usr/bin/env bash\necho "$STUB_STATUS"\n' > "$root/ws-pass-key"
printf '#!/usr/bin/env bash\necho "${STUB_CLAUDE:-path=proton host=h}"\n' > "$root/claude-pass"
# pass-access stub: records the call, prints the capture file, and exits with STUB_ACCESS_RC.
printf '#!/usr/bin/env bash\necho call >> "%s"\ncat "$STUB_ACCESS"\nexit "${STUB_ACCESS_RC:-0}"\n' "$root/access.log" > "$root/pass-access"
chmod +x "$root/brew" "$root/ws-pass-key" "$root/claude-pass" "$root/pass-access"

# The grant map the cases read: the real map with every Claude row's expiry set to $1, so no case
# depends on today's date. Scripts rows keep "keyring". Prints the file's path.
MAP="$(pwd)/secrets/proton-grants.tsv"
CAPTURE="$(pwd)/tests/fixtures/pass-access-capture.tsv"
mkgrants() {
  awk -F'\t' -v OFS='\t' -v d="$1" 'NR > 1 && $1 ~ /-claude$/ { $4 = d } { print }' "$MAP" > "$root/grants.tsv"
  echo "$root/grants.tsv"
}
mkgrants 2999-01-01 >/dev/null

drift() {  # drift <STUB_STATUS> [env...]; prints output, then "rc=N"
  local status="$1"; shift
  local out rc
  out=$(env BREW="$root/brew" WS_PASS_KEY="$root/ws-pass-key" CLAUDE_PASS="$root/claude-pass" STUB_STATUS="$status" \
    PASS_ACCESS="$root/pass-access" STUB_ACCESS="$CAPTURE" PASS_GRANTS="$root/grants.tsv" WS_HOST=pavilion \
    "$@" bash "$DRIFT" --proton-only 2>&1)
  rc=$?
  printf '%s\nrc=%s' "$out" "$rc"
}

out=$(drift "path=proton host=h expires=2999-01-01 days=900")
assert_has "$out" "pass-cli: 2.4.2" "version line"
assert_has "$out" "age key path: Proton Pass agent token" "proton path line"
assert_has "$out" "agent token expires in 900 days" "expiry line"
assert_has "$out" "Claude's agent: token in the keyring" "claude agent line"
assert_has "$out" "rc=0" "healthy host exits 0"

out=$(drift "path=proton host=h expires=2999-01-01 days=900" STUB_CLAUDE="path=none host=h")
assert_has "$out" "Claude's agent: none on this host yet" "no claude agent line"
assert_has "$out" "rc=0" "a host with no claude agent is reported, not failed"

out=$(drift "path=none host=h")
assert_has "$out" "no agent token in the keyring" "no-token line"
assert_has "$out" "rc=1" "a host with no agent token fails"
assert_has "$out" "Claude's agent:" "the claude line still prints when the age-key path fails"

out=$(drift "path=proton host=h expires=2026-11-01 days=14")
assert_has "$out" "expires in 14 days (renew it)" "near-expiry warning"
assert_has "$out" "rc=0" "near expiry warns without failing"

out=$(drift "path=proton host=h expires=2026-10-01 days=-17")
assert_has "$out" "expired 17 days ago" "expired token line"
assert_has "$out" "rc=1" "an expired token fails"

out=$(drift "path=proton host=h expires=unknown")
assert_has "$out" "expiry unknown" "unknown expiry warning"

out=$(drift "path=proton host=h expires=2999-01-01 days=900" STUB_NO_BREW=1)
assert_has "$out" "proton-pass-cli is not installed" "missing package line"
assert_has "$out" "rc=1" "a missing package fails"

# The grant leg: this host's map rows against what pass-access sees. The capture is the live
# 2026-11-03 output of the branch's pass-access, trimmed to the five vaults the map names.
HEALTHY="path=proton host=h expires=2999-01-01 days=900"
: > "$root/access.log"
out=$(drift "$HEALTHY")
assert_has "$out" "grants match" "grant leg ok line"
assert_has "$out" "rc=0" "the live capture matches the map's pavilion rows"
assert_eq_calls() { [ "$(wc -l < "$root/access.log")" = "$1" ] || { echo "FAIL: $2: pass-access called $(wc -l < "$root/access.log") times, want $1"; fail=1; }; }
assert_eq_calls 1 "the grant leg signs in once"

sed '1d' "$CAPTURE" > "$root/short.tsv"
out=$(drift "$HEALTHY" STUB_ACCESS="$root/short.tsv")
assert_has "$out" "grant missing: pavilion-claude	ASC	editor" "a removed row names the row"
assert_has "$out" "rc=1" "a missing row fails"

{ cat "$CAPTURE"; printf 'pavilion-claude\tPrivate\teditor\n'; } > "$root/extra.tsv"
out=$(drift "$HEALTHY" STUB_ACCESS="$root/extra.tsv")
assert_has "$out" "grant extra: pavilion-claude	Private	editor" "an extra row names the row"
assert_has "$out" "rc=1" "an extra row fails"

sed 's/^\(pavilion-claude\tProjects\t\)editor/\1viewer/' "$CAPTURE" > "$root/role.tsv"
out=$(drift "$HEALTHY" STUB_ACCESS="$root/role.tsv")
assert_has "$out" "rc=1" "a row whose role differs fails"
assert_has "$out" "grant missing: pavilion-claude	Projects	editor" "the row the map expects is named"
assert_has "$out" "grant extra: pavilion-claude	Projects	viewer" "the row pass-access saw is named"

# An earlier leg's failure must not hide a matching grant leg.
out=$(drift "$HEALTHY" STUB_NO_BREW=1)
assert_has "$out" "grants match" "the ok line survives an earlier failure"

out=$(drift "$HEALTHY" PASS_GRANTS="$root/absent.tsv")
assert_has "$out" "no grant map" "a missing map is named"
assert_has "$out" "rc=1" "a missing map fails"
: > "$root/empty.tsv"
out=$(drift "$HEALTHY" PASS_GRANTS="$root/empty.tsv")
assert_has "$out" "rc=1" "an empty map fails"
printf 'agent\tvault\trole\texpires\n' > "$root/header.tsv"
out=$(drift "$HEALTHY" PASS_GRANTS="$root/header.tsv")
assert_has "$out" "rc=1" "a map with a header and no rows fails"

out=$(drift "$HEALTHY" STUB_ACCESS_RC=1)
assert_has "$out" "pass-access could not sign in" "a failed pass-access warns"
assert_has "$out" "rc=0" "a failed sign-in warns and does not fail"

: > "$root/access.log"
out=$(drift "$HEALTHY" PASS_ACCESS_SKIP=1)
assert_has "$out" "skipped" "PASS_ACCESS_SKIP warns that it skipped"
assert_has "$out" "rc=0" "a skipped grant leg exits 0"
assert_eq_calls 0 "PASS_ACCESS_SKIP signs in to nothing"

# The title lint: check-drift --titles reads each Claude vault's list through claude-pass, applies
# the naming rules, writes findings (mode 600) to a file, and prints only the count and the path.
# The stub serves $root/lists/<vault>.json; every title here is invented.
mkdir -p "$root/lists"
cat > "$root/claude-lists" <<'EOF'
#!/usr/bin/env bash
echo "$*" >> "$STUB_LIST_LOG"
[ "$1 $2" = "item list" ] || exit 2
v=""
while [ $# -gt 0 ]; do [ "$1" = --vault-name ] && v="$2"; shift; done
cat "$STUB_LISTS/$v.json"
EOF
chmod +x "$root/claude-lists"
for v in Infrastructure Projects ASC "Test accounts" "Age key"; do echo '{"items":[]}' > "$root/lists/$v.json"; done
echo '{"items":[{"title":"Fine Service"},{"title":"zbrand"}]}' > "$root/lists/Projects.json"
printf 'zbrand\n' > "$root/exceptions.txt"
titles() {  # titles [env...]; prints stdout then "rc=N"
  local out rc
  out=$(env CLAUDE_PASS="$root/claude-lists" STUB_LISTS="$root/lists" STUB_LIST_LOG="$root/list.log" \
    PASS_TITLE_EXCEPTIONS="$root/exceptions.txt" PASS_TITLE_FINDINGS="$root/findings.tsv" PASS_TITLE_GAP=0 \
    "$@" bash "$DRIFT" --titles 2>&1)
  rc=$?
  printf '%s\nrc=%s' "$out" "$rc"
}
: > "$root/list.log"
out=$(titles)
assert_has "$out" "no findings" "a clean list reports none"
assert_has "$out" "rc=0" "a clean list exits 0 (the exception-listed brand passes)"
[ "$(wc -l < "$root/list.log")" = 5 ] || { echo "FAIL: --titles did not read the five vaults: $(cat "$root/list.log")"; fail=1; }

echo '{"items":[{"title":"example.com"},{"title":"Login"},{"title":"gadget thing"},{"title":"Foo (a) (b)"},{"title":"Same"},{"title":"Same"},{"title":"Old","state":"Trashed"},{"title":"Old","state":"Active"}]}' > "$root/lists/Infrastructure.json"
out=$(titles)
assert_has "$out" "5 findings" "five rule breaks are counted (domain, generic, lowercase, qualifier, duplicate)"
assert_has "$out" "$root/findings.tsv" "the findings path is printed"
assert_has "$out" "rc=1" "findings exit 1"
case "$out" in *example.com*|*Same*|*gadget*|*Login*) echo "FAIL: a title reached stdout: $out"; fail=1 ;; esac
assert_eq "$(stat -c %a "$root/findings.tsv")" "600" "the findings file is mode 600"
grep -q "^Infrastructure	example.com	a domain" "$root/findings.tsv" || { echo "FAIL: the domain finding is missing from the file"; fail=1; }
grep -q "^Infrastructure	Same	same title twice" "$root/findings.tsv" || { echo "FAIL: the duplicate finding is missing from the file"; fail=1; }
assert_eq "$(wc -l < "$root/findings.tsv")" "5" "the file holds one line per finding (a duplicate title counts once)"

out=$(titles PASS_TITLE_EXCEPTIONS="$root/absent.txt")
assert_has "$out" "no exceptions file" "a missing exceptions file says so"

printf '#!/usr/bin/env bash\nexit 1\n' > "$root/claude-fail"; chmod +x "$root/claude-fail"
out=$(titles CLAUDE_PASS="$root/claude-fail")
assert_has "$out" "could not list" "a failed list is named"
assert_has "$out" "rc=1" "a failed list fails the run"

# The expiry warnings read every Claude row in the map, from dates relative to today.
d() { date -d "$1" +%F; }
out=$(drift "$HEALTHY" PASS_GRANTS="$(mkgrants "$(d '+31 days')")")
assert_has "$out" "pavilion-claude expires in 31 days" "31 days is ok"
assert_has "$out" "rc=0" "31 days exits 0"
case "$out" in *"(renew"*) echo "FAIL: 31 days warned: $out"; fail=1 ;; esac
out=$(drift "$HEALTHY" PASS_GRANTS="$(mkgrants "$(d '+30 days')")")
assert_has "$out" "pavilion-claude expires in 30 days (renew it)" "30 days warns"
assert_has "$out" "thinkpad-claude expires in 30 days (renew it)" "the other host's agent warns too"
assert_has "$out" "rc=0" "30 days exits 0"
out=$(drift "$HEALTHY" PASS_GRANTS="$(mkgrants "$(d today)")")
assert_has "$out" "expires in 0 days (renew it)" "0 days warns"
assert_has "$out" "rc=0" "0 days exits 0"
out=$(drift "$HEALTHY" PASS_GRANTS="$(mkgrants "$(d '-1 day')")")
assert_has "$out" "pavilion-claude expired 1 days ago" "1 day past fails"
assert_has "$out" "rc=1" "an expired agent exits 1"
out=$(drift "$HEALTHY" PASS_GRANTS="$(mkgrants 'soon')")
assert_has "$out" "malformed expires 'soon'" "a malformed expiry is named"
assert_has "$out" "rc=1" "a malformed expiry fails"
case "$out" in *"scripts expires"*|*"scripts expired"*|*"malformed expires 'keyring'"*) echo "FAIL: a keyring row was date-checked: $out"; fail=1 ;; esac

exit "$fail"
