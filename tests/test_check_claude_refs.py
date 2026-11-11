"""Fixtures for scripts/check-claude-refs.py: the self-mode dead-reference, relative-link, and
retired-phrase checks (rows F1 to F8).

Every row runs the real script's "check" command, the way check.sh does, over a fixture tree
holding only the files each row needs.
"""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
REFS = REPO / "scripts" / "check-claude-refs.py"
PY = shutil.which("python3") or sys.executable

# Runs a script under an audit hook that records every path it opens, lists, or hands to a
# subprocess, minus the interpreter's own install tree. Proves self mode reads nothing
# outside the fixture root.
AUDIT_WRAPPER = r"""
import atexit, json, os, runpy, sys, sysconfig
log = os.environ["CHECK_AUDIT_LOG"]
own = {os.path.realpath(sysconfig.get_paths()[k])
       for k in ("stdlib", "platstdlib", "purelib", "platlib")}
# A layered environment (uv run --with) puts more site-packages on sys.path than sysconfig
# names, and the import system lists them; those reads are the interpreter's, not the tool's.
own |= {os.path.realpath(p) for p in sys.path if os.path.basename(p) == "site-packages"}
seen = []
def note(p):
    if isinstance(p, int) or p is None:
        return
    p = os.path.realpath(os.path.abspath(os.fsdecode(p)))
    if p.startswith("/dev/") or any(p == o or p.startswith(o + os.sep) for o in own):
        return
    seen.append(p)
def hook(event, args):
    if event == "open" or event in ("os.listdir", "os.scandir"):
        if args:
            note(args[0])
    elif event == "subprocess.Popen":
        note(args[2])
        for a in ([] if isinstance(args[1], (str, bytes)) else list(args[1])[1:]):
            if isinstance(a, (str, bytes)) and os.fsdecode(a).startswith("/"):
                note(a)
target = sys.argv[1]
sys.argv = sys.argv[1:]
atexit.register(lambda: open(log, "w").write(json.dumps(seen)))
sys.addaudithook(hook)
runpy.run_path(target, run_name="__main__")
"""


def outside_reads(log, allowed):
    """Return every audited path not under one of the allowed roots."""
    allowed = [os.path.realpath(a) for a in allowed]
    paths = json.loads(Path(log).read_text())
    return sorted({p for p in paths
                   if not any(p == a or p.startswith(a + os.sep) for a in allowed)})


class Fixture:
    """A fixture tree carrying its own copy of check-claude-refs.py."""

    def __init__(self, tmp):
        self.tmp = tmp
        self.root = tmp / "repo"
        self.home = tmp / "home"
        self.root.mkdir()
        self.home.mkdir()
        env = {**os.environ, "HOME": str(self.home), "GIT_CONFIG_NOSYSTEM": "1"}
        subprocess.run(["git", "init", "-q", "-b", "main"], cwd=self.root, env=env, check=True)
        subprocess.run(["git", "config", "user.email", "fixture@example.invalid"],
                       cwd=self.root, env=env, check=True)
        subprocess.run(["git", "config", "user.name", "Fixture"], cwd=self.root, env=env,
                       check=True)
        scripts = self.root / "scripts"
        scripts.mkdir()
        shutil.copy(REFS, scripts / "check-claude-refs.py")
        (scripts / "check-claude-refs.py").chmod(0o755)

    def write(self, rel, text):
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)

    def write_in_home(self, rel, text):
        path = self.home / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)

    def write_bin(self, name):
        path = self.root / "bin" / ".local" / "bin" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("#!/bin/sh\nexit 0\n")
        path.chmod(0o755)

    def phrases(self, text):
        self.write("claude/.claude/tooling/retired-phrases.txt", text)

    def check(self):
        """Run check-claude-refs.py check --root <fixture root> --home <fixture home>."""
        return subprocess.run(
            [PY, str(REFS), "check", "--root", str(self.root), "--home", str(self.home)],
            capture_output=True, text=True, env=dict(os.environ))

    def audited_check(self):
        """Run the fixture's own check-claude-refs.py under the audit wrapper.

        Asserts every path the run opens, lists, or hands to a subprocess sits under the
        fixture root.
        """
        log = self.tmp / "audit.json"
        module = self.root / "scripts" / "check-claude-refs.py"
        env = {**os.environ, "HOME": str(self.home), "GIT_CONFIG_NOSYSTEM": "1",
               "CHECK_AUDIT_LOG": str(log)}
        proc = subprocess.run(
            [PY, "-c", AUDIT_WRAPPER, str(module), "check",
             "--root", str(self.root), "--home", str(self.home)],
            capture_output=True, text=True, env=env)
        stray = outside_reads(log, [self.tmp])
        assert not stray, f"read outside the fixture root: {stray}"
        return proc


@pytest.fixture
def fx(tmp_path):
    fixture = Fixture(tmp_path)
    fixture.phrases("placeholder phrase\n")
    return fixture


def out(proc):
    return proc.stdout + proc.stderr


