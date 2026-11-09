"""Tests for the cleanroom tool, run through its CLI under a temporary root with no sudo."""

import json
import os
import stat
import subprocess
import sys
from pathlib import Path

import pytest

TOOL = Path(__file__).resolve().parent.parent / "bin/.local/bin/cleanroom"
TEMPLATE = Path(__file__).resolve().parent.parent / "bin/.local/share/cleanroom/settings.json"

# The deny rules of the 907-rebuild prototype; the template must keep every one.
PROTOTYPE_DENY = [
    "Read(//var/home/glw907/**)",
    "Read(//home/glw907/**)",
    "Read(//tmp/**)",
    "Read(//run/user/**)",
    "Read(//dev/shm/**)",
    "Read(//var/tmp/cairn-cleanroom/logs/**)",
    "Read(//var/tmp/cairn-cleanroom/acceptance/**)",
    "Edit(~/.claude/**)",
    "Write(~/.claude/**)",
    "Bash(*907-life-legacy*)",
    "Bash(*cairn-build*)",
    "Bash(*cairn-907-auth*)",
    "Bash(*wrangler delete*)",
    "Bash(*d1 delete*)",
    "Bash(*r2 bucket delete*)",
    "Bash(*r2 object delete*)",
    "Bash(*repo delete*)",
    "Bash(*-X DELETE*)",
    "Bash(*--method DELETE*)",
    "Bash(git push*--force*)",
    "Bash(git push* -f*)",
]


@pytest.fixture
def room(tmp_path):
    """Return a runner for the CLI whose root and state live under tmp_path."""
    env = {
        **os.environ,
        "CLEANROOM_ROOT": str(tmp_path / "root"),
        "CLEANROOM_STATE": str(tmp_path / "state"),
        "CLEANROOM_USER": "",
    }

    def run(*args):
        return subprocess.run(
            [sys.executable, "-I", str(TOOL), *args],
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )

    run.root = tmp_path / "root"
    run.state = tmp_path / "state"
    return run


def snapshot(path: Path) -> dict:
    """Map each path under path to its mode, size, and mtime."""
    out = {}
    for p in sorted(path.rglob("*")):
        st = p.lstat()
        out[str(p)] = (st.st_mode, st.st_size, st.st_mtime_ns)
    return out


def test_init_builds_the_room(room):
    res = room("init", "a1")
    assert res.returncode == 0, res.stderr
    home = room.root / "a1/home"
    assert (room.root / "a1/run").is_dir()
    assert stat.S_IMODE((room.root / "a1/keyring-pass").stat().st_mode) == 0o600
    assert (room.root / "a1/keyring-pass").read_text().strip()
    assert stat.S_IMODE((room.state / "canary").stat().st_mode) == 0o600
    assert (room.state / "canary").read_text().startswith("canary-")
    seeded = json.loads((home / ".claude.json").read_text())
    assert seeded["hasCompletedOnboarding"] is True
    assert seeded["projects"][str(home / "work")]["hasTrustDialogAccepted"] is True
    assert (home / "work").is_dir()


def test_written_settings_equal_the_filled_template(room):
    room("init", "a1")
    written = (room.root / "a1/home/.claude/settings.json").read_text()
    want = (
        TEMPLATE.read_text()
        .replace("@RUN_DIR@", str(room.root / "a1/run"))
        .replace("@TOOL@", str(TOOL.resolve()))
    )
    assert written == want
    assert "@RUN_DIR@" not in written and "@TOOL@" not in written


def test_bus_config_listens_in_the_home(room):
    room("init", "a1")
    conf = (room.root / "a1/home/.config/cleanroom/bus.conf").read_text()
    assert f"<listen>unix:dir={room.root}/a1/home/.cache/dbus</listen>" in conf
    assert "/tmp</listen>" not in conf


def test_browser_relay_appends_and_prints_nothing(room):
    room("init", "a1")
    relay = room.root / "a1/home/.local/bin/open-url"
    res = subprocess.run([str(relay), "https://example.test/x"], capture_output=True, text=True)
    assert res.stdout == "" and res.stderr == ""
    assert (room.root / "a1/run/urls.log").read_text() == "https://example.test/x\n"


def test_init_twice_refuses_and_changes_nothing(room):
    assert room("init", "a1").returncode == 0
    before = snapshot(room.root) | snapshot(room.state)
    res = room("init", "a1")
    assert res.returncode != 0
    assert snapshot(room.root) | snapshot(room.state) == before


def test_fresh_rebuilds_a_graded_run_and_refuses_an_ungraded_one(room):
    room("init", "a1")
    (room.root / "a1/home/work/site.txt").write_text("x")
    res = room("init", "a1", "--fresh")
    assert res.returncode != 0 and "run-record.json" in res.stderr
    assert (room.root / "a1/home/work/site.txt").exists()
    (room.root / "a1/run/run-record.json").write_text("{}")
    res = room("init", "a1", "--fresh")
    assert res.returncode == 0, res.stderr
    assert "removing" in res.stdout
    assert not (room.root / "a1/home/work/site.txt").exists()
    assert not (room.root / "a1/run/run-record.json").exists()


