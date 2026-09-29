#!/usr/bin/env python3
"""Self-mode reference and retired-phrase checks over a Claude Code tree.

Two ratchet checks, both scoped to the scan set below: ``claude/.claude/agents``, authored
``skills`` (a directory named in ``vendored-skills.json``, or ``skills/synced``, is
third-party), ``workflows``, ``docs`` (excluding ``docs/record``), ``output-styles``,
``instructions``, and ``CLAUDE.md``. Excluded everywhere: any ``evals/research`` path segment,
and any path component whose name starts with a date (``YYYY-MM-DD``), since those are dated
snapshots, not living prose. Scanned extensions are ``.md`` (plus the bare ``CLAUDE.md`` file)
and ``.js``; ``.json`` and other data files never carry prose citations or retired phrases.

``dead-reference``: every single-backtick span in a scanned ``.md`` file that looks like a path
(it starts with ``~`` or ``/``) must resolve. This is self mode: a ``~/.claude/<dir>/...`` span
rewrites to ``<root>/claude/.claude/<dir>/...`` and a ``~/.local/bin/<x>`` span to
``<root>/bin/.local/bin/<x>``, so a worktree that adds or deletes a doc is judged on its own
tree. A span into ``~/Projects`` (tilde or the injected home's literal expansion) or a bare
repo-relative span (no leading ``~`` or ``/``) belongs to cross-repo mode and is never checked
here. A span carrying a placeholder (``<``, ``{``, ``*``, or an ellipsis) always passes,
unchecked. A bare single-segment absolute span with no further ``/`` (``/loop``, ``/etc``) is
never a path citation on this workstation (Claude Code slash commands and route stubs share the
form); it is skipped. Every other absolute span, tilde or not, resolves as written against the
``--home``-relative real filesystem.

``retired-phrase``: a phrase from ``claude/.claude/tooling/retired-phrases.txt`` (one literal
phrase per line, matched case-insensitively with internal whitespace tolerant of line wrap,
``#`` comments allowed) fails wherever it appears in a scanned ``.md`` or ``.js`` file, unless
that occurrence's line also carries the literal marker ``retired-ok``. The retired-phrase scan
alone also reaches vendored skills (only ``skills/synced`` stays excluded), so a superseded
phrase is caught wherever it was copied, not only in workstation-authored prose. An absent or
comment-only phrase list is a configuration error (exit 2): a vacuous list is a silent tripwire.

Protocol: ``check-claude-refs.py ratchet-report --root ROOT [--home HOME]
[--projects-root PROJECTS_ROOT] [--memory-root MEMORY_ROOT]`` prints the JSON
``claude/.claude/tooling/ratchet.py``'s ``emit_report`` writes. ``--projects-root`` and
``--memory-root`` are accepted for protocol parity with the shared roots contract; self mode
does not read them. The module imports the shared ratchet baseline module from
``Path(__file__).resolve()``, never through ``~/.claude``, with ``sys.dont_write_bytecode`` set
first, per that module's own tool contract.

Exit codes, shared with the ratchet: 0 on a clean ``ratchet-report``, 2 on a configuration
error (an absent or vacuous retired-phrase list). ``ratchet-report`` itself never exits 1; the
shared ratchet module turns its violations into the gate's exit 1.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True
_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent / "claude" / ".claude" / "tooling"))
import ratchet  # noqa: E402

ConfigError = ratchet.ConfigError

DEAD_REFERENCE = "dead-reference"
RETIRED_PHRASE = "retired-phrase"
IMPLEMENTS = (DEAD_REFERENCE, RETIRED_PHRASE)

RETIRED_PHRASES_PATH = "claude/.claude/tooling/retired-phrases.txt"
CLAUDE_DIR = ("agents", "skills", "workflows", "docs", "output-styles", "instructions")
SCAN_EXTENSIONS = (".md", ".js")

BACKTICK_SPAN = re.compile(r"`([^`\n]+)`")
DATED = re.compile(r"^\d{4}-\d{2}-\d{2}")
PLACEHOLDER = re.compile(r"[<{*]|\.\.\.")
RETIRED_OK = "retired-ok"


def vendored_skill_names(root):
    """Return the skill directory names ``vendored-skills.json`` lists (a key or its rename)."""
    manifest_path = root / "claude" / ".claude" / "tooling" / "vendored-skills.json"
    if not manifest_path.is_file():
        return set()
    data = json.loads(manifest_path.read_text())
    skills = data.get("skills", {}) if isinstance(data, dict) else {}
    return {entry.get("rename", name) for name, entry in skills.items()
            if isinstance(entry, dict)}


def is_dated(name):
    """Return whether a path component's name starts with a ``YYYY-MM-DD`` date."""
    return bool(DATED.match(name))


def scan_files(root, *, include_vendored):
    """Yield every ``.md``/``.js`` file in scan-scope reach, relative to ``root``.

    ``docs/record``, any ``evals/research`` segment, and any dated path component are always
    excluded. ``skills/synced`` is always excluded; the rest of ``skills`` is excluded too
    unless ``include_vendored`` is set (the retired-phrase check's wider reach).
    """
    claude_dir = root / "claude" / ".claude"
    vendored = vendored_skill_names(root) if not include_vendored else set()
    claude_md = claude_dir / "CLAUDE.md"
    if claude_md.is_file():
        yield claude_md
    for top in CLAUDE_DIR:
        base = claude_dir / top
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*")):
            if not path.is_file() or path.suffix not in SCAN_EXTENSIONS:
                continue
            rel_parts = path.relative_to(base).parts
            if top == "docs" and rel_parts and rel_parts[0] == "record":
                continue
            if top == "skills":
                if rel_parts and rel_parts[0] == "synced":
                    continue
                if rel_parts and rel_parts[0] in vendored:
                    continue
            all_parts = path.relative_to(claude_dir).parts
            if any(all_parts[i:i + 2] == ("evals", "research") for i in range(len(all_parts) - 1)):
                continue
            if any(is_dated(part) for part in all_parts):
                continue
            yield path


