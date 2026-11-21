"""Gate tests for the paths the Claude settings and the global CLAUDE.md name.

A `~/` path resolves inside this checkout first: `~/.dotfiles/<rest>` is the checkout root, and
any other `~/<rest>` is `<package>/<rest>` for a stow package in bluefin/stow-packages.txt. A path
the checkout doesn't hold resolves under the home folder, which covers `~/.local/secrets` and the
repos under `~/Projects`.
"""

import json
import os
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SETTINGS = ROOT / "claude/.claude/settings.json"
GLOBAL_FILE = ROOT / "claude/.claude/CLAUDE.md"
PACKAGES = [line.strip() for line in (ROOT / "bluefin/stow-packages.txt").read_text().splitlines()
            if line.strip() and not line.startswith("#")]


def in_checkout(path: str) -> list[Path]:
    """Return the places in this checkout a `~/` path can stand for."""
    rest = path.removeprefix("~/")
    if rest == ".dotfiles" or rest.startswith(".dotfiles/"):
        return [ROOT / rest.removeprefix(".dotfiles").lstrip("/")]
    return [ROOT / package / rest for package in PACKAGES]


def resolve(path: str) -> Path | None:
    """Return where a `~/` path exists, or None."""
    for place in [*in_checkout(path), Path.home() / path.removeprefix("~/")]:
        if place.exists():
            return place
    return None


def hook_commands() -> list[str]:
    """Return every hook command registered in the settings source."""
    settings = json.loads(SETTINGS.read_text())
    return [hook["command"] for groups in settings.get("hooks", {}).values()
            for group in groups for hook in group.get("hooks", []) if "command" in hook]


def global_file_paths() -> list[str]:
    """Return every backticked path in the global file that starts with `~/`."""
    return sorted(set(re.findall(r"`(~/[^`\s]*)`", GLOBAL_FILE.read_text())))


def test_settings_register_hooks():
    assert hook_commands()


@pytest.mark.parametrize("command", hook_commands())
def test_registered_hook_path_exists_and_runs(command):
    path = command.split()[0]
    assert path.startswith("~/"), f"{command!r} is not registered by a ~/ path"
    found = resolve(path)
    assert found is not None, f"{path} exists neither in a stow package nor under the home folder"
    assert found.is_file() and os.access(found, os.X_OK), f"{found} is not an executable file"


def test_global_file_names_paths():
    assert global_file_paths()


@pytest.mark.parametrize("path", global_file_paths())
def test_global_file_path_exists(path):
    assert resolve(path) is not None, f"{path} exists neither in this checkout nor under the home folder"
