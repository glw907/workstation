# Prose Arm Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the prose arm's components without changing any live behavior: the missing editor register, a Microsoft end-user baseline fixture, the Vale PostToolUse feedback hook scoped to changed lines (built and proven, not yet wired), and the `prose-voice-reviewer` subagent. The cutover that flips these on is plan 07.

**Architecture:** The hook is a new Python script `vale-hook` at `~/.dotfiles/bin/.local/bin/`, modeled on `prose-guard`'s plumbing. It reads the PostToolUse JSON, acts only on Markdown prose files, finds the config root by walking up to the nearest `.vale.ini`, runs `vale --output=JSON` from there so the section globs match, and keeps only the findings on the lines the edit just changed. An error-tier finding exits 2 with the finding on stderr, the channel Claude reads back; warnings and suggestions ride along as `additionalContext`. It fails open. It is not wired into `settings.json`; `prose-guard` stays the active hook until plan 07. The registers, the Microsoft fixture, and the reviewer subagent are additive files that change no live behavior either.

**Tech Stack:** Vale 3.15.1 (errata-ai/vale) with the vendored Google and Microsoft packages and the `glw907` overlay, Python 3.12 (the hook and its pytest suite), the dotfiles repo's existing fixture runner, and a new agent definition.

## Global Constraints

- Vale is pinned to `3.15.1`; the binary is `~/.local/bin/vale`. The Google and Microsoft packages and the `glw907` overlay are already vendored under `~/.dotfiles/vale/.config/vale/styles` (plan 01).
- **This plan changes no live behavior.** It does not touch `settings.json`, the always-on `writing-voice` output style, the global CLAUDE.md, or `prose-voice.md`. It does not retire `prose-guard`, which stays the active prose hook. All of that is the cutover, plan 07. The Vale hook is built and proven here but left unwired.
- The hook acts on Markdown prose only (`.md`). Code comments are out of its scope: the comment arm (plans 02 through 05) runs its own Vale config against the comment scopes, and the prose hook must never double-cover a `.ts`, `.go`, `.py`, or `.svelte` file.
- The hook reports findings as factual statements, never imperatives. Text framed as a command can trip Claude's prompt-injection defenses, which surfaces it to the user instead of feeding it back as context. Phrase every report as "Vale found N issues", not "You must fix".
- Exit codes follow the verified PostToolUse contract: exit 2 puts stderr in front of Claude (must-fix); exit 0 with `hookSpecificOutput.additionalContext` adds advisory context (capped at 10,000 characters); any other non-zero is a non-blocking error the model never sees. The hook uses exit 2 for an error-tier finding, exit 0 plus `additionalContext` for advisory findings, and exit 0 for everything else, including every failure path (fail open).
- The `vale-hook` script is Python under `bin/.local/bin/`, so the plan-05 Python comment arm covers it: it must pass `bash scripts/check-py-comments.sh` (ruff `D` docstring correctness plus Vale on its comment prose).
- All changes commit to dotfiles `main` directly; there is no consumer branch. The dotfiles working tree carries two unrelated uncommitted files (`claude/.claude/settings.json`, `claude/.claude/skills/cairn-pass/SKILL.md`) left for Geoff. Do not touch them, and `git add` only the files each task names.
- Commit footer: `Co-Authored-By: Claude <noreply@anthropic.com>`.

## The plan series: what is in plan 06, and what plan 07 carries

This is plan 06 of the authoring-system build. Plans 01 through 05 (Vale foundation, the Go, TypeScript, Svelte, and Python comment arms) are done and pushed on dotfiles `main`.

The prose system has six layers in the spec (`2026-06-22-ai-drafting-prose-system-design.md`). Plan 06 builds the layers that do not change live behavior, and plan 07 flips the live ones in one coordinated cutover. The split is deliberate: the always-on output style, the global CLAUDE.md, the active `prose-guard` hook, and the router change what Claude does every turn, so they move together at cutover, not piecemeal.

**In plan 06 (this plan), nothing live changes:**

1. The editor register, the one missing feedforward file (the existing registers already lead on exemplars, so they need no restructuring).
2. A Microsoft end-user baseline fixture, proving the per-glob baseline path for the editor audience (Google docs and Microsoft copy are both vendored already).
3. The Vale PostToolUse hook, scoped to changed lines, built and proven against the real config and a pytest suite, but not wired into `settings.json`.
4. The `prose-voice-reviewer` subagent, the read-only second opinion (layer 6).
5. Record the prose arm as built in the charter, and point plan 07 at the cutover.

