#!/usr/bin/env python3
"""The ratchet baseline: known violations that may shrink and never grow.

The baseline is ratchet-baseline.json beside this module. It holds two things:

- ``checks``, the registry: each check id maps to ``{"tool": <repo-relative path>}``, or to
  ``{"state": "retired"}`` once the id leaves use. The registry is append-only.
- ``entries``: one object per known violation, with ``check``, ``finding`` (an audit id such as
  ``DC-04``, or ``GA-nn`` with a one-line ``defect`` for one the audit did not name), ``pass``
  (the label of the pass that removes it), and either ``file`` plus ``fingerprint`` or
  ``files`` (a sorted pair) plus ``count``. ``count`` defaults to 1 on a file entry; ``repo``
  marks a cross-repo entry.

Modes, both run with the standard library alone:

- ``hook`` compares the staged baseline with HEAD's copy (the pre-commit step).
- ``check`` runs every registered tool, matches its violations against the working-tree
  baseline, and applies the hook's growth rules against HEAD (the check.sh step).

Growth rules: a new entry under an id already registered in HEAD fails, unless it re-keys a
removed entry with the same check, fingerprint, and count; a rising count fails; a removed
registry id fails; an entry under a retired id fails; a retired id returning to active fails.
Removals, falling counts, and entries under an id new in the change pass, so a commit that
registers an id may seed its entries.

Tool protocol: the gate runs ``<tool> ratchet-report --root <root>`` (plus any injected
``--home``, ``--projects-root``, ``--memory-root``), and the tool prints the JSON that
``emit_report`` writes. A tool imports this module from ``Path(__file__).resolve()`` of its
own script, never through ``~/.claude``, and sets ``sys.dont_write_bytecode`` first.

Exit codes: 0 clean, 1 violations, 2 configuration error.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

BASELINE = "claude/.claude/tooling/ratchet-baseline.json"
PASS_LABELS = ("A-core", "A-rest", "B", "C", "D", "E", "F")
FINDING_ID = re.compile(r"(PS|CS|DC|AW|GA)-\d+")
CHECK_ID = re.compile(r"[a-z0-9][a-z0-9-]*")
ENTRY_FIELDS = {"check", "file", "files", "fingerprint", "count", "finding", "pass", "repo",
                "defect"}
TOP_FIELDS = {"comment", "checks", "entries"}


class ConfigError(Exception):
    """A missing or malformed baseline, registry, or tool report: exit 2."""

    def __init__(self, problems):
        super().__init__("\n".join(problems))
        self.problems = problems


def emit_report(implements, violations):
    """Print a tool's ratchet report: the ids it implements and the violations it found.

    Each violation is ``{"check", "file", "fingerprint"}`` or ``{"check", "files", "count"}``,
    with an optional ``repo``; repeated file violations add up to the entry's count.
    """
    print(json.dumps({"implements": sorted(implements), "violations": list(violations)}))


def locus(item):
    """Describe where a violation or entry sits, as the report prints it."""
    repo = f"{item['repo']}:" if item.get("repo") else ""
    if "files" in item:
        return repo + " + ".join(map(str, item.get("files") or []))
    return f"{repo}{item.get('file')}: {item.get('fingerprint')}"


def key(item):
    """Return the identity a baseline entry and a violation share."""
    if "files" in item:
        return (item["check"], item.get("repo", ""), tuple(sorted(item["files"])), "")
    return (item["check"], item.get("repo", ""), item["file"], item["fingerprint"])


def _shape_problems(item, fields_allowed):
    """Return the shape problems common to entries and violations."""
    problems = []
    unknown = sorted(set(item) - fields_allowed)
    if unknown:
        problems.append(f"unknown field {unknown[0]!r}")
    if not isinstance(item.get("check"), str):
        problems.append('missing field "check"')
    if ("file" in item) == ("files" in item):
        problems.append('needs exactly one of "file" and "files"')
    elif "file" in item:
        if not isinstance(item["file"], str) or not item["file"]:
            problems.append('"file" must be a non-empty string')
        if not isinstance(item.get("fingerprint"), str) or not item.get("fingerprint"):
            problems.append('missing field "fingerprint"')
    else:
        files = item["files"]
        if (not isinstance(files, list) or len(files) != 2 or files[0] == files[1]
                or not all(isinstance(f, str) and f for f in files)):
            problems.append('"files" must be two distinct paths')
        if "fingerprint" in item:
            problems.append('a "files" pair carries no fingerprint')
    count = item.get("count", 1)
    if not isinstance(count, int) or isinstance(count, bool) or count < 1:
        problems.append('"count" must be a positive integer')
    elif "files" in item and "count" not in item:
        problems.append('missing field "count"')
    if "repo" in item and (not isinstance(item["repo"], str) or not item["repo"]):
        problems.append('"repo" must be a non-empty string')
    return problems


def parse(text, source):
    """Parse baseline text into ``(checks, entries)``, entries keyed by identity.

    Empty text is an empty baseline. Raises ConfigError naming every malformed part.
    """
    if not text.strip():
        return {}, {}
    try:
        data = json.loads(text)
    except json.JSONDecodeError as err:
        raise ConfigError([f"{source}: bad JSON: {err}"]) from None
    if not isinstance(data, dict):
        raise ConfigError([f"{source}: the top level must be an object"])
    problems = [f"{source}: unknown top-level field {name!r}"
                for name in sorted(set(data) - TOP_FIELDS)]
    checks = data.get("checks")
    entries = data.get("entries")
    if not isinstance(checks, dict):
        problems.append(f'{source}: missing object "checks"')
        checks = {}
    if not isinstance(entries, list):
        problems.append(f'{source}: missing list "entries"')
        entries = []

    registry = {}
    for cid, reg in checks.items():
        where = f'{source}: check id "{cid}"'
        if not CHECK_ID.fullmatch(cid):
            problems.append(f"{where}: ids are lowercase words joined by hyphens")
        if not isinstance(reg, dict):
            problems.append(f"{where}: must map to an object")
            continue
        state = reg.get("state", "active")
        if state not in ("active", "retired") or set(reg) - {"state", "tool"}:
            problems.append(f'{where}: takes only "tool" and a "state" of active or retired')
        elif state == "active" and not (isinstance(reg.get("tool"), str) and reg["tool"]):
            problems.append(f'{where}: an active id names its "tool"')
        registry[cid] = {"state": state, "tool": reg.get("tool")}

    keyed = {}
    for i, item in enumerate(entries):
        if not isinstance(item, dict):
            problems.append(f"{source}: entry {i}: must be an object")
            continue
        where = f"{source}: entry {i} ({item.get('check')} {locus(item)})"
        found = _shape_problems(item, ENTRY_FIELDS)
        for name in ("finding", "pass"):
            if name not in item:
                found.append(f'missing field "{name}"')
        finding = item.get("finding")
        if "finding" in item and not (isinstance(finding, str) and FINDING_ID.fullmatch(finding)):
            found.append(f'bad finding id "{finding}" (want PS, CS, DC, AW, or GA, a hyphen, '
                         "and digits)")
        if "pass" in item and item["pass"] not in PASS_LABELS:
            found.append(f'bad pass label "{item["pass"]}" (want one of {", ".join(PASS_LABELS)})')
        if (isinstance(finding, str) and finding.startswith("GA-")
                and not (isinstance(item.get("defect"), str) and item["defect"])):
            found.append('a GA id carries its one-line "defect"')
        if isinstance(item.get("check"), str) and item["check"] not in registry:
            found.append(f'unregistered check id "{item["check"]}"')
        if not found:
            k = key(item)
            if k in keyed:
                found.append("duplicates an earlier entry")
            keyed[k] = {**item, "count": item.get("count", 1)}
        problems.extend(f"{where}: {p}" for p in found)
    if problems:
        raise ConfigError(problems)
    return registry, keyed


def growth(head, new):
    """Return ``(check, message)`` for each way ``new`` grows past ``head``.

    ``head`` is None when HEAD holds no baseline, which counts every entry as new. A registry
    id retired in ``head`` may not return to active in ``new``, whether or not it carries
    entries.
    """
    new_checks, new_entries = new
    head_checks, head_entries = head or ({}, {})
    found = [(cid, f"registry is append-only: {cid} was removed")
             for cid in head_checks if cid not in new_checks]
    found += [(cid, f"registry is append-only: retired id {cid} returned to active")
              for cid in head_checks
              if cid in new_checks and head_checks[cid]["state"] == "retired"
              and new_checks[cid]["state"] != "retired"]
    removed = [e for k, e in head_entries.items() if k not in new_entries]
    for k, e in new_entries.items():
        cid = e["check"]
        head_state = head_checks.get(cid, {}).get("state")
        if "retired" in (head_state, new_checks[cid]["state"]):
            found.append((cid, f"retired id admits no entries: {locus(e)}"))
            continue
        old = head_entries.get(k)
        if old is not None:
            if e["count"] > old["count"]:
                found.append((cid, f"count rises: {locus(e)}: {old['count']} -> {e['count']}"))
            continue
        if head_state is None:
            continue
        partner = next((r for r in removed if "fingerprint" in r and "fingerprint" in e
                        and (r["check"], r.get("repo", ""), r["fingerprint"], r["count"])
                        == (cid, e.get("repo", ""), e["fingerprint"], e["count"])), None)
        if partner is not None:
            removed.remove(partner)
            continue
        found.append((cid, f"new entry under registered id: {locus(e)}"))
    return found


def _git(root, *args):
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True)


def read_git(root, rev):
    """Return the baseline text at ``rev`` (``HEAD`` or ``""`` for the index), or None."""
    if _git(root, "rev-parse", "--is-inside-work-tree").returncode != 0:
        raise ConfigError([f"{root}: not inside a git work tree"])
    if rev == "HEAD" and _git(root, "rev-parse", "--verify", "-q", "HEAD^{commit}").returncode:
        return None
    spec = f"{rev}:{BASELINE}"
    if _git(root, "cat-file", "-e", spec).returncode != 0:
        return None
    shown = _git(root, "show", spec)
    if shown.returncode != 0:
        raise ConfigError([f"git show {spec}: {shown.stderr.strip()}"])
    return shown.stdout


def run_tools(root, checks, root_flags):
    """Run each registered tool once; return its violations under the active ids.

    Raises ConfigError for a registered id no tool implements, a tool that fails or prints
    no report, a report whose "implements" or "violations" field is not shaped as documented,
    and a reported id or violation outside the active registry.
    """
    active = {cid: reg["tool"] for cid, reg in checks.items() if reg["state"] == "active"}
    by_tool = defaultdict(list)
    for cid, tool in active.items():
        by_tool[tool].append(cid)
    problems, violations = [], []
    for tool, ids in sorted(by_tool.items()):
        path = root / tool
        if not path.is_file():
            problems += [f'check id "{cid}": no tool implements it ({tool} not found)'
                         for cid in ids]
            continue
        try:
            proc = subprocess.run([str(path), "ratchet-report", "--root", str(root), *root_flags],
                                  capture_output=True, text=True)
            data = json.loads(proc.stdout) if proc.returncode == 0 else None
        except (OSError, json.JSONDecodeError) as err:
            problems.append(f"{tool}: no ratchet report ({err})")
            continue
        if data is None:
            problems.append(f"{tool}: ratchet-report exited {proc.returncode}: "
                            f"{proc.stderr.strip()}")
            continue
        if not isinstance(data, dict):
            problems.append(f"{tool}: the ratchet report must be an object")
            continue
        implements_raw = data.get("implements", [])
        if not isinstance(implements_raw, list) or not all(
                isinstance(cid, str) for cid in implements_raw):
            problems.append(f'{tool}: "implements" must be a list of strings')
            continue
        violations_raw = data.get("violations", [])
        if not isinstance(violations_raw, list):
            problems.append(f'{tool}: "violations" must be a list')
            continue
        implements = set(implements_raw)
        problems += [f'check id "{cid}": no tool implements it ({tool} does not report it)'
                     for cid in ids if cid not in implements]
        problems += [f'{tool}: implements "{cid}", which the registry does not list as active'
                     for cid in sorted(implements - set(active))]
        for v in violations_raw:
            shape = (_shape_problems(v, ENTRY_FIELDS - {"finding", "pass", "defect"})
                     if isinstance(v, dict) else ["not an object"])
            if not shape and v["check"] not in implements:
                shape = [f'check "{v["check"]}" is not one it implements']
            if shape:
                problems.append(f"{tool}: violation {v!r}: {shape[0]}")
            else:
                violations.append(v)
    if problems:
        raise ConfigError(problems)
    return violations


def match(entries, checks, violations):
    """Return ``(check, message)`` for each mismatch between violations and entries."""
    observed = Counter()
    sample = {}
    for v in violations:
        k = key(v)
        observed[k] += v.get("count", 1)
        sample.setdefault(k, v)
    found = []
    for k, n in observed.items():
        e = entries.get(k)
        if e is None:
            found.append((k[0], f"new violation: {locus(sample[k])}"))
        elif n > e["count"]:
            found.append((k[0], f"count rose above the baseline: {locus(e)}: {e['count']} -> {n}"))
        elif n < e["count"]:
            found.append((k[0], f"lower this baseline entry's count to {n}: {locus(e)}"))
    for k, e in entries.items():
        if k not in observed and checks[e["check"]]["state"] == "active":
            found.append((k[0], f"remove this baseline entry: {locus(e)} "
                                f"({e['finding']}, pass {e['pass']})"))
    return found


def report(found, title):
    """Print every violation grouped by check with a count per check; return the exit code."""
    if not found:
        return 0
    groups = defaultdict(list)
    for cid, message in found:
        groups[cid].append(message)
    print(f"{title}: {len(found)} violations in {len(groups)} checks")
    for cid in sorted(groups):
        print(f"{cid}: {len(groups[cid])}")
        for message in groups[cid]:
            print(f"  {message}")
    return 1


def cmd_hook(root):
    """Compare the staged baseline with HEAD's copy."""
    staged = read_git(root, "")
    if staged is None:
        raise ConfigError([f"staged baseline absent: {BASELINE}"])
    new = parse(staged, f"{BASELINE} (staged)")
    head_text = read_git(root, "HEAD")
    head = None if head_text is None else parse(head_text, f"{BASELINE} (HEAD)")
    return report(growth(head, new), "ratchet (pre-commit)")


