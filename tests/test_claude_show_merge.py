"""Tests for claude-show-merge, driven by subprocess with fake gh and claude on PATH."""

import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "bin/.local/bin/claude-show-merge"
SITE_PASS = ROOT / "claude/.claude/skills/site-pass/SKILL.md"
DOTFILES_PASS = ROOT / ".claude/skills/dotfiles-pass/SKILL.md"
SETTINGS = ROOT / "claude/.claude/settings.json"
CAIRN_BUILD = Path.home() / "Projects/cairn-cms/.claude/skills/cairn-build/SKILL.md"

REPO = "glw907/cc-desk-scratch"
HEAD = "a" * 40
PARENT_HEAD = "b" * 40
MERGE_COMMIT = "c" * 40
CHECKS = ["task-session", "repo", "earlier-result", "spec", "session", "pull-request", "ci",
          "review", "body", "files", "current"]

# The spec's table row for glw907/workstation, every glob and script path written out.
WORKSTATION_ASK_ONLY = [
    "claude/.claude/settings.json", "claude/.claude/CLAUDE.md", "claude/.claude/rules/**",
    "claude/.claude/tooling/**", "claude/.claude/skills/building-from-specs/**",
    "claude/.claude/skills/cairn-pass/**", "claude/.claude/skills/site-pass/**",
    ".claude/skills/dotfiles-pass/**", ".github/**", "scripts/**", "secrets/**", "bash/.bashrc",
    "bluefin/**",
    "bin/.local/bin/claude-awake-touch", "bin/.local/bin/claude-block-pass",
    "bin/.local/bin/claude-context-budget", "bin/.local/bin/claude-denied-log",
    "bin/.local/bin/claude-git-guard", "bin/.local/bin/claude-memory-write-check",
    "bin/.local/bin/claude-notify", "bin/.local/bin/claude-secret-guard",
    "bin/.local/bin/claude-tail-guard", "bin/.local/bin/claude-tierguard",
    "bin/.local/bin/claude-pass", "bin/.local/bin/ws-pass-key", "bin/.local/bin/pass-count",
    "bin/.local/bin/pass-access", "bin/.local/bin/pass-sitting", "bin/.local/bin/check-drift",
    "bin/.local/bin/claude-askpass", "bin/.local/bin/claude-sudo-setup",
    "bin/.local/bin/claude-sudo-clear", "bin/.local/bin/secret-receive",
    "bin/.local/bin/claude-show-merge", "bin/.local/bin/cairn-run-gate", "bin/.local/bin/ci-green",
    "bin/.local/bin/ci-green-lib.mjs",
]
SITES = {"ecxc-ski": "ecxc-ski", "907-life-legacy": "907-life",
         "aksailingclub-org": "aksailingclub-org", "cairn-pub": "cairn-pub"}
SESSION_FILES = [".claude/**", "CLAUDE.md", "**/CLAUDE.md"]

FAKE_GH = r'''#!/usr/bin/env python3
import json, os, sys
state = json.load(open(os.environ["FAKE_STATE"]))
argv = sys.argv[1:]
with open(os.environ["FAKE_LOG"], "a") as log:
    log.write(json.dumps(argv) + "\n")
joined = " ".join(argv)
for prefix in state.get("fail", []):
    if joined.startswith(prefix):
        sys.stderr.write("HTTP 502: Bad Gateway\n")
        sys.exit(1)
if argv[:2] == ["repo", "view"]:
    print(json.dumps({"defaultBranchRef": {"name": state["default"]}}))
elif argv[:2] == ["pr", "view"]:
    pr = state["prs"][argv[2]]
    fields = argv[argv.index("--json") + 1].split(",")
    if "mergeCommit" in fields:
        pr = dict(pr, mergeCommit={"oid": state["merge_commit"]})
    print(json.dumps({field: pr.get(field) for field in fields}))
elif argv[:2] == ["pr", "checks"]:
    checks = state["checks"]
    sys.stdout.write(checks.get("stdout", ""))
    sys.stderr.write(checks.get("stderr", ""))
    sys.exit(checks.get("exit", 0))
elif argv[:2] == ["pr", "merge"]:
    head = argv[argv.index("--match-head-commit") + 1]
    if head != state.get("merge_head", state["prs"][argv[2]]["headRefOid"]):
        sys.stderr.write("GraphQL: Head branch was modified. Review and try the merge again.\n")
        sys.exit(1)
elif argv[:2] == ["pr", "comment"]:
    pass
elif argv[0] == "api" and argv[1].endswith("/files"):
    for page in state["files"]:
        print(json.dumps(page))
elif argv[0] == "api" and "/compare/" in argv[1]:
    print(json.dumps(state["compare"]))
else:
    sys.stderr.write("fake gh: unknown call " + joined + "\n")
    sys.exit(4)
'''