def test_fresh_discard_rebuilds_an_ungraded_run(room):
    room("init", "a1")
    (room.root / "a1/home/work/site.txt").write_text("x")
    assert room("init", "a1", "--fresh", "--discard").returncode == 0
    assert not (room.root / "a1/home/work/site.txt").exists()


def test_discard_without_fresh_is_refused(room):
    assert room("init", "a1", "--discard").returncode != 0
    assert not (room.root / "a1").exists()


def test_fresh_never_touches_the_ledger_or_probe_log(room):
    room("init", "a1")
    (room.root / "ledger.jsonl").write_text('{"name": "a1"}\n')
    (room.root / "probes.jsonl").write_text('{"verdict": "pass"}\n')
    before = {p: (room.root / p).stat().st_mtime_ns for p in ("ledger.jsonl", "probes.jsonl")}
    assert room("init", "a1", "--fresh", "--discard").returncode == 0
    for p, mtime in before.items():
        assert (room.root / p).stat().st_mtime_ns == mtime
    assert (room.root / "ledger.jsonl").read_text() == '{"name": "a1"}\n'


@pytest.mark.parametrize("name", ["", ".", "..", "a/b", "A", "-x", "x" * 41, "a b", "../a"])
def test_bad_names_are_refused_before_any_path_exists(room, name):
    res = room("init", name)
    assert res.returncode != 0
    assert not room.root.exists()
    assert not room.state.exists()


def test_fresh_with_a_bad_name_removes_nothing(room):
    room("init", "a1")
    before = snapshot(room.root)
    assert room("init", "..", "--fresh", "--discard").returncode != 0
    assert snapshot(room.root) == before


def test_fresh_refuses_a_symlinked_room(room, tmp_path):
    room("init", "a1")
    victim = tmp_path / "victim"
    victim.mkdir()
    (victim / "keep").write_text("x")
    (room.root / "b1").symlink_to(victim)
    res = room("init", "b1", "--fresh", "--discard")
    assert res.returncode != 0
    assert (victim / "keep").exists()


def test_geoffs_home_appears_only_where_the_template_names_it(room):
    room("init", "a1")
    base = room.root / "a1"
    for path in [p for p in base.rglob("*") if p.is_file()]:
        if path.name == "settings.json":
            continue
        assert "/var/home/glw907" not in path.read_text(), path
    settings = json.loads((base / "home/.claude/settings.json").read_text())
    hits = []

    def walk(node, where):
        if isinstance(node, str):
            if "glw907" in node:
                hits.append((where, node))
        elif isinstance(node, list):
            for item in node:
                walk(item, where)
        elif isinstance(node, dict):
            for key, val in node.items():
                walk(val, f"{where}.{key}" if where else key)

    walk(settings, "")
    allowed = {
        "permissions.deny",
        "sandbox.filesystem.denyRead",
        "sandbox.filesystem.allowRead",
        "statusLine.command",
    }
    assert {where for where, _ in hits} <= allowed
    for where, text in hits:
        if where == "sandbox.filesystem.allowRead":
            assert text.endswith("/node")


def test_template_keeps_the_invariants():
    data = json.loads(TEMPLATE.read_text())
    sandbox = data["sandbox"]
    assert sandbox["enabled"] is True
    assert sandbox["failIfUnavailable"] is True
    assert sandbox["allowUnsandboxedCommands"] is False
    denied = {e["name"] for e in sandbox["credentials"]["envVars"] if e["mode"] == "deny"}
    assert denied == {"CAIRN_CF_SETUP_TOKEN", "ANTHROPIC_API_KEY", "CLAUDE_CODE_OAUTH_TOKEN"}
    assert set(PROTOTYPE_DENY) <= set(data["permissions"]["deny"])
    assert sandbox["excludedCommands"] == [
        "cairn *",
        "npm create cairn-site",
        "npm create cairn-site -- *",
        "npx create-cairn-site *",
    ]
    for pattern in sandbox["excludedCommands"]:
        assert f"Bash({pattern})" in data["permissions"]["allow"]
    assert data["permissions"]["defaultMode"] == "default"
    assert "WebFetch" not in data["permissions"]["allow"]
    assert "WebFetch" not in data["permissions"]["deny"]
    assert data["env"]["NODE_USE_ENV_PROXY"] == "1"
    fetch = {a for a in data["permissions"]["allow"] if a.startswith("WebFetch(domain:")}
    assert {f"WebFetch(domain:{d})" for d in sandbox["network"]["allowedDomains"]} == fetch
    deny_read = sandbox["filesystem"]["denyRead"]
    assert "//var/tmp/cleanroom/*/run/**" in deny_read
    assert "//var/home/glw907/.local/state/cleanroom/**" in deny_read


def test_the_tool_names_no_product():
    assert subprocess.run(["grep", "-ci", "cairn", str(TOOL)], capture_output=True).stdout == b"0\n"
