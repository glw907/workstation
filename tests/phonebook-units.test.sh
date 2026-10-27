#!/usr/bin/env bash
# phonebook-units.test.sh: prove the phonebook nightly and gate units verify under systemd-analyze
# and hold the shape the phonebook automation plan sets (Decision 1): timers at 04:00 and 10:00
# America/Anchorage with WakeSystem and Persistent, services with ConditionHost=pavilion, no User=,
# the lingering user's XDG_RUNTIME_DIR and HOME, and an ExecStart of absolute paths through
# systemd-inhibit and setpriv to the main checkout, with no drop-in left from the pass.
# The phonebook script paths are rewritten to a stub in a temp copy, since verify wants the file to
# exist and the repo checkout is not on every host. Skips cleanly when systemd-analyze is absent.
set -uo pipefail
cd "$(dirname "$0")/.." || exit 1
repo="$(pwd)"
units="$repo/bluefin/etc/systemd/system"
fail=0

if ! command -v systemd-analyze >/dev/null 2>&1; then
    echo "SKIP: systemd-analyze is not installed"
    exit 0
fi

want() { # file pattern name
    grep -qE -- "$2" "$1" 2>/dev/null || { echo "FAIL: $3: no match for '$2' in ${1#"$repo"/}"; fail=1; }
}
lacks() { # file pattern name
    ! grep -qE -- "$2" "$1" 2>/dev/null || { echo "FAIL: $3: '$2' is in ${1#"$repo"/}"; fail=1; }
}

for u in phonebook-nightly.timer phonebook-nightly.service phonebook-gate.timer phonebook-gate.service; do
    [ -f "$units/$u" ] || { echo "FAIL: $u is missing"; fail=1; }
done
for t in nightly gate; do
    [ ! -e "$units/phonebook-$t.service.d" ] || { echo "FAIL: phonebook-$t.service.d is still in the dotfiles"; fail=1; }
done
[ "$fail" = 0 ] || exit 1

want "$units/phonebook-nightly.timer" '^OnCalendar=\*-\*-\* 04:00:00 America/Anchorage$' 'nightly fires at 04:00 Anchorage'
want "$units/phonebook-gate.timer" '^OnCalendar=\*-\*-\* 10:00:00 America/Anchorage$' 'gate fires at 10:00 Anchorage'
for t in nightly gate; do
    want "$units/phonebook-$t.timer" '^WakeSystem=true$' "$t timer wakes the system"
    want "$units/phonebook-$t.timer" '^Persistent=true$' "$t timer is persistent"
    want "$units/phonebook-$t.timer" '^ConditionHost=pavilion$' "$t timer is gated to pavilion"
    want "$units/phonebook-$t.timer" '^WantedBy=timers.target$' "$t timer is installable"
    s="$units/phonebook-$t.service"
    want "$s" '^ConditionHost=pavilion$' "$t service is gated to pavilion"
    lacks "$s" '^User=' "$t service has no User="
    want "$s" '^After=network-online\.target$' "$t service starts after the network is online"
    want "$s" '^Wants=network-online\.target$' "$t service wants the network online"
    want "$s" '^Environment=XDG_RUNTIME_DIR=/run/user/1000$' "$t service sets XDG_RUNTIME_DIR"
    want "$s" '^Environment=HOME=/var/home/glw907$' "$t service sets HOME"
    want "$s" '^ExecStart=/usr/bin/systemd-inhibit --what=sleep .* /usr/bin/setpriv --reuid=glw907 --regid=glw907 --init-groups --inh-caps=-all --no-new-privs /var/home/glw907/Projects/phonebook/scripts/check/nightly\.sh' "$t service ExecStart chain"
    lacks "$s" '^Environment=.*(CLOUDFLARE|FASTMAIL|VOIPMS|TOKEN|PASSWORD|SECRET)' "$t service carries no credential"
done
want "$units/phonebook-gate.service" 'nightly\.sh --gate$' 'gate service passes --gate'
lacks "$units/phonebook-nightly.service" '--gate' 'nightly service does not pass --gate'

# Verify a temp copy whose script path is a stub.
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
mkdir -p "$tmp/stub"
printf '#!/bin/sh\nexit 0\n' >"$tmp/stub/nightly.sh"
chmod 755 "$tmp/stub/nightly.sh"
for pass in base; do
    dir="$tmp/$pass"
    mkdir -p "$dir"
    cp -r "$units"/phonebook-* "$dir/"
    find "$dir" -type f -exec sed -i -E "s#/var/home/glw907/Projects/phonebook/[^ ]*nightly\.sh#$tmp/stub/nightly.sh#" {} +
    out="$(systemd-analyze verify "$dir"/phonebook-nightly.timer "$dir"/phonebook-nightly.service \
        "$dir"/phonebook-gate.timer "$dir"/phonebook-gate.service 2>&1)"
    rc=$?
    if [ "$rc" != 0 ]; then
        echo "FAIL: systemd-analyze verify ($pass) exited $rc:"
        sed 's/^/      /' <<<"$out"
        fail=1
    fi
done

if [ "$fail" -eq 0 ]; then
    echo "phonebook-units.test.sh: all passed"
fi
exit "$fail"
