"""Tests for scripts/githooks/pre-commit, which runs gitleaks on staged content."""

import os
import secrets
import string
import subprocess
from pathlib import Path

HOOK = Path(__file__).resolve().parent.parent / "scripts" / "githooks" / "pre-commit"


def make_repo(tmp_path):
    root = tmp_path / "repo"
    home = tmp_path / "home"
    root.mkdir()
    home.mkdir()
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(HOME=str(home), XDG_CONFIG_HOME=str(home / ".config"), GIT_CONFIG_NOSYSTEM="1")
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=root, env=env, check=True)
    return root, env


def run_hook(root, env, **overrides):
    """Stage everything, then run the real hook as git would, keeping its exit code."""
    subprocess.run(["git", "add", "-A"], cwd=root, env=env, check=True)
    return subprocess.run([str(HOOK)], cwd=root, env={**env, **overrides},
                          capture_output=True, text=True)


def fake_secret():
    alphabet = string.ascii_letters + string.digits
    return "gh" + "p_" + "".join(secrets.choice(alphabet) for _ in range(36))


def path_without_gitleaks():
    dirs = os.environ["PATH"].split(os.pathsep)
    return os.pathsep.join(d for d in dirs if not (Path(d) / "gitleaks").exists())


def test_staged_secret_fails(tmp_path):
    root, env = make_repo(tmp_path)
    (root / "leak.txt").write_text(f"token = {fake_secret()}\n")
    proc = run_hook(root, env)
    assert proc.returncode == 1
    assert "leaks found" in proc.stdout + proc.stderr


def test_gitleaks_absent_fails_closed(tmp_path):
    root, env = make_repo(tmp_path)
    (root / "b.md").write_text("harmless\n")
    proc = run_hook(root, env, PATH=path_without_gitleaks())
    assert proc.returncode == 1
    assert "gitleaks not found" in proc.stdout + proc.stderr
