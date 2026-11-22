#!/usr/bin/env -S python3 -I
"""Run one evaluation of evals.json in a fresh Claude Code session and save its evidence.

The session runs with `claude -p` in a scratch project. With `--state on`, the project's
`.claude/skills/` holds a copy of this skill (its evaluations left out), so the skill loads from
the branch under test. It is a copy because Glob does not follow a link, and a session that looks
for the file would miss it. With `--state off`, the project holds no copy and `skillOverrides`
sets the skill to "off". The raw stream stays in the scratch folder. The evidence file keeps the
query, the skills the session loaded, and its final answer.
"""

import argparse
import json
import shutil
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
SKILL = SKILL_DIR.name
MODELS = {"haiku": "claude-haiku-5-5", "sonnet": "claude-sonnet-5-5", "opus": "claude-opus-5-5"}


def project(scratch, case, state):
    """Build an empty project that holds the case's files, and a copy of the skill when it is on."""
    if scratch.exists():
        shutil.rmtree(scratch)
    (scratch / ".claude/skills").mkdir(parents=True)
    if state == "on":
        shutil.copytree(SKILL_DIR, scratch / ".claude/skills" / SKILL, ignore=shutil.ignore_patterns("evals"))
    for name in case["files"]:
        shutil.copy(SKILL_DIR / name, scratch / Path(name).name)


def overrides(state):
    """Return the session's skillOverrides: the user's own, plus this skill when it is off."""
    try:
        user = json.loads((Path.home() / ".claude/settings.json").read_text())
        merged = dict(user.get("skillOverrides", {}))
    except (OSError, ValueError):
        merged = {}
    if state == "off":
        merged[SKILL] = "off"
    return merged


def evidence(lines):
    """Pull the invoked skills, the listing, and the final answer out of a stream-json run.

    A skill counts as loaded when the session calls Skill on it or reads its SKILL.md.
    """
    invoked, read, listed, result, cost = [], False, None, "", None
    for line in lines:
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if event.get("type") == "system" and event.get("subtype") == "init":
            listed = any(s.split(":")[-1] == SKILL for s in event.get("skills", []))
        if event.get("type") == "assistant":
            for part in event.get("message", {}).get("content", []):
                if part.get("type") == "tool_use" and part.get("name") == "Skill":
                    invoked.append(part.get("input", {}).get("skill", ""))
                if part.get("type") == "tool_use" and part.get("name") == "Read":
                    path = part.get("input", {}).get("file_path", "")
                    read = read or path.endswith(f"skills/{SKILL}/SKILL.md")
        if event.get("type") == "result":
            result = event.get("result", "")
            cost = event.get("total_cost_usd")
    loaded = read or any(name.split(":")[-1] == SKILL for name in invoked)
    return {"listed": listed, "invoked": invoked, "readSkillFile": read, "loaded": loaded, "result": result, "costUsd": cost}


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--case", type=int, required=True, help="1-based index into evals.json")
    parser.add_argument("--model", choices=MODELS, required=True)
    parser.add_argument("--state", choices=("on", "off"), required=True)
    parser.add_argument("--scratch", type=Path, required=True, help="folder for the project and raw stream")
    parser.add_argument("--out", type=Path, required=True, help="folder for the evidence file")
    args = parser.parse_args()

    case = json.loads((SKILL_DIR / "evals/evals.json").read_text())[args.case - 1]
    run_id = f"{args.case}-{args.model}-{args.state}"
    proj = args.scratch / run_id
    project(proj, case, args.state)
    cmd = [
        "claude", "-p", case["query"],
        "--model", MODELS[args.model], "--effort", "medium",
        "--output-format", "stream-json", "--verbose",
        "--tools", "Read,Glob,Grep,Skill",
        "--settings", json.dumps({"skillOverrides": overrides(args.state)}),
        "--no-session-persistence",
    ]
    started = datetime.now(timezone.utc)
    clock = time.monotonic()
    run = subprocess.run(cmd, cwd=proj, capture_output=True, text=True, timeout=900)
    seconds = round(time.monotonic() - clock, 1)
    (args.scratch / f"{run_id}.jsonl").write_text(run.stdout)
    record = {
        "case": args.case,
        "model": MODELS[args.model],
        "skill": args.state,
        "query": case["query"],
        "started": started.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "seconds": seconds,
        "exitCode": run.returncode,
        **evidence(run.stdout.splitlines()),
    }
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / f"{run_id}.json").write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({k: record[k] for k in ("case", "model", "skill", "seconds", "exitCode", "listed", "loaded", "invoked", "readSkillFile")}))


if __name__ == "__main__":
    main()
