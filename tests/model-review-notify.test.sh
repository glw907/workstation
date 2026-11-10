#!/usr/bin/env bash
# model-review-notify.test.sh: prove the monthly launcher's gates with stubbed tools on PATH.
# The wrong host, a pull that keeps failing, and an existing month branch each stop before any
# claude call. The normal path reaches the /goal session and the two follow-on launchers.
set -uo pipefail
cd "$(dirname "$0")/.." || exit 1
SCRIPT="$(pwd)/bin/.local/bin/model-review-notify"
fail=0

assert_eq() {
  [ "$1" = "$2" ] || { echo "FAIL: $3: got '$1', want '$2'"; fail=1; }
}

tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
# The launcher puts $HOME/.local/bin first on PATH, so the stubs live there.
bindir="$tmp/home/.local/bin"
mkdir -p "$bindir" "$tmp/standards/.claude/worktrees/model-review-audit"

# Each stub appends its name and arguments to $STUB_LOG and answers from the STUB_* variables.
stub() {
  printf '#!/usr/bin/env bash\n%s\n' "$2" > "$bindir/$1"
  chmod +x "$bindir/$1"
}
stub hostname 'echo "${STUB_HOST:-pavilion}"'
stub git 'echo "git $*" >> "$STUB_LOG"
case " $* " in
  *" pull "*) exit "${STUB_PULL_RC:-0}" ;;
  *" ls-remote "*) exit "${STUB_LS_RC:-2}" ;;
  *" fetch "*) exit "${STUB_FETCH_RC:-0}" ;;
esac
exit 0'
stub claude 'echo "claude $*" >> "$STUB_LOG"; echo "stub report"'
stub notify-send 'echo "notify-send $*" >> "$STUB_LOG"'
stub survey-writing-review 'echo "survey-writing-review $*" >> "$STUB_LOG"'
stub cairn-docs-cycle 'echo "cairn-docs-cycle $*" >> "$STUB_LOG"'

# run_case NAME ARGS... runs the script under the stubs; the case's STUB_* variables come from
# the caller's environment. It leaves the exit code in $rc and the call log in $log.
run_case() {
  export STUB_LOG="$tmp/$1.log"
  : > "$STUB_LOG"
  shift
  HOME="$tmp/home" MODEL_REVIEW_PULL_DELAY=0 \
    MODEL_REVIEW_STANDARDS_REPO="$tmp/standards" "$SCRIPT" "$@" > /dev/null 2>&1
  rc=$?
  log=$(cat "$STUB_LOG")
}

# The wrong host exits 0 and calls nothing.
STUB_HOST=thinkpad-x1 run_case wrong-host
assert_eq "$rc" "0" "wrong host exit"
assert_eq "$log" "" "wrong host calls"

# A pull that keeps failing retries five times, tells Geoff how to rerun, exits 1, and starts no session.
STUB_PULL_RC=1 run_case failed-pull
assert_eq "$rc" "1" "failed pull exit"
assert_eq "$(grep -c '^git .* pull ' <<< "$log")" "5" "pull tries"
grep -q 'notify-send -u normal .*systemctl --user start model-review.service' <<< "$log" \
  || { echo "FAIL: failed pull: no notify-send naming the rerun command"; fail=1; }
grep -q '^claude' <<< "$log" && { echo "FAIL: failed pull reached claude"; fail=1; }

# An existing month branch exits 0 before any claude call.
STUB_LS_RC=0 run_case existing-branch
assert_eq "$rc" "0" "existing branch exit"
grep -q "refs/heads/worktree-model-review-$(date +%Y-%m)" <<< "$log" \
  || { echo "FAIL: existing branch: ls-remote did not name this month's branch"; fail=1; }
grep -q '^claude' <<< "$log" && { echo "FAIL: existing branch reached claude"; fail=1; }

# A branch check that cannot reach origin (exit 128) fails closed: exit 1, a notification, no claude call.
STUB_LS_RC=128 run_case branch-check-error
assert_eq "$rc" "1" "branch check error exit"
grep -q '^notify-send' <<< "$log" || { echo "FAIL: branch check error: no notify-send"; fail=1; }
grep -q '^claude' <<< "$log" && { echo "FAIL: branch check error reached claude"; fail=1; }

# The normal path runs both audits and the /goal session, then both follow-on launchers.
run_case normal
assert_eq "$rc" "0" "normal exit"
assert_eq "$(grep -c '^claude' <<< "$log")" "3" "normal claude calls"
grep -q '^claude .*prompt-audit plugins/standards' <<< "$log" \
  || { echo "FAIL: normal: no standards audit"; fail=1; }
grep -q '^claude .*/goal .*standards plugin audit report is at' <<< "$log" \
  || { echo "FAIL: normal: /goal call lacks the standards report path"; fail=1; }
grep -q '^survey-writing-review' <<< "$log" || { echo "FAIL: normal: no writing review"; fail=1; }
grep -q '^cairn-docs-cycle' <<< "$log" || { echo "FAIL: normal: no docs cycle"; fail=1; }

# A standards audit that cannot fetch lets the review go on, and the goal names the gap.
STUB_FETCH_RC=1 run_case audit-failure
assert_eq "$rc" "0" "audit failure exit"
grep -q '^claude .*/goal .*standards plugin audit failed this run' <<< "$log" \
  || { echo "FAIL: audit failure: goal lacks the gap note"; fail=1; }

# A dry run on another host skips the gates and the follow-on launchers, and its goal says to stop.
STUB_HOST=thinkpad-x1 run_case dry-run --dry-run
assert_eq "$rc" "0" "dry run exit"
grep -q '^claude .*/goal .*dry run: commit on your branch and stop' <<< "$log" \
  || { echo "FAIL: dry run: goal lacks the stop condition"; fail=1; }
grep -q '^git .* pull ' <<< "$log" && { echo "FAIL: dry run pulled"; fail=1; }
grep -q '^survey-writing-review' <<< "$log" && { echo "FAIL: dry run on another host launched the writing review"; fail=1; }

exit $fail