**Deferred to plan 07 (the cutover) or to per-repo sessions:**

- Wiring the hook in `settings.json`, proving the loop, and retiring `prose-guard` (spec steps 3 and 7).
- Rewriting the always-on output style and the global CLAUDE.md routing table, and building the `writing-voice` Skill that wraps the registers as the on-demand router (spec layers 1, 2, and 3's wrapper; the register content is built here).
- Repointing `prose-voice.md` (spec step 5).
- Wiring `/simplify` to name the TS, Svelte, and Python tells by number (comment-spec sequence step 5).

**Deferred deliberately, with reasons:**

- The reply and email registers. They encode Geoff's daily voice, and the em-dash matrix row for replies is his pending call, so they are their own calibration brainstorm in a later session, the way 907-life's personal-essay register is. The editor register ships here because the Microsoft end-user voice is a standard professional register, not Geoff's personal one.
- The built-in `Vale` spelling style and its accept/reject `Vocab`, and the Readability grade floor. Plan 01 routed these here, but a spelling check floods the advisory channel with every technical noun until the `Vocab` is curated against a real corpus, and the dotfiles repo has none. They land with the first real editor-doc application (cairn), where there is prose to tune against.
- The cairn application and the site applications (ECXC migrate, 907 define-then-wire), which run in their own repo sessions after the cutover.

The source specs are `~/.dotfiles/docs/superpowers/specs/2026-06-22-ai-drafting-prose-system-design.md` (prose) and `2026-06-22-code-comment-standards-design.md` (comments). The umbrella is `~/.claude/docs/authoring-charter.md`.

## Pilot findings carried into this plan

Proven against the installed binaries before the plan was written, the plan-03-through-05 discipline:

1. **The PostToolUse contract (verified against the current hooks reference).** For a PostToolUse hook, exit 2 feeds stderr back to Claude as an error message (the tool already ran, so it does not block), and on exit 2 stdout JSON is ignored. Exit 0 with `hookSpecificOutput.additionalContext` injects a system reminder next to the tool result, capped at 10,000 characters. Exit 1 (or any non-2 non-zero) is a non-blocking error the model never sees, so fail-open is exit 0, never exit 1. Findings must read as facts, not commands. The stdin payload uses `tool_input.file_path`, `tool_input.content` (Write), and `tool_input.new_string` (Edit).
2. **Vale matches a section glob against the path as given on the command line, relative to the working directory.** Run from the repo root, `vale docs/x.md` matches `[docs/**/*.md]`; run from `docs/` as `vale x.md`, or with an absolute path, the same file matches nothing. So the hook finds the config root (the nearest `.vale.ini`), runs Vale from there, and passes the file path relative to it. This is the load-bearing hook detail.
3. **Vale's JSON output carries `Line`, `Severity` (error, warning, suggestion), `Check`, and `Message` per finding.** The hook scopes by `Line` and tiers by `Severity`: error drives exit 2, warning and suggestion ride as advisory.
4. **Changed-line scoping works** (the prototype is in Task 3). A single-line edit scopes to that line and suppresses a pre-existing tell elsewhere; a multi-line insert scopes to its span; a Write or a not-found edit falls back to the whole file.
5. **The existing registers already use the spec's shape** (persona, then traits as the rule-card, then leading exemplars, then off-voice contrast as a secondary rubric). They need no restructuring; only the editor register is new.
6. **The Microsoft package fires on end-user copy** (`Microsoft.Wordiness` on "utilize" and "in order to", `Microsoft.Vocab` on "allow"), all at advisory level. So Microsoft style rides as advisory in the hook while `glw907`'s error tier drives the exit-2.

---

### Task 1: The editor register

Add the one missing register, the end-user and editor voice on the Microsoft baseline. It follows the same shape as the existing registers: persona, traits, leading exemplars, off-voice contrast. (The content below is shown inside a tilde fence so its own backtick code blocks nest cleanly; copy the inner Markdown verbatim into the file.)

**Files:**
- Create: `~/.dotfiles/claude/.claude/docs/voice/editor.md`

**Interfaces:**
- Produces: the editor register, the feedforward reference for end-user and editor-facing documentation that the router points at in plan 07.

- [ ] **Step 1: Write the failing check**

```bash
test -f ~/.dotfiles/claude/.claude/docs/voice/editor.md && echo PASS || echo FAIL
```

Expected: `FAIL`.

- [ ] **Step 2: Create the register**

Write `~/.dotfiles/claude/.claude/docs/voice/editor.md` with exactly this content:

~~~markdown
# Register: end-user and editor documentation

The reader is a non-technical person using the software to get a job done: an editor saving a
post, someone following a setup guide, a first-time user who has never seen the admin. They did
not read the code and do not want to. The persona is a calm, plain-spoken guide standing next to
the reader: second person, one step at a time, warm without being chatty. The baseline is the
Microsoft Writing Style Guide (warm and relaxed, plain words, short sentences, the reader in
charge). As Geoff drafts real editor guides in this register and edits them, his passages replace
the placeholders here and the corpus rebuilds on those.

The em dash is discouraged here by default. This is a deliberately plain, warm voice, and the
character reads as formal. End the sentence, or use a comma.

## Traits

- Second person, present tense, active voice. "You save the post", not "the post is saved".
- One idea per sentence, and short sentences. A reader anxious about breaking something reads
  slowly.
- Plain words over precise jargon. "Sign in", not "authenticate". When a technical term cannot be
  avoided, define it in the same breath.
- Lead with the task and the outcome, not the mechanism. The reader wants to know what to do and
  what will happen, not how it works inside.
- Reassure at the point of worry. If a step looks risky, say plainly what is safe.
- No marketing. The reader is already here, so nothing needs selling.

## Exemplars

A task instruction, second person and one step at a time:

```
To publish your changes, select Publish. Your post goes live within a minute, and the earlier
version stays in your history in case you want it back.
```

What happens, stated plainly with the worry addressed:

```
Saving keeps your work on a private copy, so nothing you do here touches the live site until you
publish. You can save as often as you like.
```

A recovery instruction, calm and concrete:

```
If you see "someone else changed this page", the page was edited somewhere else while you were
working. Open it again, redo your change, and save. Your text stays on this screen until you do.
```

A concept for a non-technical reader, defined with a plain analogy:

```
A draft is your private workspace. Think of it as a document you have not emailed yet. You can
change it freely, and no one else sees it until you decide to send it.
```

## Off-voice contrast

The same content in the register this file exists to prevent (jargon, passive voice, and selling):

```
cairn-cms empowers content creators with a seamless, intuitive publishing experience. Leveraging
a robust version-control backend, your content is committed to the repository upon initiation of
the publish workflow, ensuring enterprise-grade reliability.
```
~~~

- [ ] **Step 3: Re-run the check and confirm shape**

```bash
E=~/.dotfiles/claude/.claude/docs/voice/editor.md
test -f "$E" && echo PASS || echo FAIL
grep -qE '^## Traits|^## Exemplars|^## Off-voice contrast' "$E" && echo "SHAPE OK" || echo "MISSING"
```

Expected: `PASS` and `SHAPE OK`.

- [ ] **Step 4: Lint the register clean and commit**

```bash
cd ~/.dotfiles
vale --minAlertLevel=error claude/.claude/docs/voice/editor.md | tail -2
git add claude/.claude/docs/voice/editor.md
git commit -m "Add the editor register for the prose arm" \
  -m "The end-user and editor voice on the Microsoft baseline: persona, traits, leading exemplars, off-voice contrast. The reply and email registers stay deferred to their own calibration." \
  -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```

Expected: a clean or advisory-only Vale run, then the commit. The register file is under the `[claude/.claude/**/*.md]` glob, so `glw907` lints its prose; a real tell is a fix before committing. The off-voice contrast block carries marketing words on purpose (it shows the voice to avoid); those sit inside a fenced code block, which Vale and the `prose-guard` hook both skip, so the file lints clean.

---

### Task 2: The Microsoft end-user baseline fixture

Prove the Microsoft baseline fires on end-user copy and stays a permanent regression guard, mirroring the comment-scope fixture from plan 01. The fixture lives in a subdirectory so the runner's top-level `*.bad.*` and `*.good.*` loops (which assume a `glw907.<Rule>` name) skip it, and a dedicated assertion checks it through a Microsoft config.

**Files:**
- Create: `~/.dotfiles/vale/tests/fixtures/microsoft/copy.md`
- Create: `~/.dotfiles/vale/tests/microsoft.vale.ini`
- Modify: `~/.dotfiles/vale/tests/run-fixtures.sh`

**Interfaces:**
- Consumes: the Microsoft package vendored in plan 01, the pinned Vale binary.
- Produces: a runner that fails if the Microsoft baseline stops resolving or stops firing on end-user copy.

- [ ] **Step 1: Add the fixture and its config**

```bash
mkdir -p ~/.dotfiles/vale/tests/fixtures/microsoft
printf 'Please utilize the application in order to accomplish your objectives.\n' \
  > ~/.dotfiles/vale/tests/fixtures/microsoft/copy.md
```

Create `~/.dotfiles/vale/tests/microsoft.vale.ini`:

```ini
StylesPath = ../.config/vale/styles
MinAlertLevel = suggestion

[*.md]
BasedOnStyles = Microsoft
```

- [ ] **Step 2: Add a Microsoft assertion to the runner**

In `~/.dotfiles/vale/tests/run-fixtures.sh`, add this block after the comment-scope block (after line 40, before the final summary line `[ "$fail" -eq 0 ] && echo "fixtures: OK" ...`):

```bash
# Microsoft baseline: the end-user package must resolve and fire on wordy copy.
ms="fixtures/microsoft/copy.md"
ms_out="$(vale --config=microsoft.vale.ini --output=line "$ms")"
if ! grep -q 'Microsoft.Wordiness' <<<"$ms_out"; then
  echo "FAIL: $ms did not raise Microsoft.Wordiness; the Microsoft baseline may not be vendored"; fail=1
fi
```

- [ ] **Step 3: Run the runner and confirm the new assertion passes**

```bash
cd ~/.dotfiles/vale/tests && bash run-fixtures.sh
```

Expected: `fixtures: OK`. The fixture raises `Microsoft.Wordiness` on "utilize" and "in order to". If it prints a Microsoft FAIL, the package did not sync; run `vale sync` from `~/.config/vale` and retry.

- [ ] **Step 4: Commit**

```bash
cd ~/.dotfiles
git add vale/tests/fixtures/microsoft/copy.md vale/tests/microsoft.vale.ini vale/tests/run-fixtures.sh
git commit -m "Cover the Microsoft end-user baseline in the Vale fixture suite" \
  -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 3: The Vale prose hook

Build `vale-hook`, the PostToolUse feedback hook. It lints a saved Markdown file, scopes the findings to the lines the edit just changed, exits 2 with an error-tier finding on stderr, and rides warnings as `additionalContext`. It fails open everywhere. It is not wired into `settings.json`; `prose-guard` stays the active hook until plan 07.

**Files:**
- Create: `~/.dotfiles/bin/.local/bin/vale-hook`
- Create: `~/.dotfiles/tests/test_vale_hook.py`

**Interfaces:**
- Consumes: the pinned Vale binary, a repo's in-tree `.vale.ini` (resolved by walking up from the file).
- Produces: `vale-hook` reading a PostToolUse payload on stdin and reporting Vale findings on the changed lines: `new_text(tool_name, tool_input)`, `changed_span(saved, inserted)`, `config_root(start_dir)`, `run_vale(root, rel_path)`, `kept_findings(report, span)`, `main()`.

- [ ] **Step 1: Write the failing test**

Create `~/.dotfiles/tests/test_vale_hook.py` with exactly this content:

```python
"""Tests for the vale-hook PostToolUse prose feedback hook."""
import importlib.machinery
import importlib.util
import io
import json
import pathlib
import shutil

import pytest

TOOL = pathlib.Path(__file__).resolve().parent.parent / "bin" / ".local" / "bin" / "vale-hook"
STYLES = pathlib.Path.home() / ".dotfiles" / "vale" / ".config" / "vale" / "styles"
EM_DASH = "—"


def _load():
    loader = importlib.machinery.SourceFileLoader("vale_hook", str(TOOL))
    spec = importlib.util.spec_from_loader("vale_hook", loader)
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod


vh = _load()


def test_changed_span_single_line():
    assert vh.changed_span("a\nWe delve here\nc\n", "We delve here") == {2}


def test_changed_span_multiline():
    assert vh.changed_span("a\nb1\nb2\nd\n", "b1\nb2") == {2, 3}


def test_changed_span_write_scopes_whole_file():
    assert vh.changed_span("a\nb\nc\n", "") == {1, 2, 3, 4}


def test_changed_span_absent_falls_back():
    assert vh.changed_span("a\nb\nc\n", "not here") == {1, 2, 3, 4}


def test_new_text_reads_edit_and_write():
    assert vh.new_text("Edit", {"new_string": "x"}) == "x"
    assert vh.new_text("Write", {"content": "y"}) == "y"


def test_config_root_finds_nearest(tmp_path):
    (tmp_path / ".vale.ini").write_text("StylesPath = x\n")
    sub = tmp_path / "a" / "b"
    sub.mkdir(parents=True)
    assert vh.config_root(str(sub)) == str(tmp_path)


def test_non_markdown_is_skipped(tmp_path, monkeypatch):
    payload = {"tool_name": "Edit",
               "tool_input": {"file_path": str(tmp_path / "x.ts"), "new_string": "x"}}
    monkeypatch.setattr("sys.stdin", io.StringIO(json.dumps(payload)))
    assert vh.main() == 0


def _write_config(tmp_path):
    (tmp_path / ".vale.ini").write_text(
        f"StylesPath = {STYLES}\nMinAlertLevel = suggestion\n[*.md]\nBasedOnStyles = glw907\n"
    )


needs_vale = pytest.mark.skipif(
    shutil.which("vale") is None or not STYLES.exists(),
    reason="vale or the glw907 styles are unavailable",
)


@needs_vale
def test_main_error_tier_exits_2(tmp_path, monkeypatch, capsys):
    _write_config(tmp_path)
    doc = tmp_path / "doc.md"
    doc.write_text(f"Clean opening line.\nA seamless tapestry {EM_DASH} here.\nClean closing line.\n")
    payload = {"tool_name": "Edit", "tool_input": {
        "file_path": str(doc), "new_string": f"A seamless tapestry {EM_DASH} here."}}
    monkeypatch.setattr("sys.stdin", io.StringIO(json.dumps(payload)))
    code = vh.main()
    captured = capsys.readouterr()
    assert code == 2
    assert "seamless" in captured.err


@needs_vale
def test_main_clean_edit_suppresses_pre_existing(tmp_path, monkeypatch, capsys):
    _write_config(tmp_path)
    doc = tmp_path / "doc.md"
    doc.write_text(f"Clean opening line.\nA seamless tapestry {EM_DASH} here.\nClean closing line.\n")
    payload = {"tool_name": "Edit", "tool_input": {
        "file_path": str(doc), "new_string": "Clean opening line."}}
    monkeypatch.setattr("sys.stdin", io.StringIO(json.dumps(payload)))
    code = vh.main()
    captured = capsys.readouterr()
    assert code == 0
    assert captured.out == ""
```

- [ ] **Step 2: Run the test to verify it fails**

```bash
cd ~/.dotfiles && python3 -m pytest tests/test_vale_hook.py -q
```

Expected: a collection error or failure, because `bin/.local/bin/vale-hook` does not exist yet.

- [ ] **Step 3: Write the hook**

Create `~/.dotfiles/bin/.local/bin/vale-hook` with exactly this content:

```python
#!/usr/bin/env python3
"""Vale PostToolUse feedback hook for Claude-drafted prose.

Run Vale on a saved Markdown file after a Write or Edit, scope the findings to the
lines that just changed, and report them to Claude. An error-tier finding exits 2
with the finding on stderr, the channel Claude reads back, so Claude can self-correct.
Warnings and suggestions ride along as advisory additionalContext. The hook never
blocks a write (the tool has already run) and fails open: any internal problem, a
missing Vale, or a file under no .vale.ini exits 0 in silence.

Not wired into settings.json yet; prose-guard stays the active hook until the cutover
plan. Invoke by piping the PostToolUse JSON on stdin.
"""
import json
import os
import subprocess
import sys

CHAR_CAP = 9000  # stay under Claude Code's 10,000-character additionalContext cap


def new_text(tool_name, tool_input):
    """Return the text a Write or Edit just introduced, for changed-line scoping."""
    if tool_name == "Write":
        return tool_input.get("content", "")
    if tool_name == "Edit":
        return tool_input.get("new_string", "")
    if tool_name == "MultiEdit":
        return "\n".join(e.get("new_string", "") for e in tool_input.get("edits", []))
    return ""


def changed_span(saved, inserted):
    """Return the 1-based line numbers inserted occupies in saved.

    Fall back to every line when inserted is empty, absent, or repeats past a small
    cap (a replace_all), so the hook surfaces a finding rather than missing one.
    """
    whole = set(range(1, saved.count("\n") + 2))
    if not inserted:
        return whole
    span = set()
    start = 0
    hits = 0
    while True:
        idx = saved.find(inserted, start)
        if idx == -1:
            break
        hits += 1
        if hits > 5:
            return whole
        first = saved.count("\n", 0, idx) + 1
        span.update(range(first, first + inserted.count("\n") + 1))
        start = idx + max(1, len(inserted))
    return span or whole


def config_root(start_dir):
    """Return the nearest ancestor directory holding a .vale.ini, or None."""
    current = os.path.abspath(start_dir)
    while True:
        if os.path.exists(os.path.join(current, ".vale.ini")):
            return current
        parent = os.path.dirname(current)
        if parent == current:
            return None
        current = parent


def run_vale(root, rel_path):
    """Return Vale's parsed JSON for rel_path linted from root, or None on failure.

    Vale matches a section glob against the path as given relative to the working
    directory, so the file is linted from its config root by its relative path. Vale
    exits non-zero when it finds something and still writes its JSON to stdout, so the
    exit code is ignored.
    """
    try:
        proc = subprocess.run(
            ["vale", "--output=JSON", rel_path],
            cwd=root, capture_output=True, text=True, check=False,
        )
    except (OSError, ValueError):
        return None
    try:
        return json.loads(proc.stdout or "{}")
    except json.JSONDecodeError:
        return None


def kept_findings(report, span):
    """Return the findings whose line falls in span."""
    return [item for items in report.values() for item in items if item.get("Line") in span]


def _format(findings, path):
    """Return a factual, line-listed report of findings, capped for the hook."""
    rows = [
        f'  {path}:{f.get("Line")} {f.get("Check")} ({f.get("Severity")}): {f.get("Message")}'
        for f in findings
    ]
    return "\n".join(rows)[:CHAR_CAP]


def main():
    """Read the PostToolUse payload, lint the changed lines, report the findings."""
    try:
        data = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, ValueError):
        return 0
    tool_input = data.get("tool_input", {})
    path = tool_input.get("file_path", "")
    if not path.endswith(".md"):
        return 0  # prose hook: Markdown only; code comments are the comment arm's
    try:
        with open(path, encoding="utf-8") as handle:
            saved = handle.read()
    except (OSError, UnicodeDecodeError):
        return 0
    root = config_root(os.path.dirname(path))
    if root is None:
        return 0  # no .vale.ini up the tree: no declared audience, nothing to say
    report = run_vale(root, os.path.relpath(os.path.abspath(path), root))
    if report is None:
        return 0  # Vale missing or its output unreadable: fail open
    findings = kept_findings(report, changed_span(saved, new_text(data.get("tool_name", ""), tool_input)))
    if not findings:
        return 0
    body = _format(findings, path)
    if any(f.get("Severity") == "error" for f in findings):
        sys.stderr.write(
            f"Vale found {len(findings)} issue(s) on the lines just edited in {path}.\n"
            f"{body}\n"
            "These are facts from the Vale check on the changed lines; pre-existing text "
            "was not scanned.\n"
        )
        return 2
    note = (
        f"Vale advisory: {len(findings)} style finding(s) on the lines just edited in {path}. "
        "Nothing is blocked; revise if these sit in prose just written.\n"
    )
    sys.stdout.write(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PostToolUse",
        "additionalContext": note + body,
    }}))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:  # noqa: BLE001 - fail open: a hook crash must never disrupt the session
        sys.exit(0)
