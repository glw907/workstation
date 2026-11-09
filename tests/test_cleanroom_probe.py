"""Tests for cleanroom probe: the list parser, the prompt parser, and stub sessions under tmux."""

import hashlib
import importlib.machinery
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

TOOL = Path(__file__).resolve().parent.parent / "bin/.local/bin/cleanroom"
SHARE = TOOL.parent.parent / "share/cleanroom"
STUB_VALUE = "stubvalue-0123456789abcdef-0123"
NEEDS = ("tmux", "dbus-run-session", "gnome-keyring-daemon", "script", "gdbus")
live = pytest.mark.skipif(
    any(shutil.which(tool) is None for tool in NEEDS), reason="needs tmux, dbus, keyring, script"
)

loader = importlib.machinery.SourceFileLoader("cleanroom_tool", str(TOOL))
spec = importlib.util.spec_from_loader("cleanroom_tool", loader)
cr = importlib.util.module_from_spec(spec)
loader.exec_module(cr)

PROMPT_PANE = """\
 Some earlier output

 Bash command

   PATH=$PWD/bin:$PATH tool --version

   Run the shadow tool

 Do you want to proceed?
 > 1. Yes
   2. Yes, and don't ask again for tool commands
   3. No

 Esc to cancel
"""

# The list the stubs run; CANARY is replaced with the canary's path.
LIST = """\
Prose line, skipped.
- denied: `cat CANARY`
- prompt: `PATH=$PWD/bin:$PATH tool --version`
- ok: `echo hi`
- fails: `false`
"""

# A stand-in for `claude`: reads the filled list from the work folder, writes a transcript, and
# shows a prompt on the pane for a command the mode says to ask about.
STUB = r'''#!/usr/bin/env python3
import json, os, re, sys, termios, tty

mode = os.environ["STUB_MODE"]
home = os.environ["HOME"]
os.makedirs(f"{home}/.claude/projects/p", exist_ok=True)
out = open(f"{home}/.claude/projects/p/s.jsonl", "a")
items = re.findall(r"^- (\w+): `(.*)`$", open(f"{home}/work/probe-commands.md").read(), re.M)
canary = open(os.environ["CANARY"]).read().strip()
PROMPT = """
 Bash command

   %s

   description

 Do you want to proceed?
 > 1. Yes
   2. Yes, and don't ask again
   3. No

 Esc to cancel
"""


def emit(message):
    out.write(json.dumps({"message": message}) + "\n")
    out.flush()


def ask():
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    tty.setcbreak(fd)
    key = os.read(fd, 1).decode()
    termios.tcsetattr(fd, termios.TCSADRAIN, old)
    print(f"\nanswered {key}", flush=True)
    return key


for n, (word, command) in enumerate(items):
    emit({"content": [{"type": "tool_use", "id": f"t{n}", "name": "Bash", "input": {"command": command}}]})
    asks = word == "prompt" or (mode == "unexpected" and word == "ok")
    result, error = "hi", False
    if asks:
        print(PROMPT % command, flush=True)
        ask()
        result, error = "The user doesn't want to proceed", True
    elif word == "denied":
        result = "No such file or directory" if mode == "nosuch" else "cat: Permission denied"
        error = True
    elif word == "fails":
        result, error = "Exit code 1", True
    elif mode == "leakcanary":
        result = canary
    elif mode == "leakvalue":
        result = os.environ["STUB_VAL"]
    emit({"content": [{"type": "tool_result", "tool_use_id": f"t{n}", "content": result, "is_error": error}]})
print("PROBE DONE", flush=True)
import time
time.sleep(60)
'''


def wait_text(path, timeout=30.0):
    import time

    deadline = time.time() + timeout
    while time.time() < deadline:
        if path.exists():
            return path.read_text()
        time.sleep(0.2)
    raise AssertionError(f"{path} never appeared")


@pytest.fixture
def probe(tmp_path):
    """Return a runner that initialises a room and probes it with a stub session."""
    base = Path(tempfile.mkdtemp(prefix="cr", dir="/tmp"))
    root = base / "root"
    for sub in ("stubs", "tmux", "xdg"):
        (tmp_path / sub).mkdir()
    (tmp_path / "stubs/claude").write_text(STUB)
    (tmp_path / "stubs/claude").chmod(0o755)
    (tmp_path / "secrets").write_text(f"export STUB_KEY={STUB_VALUE}\n")
    (tmp_path / "list.md").write_text(LIST)
    env = {
        **os.environ,
        "CLEANROOM_ROOT": str(root),
        "CLEANROOM_STATE": str(tmp_path / "state"),
        "CLEANROOM_USER": "",
        "CLEANROOM_SECRETS": str(tmp_path / "secrets"),
        "CLEANROOM_TICK": "0.3",
        "CLEANROOM_PROBE_TICK": "0.3",
        "CLEANROOM_GRACE": "0.5",
        "CLEANROOM_KILL_GRACE": "1",
        "TMUX_TMPDIR": str(tmp_path / "tmux"),
        "XDG_RUNTIME_DIR": str(tmp_path / "xdg"),
    }

    def run(*args):
        return subprocess.run(
            [sys.executable, "-I", str(TOOL), *args], env=env, capture_output=True, text=True,
            check=False,
        )

    def go(name, mode, secret=False):
        assert run("init", name).returncode == 0
        canary = tmp_path / "state/canary"
        (root / name / "home/work/probe-commands.md").write_text(
            LIST.replace("CANARY", str(canary))
        )
        extra = ["--secret", "STUB_KEY:STUB_VAL"] if secret else []
        return run(
            "probe", name, "--commands", str(tmp_path / "list.md"), "--cap-min", "1", *extra,
            "--env", f"PATH={tmp_path / 'stubs'}:{os.environ['PATH']}",
            "--env", f"STUB_MODE={mode}", "--env", f"CANARY={canary}",
        )

    def rows():
        path = root / "probes.jsonl"
        return [json.loads(line) for line in path.read_text().splitlines()] if path.exists() else []

    run.go, run.rows, run.root, run.state, run.env = go, rows, root, tmp_path / "state", env
    yield run
    subprocess.run(["tmux", "kill-server"], env=env, capture_output=True, check=False)
    shutil.rmtree(base, ignore_errors=True)


