"""Tests for pass-report, driven by canned gh answers from tests/fixtures/pass-report."""

import importlib.machinery
import importlib.util
import json
import os
import io
import subprocess
import sys
import tarfile
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
    if "archive" in data:
        (state / "approval-queue").mkdir(parents=True, exist_ok=True)
        body = "".join(json.dumps(d) + "\n" for d in data["archive"]).encode()
        with tarfile.open(state / "approval-queue/archive-2026-11.tar.gz", "w:gz") as tar:
            info = tarfile.TarInfo("decisions.jsonl")
            info.size = len(body)
            tar.addfile(info, io.BytesIO(body))
    for doc, parts in data.get("store", {}).items():
        folder = state / "approval-queue/store" / doc
        folder.mkdir(parents=True)
        for name, value in parts.items():
            (folder / name).write_text(json.dumps(value))
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
    assert "Listing full" not in run.stdout


def test_archive_alone_gives_the_same_waits(tmp_path):
    data = fixture("waits.json")
    data["archive"] = data.pop("decisions")
    run = report(tmp_path, data)
    assert "| Waiting on Geoff | 2 | 15.5 | 30.0 | 31.0 |" in run.stdout
    assert "Negative waits dropped: 1" in run.stdout
    assert "not counted" not in run.stdout


def _decision(action, at):
    return {"action": action, "at": at}


STORE = {
    "repos": ["alpha", "beta"],
    "store": {
        # Sent back at 10:20, returned at 10:30, approved at 11:00: one 30 minute wait per PR.
        "20261110-100000-aaaaaa": {
            "meta.json": {"id": "x", "kind": "merge", "title": "t", "created": "2026-11-10T10:00:00Z", "versions": 2},
            "heads.json": [
                {"repo": "glw907/alpha", "number": 1, "head": "h1"},
                {"repo": "glw907/beta", "number": 2, "head": "h2"},
            ],
            "decision-1.json": _decision("sendback", "2026-11-10T10:20:00Z"),
            "decision-2.json": _decision("returned", "2026-11-10T10:30:00Z"),
            "decision-3.json": _decision("approve", "2026-11-10T11:00:00Z"),
        },
        # The undo cancels the approve, so the document stands undecided.
        "20261110-120000-bbbbbb": {
            "meta.json": {"id": "x", "kind": "merge", "title": "t", "created": "2026-11-10T12:00:00Z", "versions": 1},
            "heads.json": [{"repo": "glw907/alpha", "number": 3, "head": "h3"}],
            "decision-1.json": _decision("approve", "2026-11-10T12:10:00Z"),
            "decision-2.json": _decision("undo", "2026-11-10T12:11:00Z"),
        },
        "20261110-130000-cccccc": {
            "meta.json": {"id": "x", "kind": "merge", "title": "t", "created": "2026-11-10T13:00:00Z", "versions": 1},
            "heads.json": [{"repo": "glw907/alpha", "number": 4, "head": "h4"}],
            "decision-1.json": _decision("approve", "2026-11-10T13:10:00Z"),
        },
        "20261110-140000-dddddd": {
            "meta.json": {"id": "x", "kind": "design", "title": "t", "created": "2026-11-10T14:00:00Z", "versions": 1},
            "decision-1.json": _decision("approve", "2026-11-10T14:05:00Z"),
        },
        "20261110-150000-eeeeee": {
            "meta.json": {"id": "x", "kind": "report", "title": "t", "created": "2026-11-10T15:00:00Z", "versions": 1},
            "decision-1.json": _decision("read", "2026-11-10T15:05:00Z"),
        },
    },
}


def test_store_waits_run_from_creation_or_return_to_the_standing_decision(tmp_path):
    out = report(tmp_path, STORE).stdout
    assert "| Waiting on Geoff | 2 | 20.0 | 30.0 | 40.0 |" in out
    assert "| Waiting on Geoff | 1 | 30.0 | 30.0 | 30.0 |" in out
    assert "- Design and decide documents decided: 1" in out.splitlines()
    assert "Negative waits dropped: 0" in out


def test_store_beside_the_archive_adds_to_old_waits(tmp_path):
    data = {**STORE, "archive": fixture("waits.json")["decisions"]}
    out = report(tmp_path, data).stdout
    assert "| Waiting on Geoff | 4 | 20.0 | 30.0 | 71.0 |" in out


def test_listing_of_300_prs_is_named_as_full(tmp_path):
    prs = [
        {"number": n, "headRefName": f"b{n}", "createdAt": "2026-11-02T10:00:00Z",
         "mergedAt": "2026-11-02T11:00:00Z", "body": ""}
        for n in range(300)
    ]
    out = report(tmp_path, {"repos": ["alpha", "beta"], "prs": {"alpha": prs}}).stdout
    assert "- Listing full at 300 (older merged PRs missed): alpha" in out.splitlines()


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
    for name in ("runs.jsonl", "score-backfill.json"):
        assert any(l.startswith("- Not found: ") and l.endswith(name) for l in out.splitlines())
    assert "Not found: " + "~" not in out
    assert not any("decisions.jsonl" in l and l.startswith("- Not found") for l in out.splitlines())
    assert (
        "- Waits before the new queue: not counted (no decisions.jsonl and no archive-2026-11.tar.gz)"
        in out.splitlines()
    )


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


