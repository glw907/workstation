"""Tests for the claude-git-guard PreToolUse hook, driven by subprocess."""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parent.parent / "bin/.local/bin/claude-git-guard"


def hook_env(task_session):
    """Return the hook's environment: CLAUDE_TASK_SESSION set to task_session, or unset when None."""
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    env.pop("CLAUDE_TASK_SESSION", None)
    if task_session is not None:
        env["CLAUDE_TASK_SESSION"] = task_session
    return env


def run_hook(command, task_session="1"):
    """Run the hook on a Bash command, in a task session unless told otherwise."""
    return subprocess.run(
        [sys.executable, str(SCRIPT)],
        input=json.dumps({"tool_input": {"command": command}}),
        capture_output=True,
        text=True,
        check=False,
        env=hook_env(task_session),
    )


@pytest.mark.parametrize(
    "command",
    [
        "gh pr merge 5",
        "gh pr merge 5 --merge",
        "gh pr merge 5 --merge --match-head-commit abc123",
        "gh pr merge -R owner/repo 5",
        "cd /x && gh pr merge 5",
        "git status; gh pr merge 5",
        "gh pr view 5 | gh pr merge 5",
        "# note\ngh pr merge 5",
        "timeout 60 gh pr merge 5",
        "command gh pr merge 5",
        "env FOO=1 gh pr merge 5",
        "nohup gh pr merge 5",
        "FOO=1 gh pr merge 5",
        "PREMERGE_DONE=5 gh pr merge 5",
        "echo $(gh pr merge 5)",
        "echo `gh pr merge 5`",
        "(gh pr merge 5)",
        "for n in 1 2; do gh pr merge $n --merge; done",
        "if true; then gh pr merge 5; fi",
        "while read n; do gh pr merge \"$n\"; done < prs",
        "{ gh pr merge 5; }",
        "! gh pr merge 5",
        "sudo gh pr merge 5",
        "echo 5 | xargs gh pr merge",
        "timeout -s KILL 60 gh pr merge 5",
        "2>/dev/null gh pr merge 5",
        "/usr/bin/gh pr merge 5",
        'out="$(gh pr merge 5 --merge 2>&1)"; echo "$out"',
        'echo "`gh pr merge 5`"',
    ],
)
def test_every_merge_stage_is_denied_in_a_task_session(command):
    result = run_hook(command)
    assert result.returncode == 0
    out = json.loads(result.stdout)["hookSpecificOutput"]
    assert out["hookEventName"] == "PreToolUse"
    assert out["permissionDecision"] == "deny"
    unset = run_hook(command, None)
    assert (unset.returncode, unset.stdout, unset.stderr) == (0, "", "")


@pytest.mark.parametrize("task_session", ["", "0", "true"])
def test_a_merge_gets_no_decision_under_another_value(task_session):
    for command in ("gh pr merge 5", "gh api -X PUT repos/o/r/pulls/5/merge", "echo $(gh pr merge 5)"):
        result = run_hook(command, task_session)
        assert (result.returncode, result.stdout, result.stderr) == (0, "", "")


def test_deny_message_names_the_task_session():
    reason = json.loads(run_hook("gh pr merge 5").stdout)["hookSpecificOutput"]["permissionDecisionReason"]
    assert "CLAUDE_TASK_SESSION=1" in reason
    assert "Only the session Geoff is talking to merges" in reason


@pytest.mark.parametrize(
    "command",
    [
        'other-tool land glw907/x#1 "Deny gh pr merge"',
        'git commit -m "Explain gh pr merge"',
        "echo 'gh pr merge 5'",
        "echo gh\\ pr\\ merge",
        "# gh pr merge 5",
        "git status\n# gh pr merge 5\ngit log",
        "gh pr view 5",
        "gh pr list",
        "git status",
        "python3 -I - <<'EOF'\nnote = 'gh pr merge 5 later'\ngh pr merge 7\nEOF\ngit status",
        "git commit -F - <<EOF\nRun gh pr merge 5\nEOF",
        'echo "$(git status) gh pr merge"',
        'echo "run `git log` then gh pr merge"',
        "sudo systemctl restart foo",
    ],
)
def test_allows_other_commands(command):
    result = run_hook(command)
    assert (result.returncode, result.stdout, result.stderr) == (0, "", "")


