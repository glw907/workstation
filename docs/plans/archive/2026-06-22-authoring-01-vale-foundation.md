# Vale Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Stand up the shared Vale layer the whole authoring system rests on: Vale pinned to 3.15.1, the `glw907` overlay split into always-on universal tells plus a separately toggleable audience-conditional set, the Google and Microsoft baselines vendored, a global config, and a fixture suite that proves both prose linting and comment-scoped linting.

**Architecture:** Vale runs from a pinned binary in `~/.local/bin`. Styles live under a stowed `~/.config/vale/styles` tree: the private `glw907` style (hand-written rules) plus the `Google` and `Microsoft` packages fetched by `vale sync`. A stowed global `~/.config/vale/.vale.ini` provides the `StylesPath` and the workstation's own audience map; project repos carry their own in-tree `.vale.ini` later. Comment-scoped linting uses Vale's Code format support: a `[formats]` association maps a source extension to Markdown so Vale extracts only the comment text and lints that. The fixture runner asserts each `*.bad.*` raises its named rule and each `*.good.*` is clean.

**Tech Stack:** Vale 3.15.1 (errata-ai/vale), GNU Stow, bash, the existing `glw907` rule YAML.

## Global Constraints

- Vale version is `3.15.1` (the latest release as of 2026-06-22, confirmed against the errata-ai/vale releases), pinned in `~/.dotfiles/scripts/install-vale.sh`; bump deliberately.
- Vale binary installs to `~/.local/bin/vale`; releases come from `github.com/errata-ai/vale`.
- The global config is `~/.config/vale/.vale.ini` (canonical `~/.dotfiles/vale/.config/vale/.vale.ini`, stowed). No `VALE_CONFIG_PATH` env var is set; it would override in-tree configs.
- `StylesPath` for the global config is `~/.config/vale/styles` (canonical `~/.dotfiles/vale/.config/vale/styles`, stowed).
- The `glw907` style splits in two: universal tells apply in every register; the audience-conditional rules (the em dash first among them) toggle off per config section where the register allows them. The default bans the em dash, and only a section that opts out allows it.
- Baselines: the `Google` package for developer and planning docs, the `Microsoft` package for end-user copy. Both are CC BY 4.0. The Microsoft package is an unofficial implementation hosted in the Vale org; note it where it is declared.
- This plan does not touch `prose-guard`. It stays the active hook until the later cutover plan.
- Fail closed: the global config carries only the workstation's own audiences, never a generic catch-all that lints an undeclared repo.

## The plan series

This is plan 01 of the authoring-system build. Each later plan is written just-in-time after the prior one lands.

1. **Vale foundation** (this plan): the pinned binary, the split `glw907` overlay, the vendored baselines, the global config, the fixture suite including a comment-scope proof.
2. **Go comment arm:** add the `.go` Vale comment scope, prove it against poplar, confirm the existing `/simplify` Go voice lens still names tells.
3. **TypeScript comment arm:** the ESLint jsdoc/tsdoc flat config, the `ts` Vale format, the `ts-conventions` skill, the TS1-TS15 catalogue into the `ts-svelte-comments` register. Prove against cairn `src/lib`.
4. **Svelte comment arm:** the light `eslint-plugin-svelte` config plus the custom `@component` rule, `@component` Vale coverage, the script-block comment extractor, the `svelte-conventions` skill, the S1-S10 catalogue.
5. **Python comment arm:** the `ruff` `D` config, the `py` Vale format, the `python-conventions` skill, the `python-comments` register, the T-P1-T-P13 catalogue.
6. **Prose arm:** the Google and Microsoft baselines applied to docs and content per glob, the prose registers leading on exemplars, the PostToolUse prose Vale hook scoped to changed lines.
7. **Cutover:** wire the Vale hook in `settings.json`, prove the loop, retire `prose-guard`, rewrite the active output style and the CLAUDE.md writing-voice section, repoint the `prose-voice.md` router.

The two source specs are `~/.dotfiles/docs/superpowers/specs/2026-06-22-ai-drafting-prose-system-design.md` (prose arm) and `~/.dotfiles/docs/superpowers/specs/2026-06-22-code-comment-standards-design.md` (comment arm). The umbrella is `~/.claude/docs/authoring-charter.md`.

---

