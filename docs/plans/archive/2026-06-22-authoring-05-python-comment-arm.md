# Python Comment Arm Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Bring Python comments under the charter. A `ruff` `D` config lints docstring correctness, Vale's `py = md` scope lints the comment and docstring prose for the em dash and the banned lexicon, a `check-py-comments.sh` runner ties both over the repo's real Python, and a new `python-conventions` skill plus a new `python-comments` register carry the T-P1 through T-P13 semantic tells. Proven against the workstation's own bin scripts.

**Architecture:** The workstation's Python is small scripts in `~/.local/bin` (canonical `~/.dotfiles/bin/.local/bin/`), plus the dotfiles test suite. Layer 1 is `ruff` with the pydocstyle `D` rules under the google convention, configured at the dotfiles repo root in `ruff.toml`. Layer 2 is Vale: the global and in-tree configs already map `py = md`, so a `[*.py]` section in the dotfiles `.vale.ini` points Python comment prose at the `glw907` overlay. Layer 3 is the `python-conventions` skill and the `python-comments` register. A `scripts/check-py-comments.sh` runner makes the deterministic layers runnable as a unit: `ruff` lints every tracked Python file, including the extensionless bin scripts by explicit path, and Vale lints the `.py` files. No consumer repo adopts this arm; the dotfiles repo is itself the home of the configs and the proving ground.

**Tech Stack:** `ruff` 0.15.18 (pinned via pipx), Vale 3.15.1 (errata-ai/vale), the hand-written `glw907` Vale style canonical in this repo, bash, and a new `python-conventions` skill plus a new `python-comments` register.

## Global Constraints

- `ruff` is installed via `pipx` and pinned to `0.15.18`; the binary is `~/.local/bin/ruff`. Bump deliberately, the same way the Vale pin is handled.
- Vale is pinned to `3.15.1`; the binary is `~/.local/bin/vale`. The em dash stays banned in Python comments; no opt-out section is added.
- The canonical `glw907` style lives at `~/.dotfiles/vale/.config/vale/styles/glw907`. The dotfiles in-tree `.vale.ini` already resolves it through `StylesPath = vale/.config/vale/styles`. This arm adds no vendoring: the dotfiles repo owns the canonical style.
- **Presence is Claude's gate, not ruff's. The whole `D100` through `D107` missing-docstring family is ignored.** This is the load-bearing pilot finding for this arm. The charter's central rule holds presence advisory and scoped to the public API, with Claude's write-time gate owning whether a comment exists at all. The cairn TypeScript arm implemented "advisory" as `jsdoc/require-jsdoc` at `warn`, because ESLint has a warn tier. `ruff` has no per-rule warn tier: a selected rule is a hard error. Keeping `D103` selected forces a docstring on every public function, which manufactures the reflexive docstrings T-P1 and T-P2 exist to remove (the pilot found three such forced cases in `prose-guard` alone, on `main` and `main_sweep`). So presence rules are not selected, and `ruff` enforces docstring *correctness* only. This resolves the tension between the spec's enumerated ignore list (which named only `D100`, `D104`, `D105`, `D107`) and the charter's "presence stays at warn and scoped to exports" decision: the faithful port of "stays at warn" into a linter with no warn tier is "not an error", which means not selected.
- The `ruff` `D` config keeps the docstring-correctness rules (`D200`, `D205`, `D212`, `D402`, `D403`, `D415`, `D419`, and the rest the google convention leaves on), re-enables `D401` for imperative mood (the google convention drops it), and excludes tests via `per-file-ignores`, since a test name is its own documentation.
- Vale's `py = md` format reaches `.py` files only; its format detection is keyed on the extension. The extensionless bin scripts (`prose-guard` today, and any future shebang-only script) get the `ruff` layer by explicit path but not the Vale lexical pass. This is a documented limit, not a gap to paper over with an extractor: `prose-guard` is the only such script and it retires in the cutover plan, and a future Python script earns the full net by carrying a `.py` extension. The Svelte arm built an extractor because Vale's `html` format was fundamentally broken for comments; Vale's `py` format is not, so no extractor is built here.
- This plan does not touch `prose-guard`'s behavior or its hook wiring. `prose-guard` stays the active prose hook until the cutover plan (07).
- All changes commit to dotfiles `main` directly; there is no consumer branch. The dotfiles working tree already carries two unrelated uncommitted files (`claude/.claude/settings.json`, `claude/.claude/skills/cairn-pass/SKILL.md`) left for Geoff. Do not touch them, and `git add` only the specific files each task names, never `git add -A` or a whole package directory.
- Commit footer: `Co-Authored-By: Claude <noreply@anthropic.com>`.

## The plan series

This is plan 05 of the authoring-system build. Plans 01 (Vale foundation), 02 (Go arm), 03 (TypeScript arm), and 04 (Svelte arm) are done and committed on dotfiles `main`; poplar carries the Go arm and cairn carries the TypeScript and Svelte arms.

1. **Vale foundation** (done).
2. **Go comment arm** (done): poplar.
3. **TypeScript comment arm** (done): cairn.
4. **Svelte comment arm** (done): cairn.
5. **Python comment arm** (this plan): the `ruff` `D` config, the `py` Vale scope, the `check-py-comments.sh` runner, the `python-conventions` skill, the `python-comments` register, the T-P1 through T-P13 catalogue. Prove against the dotfiles bin scripts.
6. **Prose arm:** the Google and Microsoft baselines on docs and content per glob, the prose registers, the PostToolUse prose Vale hook.
7. **Cutover:** wire the Vale hook, retire `prose-guard`, rewrite the output style and the CLAUDE.md writing-voice section, repoint the router. Sequence step 5 (wire `/simplify` to name TS, S, and T-P tells by number) lands here.