FAKE_CLAUDE = r'''#!/usr/bin/env python3
import json, os, sys
state = json.load(open(os.environ["FAKE_STATE"]))
if sys.argv[1:] != ["agents", "--json", "--all"] or state.get("agents_fail"):
    sys.stderr.write("claude: could not list agents\n")
    sys.exit(1)
print(json.dumps(state["agents"]))
'''

SPEC = """# Spec: demo

Status: {status}

## Task 1: demo

Name: demo
Tier: {tier}
Files: `show/*.txt`

The task writes show files.

```text
Name: demo
Tier: ask
```

## Task 2: other

Name: other
Tier: ask
Files: `other/**`
"""


def git(repo: Path, *args: str, date: str | None = None) -> None:
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    if date:
        env.update(GIT_AUTHOR_DATE=date, GIT_COMMITTER_DATE=date)
    subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True, env=env)


class Fixture:
    """One pull request whose every check passes until a test changes a part of it."""

    def __init__(self, tmp: Path):
        self.tmp = tmp
        self.bin = tmp / "bin"
        self.bin.mkdir()
        for name, text in (("gh", FAKE_GH), ("claude", FAKE_CLAUDE)):
            (self.bin / name).write_text(text)
            (self.bin / name).chmod(0o755)
        self.specs = tmp / "specs"
        self.specs.mkdir()
        git(self.specs, "init", "-q", "-b", "main")
        git(self.specs, "config", "user.email", "t@example.com")
        git(self.specs, "config", "user.name", "T")
        self.spec = self.specs / "spec.md"
        self.commit_spec("approved by Geoff on 2026-11-01.", "show", "2026-11-01T00:00:00Z")
        self.state_dir = tmp / "state"
        self.log = tmp / "gh.log"
        self.repo = REPO
        self.env_extra: dict[str, str] = {}
        self.state = {
            "default": "main",
            "prs": {"7": {"state": "OPEN", "isDraft": False, "mergeable": "MERGEABLE",
                          "baseRefName": "main", "headRefOid": HEAD,
                          "createdAt": "2026-11-10T00:00:00Z", "body": self.body()}},
            "checks": {"exit": 0, "stdout": "gate\tpass\t1m\thttps://x\n"},
            "files": [[{"filename": "show/a.txt", "status": "added"}]],
            "compare": {"files": [{"filename": "README.md"}]},
            "merge_commit": MERGE_COMMIT,
            "agents": [{"name": "demo", "state": "failed", "startedAt": 1},
                       {"name": "demo", "state": "done", "startedAt": 2},
                       {"name": "other", "state": "working", "startedAt": 3}],
            "fail": [],
        }

    def commit_spec(self, status: str, tier: str, date: str) -> None:
        self.spec.write_text(SPEC.format(status=status, tier=tier))
        git(self.specs, "add", "spec.md")
        git(self.specs, "commit", "-q", "-m", "spec", date=date)

    def body(self, first: str = "Demo landed.", extra: str = "") -> str:
        score = '{"planPathMin": 20, "verdict": "accept", "openFindings": 0, "unmet": 0}'
        return (f"{first}\n\nFrom spec {self.spec}, task demo.\n{extra}\n"
                f"<!-- task-score {score} -->\n")

    @property
    def pr(self) -> dict:
        return self.state["prs"]["7"]

    def run(self, *args: str) -> subprocess.CompletedProcess:
        state_file = self.tmp / "state.json"
        state_file.write_text(json.dumps(self.state))
        env = {key: value for key, value in os.environ.items()
               if not key.startswith("GIT_") and key != "CLAUDE_TASK_SESSION"}
        env.update(PATH=f"{self.bin}:{env['PATH']}", XDG_STATE_HOME=str(self.state_dir),
                   FAKE_STATE=str(state_file), FAKE_LOG=str(self.log), **self.env_extra)
        argv = list(args) or [self.repo, "7", "--spec", str(self.spec), "--task", "demo"]
        return subprocess.run([str(SCRIPT), *argv], capture_output=True, text=True, env=env,
                              check=False, timeout=60)

    def rows(self) -> list[dict]:
        path = self.state_dir / "claude-show-merge.jsonl"
        return [json.loads(line) for line in path.read_text().splitlines()] if path.exists() else []

    def calls(self) -> list[list[str]]:
        if not self.log.exists():
            return []
        return [json.loads(line) for line in self.log.read_text().splitlines()]