### Task 1: Pin Vale to 3.15.1

**Files:**
- Modify: `~/.dotfiles/scripts/install-vale.sh:5`

**Interfaces:**
- Produces: a `~/.local/bin/vale` reporting version `3.15.1`, with Code-format comment scoping and regexp2 lookarounds confirmed. Every later task and plan relies on this binary.

- [ ] **Step 1: Write the failing check**

Run this; it is the test for this task and must fail before the change:

```bash
vale --version | grep -q '3\.15\.1' && echo PASS || echo FAIL
```

Expected: `FAIL` (the installed binary is 3.9.1).

- [ ] **Step 2: Bump the pin**

In `~/.dotfiles/scripts/install-vale.sh`, change line 5:

```bash
VALE_VERSION="3.15.1"   # pin; bump deliberately
```

- [ ] **Step 3: Install the pinned binary**

```bash
bash ~/.dotfiles/scripts/install-vale.sh
```

Expected: prints `Installed: vale version 3.15.1`.

- [ ] **Step 4: Re-run the check**

```bash
vale --version | grep -q '3\.15\.1' && echo PASS || echo FAIL
```

Expected: `PASS`.

- [ ] **Step 5: Confirm comment scoping and lookarounds on this version**

This guards the mechanism the comment arm depends on. Point a scratch config at the existing `glw907` styles and prove Vale lints only the comment text in a `.go` file:

```bash
d="$(mktemp -d)"
printf 'StylesPath = %s\nMinAlertLevel = suggestion\n[formats]\ngo = md\n[*.go]\nBasedOnStyles = glw907\n' \
  "$HOME/.dotfiles/vale/.config/vale/styles" > "$d/.vale.ini"
printf 'package x\n\n// This is a seamless tapestry of helpers.\nfunc Run() {}\n' > "$d/x.go"
( cd "$d" && vale --output=line x.go )
rm -rf "$d"
```

Expected: `glw907.Slop` fires on the comment (line 3, `seamless` and `tapestry`) and nothing fires on the code (line 4, `func Run`). If Vale raises nothing, errors on the `[formats]` key, or flags the code line, stop: the comment-scope mechanism is not available on this build, and the comment arm needs a version revisit before plan 02. Record the outcome in the commit message.

- [ ] **Step 6: Commit**

```bash
cd ~/.dotfiles
git add scripts/install-vale.sh
git commit -m "Pin Vale to 3.15.1 for comment-scope support" \
  -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 2: Split the em dash into an audience-conditional rule

Ban the em dash by default; toggle it off only where a register allows it. Vale toggles a single rule per config section with `glw907.EmDash = NO`, so the rule stays in the `glw907` style and the config decides per glob. This task proves the toggle with fixtures.

**Files:**
- Modify: `~/.dotfiles/vale/.config/vale/styles/glw907/EmDash.yml` (message wording only; keep `level: error`)
- Create: `~/.dotfiles/vale/tests/fixtures/EmDashAllowed.good.md`
- Modify: `~/.dotfiles/vale/tests/.vale.ini`
- Modify: `~/.dotfiles/vale/tests/run-fixtures.sh:1-27`

**Interfaces:**
- Consumes: the existing `glw907.EmDash` rule and the `EmDash.bad.md` / `EmDash.good.md` fixtures.
- Produces: a documented per-section toggle (`glw907.EmDash = NO`) that the prose and comment plans reuse to allow the em dash in literary content while banning it everywhere else.

- [ ] **Step 1: Add a fixture for the allowed register**

Create `~/.dotfiles/vale/tests/fixtures/EmDashAllowed.good.md` whose body is a single sentence carrying one em dash. Write it with a command so the literal character is exact:

```bash
printf 'A magazine sentence carries one %s here, by design.\n' "$(printf '\xe2\x80\x94')" \
  > ~/.dotfiles/vale/tests/fixtures/EmDashAllowed.good.md
