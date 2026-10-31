"""Tests for voipms-sms paths that run before any network call, driven by subprocess."""

import os
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "bin/.local/bin/voipms-sms"


def run(home: Path, *args: str) -> subprocess.CompletedProcess:
    env = {**os.environ, "HOME": str(home)}
    return subprocess.run(
        [sys.executable, "-I", str(SCRIPT), *args], env=env, capture_output=True, text=True
    )


def test_missing_credentials_named(tmp_path):
    (tmp_path / ".local").mkdir()
    (tmp_path / ".local" / "secrets").write_text("export OTHER='x'\nexport VOIPMS_API_USERNAME=u\n")
    result = run(tmp_path, "status")
    assert result.returncode != 0
    assert "VOIPMS_API_PASSWORD missing" in result.stderr
    assert "VOIPMS_API_USERNAME missing" not in result.stderr


def test_long_message_refused_before_sending(tmp_path):
    (tmp_path / ".local").mkdir()
    (tmp_path / ".local" / "secrets").write_text(
        "export VOIPMS_API_USERNAME='u'\nexport VOIPMS_API_PASSWORD=\"p w\"\n"
    )
    result = run(tmp_path, "--did", "9070000000", "send", "5550100", "x" * 161)
    assert result.returncode != 0
    assert "160 characters at most" in result.stderr
