#!/usr/bin/env bash
# workstation-sync.test.sh: prove workstation-sync's repo rules and failure handling,
# workstation-install's plugin step, the MEMORY.md union in workstation-syncthing, its pairing
# calls, and check-drift's work leg, on temporary repos with every outside command stubbed.
set -uo pipefail
cd "$(dirname "$0")/.."
bin="$(pwd)/bin/.local/bin"
fail=0
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

check() { # label expected actual
    case "$3" in *"$2"*) ;; *) echo "FAIL: $1: lacks '$2' in: $3"; fail=1 ;; esac
}
refute() { # label unexpected actual
    case "$3" in *"$2"*) echo "FAIL: $1: has '$2' in: $3"; fail=1 ;; esac
}
commit() { git -C "$1" -c user.email=t@t -c user.name=t commit -q --allow-empty -m "$2"; }

stubs=$tmp/stubs
calls=$tmp/calls
mkdir -p "$stubs"
for cmd in stow claude-tooling-sync workstation-install workstation-update \
    workstation-syncthing check-drift-notify npm; do
    printf '#!/bin/sh\necho "%s $*" >>"%s"\n' "$cmd" "$calls" >"$stubs/$cmd"
done
cat >"$stubs/systemctl" <<STUB
#!/bin/sh
echo "systemctl \$*" >>"$calls"
case "\$*" in *is-enabled*) exit 1 ;; esac
STUB
cat >"$stubs/notify-send" <<STUB
#!/bin/sh
echo "notify \$*" >>"$calls"
STUB
cat >"$stubs/claude" <<STUB
#!/bin/sh
cat "$tmp/agents.json"
STUB
cat >"$stubs/check-drift" <<STUB
#!/bin/sh
cat "$tmp/work.txt"
STUB
chmod +x "$stubs"/*

origin=$tmp/origin.git
git init -q --bare -b main "$origin"
seed=$tmp/seed
git clone -q "$origin" "$seed" 2>/dev/null
mkdir -p "$seed/bluefin" "$seed/upkeep/.config/systemd/user" "$seed/systemd/.config/systemd/user"
printf 'bin\n' >"$seed/bluefin/stow-packages.txt"
touch "$seed/upkeep/.config/systemd/user/one.timer" "$seed/systemd/.config/systemd/user/two.timer"
git -C "$seed" add .
commit "$seed" one
git -C "$seed" push -q origin HEAD:main

dot=$tmp/dot
root=$tmp/projects
mkdir "$root"
git clone -q "$origin" "$dot"
for name in plain dirty branch live dead; do git clone -q "$origin" "$root/$name"; done
git -C "$root/branch" switch -q -c pass
touch "$root/dirty/edit" && git -C "$root/dirty" add edit
echo '[]' >"$tmp/agents.json"
printf '[{"status":"busy","cwd":"%s"},{"status":null,"cwd":"%s"}]' "$root/live" "$root/dead" >"$tmp/agents.json"
: >"$tmp/work.txt"
touch "$seed/package-lock.json"
git -C "$seed" add .
commit "$seed" two
git -C "$seed" push -q origin HEAD:main

run() {
    : >"$calls"
    out=$(PATH="$stubs:$PATH" SYNC_DOTFILES=$dot SYNC_ROOT=$root SYNC_STATE=$tmp/state \
        SYNC_PROBE=${1:-$origin} "$bin/workstation-sync" 2>&1)
    rc=$?
}
head_of() { git -C "$1" rev-parse HEAD; }

want=$(git -C "$seed" rev-parse HEAD)
mkdir "$root/plain/node_modules"
run
[ "$rc" -eq 0 ] || { echo "FAIL: clean run exit $rc: $out"; fail=1; }
check "plain repo pulled" "$want" "$(head_of "$root/plain")"
check "repo under an exited session pulled" "$want" "$(head_of "$root/dead")"
refute "dirty repo left" "$want" "$(head_of "$root/dirty")"
refute "repo on another branch left" "$want" "$(head_of "$root/branch")"
refute "repo under a live session left" "$want" "$(head_of "$root/live")"
log=$(cat "$calls")
check "pull restows" "stow -R bin" "$log"
check "lockfile change runs npm ci" "npm ci" "$log"
check "timers enabled from both packages" "enable --now one.timer" "$log"
check "second package's timer" "enable --now two.timer" "$log"
refute "clean run is quiet" "notify --urgency" "$log"
check "status reports" "ok" "$(PATH="$stubs:$PATH" SYNC_STATE=$tmp/state "$bin/workstation-sync" --status)"

run
check "no pull means a plain stow" "stow -S bin" "$(cat "$calls")"

printf '#!/bin/sh\nexit 1\n' >"$stubs/workstation-install"
run
[ "$rc" -eq 1 ] || { echo "FAIL: failed step exit $rc"; fail=1; }
log=$(cat "$calls")
check "a failure notifies" "notify --urgency" "$log"
check "steps after a failure still run" "check-drift-notify" "$log"
printf '#!/bin/sh\nexit 0\n' >"$stubs/workstation-install"

printf '  ! dirty: 1 uncommitted\n' >"$tmp/work.txt"
run
check "left work notifies" "1 item(s) left here" "$(cat "$calls")"
: >"$tmp/work.txt"

run "$tmp/absent.git"
[ "$rc" -eq 0 ] || { echo "FAIL: offline exit $rc"; fail=1; }
[ ! -s "$calls" ] || { echo "FAIL: offline run did work: $(cat "$calls")"; fail=1; }
check "offline is recorded" "unreachable" "$out"

# workstation-install's plugin step: only a missing, enabled plugin installs, and only a marketplace
# the settings declare gets added.
m=$tmp/manifests
mkdir -p "$m/bluefin" "$m/claude/.claude" "$tmp/instbin"
touch "$m/bluefin/Brewfile" "$m/bluefin/flatpaks.txt" "$m/bluefin/uv-tools.txt"
cat >"$m/claude/.claude/settings.json" <<'JSON'
{"enabledPlugins": {"have@official": true, "off@official": false, "new@market": true, "plain@official": true},
 "extraKnownMarketplaces": {"market": {"source": {"source": "github", "repo": "owner/market"}}}}
JSON
for cmd in brew flatpak uv mise; do
    printf '#!/bin/sh\nexit 0\n' >"$tmp/instbin/$cmd"
done
cat >"$tmp/instbin/claude" <<STUB
#!/bin/sh
case "\$*" in
    "plugin list --json") echo '[{"id":"have@official","scope":"user"},{"id":"new@market","scope":"project"}]' ;;
    *) echo "\$*" >>"$tmp/plugin-log" ;;
esac
STUB
chmod +x "$tmp"/instbin/*
PATH="$tmp/instbin:$PATH" "$bin/workstation-install" "$m/bluefin" || { echo "FAIL: install exit"; fail=1; }
log=$(cat "$tmp/plugin-log")
check "declared marketplace added" "plugin marketplace add owner/market" "$log"
check "project-scoped plugin still installs at user scope" "plugin install new@market" "$log"
check "enabled plugin installs" "plugin install plain@official" "$log"
refute "installed plugin left" "plugin install have" "$log"
refute "disabled plugin left" "plugin install off" "$log"

# workstation-syncthing, with a stub that keeps its lists in files.
st=$tmp/st
mkdir "$st" "$tmp/stbin"
cat >"$tmp/stbin/syncthing" <<STUB
#!/bin/bash
echo "\$*" >>"$st/log"
args="\$*"
case "\$args" in
    "cli show system") echo '{"myID":"OWN"}' ;;
    "cli config devices list") cat "$st/devices" 2>/dev/null ;;
    "cli config folders list") cat "$st/folders" 2>/dev/null ;;
    "cli config devices add "*) echo "\$6" >>"$st/devices" ;;
    "cli config folders add "*) echo "\$6" >>"$st/folders" ;;
esac
STUB
chmod +x "$tmp/stbin/syncthing"
memory=$tmp/memory
mkdir -p "$memory/-a/memory" "$tmp/docs"
printf -- '- one\n- from b\n' >"$memory/-a/memory/MEMORY.md"
printf -- '- one\n- from a\n' >"$memory/-a/memory/MEMORY.sync-conflict-20261101-120000-ABC.md"
host=$(hostname)

pair() {
    out=$(PATH="$tmp/stbin:$PATH" SYNCTHING_DEVICES=$tmp/devices.txt SYNCTHING_MEMORY=$memory \
        SYNCTHING_DOCUMENTS=$tmp/docs "$bin/workstation-syncthing" 2>&1)
    rc=$?
}
printf 'other PEER\n' >"$tmp/devices.txt"
pair
check "unlisted host prints its line" "$host OWN" "$out"
[ ! -e "$st/folders" ] || { echo "FAIL: unlisted host shared a folder"; fail=1; }
index=$(cat "$memory/-a/memory/MEMORY.md")
check "union keeps this side" "from b" "$index"
check "union keeps the other side" "from a" "$index"
[ "$(grep -c -- '- one' <<<"$index")" -eq 1 ] || { echo "FAIL: union duplicated a line"; fail=1; }
[ -z "$(find "$memory" -name '*sync-conflict*')" ] || { echo "FAIL: conflict copy kept"; fail=1; }

printf '# comment\n%s OWN\nother PEER\n' "$host" >"$tmp/devices.txt"
pair
[ "$rc" -eq 0 ] || { echo "FAIL: pairing exit $rc: $out"; fail=1; }
log=$(cat "$st/log")
check "peer added" "config devices add --device-id PEER --name other" "$log"
refute "own device not added" "--device-id OWN" "$log"
check "memory shared" "folders add --id claude-memory --label claude-memory --path $memory" "$log"
check "documents shared with the peer" "folders documents devices add --device-id PEER" "$log"
check "versioning on" "folders documents versioning type set simple" "$log"
check "ignore file written" "!/*/memory/**" "$(cat "$memory/.stignore")"

: >"$st/log"
pair
refute "rerun adds no device" "devices add --device-id PEER --name" "$(cat "$st/log")"
refute "rerun adds no folder" "folders add" "$(cat "$st/log")"

# check-drift's work leg against real repos.
work=$tmp/work
mkdir -p "$work" "$tmp/wdocs" "$tmp/wmem"
git clone -q "$origin" "$work/clean"
git clone -q "$origin" "$work/held"
touch "$work/held/new"
commit "$work/held" unpushed
git clone -q "$origin" "$work/stale"
git -C "$work/stale" reset -q --hard HEAD~1
touch "$tmp/wdocs/a.sync-conflict-20261101-120000-ABC.txt"
out=$(HOME=$tmp WORK_ROOT=$work WORK_DOCUMENTS=$tmp/wdocs WORK_MEMORY=$tmp/wmem "$bin/check-drift" --work-only 2>&1)
rc=$?
[ "$rc" -eq 0 ] || { echo "FAIL: work leg exit $rc"; fail=1; }
check "dirty repo named" "held: 1 uncommitted" "$out"
check "unpushed commit named" "held: 1 unpushed" "$out"
check "behind repo named" "stale: 1 behind origin" "$out"
check "conflict copy named" "sync-conflict-20261101" "$out"
refute "clean repo quiet" "clean:" "$out"

exit "$fail"
