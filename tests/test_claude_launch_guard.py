"""Tests for the claude-launch-guard PreToolUse hook, driven by subprocess."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parent.parent / "bin/.local/bin/claude-launch-guard"
COMPLETE = "## Pre-flight\n\nPermissions checked: none needed.\nReviewed: plan-reviewer.\n\n## Tasks\n"
MISSING_REVIEW = "## Pre-flight\n\nPermissions checked: none needed.\n\n## Tasks\n"
LINES_OUTSIDE = "## Pre-flight\n\n- item\n\n## Tasks\n\nPermissions checked: x\nReviewed: x\n"


def run(command: str, cwd: Path, transcript: Path | None = None) -> str:
    """Return the hook's stdout for a Bash command run from cwd."""
    payload = json.dumps({"tool_input": {"command": command}, "cwd": str(cwd),
                          "transcript_path": str(transcript) if transcript else None})
    return subprocess.run([sys.executable, str(SCRIPT)], input=payload, text=True,
                          capture_output=True, check=True).stdout


@pytest.fixture
def repo(tmp_path):
    """Build a repo with one plan and a prompt file naming it."""
    plans = tmp_path / "docs/plans"
    plans.mkdir(parents=True)
    (plans / "a-prompt.txt").write_text("Execute docs/plans/a.md now.\n")
    return tmp_path


LAUNCH = 'claude --bg --model sonnet --name x "$(cat docs/plans/a-prompt.txt)"'


@pytest.mark.parametrize("plan,denied", [
    (COMPLETE, False), (MISSING_REVIEW, True), (LINES_OUTSIDE, True), ("no sections\n", True),
])
def test_plan_checks(repo, plan, denied):
    (repo / "docs/plans/a.md").write_text(plan)
    assert ("deny" in run(LAUNCH, repo)) is denied


def test_sibling_plan_found_when_prompt_names_none(repo):
    (repo / "docs/plans/a-prompt.txt").write_text("Go.\n")
    (repo / "docs/plans/a.md").write_text(MISSING_REVIEW)
    assert "deny" in run(LAUNCH, repo)


def test_cd_prefix_resolves_the_prompt(repo):
    (repo / "docs/plans/a.md").write_text(MISSING_REVIEW)
    assert "deny" in run(f"cd {repo} && {LAUNCH}", Path("/"))


@pytest.mark.parametrize("command", ["git status", 'claude --bg "just look around"', "claude -p hi"])
def test_other_commands_pass(repo, command):
    assert run(command, repo) == ""


@pytest.mark.parametrize("text,denied", [("skills: standards:plan-reviewer", False), ("no such skill", True)])
def test_session_must_have_the_standards_plugin(repo, tmp_path, text, denied):
    (repo / "docs/plans/a.md").write_text(COMPLETE)
    transcript = tmp_path / "t.jsonl"
    transcript.write_text(text)
    assert ("deny" in run(LAUNCH, repo, transcript)) is denied
