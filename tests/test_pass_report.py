"""Tests for pass-report, driven by canned gh answers from tests/fixtures/pass-report."""

import importlib.machinery
import importlib.util
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "bin/.local/bin/pass-report"
FIXTURES = ROOT / "tests/fixtures/pass-report"
loader = importlib.machinery.SourceFileLoader("pass_report", str(SCRIPT))
spec = importlib.util.spec_from_loader("pass_report", loader)
pass_report = importlib.util.module_from_spec(spec)
loader.exec_module(pass_report)


def materialize(tmp_path, data):
    """Write the fixture's state files under a fake home and its gh answers beside it."""
    home = tmp_path / "home"
    home.mkdir(exist_ok=True)
    data = json.loads(json.dumps(data).replace("{HOME}", str(home)))
    state = home / ".local/state"
    if "records" in data:
        lines = [r if isinstance(r, str) else json.dumps(r) for r in data["records"]]
        (state / "cairn-run-gate").mkdir(parents=True)
        (state / "cairn-run-gate/runs.jsonl").write_text("\n".join(lines) + "\n")
    if "decisions" in data:
        (state / "approval-queue").mkdir(parents=True)
        lines = [json.dumps(d) for d in data["decisions"]]
        (state / "approval-queue/decisions.jsonl").write_text("\n".join(lines) + "\n")
    if "backfill" in data:
        back = home / "Projects/initiatives/dev-speed/research"
        back.mkdir(parents=True)
        (back / "score-backfill.json").write_text(json.dumps(data["backfill"]))
    gh_data = tmp_path / "gh.json"
    gh_data.write_text(json.dumps(data))
    return home, gh_data


def report(tmp_path, data, *extra):
    home, gh_data = materialize(tmp_path, data)
    log = tmp_path / "gh.log"
    env = {
        **os.environ,
        "PASS_REPORT_GH": str(FIXTURES / "fake-gh"),
        "PASS_REPORT_HOME": str(home),
        "XDG_CACHE_HOME": str(tmp_path / "cache"),
        "FAKE_GH_DATA": str(gh_data),
        "FAKE_GH_LOG": str(log),
    }
    run = subprocess.run(
        [sys.executable, "-I", str(SCRIPT), "--since", "2026-10-01", *extra],
        capture_output=True, text=True, env=env,
    )
    run.log = log.read_text().splitlines() if log.exists() else []
    run.home = home
    return run


def fixture(name):
    return json.loads((FIXTURES / name).read_text())


def test_ci_wait_is_the_union_of_overlapping_runs(tmp_path):
    out = report(tmp_path, fixture("union.json")).stdout
    # 10:05 to 10:50 is 45 minutes; summing the four runs would give 70.
    assert "| CI wait on the PR | 1 | 45.0 | 45.0 | 45.0 |" in out
    assert "dynamic" not in out


def test_run_list_is_cached_across_runs(tmp_path):
    first = report(tmp_path, fixture("union.json"))
    env = {
        **os.environ,
        "PASS_REPORT_GH": str(FIXTURES / "fake-gh"),
        "PASS_REPORT_HOME": str(first.home),
        "XDG_CACHE_HOME": str(tmp_path / "cache"),
        "FAKE_GH_DATA": str(tmp_path / "gh.json"),
        "FAKE_GH_LOG": str(tmp_path / "gh.log"),
    }
    # Sleep past a second boundary so a window keyed to the current second would differ.
    time.sleep(1.1)
    subprocess.run([sys.executable, "-I", str(SCRIPT), "--since", "2026-10-01"], env=env, capture_output=True, check=True)
    calls = (tmp_path / "gh.log").read_text().splitlines()
    assert sum(c.startswith("run list") for c in calls) == 1


def test_full_run_range_is_split_and_both_halves_counted(tmp_path):
    start = datetime(2026, 11, 1, tzinfo=timezone.utc)
    runs = []
    for i in range(1000):
        began = start + timedelta(minutes=10 * i)
        runs.append({
            "databaseId": i, "workflowName": "ci", "headBranch": "main", "headSha": "s",
            "event": "push", "conclusion": "success", "status": "completed",
            "startedAt": began.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "updatedAt": (began + timedelta(minutes=5)).strftime("%Y-%m-%dT%H:%M:%SZ"),
        })
    run = report(tmp_path, {"repos": ["alpha"], "runs": {"alpha": runs}})
    assert "| CI on the default branch | 1000 | 5.0 | 5.0 | 5000.0 |" in run.stdout
    assert len([c for c in run.log if c.startswith("run list")]) > 1


