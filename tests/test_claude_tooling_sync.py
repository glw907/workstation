"""Fixtures for claude-tooling-sync: the tree-only `lint` checks and `verify`'s collision check.

Lint rows build a fixture tree at <root>/claude/.claude/{tooling,skills}, the shape
`scripts/check.sh` reads through `claude-tooling-sync lint --root .`. Verify rows build a
fixture home holding .dotfiles/claude/.claude/{tooling,skills,settings.json} and .claude.json,
with a stub `claude` binary on PATH so the machine checks run without touching the real
workstation.
"""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TOOL = REPO / "bin" / ".local" / "bin" / "claude-tooling-sync"
PY = shutil.which("python3") or sys.executable

ENTRY = {"repo": "example/repo", "path": "skills/x", "branch": "main", "commit": "abc123def456",
         "license": "MIT"}


def run(*args, env=None):
    full_env = dict(os.environ)
    if env:
        full_env.update(env)
    return subprocess.run([PY, str(TOOL), *args], capture_output=True, text=True, env=full_env)


def out(proc):
    return proc.stdout + proc.stderr


def write_manifest(root, skills):
    path = root / "claude" / ".claude" / "tooling" / "vendored-skills.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"skills": skills}, indent=2))


def write_skill(root, name, licensed):
    d = root / "claude" / ".claude" / "skills" / name
    d.mkdir(parents=True, exist_ok=True)
    (d / "SKILL.md").write_text(f"---\nname: {name}\n---\n")
    if licensed:
        (d / "LICENSE").write_text("MIT\n")


# ---- lint --root (S1, S2, S4, S5) ----


def test_s1_manifest_absent(tmp_path):
    proc = run("lint", "--root", str(tmp_path))
    assert proc.returncode == 2
    assert "configuration error" in out(proc)
    assert "vendored-skills.json" in out(proc)


def test_s2_manifest_malformed_names_the_entry(tmp_path):
    path = tmp_path / "claude" / ".claude" / "tooling" / "vendored-skills.json"
    path.parent.mkdir(parents=True)
    path.write_text('{"skills": {"x": {"repo": "a/b"}}}')
    proc = run("lint", "--root", str(tmp_path))
    assert proc.returncode == 2
    assert "configuration error" in out(proc)
    assert '"x": missing field "path"' in out(proc)


def test_s4_unmanifested_third_party_skill_names_the_dir(tmp_path):
    write_manifest(tmp_path, {})
    write_skill(tmp_path, "extra", licensed=True)
    proc = run("lint", "--root", str(tmp_path))
    assert proc.returncode == 1
    dir_path = tmp_path / "claude" / ".claude" / "skills" / "extra"
    assert str(dir_path) in out(proc)
    assert "no entry in claude/.claude/tooling/vendored-skills.json" in out(proc)


def test_manifested_third_party_skill_passes(tmp_path):
    write_manifest(tmp_path, {"extra": ENTRY})
    write_skill(tmp_path, "extra", licensed=True)
    proc = run("lint", "--root", str(tmp_path))
    assert proc.returncode == 0, out(proc)


def test_unlicensed_personal_skill_is_not_flagged(tmp_path):
    write_manifest(tmp_path, {})
    write_skill(tmp_path, "mine", licensed=False)
    proc = run("lint", "--root", str(tmp_path))
    assert proc.returncode == 0, out(proc)


def test_s5_unknown_argument_exits_with_usage(tmp_path):
    proc = run("lint", "--root", str(tmp_path), "--bogus")
    assert proc.returncode == 2
    assert "usage" in out(proc)


def test_lint_root_is_green_on_this_worktree():
    proc = run("lint", "--root", str(REPO))
    assert proc.returncode == 0, out(proc)


# ---- verify (S3) ----


def fixture_home(tmp_path):
    home = tmp_path / "home"
    tooling = home / ".dotfiles" / "claude" / ".claude" / "tooling"
    tooling.mkdir(parents=True)
    (tooling / "mcp-servers.json").write_text('{"servers": {}}')
    (tooling / "vendored-skills.json").write_text('{"skills": {}}')
    (home / ".dotfiles" / "claude" / ".claude" / "settings.json").write_text(
        '{"enabledPlugins": {}}')
    return home


def stub_claude_on_path(tmp_path):
    bindir = tmp_path / "stubbin"
    bindir.mkdir()
    stub = bindir / "claude"
    stub.write_text("#!/bin/sh\nexit 0\n")
    stub.chmod(0o755)
    return f"{bindir}:{os.environ['PATH']}"


def test_s3_personal_skill_shadows_a_project_skill(tmp_path):
    home = fixture_home(tmp_path)
    personal = home / ".dotfiles" / "claude" / ".claude" / "skills" / "foo"
    personal.mkdir(parents=True)
    (personal / "SKILL.md").write_text("---\nname: foo\n---\n")

    projects = tmp_path / "projects"
    project_skill = projects / "site" / ".claude" / "skills" / "foo"
    project_skill.mkdir(parents=True)

    proc = run("verify", "--home", str(home), "--projects-root", str(projects),
              env={"PATH": stub_claude_on_path(tmp_path)})
    assert proc.returncode == 1
    assert str(personal) in out(proc)
    assert str(project_skill) in out(proc)


