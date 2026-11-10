"""Live tests for cleanroom: a stub `claude` under tmux, a private session bus, the real watcher."""

import json
import os
import pwd
import shutil
import stat
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import pytest

TOOL = Path(__file__).resolve().parent.parent / "bin/.local/bin/cleanroom"
STUB_VALUE = "stubvalue-0123456789abcdef-0123"
NEEDS = ("tmux", "dbus-run-session", "gnome-keyring-daemon", "script", "gdbus")
live = pytest.mark.skipif(
    any(shutil.which(tool) is None for tool in NEEDS), reason="needs tmux, dbus, keyring, script"
)

# A stand-in for `claude`. $STUB_MODE picks the behavior; RUN and TOOL come in as --env values.
STUB = r"""#!/bin/bash
report() { printf '{"cost":{"total_cost_usd":%s}}' "$1" | python3 -I "$TOOL" statusline "$RUN" > /dev/null; }
transcript() {
  mkdir -p "$HOME/.claude/projects/p"
  printf '{"message":{"id":"m%s","model":"claude-opus-5-5","usage":{"input_tokens":10,"output_tokens":5}}}\n' \
    "$1" >> "$HOME/.claude/projects/p/s.jsonl"
}
case "$STUB_MODE" in
  cost21) report 21; sleep 60 ;;
  stale) report 1; for i in $(seq 1 100); do transcript "$i"; sleep 0.5; done ;;
  corrupt) printf 'not json' > "$RUN/statusline.json"; sleep 60 ;;
  detached) setsid sleep 300 & sleep 60 ;;
  leak) echo "token is $ANTHROPIC_API_KEY"; sleep 60 ;;
  *) sleep 60 ;;
esac
"""


def holders(root_dir):
    """Yield (pid, environ) for every process whose HOME sits under the test's root."""
    for entry in Path("/proc").iterdir():
        if not entry.name.isdigit():
            continue
        try:
            env = (entry / "environ").read_bytes()
        except OSError:
            continue
        if b"HOME=" + str(root_dir).encode() in env:
            yield int(entry.name), env


