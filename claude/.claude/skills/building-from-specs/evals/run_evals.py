#!/usr/bin/env -S python3 -I
"""Run a skill's evaluations in fresh Claude Code sessions and save their evidence.

The runner has two modes. With `--case`, it runs one of the skill's original cases, which check
that a session loads the skill. With `--suite`, it lists, proves, runs, or summarizes a suite of
graded cases, such as `spec-writing`. `--summary` reads the folders a suite run wrote.

A session runs with `claude -p` in a scratch project, with `--setting-sources project,local`, so
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

A `--case` session can only read: it gets Read, Glob, Grep, and Skill, the write tools are
refused, and no MCP server loads, so a query can ask for a plan but nothing can carry one out.

A suite session runs on Fable at high in a git repo that the case's `fixture.sh` builds, with the
skill on. Its shell runs in Claude Code's sandbox, which hides the installed skill, the main
checkout, and the real denials log, and its file tools are held to the project by deny rules.
Each check is a pattern, a command, or a judge: one Sonnet session with no tools that answers
yes or no and must quote the text that supports a yes.
"""

import argparse
import hashlib
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

EVALS_DIR = Path(__file__).resolve().parent
SKILLS_DIR = EVALS_DIR.parent.parent
MODELS = {"haiku": "claude-haiku-5-5", "sonnet": "claude-sonnet-5-5", "opus": "claude-opus-5-5"}
BASE_DIR = re.compile(r"Base directory for this skill: (\S+)")

FABLE = "claude-fable-5-2"
JUDGE = MODELS["sonnet"]
GUIDE = "references/writing-a-spec.md"
READER_BRIEF = "references/reader-brief.md"
# The flags each kind of suite session gets, from the spec's table of settings.
KINDS = {
    "write": {"tools": "Read,Glob,Grep,Skill,Bash,Edit(./**),Agent", "cap": 6.0, "limit": 1800},
    "read": {"tools": "Bash,Read,Glob,Grep", "cap": 2.0, "limit": 900},
}
MAX_WORDS = 1200
# Held back from the cap for the judge calls that grade one session.
JUDGE_RESERVE = 0.05
JUDGE_SYSTEM = (
    "You grade one document. Answer the question about it with yes or no. For a yes, quote the "
    "words of the document that support it, copied exactly, and no more than two sentences. "
    "For a no, give an empty quote. Answer from the document alone."
)
JUDGE_SCHEMA = {
    "type": "object",
    "properties": {"answer": {"enum": ["yes", "no"]}, "quote": {"type": "string"}},
    "required": ["answer", "quote"],
}
PROBE_PROMPT = ("This is a test of the shell sandbox. Run exactly this one command with the Bash tool, "
                "once, then reply with its output: echo probe > {target}")


# ---------------------------------------------------------------------------- the original cases

def project(scratch, skill_dir, case, state):
    """Build a project that holds the case's files, the other skills, and the skill when it is on."""
    if scratch.exists():
        shutil.rmtree(scratch)
    scratch.mkdir(parents=True)
    copy_skills(scratch, skill_dir, state == "on")
    for name in case["files"]:
        shutil.copy(skill_dir / name, scratch / Path(name).name)


def copy_skills(scratch, skill_dir, with_skill):
    """Copy every skill, the one under test only when wanted, and the user's CLAUDE.md into scratch."""
    skills = scratch / ".claude/skills"
    skills.mkdir(parents=True)
    for other in sorted(SKILLS_DIR.iterdir()):
        if (other / "SKILL.md").is_file() and (other != skill_dir or with_skill):
            shutil.copytree(other, skills / other.name, ignore=shutil.ignore_patterns("evals"))
    user_memory = Path.home() / ".claude/CLAUDE.md"
    if user_memory.is_file():
        shutil.copy(user_memory, scratch / "CLAUDE.md")


def user_settings():
    try:
        return json.loads((Path.home() / ".claude/settings.json").read_text())
    except (OSError, ValueError):
        return {}


def settings(skill, state, proj):
    """Return the session's settings: the user's skillOverrides and plugins, plus this skill when off.

    Deny rules keep the session from reading any copy of the skill outside the project, such as the
    main checkout's, so a load can come only from the project. They also refuse a Read of any
    SKILL.md in the project, so a load goes through the Skill tool, as it would for a user skill
    that sits outside the folder a session searches. A skill's supporting files stay readable.
    """
    user = user_settings()
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