def test_verify_passes_with_no_collision(tmp_path):
    home = fixture_home(tmp_path)
    projects = tmp_path / "projects"
    projects.mkdir()

    proc = run("verify", "--home", str(home), "--projects-root", str(projects),
              env={"PATH": stub_claude_on_path(tmp_path)})
    assert proc.returncode == 0, out(proc)


# ---- apply-overlays and the overlay lint checks ----

VALE = {"repo": "vale/tools", "branch": "main", "commit": "abc123def456", "license": "MIT"}
HOSTILE = 'Use when: a "quoted" thing # not a comment, `x` works'


def vale_manifest(**extra):
    return {
        "one": {**VALE, "path": "skills/one", **extra.get("one", {})},
        "two": {**VALE, "path": "skills/fix", "rename": "vale-fix", **extra.get("two", {})},
        "solo": {**ENTRY, "path": "skills/fix", **extra.get("solo", {})},
    }


def put_skill(root, name, text):
    d = root / "claude" / ".claude" / "skills" / name
    d.mkdir(parents=True, exist_ok=True)
    (d / "SKILL.md").write_text(text)


def read(root, name):
    return (root / "claude" / ".claude" / "skills" / name / "SKILL.md").read_text()


def overlay_tree(tmp_path, manifest):
    write_manifest(tmp_path, manifest)
    body = "\n# Title\n\nSay fix here, use `fix` and `other`.\n\n```\n`fix`\n```\n"
    put_skill(tmp_path, "one", f"---\nname: one\ndescription: old one\n---\n{body}")
    put_skill(tmp_path, "vale-fix", f'---\nname: vale-fix\ndescription: "quoted old"\n---\n{body}')
    put_skill(tmp_path, "solo",
              "---\nname: solo\ndescription: >\n  block\n  old\nmetadata:\n  v: 1\n---\n" + body)


def test_descriptions_in_every_form_become_folded_blocks(tmp_path):
    overlay_tree(tmp_path, vale_manifest(one={"description": HOSTILE},
                                         two={"description": "second new"},
                                         solo={"description": "third new"}))
    proc = run("apply-overlays", "--root", str(tmp_path))
    assert proc.returncode == 0, out(proc)
    assert "description: >-\n  " + HOSTILE + "\n---" in read(tmp_path, "one")
    assert "description: >-\n  second new\n---" in read(tmp_path, "vale-fix")
    assert "description: >-\n  third new\nmetadata:\n  v: 1\n---" in read(tmp_path, "solo")
    assert run("lint", "--root", str(tmp_path)).returncode == 0


def test_note_lands_once_after_frontmatter(tmp_path):
    overlay_tree(tmp_path, vale_manifest(one={"note": "First note."}))
    run("apply-overlays", "--root", str(tmp_path))
    first = read(tmp_path, "one")
    assert first.startswith("---\nname: one\ndescription: old one\n---\n\n<!-- local-overlay -->\n"
                            "First note.\n<!-- /local-overlay -->\n\n# Title")
    run("apply-overlays", "--root", str(tmp_path))
    assert read(tmp_path, "one") == first
    write_manifest(tmp_path, vale_manifest(one={"note": "Second note."}))
    run("apply-overlays", "--root", str(tmp_path))
    changed = read(tmp_path, "one")
    assert changed.count("local-overlay -->") == 2 and "Second note." in changed
    assert "First note." not in changed


def test_sibling_spans_rewrite_only_outside_fences_in_renaming_repos(tmp_path):
    overlay_tree(tmp_path, vale_manifest())
    run("apply-overlays", "--root", str(tmp_path))
    renamed = read(tmp_path, "one")
    assert "use `vale-fix` and `other`" in renamed
    assert "Say fix here" in renamed
    assert "```\n`fix`\n```" in renamed
    assert "use `fix` and" in read(tmp_path, "solo")


def test_apply_overlays_leaves_an_empty_home_empty(tmp_path):
    root = tmp_path / "tree"
    root.mkdir()
    overlay_tree(root, vale_manifest(one={"note": "N."}))
    home = tmp_path / "home"
    home.mkdir()
    proc = run("apply-overlays", "--root", str(root), env={"HOME": str(home)})
    assert proc.returncode == 0, out(proc)
    assert list(home.iterdir()) == []


def test_lint_fails_on_missing_description_note_and_sibling(tmp_path):
    overlay_tree(tmp_path, vale_manifest(one={"description": "wanted", "note": "Wanted note."}))
    proc = run("lint", "--root", str(tmp_path))
    assert proc.returncode == 1
    text = out(proc)
    assert "x one: description differs" in text
    assert "x one: note block missing" in text
    assert "x one: sibling span `fix`" in text


def test_lint_passes_on_a_clean_overlaid_tree(tmp_path):
    overlay_tree(tmp_path, vale_manifest(one={"description": HOSTILE, "note": "A note."}))
    assert run("apply-overlays", "--root", str(tmp_path)).returncode == 0
    proc = run("lint", "--root", str(tmp_path))
    assert proc.returncode == 0, out(proc)
