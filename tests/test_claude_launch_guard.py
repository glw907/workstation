"""Tests for the claude-launch-guard PreToolUse hook, driven by subprocess."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parent.parent / "bin/.local/bin/claude-launch-guard"
COMPLETE = (
    "## Pre-flight\n\nPermissions checked: none needed.\nReviewed: plan-reviewer.\n"
    "Evidence: the mechanism table.\n\n## Tasks\n"
)
MISSING_REVIEW = "## Pre-flight\n\nPermissions checked: none needed.\n\n## Tasks\n"
NO_EVIDENCE = "## Pre-flight\n\nPermissions checked: none needed.\nReviewed: plan-reviewer.\n\n## Tasks\n"
LINES_OUTSIDE = "## Pre-flight\n\n- item\n\n## Tasks\n\nPermissions checked: x\nReviewed: x\nEvidence: x\n"
EVIDENCE_OUTSIDE = (
    "## Pre-flight\n\nPermissions checked: x\nReviewed: x\n\n## Tasks\n\nEvidence: x\n"
)


def run(command: str, cwd: Path, transcript: Path | None = None) -> str:
    """Return the hook's stdout for a Bash command run from cwd."""
    payload = json.dumps({"tool_input": {"command": command}, "cwd": str(cwd),
                          "transcript_path": str(transcript) if transcript else None})
    return subprocess.run([sys.executable, str(SCRIPT)], input=payload, text=True,
                          capture_output=True, check=True).stdout


@pytest.fixture
def repo(tmp_path):
    """Build a repo with one plan and a prompt file naming it."""
    plans = tmp_path / "docs/plans"
    plans.mkdir(parents=True)
    (plans / "a-prompt.txt").write_text("Execute docs/plans/a.md now.\n")
    return tmp_path


LAUNCH = 'claude --bg --model sonnet --name x "$(cat docs/plans/a-prompt.txt)"'


@pytest.mark.parametrize("plan,denied", [
    (COMPLETE, False), (MISSING_REVIEW, True), (LINES_OUTSIDE, True), ("no sections\n", True),
])
def test_plan_checks(repo, plan, denied):
    (repo / "docs/plans/a.md").write_text(plan)
    assert ("deny" in run(LAUNCH, repo)) is denied


def test_sibling_plan_found_when_prompt_names_none(repo):
    (repo / "docs/plans/a-prompt.txt").write_text("Go.\n")
    (repo / "docs/plans/a.md").write_text(MISSING_REVIEW)
    assert "deny" in run(LAUNCH, repo)


def test_cd_prefix_resolves_the_prompt(repo):
    (repo / "docs/plans/a.md").write_text(MISSING_REVIEW)
    assert "deny" in run(f"cd {repo} && {LAUNCH}", Path("/"))


@pytest.mark.parametrize("command", ["git status", 'claude --bg "just look around"', "claude -p hi"])
def test_other_commands_pass(repo, command):
    assert run(command, repo) == ""


@pytest.mark.parametrize("text,denied", [("skills: standards:plan-reviewer", False), ("no such skill", True)])
def test_session_must_have_the_standards_plugin(repo, tmp_path, text, denied):
    (repo / "docs/plans/a.md").write_text(COMPLETE)
    transcript = tmp_path / "t.jsonl"
    transcript.write_text(text)
    assert ("deny" in run(LAUNCH, repo, transcript)) is denied


@pytest.mark.parametrize("command", [
    "grep -n 'claude --bg' docs/plans/a.md",
    "sed -n '/claude --bg/p' docs/plans/a.md",
    'echo "claude --bg docs/plans/a.md"',
    'git add docs/plans/a.md && git commit -m "Refuse claude --bg launches"',
    "cat > n.md <<'EOF'\n" + LAUNCH + "\nEOF",
])
def test_a_mention_is_not_a_launch(repo, command):
    (repo / "docs/plans/a.md").write_text(MISSING_REVIEW)
    assert run(command, repo) == ""


