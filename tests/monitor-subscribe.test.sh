#!/usr/bin/env bash
# monitor-subscribe.test.sh: prove the subscriber polls the monitor's /alerts endpoint with the read
# token, maps urgent to critical and routine to normal, shows each condition once per opening and
# again at its repeat, raises a notice when the last tick is stale or the endpoint stays
# unreachable, refuses a non-integer time, and exits non-zero on a failed notice so systemd replays
# it. Every run uses a temp HOME, a fake curl that serves a scripted sequence of responses and
# advances a fake clock, and a fake notify-send that logs its arguments.
set -uo pipefail
cd "$(dirname "$0")/.." || exit 1
repo="$(pwd)"
SUB="$repo/bin/.local/bin/monitor-subscribe"
fail=0
root="$(mktemp -d)"
trap 'rm -rf "$root"' EXIT

assert_eq() {
  [ "$1" = "$2" ] || { echo "FAIL: $3: got '$1', want '$2'"; fail=1; }
}
assert_has() { # haystack needle name
  case "$1" in *"$2"*) ;; *) echo "FAIL: $3: no '$2' in: $1"; fail=1 ;; esac
}
assert_lacks() {
  case "$1" in *"$2"*) echo "FAIL: $3: found '$2' in: $1"; fail=1 ;; esac
}

mkdir -p "$root/bin" "$root/home/.local" "$root/resp"
# The fake curl serves resp/<n> for its n-th call (the last one repeats), exits with the code in
# resp/<n>.rc when there is one, and moves the clock forward by FAKE_STEP seconds per call.
cat >"$root/bin/curl" <<'F'
#!/usr/bin/env bash
n=$(( $(cat "$FAKE_DIR/calls" 2>/dev/null || echo 0) + 1 ))
echo "$n" >"$FAKE_DIR/calls"
echo "curl $*" >>"$FAKE_LOG"
# The URL and token arrive as a curl config on stdin; log them apart so a test can tell them from argv.
[ -t 0 ] || echo "stdin $(cat)" >>"$FAKE_LOG"
echo $(( $(cat "$FAKE_CLOCK") + ${FAKE_STEP:-60} )) >"$FAKE_CLOCK"
f="$FAKE_DIR/resp/$n"
[ -f "$f" ] || f="$FAKE_DIR/resp/$(ls "$FAKE_DIR/resp" | /usr/bin/grep -v '\.rc$' | sort -n | tail -n1)"
cat "$f"
rc=0
[ -f "$f.rc" ] && rc=$(cat "$f.rc")
exit "$rc"
F
cat >"$root/bin/notify-send" <<'F'
#!/usr/bin/env bash
echo "notify-send $*" >>"$FAKE_NOTIFY"
F
chmod +x "$root/bin/curl" "$root/bin/notify-send"

T0=1800000000
TOKEN=read-token-dummy # secret-guard-allow

# resp N BODY [RC]: script the N-th curl response.
resp() {
  printf '%s' "$2" >"$root/resp/$1"
  [ -n "${3:-}" ] && echo "$3" >"$root/resp/$1.rc"
  return 0
}

# alerts TICK_MS CONDITIONS_JSON: an /alerts body.
alerts() { printf '{"last_tick_at":%s,"conditions":%s}' "$1" "$2"; }

# cond ID SEVERITY OPENED_MS TITLE MESSAGE
cond() { printf '{"id":"%s","severity":"%s","title":"%s","message":"%s","opened_at":%s}' "$1" "$2" "$4" "$5" "$3"; }

# fresh: a clean state, no scripted responses, and the clock at T0.
fresh() {
  rm -rf "$root/state" "$root/resp" "$root/calls"
  mkdir -p "$root/resp"
  echo "$T0" >"$root/clock"
}

# run [ENV...]: run the subscriber under the fakes; prints its exit status last.
run() {
  : >"$root/log"
  : >"$root/notify"
  env -i PATH="$root/bin:$PATH" HOME="$root/home" XDG_STATE_HOME="$root/state" \
    FAKE_DIR="$root" FAKE_LOG="$root/log" FAKE_NOTIFY="$root/notify" FAKE_CLOCK="$root/clock" \
    MONITOR_READ_TOKEN="$TOKEN" MONITOR_POLL_EVERY=0 MONITOR_POLLS=1 MONITOR_CLOCK="$root/clock" \
    "$@" bash "$SUB" >"$root/out" 2>&1
  echo $?
}

notifies() { wc -l <"$root/notify" | tr -d ' '; }

now_ms=$((T0 * 1000))