# ---- F1, F2: dead-reference self-mode rewriting ----


def test_f1_doc_deleted_only_in_the_fixture_tree_is_a_dead_path(fx):
    fx.write("claude/.claude/docs/a.md", "See `~/.claude/docs/gone.md` for detail.\n")
    # The real workstation's ~/.claude is a stow symlink into ~/.dotfiles main, so a naive
    # --home resolution finds a deleted-only-in-the-worktree doc anyway (Review focus 3). Seed
    # both shapes a home-based resolution could hit, so this row only passes when resolution
    # goes through root's self-mode rewrite, never through home.
    fx.write_in_home(".claude/docs/gone.md", "still present via a literal ~/.claude/... home\n")
    fx.write_in_home(".dotfiles/claude/.claude/docs/gone.md",
                     "still present via the dotfiles checkout under home\n")
    proc = fx.check()
    assert proc.returncode == 1
    assert "~/.claude/docs/gone.md" in out(proc)


def test_a_dotfiles_span_resolves_against_the_tree_not_the_home_checkout(fx):
    # A branch that moves a doc cites its new path while the home checkout still holds the old.
    fx.write("claude/.claude/docs/a.md",
             "Spec: `~/.dotfiles/docs/specs/new.md`.\nOld: `~/.dotfiles/docs/old/gone.md`.\n")
    fx.write("docs/specs/new.md", "moved here\n")
    fx.write_in_home(".dotfiles/docs/old/gone.md", "still in the home checkout\n")
    proc = fx.check()
    assert proc.returncode == 1
    assert "~/.dotfiles/docs/old/gone.md" in out(proc)
    assert "~/.dotfiles/docs/specs/new.md" not in out(proc)


def test_a_host_only_span_on_a_host_ok_line_passes_and_its_twin_fails(fx):
    fx.write("claude/.claude/docs/a.md",
             "Laptop only: `/etc/nothing-here.d/` <!-- host-ok -->\n"
             "Everywhere: `~/nothing-here/`\n")
    proc = fx.check()
    assert proc.returncode == 1
    assert "~/nothing-here/" in out(proc)
    assert "/etc/nothing-here.d/" not in out(proc)


def test_f2_local_bin_cited_present_in_the_fixtures_bin_passes(fx):
    fx.write("claude/.claude/docs/a.md", "Run `~/.local/bin/example-tool` to apply it.\n")
    fx.write_bin("example-tool")
    proc = fx.check()
    assert proc.returncode == 0, out(proc)


def test_local_bin_stow_link_in_home_with_the_bin_deleted_from_the_tree_is_dead(fx):
    fx.write("claude/.claude/docs/a.md", "Run `~/.local/bin/foo` to apply it.\n")
    stowed = fx.tmp / "stow" / "bin" / ".local" / "bin" / "foo"
    stowed.parent.mkdir(parents=True)
    stowed.write_text("#!/bin/sh\n")
    link = fx.home / ".local" / "bin" / "foo"
    link.parent.mkdir(parents=True)
    link.symlink_to(stowed)
    proc = fx.check()
    assert proc.returncode == 1
    assert "~/.local/bin/foo" in out(proc)


def test_local_bin_folded_dangling_stow_link_is_dead(fx):
    fx.write("claude/.claude/docs/a.md", "Run `~/.local/bin/foo` to apply it.\n")
    stow_bin = fx.tmp / "stow" / "bin" / ".local" / "bin"
    stow_bin.mkdir(parents=True)
    (fx.home / ".local").mkdir()
    (fx.home / ".local" / "bin").symlink_to(stow_bin)
    proc = fx.check()
    assert proc.returncode == 1
    assert "~/.local/bin/foo" in out(proc)


def test_local_bin_regular_file_in_home_absent_from_the_tree_passes(fx):
    fx.write("claude/.claude/docs/a.md", "Run `~/.local/bin/foo` to apply it.\n")
    fx.write_in_home(".local/bin/foo", "#!/bin/sh\n")
    proc = fx.check()
    assert proc.returncode == 0, out(proc)


def test_local_bin_span_absent_from_tree_and_home_is_dead(fx):
    fx.write("claude/.claude/docs/a.md", "Run `~/.local/bin/foo` to apply it.\n")
    proc = fx.check()
    assert proc.returncode == 1
    assert "~/.local/bin/foo" in out(proc)


# ---- relative-link ----


def test_a_dead_relative_link_fails(fx):
    fx.write("claude/.claude/docs/a.md", "See [the note](gone.md) here.\n")
    proc = fx.check()
    assert proc.returncode == 1
    assert "relative-link" in out(proc)
    assert "gone.md" in out(proc)


def test_live_and_exempt_relative_links_are_not_reported(fx):
    fx.write("claude/.claude/docs/exists.md", "target\n")
    fx.write("claude/.claude/docs/a.md",
             "[live](exists.md) [anchored](exists.md#section) [web](http://example.invalid/x)\n"
             "[here](#anchor) [abs](/etc/nothing-here) [tilde](~/nothing-here)\n"
             "[dead](gone.md) <!-- link-ok -->\n")
    proc = fx.check()
    assert proc.returncode == 0, out(proc)