@pytest.mark.parametrize("command", [
    LAUNCH, f"FOO=1 {LAUNCH}", f"(cd . && {LAUNCH})", 'claude --bg \\\n  "$(cat docs/plans/a-prompt.txt)"',
    f"git status; {LAUNCH}", 'claude --name "a&b" --bg "$(cat docs/plans/a-prompt.txt)"',
])
def test_launch_shapes_are_found(repo, command):
    (repo / "docs/plans/a.md").write_text(MISSING_REVIEW)
    assert "deny" in run(command, repo)


def test_plan_beside_a_prompt_outside_the_launch_folder(repo, tmp_path_factory):
    (repo / "docs/plans/a.md").write_text(MISSING_REVIEW)
    away = tmp_path_factory.mktemp("main")
    assert "deny" in run(f'claude --bg "$(cat {repo}/docs/plans/a-prompt.txt)"', away)


@pytest.mark.parametrize("payload", [
    {"tool_input": {"command": f"cd ~nosuchuser123 && {LAUNCH}"}},
    {"tool_input": {"command": LAUNCH}, "transcript_path": 7},
    {"tool_input": {"command": 7}},
    {"tool_input": {"command": "echo 'unclosed"}},
])
def test_bad_input_exits_silently(repo, payload):
    (repo / "docs/plans/a.md").write_text(COMPLETE)
    done = subprocess.run([sys.executable, str(SCRIPT)], input=json.dumps({**payload, "cwd": str(repo)}),
                          text=True, capture_output=True)
    assert (done.returncode, done.stdout, done.stderr) == (0, "", "")


@pytest.mark.parametrize("wrap", [
    'claude --bg "no plan"; {}', "if true; then {}; fi", "for x in 1; do {}; done", "{{ {}; }}", "! {}",
    "env {}", "nohup {}", "command {}", "timeout 5 {}", "echo hi # it's a note\n{}", "cd . # go\n{}",
    "curl -s http://x/y#z && {}",
])
def test_wrapped_launches_are_found(repo, wrap):
    (repo / "docs/plans/a.md").write_text(MISSING_REVIEW)
    assert "deny" in run(wrap.format(LAUNCH), repo)


@pytest.mark.parametrize("command", [
    'claude --bg 2>&1 "$(cat docs/plans/a-prompt.txt)"', 'claude 2>&1 --bg "$(cat docs/plans/a-prompt.txt)"',
    'claude --bg "" "$(cat docs/plans/a-prompt.txt)"', "claude --bg $(cat docs/plans/a-prompt.txt)",
    'claude --bg "$(< docs/plans/a-prompt.txt)"',
    'claude --bg "Execute the plan.\n\nPlan: docs/plans/a.md"',
])
def test_prompt_forms_are_found(repo, command):
    (repo / "docs/plans/a.md").write_text(MISSING_REVIEW)
    assert "deny" in run(command, repo)


@pytest.mark.parametrize("command", [
    'echo ";" claude --bg docs/plans/a.md', 'echo "" claude --bg docs/plans/a.md',
    "printf '%s\\n' '&&' claude --bg docs/plans/a.md", 'find . -exec echo {} ";" claude --bg docs/plans/a.md',
    "echo x \; claude --bg docs/plans/a.md", "# claude --bg docs/plans/a.md",
])
def test_quoted_operators_are_not_launches(repo, command):
    (repo / "docs/plans/a.md").write_text(MISSING_REVIEW)
    assert run(command, repo) == ""


@pytest.mark.parametrize("prompt_name,body", [
    ("a-planning-prompt.txt", "Plan from docs/plans/a.md.\n"), ("a-planner-prompt.txt", "Plan from docs/plans/a.md.\n"),
    ("b-prompt.txt", "Read docs/plans/a-design.md.\n"),
])
def test_planner_and_design_prompts_pass(repo, prompt_name, body):
    (repo / "docs/plans/a.md").write_text(MISSING_REVIEW)
    (repo / "docs/plans/a-design.md").write_text("no pre-flight\n")
    (repo / "docs/plans" / prompt_name).write_text(body)
    assert run(f'claude --bg "$(cat docs/plans/{prompt_name})"', repo) == ""


