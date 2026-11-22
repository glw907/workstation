#!/usr/bin/env -S python3 -I
"""Run one evaluation of a skill's evals.json in a fresh Claude Code session and save its evidence.

The session runs with `claude -p` in a scratch project, with `--setting-sources project,local`, so
it loads no user skill from `~/.claude/skills`. Those are links into the main checkout, and a user
skill outranks a project skill of the same name, so the branch under test would lose to them. The
project stands in for the user scope instead. Its `.claude/skills/` holds a copy of every skill
beside the one under test, its CLAUDE.md is a copy of `~/.claude/CLAUDE.md`, and the session takes
the user's `skillOverrides` and `enabledPlugins` through `--settings`.

With `--state on`, the project also holds a copy of the skill under test (its evaluations left
out), so the skill loads from the branch. It is a copy because Glob does not follow a link, and a
session that looks for the file would miss it. With `--state off`, the project holds no copy and
`skillOverrides` sets the skill to "off". The raw stream stays in the scratch folder. The evidence
file keeps the query, the skills the session loaded, the folder each load came from, the tools it
was offered, each call with its input, and its final answer.

A session can only read: it gets Read, Glob, Grep, and Skill, the write tools are refused, and no
MCP server loads, so a query can ask for a plan but nothing can carry one out.
"""

import argparse
import json
import re
import shutil
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

SKILLS_DIR = Path(__file__).resolve().parent.parent.parent
MODELS = {"haiku": "claude-haiku-5-5", "sonnet": "claude-sonnet-5-5", "opus": "claude-opus-5-5"}
BASE_DIR = re.compile(r"Base directory for this skill: (\S+)")


def project(scratch, skill_dir, case, state):
    """Build a project that holds the case's files, the other skills, and the skill when it is on."""
    if scratch.exists():
        shutil.rmtree(scratch)
    skills = scratch / ".claude/skills"
    skills.mkdir(parents=True)
    for other in sorted(SKILLS_DIR.iterdir()):
        if (other / "SKILL.md").is_file() and (other != skill_dir or state == "on"):
            shutil.copytree(other, skills / other.name, ignore=shutil.ignore_patterns("evals"))
    user_memory = Path.home() / ".claude/CLAUDE.md"
    if user_memory.is_file():
        shutil.copy(user_memory, scratch / "CLAUDE.md")
    for name in case["files"]:
        shutil.copy(skill_dir / name, scratch / Path(name).name)


def settings(skill, state, proj):
    """Return the session's settings: the user's skillOverrides and plugins, plus this skill when off.

    Deny rules keep the session from reading any copy of the skill outside the project, such as the
    main checkout's, so a load can come only from the project. They also refuse a Read of any
    SKILL.md in the project, so a load goes through the Skill tool, as it would for a user skill
    that sits outside the folder a session searches. A skill's supporting files stay readable.
    """
    try:
        user = json.loads((Path.home() / ".claude/settings.json").read_text())
    except (OSError, ValueError):
        user = {}
    merged = dict(user.get("skillOverrides", {}))
    if state == "off":
        merged[skill] = "off"
    home = Path.home().resolve()
    deny = [f"Read(/{home}/.dotfiles/**/skills/{skill}/**)", f"Read(~/.claude/skills/{skill}/**)",
            f"Read(/{proj.resolve()}/.claude/skills/*/SKILL.md)"]
    return {"skillOverrides": merged, "enabledPlugins": user.get("enabledPlugins", {}),
            "permissions": {"deny": deny}}


def texts(part):
    """Join every string in a message part, at any depth, so a tool result's text is searchable."""
    if isinstance(part, str):
        return part
    if isinstance(part, dict):
        return "\n".join(texts(v) for v in part.values())
    if isinstance(part, list):
        return "\n".join(texts(v) for v in part)
    return ""