def test_malformed_input_exits_zero():
    for stdin in ("not json", json.dumps({}), json.dumps({"tool_input": {"command": 5}}), json.dumps([])):
        result = subprocess.run(
            [sys.executable, str(SCRIPT)], input=stdin, capture_output=True, text=True, check=False
        )
        assert (result.returncode, result.stdout, result.stderr) == (0, "", "")


# The Git checks. Every case passes a cwd, and the tests replace the
# exempt list through the hook's environment, since their repos sit under /tmp.
GIT_ID = ["-c", "user.name=Test", "-c", "user.email=test@example.invalid", "-c", "commit.gpgsign=false"]


def git(directory, *args):
    """Run Git in a test repo and fail the test on an error."""
    subprocess.run(["git", "-C", str(directory), *GIT_ID, *args], check=True,
                   capture_output=True, text=True)


def run_in(command, cwd, exempt="", task_session=None):
    """Run the hook on a command with a cwd and a replaced exempt list; return the reason or None."""
    env = hook_env(task_session)
    env.pop("CLAUDE_GIT_GUARD_EXEMPT", None)
    if exempt is not None:
        env["CLAUDE_GIT_GUARD_EXEMPT"] = exempt
    result = subprocess.run(
        [sys.executable, str(SCRIPT)],
        input=json.dumps({"tool_input": {"command": command}, "cwd": str(cwd)}),
        capture_output=True, text=True, check=False, env=env,
    )
    assert result.returncode == 0, result.stderr
    assert result.stderr == ""
    if not result.stdout:
        return None
    output = json.loads(result.stdout)["hookSpecificOutput"]
    assert output["permissionDecision"] == "deny"
    return output["permissionDecisionReason"]


def denied_in_task_session(command, cwd):
    """Return whether the hook denies a command with CLAUDE_TASK_SESSION set to 1."""
    return run_in(command, cwd, task_session="1") is not None


@pytest.fixture
def repos(tmp_path):
    """Build a primary checkout on main, a worktree of it, an empty repo, and a plain folder."""
    primary = tmp_path / "primary"
    primary.mkdir()
    git(primary, "init", "-q", "-b", "main")
    (primary / "docs").mkdir()
    (primary / "docs" / "a.md").write_text("a\n")
    git(primary, "add", "docs/a.md")
    git(primary, "commit", "-q", "-m", "first")
    worktree = tmp_path / "wt"
    git(primary, "worktree", "add", "-q", "-b", "feature", str(worktree))
    empty = tmp_path / "empty"
    empty.mkdir()
    git(empty, "init", "-q", "-b", "main")
    plain = tmp_path / "plain"
    plain.mkdir()
    return {"primary": primary, "worktree": worktree, "empty": empty, "plain": plain,
            "root": tmp_path}


@pytest.mark.parametrize("command", [
    "gh -R owner/repo pr merge 5",
    "gh --repo owner/repo pr merge 5 --squash",
    "gh --repo=owner/repo pr merge 5",
    "gh api -X PUT repos/owner/repo/pulls/5/merge",
    "gh api --method PUT /repos/owner/repo/pulls/5/merge -f merge_method=squash",
    "gh api repos/owner/repo/pulls/5/merge -X PUT",
    "gh api -XPUT repos/o/r/pulls/7/merge",
])
def test_other_merge_spellings_are_denied_in_a_task_session(command, tmp_path):
    assert denied_in_task_session(command, tmp_path)
    assert run_in(command, tmp_path) is None


def test_forced_push_beside_a_merge_is_denied(repos):
    assert run_in("gh pr merge 5 --merge; git push -f origin main", repos["primary"]) is not None


