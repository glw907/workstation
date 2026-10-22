"""Tests for the claude-merge-guard PreToolUse hook, driven by subprocess with gh stubbed."""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parent.parent / "bin/.local/bin/claude-merge-guard"

STEPS = "Run `stow -R bin`, then `claude-tooling-sync apply`.\nCheck: `grep model ~/.claude/settings.json`."
WITH_SECTION = f"Adds a thing.\n\n## Before merge\n\n{STEPS}\n\n## Found, not done\n\nnone\n"
WITHOUT_SECTION = "Adds a thing.\n\n## Found, not done\n\nnone\n"

GH_STUB = """#!/bin/sh
echo "$@" >> "$STUB_LOG"
if [ "$1 $2" = "pr view" ]; then
  cat "$STUB_BODY"
fi
"""


@pytest.fixture
def env(tmp_path):
    """Build an environment whose PATH starts with a stub gh that logs its calls."""
    stub = tmp_path / "gh"
    stub.write_text(GH_STUB)
    stub.chmod(0o755)
    environment = dict(os.environ)
    environment["PATH"] = f"{tmp_path}:{environment['PATH']}"
    environment["STUB_LOG"] = str(tmp_path / "calls.log")
    environment["STUB_BODY"] = str(tmp_path / "body.md")
    return environment


def run_hook(env, command, body=WITH_SECTION):
    """Run the hook on a Bash command against a stubbed PR body."""
    Path(env["STUB_BODY"]).write_text(body)
    return subprocess.run(
        [sys.executable, str(SCRIPT)],
        input=json.dumps({"tool_input": {"command": command}}),
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )


def decision(result):
    """Return the hookSpecificOutput object of a denial."""
    assert result.returncode == 0
    return json.loads(result.stdout)["hookSpecificOutput"]


@pytest.mark.parametrize(
    "command",
    [
        "gh pr merge 16",
        "gh pr merge 16 --merge --match-head-commit abc123",
        "cd x && gh pr merge 16 --merge",
        "gh pr merge 16 -R owner/repo",
        "gh pr merge -R owner/repo 16",
        "PREMERGE_DONE=4 gh pr merge 16",
    ],
)
def test_blocks_with_section(env, command):
    out = decision(run_hook(env, command))
    assert out["hookEventName"] == "PreToolUse"
    assert out["permissionDecision"] == "deny"
    assert STEPS in out["permissionDecisionReason"]
    assert "Found, not done" not in out["permissionDecisionReason"]
    assert "PREMERGE_DONE=16" in out["permissionDecisionReason"]


@pytest.mark.parametrize(
    "command",
    [
        "PREMERGE_DONE=16 gh pr merge 16",
        "cd x && PREMERGE_DONE=16 gh pr merge 16 --merge",
    ],
)
def test_acknowledged_passes(env, command):
    result = run_hook(env, command)
    assert (result.returncode, result.stdout) == (0, "")


def test_no_number_tells_merger_to_name_it(env):
    reason = decision(run_hook(env, "PREMERGE_DONE=16 gh pr merge --merge"))["permissionDecisionReason"]
    assert "name the PR number" in reason
    assert "<n>" not in reason


def test_pr_without_section_passes(env):
    result = run_hook(env, "gh pr merge 16 --merge", body=WITHOUT_SECTION)
    assert (result.returncode, result.stdout) == (0, "")


@pytest.mark.parametrize("command", ["git status", "gh pr view 16", "echo gh pr merge 16", "gh pr list"])
def test_other_commands_never_call_gh(env, command):
    result = run_hook(env, command)
    assert (result.returncode, result.stdout) == (0, "")
    assert not Path(env["STUB_LOG"]).exists()


def test_repo_flag_reaches_pr_view(env):
    run_hook(env, "gh pr merge 5 -R owner/repo")
    assert "-R owner/repo" in Path(env["STUB_LOG"]).read_text()


def test_body_text_is_never_executed(env, tmp_path):
    marker = tmp_path / "ran"
    body = f"## Before merge\n\n$(touch {marker})\n`touch {marker}`\n"
    out = decision(run_hook(env, "gh pr merge 16", body=body))
    assert out["permissionDecision"] == "deny"
    assert not marker.exists()


def test_unreadable_pr_is_denied(env):
    Path(env["STUB_BODY"]).unlink(missing_ok=True)  # the stub's cat then fails
    result = subprocess.run(
        [sys.executable, str(SCRIPT)],
        input=json.dumps({"tool_input": {"command": "gh pr merge 16"}}),
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )
    assert decision(result)["permissionDecision"] == "deny"


def test_malformed_input_exits_zero(env):
    for stdin in ("not json", json.dumps({}), json.dumps({"tool_input": {"command": "gh pr merge 'x"}})):
        result = subprocess.run(
            [sys.executable, str(SCRIPT)], input=stdin, capture_output=True, text=True, check=False, env=env
        )
        assert (result.returncode, result.stdout, result.stderr) == (0, "", "")


def run_hook_raw(env, command):
    """Run the hook without writing a stub body first."""
    return subprocess.run(
        [sys.executable, str(SCRIPT)],
        input=json.dumps({"tool_input": {"command": command}}),
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )


# False positives from real sessions (2026-10-19 to 2026-10-21): a PR created and merged in one
# command, a redirect read as the PR number, and merge text inside a heredoc.
def test_pr_created_in_same_command_uses_its_body(env):
    Path(env["STUB_BODY"]).unlink(missing_ok=True)  # the PR does not exist yet, so view fails
    command = 'gh pr create --title "t" --body "Ledger update." && gh pr merge upload-quota --merge'
    result = run_hook_raw(env, command)
    assert (result.returncode, result.stdout) == (0, "")


def test_pr_created_in_same_command_with_section_is_denied(env):
    Path(env["STUB_BODY"]).unlink(missing_ok=True)
    command = f"gh pr create --title t --body '{WITH_SECTION}' && gh pr merge b --merge"
    out = decision(run_hook_raw(env, command))
    assert STEPS in out["permissionDecisionReason"]


def test_pr_created_from_body_file(env, tmp_path):
    Path(env["STUB_BODY"]).unlink(missing_ok=True)
    body = tmp_path / "pr.md"
    body.write_text(WITHOUT_SECTION)
    result = run_hook_raw(env, f"gh pr create -t t -F {body}; gh pr merge b --merge")
    assert (result.returncode, result.stdout) == (0, "")


def test_unreadable_pr_without_create_is_still_denied(env):
    Path(env["STUB_BODY"]).unlink(missing_ok=True)
    assert decision(run_hook_raw(env, "gh pr merge b --merge"))["permissionDecision"] == "deny"


def test_redirect_is_not_the_pr_number(env):
    run_hook(env, "gh pr merge --merge --delete-branch=false 2>&1 | tail -2", body=WITHOUT_SECTION)
    assert "pr view --json" in Path(env["STUB_LOG"]).read_text()


def test_attached_redirect_is_not_the_pr_number(env):
    run_hook(env, "gh pr merge 2>/dev/null --merge", body=WITHOUT_SECTION)
    assert "pr view --json" in Path(env["STUB_LOG"]).read_text()


def test_merge_text_in_heredoc_is_not_checked(env):
    command = "python3 -I - <<'EOF'\nnote = 'gh pr merge 5 later'\ngh pr merge 7\nEOF\ngit status"
    result = run_hook(env, command)
    assert (result.returncode, result.stdout) == (0, "")
    assert not Path(env["STUB_LOG"]).exists()