def run_case(args):
    """Run one original case, as `--case` always has."""
    skill_dir = SKILLS_DIR / args.skill
    cases = json.loads((skill_dir / "evals/evals.json").read_text())
    if not 1 <= args.case <= len(cases):
        sys.exit(f"error: --case must be from 1 to {len(cases)}")
    case = cases[args.case - 1]
    if "suite" in case:
        sys.exit(f"error: case {args.case} belongs to the {case['suite']} suite; run it with --suite")
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


# ---------------------------------------------------------------------------- suites

def suite_cases(skill_dir, suite):
    cases = [c for c in json.loads((skill_dir / "evals/evals.json").read_text()) if c.get("suite") == suite]
    if not cases:
        sys.exit(f"error: evals.json has no case in the {suite} suite")
    return cases


def pick(cases, only):
    if not only:
        return cases
    unknown = sorted(set(only) - {c["name"] for c in cases})
    if unknown:
        sys.exit(f"error: no such case: {', '.join(unknown)}")
    return [c for c in cases if c["name"] in only]


def suite_hash(skill_dir, suite):
    """Hash the runner, the suite's entries in evals.json, and every file of the suite's fixtures.

    A run records this hash, and `--summary` refuses a run whose hash no longer matches the tree,
    so a result always describes the cases as they stand.
    """
    h = hashlib.sha256()
    h.update(Path(__file__).resolve().read_bytes())
    cases = [c for c in json.loads((skill_dir / "evals/evals.json").read_text()) if c.get("suite") == suite]
    h.update(json.dumps(cases, sort_keys=True).encode())
    root = skill_dir / "evals/files" / suite
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        h.update(str(path.relative_to(root)).encode() + b"\0" + path.read_bytes())
    return h.hexdigest()


def blob_hash(text):
    """Return git's object id for text, so a hash can be checked with `git hash-object`."""
    data = text.encode()
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def build_fixture(skill_dir, case, dest):
    """Build the case's repo in dest, which must not exist yet, and return its commit."""
    dest.mkdir(parents=True)
    script = skill_dir / case["folder"] / "fixture.sh"
    subprocess.run(["bash", str(script), str(dest)], check=True, capture_output=True, text=True)
    return git(dest, "rev-parse", "HEAD")


def git(repo, *argv):
    return subprocess.run(["git", "-C", str(repo), *argv], check=True, capture_output=True, text=True).stdout.strip()


def reader_prompt(skill_dir, suite_dir):
    """Return the reader's prompt: the skill's reader brief when it has one, else the plugin's prompt."""
    brief = skill_dir / READER_BRIEF
    source = brief if brief.is_file() else suite_dir / "builder-check-prompt.md"
    text = source.read_text()
    fenced = re.search(r"^```\n(.*?)^```", text, re.S | re.M)
    if fenced:
        text = fenced.group(1)
    text = re.sub(r"\[DOMAIN[^\]]*\]", "software engineer", text)
    return text.replace("[DOCUMENT_PATH]", "spec.md").strip() + "\n"


def case_prompt(skill_dir, suite_dir, case):
    if case["kind"] == "write":
        return (suite_dir / "writing-prompt.md").read_text()
    return reader_prompt(skill_dir, suite_dir)


def hidden_paths():
    """List the paths a suite session's shell may not read, in each spelling of the home folder."""
    homes = {Path.home(), Path.home().resolve()}
    skill_link = Path.home() / ".claude/skills/building-from-specs"
    paths = {str(skill_link), str(skill_link.resolve())}
    for home in homes:
        paths.add(str(home / ".dotfiles"))
        paths.add(str(home / ".local/state/claude-denials.jsonl"))
    return sorted(paths)


def suite_settings(proj):
    """Return a suite session's settings: the plugins, the deny rules, and the sandbox.

    The sandbox holds only the shell, so the Read rules repeat its list for the file tools.
    """
    user = user_settings()
    deny = [f"Read(/{p}/**)" for p in hidden_paths()]
    deny.append(f"Read(/{proj.resolve()}/.claude/skills/*/SKILL.md)")
    return {
        "skillOverrides": user.get("skillOverrides", {}),
        "enabledPlugins": user.get("enabledPlugins", {}),
        "permissions": {"deny": deny},
        "sandbox": {"enabled": True, "failIfUnavailable": True, "allowUnsandboxedCommands": False,
                    "filesystem": {"denyRead": hidden_paths()}},
    }


