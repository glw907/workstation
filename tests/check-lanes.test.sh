#!/usr/bin/env bash
# check-lanes.test.sh: prove scripts/check.sh selects legs by changed path and that
# scripts/gate.sh forwards --fresh and --scope-changed. No leg runs: every case uses --plan.
set -uo pipefail
cd "$(dirname "$0")/.." || exit 2
fail=0
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT

ok() { echo "ok: $1"; }
bad() { echo "FAIL: $1"; fail=1; }

# plan PATHS...: the leg list --changed --plan prints for the newline-joined paths.
plan() {
    local IFS=$'\n'
    CHECK_CHANGED_FILES="$*" bash scripts/check.sh --changed --plan 2>"$tmp/err"
}

all=$(bash scripts/check.sh --plan)
all_n=$(printf '%s\n' "$all" | wc -l)
always='gitleaks retired-names claude-refs tooling-sync-lint'

# A doc change selects fewer legs than the list and includes the always-run legs.
doc=$(plan claude/.claude/docs/bluefin-admin.md)
doc_n=$(printf '%s\n' "$doc" | wc -l)
[ "$doc_n" -lt "$all_n" ] && ok "a doc change selects fewer legs ($doc_n of $all_n)" || bad "a doc change selected $doc_n of $all_n legs"
for leg in $always; do
    printf '%s\n' "$doc" | grep -qx "$leg" || bad "a doc change dropped the always-run leg $leg"
done

# BACKLOG.md selects only the always-run legs.
backlog=$(plan BACKLOG.md | sort | tr '\n' ' ')
want=$(printf '%s\n' $always | sort | tr '\n' ' ')
[ "$backlog" = "$want" ] && ok "BACKLOG.md selects only the always-run legs" || bad "BACKLOG.md selected: $backlog"

# An empty set selects only those and says so.
empty=$(plan | sort | tr '\n' ' ')
[ "$empty" = "$want" ] && ok "an empty set selects only the always-run legs" || bad "an empty set selected: $empty"
grep -q 'no changed files' "$tmp/err" && ok "an empty set prints its line" || bad "an empty set printed no line"

# An unclaimed path selects every leg and names the path.
unclaimed=$(plan zz-unclaimed/file.txt)
[ "$unclaimed" = "$all" ] && ok "an unclaimed path selects every leg" || bad "an unclaimed path did not select every leg"
grep -q 'zz-unclaimed/file.txt' "$tmp/err" && ok "an unclaimed path is named" || bad "an unclaimed path was not named"

# A change to either runner script selects every leg.
for f in scripts/check.sh scripts/gate.sh; do
    [ "$(plan "$f")" = "$all" ] && ok "$f selects every leg" || bad "$f did not select every leg"
done

# A change to a bash script selects the shellcheck leg; a doc change does not.
script=$(plan tests/check-moves.test.sh)
printf '%s\n' "$script" | grep -qx shellcheck && ok "a bash script change selects the shellcheck leg" || bad "a bash script change skipped the shellcheck leg"
printf '%s\n' "$doc" | grep -qx shellcheck && bad "a doc change selected the shellcheck leg" || ok "a doc change skips the shellcheck leg"

# --leg twice selects both; an unknown name exits 2 and lists the names.
two=$(bash scripts/check.sh --plan --leg pass-count --leg check-moves | sort | tr '\n' ' ')
[ "$two" = "check-moves pass-count " ] && ok "--leg twice selects both" || bad "--leg twice selected: $two"
out=$(bash scripts/check.sh --leg bogus 2>&1)
rc=$?
[ "$rc" -eq 2 ] && printf '%s\n' "$out" | grep -qx 'pass-count' && ok "--leg bogus exits 2 and lists the legs" || bad "--leg bogus: rc=$rc"

# gate.sh forwards its flags to cairn-run-gate. A stub first on PATH prints its arguments.
mkdir -p "$tmp/bin"
cat > "$tmp/bin/cairn-run-gate" <<'EOF'
#!/usr/bin/env bash
echo "stub args: $*"
echo "gate exit: 0"
EOF
chmod +x "$tmp/bin/cairn-run-gate"
gate() { PATH="$tmp/bin:$PATH" bash scripts/gate.sh "$@" 2>&1; }

out=$(gate)
[ "$(printf '%s\n' "$out" | grep -c '^stub args: bash scripts/check.sh$')" -eq 1 ] && ok "gate.sh runs the whole gate string" || bad "gate.sh with no flag: $out"
out=$(gate --fresh)
printf '%s\n' "$out" | grep -qx 'stub args: --fresh bash scripts/check.sh' && ok "gate.sh --fresh passes --fresh" || bad "gate.sh --fresh: $out"
out=$(gate --scope-changed)
printf '%s\n' "$out" | grep -qx 'stub args: bash scripts/check.sh --changed' && ok "gate.sh --scope-changed passes the --changed string" || bad "gate.sh --scope-changed: $out"
for order in "--fresh --scope-changed" "--scope-changed --fresh"; do
    # shellcheck disable=SC2086 # the two flags are meant to split
    out=$(gate $order)
    printf '%s\n' "$out" | grep -qx 'stub args: --fresh bash scripts/check.sh --changed' && ok "gate.sh $order passes both" || bad "gate.sh $order: $out"
done
out=$(gate --bogus)
rc=$?
[ "$rc" -eq 2 ] && printf '%s\n' "$out" | grep -q 'usage: scripts/gate.sh \[--fresh\] \[--scope-changed\]' && ok "gate.sh --bogus exits 2" || bad "gate.sh --bogus: rc=$rc"

exit "$fail"