```

- [ ] **Step 4: Make it executable and run the test to verify it passes**

```bash
cd ~/.dotfiles
chmod +x bin/.local/bin/vale-hook
python3 -m pytest tests/test_vale_hook.py -q
```

Expected: all tests pass (the two `needs_vale` integration tests run, since Vale and the styles are present). If they skip, Vale or the styles path is wrong.

- [ ] **Step 5: Prove the hook end to end against the real dotfiles config**

```bash
cd ~/.dotfiles
emdash="$(printf '\xe2\x80\x94')"
printf 'A clean opening line here.\nA seamless tapestry %s built for the test.\nA clean closing line.\n' "$emdash" > docs/_hookproof.md
echo "-- A) edit the tell line -> exit 2 + stderr --"
printf '{"tool_name":"Edit","tool_input":{"file_path":"%s/docs/_hookproof.md","new_string":"A seamless tapestry %s built for the test."}}' "$PWD" "$emdash" | vale-hook; echo "[exit: $?]"
echo "-- B) edit the clean first line -> exit 0 silent (pre-existing tell suppressed) --"
printf '{"tool_name":"Edit","tool_input":{"file_path":"%s/docs/_hookproof.md","new_string":"A clean opening line here."}}' "$PWD" | vale-hook; echo "[exit: $?]"
rm -f docs/_hookproof.md
```

Expected: A prints the em-dash and slop findings on stderr and `[exit: 2]`; B prints nothing and `[exit: 0]`, because the line-2 tell is pre-existing and the edit touched only line 1. `vale-hook` resolves on the PATH through the stow symlink; if not, run `cd ~/.dotfiles && stow -R bin` first.

- [ ] **Step 6: Run the Python comment-arm gate on the new script**

```bash
cd ~/.dotfiles
bash scripts/check-py-comments.sh
echo "exit: $?"
```

Expected: `check:py-comments OK`, exit 0. The hook's docstrings pass ruff's `D` correctness rules and its comment prose passes Vale. A `D` or Vale finding is a fix before committing.

- [ ] **Step 7: Commit**

```bash
cd ~/.dotfiles
git add bin/.local/bin/vale-hook tests/test_vale_hook.py
git commit -m "Add the vale-hook PostToolUse prose feedback hook (unwired)" \
  -m "Lints a saved Markdown file, scopes findings to the changed lines, exits 2 with an error-tier finding on stderr, rides warnings as additionalContext, and fails open. Not wired into settings.json; prose-guard stays active until the cutover plan." \
  -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 4: The prose-voice-reviewer subagent

