"""Tests for the artist-photos units and the lines they share with navidrome.service.

The spec is docs/specs/2026-11-24-artist-photos-design.md, task artist-photos-wire. The tests
read the unit files as text, so they run on any host and start nothing.
"""

from pathlib import Path
import re
import shlex

ROOT = Path(__file__).resolve().parent.parent
UNITS = ROOT / "systemd/.config/systemd/user"
ND_KEYS = ("ND_MUSICFOLDER", "ND_DATAFOLDER", "ND_ARTISTIMAGEFOLDER", "ND_ARTISTARTPRIORITY")
# The folder step 1 of the task's "Before merge" makes, since BindPaths= fails on a missing one.
MADE_AT_INSTALL = {"%h/Music/.artist-images"}
# %S in a user unit is $XDG_STATE_HOME, where StateDirectory= makes its folders.
STATE_HOME = "%h/.local/state"


def directives(name: str) -> list[tuple[str, str, str]]:
    """Return each (section, key, value) line of a unit, in file order."""
    section = ""
    lines = []
    for raw in (UNITS / name).read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith(("#", ";")):
            continue
        if line.startswith("["):
            section = line.strip("[]")
            continue
        key, _, value = line.partition("=")
        lines.append((section, key.strip(), value.strip()))
    return lines


def values(name: str, key: str, section: str = "Service") -> list[str]:
    return [v for s, k, v in directives(name) if s == section and k == key]


def nd_lines(name: str) -> dict[str, str]:
    """Map each ND_ key named under "Units" to the whole Environment= value that sets it."""
    found = {}
    for value in values(name, "Environment"):
        match = re.match(r'"?(ND_[A-Z]+)=', value)
        if match and match.group(1) in ND_KEYS:
            assert match.group(1) not in found, f"{name} sets {match.group(1)} twice"
            found[match.group(1)] = value
    return found


def test_navidrome_and_helper_share_the_four_nd_lines():
    server = nd_lines("navidrome.service")
    helper = nd_lines("artist-photos.service")
    assert set(server) == set(ND_KEYS)
    assert helper == server


def test_each_bind_path_folder_is_made_at_install_or_by_a_state_directory():
    state_dirs = {
        f"{STATE_HOME}/{d}"
        for unit in ("navidrome.service", "artist-photos.service")
        for value in values(unit, "StateDirectory")
        for d in value.split()
    }
    binds = [p for value in values("artist-photos.service", "BindPaths") for p in shlex.split(value)]
    assert binds
    for path in binds:
        assert path in MADE_AT_INSTALL or path in state_dirs, f"nothing makes {path}"


def test_fresh_tracks_starts_the_helper_on_success():
    assert values("fresh-tracks.service", "OnSuccess", section="Unit") == ["artist-photos.service"]


def test_helper_service_starts_the_tracked_script():
    assert values("artist-photos.service", "ConditionHost", section="Unit") == ["pavilion"]
    (start,) = values("artist-photos.service", "ExecStart")
    assert start == "%h/.local/bin/artist-photos"
    assert (ROOT / "bin/.local/bin/artist-photos").is_file()