def claude(cmd, cwd, limit, stdin=None):
    """Run a claude command, kill its whole process group at the time limit, and return what it wrote.

    Returns the exit code (None at the time limit), stdout, and the seconds it took.
    """
    clock = time.monotonic()
    proc = subprocess.Popen(cmd, cwd=cwd, stdin=subprocess.PIPE if stdin is not None else subprocess.DEVNULL,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, start_new_session=True)
    try:
        out, _ = proc.communicate(stdin, timeout=limit)
        code = proc.returncode
    except subprocess.TimeoutExpired:
        os.killpg(proc.pid, signal.SIGKILL)
        out, _ = proc.communicate()
        code = None
    return code, out or "", round(time.monotonic() - clock, 1)


def stream(lines):
    """Return the events of a stream-json run, skipping any line that is not JSON."""
    events = []
    for line in lines:
        try:
            events.append(json.loads(line))
        except ValueError:
            continue
    return events


def parts(events):
    """Yield each event with each content part of its message."""
    for event in events:
        message = event.get("message")
        content = message.get("content", []) if isinstance(message, dict) else []
        if isinstance(content, str):
            content = [{"type": "text", "text": content}]
        for part in content:
            if isinstance(part, dict):
                yield event, part


def ended(code, result):
    if code is None:
        return "time limit"
    if result is None:
        return "error"
    subtype = result.get("subtype", "")
    if "budget" in subtype:
        return "cost cap"
    if subtype == "success" and not result.get("is_error"):
        return "finished"
    return "error"


def session_record(events, code):
    """Pull how a suite session ended, its models, its calls, and its cost out of its stream."""
    init = next((e for e in events if e.get("type") == "system" and e.get("subtype") == "init"), {})
    result = next((e for e in reversed(events) if e.get("type") == "result"), None)
    calls = [{"name": p.get("name", ""), "input": json.dumps(p.get("input", {}))[:400]}
             for _, p in parts(events) if p.get("type") == "tool_use"]
    return {
        "ended": ended(code, result),
        "subtype": (result or {}).get("subtype"),
        "exitCode": code,
        "mainModel": init.get("model"),
        "models": sorted((result or {}).get("modelUsage", {})),
        "costUsd": (result or {}).get("total_cost_usd", 0) or 0,
        "turns": (result or {}).get("num_turns"),
        "permissionDenials": (result or {}).get("permission_denials", []),
        "toolCalls": calls,
        "result": (result or {}).get("result", ""),
    }


# ---------------------------------------------------------------------------- checks

def normalize(text):
    return " ".join(re.sub(r"[`*_]", "", text).split()).lower()


def quote_found(quote, text):
    """Return True when every piece of the quote, split at an ellipsis, appears in the text in order."""
    pieces = [normalize(p) for p in re.split(r"\.\.\.|…", quote)]
    pieces = [p for p in pieces if p]
    if not pieces:
        return False
    haystack, at = normalize(text), 0
    for piece in pieces:
        found = haystack.find(piece, at)
        if found < 0:
            return False
        at = found + len(piece)
    return True


def judge(question, text, cwd):
    """Ask the judge one yes-or-no question about text; return its answer, its quote, and the cost."""
    prompt = f"Question: {question}\n\nThe document:\n\n<document>\n{text}\n</document>\n"
    cmd = ["claude", "-p", "--model", JUDGE, "--effort", "low", "--tools", "", "--strict-mcp-config",
           "--setting-sources", "local", "--no-session-persistence", "--system-prompt", JUDGE_SYSTEM,
           "--json-schema", json.dumps(JUDGE_SCHEMA), "--output-format", "json"]
    code, out, _ = claude(cmd, cwd, 300, stdin=prompt)
    try:
        reply = json.loads(out)
    except ValueError:
        return {"answer": None, "quote": "", "cost": 0, "error": f"exit {code}: {out[:200]}"}
    answer = reply.get("structured_output") or {}
    return {"answer": answer.get("answer"), "quote": answer.get("quote", ""),
            "cost": reply.get("total_cost_usd", 0) or 0}