@pytest.mark.parametrize("prompt_name,sibling", [("x-design-prompt.txt", "x-design.md"), ("y-prompt.txt", "y.md")])
def test_design_prompt_ignores_a_sibling(repo, prompt_name, sibling):
    (repo / "docs/plans" / sibling).write_text(MISSING_REVIEW)
    (repo / "docs/plans" / prompt_name).write_text(f"Read docs/plans/{prompt_name[0]}-design.md.\n")
    assert run(f'claude --bg "$(cat docs/plans/{prompt_name})"', repo) == ""


@pytest.fixture
def record(tmp_path):
    """Build a plans folder with no `docs` parent, as an initiative record keeps its plans."""
    (tmp_path / "plans").mkdir()
    return tmp_path


def launch_of(name: str) -> str:
    """Return a launch that reads `plans/<name>` as its prompt."""
    return f'claude --bg --name x "$(cat plans/{name})"'


def test_record_plan_beside_its_prompt_is_read(record):
    (record / "plans/x-prompt.txt").write_text("Go.\n")
    (record / "plans/x-plan.md").write_text("## Tasks\n")
    out = run(launch_of("x-prompt.txt"), record)
    assert "x-plan.md" in out
    assert all(line in out for line in ("Permissions checked:", "Reviewed:", "Evidence:"))


def test_complete_record_plan_passes(record):
    (record / "plans/x-prompt.txt").write_text("Go.\n")
    (record / "plans/x-plan.md").write_text(COMPLETE)
    assert run(launch_of("x-prompt.txt"), record) == ""


def test_plan_without_evidence_is_denied_by_name(repo):
    (repo / "docs/plans/a.md").write_text(NO_EVIDENCE)
    out = run(LAUNCH, repo)
    assert "an `Evidence:` line" in out
    assert "a `Permissions checked:` line" not in out
    assert "a `Reviewed:` line" not in out


def test_other_gaps_do_not_name_evidence(repo):
    (repo / "docs/plans/a.md").write_text(
        "## Pre-flight\n\nPermissions checked: x\nEvidence: x\n\n## Tasks\n")
    out = run(LAUNCH, repo)
    assert "a `Reviewed:` line" in out
    assert "an `Evidence:` line" not in out


def test_evidence_outside_pre_flight_is_denied(repo):
    (repo / "docs/plans/a.md").write_text(EVIDENCE_OUTSIDE)
    assert "an `Evidence:` line" in run(LAUNCH, repo)


@pytest.mark.parametrize("first,second,denied", [(COMPLETE, "## Tasks\n", False), ("## Tasks\n", COMPLETE, True)])
def test_the_older_sibling_wins(record, first, second, denied):
    (record / "plans/x-prompt.txt").write_text("Go.\n")
    (record / "plans/x.md").write_text(first)
    (record / "plans/x-plan.md").write_text(second)
    out = run(launch_of("x-prompt.txt"), record)
    assert bool(out) is denied
    if denied:
        assert "x.md" in out and "x-plan.md" not in out


def test_a_named_plan_wins_over_a_plan_sibling(repo):
    (repo / "docs/plans/a.md").write_text(COMPLETE)
    (repo / "docs/plans/a-plan.md").write_text("## Tasks\n")
    assert run(LAUNCH, repo) == ""


def test_a_rulings_file_is_not_read_as_the_plan(record):
    (record / "rec/plans").mkdir(parents=True)
    (record / "rec/plans/rulings.md").write_text("Answers only.\n")
    (record / "plans/x-prompt.txt").write_text("Read rec/plans/rulings.md first.\n")
    (record / "plans/x-plan.md").write_text(COMPLETE)
    assert run(launch_of("x-prompt.txt"), record) == ""


@pytest.mark.parametrize("name", ["x-planning-prompt.txt", "x-planner-prompt.txt"])
def test_planner_prompts_read_no_sibling(record, name):
    (record / "plans" / name).write_text("Plan it.\n")
    for sibling in ("x-plan.md", "x-planning-plan.md", "x-planner-plan.md"):
        (record / "plans" / sibling).write_text("## Tasks\n")
    assert run(launch_of(name), record) == ""


def test_a_launch_that_names_no_plan_passes(record):
    (record / "plans/y-prompt.txt").write_text("Tidy the notes.\n")
    assert run(launch_of("y-prompt.txt"), record) == ""
    assert run('claude --bg --name x "Tidy the notes."', record) == ""
