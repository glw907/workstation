"""Tests for music-backup, pavilion's nightly copy of ~/Music to R2, and its two units.

Each run puts a stub rclone first on PATH and a fixture secrets file under a scratch HOME, so
nothing reaches R2 or reads the live store.
"""

import configparser
import json
from pathlib import Path
import subprocess

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "bin/.local/bin/music-backup"
UNITS = ROOT / "systemd/.config/systemd/user"
SERVICE = UNITS / "music-backup.service"
TIMER = UNITS / "music-backup.timer"

# Every file the task writes in this repo, less secrets/values.age, which the merge writes.
TASK_FILES = [
    SCRIPT,
    SERVICE,
    TIMER,
    Path(__file__),
    ROOT / "scripts/check.sh",
    ROOT / "secrets/registry.md",
    ROOT / "claude/.claude/docs/cloudflare-estate/api-tokens.md",
]

KEY_ID = "kid-music-1"
SECRET = "sec-music-1"

# The stub records its arguments and the RCLONE_CONFIG_R2_* variables it was given.
STUB = """#!/usr/bin/env python3
import json, os, sys
env = {k: v for k, v in os.environ.items() if k.startswith("RCLONE_CONFIG_R2_")}
with open(os.environ["STUB_LOG"], "w") as f:
    json.dump({"argv": sys.argv[1:], "env": env}, f)
"""


@pytest.fixture
def box(tmp_path):
    """Make a scratch HOME with a library, a secrets file, and a stub rclone."""
    home = tmp_path / "home"
    (home / "Music").mkdir(parents=True)
    (home / ".local").mkdir()
    stubs = tmp_path / "stubs"
    stubs.mkdir()
    stub = stubs / "rclone"
    stub.write_text(STUB)
    stub.chmod(0o755)
    return tmp_path


def write_secrets(box, lines):
    (box / "home/.local/secrets").write_text("".join(f"{line}\n" for line in lines))


def run(box):
    env = {
        "HOME": str(box / "home"),
        "PATH": f"{box / 'stubs'}:/usr/bin:/bin",
        "STUB_LOG": str(box / "rclone.json"),
    }
    return subprocess.run([str(SCRIPT)], env=env, capture_output=True, text=True)


def stub_call(box):
    log = box / "rclone.json"
    return json.loads(log.read_text()) if log.exists() else None


def test_copies_the_library_with_the_remote_from_the_store(box):
    write_secrets(
        box,
        [
            "export CF_WS_R2_MUSIC_RW_TOKEN=tok-music-1",
            f"export CF_WS_R2_MUSIC_RW_KEY_ID={KEY_ID}",
            f"export CF_WS_R2_MUSIC_RW_SECRET={SECRET}",
        ],
    )
    result = run(box)
    assert result.returncode == 0, result.stderr
    call = stub_call(box)
    assert call["argv"] == [
        "copy",
        str(box / "home/Music"),
        "r2:music-library/library",
        "--exclude",
        ".artist-images/.*.part",
    ]
    assert call["env"] == {
        "RCLONE_CONFIG_R2_TYPE": "s3",
        "RCLONE_CONFIG_R2_PROVIDER": "Cloudflare",
        "RCLONE_CONFIG_R2_ENDPOINT": "https://120c269ad6d3dfbe6d63a0bb53758ca0.r2.cloudflarestorage.com",
        "RCLONE_CONFIG_R2_ACCESS_KEY_ID": KEY_ID,
        "RCLONE_CONFIG_R2_SECRET_ACCESS_KEY": SECRET,
        "RCLONE_CONFIG_R2_NO_CHECK_BUCKET": "true",
    }


@pytest.mark.parametrize(
    "lines",
    [
        [f"export CF_WS_R2_MUSIC_RW_SECRET={SECRET}"],
        [f"export CF_WS_R2_MUSIC_RW_KEY_ID={KEY_ID}"],
        ["export CF_WS_R2_MUSIC_RW_KEY_ID=", f"export CF_WS_R2_MUSIC_RW_SECRET={SECRET}"],
        [f"export CF_WS_R2_MUSIC_RW_KEY_ID={KEY_ID}", "export CF_WS_R2_MUSIC_RW_SECRET="],
        None,
    ],
    ids=["no-key-id", "no-secret", "empty-key-id", "empty-secret", "no-store"],
)
def test_a_missing_half_of_the_pair_runs_nothing(box, lines):
    if lines is not None:
        write_secrets(box, lines)
    result = run(box)
    assert result.returncode != 0
    if lines is not None:
        assert "music-backup: CF_WS_R2_MUSIC_RW_" in result.stderr
    assert stub_call(box) is None


def test_no_task_file_names_a_sync():
    banned = " ".join(["rclone", "sync"])
    named = [str(p.relative_to(ROOT)) for p in TASK_FILES if banned in p.read_text()]
    assert named == []


def unit_lines(path):
    """Return each section's (key, value) pairs, keeping the keys' case."""
    unit = configparser.ConfigParser(interpolation=None)
    unit.optionxform = str
    unit.read(path)
    return {name: list(unit[name].items()) for name in unit.sections()}


def test_the_service_runs_only_on_pavilion_under_its_sandbox():
    unit = unit_lines(SERVICE)
    assert ("ConditionHost", "pavilion") in unit["Unit"]
    for pair in [
        ("Type", "oneshot"),
        ("ExecStart", "%h/.local/bin/music-backup"),
        ("TimeoutStartSec", "6h"),
        ("ProtectSystem", "strict"),
        ("ProtectHome", "read-only"),
        ("PrivateTmp", "yes"),
        ("NoNewPrivileges", "yes"),
        ("IOSchedulingClass", "idle"),
    ]:
        assert pair in unit["Service"]


def test_the_timer_runs_nightly_and_catches_up():
    unit = unit_lines(TIMER)
    assert ("Persistent", "true") in unit["Timer"]
    assert ("OnCalendar", "*-*-* 03:30") in unit["Timer"]
    assert ("WantedBy", "timers.target") in unit["Install"]