def evidence(lines, skill, query=""):
    """Pull the loads, the listing, the tools called, and the final answer out of a stream-json run.

    A skill counts as loaded when the session calls Skill on it, reads its SKILL.md, or receives
    its text, which the stream shows as its base directory line. A query that opens with the
    skill's slash command also counts when the session lists that command: in `-p` mode the CLI
    expands it before the model runs, and the stream does not echo the expanded text.
    """
    invoked, reads, listed, result, cost, tools, bases = [], [], None, "", None, [], []
    slash, offered, calls = False, [], []
    for line in lines:
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if event.get("type") == "system" and event.get("subtype") == "init":
            listed = any(s.split(":")[-1] == skill for s in event.get("skills", []))
            opens = query.split(maxsplit=1)[0] if query.strip() else ""
            slash = opens == f"/{skill}" and skill in event.get("slash_commands", [])
            offered = sorted(event.get("tools", []))
        message = event.get("message")
        content = message.get("content", []) if isinstance(message, dict) else []
        if isinstance(content, str):
            content = [{"type": "text", "text": content}]
        for part in content:
            if not isinstance(part, dict):
                continue
            if part.get("type") == "tool_use":
                tools.append(part.get("name", ""))
                # The input is kept so a reader can check each call for a write.
                calls.append({"name": part.get("name", ""), "input": json.dumps(part.get("input", {}))[:400]})
                if part.get("name") == "Skill":
                    invoked.append(part.get("input", {}).get("skill", ""))
                path = part.get("input", {}).get("file_path", "")
                if part.get("name") == "Read" and path.endswith(f"skills/{skill}/SKILL.md"):
                    reads.append(path)
            if event.get("type") == "user":
                bases += [b for b in BASE_DIR.findall(texts(part)) if b.rstrip("/").endswith(f"/{skill}")]
        if event.get("type") == "result":
            result = event.get("result", "")
            cost = event.get("total_cost_usd")
    loaded = bool(reads or bases or slash) or any(name.split(":")[-1] == skill for name in invoked)
    return {"listed": listed, "invoked": invoked, "readSkillFile": reads, "loadedFrom": sorted(set(bases)),
            "slashExpanded": slash,
            "loaded": loaded, "toolsOffered": offered, "toolsUsed": sorted(set(tools)), "toolCalls": calls,
            "result": result, "costUsd": cost}


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--skill", default="building-from-specs", help="skill folder beside this one")
    parser.add_argument("--case", type=int, required=True, help="1-based index into evals.json")
    parser.add_argument("--model", choices=MODELS, required=True)
    parser.add_argument("--state", choices=("on", "off"), required=True)
    parser.add_argument("--scratch", type=Path, required=True, help="folder for the project and raw stream")
    parser.add_argument("--out", type=Path, required=True, help="folder for the evidence file")
    args = parser.parse_args()

    skill_dir = SKILLS_DIR / args.skill
    case = json.loads((skill_dir / "evals/evals.json").read_text())[args.case - 1]
    run_id = f"{args.case}-{args.model}-{args.state}"
    proj = args.scratch / run_id
    project(proj, skill_dir, case, args.state)
    cmd = [
        "claude", "-p", case["query"],
        "--model", MODELS[args.model], "--effort", "medium",
        "--output-format", "stream-json", "--verbose",
        "--tools", "Read,Glob,Grep,Skill",
        # --tools alone let Bash through in one round, so the write tools are refused outright.
        # --strict-mcp-config drops the connectors but not a plugin's server, which is denied by name.
        "--disallowedTools", "Bash,Edit,Write,NotebookEdit,WebFetch,mcp__plugin_cloudflare_cloudflare",
        "--strict-mcp-config",
        "--setting-sources", "project,local",
        "--settings", json.dumps(settings(args.skill, args.state, proj)),
        "--no-session-persistence",
    ]
    started = datetime.now(timezone.utc)
    clock = time.monotonic()
    run = subprocess.run(cmd, cwd=proj, capture_output=True, text=True, timeout=900)
    seconds = round(time.monotonic() - clock, 1)
    (args.scratch / f"{run_id}.jsonl").write_text(run.stdout)
    record = {
        "skillName": args.skill,
        "case": args.case,
        "model": MODELS[args.model],
        "skill": args.state,
        "query": case["query"],
        "started": started.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "seconds": seconds,
        "exitCode": run.returncode,
        **evidence(run.stdout.splitlines(), args.skill, case["query"]),
    }
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / f"{run_id}.json").write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n")
    keys = ("case", "model", "skill", "seconds", "exitCode", "listed", "loaded", "invoked", "loadedFrom", "slashExpanded", "toolsUsed")
    print(json.dumps({k: record[k] for k in keys}))


if __name__ == "__main__":
    main()
