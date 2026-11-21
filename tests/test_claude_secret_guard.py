"""Tests for the credential-assignment rule in the claude-secret-guard PreToolUse hook."""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

GUARD = Path(__file__).resolve().parent.parent / "bin/.local/bin/claude-secret-guard"


def run(content):
    payload = {"tool_name": "Write", "tool_input": {"file_path": "/tmp/x", "content": content}}
    return subprocess.run(
        [sys.executable, str(GUARD)], input=json.dumps(payload), capture_output=True, text=True, check=False
    )


# Lines that blocked real sessions (2026-10-18 to 2026-10-21): a file path and self-declared fakes.
@pytest.mark.parametrize(
    "line",
    [
        "RESTIC_PASSWORD_FILE=/etc/servers/restic-password",
        "export TLS_SECRET_PATH=./fixtures/tls-secret.pem",
        "TOKEN=read-token-dummy-value",
        "    CF_WS_SERVERS_TOKEN=dummy-token-9f3a CF_ACCOUNT_ID=acct123",
        "export FASTMAIL_API_TOKEN=FMTOK-geoff-sentinel",
        "API_TOKEN=example-token-for-the-docs",
        "export STRIPE_SECRET=fake_aB3dE5gH7jK9mN1p",
    ],
)
def test_passes_paths_and_fakes(line):
    assert run(line + "\n").returncode == 0


# The value literal is split so this file carries no key-shaped string itself.
RANDOM = "aB3dE5gH7jK9" + "mN1pQ2rS4tU6"


@pytest.mark.parametrize(
    "line",
    [
        "export STALWART_ADMIN_PASSWORD=" + RANDOM,
        "API_TOKEN=" + RANDOM,
        # A _FILE name does not clear a value that is not a path.
        "RESTIC_PASSWORD_FILE=" + RANDOM,
    ],
)
def test_blocks_literal_values(line):
    result = run(line + "\n")
    assert result.returncode == 2
    assert "credential-shaped assignment" in result.stderr


def test_block_message_leads_with_the_fixture_marker():
    result = run("API_TOKEN=" + RANDOM + "\n")
    after_finding = result.stderr.split("). ", 1)[1]
    assert "secret-guard-allow" in after_finding.split(". ", 1)[0]


# The .env commit check (cc-desk core spec). Each case passes a cwd inside a temporary repo.
GIT_ID = ["-c", "user.name=Test", "-c", "user.email=test@example.invalid", "-c", "commit.gpgsign=false"]


def git(directory, *args):
    """Run Git in a test repo and fail the test on an error."""
    subprocess.run(["git", "-C", str(directory), *GIT_ID, *args], check=True, capture_output=True)


def run_bash(command, cwd, allow=False):
    """Run the hook on a Bash command in cwd."""
    env = {key: value for key, value in os.environ.items()
           if not key.startswith("GIT_") and key != "CLAUDE_SECRET_GUARD_ALLOW"}
    if allow:
        env["CLAUDE_SECRET_GUARD_ALLOW"] = "1"
    payload = {"tool_name": "Bash", "tool_input": {"command": command}, "cwd": str(cwd)}
    return subprocess.run([sys.executable, str(GUARD)], input=json.dumps(payload),
                          capture_output=True, text=True, check=False, env=env)


@pytest.fixture
def repo(tmp_path):
    """Build a repo with one commit, holding a tracked .env.example and a tracked config/.env."""
    git(tmp_path, "init", "-q", "-b", "main")
    (tmp_path / "README").write_text("r\n")
    (tmp_path / ".env.example").write_text("TOKEN=\n")
    (tmp_path / "config").mkdir()
    (tmp_path / "config" / ".env").write_text("A=1\n")
    git(tmp_path, "add", "README", ".env.example", "config/.env")
    git(tmp_path, "commit", "-q", "-m", "first")
    return tmp_path


@pytest.mark.parametrize("name", [".env", ".env.local", ".env.production"])
def test_commit_with_staged_env_refused(name, repo):
    (repo / name).write_text("A=1\n")
    git(repo, "add", "-f", name)
    result = run_bash("git commit -m wip", repo)
    assert result.returncode == 2
    assert name in result.stderr


@pytest.mark.parametrize("command", [
    "git add .env && git commit -m wip",
    "git add .env.local",
    "git add -f docs/.env.production",
    "git stage .env",
    "git commit -m wip .env",
    "git commit -m wip -- sub/.env.local",
])
def test_named_env_refused(command, repo):
    assert run_bash(command, repo).returncode == 2


@pytest.mark.parametrize("command", ["git add -A && git commit -m wip", "git add . ; git commit -m wip"])
def test_whole_tree_add_then_commit_checks_untracked(command, repo):
    (repo / ".env.local").write_text("A=1\n")
    result = run_bash(command, repo)
    assert result.returncode == 2
    assert ".env.local" in result.stderr


def test_commit_all_over_modified_tracked_env_refused(repo):
    (repo / "config" / ".env").write_text("A=2\n")
    result = run_bash("git commit -a -m wip", repo)
    assert result.returncode == 2
    assert "config/.env" in result.stderr


@pytest.mark.parametrize("command", [
    "git commit -m wip",
    "git commit -a -m wip",
    "git add .env.example && git commit -m wip",
    "git add -A && git commit -m wip",
    "git commit -m wip .env.example",
    "git add .envrc docs/env.md",
    "echo git add .env",
])
def test_example_and_unrelated_names_pass(command, repo):
    (repo / ".env.example").write_text("TOKEN=\nOTHER=\n")
    (repo / ".env.sample").write_text("x\n")
    git(repo, "add", ".env.sample")
    result = run_bash(command, repo)
    assert (result.returncode, result.stderr) == (0, "")


def test_untracked_env_without_whole_tree_add_passes(repo):
    (repo / ".env").write_text("A=1\n")
    assert run_bash("git commit -m wip", repo).returncode == 0


def test_override_covers_env_check(repo):
    assert run_bash("git add .env", repo, allow=True).returncode == 0


@pytest.mark.parametrize("folder", ["plain", "missing"])
def test_git_failure_allows(folder, tmp_path):
    place = tmp_path / folder
    if folder == "plain":
        place.mkdir()
    assert run_bash("git commit -a -m wip", place).returncode == 0
    assert run_bash("git add -A && git commit -m wip", place).returncode == 0


def test_unreadable_directory_allows(repo):
    (repo / "config" / ".env").write_text("A=2\n")
    assert run_bash('git -C "$REPO" commit -a -m wip', repo / "config").returncode == 0


@pytest.mark.parametrize("name", [".env.example", ".env.sample", ".env.template", ".env.dist"])
def test_commit_with_staged_example_passes(name, repo):
    (repo / name).write_text("TOKEN=\nOTHER=\n")
    git(repo, "add", "-f", name)
    result = run_bash("git commit -m wip", repo)
    assert (result.returncode, result.stderr) == (0, "")
