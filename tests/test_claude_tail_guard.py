"""Tests for the claude-tail-guard PreToolUse hook, driven by subprocess."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parent.parent / "bin/.local/bin/claude-tail-guard"

DENIED = [
    "cairn-run-gate 'bash scripts/check.sh' | tail -5",
    "bash scripts/gate.sh 2>&1 | head -40",
    "ci-green 12 | tail -1",
    "npm test | tail -20",
    "npm run check:cairn 2>&1 | tail",
    "gh pr checks 7 --watch | tail -3",
    "bash scripts/check.sh | tee out.log | tail",
    "bash scripts/gate.sh |& tail -5",
    "timeout 600 cairn-run-gate 'bash scripts/check.sh' | tail",
    "CI=1 npm test | head",
    "git status\nnpm test | tail",
    "npm run check:cairn|&tail",
    "npm test | tail&",
    "(npm test) | tail",
    "timeout -k 5 600 npm test | tail",
    "env CI=1 npm test | tail",
    "time npm test | head",
    "gh pr checks 7 --interval 5 --watch | tail",
]

HEREDOC_NO_APOSTROPHE = "git commit -F - <<'EOF'\nNotes on npm test | tail\nEOF"
HEREDOC_APOSTROPHE = "git commit -F - <<'EOF'\nIt's about npm test | tail\nEOF"
HEREDOC_SUBSTITUTION = (
    "git commit -m \"$(cat <<'EOF'\nIt's fine: npm test | tail\nEOF\n)\""
)
MULTILINE_MESSAGE = 'git commit -m "first line\nnpm test | tail\nlast line"'

ALLOWED = [
    "bash scripts/gate.sh",
    "cairn-run-gate 'bash scripts/check.sh' > /tmp/gate.log 2>&1",
    "npm test; git log --oneline | head -5",
    "npm test || echo failed",
    "tail -5 gate.log",
    "git log | head",
    "cat scripts/check.sh | head -20",
    "git diff -- scripts/gate.sh | head",
    "grep -n run scripts/check.sh | tail",
    "npm test\ngit log | head",
    "npm test 2>&1 && git log | head",
    HEREDOC_NO_APOSTROPHE,
    HEREDOC_APOSTROPHE,
    HEREDOC_SUBSTITUTION,
    MULTILINE_MESSAGE,
    "gh pr checks 7 | tail -3",
    "gh pr checks 7 --json name,state | head",
    "npm test --help | head",
    "cairn-run-gate --help | head -20",
    "bash scripts/check.sh -h | tail",
]


def run_hook(payload: object) -> subprocess.CompletedProcess:
    """Run the hook with a JSON payload on stdin."""
    return subprocess.run(
        [sys.executable, str(SCRIPT)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.mark.parametrize("command", DENIED)
def test_denied(command):
    result = run_hook({"tool_input": {"command": command}})
    assert result.returncode == 2
    assert "redirect" in result.stderr


@pytest.mark.parametrize("command", ALLOWED)
def test_allowed(command):
    result = run_hook({"tool_input": {"command": command}})
    assert result.returncode == 0
    assert result.stdout == ""
    assert result.stderr == ""


def test_no_command():
    for payload in ({}, {"tool_input": {}}, {"tool_input": None}):
        result = run_hook(payload)
        assert result.returncode == 0
        assert result.stderr == ""


def test_unparseable_input_exits_zero():
    result = run_hook({"tool_input": {"command": "npm test | tail 'unclosed"}})
    assert result.returncode == 0
    assert result.stderr == ""


def test_invalid_json_exits_zero():
    result = subprocess.run(
        [sys.executable, str(SCRIPT)],
        input="not json",
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
