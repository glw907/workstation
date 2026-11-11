#!/usr/bin/env bash
set -uo pipefail

# scripts/check.sh: the one gate for this repo. A pass, a pre-push, or a
# "did I break anything" moment runs this and nothing else; green here is
# what "the gate passed" means. Individual checks stay runnable on their own.
#
# Usage: scripts/check.sh [--changed] [--plan] [--leg NAME]...
#
#   --changed  run only the legs the working tree's changes touch, plus the legs that
#              always run (gitleaks, retired names, claude refs, tooling-sync lint)
#   --plan     print the legs that would run, one per line, and run none
#   --leg      run only the named leg (repeatable); an unknown name exits 2
#
# The changed set is `git diff --name-only HEAD` plus the untracked files; on a clean tree it
# is the last commit. CHECK_CHANGED_FILES (newline-separated paths) replaces it, for tests.
# Each leg declares a claim: an extended regex over repo-relative paths, or `shebang-bash`
# (a changed file that exists and whose first line names bash), or `-` for none. A leading
# `+` marks a leg that always runs. A changed path that no leg claims selects every leg, and
# so does a change to this script or to scripts/gate.sh.

# Keep bytecode caches out of the stow packages; stow would link them into
# $HOME (it happened; see docs/HISTORY.md 2026-08-30).
export PYTHONDONTWRITEBYTECODE=1

cd "$(dirname "$0")/.." || exit 2
fail=0

changed_only=0 plan_only=0 only=" "
while [ $# -gt 0 ]; do
    case $1 in
    --changed) changed_only=1 ;;
    --plan) plan_only=1 ;;
    --leg)
        only="$only${2:?--leg needs a name} "
        shift
        ;;
    *)
        echo "check: unknown argument $1" >&2
        exit 2
        ;;
    esac
    shift
done

# changed_files prints the changed set, one path per line.
changed_files() {
    if [ -n "${CHECK_CHANGED_FILES+x}" ]; then
        printf '%s\n' "$CHECK_CHANGED_FILES"
        return
    fi
    local files
    files=$(
        git diff --name-only HEAD
        git ls-files --others --exclude-standard
    )
    if [ -z "$files" ] && git rev-parse --verify -q HEAD~1 >/dev/null; then
        files=$(git diff --name-only HEAD~1..HEAD)
    fi
    printf '%s\n' "$files"
}

# claim_matches CLAIM PATH: true when the claim holds for the changed path.
claim_matches() {
    local claim=${1#+} path=$2
    case $claim in
    -) return 1 ;;
    shebang-bash)
        [ -f "$path" ] && head -n1 "$path" 2>/dev/null | grep -aq '^#!.*bash'
        ;;
    *) printf '%s\n' "$path" | grep -Eq -- "$claim" ;;
    esac
}

check_bash_syntax() {
    # Every tracked file whose shebang names bash, wherever it lives
    # (extensionless skill scripts included).
    local f ok=0
    while IFS= read -r f; do
        if head -1 "$f" 2>/dev/null | grep -q '^#!.*bash'; then
            bash -n "$f" || ok=1
        fi
    done < <(git ls-files)
    return "$ok"
}

check_shellcheck() {
    # Warning-level findings over the same files check_bash_syntax reads. bin/.local/bin/check-drift
    # is excluded from SC2140 only: its line 173 carries a finding in an auth-data file this pass
    # leaves alone (BACKLOG has the item). Any other finding there still fails.
    if ! command -v shellcheck >/dev/null 2>&1; then
        echo "shellcheck is not installed (brew install shellcheck)" >&2
        return 1
    fi
    local f ok=0
    while IFS= read -r f; do
        if head -1 "$f" 2>/dev/null | grep -q '^#!.*bash'; then
            if [ "$f" = bin/.local/bin/check-drift ]; then
                shellcheck -S warning --exclude=SC2140 "$f" || ok=1
            else
                shellcheck -S warning "$f" || ok=1
            fi
        fi
    done < <(git ls-files)
    return "$ok"
}