@pytest.mark.parametrize("command", [
    "gh api repos/owner/repo/pulls/5/merge",
    "gh api -X GET repos/owner/repo/pulls/5/merge",
    "gh api repos/owner/repo/pulls/5",
    "gh -R owner/repo pr view 5",
    "echo 'gh api -X PUT repos/o/r/pulls/5/merge'",
])
def test_merge_lookalikes_pass(command, tmp_path):
    assert run_in(command, tmp_path) is None


@pytest.mark.parametrize("command", [
    "git push --force",
    "git push -f",
    "git push --force origin",
    "git push --force-with-lease",
    "git push --force-if-includes origin HEAD",
    "git push -f origin @",
    "git push -fu origin",
    "git push origin +main",
    "git push origin +HEAD:main",
    "git push --force origin main",
    "git push --force-with-lease origin main",
    "git push --force-with-lease=main:abc123 origin main",
    "git push -f origin master",
    "git push -f origin feature:refs/heads/main",
    "git push --all --force origin",
    "git push --mirror --force origin",
    "git status && git push -f",
])
def test_forced_push_to_main_refused(command, repos):
    assert "forced push" in run_in(command, repos["primary"])


def test_forced_push_through_dash_c_refused(repos):
    command = f"git -C {repos['primary']} push --force"
    assert "forced push" in run_in(command, repos["plain"])


def test_forced_push_through_cd_refused(repos):
    command = f"cd {repos['primary']} && git push -f origin"
    assert "forced push" in run_in(command, repos["plain"])


@pytest.mark.parametrize("command", [
    "git push --force-with-lease origin feature",
    "git push -f origin feature",
    "git push origin +feature",
    "git push --force",
    "git push -fu origin",
    "git push --force origin HEAD",
    "git push origin main",
    "git push",
    "git push -o ci.skip origin main",
])
def test_forced_push_to_other_branch_passes(command, repos):
    assert run_in(command, repos["worktree"]) is None


@pytest.mark.parametrize("command", [
    "git push origin main",
    "git push -u origin main",
    "git push",
    "git push --dry-run origin main",
    'git commit -m "git push -f origin main"',
    "echo git push --force origin main",
])
def test_unforced_push_to_main_passes(command, repos):
    assert run_in(command, repos["primary"]) is None


def test_detached_head_forced_push_with_no_ref_passes(repos):
    git(repos["primary"], "checkout", "-q", "--detach")
    assert run_in("git push --force", repos["primary"]) is None
    assert "forced push" in run_in("git push --force origin main", repos["primary"])


@pytest.mark.parametrize("command", [
    "git add -A",
    "git add --all",
    "git add -u",
    "git add --update",
    "git add .",
    "git add -A .",
    "git add :/",
    "git add '*'",
    "git add -- .",
    "git commit -a -m wip",
    "git commit -am wip",
    "git commit --all -m wip",
    "git commit -qam wip",
    "git status; git add -A && git commit -m wip",
])
def test_whole_tree_staging_refused_in_primary(command, repos):
    assert "whole-tree staging" in run_in(command, repos["primary"])


def test_whole_tree_staging_through_cd_refused(repos):
    command = f"cd {repos['primary']} && git add -A"
    assert "whole-tree staging" in run_in(command, repos["plain"])


def test_whole_tree_staging_through_dash_c_refused(repos):
    command = f"git -C {repos['primary']} commit -a -m wip"
    assert "whole-tree staging" in run_in(command, repos["plain"])


def test_whole_tree_staging_from_a_subfolder_refused(repos):
    assert "whole-tree staging" in run_in("git add .", repos["primary"] / "docs")


@pytest.mark.parametrize("command", [
    "git add -A docs/",
    "git add docs/a.md",
    "git add -u docs",
    "git add -p",
    "git commit -m 'add -A everything'",
    "git commit -m wip docs/a.md",
    "git commit --amend --no-edit",
    "git commit -ma",
    "echo git add -A",
])
def test_named_staging_passes_in_primary(command, repos):
    assert run_in(command, repos["primary"]) is None