def is_in_home_projects(candidate, home):
    """Return whether ``candidate`` (already home-expanded) sits under ``home / "Projects"``."""
    try:
        candidate.relative_to(home / "Projects")
        return True
    except ValueError:
        return False


def resolve_self_mode(raw, root, home):
    """Return the Path a self-mode span resolves to, or None if out of self-mode reach.

    ``~/.claude/<dir>/...`` and ``~/.local/bin/<x>`` rewrite under ``root``. A span into
    ``~/Projects`` (tilde or the home's literal absolute form) and a bare repo-relative span
    belong to cross-repo mode and return None. A placeholder span, a protocol-relative URL
    (``//host/...``), and a bare single-segment absolute span (no further ``/``, a slash
    command or route stub) are never path citations and return None. Everything else absolute,
    tilde or not, resolves as written against ``home``.
    """
    if PLACEHOLDER.search(raw) or raw.startswith("//"):
        return None
    if raw.startswith("~/.claude/"):
        return root / "claude" / ".claude" / raw[len("~/.claude/"):]
    if raw.startswith("~/.local/bin/"):
        return root / "bin" / ".local" / "bin" / raw[len("~/.local/bin/"):]
    if raw.startswith("~/Projects/") or raw == "~/Projects":
        return None
    if raw.startswith("~/"):
        expanded = home / raw[2:]
    elif raw.startswith("/"):
        if raw.count("/") == 1:
            return None  # bare single-segment absolute: a slash command or route stub
        expanded = Path(raw)
    else:
        return None  # bare repo-relative: cross-repo mode
    if is_in_home_projects(expanded, home):
        return None
    return expanded


def dead_reference_violations(root, home):
    """Yield ``{"check", "file", "fingerprint"}`` for every unresolved self-mode span.

    Markdown only: a ``.js`` backtick pair is a template literal, not an inline code span, and
    scanning it for path-shaped text would read JavaScript syntax as prose citations.
    """
    for path in scan_files(root, include_vendored=False):
        if path.suffix != ".md":
            continue
        text = path.read_text(errors="replace")
        rel = str(path.relative_to(root))
        for m in BACKTICK_SPAN.finditer(text):
            raw = m.group(1)
            if not (raw.startswith("~/") or raw.startswith("/")):
                continue
            target = resolve_self_mode(raw, root, home)
            if target is None:
                continue
            if not target.exists():
                yield {"check": DEAD_REFERENCE, "file": rel, "fingerprint": raw}


def load_retired_phrases(root):
    """Return the retired phrases, each with its compiled whitespace-tolerant pattern.

    Raises ConfigError when the list is absent or holds no phrase after stripping ``#``
    comments and blank lines (a vacuous tripwire).
    """
    path = root / RETIRED_PHRASES_PATH
    if not path.is_file():
        raise ConfigError([f"{path}: retired-phrase list absent"])
    phrases = []
    for line in path.read_text().splitlines():
        text = line.split("#", 1)[0].strip()
        if text:
            phrases.append(text)
    if not phrases:
        raise ConfigError([f"{path}: retired-phrase list is vacuous (no phrase after comments)"])
    compiled = [(p, re.compile(r"\s+".join(re.escape(w) for w in p.split()), re.IGNORECASE))
                for p in phrases]
    return compiled


def retired_phrase_violations(root):
    """Yield ``{"check", "file", "fingerprint"}`` for each phrase hit outside a retired-ok line."""
    phrases = load_retired_phrases(root)
    for path in scan_files(root, include_vendored=True):
        text = path.read_text(errors="replace")
        rel = str(path.relative_to(root))
        lines = text.splitlines(keepends=True)
        offsets = []
        pos = 0
        for line in lines:
            offsets.append(pos)
            pos += len(line)
        for phrase, pattern in phrases:
            for m in pattern.finditer(text):
                start_line = _line_index(offsets, m.start())
                end_line = _line_index(offsets, max(m.end() - 1, m.start()))
                if any(RETIRED_OK in lines[i] for i in range(start_line, end_line + 1)):
                    continue
                yield {"check": RETIRED_PHRASE, "file": rel, "fingerprint": phrase}


def _line_index(offsets, pos):
    """Return the 0-based line index whose text contains byte offset ``pos``."""
    lo, hi = 0, len(offsets) - 1
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if offsets[mid] <= pos:
            lo = mid
        else:
            hi = mid - 1
    return lo


def cmd_ratchet_report(root, home):
    """Print the ratchet report for both checks; raise ConfigError on a bad phrase list."""
    violations = list(dead_reference_violations(root, home))
    violations += list(retired_phrase_violations(root))
    ratchet.emit_report(IMPLEMENTS, violations)
    return 0


def main(argv=None):
    """Parse arguments and dispatch; return the process exit code."""
    parser = argparse.ArgumentParser(prog="check-claude-refs",
                                     description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    report = sub.add_parser("ratchet-report", help="print the ratchet report for both checks")
    report.add_argument("--root", required=True, type=Path)
    report.add_argument("--home", type=Path, default=Path.home())
    report.add_argument("--projects-root", type=Path, default=None)
    report.add_argument("--memory-root", type=Path, default=None)
    args = parser.parse_args(argv)
    try:
        return cmd_ratchet_report(args.root.resolve(), args.home.resolve())
    except ConfigError as err:
        print(f"{args.command}: configuration error", file=sys.stderr)
        for problem in err.problems:
            print(f"  {problem}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
