#!/usr/bin/env bash
# check-moves.test.sh: prove the draft check in scripts/check-moves.sh against a fixture source
# repo and a fixture destination tree. A clean move passes. An edited moved file, a missing
# destination, an edited code row, and a destination that differs from the source each fail.
set -uo pipefail
cd "$(dirname "$0")/.."
SCRIPT="$(pwd)/scripts/check-moves.sh"
fail=0
root="$(mktemp -d)"
trap 'rm -rf "$root"' EXIT

assert_eq() {
  [ "$1" = "$2" ] || { echo "FAIL: $3: got '$1', want '$2'"; fail=1; }
}

src="$root/src"
dest="$root/dest"
git init -q "$src"
mkdir -p "$src/docs/superpowers" "$src/code" "$dest/other/docs/superpowers" "$dest/other/code"
printf 'spec body\nsee docs/superpowers/plan.md\n' > "$src/docs/superpowers/spec.md"
printf 'plan body\n' > "$src/docs/superpowers/plan.md"
printf 'tool body\n' > "$src/code/tool"
printf 'stays\n' > "$src/docs/superpowers/keep.md"
git -C "$src" add -A
git -C "$src" -c user.email=t@t -c user.name=t commit -q -m pin
pin=$(git -C "$src" rev-parse HEAD)
cp "$src/docs/superpowers/spec.md" "$dest/other/docs/superpowers/spec.md"
cp "$src/docs/superpowers/plan.md" "$dest/other/docs/superpowers/plan.md"
printf 'tool body, rewritten\n' > "$dest/other/code/tool"

map="$root/map.tsv"
{
  printf 'source_repo\told_path\tnew_repo\tnew_path\tinitiative\tstate\tpin\n'
  printf 'src\tdocs/superpowers/spec.md\tother\tdocs/superpowers/spec.md\t\tmoved\t%s\n' "$pin"
  printf 'src\tdocs/superpowers/plan.md\tother\tdocs/superpowers/plan.md\t\tcollision-identical\t%s\n' "$pin"
  printf 'src\tcode/tool\tother\tcode/tool\t\thistory\t%s\n' "$pin"
  printf 'src\tdocs/superpowers/keep.md\tsrc\t\t\tstays\t%s\n' "$pin"
  printf 'src\tdocs/superpowers/later.md\tother\t\t\tdeferred:p5\t%s\n' "$pin"
} > "$map"

run() {
  out=$(bash "$SCRIPT" --map "$map" --repo "$src" --head HEAD --dest-root "$dest" 2>&1)
  rc=$?
}

run
assert_eq "$rc" "0" "clean move passes ($out)"
case "$out" in *"checked 3 of 3"*) ;; *) echo "FAIL: clean move: row count line missing: $out"; fail=1 ;; esac

printf 'edited later\n' >> "$src/docs/superpowers/spec.md"
git -C "$src" -c user.email=t@t -c user.name=t commit -q -am "edit a moved file"
run
assert_eq "$rc" "1" "an edited moved file fails"
case "$out" in *"source edited after the pin: docs/superpowers/spec.md"*) ;; *) echo "FAIL: edited moved file not named: $out"; fail=1 ;; esac
git -C "$src" reset -q --hard "$pin"

rm "$dest/other/docs/superpowers/plan.md"
run
assert_eq "$rc" "1" "a missing destination fails"
case "$out" in *"missing destination: docs/superpowers/plan.md"*) ;; *) echo "FAIL: missing destination not named: $out"; fail=1 ;; esac
cp "$src/docs/superpowers/plan.md" "$dest/other/docs/superpowers/plan.md"

printf 'tool body edited later\n' > "$src/code/tool"
git -C "$src" -c user.email=t@t -c user.name=t commit -q -am "edit a code row"
run
assert_eq "$rc" "1" "an edited code row fails"
case "$out" in *"source edited after the pin: code/tool"*) ;; *) echo "FAIL: edited code row not named: $out"; fail=1 ;; esac
git -C "$src" reset -q --hard "$pin"

printf 'spec body\nsee other/docs/superpowers/plan.md\n' > "$dest/other/docs/superpowers/spec.md"
run
assert_eq "$rc" "0" "a destination that differs only in a rewritten reference passes ($out)"
case "$out" in *"1 files differ only in rewritten references"*) ;; *) echo "FAIL: rewrite not counted: $out"; fail=1 ;; esac

printf 'different\n' > "$dest/other/docs/superpowers/spec.md"
run
assert_eq "$rc" "1" "a destination that differs from the source fails"
case "$out" in *"destination differs from the source at the pin: docs/superpowers/spec.md"*) ;; *) echo "FAIL: differing destination not named: $out"; fail=1 ;; esac

exit "$fail"
