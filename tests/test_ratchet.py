"""Fixtures for the ratchet baseline: the pre-commit hook and the check.sh gate.

Hook rows run the real scripts/githooks/pre-commit in a temporary repository, the way git
runs it at commit time. Gate rows run the real claude/.claude/tooling/ratchet.py the way check.sh does,
under an audit hook that fails the fixture on any read outside the fixture root.
"""
import json
import os
import re
import secrets
import shutil
import stat
import string
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
MODULE = REPO / "claude" / ".claude" / "tooling" / "ratchet.py"
HOOKS = REPO / "scripts" / "githooks"
BASELINE = "claude/.claude/tooling/ratchet-baseline.json"
TOOLING = "claude/.claude/tooling"
PY = shutil.which("python3") or sys.executable

# A stand-in for a check tool. It imports the shared module the way a real tool must:
# located through Path(__file__).resolve(), bytecode writing off before the import.
STUB_TOOL = """#!/usr/bin/env python3
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "claude" / ".claude" / "tooling"))
import ratchet  # noqa: E402

(HERE / "stub-tool.argv.json").write_text(json.dumps(sys.argv[1:]))
spec = json.loads((HERE / "stub-tool.json").read_text())
ratchet.emit_report(spec["implements"], spec["violations"])
"""

# Runs a script under an audit hook that records every path the process opens, lists, or
# hands to a subprocess, minus the interpreter's own install tree.
AUDIT_WRAPPER = r"""
import atexit, json, os, runpy, sys, sysconfig
log = os.environ["RATCHET_AUDIT_LOG"]
own = {os.path.realpath(sysconfig.get_paths()[k])
       for k in ("stdlib", "platstdlib", "purelib", "platlib")}
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


def entry(check, file, fingerprint, finding="DC-04", label="B", **extra):
    return {"check": check, "file": file, "fingerprint": fingerprint,
            "finding": finding, "pass": label, **extra}


def pair(check, a, b, count, finding="DC-21", label="E"):
    return {"check": check, "files": sorted([a, b]), "count": count,
            "finding": finding, "pass": label}


def outside_reads(log, allowed):
    """Return every audited path not under one of the allowed roots."""
    allowed = [os.path.realpath(a) for a in allowed]
    paths = json.loads(Path(log).read_text())
    return sorted({p for p in paths
                   if not any(p == a or p.startswith(a + os.sep) for a in allowed)})


def assert_reads_inside(log, allowed):
    stray = outside_reads(log, allowed)
    assert not stray, f"read outside the fixture root: {stray}"


class Fixture:
    """A temporary repository with a fixture home, both under one root."""

    def __init__(self, tmp):
        self.tmp = tmp
        self.root = tmp / "repo"
        self.home = tmp / "home"
        self.root.mkdir()
        self.home.mkdir()
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.name", "Fixture")
        self.git("config", "user.email", "fixture@example.invalid")
        self.git("config", "commit.gpgsign", "false")
        tooling = self.root / TOOLING
        tooling.mkdir(parents=True)
        shutil.copy(MODULE, tooling / "ratchet.py")

    def env(self, **overrides):
        env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
        env.update(HOME=str(self.home), XDG_CONFIG_HOME=str(self.home / ".config"),
                   GIT_CONFIG_NOSYSTEM="1")
        env.update(overrides)
        return env

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.root, env=self.env(), check=True,
                              capture_output=True, text=True).stdout

    def write(self, rel, text):
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)

    def baseline(self, checks, entries):
        self.write(BASELINE, json.dumps({"checks": checks, "entries": entries}, indent=2))

    def stub_tool(self, implements, violations=()):
        self.write("tools/stub-tool.json",
                   json.dumps({"implements": implements, "violations": list(violations)}))
        path = self.root / "tools" / "stub-tool"
        path.write_text(STUB_TOOL)
        path.chmod(path.stat().st_mode | stat.S_IXUSR)

    def commit(self, msg="setup"):
        self.git("add", "-A")
        self.git("commit", "-q", "--allow-empty", "-m", msg)

    def hook_commit(self, *paths, **env):
        """Stage paths, then run the real pre-commit hook as git would, keeping its exit code.

        git commit reports any hook failure as 1, so the hook runs directly here;
        test_no_bytecode_lands_in_the_stow_packages covers the run through git commit.
        """
        self.git("add", *(paths or ["-A"]))
        return subprocess.run([str(HOOKS / "pre-commit")], cwd=self.root,
                              env=self.env(**env), capture_output=True, text=True)

    def ratchet(self, *args, module=MODULE, **env):
        """Run the module as check.sh does, failing on any read outside the fixture."""
        log = self.tmp / "audit.json"
        proc = subprocess.run(
            [PY, "-c", AUDIT_WRAPPER, str(module), *args], cwd=self.root,
            env=self.env(RATCHET_AUDIT_LOG=str(log), **env), capture_output=True, text=True)
        assert_reads_inside(log, [self.tmp, module])
        return proc


@pytest.fixture
def fx(tmp_path):
    return Fixture(tmp_path)


def out(proc):
    return proc.stdout + proc.stderr


ACTIVE = {"demo": {"tool": "tools/stub-tool"}}


def seed(fx, entries, checks=None):
    """Commit a baseline, the stub tool, and a doc as HEAD."""
    fx.baseline(checks or ACTIVE, entries)
    fx.stub_tool(sorted(k for k, v in (checks or ACTIVE).items()
                        if v.get("state", "active") == "active"))
    fx.write("docs/a.md", "a doc\n")
    fx.commit()


# ---- Hook rows (R1 to R8, R12) ----


def test_r1_new_entry_under_registered_id_fails(fx):
    seed(fx, [entry("demo", "docs/a.md", "sleep 30")])
    fx.baseline(ACTIVE, [entry("demo", "docs/a.md", "sleep 30"),
                         entry("demo", "docs/b.md", "sleep 30")])
    proc = fx.hook_commit()
    assert proc.returncode == 1
    assert "new entry under registered id: docs/b.md: sleep 30" in out(proc)
    assert "demo" in out(proc)


def test_r2_new_entry_under_emptied_registered_id_fails(fx):
    seed(fx, [])
    fx.baseline(ACTIVE, [entry("demo", "docs/a.md", "sleep 30")])
    proc = fx.hook_commit()
    assert proc.returncode == 1
    assert "new entry under registered id: docs/a.md: sleep 30" in out(proc)


def test_r3_new_id_registered_with_its_entries_passes(fx):
    seed(fx, [entry("demo", "docs/a.md", "sleep 30")])
    checks = {**ACTIVE, "fresh": {"tool": "tools/stub-tool"}}
    fx.baseline(checks, [entry("demo", "docs/a.md", "sleep 30"),
                         entry("fresh", "docs/a.md", "x"), entry("fresh", "docs/b.md", "y")])
    proc = fx.hook_commit()
    assert proc.returncode == 0, out(proc)


def test_r4_entry_under_retired_id_fails(fx):
    checks = {**ACTIVE, "old": {"state": "retired"}}
    seed(fx, [], checks)
    fx.baseline(checks, [entry("old", "docs/a.md", "x")])
    proc = fx.hook_commit()
    assert proc.returncode == 1
    assert "retired id admits no entries: docs/a.md: x" in out(proc)


def test_r5_registry_id_removed_fails(fx):
    checks = {**ACTIVE, "old": {"state": "retired"}}
    seed(fx, [], checks)
    fx.baseline(ACTIVE, [])
    proc = fx.hook_commit()
    assert proc.returncode == 1
    assert "registry is append-only: old was removed" in out(proc)


def test_r6_rekey_across_heavily_edited_move_passes(fx):
    fx.write("docs/old.md", "".join(f"line {i} of the original\n" for i in range(40))
             + "then sleep 30 and poll\n")
    seed(fx, [entry("demo", "docs/old.md", "sleep 30")])
    fx.git("mv", "docs/old.md", "docs/new.md")
    fx.write("docs/new.md", "A rewrite.\n\nNow sleep 30 sits elsewhere.\n")
    fx.baseline(ACTIVE, [entry("demo", "docs/new.md", "sleep 30")])
    proc = fx.hook_commit()
    assert proc.returncode == 0, out(proc)


def test_r6_rekey_with_a_changed_count_is_new_growth(fx):
    seed(fx, [entry("demo", "docs/old.md", "sleep 30")])
    fx.baseline(ACTIVE, [entry("demo", "docs/new.md", "sleep 30", count=2)])
    proc = fx.hook_commit()
    assert proc.returncode == 1
    assert "new entry under registered id: docs/new.md: sleep 30" in out(proc)


def test_r7_overlap_count_rises_fails(fx):
    seed(fx, [pair("demo", "docs/b.md", "docs/a.md", 3)])
    fx.baseline(ACTIVE, [pair("demo", "docs/a.md", "docs/b.md", 4)])
    proc = fx.hook_commit()
    assert proc.returncode == 1
    assert "count rises: docs/a.md + docs/b.md: 3 -> 4" in out(proc)


def test_r8_removals_and_a_falling_count_pass(fx):
    seed(fx, [pair("demo", "docs/a.md", "docs/b.md", 3),
              entry("demo", "docs/a.md", "sleep 30"), entry("demo", "docs/c.md", "x")])
    fx.baseline(ACTIVE, [pair("demo", "docs/a.md", "docs/b.md", 2)])
    proc = fx.hook_commit()
    assert proc.returncode == 0, out(proc)


@pytest.mark.parametrize("head", ["commit-without-baseline", "unborn"])
def test_r12_head_without_baseline_accepts_the_seeded_file(fx, head):
    if head == "commit-without-baseline":
        fx.write("README", "x\n")
        fx.git("add", "README")
        fx.git("commit", "-q", "-m", "first")
    fx.stub_tool(["demo"])
    fx.baseline(ACTIVE, [entry("demo", "docs/a.md", "sleep 30")])
    proc = fx.hook_commit()
    assert proc.returncode == 0, out(proc)


def test_hook_rejects_a_malformed_staged_baseline(fx):
    seed(fx, [])
    fx.write(BASELINE, "{not json")
    proc = fx.hook_commit()
    assert proc.returncode == 2
    assert "bad JSON" in out(proc)


# ---- Hook rows around gitleaks (H1 to H4) ----


def fake_secret():
    alphabet = string.ascii_letters + string.digits
    return "gh" + "p_" + "".join(secrets.choice(alphabet) for _ in range(36))


@pytest.mark.parametrize("path", ["fast", "ratchet-step"])
def test_h1_staged_secret_with_clean_baseline_fails(fx, path):
    seed(fx, [])
    if path == "ratchet-step":
        fx.baseline({**ACTIVE, "fresh": {"tool": "tools/stub-tool"}}, [])
    fx.write("leak.txt", f"token = {fake_secret()}\n")
    proc = fx.hook_commit()
    assert proc.returncode == 1
    assert "leaks found" in out(proc)


def gitleaks_marker_stub(tmp):
    bindir = tmp / "stubbin"
    bindir.mkdir()
    marker = tmp / "gitleaks-ran"
    stub = bindir / "gitleaks"
    stub.write_text(f"#!/bin/sh\ntouch {marker}\nexit 0\n")
    stub.chmod(0o755)
    return bindir, marker


def test_h2_ratchet_violation_blocks_before_gitleaks(fx, tmp_path):
    seed(fx, [])
    fx.baseline(ACTIVE, [entry("demo", "docs/a.md", "sleep 30")])
    bindir, marker = gitleaks_marker_stub(tmp_path)
    proc = fx.hook_commit(PATH=f"{bindir}:{os.environ['PATH']}")
    assert proc.returncode == 1
    assert "new entry under registered id: docs/a.md: sleep 30" in out(proc)
    assert not marker.exists()


def path_without_gitleaks():
    dirs = os.environ["PATH"].split(os.pathsep)
    return os.pathsep.join(d for d in dirs if not (Path(d) / "gitleaks").exists())


@pytest.mark.parametrize("path", ["fast", "ratchet-step"])
def test_h3_gitleaks_absent_fails_closed(fx, path):
    seed(fx, [])
    if path == "ratchet-step":
        fx.baseline({**ACTIVE, "fresh": {"tool": "tools/stub-tool"}}, [])
    fx.write("docs/b.md", "harmless\n")
    proc = fx.hook_commit(PATH=path_without_gitleaks())
    assert proc.returncode == 1
    assert "gitleaks not found" in out(proc)


def test_h4_unrelated_file_with_malformed_worktree_baseline_takes_fast_path(fx):
    seed(fx, [])
    fx.write(BASELINE, "{not json")
    fx.write("docs/b.md", "harmless\n")
    proc = fx.hook_commit("docs/b.md")
    assert proc.returncode == 0, out(proc)


def test_hook_mode_reads_only_inside_the_repository(fx):
    seed(fx, [entry("demo", "docs/a.md", "sleep 30")])
    fx.baseline(ACTIVE, [])
    fx.git("add", BASELINE)
    proc = fx.ratchet("hook")
    assert proc.returncode == 0, out(proc)


# ---- Gate rows (R9 to R11, R13 to R17) ----


def test_r9_registered_id_whose_tool_is_missing(fx):
    fx.baseline({"ghost": {"tool": "tools/no-such-tool"}}, [])
    fx.commit()
    proc = fx.ratchet("check", "--root", ".")
    assert proc.returncode == 2
    assert 'check id "ghost"' in out(proc)
    assert "no tool implements it" in out(proc)


def test_r9_registered_id_its_tool_does_not_report(fx):
    fx.baseline({**ACTIVE, "ghost": {"tool": "tools/stub-tool"}}, [])
    fx.stub_tool(["demo"])
    fx.commit()
    proc = fx.ratchet("check", "--root", ".")
    assert proc.returncode == 2
    assert 'check id "ghost"' in out(proc)
    assert "no tool implements it" in out(proc)


def test_tool_reporting_an_unregistered_id_is_a_config_error(fx):
    seed(fx, [])
    fx.stub_tool(["demo", "stray"])
    proc = fx.ratchet("check", "--root", ".")
    assert proc.returncode == 2
    assert '"stray"' in out(proc)


def test_r10_entry_no_violation_matches(fx):
    seed(fx, [entry("demo", "docs/a.md", "sleep 30")])
    proc = fx.ratchet("check", "--root", ".")
    assert proc.returncode == 1
    assert "remove this baseline entry: docs/a.md: sleep 30" in out(proc)


def test_r11_violation_no_entry_matches(fx):
    seed(fx, [])
    fx.stub_tool(["demo"], [{"check": "demo", "file": "docs/a.md", "fingerprint": "sleep 30"}])
    proc = fx.ratchet("check", "--root", ".")
    assert proc.returncode == 1
    assert "new violation: docs/a.md: sleep 30" in out(proc)


def test_matching_violations_and_entries_pass(fx):
    seed(fx, [entry("demo", "docs/a.md", "sleep 30", count=2),
              pair("demo", "docs/a.md", "docs/b.md", 3)])
    fx.stub_tool(["demo"], [
        {"check": "demo", "file": "docs/a.md", "fingerprint": "sleep 30"},
        {"check": "demo", "file": "docs/a.md", "fingerprint": "sleep 30"},
        {"check": "demo", "files": ["docs/b.md", "docs/a.md"], "count": 3}])
    proc = fx.ratchet("check", "--root", ".")
    assert proc.returncode == 0, out(proc)


def test_a_count_below_its_entry_asks_to_lower_the_entry(fx):
    seed(fx, [pair("demo", "docs/a.md", "docs/b.md", 3)])
    fx.stub_tool(["demo"], [{"check": "demo", "files": ["docs/a.md", "docs/b.md"], "count": 2}])
    proc = fx.ratchet("check", "--root", ".")
    assert proc.returncode == 1
    assert "lower this baseline entry's count to 2: docs/a.md + docs/b.md" in out(proc)


def test_r13_baseline_absent(fx):
    fx.commit()
    proc = fx.ratchet("check", "--root", ".")
    assert proc.returncode == 2
    assert "configuration error" in out(proc)
    assert "baseline absent" in out(proc)


@pytest.mark.parametrize("text", ["", '{"checks": {}, "entries": []}'])
def test_r14_baseline_present_and_empty(fx, text):
    fx.write(BASELINE, text)
    fx.commit()
    proc = fx.ratchet("check", "--root", ".")
    assert proc.returncode == 0, out(proc)


MALFORMED = {
    "bad-json": ("{\"checks\": {", "bad JSON"),
    "missing-field": ({"check": "demo", "file": "docs/a.md", "fingerprint": "x",
                       "pass": "B"}, 'entry 0 (demo docs/a.md: x): missing field "finding"'),
    "unregistered-id": (entry("nope", "docs/a.md", "x"),
                        'entry 0 (nope docs/a.md: x): unregistered check id "nope"'),
    "bad-finding-id": (entry("demo", "docs/a.md", "x", finding="DC04"),
                       'entry 0 (demo docs/a.md: x): bad finding id "DC04"'),
}


@pytest.mark.parametrize("case", sorted(MALFORMED))
def test_r15_malformed_baseline_names_the_entry(fx, case):
    bad, expected = MALFORMED[case]
    fx.stub_tool(["demo"])
    if isinstance(bad, str):
        fx.write(BASELINE, bad)
    else:
        fx.baseline(ACTIVE, [bad])
    fx.commit()
    proc = fx.ratchet("check", "--root", ".")
    assert proc.returncode == 2
    assert "configuration error" in out(proc)
    assert expected in out(proc)


def test_r16_many_bad_run_reports_every_violation_grouped(fx):
    checks = {"alpha": {"tool": "tools/stub-tool"}, "beta": {"tool": "tools/stub-tool"}}
    seed(fx, [entry("alpha", "docs/a.md", "stale one"), entry("beta", "docs/b.md", "stale two")],
         checks)
    fx.stub_tool(["alpha", "beta"], [
        {"check": "alpha", "file": "docs/a.md", "fingerprint": "new one"},
        {"check": "alpha", "file": "docs/c.md", "fingerprint": "new two"},
        {"check": "beta", "file": "docs/d.md", "fingerprint": "new three"}])
    proc = fx.ratchet("check", "--root", ".")
    text = out(proc)
    assert proc.returncode == 1
    assert "ratchet: 5 violations in 2 checks" in text
    assert "alpha: 3" in text and "beta: 2" in text
    for line in ["remove this baseline entry: docs/a.md: stale one",
                 "new violation: docs/a.md: new one", "new violation: docs/c.md: new two",
                 "remove this baseline entry: docs/b.md: stale two",
                 "new violation: docs/d.md: new three"]:
        assert line in text
    assert text.index("alpha: 3") < text.index("new two") < text.index("beta: 2")


def test_r17_working_tree_growth_against_head(fx):
    seed(fx, [])
    fx.baseline(ACTIVE, [entry("demo", "docs/a.md", "sleep 30")])
    fx.stub_tool(["demo"], [{"check": "demo", "file": "docs/a.md", "fingerprint": "sleep 30"}])
    proc = fx.ratchet("check", "--root", ".")
    assert proc.returncode == 1
    assert "new entry under registered id: docs/a.md: sleep 30" in out(proc)


# ---- Roots, module location, bytecode (M1, M2) ----


def test_m1_worktree_copy_runs_with_a_home_holding_no_module(fx):
    seed(fx, [entry("demo", "docs/a.md", "sleep 30")])
    fx.stub_tool(["demo"], [{"check": "demo", "file": "docs/a.md", "fingerprint": "sleep 30"}])
    assert not any(fx.home.iterdir())
    proc = fx.ratchet("check", "--root", ".")
    assert proc.returncode == 0, out(proc)


def test_m2_a_read_outside_the_fixture_root_fails_the_fixture(fx):
    outside = REPO / "scripts" / "check.sh"
    reader = fx.tmp / "reader.py"
    reader.write_text(f"open({str(outside)!r}).read()\n")
    with pytest.raises(AssertionError, match=re.escape(str(outside))):
        fx.ratchet(module=reader)


def test_injected_roots_reach_each_tool(fx):
    seed(fx, [])
    projects, memory = fx.tmp / "projects", fx.tmp / "memory"
    proc = fx.ratchet("check", "--root", ".", "--home", str(fx.home),
                      "--projects-root", str(projects), "--memory-root", str(memory))
    assert proc.returncode == 0, out(proc)
    argv = json.loads((fx.root / "tools" / "stub-tool.argv.json").read_text())
    assert argv[0] == "ratchet-report"
    for flag, value in [("--home", fx.home), ("--projects-root", projects),
                        ("--memory-root", memory)]:
        assert argv[argv.index(flag) + 1] == str(value)


def pycache_dirs(*trees):
    return {p for t in trees for p in t.rglob("__pycache__")}


def test_no_bytecode_lands_in_the_stow_packages(fx):
    trees = [REPO / "claude", REPO / "bin", fx.root / "claude"]
    before = pycache_dirs(*trees)
    seed(fx, [entry("demo", "docs/a.md", "sleep 30")])
    fx.stub_tool(["demo"], [{"check": "demo", "file": "docs/a.md", "fingerprint": "sleep 30"}])
    env = {k: v for k, v in fx.env().items() if k != "PYTHONDONTWRITEBYTECODE"}
    subprocess.run([PY, str(MODULE), "check", "--root", "."], cwd=fx.root, env=env, check=True)
    fx.baseline(ACTIVE, [])
    fx.git("add", BASELINE)
    subprocess.run(["git", "-c", f"core.hooksPath={HOOKS}", "commit", "-q", "-m", "t"],
                   cwd=fx.root, env=env, check=True)
    assert pycache_dirs(*trees) == before
