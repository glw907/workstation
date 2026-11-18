#!/usr/bin/env bash
# check-drift-pins.test.sh: prove `check-drift --pins-only` passes a host with no pinned formulae
# or with every pin current, and fails one line per pinned formula that is behind, from a stub
# brew. No real brew is touched.
set -uo pipefail
cd "$(dirname "$0")/.." || exit 1
DRIFT="$(pwd)/bin/.local/bin/check-drift"
fail=0
root="$(mktemp -d)"
trap 'rm -rf "$root"' EXIT

assert_has() {  # assert_has <output> <fragment> <label>
  case "$1" in *"$2"*) ;; *) echo "FAIL: $3: no '$2' in: $1"; fail=1 ;; esac
}
assert_lacks() {  # assert_lacks <output> <fragment> <label>
  case "$1" in *"$2"*) echo "FAIL: $3: found '$2' in: $1"; fail=1 ;; esac
}

# The stub answers the two calls the leg makes and fails any other, so a new call shows up here.
cat > "$root/brew" <<'STUB'
#!/usr/bin/env bash
case "$*" in
  "list --pinned") printf '%s' "${STUB_PINNED:-}" ;;
  "outdated --verbose") printf '%s' "${STUB_OUTDATED:-}" ;;
  *) echo "stub brew: unexpected call: $*" >&2; exit 64 ;;
esac
STUB
chmod +x "$root/brew"

drift() {  # drift [env...]; prints output, then "rc=N"
  local out rc
  out=$(env BREW="$root/brew" "$@" bash "$DRIFT" --pins-only 2>&1)
  rc=$?
  printf '%s\nrc=%s' "$out" "$rc"
}

out=$(drift)
assert_has "$out" "no pinned formulae" "no pins line"
assert_has "$out" "rc=0" "a host with no pins exits 0"

out=$(drift STUB_PINNED=$'libxml2\nproton-pass-cli\n')
assert_has "$out" "pinned formulae current: libxml2 proton-pass-cli" "current pins line"
assert_has "$out" "rc=0" "current pins exit 0"

# An outdated formula that is not pinned is `ujust update`'s business and never fails the leg.
out=$(drift STUB_PINNED=$'libxml2\nproton-pass-cli\n' STUB_OUTDATED=$'mise (2026.11.1) < 2026.11.4\n')
assert_has "$out" "pinned formulae current" "an unpinned outdated formula is ignored"
assert_lacks "$out" "mise" "the unpinned formula is not named"
assert_has "$out" "rc=0" "an unpinned outdated formula exits 0"

out=$(drift STUB_PINNED=$'libxml2\nproton-pass-cli\n' \
  STUB_OUTDATED=$'mise (2026.11.1) < 2026.11.4\nproton-pass-cli (2.7.0) < 2.7.1 [pinned at 2.7.0]\n')
assert_has "$out" "x pinned formula behind: proton-pass-cli (2.7.0) < 2.7.1 (brew unpin" "behind line"
assert_lacks "$out" "mise" "only the pinned formula is named"
assert_has "$out" "rc=1" "a pin behind fails"

out=$(drift STUB_PINNED=$'libxml2\nproton-pass-cli\n' \
  STUB_OUTDATED=$'libxml2 (2.15.4) < 2.15.5 [pinned at 2.15.4]\nproton-pass-cli (2.7.0) < 2.7.1 [pinned at 2.7.0]\n')
assert_has "$out" "behind: libxml2 (2.15.4) < 2.15.5" "first of two behind"
assert_has "$out" "behind: proton-pass-cli (2.7.0) < 2.7.1" "second of two behind"
assert_has "$out" "rc=1" "two pins behind fail"

exit "$fail"