```

- [ ] **Step 2: Add a scoped section that disables the rule, and run the runner to see it fail**

In `~/.dotfiles/vale/tests/.vale.ini`, add a section that treats the `EmDashAllowed.*` fixture as the literary register with the em-dash rule off:

```ini
[fixtures/EmDashAllowed.*]
BasedOnStyles = glw907
glw907.EmDash = NO
```

The runner does not yet know `*.good.md` files named `EmDashAllowed` should stay clean under a toggle; run it to confirm the current contract still holds and nothing regressed:

```bash
cd ~/.dotfiles/vale/tests && bash run-fixtures.sh
```

Expected: `fixtures: OK` if the section parses and the `EmDashAllowed.good.md` raises nothing. If it raises `glw907.EmDash`, the toggle did not take; fix the section glob before continuing.

- [ ] **Step 3: Prove the ban still fires without the toggle**

```bash
cd ~/.dotfiles/vale/tests && vale --output=line fixtures/EmDash.bad.md | grep -q EmDash && echo PASS || echo FAIL
```

Expected: `PASS` (the default register still bans the em dash; only the scoped `EmDashAllowed` section opts out).

- [ ] **Step 4: Document the toggle in the rule file**

Update the `message` in `~/.dotfiles/vale/.config/vale/styles/glw907/EmDash.yml` so the finding names the fix and the toggle:

```yaml
extends: existence
message: "Em dash is a tell here. End the sentence, or use a colon, a comma, or parentheses. Allowed only in a register that sets glw907.EmDash = NO."
level: error
nonword: true
tokens:
  - '—'
```

- [ ] **Step 5: Re-run the full fixture suite**

```bash
cd ~/.dotfiles/vale/tests && bash run-fixtures.sh
```

Expected: `fixtures: OK`.

- [ ] **Step 6: Commit**

```bash
cd ~/.dotfiles
git add vale/.config/vale/styles/glw907/EmDash.yml vale/tests/.vale.ini vale/tests/fixtures/EmDashAllowed.good.md
git commit -m "Make the em dash an audience-conditional Vale rule" \
  -m "The em dash is banned by default and toggles off per config section with glw907.EmDash = NO, for the literary register only." \
  -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 3: Vendor the Google and Microsoft baselines

**Files:**
- Create: `~/.dotfiles/vale/.config/vale/.vale.ini` (the global config; minimal here, extended in Task 4)
- Create: `~/.dotfiles/vale/.gitignore`
- Modify: `~/.dotfiles/scripts/install-vale.sh` (append a `vale sync` step)

**Interfaces:**
- Consumes: the pinned Vale binary from Task 1.
- Produces: `Google` and `Microsoft` package styles fetched into `~/.config/vale/styles`, available to every config that names them in `BasedOnStyles`.

- [ ] **Step 1: Declare the packages in the global config**

Create `~/.dotfiles/vale/.config/vale/.vale.ini` as pure infrastructure: where the styles live, which packages to fetch, and how to scope comments. It declares no `BasedOnStyles` section, so it lints nothing on its own. That is the fail-closed default: a file under no repo config gets no rules.

```ini
StylesPath = styles
MinAlertLevel = suggestion

Packages = Google, Microsoft

# Comment-scoped linting: extract comment text and lint it as Markdown.
[formats]
go = md
ts = md
py = md
```

- [ ] **Step 2: Stow so the config resolves at the global path**

```bash
cd ~/.dotfiles && stow -R vale
ls -la ~/.config/vale/.vale.ini
```

Expected: the path resolves as a symlink into `~/.dotfiles/vale/.config/vale/.vale.ini`.

- [ ] **Step 3: Sync the packages, then verify they landed**

```bash
vale sync
ls ~/.config/vale/styles
```

Expected: the directory now contains `Google` and `Microsoft` alongside `glw907`.

- [ ] **Step 4: Gitignore the fetched packages, keep the private style**

`vale sync` output is re-fetchable, so it is not committed; the hand-written `glw907` style is. Create `~/.dotfiles/vale/.gitignore`:

```gitignore
# vale sync fetches these; the pin lives in install-vale.sh / .vale.ini Packages
.config/vale/styles/Google/
.config/vale/styles/Microsoft/
.config/vale/styles/.vale-config/
```

- [ ] **Step 5: Make the install script self-contained**

Append to `~/.dotfiles/scripts/install-vale.sh` so a fresh machine fetches the packages after installing the binary:

```bash

# Fetch the pinned baseline packages into the stowed StylesPath.
if command -v vale >/dev/null 2>&1; then
  echo "Syncing Vale packages ..."
  ( cd "$HOME/.config/vale" && vale sync )
fi
```