@pytest.fixture
def fx(tmp_path):
    return Fixture(tmp_path)


def verdicts(stdout: str) -> dict[str, str]:
    """Map each check to its printed line."""
    found = {}
    for printed in stdout.splitlines():
        match = re.match(r"(pass|fail|wait) ([\w-]+)", printed)
        if match and match.group(2) in CHECKS:
            found[match.group(2)] = printed
    return found


def assert_only(result, check: str, word: str = "fail") -> str:
    """Assert that every check printed a line and only `check` printed `word`; return its line."""
    lines = verdicts(result.stdout)
    assert sorted(lines) == sorted(CHECKS), result.stdout
    for name, printed in lines.items():
        if name == check:
            assert printed.startswith(f"{word} {check}: "), result.stdout
        else:
            assert printed == f"pass {name}", result.stdout
    return lines[check]


def test_help_names_every_option():
    out = subprocess.run([str(SCRIPT), "--help"], capture_output=True, text=True, check=True).stdout
    for option in ("--spec", "--task", "--dry-run", "--report", "--ask-only"):
        assert option in out


@pytest.mark.parametrize("repo", ["glw907/workstation", "glw907/cairn-cms", "glw907/ecxc-ski",
                                  "glw907/907-life-legacy", "glw907/aksailingclub-org",
                                  "glw907/cairn-pub", "glw907/cc-desk-scratch"])
def test_ask_only_lists_each_mapped_repo(repo):
    result = subprocess.run([str(SCRIPT), "--ask-only", repo], capture_output=True, text=True)
    assert result.returncode == 0
    assert result.stdout.strip()


@pytest.mark.parametrize("repo", ["glw907/standards", "glw907/907-life"])
def test_ask_only_refuses_an_unmapped_repo(repo):
    result = subprocess.run([str(SCRIPT), "--ask-only", repo], capture_output=True, text=True)
    assert result.returncode == 1
    assert result.stdout == ""


def ask_only(repo: str) -> list[str]:
    return subprocess.run([str(SCRIPT), "--ask-only", repo], capture_output=True, text=True,
                          check=True).stdout.splitlines()


def test_workstation_list_holds_the_spec_table():
    lines = ask_only("glw907/workstation")
    assert [glob for glob in WORKSTATION_ASK_ONLY if glob not in lines] == []


def test_workstation_list_holds_every_hook_script_settings_runs():
    hooks = json.dumps(json.loads(SETTINGS.read_text())["hooks"])
    names = set(re.findall(r"\b(claude-[\w-]+|cairn-[\w-]+)\b", hooks))
    scripts = {name for name in names if (ROOT / "bin/.local/bin" / name).exists()}
    assert scripts
    lines = ask_only("glw907/workstation")
    assert sorted(name for name in scripts if f"bin/.local/bin/{name}" not in lines) == []


def expand(glob: str) -> list[str]:
    """Write out the first brace group of a glob, recursively."""
    found = re.search(r"\{([^{}]*)\}", glob)
    if not found:
        return [glob]
    return [out for option in found.group(1).split(",")
            for out in expand(glob[:found.start()] + option + glob[found.end():])]


def test_workstation_list_holds_every_dotfiles_pass_secrets_script():
    text = DOTFILES_PASS.read_text()
    section = text.split("These paths touch secrets", 1)[1].split("A path in both", 1)[0]
    scripts = [path for raw in re.findall(r"`(bin/\.local/bin/[^`]+)`", section)
               for path in expand(raw)]
    assert len(scripts) >= 10
    lines = ask_only("glw907/workstation")
    assert [path for path in scripts if path not in lines] == []