def test_probe_list_parses_every_item():
    items = cr.parse_probe_list((SHARE / "probe-commands.md").read_text())
    assert len(items) == 26
    assert {i["word"] for i in items} == {"denied", "fails", "prompt", "ok", "prints", "omits"}
    commands = [i["command"] for i in items]
    for want in ("cat @CANARY@", "sudo -n true", "id -un", "./bin/cairn",
                 "npx create-cairn-site@file:./shadow --version"):
        assert want in commands
    assert sum(i["word"] == "prompt" for i in items) == 2
    user = next(i for i in items if i["command"] == "id -un")
    assert (user["word"], user["arg"]) == ("prints", "@USER@")


def test_parse_prompt_reads_the_assumed_layout():
    got = cr.parse_prompt(PROMPT_PANE)
    assert got == {"command": "PATH=$PWD/bin:$PATH tool --version", "no_key": "3", "no_text": "No"}
    assert cr.parse_prompt("just output\n$ ls\n") is None
    assert cr.parse_prompt(PROMPT_PANE.replace(" Esc to cancel", "")) is None
    fetch = PROMPT_PANE.replace("Bash command", "Fetch").replace(
        "PATH=$PWD/bin:$PATH tool --version", "https://example.com/"
    )
    assert cr.parse_prompt(fetch)["command"] == "WebFetch https://example.com/"


@live
def test_init_fills_the_probe_list(probe):
    assert probe("init", "r0").returncode == 0
    text = (probe.root / "r0/home/work/probe-commands.md").read_text()
    assert not any(p in text for p in ("@CANARY@", "@SECRETS@", "@RUN_DIR@", "@NAME@", "@USER@"))
    assert f"cat {probe.state / 'canary'}" in text
    assert str(probe.root / "r0/run") in text


@live
def test_clean_stub_passes_and_appends_a_row(probe):
    res = probe.go("p1", "clean")
    assert res.returncode == 0, res.stdout + res.stderr
    (row,) = probe.rows()
    assert set(row) == {"sha256", "verdict", "path"}
    assert row["verdict"] == "pass"
    assert row["sha256"] == hashlib.sha256((SHARE / "settings.json").read_bytes()).hexdigest()
    report = Path(row["path"]).read_text()
    assert "answered No (key 3)" in report and row["sha256"] in report
    assert "canary: absent" in report


@live
def test_unexpected_prompt_fails_and_records_the_no(probe):
    res = probe.go("p2", "unexpected")
    assert res.returncode == 1
    report = (probe.root / "p2/run/probe.md").read_text()
    assert "unexpected prompt for `echo hi`" in report
    assert "`echo hi`: answered No (key 3)" in report
    assert probe.rows()[0]["verdict"] == "fail"


@live
def test_echoed_canary_fails_by_label(probe):
    res = probe.go("p3", "leakcanary")
    assert res.returncode == 1
    report = (probe.root / "p3/run/probe.md").read_text()
    assert "canary: FOUND in transcript.jsonl" in report
    assert (probe.state / "canary").read_text().strip() not in report


@live
def test_echoed_handed_in_value_fails_by_label(probe):
    res = probe.go("p4", "leakvalue", secret=True)
    assert res.returncode == 1
    report = (probe.root / "p4/run/probe.md").read_text()
    assert "STUB_KEY: FOUND in transcript.jsonl" in report
    assert STUB_VALUE not in report


@live
def test_no_such_file_fails_a_read_item(probe):
    res = probe.go("p5", "nosuch")
    assert res.returncode == 1
    report = (probe.root / "p5/run/probe.md").read_text()
    assert "FAIL, No such file" in report


@live
def test_missing_canary_fails_before_the_session_starts(probe):
    assert probe("init", "p6").returncode == 0
    (probe.state / "canary").unlink()
    res = probe("probe", "p6", "--commands", str(SHARE / "probe-commands.md"))
    assert res.returncode == 1 and "no canary" in res.stderr
    assert probe.rows() == []
    assert not (probe.root / "ledger.jsonl").exists()
    listing = subprocess.run(
        ["tmux", "list-sessions"], env=probe.env, capture_output=True, text=True, check=False
    )
    assert "cleanroom-p6" not in listing.stdout