- [ ] **Step 6: Confirm the baseline package resolves**

```bash
d="$(mktemp -d)"
printf 'StylesPath = %s\nMinAlertLevel = suggestion\n[*.md]\nBasedOnStyles = Google\n' \
  "$HOME/.config/vale/styles" > "$d/.vale.ini"
printf 'We should leverage our synergy here.\n' > "$d/t.md"
( cd "$d" && vale t.md 2>&1 ) | tee "$d/out"
grep -qi 'does not exist\|runtime error' "$d/out" && echo "Google MISSING" || echo "Google resolved"
rm -rf "$d"
```

Expected: `Google resolved`, with Vale reporting findings on the sentence (the first-person `we`/`our` is a Google rule). If it prints `Google MISSING`, the package did not sync; recheck Task 3 step 3.

- [ ] **Step 7: Commit**

```bash
cd ~/.dotfiles
git add vale/.config/vale/.vale.ini vale/.gitignore scripts/install-vale.sh
git commit -m "Vendor the Google and Microsoft Vale baselines via vale sync" \
  -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 4: Give the dotfiles repo its own audience map

The global config is pure infrastructure and lints nothing on its own, so a repo opts in with its own in-tree `.vale.ini`. The dotfiles repo is the first adopter, and it doubles as the worked example of the charter's adoption recipe: its planning docs take the Google baseline plus the house overlay, and its agent-facing registers take the overlay alone. The section globs are relative to the config's own directory, which is why an in-tree config is correct here and an absolute glob in the global config is not.

**Files:**
- Create: `~/.dotfiles/.vale.ini`

**Interfaces:**
- Consumes: the `glw907`, `Google`, and `Microsoft` styles vendored into the repo's `vale/.config/vale/styles` tree by Tasks 2 and 3.
- Produces: the dotfiles audience map, the pattern every other repo copies to adopt the charter.

- [ ] **Step 1: Write the in-tree audience map**

Create `~/.dotfiles/.vale.ini`. Its `StylesPath` is repo-relative, pointing at the styles the vale package already holds:

```ini
StylesPath = vale/.config/vale/styles
MinAlertLevel = suggestion

Packages = Google, Microsoft

[formats]
go = md
ts = md
py = md

# Planning docs and specs: the Google developer baseline plus the house overlay.
# The em dash stays banned here (no opt-out section).
[docs/**/*.md]
BasedOnStyles = Vale, Google, glw907

# Agent-facing house docs and the registers (stowed into ~/.claude): overlay only.
[claude/.claude/**/*.md]
BasedOnStyles = glw907
```

- [ ] **Step 2: Verify the config parses and resolves its styles**

```bash
cd ~/.dotfiles && vale ls-config | grep -E 'StylesPath|MinAlertLevel' && echo PARSED
```

Expected: the resolved `StylesPath` ends in `vale/.config/vale/styles` and prints `PARSED`. An error here means a glob or key is malformed.

- [ ] **Step 3: Lint a real planning doc through the Google baseline**

```bash
cd ~/.dotfiles && vale docs/superpowers/specs/2026-06-22-code-comment-standards-design.md | tail -5
```

Expected: Vale runs against the combined `Vale, Google, glw907` style and reports a count. Findings are advisory at `suggestion` level; the point is a clean run, not zero findings.

- [ ] **Step 4: Confirm fail-closed outside any repo config**

```bash
d="$(mktemp -d)"; printf 'Moreover, this can be utilized.\n' > "$d/x.md"
vale "$d/x.md" 2>&1 | tail -2; rm -rf "$d"
```

Expected: a path under no in-tree config falls back to the pure-infra global config, which declares no `BasedOnStyles`, so Vale reports `0 errors, 0 warnings, 0 suggestions`. That is the fail-closed behavior.

- [ ] **Step 5: Commit**

```bash
cd ~/.dotfiles
git add .vale.ini
git commit -m "Adopt the charter in the dotfiles repo with an in-tree Vale config" \
  -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 5: Extend the fixture suite to cover the comment scope

The runner already asserts the prose rules. Add a comment-scope fixture so a regression in Vale's Code-format extraction is caught here, not in a downstream plan.

**Files:**
- Create: `~/.dotfiles/vale/tests/fixtures/comment-scope/x.go`
- Create: `~/.dotfiles/vale/tests/comment-scope.vale.ini`
- Modify: `~/.dotfiles/vale/tests/run-fixtures.sh`