Add the read-only second-opinion reviewer (layer 6), forked from the reviewer-agent template, pinned to a strong model, bounded to register fit and tells so it does not nitpick. (The content is shown in a tilde fence; copy the inner Markdown into the file.)

**Files:**
- Create: `~/.dotfiles/claude/.claude/agents/prose-voice-reviewer.md`

**Interfaces:**
- Produces: the `prose-voice-reviewer` agent, invoked on a substantial prose artifact after the Vale floor passes and before a human read.

- [ ] **Step 1: Write the failing check**

```bash
test -f ~/.dotfiles/claude/.claude/agents/prose-voice-reviewer.md && echo PASS || echo FAIL
```

Expected: `FAIL`.

- [ ] **Step 2: Create the agent**

Write `~/.dotfiles/claude/.claude/agents/prose-voice-reviewer.md` with exactly this content:

~~~markdown
---
name: prose-voice-reviewer
description: Reviews Claude-drafted prose (docs, plans, specs, site content) against its register and the workstation tell catalogue. Use on a substantial prose artifact after the Vale floor passes and before a human read. Read-only.
tools: Read, Grep, Glob
model: claude-opus-4-8
effort: high
color: purple
---

You review Claude-drafted prose for register fit and AI-writing tells. You are read-only: you find
and explain problems, you do not edit files. You judge the result, not the reasoning that produced
it, which is what the fresh context buys.

