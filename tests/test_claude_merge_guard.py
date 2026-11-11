"""Tests for the claude-merge-guard PreToolUse hook, driven by subprocess."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parent.parent / "bin/.local/bin/claude-merge-guard"


def run_hook(command):
    """Run the hook on a Bash command."""
    return subprocess.run(
        [sys.executable, str(SCRIPT)],
        input=json.dumps({"tool_input": {"command": command}}),
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.mark.parametrize(
    "command",
    [
        "gh pr merge 5",
        "gh pr merge 5 --merge",
        "gh pr merge 5 --merge --match-head-commit abc123",
        "gh pr merge -R owner/repo 5",
        "cd /x && gh pr merge 5",
        "git status; gh pr merge 5",
        "gh pr view 5 | gh pr merge 5",
        "# note\ngh pr merge 5",
        "timeout 60 gh pr merge 5",
        "command gh pr merge 5",
        "env FOO=1 gh pr merge 5",
        "nohup gh pr merge 5",
        "FOO=1 gh pr merge 5",
        "PREMERGE_DONE=5 gh pr merge 5",
        "echo $(gh pr merge 5)",
        "echo `gh pr merge 5`",
        "(gh pr merge 5)",
        "for n in 1 2; do gh pr merge $n --merge; done",
        "if true; then gh pr merge 5; fi",
        "while read n; do gh pr merge \"$n\"; done < prs",
        "{ gh pr merge 5; }",
        "! gh pr merge 5",
        "sudo gh pr merge 5",
        "echo 5 | xargs gh pr merge",
        "timeout -s KILL 60 gh pr merge 5",
        "2>/dev/null gh pr merge 5",
        "/usr/bin/gh pr merge 5",
        'out="$(gh pr merge 5 --merge 2>&1)"; echo "$out"',
        'echo "`gh pr merge 5`"',
    ],
)
def test_denies_every_merge_stage(command):
    result = run_hook(command)
    assert result.returncode == 0
    out = json.loads(result.stdout)["hookSpecificOutput"]
    assert out["hookEventName"] == "PreToolUse"
    assert out["permissionDecision"] == "deny"


def test_deny_message_names_replacements():
    reason = json.loads(run_hook("gh pr merge 5").stdout)["hookSpecificOutput"]["permissionDecisionReason"]
    assert "approval-queue merge <id>" in reason
    assert "approval-queue land <owner/repo#n> <claim>" in reason
    assert "approval-packet" in reason
    assert "--premerge-done" in reason


@pytest.mark.parametrize(
    "command",
    [
        "approval-queue merge 20261110T120000-1",
        'approval-queue land glw907/x#1 "Deny gh pr merge"',
        'git commit -m "Explain gh pr merge"',
        "echo 'gh pr merge 5'",
        "echo gh\\ pr\\ merge",
        "# gh pr merge 5",
        "git status\n# gh pr merge 5\ngit log",
        "gh pr view 5",
        "gh pr list",
        "git status",
        "python3 -I - <<'EOF'\nnote = 'gh pr merge 5 later'\ngh pr merge 7\nEOF\ngit status",
        "git commit -F - <<EOF\nRun gh pr merge 5\nEOF",
        'echo "$(git status) gh pr merge"',
        'echo "run `git log` then gh pr merge"',
        "sudo systemctl restart foo",
    ],
)
def test_allows_other_commands(command):
    result = run_hook(command)
    assert (result.returncode, result.stdout, result.stderr) == (0, "", "")


def test_malformed_input_exits_zero():
    for stdin in ("not json", json.dumps({}), json.dumps({"tool_input": {"command": 5}}), json.dumps([])):
        result = subprocess.run(
            [sys.executable, str(SCRIPT)], input=stdin, capture_output=True, text=True, check=False
        )
        assert (result.returncode, result.stdout, result.stderr) == (0, "", "")