The source specs are `~/.dotfiles/docs/superpowers/specs/2026-06-22-ai-drafting-prose-system-design.md` (prose) and `~/.dotfiles/docs/superpowers/specs/2026-06-22-code-comment-standards-design.md` (comments). The umbrella is `~/.claude/docs/authoring-charter.md`.

## Pilot findings carried into this plan

These were proven against the installed binaries before the plan was written, settling the spec's verification flags:

1. **`ruff` 0.15.18 fires `D417`.** The reported non-firing bug (astral-sh/ruff #16477) is fixed on this version. `D417` flagged a missing argument description under `convention = "google"`. The spec's flag resolves green; no workaround is needed.
2. **Vale `py = md` scopes to `#` comments and `"""` docstrings on 3.15.1.** A planted slop word and an em dash in a docstring and a `#` comment both fired; the code identifiers on the `def` and `return` lines stayed clean.
3. **An extensionless Python script defeats Vale's `py` scope.** With no `.py` extension Vale cannot detect the format, so it scans the whole file as prose and flags code identifiers. This drives the documented limit above.
4. **`ruff` lints an extensionless script by explicit path.** `ruff check bin/.local/bin/prose-guard` applied the `D` rules. So the `ruff` layer covers the bin scripts the Vale layer cannot.
5. **`convention = "google"` suppresses the `D203`/`D211` and `D212`/`D213` incompatibility warnings**, and `extend-select = ["D401]"` re-enables imperative-mood checking. `per-file-ignores` of `tests/**` excludes the test suite from the `D` rules. `ruff.toml` at the repo root is discovered by walking up from each file, so no `--config` flag is needed in the runner.

---

### Task 1: The `ruff` `D` docstring config

Install and pin `ruff`, then add `ruff.toml` at the dotfiles repo root with the `D` config. Prove the four behaviors that matter: `D417` fires, `D401` re-enables, the presence family is silent, and tests are excluded.

**Files:**
- Create: `~/.dotfiles/ruff.toml`

**Interfaces:**
- Produces: a `~/.local/bin/ruff` reporting `0.15.18`, and a repo-root `ruff.toml` that the runner in Task 3 and the skill in Task 4 both reference. Running `ruff check <python-file>` from the repo root applies the `D` config by config discovery.

- [ ] **Step 1: Install and pin ruff via pipx**

```bash
pipx install 'ruff==0.15.18'
export PATH="$HOME/.local/bin:$PATH"; hash -r
ruff --version
```

Expected: `ruff 0.15.18`. If `pipx` reports it already installed at a different version, run `pipx install --force 'ruff==0.15.18'`.

- [ ] **Step 2: Write the failing check**

```bash
test -f ~/.dotfiles/ruff.toml && echo PASS || echo FAIL
```

Expected: `FAIL`.

- [ ] **Step 3: Create the config**

Write `~/.dotfiles/ruff.toml` with exactly this content:

```toml
# Docstring linting for the workstation's Python scripts (the charter's Python comment arm).
# PEP 257 baseline, Google-style sections used sparingly, terse one-liners the default. Only the
# D (pydocstyle) rules run here; this is the comment arm, not a full lint config. ruff enforces
# docstring CORRECTNESS, never PRESENCE: the whole D100-D107 missing-docstring family is ignored,
# because ruff has no warn tier and the charter holds presence as Claude's write-time gate, not a
# hard block. Forcing a docstring on every public symbol manufactures the reflexive docstrings
# T-P1 and T-P2 exist to remove.
[lint]
select = ["D"]
ignore = ["D100", "D101", "D102", "D103", "D104", "D105", "D106", "D107"]
extend-select = ["D401"]

[lint.pydocstyle]
convention = "google"

[lint.per-file-ignores]
"tests/**" = ["D"]
```

- [ ] **Step 4: Prove D417 and D401 fire on a planted function**

```bash
cd ~/.dotfiles
d="$(mktemp -d)"
printf 'def add(a: int, b: int) -> int:\n    """returns the sum of a and b\n\n    Args:\n        a: the first number.\n    """\n    return a + b\n' > "$d/sample.py"
ruff check --config ruff.toml --select D401,D417 "$d/sample.py"; echo "exit: $?"
rm -rf "$d"
```

Expected: `D417 Missing argument description in the docstring for \`add\`: \`b\`` and `D401 First line of docstring should be in imperative mood: "returns the sum of a and b"`, exit `1`. Both rules are load-bearing: `D417` is the bug the spec flagged (fixed here), `D401` is the re-enabled imperative-mood check.

- [ ] **Step 5: Prove the presence family is silent and tests are excluded**

```bash
cd ~/.dotfiles
echo "-- bin script: presence ignored, so no D103 --"
ruff check ruff.toml >/dev/null 2>&1  # warm config discovery
ruff check bin/.local/bin/prose-guard 2>&1 | grep -c 'D10[0-7]' | xargs -I{} echo "presence findings: {}"
echo "-- test file: per-file-ignores excludes D --"
ruff check tests/test_prose_guard.py; echo "test exit: $?"
echo "-- no incompatibility warnings --"
ruff check bin/.local/bin/prose-guard 2>&1 | grep -i 'incompatible' || echo "no incompatibility warnings"
```

Expected: `presence findings: 0` (the three `D103` cases the spec config would have raised are now silent), the test file reports `All checks passed!` with `test exit: 0`, and `no incompatibility warnings`. If any `D10x` appears, the ignore list is wrong; if the test file raises a `D` finding, the `per-file-ignores` glob is wrong.

- [ ] **Step 6: Commit**

```bash
cd ~/.dotfiles
git add ruff.toml
git commit -m "Add the ruff D docstring config for the Python comment arm" \
  -m "Enforces docstring correctness under the google convention with D401 re-enabled; ignores the D100-D107 presence family because ruff has no warn tier and presence is Claude's gate; excludes tests." \
  -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 2: The Vale `py` comment scope

The dotfiles `.vale.ini` already maps `py = md` under `[formats]`. Add a `[*.py]` section so Python comment and docstring prose runs through the `glw907` overlay, with `glw907.Judgment` demoted to advisory (it over-fires on legitimate technical vocabulary, the same call cairn's `.ts` and the Svelte extractor already make).

**Files:**
- Modify: `~/.dotfiles/.vale.ini`

**Interfaces:**
- Consumes: the `[formats] py = md` mapping already present, and the `glw907` style at `vale/.config/vale/styles`.
- Produces: a `[*.py]` audience section that lints the em dash and the banned lexicon in Python comments and docstrings, used by the runner in Task 3.

- [ ] **Step 1: Add the Python section**

In `~/.dotfiles/.vale.ini`, after the `[claude/.claude/**/*.md]` section, append:

```ini
# Python scripts and the test suite: the house overlay on comment and docstring prose. The
# py = md mapping above scopes Vale to # comments and """ docstrings on its own. Judgment is
# advisory here, as on cairn's .ts comments: it over-fires on legitimate technical vocabulary.
# The em dash stays banned (no opt-out). Vale's py scope reaches .py files only; the extensionless
# bin scripts get the ruff layer instead (see scripts/check-py-comments.sh).
[*.py]
BasedOnStyles = glw907
glw907.Judgment = suggestion
```

- [ ] **Step 2: Confirm the config parses and the section resolved**

```bash
cd ~/.dotfiles
vale ls-config >/dev/null 2>&1 && echo PARSED || echo FAIL
vale ls-config | grep -q '"\*\.py"' && echo "PY SECTION OK" || echo "PY SECTION MISSING"
```

Expected: `PARSED` (the config parses; `vale ls-config` exits non-zero on a malformed config) and `PY SECTION OK` (the `[*.py]` glob bound, which appears as a `"*.py"` key under `SBaseStyles`). Vale 3.15.1's `ls-config` JSON carries no literal `StylesPath` key, since the resolved style path lives under a `Paths` array; the section binding is the reliable signal that the new section took effect.

- [ ] **Step 3: Prove the scope fires on a comment and a docstring, not on code**

The planted file lands in the repo root, then gets removed. The em dash is written from its bytes so the literal stays out of the repo:

```bash
cd ~/.dotfiles
emdash="$(printf '\xe2\x80\x94')"
printf 'def utilize(seamless):\n    """A seamless tapestry of helpers %s built to delve."""\n    # we should leverage the synergy here\n    return seamless\n' "$emdash" > zzproof.py
vale --minAlertLevel=suggestion --output=line zzproof.py
rm -f zzproof.py
```

Expected: findings at `zzproof.py:2` (the docstring: `glw907.Slop` on `seamless` and `tapestry`, `glw907.EmDash`, `glw907.BannedPhrases` on `delve`) and `zzproof.py:3` (the `#` comment: `glw907.Judgment` on `leverage`, at `suggestion`), and NOTHING on line 1 (`def utilize(seamless)`) or line 4 (`return seamless`). The clean code lines prove the scope holds; the `delve` and em-dash findings prove the lexical net reaches the docstring.

- [ ] **Step 4: Prove the real test file lints clean at error level**

```bash
cd ~/.dotfiles
vale --minAlertLevel=error tests/test_prose_guard.py | tail -3
```

Expected: `0 errors`. The only real `.py` in the repo carries no em dash or banned word in its comments, so the error-level pass is clean. A real finding here is a genuine tell to clean in a separate commit, the same way the Go and Svelte arms cleaned pre-existing tells.

- [ ] **Step 5: Commit**

```bash
cd ~/.dotfiles
git add .vale.ini
git commit -m "Add the Vale py comment scope for the Python comment arm" \
  -m "A [*.py] section lints # comments and \"\"\" docstrings through glw907; Judgment is advisory, the em dash stays banned." \
  -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 3: The `check-py-comments.sh` runner

Tie the two deterministic layers into one runnable gate, mirroring poplar's `scripts/vale-comments.sh` and cairn's `scripts/check-comments.sh`. `ruff` lints every tracked Python file, including the extensionless bin scripts found by their python shebang; Vale lints the `.py` files. The runner discovers Python generically, so it survives `prose-guard`'s retirement without an edit.

**Files:**
- Create: `~/.dotfiles/scripts/check-py-comments.sh`

**Interfaces:**
- Consumes: `ruff.toml` from Task 1, the `[*.py]` Vale section from Task 2.
- Produces: `bash scripts/check-py-comments.sh` exits non-zero on a `ruff` `D` error or a Vale error in a Python comment, and is the repeatable proof against real bin Python.

- [ ] **Step 1: Write the failing check**

```bash
test -f ~/.dotfiles/scripts/check-py-comments.sh && echo PASS || echo FAIL
```

Expected: `FAIL`.

- [ ] **Step 2: Write the runner**

Create `~/.dotfiles/scripts/check-py-comments.sh` with exactly this content:

```bash
#!/usr/bin/env bash
# check-py-comments.sh: the Python comment gate for the dotfiles repo. Runs ruff's D (docstring)
# rules and Vale's lexical net over the repo's Python. ruff lints every tracked .py file and every
# extensionless bin script with a python shebang (passed by explicit path, which ruff accepts
# regardless of extension). Vale's py = md scope reaches .py files only, so the extensionless bin
# scripts get the ruff layer but not the Vale lexical pass; that is a known limit of Vale's
# extension-keyed format detection, documented in the Python comment-arm plan.
set -uo pipefail
cd "$(dirname "$0")/.." || exit 2

fail=0

# Tracked .py files, and extensionless bin scripts whose first line names python.
mapfile -t py_files < <(git ls-files -- '*.py')
bin_py=()
for f in bin/.local/bin/*; do
  [ -f "$f" ] || continue
  case "$f" in *.py) continue ;; esac   # .py already covered by py_files
  if head -1 "$f" | grep -qi 'python'; then bin_py+=("$f"); fi
done

echo "== ruff D (docstring) rules =="
if (( ${#py_files[@]} + ${#bin_py[@]} > 0 )); then
  ruff check "${py_files[@]}" "${bin_py[@]}" || fail=1
else
  echo "(no Python files)"
fi

echo "== vale on .py comment and docstring prose =="
if (( ${#py_files[@]} > 0 )); then
  vale --minAlertLevel=error "${py_files[@]}" || fail=1
else
  echo "(no .py files)"
fi

if [ "$fail" -eq 0 ]; then echo "check:py-comments OK"; else echo "check:py-comments FAILED"; fi
exit "$fail"
```

- [ ] **Step 3: Make it executable and run it green against real Python**

```bash
cd ~/.dotfiles
chmod +x scripts/check-py-comments.sh
bash scripts/check-py-comments.sh
echo "exit: $?"
```

Expected: the `ruff` block runs over `tests/test_prose_guard.py` and `bin/.local/bin/prose-guard`, the Vale block runs over `tests/test_prose_guard.py`, and it prints `check:py-comments OK`, exit `0`. The presence family is ignored, so `prose-guard`'s missing-docstring lines do not fail it. A `ruff` `D` correctness finding or a Vale error is a real tell to clean first.

- [ ] **Step 4: Prove the runner fails on a planted tell**

```bash
cd ~/.dotfiles
emdash="$(printf '\xe2\x80\x94')"
printf 'def helper(x: int) -> int:\n    """Double x %s for callers."""\n    return x * 2\n' "$emdash" > tests/zz_planted.py
git add tests/zz_planted.py   # the runner lints tracked files; stage so git ls-files finds it
bash scripts/check-py-comments.sh; echo "exit: $?"
git restore --staged tests/zz_planted.py
rm -f tests/zz_planted.py
```

Expected: the runner FAILS (exit `1`). The runner discovers Python through `git ls-files`, so the planted file is staged first to put it in front of the gate. Vale flags the em dash in the docstring. The `tests/**` `per-file-ignores` silences `ruff`'s `D` on this path, so the gate fails through the Vale arm. The cleanup unstages and removes the file, and the runner returns to green. Staging a throwaway file is the proof's own scaffolding; the runner is right to lint tracked files only, since a gate should not flag a stray scratch file in the working tree.

- [ ] **Step 5: Commit**

```bash
cd ~/.dotfiles
git add scripts/check-py-comments.sh
git commit -m "Add the check-py-comments runner for the Python comment arm" \
  -m "Runs ruff D rules over all tracked Python (including extensionless bin scripts by shebang) and Vale over the .py files; discovers Python generically so it survives prose-guard's retirement." \
  -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 4: The `python-conventions` skill

Create the layer-3 skill for Python, mirroring `ts-conventions` and `svelte-conventions`: the write-time gate, the docstring shape, the copy-in `ruff` config, and the T-P1 through T-P13 catalogue. The new `python-comments` register (Task 5) is the prose authority.

**Files:**
- Create: `~/.dotfiles/claude/.claude/skills/python-conventions/SKILL.md`

**Interfaces:**
- Produces: the `python-conventions` skill, carrying the §0 gate, the docstring shape, the `ruff` config, and the T-P catalogue the `/simplify` lens will cite by number in the cutover plan.

- [ ] **Step 1: Write the failing check**

```bash
test -f ~/.dotfiles/claude/.claude/skills/python-conventions/SKILL.md && echo PASS || echo FAIL
```

Expected: `FAIL`.

- [ ] **Step 2: Create the skill**

```bash
mkdir -p ~/.dotfiles/claude/.claude/skills/python-conventions
```

Write `~/.dotfiles/claude/.claude/skills/python-conventions/SKILL.md` with exactly this content:

````markdown
---
name: python-conventions
description: >
  Mandatory rules for writing Python docstrings and comments on this
  workstation. Use before writing, reviewing, or modifying any Python
  docstring or inline comment. Covers the write-time comment-or-not gate,
  the PEP 257 docstring shape (state intent, never the type the hint
  carries), the copy-in ruff D config, and the T-P1 through T-P13 AI-tell
  catalogue. The prose authority is the python-comments register.
---

# Python Comment Conventions

The reader is a Python coder or an agent already looking at the code. A comment carries what the
code cannot: a why, a constraint, a piece of evidence. The type hint already states the type, so a
docstring that restates it is noise. This skill is the Python arm of the authoring charter
(`~/.claude/docs/authoring-charter.md`). The deeper prose authority, with exemplars, is the
`python-comments` register at `~/.claude/docs/voice/python-comments.md`; load it before writing or
reviewing comments.

## Persona

You write Python the way the standard library and a well-run CLI do: a terse one-line docstring or
none, a `#` comment only where the why is non-obvious, type hints carrying the types. The
workstation's Python is small scripts in `~/.local/bin`, not a documented library, so a one-line
docstring is the common case and a missing one is fine. An `Args:` or `Returns:` block is reserved
for a contract the signature and the hints leave unobvious. Imperative mood, period-terminated.

## §0: Comment-or-not (write-time gate)

```
(a) Does the name plus the typed signature already say this?
(b) Is the why obvious from the next 5 lines or fewer?
(c) Would a reader otherwise miss a hidden constraint, an invariant, a
    side effect, or a surprising consequence?
```

Skip on (a) or (b). Write only for (c). A `with` block, a comprehension, and a standard idiom get
no narration; a Python reader knows them. The paraphrase test is the primary filter: if the
docstring is the signature in English, or the `#` comment restates the next line, delete it.

## Decision rubric

```
1. Public function, class, or method whose contract is fully implied by
   name + signature + hints?
   YES -> a one-line docstring if it sharpens intent, or none. No Args:/Returns:.
   NO  -> a one-line summary plus an Args:/Returns: entry only for the part
          the signature cannot express (a unit, a bound, a None-semantic).

2. Internal helper (leading underscore) with unobvious behavior?
   YES -> a one-line docstring or a short # comment.   NO -> nothing.

3. Inside a function: does this block differ from what the name and
   control flow imply?
   YES -> one-line # why-comment with evidence (issue URL, spec, symptom).
   NO  -> no comment.

4. A real gap or deferral?
   YES -> a concrete # TODO(glw907): ...   NO -> no apology, no hedge.
```

ruff does not force a docstring to exist; the `D100` through `D107` presence family is ignored
precisely so this gate, not the linter, owns presence. That mirrors Go's opt-in-on-unexported rule.

## Docstring shape

- PEP 257: a one-line docstring is one physical line, opening with a capital and ending with a
  period, in imperative mood ("Return the sum", not "Returns the sum"). ruff's `D401` enforces the
  mood and `D415` the period.
- State intent, never the type. The signature and the hints carry the types; the docstring carries
  the constraint, the unit, the None-semantic, or the caller obligation they cannot express.
- Google-style sections (`Args:`, `Returns:`, `Raises:`) are used sparingly, only when a parameter
  or return value carries a contract beyond its type. Document an `Args:` entry for the why, not the
  type. Document a `Raises:` entry only for an exception a caller must handle, never a speculative
  one.
- A module docstring is one sentence of intent when it earns its place, not a banner and not
  metadata git already tracks.
- Vary the opener across neighbors. Never lead every docstring with "Foo does X". One thought per
  comment. No em dash.

## Linting: the copy-in ruff config

The dotfiles repo carries this at `ruff.toml` in its root. A consumer repo copies it in and adjusts
`per-file-ignores` to its own test layout.

```toml
[lint]
select = ["D"]
ignore = ["D100", "D101", "D102", "D103", "D104", "D105", "D106", "D107"]
extend-select = ["D401"]

[lint.pydocstyle]
convention = "google"

[lint.per-file-ignores]
"tests/**" = ["D"]
```

`select = ["D"]` turns on the pydocstyle rules; `convention = "google"` disables the
convention-incompatible ones for you (and suppresses the `D203`/`D211` and `D212`/`D213`
incompatibility warnings). The `ignore` list drops the whole missing-docstring presence family,
because ruff has no warn tier and presence is this skill's gate, not a hard block. `extend-select`
restores `D401`, which the google convention drops. `per-file-ignores` exempts tests. ruff lints an
extensionless script too when you pass its path, so the bin scripts are covered; Vale's `py` scope
reaches `.py` files only.

## §catalogue: the T-P1 through T-P13 AI-tell catalogue

Each tell: id, name, the mechanical avoidance rule. The full prose, with an AI-shaped example and a
human counter-example, is in the `python-comments` register. When a finding triggers more than one
tell, cite the strongest: T-P1 (signature restatement) outranks T-P6 (type in the docstring); T-P4
(paraphrase) outranks a structural tell on the same line. Cite as `T-P<n> at file:line`.

| id | name | rule |
|---|---|---|
| T-P1 | docstring restating the signature | if it is the signature in English, delete it |
| T-P2 | reflexive docstring on a trivial helper | a private helper gets a docstring only for unobvious behavior |
| T-P3 | `Args:`/`Returns:` duplicating type hints | document a constraint, not a type the hint declares |
| T-P4 | `# This function` / restating the next line | the paraphrase test; comment the surprise |
| T-P5 | module or class docstring banner | one prose sentence; no banner art, no metadata git tracks |
| T-P6 | type info in the docstring | annotate the signature; the docstring states intent |
| T-P7 | hedging or apologetic docstring | state the invariant; a real gap is a concrete `# TODO(glw907):` |
| T-P8 | uniform docstring rhythm | length follows complexity |
| T-P9 | uniform "Foo does X" shape | imperative mood, varied sentence shape across neighbors |
| T-P10 | speculative `Raises:` entries | document only an exception a caller must handle |
| T-P11 | over-explaining Python idioms | never explain `with` or a comprehension to a Python reader |
| T-P12 | task-framing or changelog comments | git carries the task and the fix |
| T-P13 | restated-annotation `#` comment | the annotation is the type statement; delete the comment |

## Tooling and the division of labor

- ruff (`D` rules) owns docstring correctness: imperative mood, the period, the one-line form,
  argument-description completeness when an `Args:` block exists. It cannot see prose quality, and it
  does not force presence.
- Vale on `.py` comments owns the deterministic lexical net: the em dash, the marketing and slop
  words, the banned phrases, inside `#` comments and `"""` docstrings. It is the home of the retired
  `prose-guard` comment tier. It reaches `.py` files only; an extensionless script gets the ruff
  layer alone.
- This skill and the register own the semantic tells neither tool can see: the paraphrase, the
  reflexive docstring, the type narrated in prose, the uniform rhythm. When a finding is a plain
  lexical or correctness hit, expect ruff or Vale to have caught it; spend the judgment here.

## Output

When reviewing, cite each finding as `T-P<n> at file:line` with the one-line avoidance rule. When
writing, run the §0 gate first, then the rubric, then write only what survives.
````

- [ ] **Step 3: Re-run the check and confirm content**

```bash
S=~/.dotfiles/claude/.claude/skills/python-conventions/SKILL.md
test -f "$S" && echo PASS || echo FAIL
grep -q 'Comment-or-not' "$S" && echo "GATE OK" || echo "MISSING"
grep -qE 'T-P1 \||T-P13 \|' "$S" && echo "CATALOGUE OK" || echo "MISSING"
grep -q 'D100' "$S" && echo "RUFF CONFIG OK" || echo "MISSING"
```

Expected: `PASS`, `GATE OK`, `CATALOGUE OK`, `RUFF CONFIG OK`.

- [ ] **Step 4: Lint the skill clean and commit**

```bash
cd ~/.dotfiles
vale --minAlertLevel=error claude/.claude/skills/python-conventions/SKILL.md | tail -2
git add claude/.claude/skills/python-conventions/SKILL.md
git commit -m "Add the python-conventions skill for the Python comment arm" \
  -m "Carries the write-time gate, the PEP 257 docstring shape, the copy-in ruff D config, and the T-P1 through T-P13 catalogue. The python-comments register is the prose authority." \
  -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```

Expected: a clean or advisory-only Vale run, then the commit.

---

### Task 5: The `python-comments` register

Create the new register, the prose authority for Python comments, mirroring the `ts-svelte-comments` register: the reader, when a comment exists, length scaling, real terse exemplars, the anti-patterns, the off-voice contrast, and the T-P catalogue with worked examples.

**Files:**
- Create: `~/.dotfiles/claude/.claude/docs/voice/python-comments.md`

**Interfaces:**
- Consumes: the T-P1 through T-P13 ids from the Task 4 skill.
- Produces: the register the `python-conventions` skill points at, the single home of the expanded Python tells.

- [ ] **Step 1: Create the register**

Write `~/.dotfiles/claude/.claude/docs/voice/python-comments.md` with exactly this content:

````markdown
# Register: Python code comments

The reader is a Python coder or an agent already looking at the code. A comment exists to carry
what the code cannot: a why, a constraint, a piece of evidence. Placement and function come before
prose style. The empirical baseline is PEP 257, the CPython standard library (terse one-line
docstrings, sparse `#` comments concentrated where intent is non-obvious), and the workstation's
own scripts in `~/.local/bin`. Type hints carry the types, so the docstring never restates them.

## When a comment exists

- Comment why, almost never what. The paraphrase test applies: if the docstring is the signature in
  English, or the `#` comment restates the next line, delete it.
- A docstring on a public function is a one-liner stating intent, or nothing when the name and the
  hints already say it. The script is small; a missing docstring is not a defect.
- An `Args:`, `Returns:`, or `Raises:` block earns its place only for a contract the signature
  cannot show: a unit, a bound, a None-semantic, an exception a caller must handle.
- A `#` comment justifying odd-looking code sits immediately above it and carries evidence: the
  issue URL, the spec citation, the observed symptom.
- A real gap is a concrete `# TODO(glw907): ...`, never an apology folded into the docstring.
- Standard idioms stay silent. A Python reader knows `with`, a comprehension, and an unpacking.

## Length scales with distance from the reader

A public entry point gets a full docstring: a capitalized imperative sentence with a period, the
contract stated, an `Args:` line only where a parameter hides a constraint. An internal helper gets
a one-line docstring or a bare `#` line. An inline aside is a lowercase fragment or a plain
sentence, candid about a hack. Length follows the code's surprise, not a fixed shape: a tricky
parser function earns a paragraph, a one-line wrapper earns nothing.

## Exemplars

A public function, terse, stating intent the name does not quite carry:

```python
def slugify(title: str) -> str:
    """Return a URL-safe slug, collapsing runs of punctuation to a single hyphen."""
    ...
```

A contract the signature cannot express, in a sparing `Args:` block:

```python
def retry(fn: Callable[[], T], attempts: int = 3) -> T:
    """Call fn until it returns, backing off between tries.

    Args:
        attempts: total tries, not retries; attempts=1 means no retry.
    """
    ...
```

The why behind odd-looking code, with the receipt:

```python
# CPython rounds half-to-even, so 2.5 rounds to 2; the spec wants half-up, hence the Decimal.
total = (Decimal(raw) ).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
```

An intentional swallow, marked so the emptiness reads as a decision:

```python
try:
    os.remove(lockfile)
except FileNotFoundError:
    pass  # already gone; a missing lock is the state we want
```

A scheduled gap, concrete and owned:

```python
# TODO(glw907): drop this shim once the D1 migration lands; it double-writes for now.
```

## Anti-patterns (do not imitate)

The docstring that restates the signature:

```python
def add(a: int, b: int) -> int:
    """Takes two ints, a and b, and returns an int."""
    return a + b
```

The module banner repeating what the path and git already carry:

```python
# ======================================================================
# slugify.py - slug helpers
# Author: glw907  Created: 2026-06-22  Version: 1.0
# ======================================================================
```

## Off-voice contrast

The AI comment spray this register exists to prevent: narrating each step, restating the types,
no information the code lacks:

```python
# This function loops through the items
for item in items:
    # Check if the item is valid
    if is_valid(item):
        # Increment the counter by one
        count += 1  # count is an integer
```

## The T-P catalogue (T-P1 through T-P13)

The numbered tells the `python-conventions` skill cites. Each is an AI-shaped habit with its
mechanical fix; the worked examples below cover the tells the exemplars above do not already show.

| id | name | rule |
|---|---|---|
| T-P1 | docstring restating the signature | if it is the signature in English, delete it |
| T-P2 | reflexive docstring on a trivial helper | a private helper gets a docstring only for unobvious behavior |
| T-P3 | `Args:`/`Returns:` duplicating type hints | document a constraint, not a type the hint declares |
| T-P4 | `# This function` / restating the next line | the paraphrase test; comment the surprise |
| T-P5 | module or class docstring banner | one prose sentence; no banner art, no metadata git tracks |
| T-P6 | type info in the docstring | annotate the signature; the docstring states intent |
| T-P7 | hedging or apologetic docstring | state the invariant; a real gap is a concrete `# TODO(glw907):` |
| T-P8 | uniform docstring rhythm | length follows complexity |
| T-P9 | uniform "Foo does X" shape | imperative mood, varied sentence shape across neighbors |
| T-P10 | speculative `Raises:` entries | document only an exception a caller must handle |
| T-P11 | over-explaining Python idioms | never explain `with` or a comprehension to a Python reader |
| T-P12 | task-framing or changelog comments | git carries the task and the fix |
| T-P13 | restated-annotation `#` comment | the annotation is the type statement; delete the comment |

T-P3, the `Args:` block duplicating the hints. The signature already says `int` and `str`; document
the constraint the type cannot:

```python
# off-voice: every parameter restated as its type
def crop(path: str, width: int) -> bytes:
    """Crop an image.

    Args:
        path: a string, the file path.
        width: an integer, the width.
    """
# in-voice: an Args: line only for the part the type cannot carry
def crop(path: str, width: int) -> bytes:
    """Crop an image to width, preserving aspect ratio.

    Args:
        width: target width in pixels; must be even, the encoder rejects odd widths.
    """
```

T-P9, the uniform "Foo does X" shape across neighbors. Imperative mood, varied openers:

```python
# off-voice: every docstring molded to the same frame
def load(p): """This function loads the config."""
def save(p): """This function saves the config."""
def reset(): """This function resets the config."""
# in-voice: imperative, and varied where the work differs
def load(p): """Read the config, falling back to defaults on a missing file."""
def save(p): """Write the config atomically through a temp file and rename."""
def reset(): """Restore the shipped defaults."""
```

T-P11, the explained idiom. A Python reader knows `with` and a comprehension:

```python
# off-voice
# use a context manager so the file closes automatically
with open(path) as f:
    # build a list of stripped lines using a comprehension
    lines = [ln.strip() for ln in f]
# in-voice: silence, unless a non-obvious why hides here
with open(path) as f:
    lines = [ln.strip() for ln in f]
```

T-P12, the changelog comment. Git carries the task and the fix:

```python
# off-voice
# added 2026-06 to fix the double-encode bug, see #91
text = raw.encode("utf-8")
# in-voice: the why, only if it is not obvious; the issue link only if it argues the code
text = raw.encode("utf-8")  # the upstream feed double-encodes latin-1; normalize here
```
````

- [ ] **Step 2: Confirm and commit**

```bash
cd ~/.dotfiles
grep -q 'T-P catalogue' claude/.claude/docs/voice/python-comments.md && echo "CATALOGUE OK" || echo "MISSING"
grep -q 'Off-voice contrast' claude/.claude/docs/voice/python-comments.md && echo "CONTRAST OK" || echo "MISSING"
vale --minAlertLevel=error claude/.claude/docs/voice/python-comments.md | tail -2
git add claude/.claude/docs/voice/python-comments.md
git commit -m "Add the python-comments register for the Python comment arm" \
  -m "The prose authority for Python docstrings and comments: the reader, length scaling, real exemplars, and the T-P1 through T-P13 catalogue with worked examples." \
  -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```

Expected: `CATALOGUE OK`, `CONTRAST OK`, a clean or advisory-only Vale run, then the commit. A Vale error in the register's own prose is a tell to fix before committing.

---

### Task 6: Record the Python arm as built, and prove the feedforward

**Files:**
- Modify: `~/.dotfiles/claude/.claude/docs/authoring-charter.md` (the build-state bullet and the Pointers line)

**Interfaces:**
- Consumes: everything above.
- Produces: a charter that names the Python arm as live and points the next plan at the prose arm, and a recorded proof that the skill and register let an agent name T-P tells by number.

- [ ] **Step 1: Prove the feedforward layer names a T-P tell**

Dispatch one `general-purpose` agent with this prompt: "Read `~/.dotfiles/claude/.claude/skills/python-conventions/SKILL.md` and `~/.dotfiles/claude/.claude/docs/voice/python-comments.md`. Review this Python as the python-conventions reviewer, citing each finding as `T-P<n> at file:line`. Code (`sample.py`):

```python
def add(a: int, b: int) -> int:
    \"\"\"This function takes two ints, a and b, and returns their sum as an int.\"\"\"
    # use the + operator to add them
    return a + b
```

Return only the findings." Expected: the agent cites T-P1 (docstring restating the signature) and T-P11 or T-P4 (the explained `+` operator). Record the outcome in the commit message.

- [ ] **Step 2: Update the charter build-state bullet and the Pointers line**

In `~/.dotfiles/claude/.claude/docs/authoring-charter.md`:

First, replace the build-state bullet that begins "The Vale foundation is built and the Go, TypeScript, and Svelte comment arms are live" so it names the Python arm too. Change the opening to "The Vale foundation is built and the Go, TypeScript, Svelte, and Python comment arms are live." Then, before the closing sentence, add: "The dotfiles repo carries the Python arm itself: a root `ruff.toml` running the `D` docstring rules under the google convention (presence ignored, correctness enforced), a `[*.py]` Vale section linting comment and docstring prose through `glw907`, a `scripts/check-py-comments.sh` runner over the repo's Python including the extensionless bin scripts, and the `python-conventions` skill with the `python-comments` register for the semantic tells." End the bullet with "The prose arm is the next plan."

Second, in the Pointers section, change the line "Comment voice references are `~/.claude/docs/go-comment-voice.md` and `~/.claude/docs/voice/ts-svelte-comments.md`, with a Python companion to follow." Drop "with a Python companion to follow" and name the new register: "and `~/.claude/docs/voice/python-comments.md`."

- [ ] **Step 3: Lint clean and commit the charter**

```bash
cd ~/.dotfiles
vale --minAlertLevel=error claude/.claude/docs/authoring-charter.md | tail -2
git add claude/.claude/docs/authoring-charter.md
git commit -m "Record the Python comment arm as built in the charter" \
  -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```

Expected: a clean or advisory-only Vale run, then the commit.

- [ ] **Step 4: Run the full Python gate once more**

```bash
cd ~/.dotfiles
bash scripts/check-py-comments.sh
echo "exit: $?"
git status --short
```

Expected: `check:py-comments OK`, exit `0`, and `git status` showing only the two pre-existing untouched files (`claude/.claude/settings.json`, `claude/.claude/skills/cairn-pass/SKILL.md`). Every file this plan created or modified is committed; nothing else moved.

---

## Self-Review

Run after the last task.

1. **ruff config present and correct:** `ruff.toml` selects `D`, ignores `D100` through `D107`, re-enables `D401`, uses the google convention, and excludes tests; `D417` and `D401` fire on a planted function (Task 1).
2. **Vale py scope works:** the planted `.py` proof fires on the docstring and the `#` comment and not on code; the real test file lints clean at error level (Task 2).
3. **Runner ties the layers:** `check-py-comments.sh` runs ruff over all tracked Python plus the extensionless bin scripts and Vale over the `.py` files, is green against the real repo, and fails on a planted tell (Task 3).
4. **Skill present:** `python-conventions/SKILL.md` carries the §0 gate, the docstring shape, the copy-in ruff config, and the T-P1 through T-P13 catalogue (Task 4).
5. **Register present:** `python-comments.md` carries the reader, the exemplars, the off-voice contrast, and the T-P catalogue with worked examples (Task 5).
6. **Feedforward usable:** an agent given the skill and register names T-P tells by number (Task 6 Step 1).
7. **Charter accurate:** the build-state bullet names the Python arm live and points at the prose arm; the Pointers line names the `python-comments` register (Task 6).
8. **Presence stays Claude's gate:** ruff forces no docstring; the `D100` through `D107` family is ignored, the decision the central rule requires.
9. **Nothing else moved:** the extensionless-script limit is documented, not papered over with an extractor; `prose-guard`'s behavior and hook are untouched; the two pre-existing uncommitted files are left for Geoff; `prose-guard` retires in the cutover plan.
````