Start by naming the artifact's audience and opening its register. The routing table is in
`~/.claude/docs/prose-voice.md`, and the registers are in `~/.claude/docs/voice/`. Read the
register's persona, traits, and exemplars before you judge a single sentence. A tell is usually a
register misapplied, so the register is your standard, not a generic notion of good writing.

Then read the artifact and flag two things only:

- Register violations: a sentence that breaks the named register's persona or traits, named against
  the exemplar it should have resembled.
- AI-writing tells: the habits in the writing-voice standard, including the em dash in a docs-tier
  file, the "it's not X, it's Y" contrast frame, the setup-colon payoff, the reflexive three-item
  list, the participial or connector opener, marketing and filler words, and flat cadence from
  uniform sentence length.

Treat style preferences as optional. If a choice is defensible within the register, leave it. You
are not a copy editor running up a score; you catch what a careful reader would call machine-written.

Report findings grouped as **Blocker** (a tell the standard bans outright, or a clear register
break), **Warning** (a probable tell worth a rewrite), and **Suggestion** (a lighter touch), each
with a `file:line` reference and a concrete rewrite in the register's voice. If a category is empty,
say so. End with a one-line verdict: does this read as written by the register's plausible human
author?
~~~

- [ ] **Step 3: Re-run the check and confirm the frontmatter**

