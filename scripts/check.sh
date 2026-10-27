#!/usr/bin/env bash
set -uo pipefail

# scripts/check.sh: the one gate for this repo. A pass, a pre-push, or a
# "did I break anything" moment runs this and nothing else; green here is
# what "the gate passed" means. Individual checks stay runnable on their own.

# Keep bytecode caches out of the stow packages; stow would link them into
# $HOME (it happened; see docs/HISTORY.md 2026-08-30).
export PYTHONDONTWRITEBYTECODE=1

cd "$(dirname "$0")/.."
fail=0

run() {
    echo ""
    echo "== $1 =="
    shift
    if ! "$@"; then
        echo "FAILED: $*" >&2
        fail=1
    fi
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

run "bash -n over tracked shell scripts" check_bash_syntax
run "tellgrader go check" make -C claude/.claude/skills/writing-voice/evals/tellgrader check
run "ruff docstring rules (python)" bash scripts/check-py-comments.sh
check_no_old_names() {
    # The old app and hook names, and the old planning folder, stay gone from live files. The
    # brackets keep this pattern from matching its own line. git grep exits 1 when nothing
    # matches. The planning folders and the move records cite these names as history.
    if git grep -n -I -i -E 'review[-_ ]?desk|claude-desk-[r]eminder|docs/[s]uperpowers' -- . \
        ':!docs/specs/' ':!docs/plans/' ':!docs/research/' ':!docs/HISTORY.md' \
        ':!scripts/check-moves.sh' ':!tests/check-moves.test.sh' ':!tests/fixtures/ci-green/pr-107-files.txt' \
        ':!claude/.claude/skills/brainstorming/SKILL.md'; then
        echo "a retired name is back in a live file" >&2
        return 1
    fi
    if [ -n "$(git ls-files 'docs/[s]uperpowers/*')" ]; then
        echo "a tracked file is back under the retired planning folder" >&2
        return 1
    fi
}

run "retired names absent" check_no_old_names
run "non-cairn ROADMAP references absent" bash scripts/check-roadmap-refs.sh
run "roadmap-refs check test" bash tests/check-roadmap-refs.test.sh
run "claude-memory-write-check hook" bash tests/claude-memory-write-check.test.sh
run "vale-hook test suite" uv run --with pytest --no-project python -m pytest tests/ -q
run "vale style fixtures" bash tests/vale/run-fixtures.sh
run "check-drift initiatives leg" bash tests/check-drift-initiatives.test.sh
run "gather-dotfiles initiatives leg" bash tests/gather-dotfiles-initiatives.test.sh
run "secret-set.sh path overrides" bash tests/secret-set-overrides.test.sh
run "secret-set.sh value quoting" bash tests/secret-set-quoting.test.sh
run "secret store flags, lock, and drop check" bash tests/secret-store-flags.test.sh
run "ws-pass-key agent-token read" bash tests/ws-pass-key.test.sh
run "claude-pass agent run" bash tests/claude-pass.test.sh
run "secret-receive --pass and the sudo dialog" bash tests/secret-receive-pass.test.sh
run "pass-count counts and hashes" bash tests/pass-count.test.sh
run "check-drift Proton Pass leg" bash tests/check-drift-proton.test.sh
run "check-moves draft check" bash tests/check-moves.test.sh
run "ci-green test" node tests/ci-green.test.mjs
run "cairn-run-gate vanish handling" bash tests/cairn-run-gate.test.sh
run "claude-clock-stop hook" bash tests/claude-clock-stop.test.sh
run "monitor-subscribe service" bash tests/monitor-subscribe.test.sh
run "phonebook units verify" bash tests/phonebook-units.test.sh
run "guidance citation (warning only)" bash scripts/check-guidance-cite.sh
run "guidance citation test" bash tests/check-guidance-cite.test.sh
run "claude-context-budget line cap" bash tests/claude-context-budget.test.sh
run "CLAUDE.md context budget" bash bin/.local/bin/claude-context-budget claude/.claude/CLAUDE.md
run "ratchet baseline" python3 claude/.claude/tooling/ratchet.py check --root .
run "claude-tooling-sync lint" bin/.local/bin/claude-tooling-sync lint --root .
run "gitleaks working-tree scan" gitleaks dir . --no-banner --redact

echo ""
if [[ "$fail" -eq 0 ]]; then
    echo "GATE: all checks passed"
else
    echo "GATE: FAILED (see above)" >&2
fi
exit "$fail"