check_no_old_names() {
    # The old app and hook names, and the old planning folder, stay gone from live files. The
    # brackets keep this pattern from matching its own line. git grep exits 1 when nothing
    # matches. The planning folders and the move records cite these names as history.
    if git grep -n -I -i -E 'review[-_ ]?desk|claude-desk-[r]eminder|docs/[s]uperpowers' -- . \
        ':!docs/specs/' ':!docs/plans/' ':!docs/research/' ':!docs/HISTORY.md' \
        ':!scripts/check-moves.sh' ':!tests/check-moves.test.sh' ':!tests/fixtures/ci-green/pr-107-files.txt'; then
        echo "a retired name is back in a live file" >&2
        return 1
    fi
    if [ -n "$(git ls-files 'docs/[s]uperpowers/*')" ]; then
        echo "a tracked file is back under the retired planning folder" >&2
        return 1
    fi
}

# Shared claim fragments.
SKILLS='^(\.claude/skills/|claude/\.claude/skills/)'
GUIDED='^(\.claude/skills/|claude/\.claude/(skills|agents)/|claude/\.claude/(settings\.json|CLAUDE\.md)$)'

# legs lists every leg once. In the "collect" pass, run records a leg's name and claim; in the
# "exec" pass it runs the selected ones. run NAME CLAIM DESCRIPTION COMMAND...
legs() {
    run bash-n shebang-bash "bash -n over tracked shell scripts" check_bash_syntax
    run shellcheck shebang-bash "shellcheck -S warning over tracked shell scripts" check_shellcheck
    run tellgrader '^claude/\.claude/skills/writing-voice/evals/tellgrader/' \
        "tellgrader go check" make -C claude/.claude/skills/writing-voice/evals/tellgrader check
    run py-comments '\.py$|^ruff\.toml$|^scripts/check-py-comments\.sh$|^bin/\.local/bin/' \
        "ruff docstring rules (python)" bash scripts/check-py-comments.sh
    run retired-names '+^(BACKLOG|README)\.md$|^docs/' "retired names absent" check_no_old_names
    run roadmap-refs '^(claude/\.claude/skills|\.claude/skills|bin)/|^scripts/(check-roadmap-refs\.sh|roadmap-refs-allow\.txt)$' \
        "non-cairn ROADMAP references absent" bash scripts/check-roadmap-refs.sh
    run roadmap-refs-test '^tests/check-roadmap-refs\.test\.sh$|^(claude/\.claude/skills|\.claude/skills|bin)/|^scripts/(check-roadmap-refs\.sh|roadmap-refs-allow\.txt)$' \
        "roadmap-refs check test" bash tests/check-roadmap-refs.test.sh
    run memory-write-check '^tests/claude-memory-write-check\.test\.sh$|^bin/\.local/bin/claude-memory-write-check$' \
        "claude-memory-write-check hook" bash tests/claude-memory-write-check.test.sh
    run pytest "\\.py\$|^ruff\\.toml\$|^tests/(fixtures|vale)/|^bin/\\.local/bin/(claude-(block-pass|launch-guard|merge-guard|secret-guard|tail-guard|tierguard|tooling-sync|pass|worktree-busy)|cairn-run-gate|ci-green|cleanroom|phone-check|pass-report|vale-hook|voipms-sms|pass-access|pass-count|pass-sitting|secret-receive|ws-pass-key|planner)\$|^bin/\\.local/share/cleanroom/|^scripts/(check-claude-refs\\.py|check\\.sh|gate\\.sh|githooks/)|^vale/|^claude/\\.claude/(settings\\.json|tooling/|docs/bluefin-admin)|^bluefin/(Brewfile|layered-packages\\.txt|etc/sudoers\\.d/)|$SKILLS" \
        "vale-hook test suite" uv run --with pytest --no-project python -m pytest tests/ -q
    run vale-fixtures '^tests/(vale/|test_vale_hook\.py$)|^vale/|^bin/\.local/bin/vale-hook$' \
        "vale style fixtures" bash tests/vale/run-fixtures.sh
    run check-drift-initiatives '^tests/(check-drift-initiatives\.test\.sh$|fixtures/initiatives/)|^bin/\.local/bin/check-drift$' \
        "check-drift initiatives leg" bash tests/check-drift-initiatives.test.sh
    run gather-dotfiles '^tests/(gather-dotfiles-initiatives\.test\.sh$|fixtures/initiatives/)|^claude/\.claude/gather-dotfiles\.sh$' \
        "gather-dotfiles initiatives leg" bash tests/gather-dotfiles-initiatives.test.sh
    run secret-set-overrides '^tests/secret-set-overrides\.test\.sh$|^scripts/secrets/|^bin/\.local/bin/ws-pass-key$|^secrets/' \
        "secret-set.sh path overrides" bash tests/secret-set-overrides.test.sh
    run secret-set-quoting '^tests/secret-set-quoting\.test\.sh$|^scripts/secrets/|^secrets/' \
        "secret-set.sh value quoting" bash tests/secret-set-quoting.test.sh
    run secret-store-flags '^tests/secret-store-flags\.test\.sh$|^scripts/secrets/|^bin/\.local/bin/(secret-receive|ws-pass-key)$|^secrets/' \
        "secret store flags, lock, and drop check" bash tests/secret-store-flags.test.sh
    run ws-pass-key '^tests/(ws-pass-key\.test\.sh$|fixtures/pass-cli$)|^scripts/secrets/|^bin/\.local/bin/ws-pass-key$|^secrets/' \
        "ws-pass-key agent-token read" bash tests/ws-pass-key.test.sh
    run claude-pass '^tests/(claude-pass\.test\.sh$|fixtures/pass-cli$)|^bin/\.local/bin/claude-pass$' \
        "claude-pass agent run" bash tests/claude-pass.test.sh
    run secret-receive-pass '^tests/(secret-receive-pass\.test\.sh$|fixtures/pass-cli$)|^bin/\.local/bin/(secret-receive|claude-sudo-setup)$|^scripts/secrets/|^secrets/' \
        "secret-receive --pass and the sudo dialog" bash tests/secret-receive-pass.test.sh
    run pass-count '^tests/(pass-count\.test\.sh$|fixtures/pass-cli$)|^bin/\.local/bin/pass-count$' \
        "pass-count counts and hashes" bash tests/pass-count.test.sh
    run pass-access '^tests/(pass-access\.test\.sh$|fixtures/pass-access-capture\.tsv$)|^bin/\.local/bin/(claude-pass|pass-access|ws-pass-key)$' \
        "pass-access rows" bash tests/pass-access.test.sh
    run pass-sitting '^tests/(pass-sitting\.test\.sh$|fixtures/(pass-sitting/|pass-cli$))|^bin/\.local/bin/pass-sitting$' \
        "pass-sitting against the fake pass-cli" bash tests/pass-sitting.test.sh
    run check-drift-proton '^tests/(check-drift-proton\.test\.sh$|fixtures/pass-access-capture\.tsv$)|^bin/\.local/bin/(check-drift|claude-pass|pass-access|ws-pass-key)$|^secrets/proton-grants\.tsv$' \
        "check-drift Proton Pass leg" bash tests/check-drift-proton.test.sh
    run workstation-sync '^tests/workstation-sync\.test\.sh$|^bin/\.local/bin/(check-drift|claude-tooling-sync|workstation-[a-z]+)$|^bluefin/|^bin/\.local/share/cleanroom/settings\.json$|^claude/\.claude/settings\.json$' \
        "workstation-sync, workstation-syncthing, and check-drift's work leg" bash tests/workstation-sync.test.sh
    run check-moves '^tests/check-moves\.test\.sh$|^scripts/check-moves\.sh$' \
        "check-moves draft check" bash tests/check-moves.test.sh
    run ci-green '^tests/(ci-green\.test\.mjs$|fixtures/ci-green/)|^bin/\.local/bin/ci-green(-lib\.mjs)?$' \
        "ci-green test" node tests/ci-green.test.mjs
    run cairn-run-gate '^tests/cairn-run-gate\.test\.sh$|^bin/\.local/bin/cairn-run-gate$|^claude/\.claude/agents/site-implementer\.md$' \
        "cairn-run-gate vanish handling" bash tests/cairn-run-gate.test.sh
    run claude-denied-log '^tests/claude-denied-log\.test\.sh$|^bin/\.local/bin/claude-denied-log$' \
        "claude-denied-log hook" bash tests/claude-denied-log.test.sh
    run cairn-docs-cycle '^tests/cairn-docs-cycle\.test\.sh$|^bin/\.local/bin/cairn-docs-cycle$' \
        "cairn-docs-cycle argument guard" bash tests/cairn-docs-cycle.test.sh
    run model-review-notify '^tests/model-review-notify\.test\.sh$|^bin/\.local/bin/(cairn-docs-cycle|model-review-notify|survey-writing-review)$|^upkeep/\.config/systemd/user/model-review\.service$' \
        "model-review-notify gates" bash tests/model-review-notify.test.sh
    run monitor-subscribe '^tests/monitor-subscribe\.test\.sh$|^bin/\.local/bin/monitor-subscribe$' \
        "monitor-subscribe service" bash tests/monitor-subscribe.test.sh
    run phonebook-units '^tests/phonebook-units\.test\.sh$|^bluefin/etc/systemd/system/phonebook-' \
        "phonebook units verify" bash tests/phonebook-units.test.sh
    run maintain-projects '^tests/maintain-projects\.test\.sh$|^bin/\.local/bin/maintain-projects$' \
        "maintain-projects cases" bash tests/maintain-projects.test.sh
    run guidance-cite "^tests/check-guidance-cite\\.test\\.sh\$|^scripts/check-guidance-cite\\.sh\$|$GUIDED" \
        "guidance citation (warning only)" bash scripts/check-guidance-cite.sh
    run guidance-cite-test "^tests/check-guidance-cite\\.test\\.sh\$|^scripts/check-guidance-cite\\.sh\$|$GUIDED" \
        "guidance citation test" bash tests/check-guidance-cite.test.sh
    run context-budget-test "^tests/claude-context-budget\\.test\\.sh\$|^bin/\\.local/bin/(claude-context-budget|planner)\$|^claude/\\.claude/(CLAUDE\\.md|docs/claude-md-archive\\.md)\$|$SKILLS" \
        "claude-context-budget line cap" bash tests/claude-context-budget.test.sh
    run pass-load-test "^tests/claude-pass-load\\.test\\.sh\$|^bin/\\.local/bin/(claude-pass-load|claude-pass|planner)\$|^claude/\\.claude/(CLAUDE\\.md|docs/voice/)|$SKILLS" \
        "claude-pass-load" bash tests/claude-pass-load.test.sh
    run worktree-busy '^tests/claude-worktree-busy\.test\.sh$|^bin/\.local/bin/claude-worktree-busy$' \
        "claude-worktree-busy" bash tests/claude-worktree-busy.test.sh
    run claude-md-budget '^claude/\.claude/CLAUDE\.md$|^bin/\.local/bin/claude-context-budget$' \
        "CLAUDE.md context budget" bash bin/.local/bin/claude-context-budget claude/.claude/CLAUDE.md
    run skill-caps "^bin/\\.local/bin/claude-context-budget\$|$SKILLS" \
        "pass-core word caps" bin/.local/bin/claude-context-budget --skill-caps --root .
    run pass-loads "^bin/\\.local/bin/claude-pass-load\$|^claude/\\.claude/CLAUDE\\.md\$|^claude/\\.claude/docs/voice/approval-brief\\.md\$|$SKILLS" \
        "pass role loads" bin/.local/bin/claude-pass-load --check --root .
    run claude-refs '+^claude/\.claude/.*\.md$|^scripts/check-claude-refs\.py$|^claude/\.claude/tooling/retired-phrases\.txt$' \
        "claude refs and retired phrases" python3 scripts/check-claude-refs.py check --root .
    run tooling-sync-lint '+^claude/\.claude/(tooling|skills)/|^bin/\.local/bin/claude-tooling-sync$' \
        "claude-tooling-sync lint" bin/.local/bin/claude-tooling-sync lint --root .
    run check-lanes '^tests/check-lanes\.test\.sh$' \
        "check.sh lanes and gate.sh flags" bash tests/check-lanes.test.sh
    run gitleaks '+-' "gitleaks working-tree scan" gitleaks dir . --no-banner --redact
}

