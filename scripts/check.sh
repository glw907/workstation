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
run "vale-hook test suite" uv run --with pytest --no-project python -m pytest tests/ -q
run "vale style fixtures" bash tests/vale/run-fixtures.sh
run "docs-page-chain derivation test" node tests/docs-page-chain-derivation.test.mjs
run "docs-page-chain outline test" node tests/docs-page-chain-outline.test.mjs
run "pass-execute runners test" node tests/pass-execute-runners.test.mjs
run "ci-green test" node tests/ci-green.test.mjs
run "cairn-run-gate vanish handling" bash tests/cairn-run-gate.test.sh
run "claude-clock-stop hook" bash tests/claude-clock-stop.test.sh
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
