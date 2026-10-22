"""Tests for the claude-tierguard PreToolUse hook, run with a stub rpm-ostree and a temp HOME."""

import json
import os
import subprocess
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parent.parent / "bin/.local/bin/claude-tierguard"


@pytest.fixture
def env(tmp_path):
    """Give the hook an rpm-ostree on PATH and a layered list holding only `micro`."""
    stub = tmp_path / "bin" / "rpm-ostree"
    stub.parent.mkdir()
    stub.write_text("#!/bin/sh\nexit 0\n")
    stub.chmod(0o755)
    listing = tmp_path / ".dotfiles" / "bluefin" / "layered-packages.txt"
    listing.parent.mkdir(parents=True)
    listing.write_text("# layered\nmicro\n")
    environment = dict(os.environ)
    environment["PATH"] = f"{stub.parent}:{environment['PATH']}"
    environment["HOME"] = str(tmp_path)
    return environment


def denied(env, command):
    result = subprocess.run(
        ["bash", str(SCRIPT)],
        input=json.dumps({"tool_input": {"command": command}}),
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )
    assert result.returncode == 0
    return '"deny"' in result.stdout


@pytest.mark.parametrize(
    "command",
    [
        "rpm-ostree install htop",
        "sudo -A rpm-ostree install htop",
        "cd / && rpm-ostree install micro htop",
        "bash <<'EOF'\nrpm-ostree install htop\nEOF",
    ],
)
def test_denies_unlisted_package(env, command):
    assert denied(env, command)


@pytest.mark.parametrize(
    "command",
    [
        "rpm-ostree install micro",
        "rpm-ostree status && echo install done",
        # Prose about layering inside a heredoc edit, as in two real sessions (2026-10-19).
        "python3 -I - <<'EOF'\ns = 'never rpm-ostree layering; install only if rpm verifies'\nEOF",
        "git commit -m 'Say why rpm-ostree install is a last resort'",
    ],
)
def test_allows(env, command):
    assert not denied(env, command)
