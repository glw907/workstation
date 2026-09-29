"""Fixtures for scripts/check-claude-refs.py: the self-mode dead-reference and retired-phrase
checks (rows F1 to F8).

Every row runs the real claude/.claude/tooling/ratchet.py "check" mode, the way check.sh does,
with scripts/check-claude-refs.py registered as the tool for both check ids, over a fixture
tree holding only the files each row needs.
"""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
RATCHET = REPO / "claude" / ".claude" / "tooling" / "ratchet.py"
REFS = REPO / "scripts" / "check-claude-refs.py"
BASELINE = "claude/.claude/tooling/ratchet-baseline.json"
PY = shutil.which("python3") or sys.executable

CHECKS = {"dead-reference": {"tool": "scripts/check-claude-refs.py"},
          "retired-phrase": {"tool": "scripts/check-claude-refs.py"}}


def entry(check, file, fingerprint, finding="GA-01", label="C", defect="an example defect"):
    """Build one baseline entry for the given check, file, and fingerprint."""
    return {"check": check, "file": file, "fingerprint": fingerprint,
            "finding": finding, "pass": label, "defect": defect}


class Fixture:
    """A fixture tree carrying its own copy of ratchet.py and check-claude-refs.py."""

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
        tooling = self.root / "claude" / ".claude" / "tooling"
        tooling.mkdir(parents=True)
        shutil.copy(RATCHET, tooling / "ratchet.py")
        scripts = self.root / "scripts"
        scripts.mkdir()
        shutil.copy(REFS, scripts / "check-claude-refs.py")
        (scripts / "check-claude-refs.py").chmod(0o755)

    def write(self, rel, text):
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)

    def write_bin(self, name):
        path = self.root / "bin" / ".local" / "bin" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("#!/bin/sh\nexit 0\n")
        path.chmod(0o755)

    def phrases(self, text):
        self.write("claude/.claude/tooling/retired-phrases.txt", text)

    def baseline(self, entries):
        self.write(BASELINE, json.dumps({"checks": CHECKS, "entries": entries}, indent=2))

    def check(self):
        """Run ratchet.py check --root <fixture root> --home <fixture home>."""
        env = {k: v for k, v in os.environ.items()}
        return subprocess.run(
            [PY, str(RATCHET), "check", "--root", str(self.root), "--home", str(self.home)],
            capture_output=True, text=True, env=env)


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
    fx.baseline([])
    proc = fx.check()
    assert proc.returncode == 1
    assert "new violation" in out(proc)
    assert "~/.claude/docs/gone.md" in out(proc)


def test_f2_local_bin_cited_present_in_the_fixtures_bin_passes(fx):
    fx.write("claude/.claude/docs/a.md", "Run `~/.local/bin/example-tool` to apply it.\n")
    fx.write_bin("example-tool")
    fx.baseline([])
    proc = fx.check()
    assert proc.returncode == 0, out(proc)


# ---- F3, F4: retired phrases ----


def test_f3_retired_phrase_in_an_authored_file_fails(fx):
    fx.phrases("sleep 30\n")
    fx.write("claude/.claude/docs/a.md", "Poll it with `sleep 30` between checks.\n")
    fx.baseline([])
    proc = fx.check()
    assert proc.returncode == 1
    assert "new violation" in out(proc)
    assert "claude/.claude/docs/a.md" in out(proc)
    assert "sleep 30" in out(proc)


def test_f4_retired_phrase_on_a_retired_ok_line_passes(fx):
    fx.phrases("sleep 30\n")
    fx.write("claude/.claude/docs/a.md",
             "Poll it with `sleep 30` between checks. <!-- retired-ok: quoting the old form -->\n")
    fx.baseline([])
    proc = fx.check()
    assert proc.returncode == 0, out(proc)


# ---- F5, F6: phrase list configuration errors ----


def test_f5_phrase_list_absent_is_a_config_error(fx):
    (fx.root / "claude" / ".claude" / "tooling" / "retired-phrases.txt").unlink()
    fx.write("claude/.claude/docs/a.md", "nothing to see\n")
    fx.baseline([])
    proc = fx.check()
    assert proc.returncode == 2
    assert "configuration error" in out(proc)
    assert "retired-phrase list absent" in out(proc)


def test_f6_phrase_list_with_only_comments_is_vacuous(fx):
    fx.phrases("# nothing retired yet\n# still nothing\n")
    fx.write("claude/.claude/docs/a.md", "nothing to see\n")
    fx.baseline([])
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
    fx.baseline([])
    proc = fx.check()
    assert proc.returncode == 1
    text = out(proc)
    assert "sleep 30" in text
    assert "gone.md" not in text


def test_f8_retired_phrase_under_skills_synced_and_dead_path_under_docs_record_both_pass(fx):
    fx.phrases("sleep 30\n")
    fx.write("claude/.claude/skills/synced/example/SKILL.md",
             "---\nname: example\n---\n\nPoll it with `sleep 30` between checks.\n")
    fx.write("claude/.claude/docs/record/2026-01-01-old-note.md",
             "See `~/.claude/docs/gone.md` for the old plan.\n")
    fx.baseline([])
    proc = fx.check()
    assert proc.returncode == 0, out(proc)


# ---- Matching a seeded baseline (exercises the growth rules against real findings) ----


def test_seeded_entries_matching_current_violations_pass(fx):
    fx.write("claude/.claude/CLAUDE.md", "Watch `~/.local/bin/missing-tool` here.\n")
    fx.phrases("sleep 30\n")
    fx.baseline([entry("dead-reference", "claude/.claude/CLAUDE.md", "~/.local/bin/missing-tool")])
    proc = fx.check()
    assert proc.returncode == 0, out(proc)


def test_a_stale_baseline_entry_asks_for_its_removal(fx):
    fx.write("claude/.claude/docs/a.md", "nothing dead here\n")
    fx.baseline([entry("dead-reference", "claude/.claude/docs/gone.md", "~/.claude/docs/x.md")])
    proc = fx.check()
    assert proc.returncode == 1
    assert "remove this baseline entry" in out(proc)
