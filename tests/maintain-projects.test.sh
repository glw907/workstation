#!/usr/bin/env bash
# maintain-projects.test.sh: drive the script against a local origin with npm, gh, and notify-send
# stubbed. A passing update reaches origin, a failed gate and a dirty checkout leave it alone and
# notify once, no change stays quiet, and a dry run pushes nothing.
set -uo pipefail
script="$(cd "$(dirname "$0")/.." && pwd)/bin/.local/bin/maintain-projects"
fail=0
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT

mkdir "$work/bin"
cat >"$work/bin/npm" <<'S'
#!/usr/bin/env bash
case $1 in
  update) [ -n "${STUB_CHANGE:-}" ] && echo "$RANDOM" >>package-lock.json ;;
  run) exit "${STUB_GATE:-0}" ;;
  outdated) exit 1 ;;
esac
exit 0
S
cat >"$work/bin/gh" <<'S'
#!/usr/bin/env bash
case $2 in list) echo 7 ;; watch) exit "${STUB_CI:-0}" ;; esac
S
cat >"$work/bin/notify-send" <<'S'
#!/usr/bin/env bash
echo "$*" >>"$NOTIFIED"
S
chmod +x "$work/bin/"*

setup() {
    rm -rf "$work/origin.git" "$work/Projects" "$work/state" "$work/notified"
    git init -q --bare -b main "$work/origin.git"
    git clone -q "$work/origin.git" "$work/Projects/demo" 2>/dev/null
    git -C "$work/Projects/demo" checkout -q -b main 2>/dev/null
    echo '{}' >"$work/Projects/demo/package.json"
    echo '{}' >"$work/Projects/demo/package-lock.json"
    git -C "$work/Projects/demo" add .
    git -C "$work/Projects/demo" -c user.name=t -c user.email=t@t commit -q -m start
    git -C "$work/Projects/demo" push -q origin main
    echo demo >"$work/list"
}

run() {
    PATH="$work/bin:$PATH" MAINTAIN_ROOT="$work/Projects" MAINTAIN_LIST="$work/list" \
        MAINTAIN_STATE="$work/state" NOTIFIED="$work/notified" MAINTAIN_CI_WAIT=0 \
        GIT_AUTHOR_NAME=t GIT_AUTHOR_EMAIL=t@t GIT_COMMITTER_NAME=t GIT_COMMITTER_EMAIL=t@t \
        "$script" "$@" >/dev/null 2>&1
}

commits() { git -C "$work/origin.git" rev-list --count main; }
notes() { [ -f "$work/notified" ] && wc -l <"$work/notified" || echo 0; }

check() { # name exit-got exit-want commits-want notes-want
    if [ "$2" = "$3" ] && [ "$(commits)" = "$4" ] && [ "$(notes)" = "$5" ]; then
        return
    fi
    echo "FAIL: $1: exit $2, commits $(commits), notes $(notes)"
    fail=1
}

setup; STUB_CHANGE=1 run; check "update reaches origin" $? 0 2 0
[ "$(git -C "$work/Projects/demo" rev-parse HEAD)" = "$(git -C "$work/origin.git" rev-parse main)" ] \
    || { echo "FAIL: main checkout did not follow origin"; fail=1; }
setup; run; check "no change stays quiet" $? 0 1 0
setup; STUB_CHANGE=1 STUB_GATE=1 run; check "gate failure leaves main" $? 1 1 1
setup; STUB_CHANGE=1 run --dry-run; check "dry run pushes nothing" $? 0 1 0
setup; STUB_CHANGE=1 STUB_CI=1 run; check "CI failure notifies" $? 1 2 1
setup; echo x >>"$work/Projects/demo/package.json"; STUB_CHANGE=1 run
check "dirty checkout is skipped" $? 1 1 1

out=$(PATH="$work/bin:$PATH" MAINTAIN_LIST="$work/list" MAINTAIN_STATE="$work/state" "$script" --status)
case $out in demo:\ last\ run\ *) ;; *) echo "FAIL: status printed: $out"; fail=1 ;; esac

: >"$work/state/demo.held"
out=$(PATH="$work/bin:$PATH" MAINTAIN_LIST="$work/list" MAINTAIN_STATE="$work/state" "$script" --status)
case $out in *' 0 held behind'*) ;; *) echo "FAIL: empty held file printed: $out"; fail=1 ;; esac

rm -f "$work/notified"; rm "$work/list"; run; check "missing list notifies" $? 1 1 1

[ "$fail" = 0 ] && echo "maintain-projects.test.sh: all cases passed"
exit "$fail"
