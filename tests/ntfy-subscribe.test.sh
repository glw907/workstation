#!/usr/bin/env bash
# ntfy-subscribe.test.sh: prove the subscriber maps urgent to critical and routine to normal,
# records the all-quiet silently, fetches what it missed with since=, skips a replayed message,
# raises the stale notice only when no all-quiet has arrived, and exits non-zero when the stream
# ends in an error so systemd restarts it. Every run uses a temp HOME, a fake curl that replays a
# stream file, and a fake notify-send that logs its arguments.
set -uo pipefail
cd "$(dirname "$0")/.." || exit 1
repo="$(pwd)"
SUB="$repo/bin/.local/bin/ntfy-subscribe"
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

mkdir -p "$root/bin" "$root/home/.local"
cat >"$root/bin/curl" <<'F'
#!/usr/bin/env bash
echo "curl $*" >>"$FAKE_LOG"
# The URL arrives as a curl config on stdin; log it on its own line so a test can tell it from argv.
[ -t 0 ] || echo "stdin $(cat)" >>"$FAKE_LOG"
cat "$FAKE_STREAM"
sleep "${FAKE_HOLD:-0}"
exit "${FAKE_CURL_RC:-0}"
F
cat >"$root/bin/notify-send" <<'F'
#!/usr/bin/env bash
echo "notify-send $*" >>"$FAKE_NOTIFY"
F
chmod +x "$root/bin/curl" "$root/bin/notify-send"

URGENT=urg-topic-dummy
ROUTINE=rtn-topic-dummy

# run [ENV...]: run the subscriber once under the fakes; prints its exit status last.
run() {
  : >"$root/log"
  : >"$root/notify"
  env -i PATH="$root/bin:$PATH" HOME="$root/home" XDG_STATE_HOME="$root/state" \
    FAKE_LOG="$root/log" FAKE_NOTIFY="$root/notify" FAKE_STREAM="$root/stream" \
    NTFY_URGENT_TOPIC="$URGENT" NTFY_ROUTINE_TOPIC="$ROUTINE" "$@" bash "$SUB" >"$root/out" 2>&1
  echo $?
}

# --- Urgency mapping, the open and keepalive events, and a malformed line --------------------------
cat >"$root/stream" <<S
{"id":"o1","time":1000,"event":"open","topic":"$URGENT,$ROUTINE"}
{"id":"m1","time":1001,"event":"message","topic":"$URGENT","title":"Mail down","message":"healthz failed twice","priority":5}
not json at all
{"id":"m2","time":1002,"event":"message","topic":"$ROUTINE","title":"Disk 85%","message":"media /","priority":3}
{"id":"k1","time":1003,"event":"keepalive","topic":"$URGENT,$ROUTINE"}
S
assert_eq "$(run)" 0 "a clean stream exits 0"
notify=$(cat "$root/notify")
assert_has "$notify" "notify-send -u critical -- Mail down healthz failed twice" "urgent maps to critical"
assert_has "$notify" "notify-send -u normal -- Disk 85% media /" "routine maps to normal"
assert_eq "$(wc -l <"$root/notify" | tr -d ' ')" 2 "only the two messages notify"
assert_has "$(cat "$root/log")" "/json?since=12h" "the first start asks for the last 12 hours"
assert_has "$(cat "$root/log")" "$URGENT,$ROUTINE" "both topics ride one connection"
assert_eq "$(/usr/bin/grep -c -e "$URGENT" -e "$ROUTINE" <(/usr/bin/grep '^curl' "$root/log"))" 0 "the topic names are never on curl's command line"

# --- A notice that cannot be shown is not recorded, so a restart replays it -------------------------
mkdir -p "$root/bin2"
printf '#!/usr/bin/env bash\nexit 1\n' >"$root/bin2/notify-send"
chmod +x "$root/bin2/notify-send"
rm -rf "$root/state"
printf '{"id":"m9","time":3000,"event":"message","topic":"%s","title":"Mail down","message":"x","priority":5}\n' "$URGENT" >"$root/stream"
assert_eq "$(run PATH="$root/bin2:$root/bin:$PATH")" 1 "a stream with a failing notify-send exits 1"
assert_eq "$(ls "$root/state/ntfy-subscribe/last_time" 2>/dev/null | wc -l | tr -d ' ')" 0 "a notice that failed to show does not advance last_time"
# A later all-quiet in the same stream must not move last_time past the failed notice.
rm -rf "$root/state"
{
  printf '{"id":"m9","time":3000,"event":"message","topic":"%s","title":"Mail down","message":"x","priority":5}\n' "$URGENT"
  printf '{"id":"q9","time":3001,"event":"message","topic":"%s","title":"all-quiet","message":"ok","priority":1}\n' "$ROUTINE"
} >"$root/stream"
assert_eq "$(run PATH="$root/bin2:$root/bin:$PATH")" 1 "a failed notice ends the stream with exit 1"
assert_eq "$(ls "$root/state/ntfy-subscribe/last_time" 2>/dev/null | wc -l | tr -d ' ')" 0 "a later all-quiet does not advance last_time past a failed notice"
assert_eq "$(run)" 0 "the restart exits 0"
assert_has "$(cat "$root/notify")" "notify-send -u critical -- Mail down x" "the restart shows the notice that failed before"
rm -rf "$root/state"
cat >"$root/stream" <<S
{"id":"o1","time":1000,"event":"open","topic":"$URGENT,$ROUTINE"}
{"id":"m1","time":1001,"event":"message","topic":"$URGENT","title":"Mail down","message":"healthz failed twice","priority":5}
not json at all
{"id":"m2","time":1002,"event":"message","topic":"$ROUTINE","title":"Disk 85%","message":"media /","priority":3}
{"id":"k1","time":1003,"event":"keepalive","topic":"$URGENT,$ROUTINE"}
S
assert_eq "$(run)" 0 "the first stream runs again"

