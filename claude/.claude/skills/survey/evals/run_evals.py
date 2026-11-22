#!/usr/bin/env -S python3 -I
"""Run one evaluation of evals.json in a fresh Claude Code session and save its evidence.

Adapted from the runner in the workstation's building-from-specs skill. The workstation loads a
released copy of this skill as a user skill, and a user skill wins over a project skill of the
same name. So the session sets `skillOverrides` to turn the user's `survey` off in both states,
and denies reads of every other copy on disk. With `--state on`, the session also loads this
branch's copy through `--plugin-dir`, from a one-skill plugin named `survey`, where it lists as
`survey:survey`. With `--state off`, it loads no copy at all. The raw stream stays in the scratch
folder. The evidence file keeps the query, the skills the session loaded, and its final answer.

Clear the whole scratch root before each round: this script clears only its own session's folder.
It removes the plugin when its session ends, so a later session never finds a stale copy there.
"""

import argparse
import hashlib
import json
import shutil
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
SKILL = SKILL_DIR.name
PLUGIN_SKILL = f"{SKILL}:{SKILL}"
MODELS = {"haiku": "claude-haiku-5-5", "sonnet": "claude-sonnet-5-5", "opus": "claude-opus-5-5"}


def build(root, case, state):
    """Build an empty project holding the case's files, and the one-skill plugin when it is on."""
    if root.exists():
        shutil.rmtree(root)
    proj = root / "project"
    proj.mkdir(parents=True)
    for name in case["files"]:
        shutil.copy(SKILL_DIR / name, proj / Path(name).name)
    if state == "off":
        return proj, None
    plugin = root / "plugin"
    (plugin / ".claude-plugin").mkdir(parents=True)
    manifest = {"name": SKILL, "version": "0.0.0", "description": "This branch's copy of the survey skill"}
    (plugin / ".claude-plugin/plugin.json").write_text(json.dumps(manifest) + "\n")
    shutil.copytree(SKILL_DIR, plugin / "skills" / SKILL, ignore=shutil.ignore_patterns("evals"))
    return proj, plugin


def settings(scratch, root):
    """Return the session's settings: the user's overrides with `survey` off, and the read denials.

    The denials cover the workstation's vendored copy, its link under ~/.claude/skills, and every
    copy under ~/Projects, which holds this repo's checkouts and the workstation's worktrees. They
    cover every other background job's folder that holds a `skills/survey` folder, even a partial
    one, and each such folder left in this job outside the session's folder `root`. They also
    cover the raw streams of earlier sessions in this round, which hold the skill's text, and the
    private survey-notes repo, whose corrections must stay out of this public repo's evidence.
    The read rules also stop Grep and Glob.
    """
    try:
        user = json.loads((Path.home() / ".claude/settings.json").read_text())
        merged = dict(user.get("skillOverrides", {}))
    except (OSError, ValueError):
        merged = {}
    merged[SKILL] = "off"
    homes = {str(Path.home()), str(Path.home().resolve())}
    globs = [".claude/skills/survey/**", ".dotfiles/**/skills/survey/**", "Projects/**/skills/survey/**",
             "Projects/survey-notes/**"]
    home = Path.home().resolve()
    jobs = home / ".claude/jobs"
    own = {p for p in scratch.resolve().parents if p.parent == jobs}
    for copy in jobs.glob(f"*/**/skills/{SKILL}"):
        job = jobs / copy.relative_to(jobs).parts[0]
        if job not in own:
            globs.append(f"{job.relative_to(home)}/**")
        elif not copy.is_relative_to(root.resolve()):
            globs.append(f"{copy.relative_to(home)}/**")
    deny = sorted({f"Read(/{home}/{g})" for home in homes for g in globs})
    deny.append(f"Read(/{scratch.resolve()}/*.jsonl)")
    return {"skillOverrides": merged, "permissions": {"deny": deny}}


def evidence(lines, plugin):
    """Pull the skill calls, the listing, the reads of any survey copy, and the final answer.

    The skill counts as loaded when the session calls Skill on `survey:survey` or reads the
    plugin copy's SKILL.md. A Read or Grep of any other copy is kept apart, in `otherCopyReads`,
    whether or not the denial stopped it.
    """
    invoked, read, other, listed, result, cost = [], False, [], [], "", None
    for line in lines:
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if event.get("type") == "system" and event.get("subtype") == "init":
            listed = [s for s in event.get("skills", []) if s.split(":")[-1] == SKILL]
        if event.get("type") == "assistant":
            for part in event.get("message", {}).get("content", []):
                if part.get("type") != "tool_use":
                    continue
                if part.get("name") == "Skill":
                    invoked.append(part.get("input", {}).get("skill", ""))
                if part.get("name") in ("Read", "Grep"):
                    tool_input = part.get("input", {})
                    path = tool_input.get("file_path") or tool_input.get("path") or ""
                    if f"skills/{SKILL}/" not in path.rstrip("/") + "/":
                        continue
                    if plugin and path.startswith(str(plugin)):
                        read = read or path.endswith("SKILL.md")
                    else:
                        other.append(path)
        if event.get("type") == "result":
            result = event.get("result", "")
            cost = event.get("total_cost_usd")
    loaded = read or PLUGIN_SKILL in invoked
    return {"listed": listed, "invoked": invoked, "readSkillFile": read, "otherCopyReads": other,
            "loaded": loaded, "result": result, "costUsd": cost}


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
    proj, plugin = build(args.scratch.resolve() / run_id, case, args.state)
    cmd = [
        "claude", "-p", case["query"],
        "--model", MODELS[args.model], "--effort", "medium",
        "--output-format", "stream-json", "--verbose",
        "--tools", "Read,Glob,Grep,Skill",
        "--settings", json.dumps(settings(args.scratch, proj.parent)),
        "--no-session-persistence",
    ]
    if plugin:
        cmd += ["--plugin-dir", str(plugin)]
    started = datetime.now(timezone.utc)
    clock = time.monotonic()
    run = subprocess.run(cmd, cwd=proj, capture_output=True, text=True, timeout=900)
    seconds = round(time.monotonic() - clock, 1)
    if plugin:
        shutil.rmtree(plugin)
    (args.scratch / f"{run_id}.jsonl").write_text(run.stdout)
    record = {
        "case": args.case,
        "model": MODELS[args.model],
        "skill": args.state,
        "query": case["query"],
        "skillSha256": hashlib.sha256((SKILL_DIR / "SKILL.md").read_bytes()).hexdigest(),
        "started": started.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "seconds": seconds,
        "exitCode": run.returncode,
        **evidence(run.stdout.splitlines(), plugin),
    }
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / f"{run_id}.json").write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n")
    keys = ("case", "model", "skill", "seconds", "exitCode", "listed", "loaded", "invoked", "otherCopyReads")
    print(json.dumps({k: record[k] for k in keys}))


if __name__ == "__main__":
    main()
