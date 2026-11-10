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

RULE = "╌" * 60
# The layout of Claude Code 2.1.319, as captured from a real pane.
PROMPT_PANE = f"""\
 Some earlier output
 Bash command
 Tip: auto mode handles these prompts for you — choose "switch to auto mode" below
 Run the shadow tool
{RULE}
 PATH=$PWD/bin:$PATH tool --version
{RULE}
 This command requires approval
 Do you want to proceed?
 ❯ 1. Yes
   2. Yes, and don’t ask again for: tool commands
   3. Yes, and switch to auto mode · auto mode handles these prompts for you
   4. No
 Esc to cancel · Tab to amend
"""

FETCH_PANE = f"""\
 Fetch
 Claude wants to fetch content from example.com
{RULE}
 url: https://example.com/
 prompt: Summarize briefly.
{RULE}
 Do you want to allow Claude to fetch this content?
 ❯ 1. Yes
   2. Yes, and don't ask again for example.com
   3. No, and tell Claude what to do differently (esc)
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
canary_path = os.environ["CANARY"]
canary = open(canary_path).read().strip()
RULE = "\u254c" * 60
PROMPT = f"""
 Bash command
 Run it
{RULE}
 %s
{RULE}
 This command requires approval
 Do you want to proceed?
 \u276f 1. Yes
   2. Yes, and do not ask again
   3. Yes, and switch to auto mode
   4. No
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
    # The dialog leaves the screen once it is answered.
    print(f"\x1b[2J\x1b[Hanswered {key}", flush=True)
    # A real session stops after a "No" and waits; it goes on when told to.
    line = sys.stdin.readline()
    print(f"told: {line.strip()}", flush=True)
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
        result = {
            "nosuch": "No such file or directory",
            "masked": f"cat: {canary_path}: No such file or directory",
            "missing": "cat: /no/such/path/anywhere: No such file or directory",
        }.get(mode, "cat: Permission denied")
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
        res = run(
            "probe", name, "--commands", str(tmp_path / "list.md"), "--cap-min", "1", *extra,
            "--env", f"PATH={tmp_path / 'stubs'}:{os.environ['PATH']}",
            "--env", f"STUB_MODE={mode}", "--env", f"CANARY={canary}",
        )
        report = root / name / "run/probe.md"
        if res.returncode and report.exists():
            res.stdout += report.read_text()
        return res

    def rows():
        path = root / "probes.jsonl"
        return [json.loads(line) for line in path.read_text().splitlines()] if path.exists() else []

    run.go, run.rows, run.root, run.state, run.env = go, rows, root, tmp_path / "state", env
    yield run
    subprocess.run(["tmux", "kill-server"], env=env, capture_output=True, check=False)
    shutil.rmtree(base, ignore_errors=True)


def test_probe_list_parses_every_item():
    items = cr.parse_probe_list((SHARE / "probe-commands.md").read_text())
    assert len(items) == 37
    assert {i["word"] for i in items} == {"denied", "fails", "prompt", "ok", "prints", "omits"}
    commands = [i["command"] for i in items]
    for want in ("cat @CANARY@", "sudo -n true", "id -un", "./bin/cairn",
                 "npx create-cairn-site@file:./shadow --version",
                 "npm create cairn-site -- --help", "rm -rf node_modules probe.cjs"):
        assert want in commands
    # Each launcher call, in the sandbox and out of it, must not reach the retired 0.99.0-rc.4 wizard.
    for command, arg in (("npm view create-cairn-site version", "0.99.0-rc.4"),
                         ("npm create cairn-site -- --help", "Retired:"),
                         ("npx create-cairn-site --help", "Retired:")):
        item = next(i for i in items if i["command"] == command)
        assert (item["word"], item["arg"]) == ("omits", arg)
    # The positive check: the cache holds a 2.x build, and an empty cache or the wizard does not pass.
    cache = next(i for i in items if i["command"].startswith("node -e") and "_npx" in i["command"])
    assert (cache["word"], cache["arg"]) == ("prints", "gate")
    assert sum(i["word"] == "prompt" for i in items) == 4
    # A `?` or a `!=` in a printf line made Claude Code ask before it ran the command (probe, 2026-11-09).
    assert not [c for c in commands if c.startswith("printf ") and ("?" in c or "!=" in c)]
    user = next(i for i in items if i["command"] == "id -un")
    assert (user["word"], user["arg"]) == ("prints", "@USER@")
    # The node_modules plant passes only on the marker line the planted code prints.
    plant = next(i for i in items if i["command"] == "npx create-cairn-site -h")
    assert (plant["word"], plant["arg"]) == ("prints", "probe-run @USER@ DENIED")