def cmd_check(root, root_flags):
    """Match the working tree's violations to its baseline, then apply growth against HEAD."""
    path = root / BASELINE
    if not path.is_file():
        raise ConfigError([f"baseline absent: {path}"])
    new = parse(path.read_text(), BASELINE)
    head_text = read_git(root, "HEAD")
    head = None if head_text is None else parse(head_text, f"{BASELINE} (HEAD)")
    violations = run_tools(root, new[0], root_flags)
    found = match(new[1], new[0], violations)
    found += [(cid, f"working tree vs HEAD: {m}") for cid, m in growth(head, new)]
    return report(found, "ratchet")


def main(argv=None):
    """Run the hook or check mode; return the exit code."""
    parser = argparse.ArgumentParser(prog="ratchet", description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="mode", required=True)
    hook = sub.add_parser("hook", help="compare the staged baseline with HEAD")
    check = sub.add_parser("check", help="run the tools and match the working-tree baseline")
    for p in (hook, check):
        p.add_argument("--root", default=".", help="repository root (default: .)")
    for flag in ("--home", "--projects-root", "--memory-root"):
        check.add_argument(flag, help="forwarded to each tool")
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()
    try:
        if args.mode == "hook":
            return cmd_hook(root)
        flags = []
        for name in ("home", "projects_root", "memory_root"):
            value = getattr(args, name)
            if value is not None:
                flags += ["--" + name.replace("_", "-"), value]
        return cmd_check(root, flags)
    except ConfigError as err:
        print("ratchet: configuration error", file=sys.stderr)
        for problem in err.problems:
            print(f"  {problem}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