def site_map() -> dict[str, list[str]]:
    """Read site-pass "Risk-class path map" into the globs for every site and each site's adds."""
    paragraph = SITE_PASS.read_text().split("**Risk-class path map**", 1)[1].split("\n\n", 1)[0]
    owner, found = "every", {"every": []}
    for match in re.finditer(r"([\w-]+) adds|`([^`]+)`", paragraph):
        if match.group(1):
            owner = match.group(1)
            found.setdefault(owner, [])
        elif match.group(2) in ("auth-data", "runner", "ordinary"):
            owner = "every" if match.group(2) == "runner" else owner
        else:
            found[owner].extend(expand(match.group(2)))
    return found


@pytest.mark.parametrize("key", sorted(SITES))
def test_site_lists_follow_site_pass(key):
    found = site_map()
    assert found["every"] and "aksailingclub-org" in found
    lines = ask_only(f"glw907/{key}")
    own = found.get(SITES[key], [])
    assert [glob for glob in found["every"] + own + SESSION_FILES if glob not in lines] == []
    others = {glob for site, globs in found.items() if site not in ("every", SITES[key])
              for glob in globs} - set(found["every"]) - set(own)
    assert sorted(others & set(lines)) == []


def test_cairn_cms_list_follows_cairn_build():
    if not CAIRN_BUILD.exists():
        pytest.skip("no cairn-cms checkout")
    text = CAIRN_BUILD.read_text().split("## Risk classes", 1)[1].split("- `ordinary`", 1)[0]
    globs = [glob.replace("\\[", "[[]").replace("\\]", "[]]")
             for raw in re.findall(r"`([^`]+)`", text) if raw not in ("auth-data", "runner", "[token]")
             for glob in expand(raw)]
    lines = ask_only("glw907/cairn-cms")
    assert [glob for glob in globs + SESSION_FILES if glob not in lines] == []


def test_a_full_pass_merges_at_the_checked_head(fx):
    result = fx.run()
    assert result.returncode == 0, result.stdout + result.stderr
    assert all(line == f"pass {name}" for name, line in verdicts(result.stdout).items())
    assert f"merged {REPO}#7 {MERGE_COMMIT}" in result.stdout.splitlines()
    assert f"undo: git revert -m 1 {MERGE_COMMIT}" in result.stdout.splitlines()
    assert ["pr", "merge", "7", "--repo", REPO, "--merge", "--match-head-commit", HEAD] in fx.calls()
    rows = fx.rows()
    assert [(row["result"], row["mergeCommit"], row["task"]) for row in rows] == [
        ("merged", MERGE_COMMIT, "demo")]
    comments = [call for call in fx.calls() if call[:2] == ["pr", "comment"]]
    assert len(comments) == 1 and f"merged {REPO}#7 {MERGE_COMMIT}" in comments[0][-1]


def test_report_prints_each_row_once(fx):
    assert fx.run().returncode == 0
    first = fx.run("--report")
    assert first.returncode == 0
    lines = first.stdout.splitlines()
    assert len(lines) == 1
    assert f"{REPO}#7" in lines[0] and f"git revert -m 1 {MERGE_COMMIT}" in lines[0]
    second = fx.run("--report")
    assert (second.returncode, second.stdout) == (0, "")


def test_dry_run_merges_nothing_and_writes_no_row(fx):
    result = fx.run(REPO, "7", "--spec", str(fx.spec), "--task", "demo", "--dry-run")
    assert result.returncode == 0, result.stdout
    assert not [call for call in fx.calls() if call[:2] in (["pr", "merge"], ["pr", "comment"])]
    assert fx.rows() == []


def test_check_1_task_session(fx):
    fx.env_extra["CLAUDE_TASK_SESSION"] = "1"
    result = fx.run()
    assert result.returncode == 1
    assert "CLAUDE_TASK_SESSION" in assert_only(result, "task-session")


def test_check_2_repo(fx):
    fx.repo = "glw907/standards"
    result = fx.run()
    assert result.returncode == 1
    assert "no Ask-only list" in assert_only(result, "repo")


def test_check_3_earlier_result(fx):
    fx.state_dir.mkdir()
    (fx.state_dir / "claude-show-merge.jsonl").write_text(json.dumps(
        {"time": "2026-11-20T00:00:00+00:00", "repo": REPO, "number": 7, "result": "ask"}) + "\n")
    result = fx.run()
    assert result.returncode == 1
    assert "ask row" in assert_only(result, "earlier-result")
    assert not [call for call in fx.calls() if call[:2] == ["pr", "merge"]]


