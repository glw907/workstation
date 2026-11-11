"""Tests for the claude-tail-guard PreToolUse hook, driven by subprocess."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parent.parent / "bin/.local/bin/claude-tail-guard"

DENIED = [
    "bash scripts/check.sh | tee out.log | tail",
    "bash scripts/gate.sh |& tail -5",
    "git status\nnpm test | tail",
    "echo x && cairn-run-gate 'y' | tail -3",
    "npm run check:cairn|&tail",
    "npm test | tail&",
]

# A lone guarded pipeline ending in tail or head is rewritten, not denied.
REWRITTEN = [
    ("cairn-run-gate 'bash scripts/check.sh' | tail -5", "cairn-run-gate 'bash scripts/check.sh'"),
    ("bash scripts/gate.sh 2>&1 | head -40", "bash scripts/gate.sh 2>&1"),
    ("ci-green 12 | tail -1", "ci-green 12"),
    ("npm test | tail -20", "npm test"),
    ("npm run check:cairn 2>&1 | tail", "npm run check:cairn 2>&1"),
    ("gh pr checks 7 --watch | tail -3", "gh pr checks 7 --watch"),
    ("timeout 600 cairn-run-gate 'bash scripts/check.sh' | tail", "timeout 600 cairn-run-gate 'bash scripts/check.sh'"),
    ("CI=1 npm test | head", "CI=1 npm test"),
    ("timeout -k 5 600 npm test | tail", "timeout -k 5 600 npm test"),
    ("env CI=1 npm test | tail", "env CI=1 npm test"),
    ("time npm test | head", "time npm test"),
    ("npm test | tail | head -2", "npm test"),
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
    "cairn-run-gate --records | tail -5",
    "cairn-run-gate --receipt 2>&1 | head -40",
    "bash scripts/gate.sh --dry-run | tail",
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
    assert "nothing in this Bash call ran" in result.stderr


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


@pytest.mark.parametrize(("command", "expected"), REWRITTEN)
def test_rewritten(command, expected):
    result = run_hook({"tool_input": {"command": command}})
    assert result.returncode == 0
    assert result.stderr == ""
    updated = json.loads(result.stdout)["hookSpecificOutput"]["updatedInput"]
    assert updated == {"command": expected}


def test_unclean_strip_is_denied():
    result = run_hook({"tool_input": {"command": "cairn-run-gate 'a | tail' | tail"}})
    assert result.returncode == 2


def test_lone_tail_is_rewritten_with_input_preserved():
    tool_input = {
        "command": "cairn-run-gate 'npm run check' 2>&1 | tail -5",
        "timeout": 600000,
        "description": "Run the gate",
    }
    result = run_hook({"tool_input": tool_input})
    assert result.returncode == 0
    output = json.loads(result.stdout)["hookSpecificOutput"]
    assert output["hookEventName"] == "PreToolUse"
    assert "permissionDecision" not in output
    assert output["updatedInput"] == {
        "command": "cairn-run-gate 'npm run check' 2>&1",
        "timeout": 600000,
        "description": "Run the gate",
    }


def test_rewrite_keeps_quoted_expansion_byte_for_byte():
    command = 'cairn-run-gate "$X" 2>&1 | head -40'
    result = run_hook({"tool_input": {"command": command}})
    assert result.returncode == 0
    updated = json.loads(result.stdout)["hookSpecificOutput"]["updatedInput"]
    assert updated["command"] == 'cairn-run-gate "$X" 2>&1'