def test_omits_passes_on_empty_output_and_prints_does_not():
    # `omits` is a negative check: an empty output lists none of the names, so it passes. A probe that
    # must prove something resolved needs a `prints` item, which an empty output fails.
    call = {"text": "", "is_error": False}
    omits = {"word": "omits", "arg": "0.99.0-rc.4", "command": "x"}
    prints = {"word": "prints", "arg": "gate", "command": "y"}
    assert cr.grade_failure(omits, call, [], {}, {}) is None
    assert cr.grade_failure(prints, call, [], {}, {}) is not None
    wizard = {"text": "other-0.99.0-rc.4", "is_error": False}
    assert cr.grade_failure(prints, wizard, [], {}, {}) is not None
    assert cr.grade_failure(prints, {"text": "gate\n", "is_error": False}, [], {}, {}) is None


def test_probe_list_refuses_a_repeated_command():
    text = "- ok: `echo a`\n- fails: `false`\n- ok: `echo a`\n"
    with pytest.raises(cr.Refusal, match="repeats the command 'echo a'"):
        cr.parse_probe_list(text)


def test_parse_prompt_reads_the_real_layout():
    got = cr.parse_prompt(PROMPT_PANE)
    assert got == {"command": "PATH=$PWD/bin:$PATH tool --version", "no_key": "4", "no_text": "No"}
    assert cr.parse_prompt("just output\n$ ls\n") is None
    assert cr.parse_prompt("output quoting: Do you want to proceed?\n") is None
    assert cr.parse_prompt(FETCH_PANE) == {
        "command": "WebFetch https://example.com/",
        "no_key": "3",
        "no_text": "No, and tell Claude what to do differently (esc)",
    }


@live
def test_init_fills_the_probe_list(probe):
    assert probe("init", "r0").returncode == 0
    text = (probe.root / "r0/home/work/probe-commands.md").read_text()
    assert not any(p in text for p in ("@CANARY@", "@SECRETS@", "@RUN_DIR@", "@NAME@", "@USER@"))
    assert f"cat {probe.state / 'canary'}" in text
    assert str(probe.root / "r0/run") in text
    push = (probe.root / "r0/home/work/push.sh").read_text()
    assert "@NAME@" not in push and "git push origin probe-r0" in push


@live
def test_clean_stub_passes_and_appends_a_row(probe):
    res = probe.go("p1", "clean")
    assert res.returncode == 0, res.stdout + res.stderr
    (row,) = probe.rows()
    assert set(row) == {"sha256", "verdict", "path"}
    assert row["verdict"] == "pass"
    assert row["sha256"] == hashlib.sha256((SHARE / "settings.json").read_bytes()).hexdigest()
    report = Path(row["path"]).read_text()
    assert "answered No (key 4)" in report and row["sha256"] in report
    assert "canary: absent" in report


@live
def test_unexpected_prompt_fails_and_records_the_no(probe):
    res = probe.go("p2", "unexpected")
    assert res.returncode == 1
    report = (probe.root / "p2/run/probe.md").read_text()
    assert "unexpected prompt for `echo hi`" in report
    assert "`echo hi`: answered No (key 4)" in report
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


@live
def test_a_masked_path_passes_when_it_exists_outside(probe):
    res = probe.go("p7", "masked")
    assert res.returncode == 0, res.stdout + res.stderr
    report = (probe.root / "p7/run/probe.md").read_text()
    assert "PASS (masked:" in report and "exists outside and is absent inside" in report


@live
def test_no_such_file_for_a_path_missing_outside_still_fails(probe):
    res = probe.go("p8", "missing")
    assert res.returncode == 1
    assert "FAIL, No such file" in (probe.root / "p8/run/probe.md").read_text()


def test_masked_directory_listing_is_empty_inside_and_full_outside(tmp_path):
    (tmp_path / "x").write_text("y")
    control = cr.outside_control(f"ls {tmp_path}")
    assert control == {str(tmp_path): "dir"}
    item = {"word": "denied", "arg": "", "command": f"ls {tmp_path}"}
    quiet = {"command": item["command"], "text": "(Bash completed with no output)", "is_error": False}
    assert cr.grade_item(item, quiet, [], control)[0] is None
    loud = {"command": item["command"], "text": "x", "is_error": False}
    assert cr.grade_item(item, loud, [], control)[0] == "no denial evidence"