def test_check_4_spec_status(fx):
    fx.commit_spec("draft", "show", "2026-11-01T00:00:01Z")
    result = fx.run()
    assert result.returncode == 1
    assert "not approved" in assert_only(result, "spec")


def test_check_4_spec_tier_changed_after_the_task_started(fx):
    fx.commit_spec("approved by Geoff on 2026-11-01.", "ask", "2026-11-01T00:00:01Z")
    fx.commit_spec("approved by Geoff on 2026-11-01.", "show", "2026-11-15T00:00:00Z")
    assert "Tier: show" in fx.spec.read_text()
    result = fx.run()
    assert result.returncode == 1
    assert "Tier" in assert_only(result, "spec")


def test_check_4_spec_uncommitted_change(fx):
    fx.spec.write_text(fx.spec.read_text() + "\nMore.\n")
    result = fx.run()
    assert result.returncode == 1
    assert "uncommitted" in assert_only(result, "spec")


def test_check_4_missing_section_is_named(fx):
    result = fx.run(REPO, "7", "--spec", str(fx.spec), "--task", "absent", "--dry-run")
    assert result.returncode == 1
    assert "no section holds `Name: absent`" in verdicts(result.stdout)["spec"]


def test_check_5_session(fx):
    fx.state["agents"].append({"name": "demo", "state": "blocked", "startedAt": 9})
    result = fx.run()
    assert result.returncode == 1
    assert "blocked" in assert_only(result, "session")


def test_check_6_pull_request(fx):
    fx.pr["isDraft"] = True
    result = fx.run()
    assert result.returncode == 1
    assert "draft" in assert_only(result, "pull-request")


def test_check_6_conflicting(fx):
    fx.pr["mergeable"] = "CONFLICTING"
    result = fx.run()
    assert result.returncode == 1
    assert "CONFLICTING" in assert_only(result, "pull-request")


def test_check_7_ci(fx):
    fx.state["checks"] = {"exit": 1, "stdout": "gate\tfail\t1m\thttps://x\n"}
    result = fx.run()
    assert result.returncode == 1
    assert "gate" in assert_only(result, "ci")


def test_check_7_no_checks_fails_outside_the_workstation(fx):
    fx.state["checks"] = {"exit": 1, "stderr": "no checks reported on the 'x' branch\n"}
    result = fx.run()
    assert result.returncode == 1
    assert "no checks reported" in assert_only(result, "ci")


def test_check_8_review(fx):
    fx.pr["body"] = fx.pr["body"].replace('"openFindings": 0', '"openFindings": 1')
    result = fx.run()
    assert result.returncode == 1
    assert "openFindings" in assert_only(result, "review")


def test_check_9_body(fx):
    fx.pr["body"] = fx.body(extra="\n## For Geoff\n\nOne choice.\n")
    result = fx.run()
    assert result.returncode == 1
    assert "For Geoff" in assert_only(result, "body")


def test_check_9_from_spec_line_names_the_given_task(fx):
    fx.pr["body"] = fx.pr["body"].replace("task demo.", "task other.")
    result = fx.run()
    assert result.returncode == 1
    assert "From spec" in assert_only(result, "body")


def test_check_10_files(fx):
    fx.state["files"] = [[{"filename": "show/a.txt"}], [{"filename": "show/extra.md"}]]
    result = fx.run()
    assert result.returncode == 1
    assert "show/extra.md" in assert_only(result, "files")


def test_check_10_renamed_from_an_ask_only_path(fx):
    fx.state["files"] = [[{"filename": "show/a.txt", "previous_filename": "scripts/a.txt"}]]
    result = fx.run()
    assert result.returncode == 1
    assert "scripts/a.txt" in assert_only(result, "files")


def test_check_11_current(fx):
    fx.state["compare"] = {"files": [{"filename": "show/a.txt"}]}
    result = fx.run()
    assert result.returncode == 1
    assert "show/a.txt" in assert_only(result, "current")


def test_check_11_compare_list_at_the_cap_fails(fx):
    fx.state["compare"] = {"files": [{"filename": f"docs/{index}.md"} for index in range(300)]}
    result = fx.run()
    assert result.returncode == 1
    assert "300" in assert_only(result, "current")


