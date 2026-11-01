"""Fixtures for claude-tooling-sync: the tree-only `lint` checks and `verify`'s collision check.

Lint rows build a fixture tree at <root>/claude/.claude/{tooling,skills}, the shape
`scripts/check.sh` reads through `claude-tooling-sync lint --root .`. Verify rows build a
fixture home holding .dotfiles/claude/.claude/{tooling,skills,settings.json}, a live
.claude/settings.json, and .claude.json,
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
    (home / ".claude").mkdir()
    (home / ".claude" / "settings.json").write_text('{"enabledPlugins": {}}')
    return home


def stub_claude_on_path(tmp_path):
    bindir = tmp_path / "stubbin"
    bindir.mkdir(exist_ok=True)
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


# ---- ratchet-report: description-cap and fork-skill ----


def cap_skill(root, name, description, extra=""):
    put_skill(root, name, f"---\nname: {name}\ndescription: {description}\n{extra}---\n\nBody.\n")


def report(root, *flags):
    proc = run("ratchet-report", "--root", str(root), *flags)
    assert proc.returncode == 0, out(proc)
    return json.loads(proc.stdout)


def hits(data, check):
    return sorted((v["file"].split("/")[-2], v["fingerprint"]) for v in data["violations"]
                  if v["check"] == check)


def test_description_cap_counts_code_points_after_collapse(tmp_path):
    cap_skill(tmp_path, "over", "é" * 501)
    cap_skill(tmp_path, "edge", "x" * 500)
    cap_skill(tmp_path, "gated", "y" * 901, extra="paths: src/**\n")
    put_skill(tmp_path, "block",
              "---\nname: block\ndescription: >-\n  " + "word " * 60 + "\n  " + "more " * 41 + "\n---\n")
    cap_skill(tmp_path, "colon", "Use when: " + "z" * 495)
    data = report(tmp_path)
    assert hits(data, "description-cap") == [("block", "description"), ("colon", "description"),
                                             ("over", "description")]


def test_description_cap_scopes_to_skill_dirs_without_synced(tmp_path):
    cap_skill(tmp_path, "vendored", "v" * 501)
    cap_skill(tmp_path, "synced", "s" * 501)
    d = tmp_path / "claude" / ".claude" / "skills" / "synced" / "inner"
    d.mkdir(parents=True)
    (d / "SKILL.md").write_text("---\nname: inner\ndescription: " + "i" * 501 + "\n---\n")
    assert hits(report(tmp_path), "description-cap") == [("vendored", "description")]


def test_missing_description_is_clean_and_unterminated_frontmatter_exits_2(tmp_path):
    put_skill(tmp_path, "bare", "---\nname: bare\n---\n")
    assert hits(report(tmp_path), "description-cap") == []
    put_skill(tmp_path, "broken", "---\nname: broken\ndescription: x\n")
    proc = run("ratchet-report", "--root", str(tmp_path))
    assert proc.returncode == 2
    assert "unterminated frontmatter" in out(proc)


def fork_skill(root, name, body, context="context: fork\n"):
    put_skill(root, name, f"---\nname: {name}\ndescription: d\n{context}---\n\n{body}\n")


def test_fork_skill_phrases_fail_only_under_context_fork(tmp_path):
    fork_skill(tmp_path, "bad", "Apply the rule under discussion, and ask the user.")
    fork_skill(tmp_path, "plain", "Apply the rule under discussion.", context="")
    fork_skill(tmp_path, "clean", "Apply the rule to the diff.")
    fork_skill(tmp_path, "wrapped", "Apply the rule Under\n  Discussion now.")
    fork_skill(tmp_path, "quote", 'Then ask "which page?" of the owner.')
    data = report(tmp_path)
    assert hits(data, "fork-skill") == [("bad", "ask the user"), ("bad", "under discussion"),
                                        ("quote", 'ask "'), ("wrapped", "under discussion")]


def test_fork_skill_repeats_report_one_violation_each(tmp_path):
    fork_skill(tmp_path, "twice", "It was delegated. Then delegated again.")
    assert hits(report(tmp_path), "fork-skill") == [("twice", "delegated"), ("twice", "delegated")]


def test_ratchet_report_accepts_the_forwarded_flags_and_names_both_ids(tmp_path):
    data = report(tmp_path, "--home", str(tmp_path), "--projects-root", str(tmp_path),
                  "--memory-root", str(tmp_path))
    assert data["implements"] == ["description-cap", "fork-skill"]
    assert data["violations"] == []


# ---- the generated live settings.json ----


def tracked_settings(home):
    return home / ".dotfiles" / "claude" / ".claude" / "settings.json"


def live_settings(home):
    return home / ".claude" / "settings.json"


def sync(command, home, tmp_path):
    args = [command, "--home", str(home)]
    if command == "verify":
        args += ["--projects-root", str(tmp_path / "projects")]
    return run(*args, env={"PATH": stub_claude_on_path(tmp_path)})


def test_apply_replaces_a_symlink_and_keeps_live_only_keys(tmp_path):
    home = fixture_home(tmp_path)
    old = tmp_path / "old.json"
    old.write_text('{"model": "opus", "enabledPlugins": {}}')
    live_settings(home).unlink()
    live_settings(home).symlink_to(old)
    tracked_settings(home).write_text('{"enabledPlugins": {"a@b": true}}')

    proc = sync("apply", home, tmp_path)
    assert proc.returncode == 0, out(proc)
    assert not live_settings(home).is_symlink()
    assert json.loads(live_settings(home).read_text()) == {"model": "opus",
                                                           "enabledPlugins": {"a@b": True}}
    assert json.loads(old.read_text())["enabledPlugins"] == {}


def test_second_apply_changes_nothing(tmp_path):
    home = fixture_home(tmp_path)
    tracked_settings(home).write_text('{"enabledPlugins": {}, "tui": "fullscreen"}')
    assert sync("apply", home, tmp_path).returncode == 0
    before = live_settings(home).stat().st_mtime_ns
    proc = sync("apply", home, tmp_path)
    assert proc.returncode == 0, out(proc)
    assert "settings.json is current" in out(proc)
    assert live_settings(home).stat().st_mtime_ns == before


def test_verify_fails_on_a_missing_live_settings_file(tmp_path):
    home = fixture_home(tmp_path)
    live_settings(home).unlink()
    proc = sync("verify", home, tmp_path)
    assert proc.returncode == 1
    assert "missing" in out(proc)


def test_verify_fails_on_a_live_settings_link(tmp_path):
    home = fixture_home(tmp_path)
    live_settings(home).unlink()
    live_settings(home).symlink_to(tracked_settings(home))
    proc = sync("verify", home, tmp_path)
    assert proc.returncode == 1
    assert "a link" in out(proc)


def test_verify_fails_on_a_changed_tracked_key_and_passes_on_a_live_only_key(tmp_path):
    home = fixture_home(tmp_path)
    tracked_settings(home).write_text('{"enabledPlugins": {}, "tui": "fullscreen"}')
    live_settings(home).write_text('{"enabledPlugins": {}, "tui": "default"}')
    proc = sync("verify", home, tmp_path)
    assert proc.returncode == 1
    assert "tui" in out(proc)

    live_settings(home).write_text('{"enabledPlugins": {}, "tui": "fullscreen", "model": "opus"}')
    proc = sync("verify", home, tmp_path)
    assert proc.returncode == 0, out(proc)


def test_cutover_keeps_preference_keys_and_leaves_the_tracked_file_alone(tmp_path):
    home = fixture_home(tmp_path)
    live_settings(home).write_text(json.dumps({
        "enabledPlugins": {}, "model": "opus", "effortLevel": "medium",
        "modelSettings": {"claude-fable-5-1": {"effortLevel": "high"}}}))
    tracked_settings(home).write_text('{"enabledPlugins": {}, "tui": "fullscreen"}')
    tracked_bytes = tracked_settings(home).read_bytes()

    assert sync("apply", home, tmp_path).returncode == 0
    live = json.loads(live_settings(home).read_text())
    assert live["tui"] == "fullscreen"
    assert live["model"] == "opus"
    assert live["effortLevel"] == "medium"
    assert live["modelSettings"] == {"claude-fable-5-1": {"effortLevel": "high"}}
    assert sync("verify", home, tmp_path).returncode == 0

    live["modelSettings"]["claude-opus-5-5"] = {"effortLevel": "low"}
    live_settings(home).write_text(json.dumps(live))
    proc = sync("verify", home, tmp_path)
    assert proc.returncode == 0, out(proc)
    assert tracked_settings(home).read_bytes() == tracked_bytes


# ---- update-skills restows the claude package ----

def load_tool():
    """Import the tool as a module so restow runs in-process against a fixture home."""
    import importlib.util
    spec = importlib.util.spec_from_loader("claude_tooling_sync", loader=None)
    module = importlib.util.module_from_spec(spec)
    exec(compile(TOOL.read_text(), str(TOOL), "exec"), module.__dict__)
    return module


def stub_stow(tmp_path, body):
    bindir = tmp_path / "stubbin"
    bindir.mkdir()
    stub = bindir / "stow"
    stub.write_text("#!/bin/sh\n" + body)
    stub.chmod(0o755)
    return bindir


def test_restow_runs_stow_from_the_dotfiles_checkout(tmp_path, monkeypatch, capsys):
    home = tmp_path / "home"
    (home / ".dotfiles").mkdir(parents=True)
    log = tmp_path / "stow.log"
    bindir = stub_stow(tmp_path, f'pwd > "{log}"; echo "$@" >> "{log}"\n')
    monkeypatch.setenv("PATH", f"{bindir}:{os.environ['PATH']}")
    tool = load_tool()
    tool.restow(tool.Paths(home))
    cwd, args = log.read_text().splitlines()
    assert Path(cwd).resolve() == (home / ".dotfiles").resolve()
    assert args == f"-R -t {home} claude"
    assert "restowed claude" in capsys.readouterr().out


def test_restow_names_the_manual_command_when_stow_fails(tmp_path, monkeypatch, capsys):
    home = tmp_path / "home"
    (home / ".dotfiles").mkdir(parents=True)
    bindir = stub_stow(tmp_path, "echo 'conflict' >&2; exit 1\n")
    monkeypatch.setenv("PATH", f"{bindir}:{os.environ['PATH']}")
    tool = load_tool()
    tool.restow(tool.Paths(home))
    text = capsys.readouterr().out
    assert "stow -R claude" in text and "conflict" in text


# ---- the standards plugin: verify names the install, update-skills writes to its clone ----

STANDARDS_KEY = "standards@glw907-standards"
STANDARDS_ENTRY = {**ENTRY, "path": "skills/go", "home": "standards"}


def standards_home(tmp_path):
    """A fixture home whose tracked settings enable the plugin and whose manifest has a plugin skill."""
    home = fixture_home(tmp_path)
    claude = home / ".dotfiles" / "claude" / ".claude"
    (claude / "settings.json").write_text(json.dumps({"enabledPlugins": {STANDARDS_KEY: True}}))
    (claude / "tooling" / "vendored-skills.json").write_text(
        json.dumps({"skills": {"go-conventions": STANDARDS_ENTRY}}))
    return home


def test_verify_names_the_install_when_the_standards_plugin_is_absent(tmp_path):
    home = standards_home(tmp_path)
    proc = run("verify", "--home", str(home), "--projects-root", str(tmp_path / "projects"),
              env={"PATH": stub_claude_on_path(tmp_path)})
    assert proc.returncode == 1
    assert "claude plugin marketplace add glw907/standards" in out(proc)
    assert f"claude plugin install {STANDARDS_KEY}" in out(proc)


def test_verify_does_not_look_for_a_plugin_skill_under_the_skills_directory(tmp_path):
    home = standards_home(tmp_path)
    proc = run("verify", "--home", str(home), "--projects-root", str(tmp_path / "projects"),
              env={"PATH": stub_claude_on_path(tmp_path)})
    assert "missing under claude/.claude/skills" not in out(proc)


def test_update_skills_refuses_when_the_standards_clone_is_missing(tmp_path):
    home = standards_home(tmp_path)
    proc = run("update-skills", "go-conventions", "--home", str(home))
    assert proc.returncode != 0
    assert "Projects/standards" in out(proc) and "missing" in out(proc)


def test_update_skills_refuses_when_the_standards_clone_is_dirty(tmp_path):
    home = standards_home(tmp_path)
    clone = home / "Projects" / "standards"
    clone.mkdir(parents=True)
    subprocess.run(["git", "init", "-q", "-b", "main", str(clone)], check=True)
    (clone / "stray.txt").write_text("uncommitted\n")
    proc = run("update-skills", "go-conventions", "--home", str(home))
    assert proc.returncode != 0
    assert "dirty" in out(proc)