def test_a_vendored_skills_dead_relative_link_is_not_scanned(fx):
    fx.write("claude/.claude/tooling/vendored-skills.json",
             json.dumps({"skills": {"vendored-example": {
                 "repo": "example/repo", "path": "skills/x", "branch": "main",
                 "commit": "abc123def456", "license": "MIT"}}}))
    fx.write("claude/.claude/skills/vendored-example/SKILL.md",
             "---\nname: vendored-example\n---\n\nSee [x](gone.md).\n")
    proc = fx.check()
    assert proc.returncode == 0, out(proc)


# ---- F3, F4: retired phrases ----


def test_f3_retired_phrase_in_an_authored_file_fails(fx):
    fx.phrases("sleep 30\n")
    fx.write("claude/.claude/docs/a.md", "Poll it with `sleep 30` between checks.\n")
    proc = fx.check()
    assert proc.returncode == 1
    assert "claude/.claude/docs/a.md" in out(proc)
    assert "sleep 30" in out(proc)


def test_f4_retired_phrase_on_a_retired_ok_line_passes(fx):
    fx.phrases("sleep 30\n")
    fx.write("claude/.claude/docs/a.md",
             "Poll it with `sleep 30` between checks. <!-- retired-ok: quoting the old form -->\n")
    proc = fx.check()
    assert proc.returncode == 0, out(proc)


# ---- F5, F6: phrase list configuration errors ----


def test_f5_phrase_list_absent_is_a_config_error(fx):
    (fx.root / "claude" / ".claude" / "tooling" / "retired-phrases.txt").unlink()
    fx.write("claude/.claude/docs/a.md", "nothing to see\n")
    proc = fx.check()
    assert proc.returncode == 2
    assert "configuration error" in out(proc)
    assert "retired-phrase list absent" in out(proc)


def test_f6_phrase_list_with_only_comments_is_vacuous(fx):
    fx.phrases("# nothing retired yet\n# still nothing\n")
    fx.write("claude/.claude/docs/a.md", "nothing to see\n")
    proc = fx.check()
    assert proc.returncode == 2
    assert "configuration error" in out(proc)
    assert "vacuous" in out(proc)


# ---- F7, F8: vendored skills and excluded trees ----


def test_f7_vendored_skill_with_a_retired_phrase_and_a_dead_path_reports_the_phrase_only(fx):
    fx.phrases("sleep 30\n")
    fx.write("claude/.claude/tooling/vendored-skills.json",
             json.dumps({"skills": {"vendored-example": {
                 "repo": "example/repo", "path": "skills/x", "branch": "main",
                 "commit": "abc123def456", "license": "MIT"}}}))
    fx.write("claude/.claude/skills/vendored-example/SKILL.md",
             "---\nname: vendored-example\n---\n\n"
             "Poll it with `sleep 30`, and see `~/.claude/docs/gone.md`.\n")
    proc = fx.check()
    assert proc.returncode == 1
    text = out(proc)
    assert "sleep 30" in text
    assert "gone.md" not in text


def test_f8_retired_phrase_under_skills_synced_and_dead_path_under_docs_record_both_pass(fx):
    fx.phrases("sleep 30\n")
    fx.write("claude/.claude/skills/synced/example/SKILL.md",
             "---\nname: example\n---\n\nPoll it with `sleep 30` between checks.\n")
    # An undated name isolates the docs/record exclusion: a dated file would also be caught by
    # the separate "dated path component" exclusion, so this row would pass even if the
    # docs/record exclusion broke.
    fx.write("claude/.claude/docs/record/old-note.md",
             "See `~/.claude/docs/gone.md` for the old plan.\n")
    proc = fx.check()
    assert proc.returncode == 0, out(proc)


# ---- Self-mode reach: stowed dirs only, and no read outside the fixture root ----


def test_a_non_stowed_claude_projects_path_is_out_of_self_mode_reach(fx):
    fx.write("claude/.claude/docs/a.md",
             "See `~/.claude/projects/some-session.jsonl` for the transcript.\n")
    proc = fx.check()
    assert proc.returncode == 0, out(proc)


def test_audited_run_reads_nothing_outside_the_fixture_root(fx):
    fx.write("claude/.claude/docs/a.md", "nothing to see\n")
    proc = fx.audited_check()
    assert proc.returncode == 0, out(proc)


# ---- Acceptance: a planted dead ~/.dotfiles span fails the leg ----


def test_a_planted_dead_dotfiles_span_fails_the_leg_and_names_it(fx):
    fx.write("claude/.claude/docs/a.md", "Run it from `~/.dotfiles/nope`.\n")
    proc = fx.check()
    assert proc.returncode == 1
    assert "dead-reference: claude/.claude/docs/a.md: ~/.dotfiles/nope" in out(proc)