def test_check_11_child_whose_parent_merged_at_another_sha(fx):
    fx.pr["body"] = fx.body(first=f"Built on #3 at {PARENT_HEAD}.")
    fx.state["prs"]["3"] = {"state": "MERGED", "headRefOid": "d" * 40}
    result = fx.run()
    assert result.returncode == 1
    assert "#3" in assert_only(result, "current")


def test_check_11_child_whose_parent_merged_at_the_named_sha(fx):
    fx.pr["body"] = fx.body(first=f"Built on #3 at {PARENT_HEAD}.")
    fx.state["prs"]["3"] = {"state": "MERGED", "headRefOid": PARENT_HEAD}
    result = fx.run(REPO, "7", "--spec", str(fx.spec), "--task", "demo", "--dry-run")
    assert result.returncode == 0, result.stdout
    assert verdicts(result.stdout)["current"] == "pass current"
    assert ["pr", "view", "3", "--repo", REPO, "--json", "state,headRefOid"] in fx.calls()


def test_pending_checks_wait_with_no_row(fx):
    fx.state["checks"] = {"exit": 8, "stdout": "gate\tpending\t0\thttps://x\n"}
    result = fx.run()
    assert result.returncode == 3
    assert_only(result, "ci", "wait")
    assert fx.rows() == []
    assert not [call for call in fx.calls() if call[:2] in (["pr", "merge"], ["pr", "comment"])]


def test_no_session_entry_waits_with_no_row(fx):
    fx.state["agents"] = [{"name": "other", "state": "done", "startedAt": 1}]
    result = fx.run()
    assert result.returncode == 3
    assert_only(result, "session", "wait")
    assert fx.rows() == []


def test_a_failed_read_retries_once_then_asks(fx):
    fx.state["fail"] = ["pr checks"]
    first = fx.run()
    assert first.returncode == 2, first.stdout
    assert "read failed" in verdicts(first.stdout)["ci"]
    assert [row["result"] for row in fx.rows()] == ["retry"]
    assert not [call for call in fx.calls() if call[:2] == ["pr", "merge"]]
    second = fx.run()
    assert second.returncode == 1, second.stdout
    assert [row["result"] for row in fx.rows()] == ["retry", "ask"]
    comments = [call for call in fx.calls() if call[:2] == ["pr", "comment"]]
    assert len(comments) == 1 and "fail ci: read failed" in comments[0][-1]


def test_a_failed_claude_read_exits_2(fx):
    fx.state["agents_fail"] = True
    result = fx.run()
    assert result.returncode == 2
    assert "read failed" in verdicts(result.stdout)["session"]


def test_a_head_that_moves_before_the_merge_exits_2(fx):
    fx.state["merge_head"] = "e" * 40
    result = fx.run()
    assert result.returncode == 2, result.stdout
    assert ["pr", "merge", "7", "--repo", REPO, "--merge", "--match-head-commit", HEAD] in fx.calls()
    assert "Head branch was modified" in result.stdout
    assert [row["result"] for row in fx.rows()] == ["retry"]


def test_a_failed_check_outranks_a_failed_read(fx):
    fx.pr["isDraft"] = True
    fx.state["fail"] = ["pr checks"]
    result = fx.run()
    assert result.returncode == 1, result.stdout
    assert verdicts(result.stdout)["pull-request"].startswith("fail pull-request: ")
    assert "read failed" in verdicts(result.stdout)["ci"]
    rows = fx.rows()
    assert [row["result"] for row in rows] == ["ask"]
    assert {item["check"] for item in rows[0]["failed"]} == {"pull-request", "ci"}


def test_report_names_an_ask_and_its_reason(fx):
    fx.pr["isDraft"] = True
    assert fx.run().returncode == 1
    lines = fx.run("--report").stdout.splitlines()
    assert len(lines) == 1 and lines[0].startswith("Ask: ") and "draft" in lines[0]


def test_a_usage_error_exits_64(fx):
    result = fx.run(REPO, "7")
    assert result.returncode == 64
    assert fx.calls() == []


@pytest.mark.skipif(sys.version_info < (3, 13), reason="PurePath.full_match needs Python 3.13")
def test_globs_match_across_folders():
    lines = ask_only("glw907/cairn-cms")
    assert "**/preview/[[]token[]]/**" in lines
