"""Tests for the credential-assignment rule in the claude-secret-guard PreToolUse hook."""

import json
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