def test_worktree_gate_record_folds_into_its_repo(tmp_path):
    run = report(tmp_path, fixture("gate_fold.json"))
    assert "### workstation" in run.stdout
    # 600 s run minus 60 s lock wait; the "lost" run adds nothing.
    assert "| Local gates | 1 | 9.0 | 9.0 | 9.0 |" in run.stdout
    assert "Lock wait behind other gates: 1.0 min" in run.stdout


def test_pr_gate_seconds_is_a_plain_join(tmp_path):
    home, _ = materialize(tmp_path, fixture("gate_fold.json"))
    lines = (home / ".local/state/cairn-run-gate/runs.jsonl").read_text().splitlines()
    records = [pass_report.parse_record(line) for line in lines]
    pr = pass_report.build_pr("workstation", fixture("gate_fold.json")["prs"]["workstation"][0])
    assert pass_report.pr_gate_seconds(pr, records, [pr], {"workstation"}, home) == 540


def test_branch_join_and_dropped_record(tmp_path):
    run = report(tmp_path, fixture("gate_branch.json"))
    assert "| Local gates | 1 | 6.0 | 6.0 | 6.0 |" in run.stdout
    assert "Dropped gate records: 1" in run.stdout


def test_decision_waits_use_anchorage_local_time(tmp_path):
    run = report(tmp_path, fixture("waits.json"))
    # 30 min in November (UTC-9) and 1 min on the real October line (UTC-8). A fixed UTC-9
    # offset would turn the October wait negative.
    assert "| Waiting on Geoff | 2 | 15.5 | 30.0 | 31.0 |" in run.stdout
    assert "Negative waits dropped: 1" in run.stdout


def test_score_line_beats_backfill_row(tmp_path):
    out = report(tmp_path, fixture("score_wins.json")).stdout
    assert "| Planned path (min) | 2 | 150.0 | 200.0 | 300.0 |" in out
    assert "| Actual / planned | 2 | 0.5 | 0.5 | - |" in out
    assert "| Fix rounds | 2 | 2.0 | 3.0 | 4.0 |" in out
    assert "PRs with no score: 0" in out


def test_malformed_jsonl_line_is_skipped_and_counted(tmp_path):
    run = report(tmp_path, fixture("malformed.json"))
    assert run.returncode == 0
    assert "| Local gates | 1 | 12.0 | 12.0 | 12.0 |" in run.stdout
    assert "Malformed lines or rows skipped: 1" in run.stdout


def test_repo_without_data_prints_one_line(tmp_path):
    out = report(tmp_path, fixture("empty.json")).stdout
    assert "### quiet\n\nNo data in the window.\n" in out
    assert "| Row |" not in out


def test_missing_state_files_are_named_in_the_footer(tmp_path):
    out = report(tmp_path, fixture("empty.json")).stdout
    for name in ("runs.jsonl", "decisions.jsonl", "score-backfill.json"):
        assert any(l.startswith("- Not found: ") and l.endswith(name) for l in out.splitlines())


def test_missing_records_file_exits_2(tmp_path):
    run = report(tmp_path, fixture("empty.json"), "--records", str(tmp_path / "nope.jsonl"))
    assert run.returncode == 2
    assert "nope.jsonl" in run.stderr


def test_gh_failure_exits_1_with_its_message(tmp_path):
    run = report(tmp_path, {"repos": [], "fail": "gh: boom"})
    assert run.returncode == 1
    assert "gh: boom" in run.stderr


def test_rate_limited_repo_is_marked_partial(tmp_path):
    data = {**fixture("union.json"), "ratelimit": ["alpha"]}
    run = report(tmp_path, data)
    assert run.returncode == 0
    assert "Partial data (gh rate limit, cache used): alpha" in run.stdout


@pytest.mark.parametrize(
    "top, want",
    [
        ("{h}/Projects/cairn-cms/.claude/worktrees/x", "cairn-cms"),
        ("{h}/.dotfiles", "workstation"),
        ("{h}/.dotfiles-pass/sub", "workstation"),
        ("{h}/Projects/workstation-wt/a", "workstation"),
        ("{h}/.cache/wt-x", None),
        ("/elsewhere/Projects/alpha", None),
    ],
)
def test_toplevel_mapping(top, want):
    home = Path("/h")
    assert pass_report.repo_of_toplevel(top.format(h=home), home) == want