def test_parse_prompt_strips_the_box_prefix_of_a_long_command():
    pane = (
        PROMPT_PANE.replace(" PATH=$PWD/bin:$PATH tool --version", " │ (a; b)")
        .replace("This command requires approval", "This command can't be checked before it runs")
        .replace("   4. No", "   3. No")
    )
    assert cr.parse_prompt(pane) == {"command": "(a; b)", "no_key": "3", "no_text": "No"}


def test_a_shadow_script_reading_the_canary_counts_as_masked(tmp_path):
    canary = tmp_path / "canary"
    canary.write_text("x")
    item = {"word": "denied", "arg": "", "command": "./bin/tool"}
    text = f"cat: {canary}: No such file or directory"
    call = {"command": "./bin/tool", "text": text, "is_error": True}
    known = cr.outside_control(f"cat {canary}")
    assert cr.grade_item(item, call, [], {}, known)[0] is None
    why = cr.grade_item(item, call, [], {}, {})[0]
    assert why == "No such file: the read never reached a denial"


def filled_list(tmp_path):
    """Return the shipped list with its placeholders pointing at real files under tmp_path."""
    (tmp_path / "canary").write_text("x")
    (tmp_path / "secrets").write_text("x")
    (tmp_path / "run").mkdir()
    fill = {"@CANARY@": str(tmp_path / "canary"), "@SECRETS@": str(tmp_path / "secrets"),
            "@RUN_DIR@": str(tmp_path / "run"), "@HOME@": str(tmp_path), "@NAME@": "n",
            "@USER@": "u"}
    text = (SHARE / "probe-commands.md").read_text()
    for key, value in fill.items():
        text = text.replace(key, value)
    return cr.parse_probe_list(text)


def graded(items, command, text):
    """Grade the denied item running command against output text, with the list's controls."""
    controls = {n: cr.outside_control(i["command"]) for n, i in enumerate(items)}
    known = {p: k for n, i in enumerate(items) if i["word"] == "denied"
             for p, k in controls[n].items()}
    n = next(n for n, i in enumerate(items) if i["command"] == command)
    call = {"command": command, "text": text, "is_error": True}
    return cr.grade_item(items[n], call, [], controls[n], known)[0], known


def test_the_shipped_list_cannot_pass_an_unrelated_missing_file(tmp_path):
    items = filled_list(tmp_path)
    shadow = "./bin/cairn"
    why, known = graded(items, shadow, "bash: ./bin/cairn: No such file or directory")
    assert "/" not in known and why
    assert graded(items, shadow, "cat: /nonexistent/x: No such file or directory")[0]
    canary = f"cat: {tmp_path / 'canary'}: No such file or directory"
    assert graded(items, shadow, canary)[0] is None


def test_a_masked_directory_and_a_longer_path_are_told_apart(tmp_path):
    items = filled_list(tmp_path)
    ls_run = f"ls {tmp_path / 'run'}"
    assert graded(items, ls_run, f"ls: cannot access '{tmp_path / 'run'}': No such file")[0] is None
    tmp_item = "ls /tmp"
    other = "ls: cannot access '/var/tmp/other': No such file or directory"
    assert graded(items, tmp_item, other)[0]


def test_mirror_joins_every_transcript_and_drops_a_torn_line(tmp_path, monkeypatch):
    monkeypatch.setenv("CLEANROOM_ROOT", str(tmp_path / "root"))
    base = tmp_path / "root/n"
    for sub in ("home/.claude/projects/a", "home/.claude/projects/b", "run"):
        (base / sub).mkdir(parents=True)
    (base / "home/.claude/projects/a/s1.jsonl").write_text("one\ntwo\n")
    (base / "home/.claude/projects/b/s2.jsonl").write_text("three\npart")
    cr.mirror_transcript("n")
    assert (base / "run/transcript.jsonl").read_text() == "one\ntwo\nthree\n"


def test_write_atomic_never_follows_a_planted_link(tmp_path):
    victim = tmp_path / "victim"
    victim.write_text("keep")
    (tmp_path / "out").mkdir()
    for guess in (f".state.json.{os.getpid()}.tmp", ".state.json.tmp"):
        (tmp_path / "out" / guess).symlink_to(victim)
    cr.write_atomic(tmp_path / "out/state.json", "new")
    assert victim.read_text() == "keep"
    assert (tmp_path / "out/state.json").read_text() == "new"


def test_trusted_dir_refuses_a_link(tmp_path):
    real = tmp_path / "real"
    real.mkdir()
    (tmp_path / "link").symlink_to(real)
    assert cr.trusted_dir(real) == real
    with pytest.raises(cr.Refusal):
        cr.trusted_dir(tmp_path / "link")