def trap_check(case, text, cwd):
    """Grade the trap: the pattern gate first, then the judge, whose quote must be in the text."""
    trap = case["trap"]
    if trap.get("pattern") and not re.search(trap["pattern"], text, re.I):
        return {"passed": False, "pattern": False, "answer": None, "quote": "", "quoteFound": None, "cost": 0}
    verdict = judge(trap["question"], text, cwd)
    found = quote_found(verdict["quote"], text) if verdict["answer"] == "yes" else None
    return {"passed": verdict["answer"] == "yes" and bool(found), "pattern": bool(trap.get("pattern")) or None,
            "answer": verdict["answer"], "quote": verdict["quote"], "quoteFound": found, "cost": verdict["cost"],
            **({"error": verdict["error"]} if "error" in verdict else {})}


def length_check(text):
    words = len(text.split())
    return {"passed": words <= MAX_WORDS, "words": words}


def built_check(proj, head):
    """Pass when spec.md is the only change in the repo and its commit is still the fixture's."""
    status = git(proj, "status", "--porcelain", "--untracked-files=all").splitlines()
    now = git(proj, "rev-parse", "HEAD")
    return {"passed": status == ["?? spec.md"] and now == head, "status": status, "headUnchanged": now == head}


def guide_check(events, proj):
    """Pass when the session read the project's copy of the guide and the read succeeded."""
    target = f".claude/skills/building-from-specs/{GUIDE}"
    results = {p.get("tool_use_id"): p for _, p in parts(events) if p.get("type") == "tool_result"}
    reads = []
    for _, part in parts(events):
        if part.get("type") != "tool_use" or part.get("name") not in ("Read", "Bash"):
            continue
        given = part.get("input", {})
        named = given.get("file_path", "") if part["name"] == "Read" else given.get("command", "")
        if target not in named:
            continue
        absolute = re.findall(r"(/\S*" + re.escape(target) + ")", named)
        inside = all(a.startswith(str(proj)) for a in absolute)
        failed = results.get(part.get("id"), {}).get("is_error", False)
        reads.append({"call": named[:200], "inside": inside, "failed": bool(failed)})
    return {"passed": any(r["inside"] and not r["failed"] for r in reads), "reads": reads}


def grade(case, text, events, proj, head, cwd):
    checks = {"trap": trap_check(case, text, cwd)}
    if case["kind"] == "write":
        checks["length"] = length_check(text)
        checks["built"] = built_check(proj, head)
        checks["guide"] = guide_check(events, proj)
    return checks


# ---------------------------------------------------------------------------- spending

class Budget:
    """Hold the run's spending under a total, reserving each session's cap before it starts."""

    def __init__(self, total):
        self.total, self.spent, self.held = total, 0.0, 0.0
        self.lock = threading.Lock()

    def reserve(self, amount):
        with self.lock:
            if self.total is not None and self.spent + self.held + amount > self.total:
                return False
            self.held += amount
            return True

    def settle(self, held, cost):
        with self.lock:
            self.held -= held
            self.spent += cost


# ---------------------------------------------------------------------------- suite commands

def cmd_list(cases):
    for case in cases:
        print(case["name"])


