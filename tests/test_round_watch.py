"""Tests for round-watch, driven by subprocess against fake `claude` and `gh` commands."""

import json
import os
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "bin/.local/bin/round-watch"

# Each fake prints the file for its call number, or the last file once the calls outrun them.
# A file holding the word FAIL makes that call exit 1.
FAKE = """#!/usr/bin/env bash
dir="$(dirname "$0")/{name}"
n=$(cat "$dir/count" 2>/dev/null || echo 0)
echo $((n + 1)) > "$dir/count"
f="$dir/$n.json"
[ -f "$f" ] || f="$(ls "$dir"/*.json | sort -V | tail -n 1)"
grep -q '^FAIL$' "$f" && exit 1
cat "$f"
"""


def agent(state, name="cairn-cms-tui-language-2"):
    """Return one row of `claude agents --json`."""
    return {"id": "abc12345", "name": name, "state": state}


def pull(draft=True, conclusion=None, branch="tui-language-2"):
    """Return one row of `gh pr list --json`."""
    rollup = [{"status": "COMPLETED" if conclusion else "IN_PROGRESS", "conclusion": conclusion or ""}]
    return {
        "number": 247,
        "isDraft": draft,
        "headRefName": branch,
        "headRefOid": "e19f5fbf2aaaa",
        "statusCheckRollup": rollup,
    }


def watch(tmp_path, agents, pulls, polls=4):
    """Run round-watch over the given sequence of readings and return the finished process."""
    for name, readings in (("claude", agents), ("gh", pulls)):
        (tmp_path / name).mkdir()
        for i, reading in enumerate(readings):
            text = "FAIL\n" if reading == "FAIL" else json.dumps(reading)
            (tmp_path / name / f"{i}.json").write_text(text)
        (tmp_path / "bin").mkdir(exist_ok=True)
        fake = tmp_path / "bin" / name
        fake.write_text(FAKE.format(name=f"../{name}"))
        fake.chmod(0o755)
    env = dict(os.environ, PATH=f"{tmp_path / 'bin'}:{os.environ['PATH']}")
    env.update(ROUND_WATCH_EVERY="0", ROUND_WATCH_POLLS=str(polls))
    return subprocess.run(
        [sys.executable, "-I", str(SCRIPT), "cairn-cms-tui-language", "glw907/cairn-cms", "tui-language"],
        capture_output=True,
        text=True,
        env=env,
        timeout=60,
        check=False,
    )


def test_exits_when_the_executor_finishes(tmp_path):
    done = watch(tmp_path, [[agent("working")], [agent("idle")]], [[pull()], [pull(False, "SUCCESS")]])
    assert done.returncode == 0
    assert "now: session cairn-cms-tui-language-2 abc12345 idle" in done.stdout
    assert "now: pr #247 tui-language-2 ready e19f5fbf2 checks pass" in done.stdout


def test_exits_when_checks_finish_under_an_idle_session(tmp_path):
    done = watch(tmp_path, [[agent("idle")]], [[pull()], [pull(conclusion="FAILURE")]])
    assert done.returncode == 0
    assert "checks fail" in done.stdout


def test_stays_up_while_a_session_works(tmp_path):
    done = watch(tmp_path, [[agent("working")]], [[pull()], [pull(False, "SUCCESS")]])
    assert done.returncode == 3
    assert done.stdout == ""


def test_stays_up_when_nothing_changes(tmp_path):
    done = watch(tmp_path, [[agent("idle")]], [[pull()]])
    assert done.returncode == 3


def test_a_failed_read_is_no_change(tmp_path):
    done = watch(tmp_path, [[agent("idle")], "FAIL", [agent("idle")]], [[pull()], "FAIL", [pull()]])
    assert done.returncode == 3


def test_ignores_other_rounds(tmp_path):
    other = [agent("idle"), agent("done", name="cairn-cms-theme-catalog-1")]
    done = watch(
        tmp_path,
        [[agent("idle")], other],
        [[pull()], [pull(), pull(False, "SUCCESS", branch="theme-catalog-1")]],
    )
    assert done.returncode == 3


def test_a_failed_first_read_is_no_baseline(tmp_path):
    done = watch(tmp_path, ["FAIL", [agent("idle")]], ["FAIL", [pull()]])
    assert done.returncode == 3
    assert done.stdout == ""


def test_prefixes_that_match_nothing_exit_at_once(tmp_path):
    done = watch(tmp_path, [[agent("idle", name="other-1")]], [[pull(branch="other-1")]])
    assert done.returncode == 4
    assert "no session named" in done.stderr


def test_usage(tmp_path):
    done = subprocess.run([sys.executable, "-I", str(SCRIPT)], capture_output=True, text=True, check=False)
    assert done.returncode == 2