```bash
A=~/.dotfiles/claude/.claude/agents/prose-voice-reviewer.md
test -f "$A" && echo PASS || echo FAIL
grep -qE '^name: prose-voice-reviewer' "$A" && grep -qE '^tools: Read, Grep, Glob' "$A" && echo "FRONTMATTER OK" || echo "MISSING"
```

Expected: `PASS` and `FRONTMATTER OK`.

- [ ] **Step 4: Lint clean and commit**

```bash
cd ~/.dotfiles
vale --minAlertLevel=error claude/.claude/agents/prose-voice-reviewer.md | tail -2
git add claude/.claude/agents/prose-voice-reviewer.md
git commit -m "Add the prose-voice-reviewer subagent for the prose arm" \
  -m "A read-only second opinion bounded to register fit and tells, pinned to Opus, for a substantial artifact after the Vale floor." \
  -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```

Expected: a clean or advisory-only Vale run, then the commit.

---

### Task 5: Record the prose arm as built, and point plan 07 at the cutover

**Files:**
- Modify: `~/.dotfiles/claude/.claude/docs/authoring-charter.md` (the build-state bullet)

**Interfaces:**
- Consumes: everything above.
- Produces: a charter that names the prose arm's built components and the cutover that remains, so plan 07 has an accurate starting point.