def cmd_check_graders(skill_dir, suite, cases, jobs, budget):
    """Prove every check on its samples and every fixture's trap; exit 1 on any wrong result."""
    suite_dir = skill_dir / "evals/files" / suite
    work = Path(tempfile.mkdtemp(prefix=f"{suite}-graders-"))
    empty = work / "judge"
    empty.mkdir()

    def one(case):
        folder = skill_dir / case["folder"]
        wrong, judged = [], 0
        for sample, want in (("pass.md", True), ("fail.md", False), ("near-miss.md", False)):
            text = (folder / "samples" / sample).read_text()
            for _ in range(2):
                if not budget.reserve(JUDGE_RESERVE):
                    return case, None, "the cost cap was reached"
                got = trap_check(case, text, empty)
                budget.settle(JUDGE_RESERVE, got["cost"])
                judged += got["answer"] is not None
                if got["passed"] != want:
                    wrong.append(f"{sample} graded {'pass' if got['passed'] else 'fail'}")
                if got["answer"] is None:
                    break  # The pattern gate decided, and it gives the same answer every time.
        counts = [f"trap 3 samples ({judged} judge answers)"]
        build = work / case["name"]
        head = build_fixture(skill_dir, case, build)
        if case["kind"] == "write":
            for sample, want in (("length-pass.md", True), ("length-fail.md", False)):
                if length_check((suite_dir / "samples" / sample).read_text())["passed"] != want:
                    wrong.append(f"{sample} graded wrong")
            for sample, want in (("built-pass.sh", True), ("built-fail.sh", False)):
                proj = work / f"{case['name']}-{sample}"
                build_fixture(skill_dir, case, proj)
                subprocess.run(["bash", str(suite_dir / "samples" / sample)], cwd=proj, check=True,
                               capture_output=True)
                if built_check(proj, head)["passed"] != want:
                    wrong.append(f"{sample} graded wrong")
            for sample, want in (("guide-read-pass.jsonl", True), ("guide-read-fail.jsonl", False)):
                raw = (suite_dir / "samples" / sample).read_text().replace("{project}", str(build))
                if guide_check(stream(raw.splitlines()), build)["passed"] != want:
                    wrong.append(f"{sample} graded wrong")
            counts += ["length 2", "built 2", "guide 2"]
        proof = subprocess.run(["bash", str(folder / "proof.sh"), str(build)], capture_output=True, text=True)
        trap = "fixture trap in place" if proof.returncode == 0 else "fixture trap MISSING"
        if proof.returncode != 0:
            wrong.append("the fixture's proof failed")
        return case, wrong, ", ".join(counts) + "; " + trap

    failed = False
    with ThreadPoolExecutor(max_workers=jobs) as pool:
        for case, wrong, detail in pool.map(one, cases):
            if wrong is None:
                print(f"STOP  {case['name']}  {detail}")
                failed = True
                continue
            failed |= bool(wrong)
            print(f"{'ok  ' if not wrong else 'FAIL'}  {case['name']}  {detail}"
                  + (f"  [{'; '.join(wrong)}]" if wrong else ""))
    shutil.rmtree(work, ignore_errors=True)
    print(f"judge cost ${budget.spent:.4f}")
    return 1 if failed else 0


def probe_sandbox(out, budget):
    """Run one cheap session that tries to write outside its folder; return True when it was refused."""
    root = Path(tempfile.mkdtemp(prefix="sandbox-probe-"))
    proj, outside = root / "project", root / "outside"
    proj.mkdir()
    outside.mkdir()
    target = outside / "written.txt"
    if not budget.reserve(0.5):
        print("the cost cap leaves nothing for the sandbox probe")
        return False
    cmd = ["claude", "-p", PROBE_PROMPT.format(target=target), "--model", JUDGE, "--effort", "low",
           "--permission-mode", "dontAsk", "--allowedTools", "Bash", "--max-budget-usd", "0.50",
           "--strict-mcp-config", "--setting-sources", "project,local", "--no-session-persistence",
           "--settings", json.dumps(suite_settings(proj)), "--output-format", "stream-json", "--verbose"]
    code, raw, seconds = claude(cmd, proj, 300)
    events = stream(raw.splitlines())
    record = session_record(events, code)
    budget.settle(0.5, record["costUsd"])
    attempted = any(p.get("type") == "tool_use" and p.get("name") == "Bash" and str(target) in json.dumps(p.get("input"))
                    for _, p in parts(events))
    refused = attempted and not target.exists()
    probe = {"target": str(target), "attempted": attempted, "written": target.exists(), "refused": refused,
             "seconds": seconds, **{k: record[k] for k in ("ended", "mainModel", "costUsd", "toolCalls", "result")}}
    (out / "probe.json").write_text(json.dumps(probe, indent=2, ensure_ascii=False) + "\n")
    shutil.rmtree(root, ignore_errors=True)
    print(f"sandbox probe: attempted {attempted}, written {probe['written']}, cost ${record['costUsd']:.4f}")
    return refused