@pytest.mark.parametrize("command", [
    "git add -A",
    "git add .",
    "git add -A .",
    "git commit -a -m wip",
])
def test_whole_tree_staging_passes_in_worktree(command, repos):
    assert run_in(command, repos["worktree"]) is None


def test_whole_tree_staging_passes_in_worktree_through_cd_and_dash_c(repos):
    assert run_in(f"cd {repos['worktree']} && git add -A", repos["primary"]) is None
    assert run_in(f"git -C {repos['worktree']} commit -a -m wip", repos["primary"]) is None


def test_whole_tree_staging_passes_with_no_commit(repos):
    assert run_in("git add -A", repos["empty"]) is None


def test_whole_tree_staging_passes_under_exempt_folder(repos):
    assert run_in("git add -A", repos["primary"], exempt=str(repos["root"])) is None


def test_default_exempt_list_covers_tmp(repos):
    if not repos["root"].resolve().is_relative_to("/tmp"):
        pytest.skip("pytest's temporary folder is outside /tmp")
    assert run_in("git add -A", repos["primary"], exempt=None) is None


@pytest.mark.parametrize("name", ["plain", "missing"])
def test_git_failure_allows(name, repos):
    folder = repos["root"] / name
    assert run_in("git add -A", folder) is None
    assert run_in("git push --force", folder) is None
    assert run_in("git commit -a -m wip", folder) is None


@pytest.mark.parametrize("command", [
    'git -C "$REPO" add -A',
    "git -C $REPO add -A",
    'cd "$REPO" && git add -A',
    "cd ~/Projects/* && git add -A",
    "git --git-dir=$GIT add -A",
])
def test_unreadable_directory_allows(command, repos):
    assert run_in(command, repos["plain"]) is None


def test_no_git_or_gh_word_exits_before_parsing(repos):
    # An unbalanced quote would make the parser fall back; the prefilter means it never runs.
    assert run_in("echo 'legit ghost digit", repos["primary"]) is None
    assert run_in("make push -f", repos["primary"]) is None


# An unquoted variable or substitution names a path or ref the text can't show, so it passes.
@pytest.mark.parametrize("command", [
    "git add -A $DIR",
    "git add -u $(git diff --name-only -- docs)",
    "git add -A ${DIR}",
])
def test_unquoted_expansion_operand_passes(command, repos):
    assert run_in(command, repos["primary"]) is None


# A forced push to a ref the text can't show falls back to the current branch.
@pytest.mark.parametrize("command", [
    "git push -f origin $BRANCH",
    "git push -f origin $(git branch --show-current)",
    'git push --force-with-lease origin "$(git branch --show-current)"',
    "git push -f origin `git branch --show-current`",
])
def test_forced_push_to_unreadable_ref(command, repos):
    assert run_in(command, repos["primary"]) is not None
    assert run_in(command, repos["worktree"]) is None


def test_crash_allows(repos):
    assert run_in("git -C ~\udcff add -A", repos["primary"]) is None


@pytest.mark.parametrize("command", [
    "git add -A; echo $DIR",
    "echo $DIR && git add -A",
    "git push -f origin main $EXTRA",
])
def test_expansion_elsewhere_still_refused(command, repos):
    assert run_in(command, repos["primary"]) is not None


def test_merge_inside_substitution_is_denied_in_a_task_session(tmp_path):
    assert denied_in_task_session('echo "$(gh pr merge 7)"', tmp_path)
    assert denied_in_task_session("x=$(gh pr merge 7)", tmp_path)


def test_absolute_directory_read_without_cwd(repos):
    env = hook_env(None)
    env["CLAUDE_GIT_GUARD_EXEMPT"] = ""
    for command in (f"git -C {repos['primary']} add -A", f"cd {repos['primary']} && git add -A"):
        result = subprocess.run(
            [sys.executable, str(SCRIPT)],
            input=json.dumps({"tool_input": {"command": command}, "cwd": ""}),
            capture_output=True, text=True, check=False, env=env,
        )
        assert result.returncode == 0, result.stderr
        assert json.loads(result.stdout)["hookSpecificOutput"]["permissionDecision"] == "deny"