- [ ] **Step 1: Update the charter build-state bullet**

In `~/.dotfiles/claude/.claude/docs/authoring-charter.md`, find the bullet that records the four comment arms as live (the one ending "The prose arm is the next plan."). Replace "The prose arm is the next plan." with this text:

```markdown
The prose arm's components are built and unwired: the editor register joins the existing
registers, the Vale `vale-hook` lints a saved Markdown file and scopes findings to the changed
lines (exit 2 on an error-tier finding, advisory `additionalContext` otherwise, fail open), a
Microsoft fixture guards the end-user baseline, and the `prose-voice-reviewer` subagent gives the
read-only second opinion. The cutover is the next plan: wire the hook in `settings.json`, rewrite
the always-on output style and the global CLAUDE.md, build the `writing-voice` Skill router, retire
`prose-guard`, and repoint `prose-voice.md`.
```

- [ ] **Step 2: Lint clean and commit the charter**

```bash
cd ~/.dotfiles
vale --minAlertLevel=error claude/.claude/docs/authoring-charter.md | tail -2
git add claude/.claude/docs/authoring-charter.md
git commit -m "Record the prose arm's built components in the charter" \
  -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```

- [ ] **Step 3: Confirm nothing live moved**

```bash
cd ~/.dotfiles
git status --short
grep -rn 'vale-hook' claude/.claude/settings.json || echo "settings.json does not mention vale-hook (correct: the hook stays unwired)"
```