MISS_CLASSES = (
    "mechanism", "file-list", "permission", "design-gap", "stale-fact",
    "owner-call", "no-answer", "conflict", "estimate", "ambiguous",
)

MISS_TABLE = """\
## Planning misses

Miss lines: 15, in 3 of 7 merged PRs.

| Class | Misses | Per 100 merged PRs |
|---|---|---|
| mechanism | 3 | 42.9 |
| file-list | 2 | 28.6 |
| permission | 1 | 14.3 |
| design-gap | 1 | 14.3 |
| stale-fact | 1 | 14.3 |
| owner-call | 1 | 14.3 |
| no-answer | 1 | 14.3 |
| conflict | 1 | 14.3 |
| estimate | 1 | 14.3 |
| ambiguous | 1 | 14.3 |
| untagged | 2 | 28.6 |
| Total | 15 | 214.3 |"""

# The misses.json report as it stood before the misses section, minus the Window line.
OLD_REPORT = """\
# Pass score report


### alpha

| Row | n | Median | p90 | Total |
|---|---|---|---|---|
| PR open to merge | 6 | 180.0 | 180.0 | 1080.0 |
| Planned path (min) | 1 | 60.0 | 60.0 | 60.0 |
| Actual path (min) | 1 | 50.0 | 50.0 | 50.0 |
| Actual / planned | 1 | 0.8 | 0.8 | - |
| Fix rounds | 1 | 0.0 | 0.0 | 0.0 |
| Attended events | 1 | 0.0 | 0.0 | 0.0 |
| Escapes | 1 | 0.0 | 0.0 | 0.0 |

### beta

| Row | n | Median | p90 | Total |
|---|---|---|---|---|
| PR open to merge | 1 | 180.0 | 180.0 | 180.0 |

## Notes

- Gate records read: ~/.local/state/cairn-run-gate/runs.jsonl
- Not found: ~/.local/state/cairn-run-gate/runs.jsonl
- Waits before the new queue: not counted (no decisions.jsonl and no archive-2026-11.tar.gz)
- Not found: ~/Projects/initiatives/dev-speed/research/score-backfill.json
- Dropped gate records: 0
- Negative waits dropped: 0
- Malformed lines or rows skipped: 0
- PRs with no score: 6"""


def test_miss_lines_are_counted_by_tag(tmp_path):
    out = report(tmp_path, fixture("misses.json")).stdout
    start = out.index("## Planning misses")
    end = out.index("\n\n", out.index("| Total |", start))
    assert out[start:end] == MISS_TABLE
    assert out[end:].startswith("\n\n## Notes")


def test_line_with_no_tag_counts_as_untagged(tmp_path):
    data = {"repos": ["alpha"], "prs": {"alpha": [fixture("misses.json")["prs"]["alpha"][2]]}}
    out = report(tmp_path, data).stdout
    assert "Miss lines: 2, in 1 of 1 merged PRs." in out
    assert "| untagged | 2 | 200.0 |" in out
    for name in MISS_CLASSES:
        assert f"| {name} | 0 | 0.0 |" in out
    assert "| Total | 2 | 200.0 |" in out


def test_pr_without_the_section_adds_nothing(tmp_path):
    out = report(tmp_path, fixture("score_wins.json")).stdout
    assert "## Planning misses\n\nNo miss lines in the window.\n" in out
    assert "| Class |" not in out


def test_other_tables_do_not_change(tmp_path):
    run = report(tmp_path, fixture("misses.json"))
    lines = [l for l in run.stdout.splitlines() if not l.startswith("Window:")]
    text = "\n".join(lines).replace(str(run.home), "~")
    start = text.find("## Planning misses")
    if start != -1:
        end = text.find("## Notes", start)
        text = text[:start] + (text[end:] if end != -1 else "")
    assert text == OLD_REPORT
    assert "## Planning misses" in run.stdout


@pytest.mark.parametrize(
    "body, want",
    [
        ("## Planning misses \t\n- [mechanism] a", ["mechanism"]),
        ("## Planning misses\n+ [conflict] a\n1) [estimate] b\n`[ambiguous]` c", ["conflict", "estimate", "ambiguous"]),
        ("## Planning misses\n-  [mechanism] spaced", ["mechanism"]),
        ("## Planning misses\n- NONE.  \n- \n- - -\n\t- [mechanism] tabbed", []),
        ("## Planning misses\n- [mechanism] a\n### Deeper\n- [conflict] b\n# Next\n- [estimate] c", ["mechanism", "conflict"]),
        ("## Planning misses\n- [mechanism] a\n## Other\n## Planning misses\n- [conflict] b", ["mechanism"]),
        ("## Planning misses:\n- [mechanism] a", []),
    ],
)
def test_miss_classes_follow_the_section_rules(body, want):
    assert pass_report.miss_classes(body) == want
