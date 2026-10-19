"""Tests for the claude-block-pass PreToolUse hook and the Proton token pattern in claude-secret-guard."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

BIN = Path(__file__).resolve().parent.parent / "bin/.local/bin"
BLOCK = BIN / "claude-block-pass"
GUARD = BIN / "claude-secret-guard"

DENIED = [
    "pass-cli item view pass://Workstation/key/key",
    "pass-cli login",
    "PROTON_PASS_SESSION_DIR=/tmp/x pass-cli info",
    "cd ~ && pass-cli item list",
    "echo hi; pass-cli logout",
    "env FOO=1 pass-cli agent create x",
    "sudo pass-cli info",
    "(pass-cli info)",
    "x=$(pass-cli item view pass://a/b/c)",
    "secret-tool lookup service proton-pass-agent host pavilion",
    "echo go && secret-tool lookup service x",
    "keyctl print 123",
    "keyctl pipe 123",
    "keyctl read 123",
    "sudo keyctl print @u",
    "ls $XDG_RUNTIME_DIR/pass-ws",
    "cat /run/user/1000/pass-ws/session",
    "ls /run/user/1000/pass-recv.AbC123",
    "cat ~/.local/share/proton-pass-cli/.session/data",
    "tar c ~/.local/share/proton-pass-cli",
    # Wrappers, shell keywords, and nesting.
    "bash -c 'pass-cli info'",
    'bash -c "pass-cli info"',
    "echo info | xargs pass-cli",
    "eval pass-cli info",
    "watch pass-cli info",
    "stdbuf -o0 pass-cli info",
    "sudo -u glw907 pass-cli info",
    "nice -n 5 pass-cli info",
    "timeout -s KILL 5 pass-cli info",
    "timeout 5 pass-cli info",
    "if pass-cli info; then :; fi",
    "! pass-cli info",
    "{ pass-cli info; }",
    "for i in 1; do pass-cli info; done",
    # Path prefixes and options before the subcommand.
    "/home/linuxbrew/.linuxbrew/bin/pass-cli info",
    "$(brew --prefix)/bin/pass-cli info",
    "/usr/bin/secret-tool lookup service x",
    "/usr/bin/keyctl print 1",
    "keyctl -v print 1",
    # secret-tool search prints the secret too.
    "secret-tool search service proton-pass-agent",
    "secret-tool search --all service x",
    # Quoting and continuation tricks.
    "'pass-cli' info",
    '"pass-cli" info',
    "p''ass-cli info",
    "\\pass-cli info",
    "pass\\\n-cli info",
    # Session directories by glob or the count script's own.
    "ls $XDG_RUNTIME_DIR/pass-count.abc",
    "cat $XDG_RUNTIME_DIR/pass-w*/session",
    "ls ~/.local/share/proton-pass-*",
    "cd $XDG_RUNTIME_DIR && cat pass-ws.abc/session",
    # Combined and leading shell flags, other pass-through wrappers.
    'bash -lc "pass-cli info"',
    "sh -ec pass-cli",
    "zsh -ic pass-cli",
    'bash -x -c "pass-cli"',
    "bash --norc -c pass-cli",
    'busybox sh -c "pass-cli"',
    "ionice -c 3 pass-cli info",
    "strace -f pass-cli info",
    "unbuffer pass-cli info",
    # More session-directory globs.
    "cat /run/user/1000/pass-*/session",
    "cat /run/user/1000/pass-c*/x",
    "cat /run/user/1000/pass-w?.abc/x",
    "cat /run/user/1000/pass-[w]s.a/x",
]

ALLOWED = [
    "ws-pass-key --status",
    "secret-receive FOO",
    "secret-tool store --label x service y",
    "secret-tool --help",
    "keyctl show",
    "keyctl list @u",
    "grep -n passcli notes.txt",
    "cat docs/pass-cli-notes.md",
    "brew pin proton-pass-cli",
    "git commit -m 'mention pass-cli in the docs'",
    "echo 'run pass-cli later'",
    "ls ~/Projects/pass-client",
    "bash tests/ws-pass-key.test.sh",
    "ssh-add -l",
]


def run(script, payload):
    return subprocess.run(
        [sys.executable, str(script)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        check=False,
    )


def bash(cmd):
    return {"tool_name": "Bash", "tool_input": {"command": cmd}, "session_id": "t"}


@pytest.mark.parametrize("cmd", DENIED)
def test_denied(cmd):
    result = run(BLOCK, bash(cmd))
    assert result.returncode == 0
    decision = json.loads(result.stdout)["hookSpecificOutput"]
    assert decision["permissionDecision"] == "deny"
    assert "ws-pass-key" in decision["permissionDecisionReason"]


@pytest.mark.parametrize("cmd", ALLOWED)
def test_allowed(cmd):
    result = run(BLOCK, bash(cmd))
    assert result.returncode == 0
    assert result.stdout == ""


def test_denies_every_time_not_a_rate_limit():
    for _ in range(5):
        assert "deny" in run(BLOCK, bash("pass-cli info")).stdout


def test_ignores_non_bash_tools():
    payload = {"tool_name": "Write", "tool_input": {"content": "pass-cli info"}}
    assert run(BLOCK, payload).stdout == ""


def test_malformed_payload_fails_open():
    result = subprocess.run(
        [sys.executable, str(BLOCK)], input="not json", capture_output=True, text=True, check=False
    )
    assert result.returncode == 0
    assert result.stdout == ""


# The token literals are split so this file carries no token-shaped string itself.
PROTON_TOKEN = "pst_" + "a1B2c3D4e5F6g7H8" + "::" + "k9L0m1N2o3P4q5R6s7T8"


def test_secret_guard_blocks_proton_token():
    result = run(GUARD, {"tool_name": "Write", "tool_input": {"content": f"token {PROTON_TOKEN}\n"}})
    assert result.returncode == 2
    assert "Proton" in result.stderr


def test_secret_guard_blocks_proton_token_in_bash():
    result = run(GUARD, bash(f"curl -H 'x: {PROTON_TOKEN}' https://example.test"))
    assert result.returncode == 2


@pytest.mark.parametrize(
    "text",
    [
        "pst_ is the prefix of a Proton token",
        "the token looks like pst_xxxx::KEY in the docs",
        "set PROTON_PASS_PERSONAL_ACCESS_TOKEN before pass-cli login",
        "pst_short::tiny",
    ],
)
def test_secret_guard_passes_lookalikes(text):
    result = run(GUARD, {"tool_name": "Write", "tool_input": {"content": text}})
    assert result.returncode == 0