Expected: `git status` shows only the two pre-existing untouched files (`claude/.claude/settings.json`, `claude/.claude/skills/cairn-pass/SKILL.md`), and `settings.json` does not reference `vale-hook`. The hook is built but not wired; `prose-guard` is still the active hook.

---

## Self-Review

Run after the last task.

1. **Editor register present:** `claude/.claude/docs/voice/editor.md` carries the persona, traits, leading exemplars, and off-voice contrast (Task 1).
2. **Microsoft baseline proven:** the fixture raises `Microsoft.Wordiness`, and the runner guards it (Task 2).
3. **Hook scopes and tiers correctly:** the pytest suite passes, and the end-to-end proof shows exit 2 with an error-tier finding on the edited line and exit 0 silent when the edit touches a clean line while a pre-existing tell sits elsewhere (Task 3).
4. **Hook fails open and is Markdown-only:** a non-`.md` path, a file under no `.vale.ini`, and a missing Vale all return 0; the `__main__` guard swallows any exception to 0 (Task 3).
5. **Hook passes the Python arm:** `scripts/check-py-comments.sh` is green on the new script (Task 3 Step 6).
6. **Reviewer present:** the `prose-voice-reviewer` agent is read-only (`Read, Grep, Glob`), Opus-pinned, and bounded to register fit and tells (Task 4).
7. **Charter accurate:** the build-state bullet names the built components and the cutover that remains (Task 5).
8. **Nothing live moved:** `settings.json`, the output style, the global CLAUDE.md, `prose-voice.md`, and `prose-guard` are all untouched; the two pre-existing uncommitted files are left for Geoff; the reply and email registers, the built-in `Vale` spelling style with its `Vocab`, and Readability are deferred with reasons (Task 5 Step 3).
````