# --- Urgency mapping, one notice per condition, and the request ------------------------------------
fresh
resp 1 "$(alerts "$now_ms" "[$(cond mail_down:tls_993 urgent "$now_ms" 'Mail check failing' 'tls_993 failed 2 times in a row'),$(cond snapshot:mail routine "$now_ms" 'Backup snapshot problem' 'config changed')]")"
assert_eq "$(run)" 0 "a clean poll exits 0"
notify=$(cat "$root/notify")
assert_has "$notify" "notify-send -u critical -- Mail check failing tls_993 failed 2 times in a row" "urgent maps to critical"
assert_has "$notify" "notify-send -u normal -- Backup snapshot problem config changed" "routine maps to normal"
assert_eq "$(notifies)" 2 "each open condition notifies once"
log=$(cat "$root/log")
assert_has "$log" "https://monitor.907.life/alerts" "the default endpoint is the monitor's /alerts"
assert_has "$log" "Authorization: Bearer $TOKEN" "the read token goes in a bearer header"
assert_eq "$(/usr/bin/grep -c -e "$TOKEN" <(/usr/bin/grep '^curl' "$root/log"))" 0 "the token is never on curl's command line"

# --- Once per opening: a later poll shows nothing new ----------------------------------------------
fresh
body="$(alerts "$now_ms" "[$(cond mail_down:tls_993 urgent "$now_ms" 'Mail check failing' 'x')]")"
resp 1 "$body"
assert_eq "$(run MONITOR_POLLS=3 FAKE_STEP=60)" 0 "three polls exit 0"
assert_eq "$(notifies)" 1 "an open condition shows once across polls"
assert_eq "$(run MONITOR_POLLS=2 FAKE_STEP=60)" 0 "a restart exits 0"
assert_eq "$(notifies)" 0 "a restart does not show it again"

# --- Again at its 12-hour repeat, not before --------------------------------------------------------
fresh
resp 1 "$body"
assert_eq "$(run MONITOR_POLLS=2 FAKE_STEP=43000 MONITOR_STALE_LIMIT=999999999)" 0 "polls just under 12 hours apart exit 0"
assert_eq "$(notifies)" 1 "no repeat before 12 hours"
fresh
resp 1 "$body"
assert_eq "$(run MONITOR_POLLS=3 FAKE_STEP=22000 MONITOR_STALE_LIMIT=999999999)" 0 "polls spanning 12 hours exit 0"
assert_eq "$(notifies)" 2 "an open condition shows again after 12 hours"

# --- A cleared and reopened condition shows again ---------------------------------------------------
fresh
resp 1 "$body"
resp 2 "$(alerts "$now_ms" '[]')"
resp 3 "$(alerts "$now_ms" "[$(cond mail_down:tls_993 urgent "$((now_ms + 120000))" 'Mail check failing' 'x')]")"
assert_eq "$(run MONITOR_POLLS=3 FAKE_STEP=60)" 0 "a clear and reopen exit 0"
assert_eq "$(notifies)" 2 "a reopened condition shows as a new opening"

# --- A stale tick raises one notice -----------------------------------------------------------------
fresh
resp 1 "$(alerts "$((now_ms - 1000000))" '[]')"
assert_eq "$(run MONITOR_POLLS=2 FAKE_STEP=60)" 0 "a stale tick exits 0"
assert_has "$(cat "$root/notify")" "notify-send -u normal" "the stale notice is normal urgency"
assert_has "$(cat "$root/notify")" "stalled" "the stale notice says the monitor stalled"
assert_eq "$(notifies)" 1 "a stale tick notifies once, not on every poll"
fresh
resp 1 "$(alerts "$now_ms" '[]')"
assert_eq "$(run MONITOR_POLLS=2 FAKE_STEP=60)" 0 "a fresh tick exits 0"
assert_eq "$(notifies)" 0 "a recent tick raises no notice"

# A tick that goes stale, recovers, and goes stale again notifies each time.
fresh
resp 1 "$(alerts "$((now_ms - 1000000))" '[]')"
resp 2 "$(alerts "$((now_ms + 100000))" '[]')"
resp 3 "$(alerts "$((now_ms + 100000))" '[]')"
assert_eq "$(run MONITOR_POLLS=3 FAKE_STEP=60)" 0 "a stale tick that recovers exits 0"
assert_eq "$(notifies)" 1 "the stale notice came once while it was stale"
assert_eq "$(ls "$root/state/monitor-subscribe/stale_notified" 2>/dev/null | wc -l | tr -d ' ')" 0 "a recovered tick re-arms the stale notice"

# --- A tick time of null counts from the first poll -------------------------------------------------
fresh
resp 1 '{"last_tick_at":null,"conditions":[]}'
assert_eq "$(run MONITOR_POLLS=2 FAKE_STEP=60)" 0 "a null tick time exits 0"
assert_eq "$(notifies)" 0 "a null tick time is not stale at once"
fresh
resp 1 '{"last_tick_at":null,"conditions":[]}'
assert_eq "$(run MONITOR_POLLS=3 FAKE_STEP=600)" 0 "a null tick time that never fills exits 0"
assert_has "$(cat "$root/notify")" "stalled" "a null tick time stalls after the limit"