# --- A restart asks for what it missed and skips a replayed message --------------------------------
assert_eq "$(run)" 0 "the second start exits 0"
assert_has "$(cat "$root/log")" "since=1002" "a restart asks since the last message time"
assert_eq "$(wc -l <"$root/notify" | tr -d ' ')" 0 "a replayed message does not notify again"

# --- The all-quiet is recorded and never shown ------------------------------------------------------
rm -rf "$root/state"
cat >"$root/stream" <<S
{"id":"q1","time":2000,"event":"message","topic":"$ROUTINE","title":"all-quiet","message":"all quiet","priority":1}
S
assert_eq "$(run)" 0 "an all-quiet stream exits 0"
assert_eq "$(wc -l <"$root/notify" | tr -d ' ')" 0 "the all-quiet raises no notification"
assert_eq "$(cat "$root/state/ntfy-subscribe/quiet")" 2000 "the all-quiet time is recorded"

# --- A non-integer time is refused and never evaluated -----------------------------------------------
rm -rf "$root/state" "$root/pwn"
printf '{"id":"q3","time":"a[$(touch %s)]","event":"message","topic":"%s","title":"all-quiet","message":"ok","priority":1}\n' "$root/pwn" "$ROUTINE" >"$root/stream"
run NTFY_QUIET_LIMIT=600 NTFY_CHECK_EVERY=1 FAKE_HOLD=3 >/dev/null
assert_eq "$([ -e "$root/pwn" ] && echo ran || echo clean)" clean "a string time is never evaluated"
assert_eq "$(ls "$root/state/ntfy-subscribe/quiet" 2>/dev/null | wc -l | tr -d ' ')" 0 "a string time is not recorded"

# --- The stale notice -------------------------------------------------------------------------------
rm -rf "$root/state"
: >"$root/stream"
assert_eq "$(run NTFY_QUIET_LIMIT=1 NTFY_CHECK_EVERY=1 FAKE_HOLD=3)" 0 "a held empty stream exits 0"
assert_has "$(cat "$root/notify")" "notify-send -u normal" "the stale notice is normal urgency"
assert_has "$(cat "$root/notify")" "silent" "the stale notice says the monitor went silent"
assert_eq "$(wc -l <"$root/notify" | tr -d ' ')" 1 "the stale notice repeats no sooner than its interval"

rm -rf "$root/state"
mkdir -p "$root/state/ntfy-subscribe"
echo 1000 >"$root/state/ntfy-subscribe/first_seen" # old, so only the all-quiet below resets the clock
now=$(date +%s)
printf '{"id":"q2","time":%s,"event":"message","topic":"%s","title":"all-quiet","message":"ok","priority":1}\n' "$now" "$ROUTINE" >"$root/stream"
assert_eq "$(run NTFY_QUIET_LIMIT=600 NTFY_CHECK_EVERY=1 FAKE_HOLD=3)" 0 "a fresh all-quiet stream exits 0"
assert_eq "$(wc -l <"$root/notify" | tr -d ' ')" 0 "a recent all-quiet raises no stale notice"

# --- Configuration and failure ----------------------------------------------------------------------
: >"$root/stream"
rm -rf "$root/state"
assert_eq "$(run FAKE_CURL_RC=7)" 7 "a failing stream exits non-zero so systemd restarts it"

: >"$root/log"
env -i PATH="$root/bin:$PATH" HOME="$root/home" XDG_STATE_HOME="$root/state" FAKE_LOG="$root/log" \
  FAKE_NOTIFY="$root/notify" FAKE_STREAM="$root/stream" bash "$SUB" >"$root/out" 2>&1
assert_eq "$?" 1 "missing topics exit 1"
assert_has "$(cat "$root/out")" "NTFY_URGENT_TOPIC" "the error names the missing store name"
assert_eq "$(wc -c <"$root/log" | tr -d ' ')" 0 "a missing topic makes no connection"

printf 'export NTFY_URGENT_TOPIC=from-file-u\nexport NTFY_ROUTINE_TOPIC=from-file-r\n' >"$root/home/.local/secrets"
rm -rf "$root/state"
: >"$root/log"
env -i PATH="$root/bin:$PATH" HOME="$root/home" XDG_STATE_HOME="$root/state" FAKE_LOG="$root/log" \
  FAKE_NOTIFY="$root/notify" FAKE_STREAM="$root/stream" bash "$SUB" >"$root/out" 2>&1
assert_has "$(cat "$root/log")" "from-file-u,from-file-r" "topics are read from ~/.local/secrets"

exit "$fail"