def cmd_run(skill_dir, suite, cases, out, jobs, budget, scratch):
    """Run each case once on Fable, grade it, and write its evidence, spec or report, and stream."""
    suite_dir = skill_dir / "evals/files" / suite
    out.mkdir(parents=True, exist_ok=True)
    scratch.mkdir(parents=True, exist_ok=True)
    print(f"scratch folder: {scratch}")
    if not probe_sandbox(out, budget):
        print("stopped: the sandbox did not refuse a write outside the project")
        return 1
    digest = suite_hash(skill_dir, suite)
    guide_hash = blob_hash((skill_dir / GUIDE).read_text())

    def one(case):
        kind = KINDS[case["kind"]]
        hold = kind["cap"] + JUDGE_RESERVE
        if not budget.reserve(hold):
            return case["name"], "not run: the cost cap was reached"
        proj = scratch / case["name"]
        if proj.exists():
            shutil.rmtree(proj)
        head = build_fixture(skill_dir, case, proj)
        copy_skills(proj, skill_dir, True)
        prompt = case_prompt(skill_dir, suite_dir, case)
        cmd = ["claude", "-p", prompt, "--model", FABLE, "--effort", "high", "--permission-mode", "dontAsk",
               "--allowedTools", kind["tools"], "--disallowedTools", "mcp__plugin_cloudflare_cloudflare",
               "--max-budget-usd", f"{kind['cap']:.2f}", "--strict-mcp-config",
               "--setting-sources", "project,local", "--no-session-persistence",
               "--settings", json.dumps(suite_settings(proj)), "--output-format", "stream-json", "--verbose"]
        started = datetime.now(timezone.utc)
        code, raw, seconds = claude(cmd, proj, kind["limit"])
        (scratch / f"{case['name']}.jsonl").write_text(raw)
        events = stream(raw.splitlines())
        record = session_record(events, code)
        if case["kind"] == "write":
            spec = proj / "spec.md"
            text = spec.read_text() if spec.is_file() else ""
        else:
            text = record["result"] or ""
        checks = grade(case, text, events, proj, head, scratch)
        judge_cost = checks["trap"].pop("cost")
        budget.settle(hold, record["costUsd"] + judge_cost)
        evidence_file = {
            "case": case["name"], "kind": case["kind"], "suite": suite,
            "started": started.strftime("%Y-%m-%dT%H:%M:%SZ"), "seconds": seconds,
            "suiteHash": digest, "guideHash": guide_hash, "promptHash": blob_hash(prompt),
            "fixtureHead": head, "effort": "high", "sandbox": True, "costCapUsd": kind["cap"],
            "timeLimitSeconds": kind["limit"], "words": len(text.split()), "judgeCostUsd": judge_cost,
            "checks": checks, **record,
        }
        (out / f"{case['name']}.json").write_text(json.dumps(evidence_file, indent=2, ensure_ascii=False) + "\n")
        (out / f"{case['name']}.md").write_text(text)
        marks = " ".join(f"{k} {'pass' if v['passed'] else 'FAIL'}" for k, v in checks.items())
        return case["name"], f"{record['ended']}, {marks}, ${record['costUsd'] + judge_cost:.2f}"

    def guarded(case):
        # One broken case leaves no evidence file, which --summary reports, and the others still run.
        try:
            return one(case)
        except Exception as error:  # noqa: BLE001
            return case["name"], f"error: {error!r}"

    # Writing cases go first: they take longest, so two at once finish closer together.
    ordered = sorted(cases, key=lambda c: c["kind"] != "write")
    with ThreadPoolExecutor(max_workers=jobs) as pool:
        for name, line in pool.map(guarded, ordered):
            print(f"{name}  {line}", flush=True)
    print(f"total cost ${budget.spent:.2f}")
    return 0