# --- An unreachable endpoint: silent at first, one notice after 15 minutes --------------------------
fresh
resp 1 '' 7
assert_eq "$(run MONITOR_POLLS=3 FAKE_STEP=60)" 0 "a brief outage exits 0"
assert_eq "$(notifies)" 0 "an outage under 15 minutes raises no notice"
fresh
resp 1 '' 7
assert_eq "$(run MONITOR_POLLS=4 FAKE_STEP=400)" 0 "a long outage exits 0"
assert_has "$(cat "$root/notify")" "unreachable" "an outage past 15 minutes says it is unreachable"
assert_eq "$(notifies)" 1 "an outage notifies once"

# A garbled body is an outage, not a crash.
fresh
resp 1 '<html>bad gateway</html>'
assert_eq "$(run MONITOR_POLLS=4 FAKE_STEP=400)" 0 "a body that is not JSON exits 0"
assert_has "$(cat "$root/notify")" "unreachable" "a body that is not JSON counts as unreachable"

# --- A non-integer time is refused and never evaluated ----------------------------------------------
fresh
rm -rf "$root/pwn"
resp 1 "{\"last_tick_at\":\"a[\$(touch $root/pwn)]\",\"conditions\":[{\"id\":\"x\",\"severity\":\"urgent\",\"title\":\"t\",\"message\":\"m\",\"opened_at\":\"a[\$(touch $root/pwn)]\"}]}"
run MONITOR_POLLS=2 FAKE_STEP=60 >/dev/null
assert_eq "$([ -e "$root/pwn" ] && echo ran || echo clean)" clean "a string time is never evaluated"
assert_eq "$(cat "$root/state/monitor-subscribe/shown" 2>/dev/null | wc -c | tr -d ' ')" 0 "a condition with a string opening time is not recorded"
fresh
resp 1 "$(alerts "$now_ms" "[$(cond x urgent '08' 't' 'm')]")"
run >/dev/null
assert_eq "$(notifies)" 0 "a leading-zero opening time is refused"
# A stored value that is not a clean integer never reaches arithmetic.
fresh
mkdir -p "$root/state/monitor-subscribe"
echo 08 >"$root/state/monitor-subscribe/first_seen"
resp 1 "$(alerts "$now_ms" '[]')"
run >/dev/null
assert_lacks "$(cat "$root/out")" "too great" "a bad stored first-seen time never reaches arithmetic"

# --- A notice that cannot be shown is not recorded, and ends the run ----------------------------------
mkdir -p "$root/bin2"
printf '#!/usr/bin/env bash\nexit 1\n' >"$root/bin2/notify-send"
chmod +x "$root/bin2/notify-send"
fresh
resp 1 "$body"
assert_eq "$(run PATH="$root/bin2:$root/bin:$PATH" MONITOR_POLLS=3)" 1 "a failing notify-send exits 1"
assert_eq "$(cat "$root/calls")" 1 "a failed notice ends the run before the next poll"
assert_eq "$(run MONITOR_POLLS=1)" 0 "the restart exits 0"
assert_has "$(cat "$root/notify")" "notify-send -u critical -- Mail check failing x" "the restart shows the notice that failed before"

# --- Configuration ------------------------------------------------------------------------------------
fresh
resp 1 "$(alerts "$now_ms" '[]')"
: >"$root/log"
env -i PATH="$root/bin:$PATH" HOME="$root/home" XDG_STATE_HOME="$root/state" FAKE_DIR="$root" FAKE_LOG="$root/log" \
  FAKE_NOTIFY="$root/notify" FAKE_CLOCK="$root/clock" bash "$SUB" >"$root/out" 2>&1
assert_eq "$?" 1 "a missing token exits 1"
assert_has "$(cat "$root/out")" "MONITOR_READ_TOKEN" "the error names the missing store name"
assert_eq "$(wc -c <"$root/log" | tr -d ' ')" 0 "a missing token makes no request"

printf 'export MONITOR_READ_TOKEN=from-file-token\n' >"$root/home/.local/secrets" # secret-guard-allow
fresh
resp 1 "$(alerts "$now_ms" '[]')"
: >"$root/log"
env -i PATH="$root/bin:$PATH" HOME="$root/home" XDG_STATE_HOME="$root/state" FAKE_DIR="$root" FAKE_LOG="$root/log" \
  FAKE_NOTIFY="$root/notify" FAKE_CLOCK="$root/clock" MONITOR_POLL_EVERY=0 MONITOR_POLLS=1 MONITOR_CLOCK="$root/clock" \
  bash "$SUB" >"$root/out" 2>&1
assert_has "$(cat "$root/log")" "Bearer from-file-token" "the token is read from ~/.local/secrets"

exit "$fail"