def wait_for(check, timeout=30.0):
    """Poll check until it returns something truthy, or fail."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        got = check()
        if got:
            return got
        time.sleep(0.2)
    raise AssertionError("timed out")


@pytest.fixture
def lroom(tmp_path):
    """Return a runner with the knobs a live run needs; kill its tmux server and processes after."""
    # The private bus listens inside the home, and a unix socket path stops at 108 characters,
    # so the root stays short instead of living under pytest's long temporary directory.
    base = Path(tempfile.mkdtemp(prefix="cr", dir="/tmp"))
    root = base / "root"
    stubs = tmp_path / "stubs"
    for sub in ("stubs", "tmux", "xdg"):
        (tmp_path / sub).mkdir()
    (stubs / "claude").write_text(STUB)
    (stubs / "claude").chmod(0o755)
    (tmp_path / "secrets").write_text(f"export STUB_KEY={STUB_VALUE}\n")
    env = {
        **os.environ,
        "CLEANROOM_ROOT": str(root),
        "CLEANROOM_STATE": str(tmp_path / "state"),
        "CLEANROOM_USER": "",
        "CLEANROOM_SECRETS": str(tmp_path / "secrets"),
        "CLEANROOM_TICK": "0.3",
        "CLEANROOM_GRACE": "0.5",
        "CLEANROOM_KILL_GRACE": "1",
        "CLEANROOM_STALE": "2",
        "TMUX_TMPDIR": str(tmp_path / "tmux"),
        "XDG_RUNTIME_DIR": str(tmp_path / "xdg"),
    }

    def run(*args):
        return subprocess.run(
            [sys.executable, "-I", str(TOOL), *args], env=env, capture_output=True, text=True,
            check=False,
        )

    def start(name, mode, *extra):
        assert run("init", name).returncode == 0
        res = run(
            "run", name, "--goal", "do the thing",
            "--secret", "STUB_KEY:ANTHROPIC_API_KEY",
            "--env", f"PATH={stubs}:{os.environ['PATH']}",
            "--env", f"STUB_MODE={mode}",
            "--env", f"RUN={root / name / 'run'}",
            "--env", f"TOOL={TOOL}",
            "--env", f"CLEANROOM_ROOT={root}",
            *extra,
        )
        assert res.returncode == 0, res.stderr
        return res

    def ledger():
        path = root / "ledger.jsonl"
        if not path.exists():
            return []
        return [json.loads(line) for line in path.read_text().splitlines()]

    def final(name):
        return wait_for(
            lambda: next((r for r in ledger() if r["name"] == name and r["state"] != "running"), None)
        )

    run.start, run.ledger, run.final, run.env = start, ledger, final, env
    run.root, run.state = root, tmp_path / "state"
    yield run
    subprocess.run(["tmux", "kill-server"], env=env, capture_output=True, check=False)
    for pid, _ in holders(root):
        os.kill(pid, 9)
    shutil.rmtree(base, ignore_errors=True)


@live
def test_run_hands_the_value_in_by_environment_only(lroom):
    lroom.start("r1", "sleep")
    run = lroom.root / "r1/run"
    wait_for(lambda: (run / "state.json").exists())
    row = lroom.ledger()[0]
    assert row["state"] == "running" and row["end"] is None
    assert list((Path(lroom.env["XDG_RUNTIME_DIR"]) / "cleanroom").glob("*")) == []
    value = STUB_VALUE.encode()
    assert wait_for(lambda: [p for p, env in holders(lroom.root) if value in env])
    for entry in Path("/proc").iterdir():
        if entry.name.isdigit():
            try:
                assert value not in (entry / "cmdline").read_bytes()
            except OSError:
                continue
    for path in (run / "state.json", run / "meta.json", lroom.root / "ledger.jsonl"):
        assert STUB_VALUE not in path.read_text()
    assert lroom("stop", "r1").returncode == 0


@live
def test_run_records_the_approval_and_no_file_holds_the_value(lroom):
    lroom.start("r1", "sleep")
    claude_json = lroom.root / "r1/home/.claude.json"
    wait_for(lambda: "customApiKeyResponses" in claude_json.read_text())
    approved = json.loads(claude_json.read_text())["customApiKeyResponses"]["approved"]
    assert approved == [STUB_VALUE[-20:]]
    lroom("stop", "r1")
    for path in lroom.root.rglob("*"):
        if path.is_file() and not path.is_symlink():
            assert STUB_VALUE.encode() not in path.read_bytes(), path


@live
def test_a_run_past_cap_min_ends_as_stopped_time(lroom):
    lroom.start("r1", "sleep", "--cap-min", "0.05")
    row = lroom.final("r1")
    assert row["state"] == "stopped:time" and row["end"] is not None
    assert json.loads((lroom.root / "r1/run/state.json").read_text())["state"] == "stopped:time"


@live
def test_a_statusline_cost_of_21_ends_as_stopped_cost(lroom):
    lroom.start("r1", "cost21")
    row = lroom.final("r1")
    assert row["state"] == "stopped:cost" and row["cost"] >= 21


@live
def test_a_stale_statusline_ends_as_stopped_cost_unknown(lroom):
    lroom.start("r1", "stale")
    assert lroom.final("r1")["state"] == "stopped:cost-unknown"


@live
def test_a_watcher_that_raises_ends_as_stopped_watcher(lroom):
    lroom.start("r1", "corrupt")
    assert lroom.final("r1")["state"] == "stopped:watcher"


@live
def test_a_watcher_that_cannot_write_its_state_still_ends_the_run(lroom):
    lroom.start("r1", "sleep")
    state = lroom.root / "r1/run/state.json"
    wait_for(state.exists)

    def block():
        # A directory in state.json's place makes the watcher's next write fail.
        try:
            state.unlink()
            state.mkdir()
        except OSError:
            return False
        return True

    wait_for(block)
    assert lroom.final("r1")["state"] == "stopped:watcher"
    wait_for(lambda: not list(holders(lroom.root)))


@live
def test_stop_ends_a_detached_child_and_rewrites_the_row(lroom):
    lroom.start("r1", "detached")
    wait_for(lambda: (lroom.root / "r1/run/state.json").exists())

    def sleeper():
        return any(Path(f"/proc/{p}/comm").read_text().strip() == "sleep" and b"HOME=" in e
                   for p, e in holders(lroom.root))

    wait_for(sleeper)
    assert lroom("stop", "r1").returncode == 0
    assert list(holders(lroom.root)) == []
    assert lroom.ledger()[0]["state"] == "stopped:manual"


@live
def test_shell_prints_only_the_clean_set(lroom):
    assert lroom("init", "s1").returncode == 0
    res = lroom("shell", "s1", "-c", "env | cut -d= -f1 | sort")
    assert res.returncode == 0, res.stderr
    names = set(res.stdout.split())
    base = {"HOME", "PATH", "LANG", "TERM", "TMPDIR", "BROWSER", "DISABLE_AUTOUPDATER",
            "DBUS_SESSION_BUS_ADDRESS"}
    assert base <= names
    assert names - base <= {"PWD", "OLDPWD", "SHLVL", "_"}


@live
def test_shell_exits_with_the_commands_status(lroom):
    assert lroom("init", "s1").returncode == 0
    assert lroom("shell", "s1", "-c", "exit 7").returncode == 7


@live
def test_shell_has_a_private_bus_and_an_unlocked_keyring(lroom):
    assert lroom("init", "s1").returncode == 0
    res = lroom(
        "shell", "s1", "-c",
        'echo "$DBUS_SESSION_BUS_ADDRESS"; gdbus call --session --dest org.freedesktop.secrets'
        " --object-path /org/freedesktop/secrets"
        " --method org.freedesktop.Secret.Service.ReadAlias default",
    )
    assert res.returncode == 0, res.stderr
    bus, alias = res.stdout.splitlines()
    assert f"{lroom.root}/s1/home/.cache/dbus/" in bus
    assert "/collection/" in alias and "'/'" not in alias


@live
def test_open_with_appends_and_runs(lroom, tmp_path):
    assert lroom("init", "s1").returncode == 0
    opened = tmp_path / "opened.txt"
    res = lroom(
        "shell", "s1", "-c", '"$BROWSER" https://example.test/one',
        "--open-with", f"sh -c 'echo \"$0\" >> {opened}'",
    )
    assert res.returncode == 0, res.stderr
    assert (lroom.root / "s1/run/urls.log").read_text() == "https://example.test/one\n"
    assert opened.read_text() == "https://example.test/one\n"


@live
def test_capture_redacts_and_scan_catches_the_value(lroom, tmp_path):
    lroom.start("r1", "leak")
    wait_for(lambda: "token is" in lroom("capture", "r1").stdout)
    shown = lroom("capture", "r1").stdout
    assert STUB_VALUE not in shown and "[redacted:STUB_KEY]" in shown
    lroom("stop", "r1")
    leaky, clean = tmp_path / "leaky.txt", tmp_path / "clean.txt"
    leaky.write_text(f"x {STUB_VALUE} y")
    clean.write_text("nothing here")
    assert lroom("scan", "r1", str(clean)).returncode == 0
    res = lroom("scan", "r1", str(clean), str(leaky))
    assert res.returncode != 0
    assert str(leaky) in res.stderr and STUB_VALUE not in res.stderr + res.stdout
    leaky.write_text((lroom.state / "canary").read_text())
    assert lroom("scan", "r1", str(leaky)).returncode != 0


def test_cost_matches_a_hand_computed_total(tmp_path):
    def usage(**kw):
        return {"message": {"id": kw.pop("id"), "model": kw.pop("model"), "usage": kw}}

    opus = dict(id="a", model="claude-opus-5-5", input_tokens=1000, output_tokens=2000,
                cache_read_input_tokens=10000, cache_creation_input_tokens=4000,
                cache_creation={"ephemeral_5m_input_tokens": 3000, "ephemeral_1h_input_tokens": 1000})
    lines = [
        usage(**opus),
        usage(**opus),  # the same message id again: the later entry replaces the earlier one
        usage(id="b", model="claude-sonnet-5-5", input_tokens=5000, output_tokens=1000,
              cache_creation_input_tokens=2000),  # no split: all of it counts as 5 minutes
        {"type": "user", "message": {"role": "user", "content": "hi"}},
    ]
    transcript = tmp_path / "t.jsonl"
    transcript.write_text("".join(json.dumps(line) + "\n" for line in lines))
    opus_cost = (1000 * 4 + 2000 * 20 + 10000 * 0.20 + 3000 * 4 * 1.25 + 1000 * 4 * 2) / 1e6
    sonnet_cost = (5000 * 2 + 1000 * 10 + 2000 * 2 * 1.25) / 1e6
    res = subprocess.run([sys.executable, "-I", str(TOOL), "cost", str(transcript)],
                         capture_output=True, text=True, check=False)
    assert res.returncode == 0
    assert res.stdout.strip() == f"${opus_cost + sonnet_cost:.4f}"


def test_an_unknown_model_is_priced_as_the_dearest(tmp_path):
    entry = {"message": {"id": "a", "model": "claude-future-9", "usage": {"output_tokens": 1000000}}}
    transcript = tmp_path / "t.jsonl"
    transcript.write_text(json.dumps(entry) + "\n")
    res = subprocess.run([sys.executable, "-I", str(TOOL), "cost", str(transcript)],
                         capture_output=True, text=True, check=False)
    assert res.stdout.strip() == "$50.0000"


@live
def test_run_refuses_a_missing_store_name_and_leaves_no_row(lroom):
    assert lroom("init", "r1").returncode == 0
    res = lroom("run", "r1", "--goal", "x", "--secret", "NO_SUCH_STORE")
    assert res.returncode != 0 and "NO_SUCH_STORE" in res.stderr
    assert lroom.ledger() == []


@live
def test_run_refuses_a_bad_secret_spec(lroom):
    assert lroom("init", "r1").returncode == 0
    assert lroom("run", "r1", "--goal", "x", "--secret", "lower:case").returncode != 0


def s8_available() -> bool:
    """Report whether the cleanroom user and its sudo rule exist on this host (Decide S-8)."""
    try:
        pwd.getpwnam("cleanroom")
    except KeyError:
        return False
    probe = subprocess.run(
        ["sudo", "-n", "-u", "cleanroom", "/usr/bin/python3", "-I", str(TOOL), "_child", "x", "bogus"],
        capture_output=True, text=True, check=False,
    )
    return "unknown _child step" in probe.stderr


@pytest.mark.skipif(not s8_available(), reason="no cleanroom user or sudo rule on this host")
@live
def test_the_session_runs_as_the_clean_user_and_cannot_read_the_store(tmp_path):
    base = Path(tempfile.mkdtemp(prefix="cleanroom-pytest-", dir="/var/tmp"))
    base.chmod(0o755)
    env = {**os.environ, "CLEANROOM_ROOT": str(base / "root"), "CLEANROOM_STATE": str(tmp_path)}

    def run(*args):
        return subprocess.run([sys.executable, "-I", str(TOOL), *args], env=env,
                              capture_output=True, text=True, check=False)

    try:
        assert run("init", "s1").returncode == 0
        res = run("shell", "s1", "-c",
                  "id -un; test -r /var/home/glw907/.local/secrets && echo READABLE || echo DENIED")
        assert res.stdout.split() == ["cleanroom", "DENIED"], res.stderr
        owner = (base / "root/s1/home/.claude/settings.json").stat().st_uid
        assert pwd.getpwuid(owner).pw_name == "cleanroom"
        for sub in ("root/s1", "root/s1/run"):
            assert (base / sub).stat().st_mode & stat.S_ISVTX, f"{sub} is not sticky"
        assert run("init", "s1", "--fresh", "--discard").returncode == 0
    finally:
        subprocess.run(
            ["sudo", "-n", "-u", "cleanroom", "--preserve-env=CLEANROOM_ROOT", "/usr/bin/python3",
             "-I", str(TOOL), "_child", "s1", "remove"],
            env=env, capture_output=True, check=False,
        )
        shutil.rmtree(base, ignore_errors=True)