# Pass 1, collect: record each leg's name, claim, and whether it always runs.
names=() claims=() always=()
run() {
    local name=$1 claim=$2
    names+=("$name")
    case $claim in
    +*) always+=(1) ;;
    *) always+=(0) ;;
    esac
    claims+=("${claim#+}")
}
legs

# A leg named on --leg must exist.
for want in $only; do
    found=0
    for n in "${names[@]}"; do [ "$n" = "$want" ] && found=1; done
    if [ "$found" = 0 ]; then
        echo "check: no leg named $want; the legs are:" >&2
        printf '%s\n' "${names[@]}" >&2
        exit 2
    fi
done

# Select the legs.
select_all=1
selected=()
if [ "$changed_only" = 1 ]; then
    select_all=0
    changed=$(changed_files)
    [ -n "$changed" ] || echo "check: no changed files; running only the legs that always run" >&2
    while IFS= read -r path; do
        [ -n "$path" ] || continue
        if printf '%s\n' "$path" | grep -Eq '^scripts/(check|gate)\.sh$'; then
            echo "check: $path changed; running every leg" >&2
            select_all=1
            continue
        fi
        claimed=0
        for i in "${!names[@]}"; do
            if claim_matches "${claims[$i]}" "$path"; then
                claimed=1
                selected[i]=1
            fi
        done
        if [ "$claimed" = 0 ]; then
            echo "check: no leg claims $path; running every leg" >&2
            select_all=1
        fi
    done <<<"$changed"
    for i in "${!names[@]}"; do
        [ "${always[$i]}" = 1 ] && selected[i]=1
    done
fi

# Pass 2, exec: run the selected legs.
ran=0 skipped=0
start=$SECONDS
wanted() { # index
    local i=$1
    [ "$only" = " " ] || [[ $only == *" ${names[$i]} "* ]] || return 1
    [ "$select_all" = 1 ] || [ "${selected[$i]:-0}" = 1 ]
}
cur=0
run() {
    local name=$1 desc=$3 i=$cur t0=$SECONDS
    cur=$((cur + 1))
    shift 3
    if ! wanted "$i"; then
        skipped=$((skipped + 1))
        return
    fi
    ran=$((ran + 1))
    if [ "$plan_only" = 1 ]; then
        echo "$name"
        return
    fi
    echo ""
    echo "== $name: $desc =="
    if ! "$@"; then
        echo "FAILED: $*" >&2
        fail=1
    fi
    echo "-- $name: $((SECONDS - t0))s"
}
legs
[ "$plan_only" = 1 ] && exit 0

echo ""
echo "legs run: $ran, legs skipped: $skipped, total: $((SECONDS - start))s"
if [[ "$fail" -eq 0 ]]; then
    echo "GATE: all checks passed"
else
    echo "GATE: FAILED (see above)" >&2
fi
exit "$fail"