def cmd_summary(skill_dir, folders, require_pass):
    """Print one row per session in each folder; exit 1 on a missing, unfinished, or stale run."""
    bad, failed_check = [], False
    for folder in folders:
        rows = {}
        for path in sorted(folder.glob("*.json")):
            if path.name == "probe.json":
                continue
            record = json.loads(path.read_text())
            rows[record["case"]] = record
        suites = {r["suite"] for r in rows.values()} or {"spec-writing"}
        if len(suites) != 1:
            bad.append(f"{folder}: holds more than one suite")
            continue
        suite = suites.pop()
        current = suite_hash(skill_dir, suite)
        print(f"{folder}")
        print(f"{'case':26} {'trap':5} {'len':5} {'built':5} {'guide':5} {'ended':10} {'models':40} "
              f"{'effort':6} {'sbox':4} {'guide':7} {'prompt':7} {'suite':6} {'words':>5} {'cost':>6}")
        for case in suite_cases(skill_dir, suite):
            record = rows.get(case["name"])
            if record is None:
                print(f"{case['name']:26} no row")
                bad.append(f"{case['name']}: no row in {folder}")
                continue
            marks = []
            for check in ("trap", "length", "built", "guide"):
                result = record["checks"].get(check)
                marks.append("-" if result is None else "pass" if result["passed"] else "fail")
                failed_check |= result is not None and not result["passed"]
            fresh = record["suiteHash"] == current
            cost = record["costUsd"] + record["judgeCostUsd"]
            print(f"{case['name']:26} {marks[0]:5} {marks[1]:5} {marks[2]:5} {marks[3]:5} {record['ended']:10} "
                  f"{','.join(record['models']):40} {record['effort']:6} {'on' if record['sandbox'] else 'off':4} "
                  f"{record['guideHash'][:7]:7} {record['promptHash'][:7] if case['kind'] == 'read' else '-':7} "
                  f"{'same' if fresh else 'STALE':6} {record['words']:>5} {cost:>6.2f}")
            if record["ended"] != "finished":
                bad.append(f"{case['name']}: ended {record['ended']}")
            if record["mainModel"] != FABLE:
                bad.append(f"{case['name']}: main model {record['mainModel']}")
            if not fresh:
                bad.append(f"{case['name']}: run before the runner, a case, or a fixture last changed")
    for line in bad:
        print(f"error: {line}")
    if require_pass and failed_check:
        print("error: a check failed")
    return 1 if bad or (require_pass and failed_check) else 0


# ---------------------------------------------------------------------------- command line

def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--skill", default="building-from-specs", help="skill folder beside this one")
    parser.add_argument("--case", type=int, help="1-based index into evals.json, for an original case")
    parser.add_argument("--model", choices=MODELS)
    parser.add_argument("--state", choices=("on", "off"))
    parser.add_argument("--scratch", type=Path, help="folder for the projects and raw streams")
    parser.add_argument("--out", type=Path, help="folder for the evidence files")
    parser.add_argument("--suite", help="a suite of graded cases in evals.json, such as spec-writing")
    parser.add_argument("--list", action="store_true", help="print the suite's cases")
    parser.add_argument("--check-graders", action="store_true", help="prove every check and fixture")
    parser.add_argument("--run", action="store_true", help="run the suite's cases and grade them")
    parser.add_argument("--only", action="append", help="a case to run or prove; repeat for more")
    parser.add_argument("--jobs", type=int, default=1, help="sessions at once")
    parser.add_argument("--max-total-usd", type=float, help="the most this command may spend")
    parser.add_argument("--summary", type=Path, nargs="+", help="run folders to summarize")
    parser.add_argument("--require-pass", action="store_true", help="with --summary, exit 1 on a failed check")
    args = parser.parse_args()
    skill_dir = SKILLS_DIR / args.skill

    if args.summary:
        sys.exit(cmd_summary(skill_dir, args.summary, args.require_pass))
    if args.suite:
        cases = pick(suite_cases(skill_dir, args.suite), args.only)
        budget = Budget(args.max_total_usd)
        if args.list:
            cmd_list(cases)
        elif args.check_graders:
            sys.exit(cmd_check_graders(skill_dir, args.suite, cases, args.jobs, budget))
        elif args.run:
            if not args.out:
                parser.error("--run needs --out")
            # Under /tmp the project has no ancestor CLAUDE.md, so the session reads only its copy.
            scratch = args.scratch or Path(tempfile.mkdtemp(prefix=f"{args.suite}-run-", dir="/tmp"))
            sys.exit(cmd_run(skill_dir, args.suite, cases, args.out, args.jobs, budget, scratch))
        else:
            parser.error("--suite needs --list, --check-graders, or --run")
        return
    missing = [f"--{name}" for name in ("case", "model", "state", "scratch", "out") if getattr(args, name) is None]
    if missing:
        parser.error(f"the following arguments are required: {', '.join(missing)}")
    run_case(args)


if __name__ == "__main__":
    main()