**Interfaces:**
- Consumes: the pinned binary and the `glw907` style.
- Produces: a runner that fails if Vale stops scoping to comments, or if it starts linting code tokens.

- [ ] **Step 1: Add the comment-scope fixture and its config**

```bash
mkdir -p ~/.dotfiles/vale/tests/fixtures/comment-scope
printf 'package x\n\n// This is a seamless tapestry of helpers.\nfunc Utilize() {}\n' \
  > ~/.dotfiles/vale/tests/fixtures/comment-scope/x.go
```

Create `~/.dotfiles/vale/tests/comment-scope.vale.ini`:

```ini
StylesPath = ../.config/vale/styles
MinAlertLevel = suggestion

[formats]
go = md

[*.go]
BasedOnStyles = glw907
```

- [ ] **Step 2: Add a comment-scope assertion to the runner**

Append before the final summary in `~/.dotfiles/vale/tests/run-fixtures.sh` (after the `*.good.*` loop, before the `[ "$fail" -eq 0 ]` line):

```bash
# Comment scope: the rule must fire on comment text and ignore code tokens.
cs="fixtures/comment-scope/x.go"
out="$(vale --config=comment-scope.vale.ini --output=line "$cs")"
if ! grep -q 'Slop\|Marketing' <<<"$out"; then
  echo "FAIL: $cs did not raise a glw907 rule on its comment"; fail=1
fi
if grep -q ':4:' <<<"$out"; then
  echo "FAIL: $cs raised on the code line (func Utilize), comment scope leaked"; fail=1
fi
```

- [ ] **Step 3: Run the runner and confirm the new assertion passes**

```bash
cd ~/.dotfiles/vale/tests && bash run-fixtures.sh
```

Expected: `fixtures: OK`. The comment on line 3 (`seamless`, `tapestry`) raises `glw907.Slop`; the code on line 4 (`Utilize`) does not raise, proving the scope holds.

- [ ] **Step 4: Commit**

```bash
cd ~/.dotfiles
git add vale/tests/fixtures/comment-scope/x.go vale/tests/comment-scope.vale.ini vale/tests/run-fixtures.sh
git commit -m "Cover comment-scoped linting in the Vale fixture suite" \
  -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 6: Record the foundation state and point the next plan at it

**Files:**
- Modify: `~/.claude/docs/authoring-charter.md` (the build-state line)

**Interfaces:**
- Consumes: everything above.
- Produces: an accurate build-state line so the charter does not claim more than is built.

- [ ] **Step 1: Update the charter build-state line**

In `~/.claude/docs/authoring-charter.md`, in the Pointers section, replace the line that begins "Go comments are the proven instance today" with:

```markdown
- The Vale foundation is built: the pinned binary, the split `glw907` overlay, the vendored Google
  and Microsoft baselines, the global config, and the fixture suite including a comment-scope proof.
  Go comments are the proven judgment instance (the `go-conventions` skill, golangci-lint, the
  `/simplify` voice lens). The four comment arms and the prose arm are the next plans.
```

- [ ] **Step 2: Confirm the charter still lints clean**

```bash
vale ~/.claude/docs/authoring-charter.md | tail -3
```

Expected: a clean or advisory-only run.

- [ ] **Step 3: Commit**

```bash
cd ~/.dotfiles
git add claude/.claude/docs/authoring-charter.md
git commit -m "Record the Vale foundation as built in the charter" \
  -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Self-Review

Run after the last task.

1. **Foundation present:** `~/.local/bin/vale` reports 3.15.1; `~/.config/vale/.vale.ini` resolves; `vale sync` populated `Google` and `Microsoft`; `bash ~/.dotfiles/vale/tests/run-fixtures.sh` prints `fixtures: OK`.
2. **Em-dash toggle works:** the default register bans the em dash; the `EmDashAllowed` section allows it; the runner asserts both.
3. **Comment scope works:** Task 1 step 5 and Task 5 both prove Vale lints comment text and ignores code tokens.
4. **Fail-closed holds:** a path outside the declared globs gets no rules.
5. **prose-guard untouched:** no file under `~/.local/bin/prose-guard` or the prose-guard hook config changed in this plan.
