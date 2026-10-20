# Go Comment Arm Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make Vale lint the prose inside Go comments live in a real consumer repo. poplar adopts the charter, carries a committed copy of the `glw907` overlay, and gets an in-tree `.vale.ini` that scopes the overlay to `.go` comment text. The existing `/simplify` Go voice lens stays the semantic layer and is confirmed intact.

**Architecture:** Vale's Code-format support extracts comment text from a `.go` file and lints it as Markdown, so the `glw907` lexical rules (the em dash, the marketing and slop words, the banned phrases) fire on comments and ignore code tokens. A consumer repo opts in by committing a vendored copy of the `glw907` style under `.vale/styles/glw907` and an in-tree `.vale.ini` that maps `[*.go]` to that overlay. A reusable dotfiles script vendors the style and checks a repo's copy for drift against the canonical source. This is the first real consumer adoption; the dotfiles repo was the worked example in plan 01.

**Tech Stack:** Vale 3.15.1 (errata-ai/vale), bash, the hand-written `glw907` Vale style, the poplar Go repo, the `go-conventions` skill and `go-comment-voice.md`.

## Global Constraints

- Vale is pinned to `3.15.1`; the binary is `~/.local/bin/vale` and reports that version. The Code-format comment scoping this plan depends on is confirmed present on that build (plan 01 Task 1, and the pre-flight for this plan).
- The canonical `glw907` style lives at `~/.dotfiles/vale/.config/vale/styles/glw907`. Every consumer repo carries a committed copy, never a symlink, so Vale runs the same rules in CI and on a fresh machine.
- A consumer repo's vendored copy lives at `<repo>/.vale/styles/glw907` and its in-tree config at `<repo>/.vale.ini`, with `StylesPath = .vale/styles`.
- The em dash stays banned in Go comments. No opt-out section is added for `.go`; the `glw907.EmDash = NO` toggle exists only for a literary register and never applies to code.
- This arm changes nothing else about Go. poplar's `.golangci.yml`, its `make check` gate, its `scripts/voice-check.sh`, and its `/simplify` skill keep their current behavior. The spec is explicit that Go is the template the other languages follow, so the Go tooling does not move here.
- This plan does not touch `prose-guard`. It stays the active hook until the cutover plan (07).
- dotfiles changes commit to dotfiles `main`, matching plan 01. poplar changes land on a poplar branch off `master` and merge back when green, since the change is additive config with no Go code.
- Commit footer on both repos: `Co-Authored-By: Claude <noreply@anthropic.com>`.

## The plan series

This is plan 02 of the authoring-system build. Each plan is written just-in-time after the prior one lands. Plan 01 (Vale foundation) is done and committed on dotfiles `main`.

1. **Vale foundation** (done): the pinned binary, the split `glw907` overlay, the vendored Google and Microsoft baselines, the global config, the fixture suite including a comment-scope proof.
2. **Go comment arm** (this plan): the reusable vendor-and-drift-check script, poplar's adoption with an in-tree `.vale.ini` scoping `glw907` to `.go` comments, the live proof against poplar's real code, and a confirmation that the `/simplify` Go voice lens still names tells.
3. **TypeScript comment arm:** the ESLint jsdoc/tsdoc flat config, the `ts` Vale format, the `ts-conventions` skill, the TS1-TS15 catalogue into the `ts-svelte-comments` register. Prove against cairn `src/lib`.
4. **Svelte comment arm:** the light `eslint-plugin-svelte` config plus the custom `@component` rule, `@component` Vale coverage, the script-block comment extractor, the `svelte-conventions` skill, the S1-S10 catalogue.
5. **Python comment arm:** the `ruff` `D` config, the `py` Vale format, the `python-conventions` skill, the `python-comments` register, the T-P1-T-P13 catalogue.
6. **Prose arm:** the Google and Microsoft baselines applied to docs and content per glob, the prose registers leading on exemplars, the PostToolUse prose Vale hook scoped to changed lines. poplar's docs gain their `docs/**/*.md` to Google mapping here.
7. **Cutover:** wire the Vale hook in `settings.json`, prove the loop, retire `prose-guard`, rewrite the active output style and the CLAUDE.md writing-voice section, repoint the `prose-voice.md` router.

The source specs are `~/.dotfiles/docs/superpowers/specs/2026-06-22-ai-drafting-prose-system-design.md` (prose arm) and `~/.dotfiles/docs/superpowers/specs/2026-06-22-code-comment-standards-design.md` (comment arm). The umbrella is `~/.claude/docs/authoring-charter.md`.

---

### Task 1: A reusable vendor-and-drift-check script

The distribution model is a committed copy of `glw907` per repo with a drift-check against the canonical source. This task builds the one script that does both jobs, so every later arm reuses it. Its test uses a throwaway directory, not poplar, so the tool is proven before poplar relies on it.

**Files:**
- Create: `~/.dotfiles/scripts/glw907-vendor.sh`

**Interfaces:**
- Consumes: the canonical style at `~/.dotfiles/vale/.config/vale/styles/glw907`.
- Produces: `glw907-vendor.sh <repo-root>` checks `<repo-root>/.vale/styles/glw907` against the canonical style and exits non-zero on drift or a missing copy; `glw907-vendor.sh <repo-root> --sync` overwrites the repo's copy from the canonical style. Task 2 and every later consumer arm call this with `--sync`.

- [ ] **Step 1: Write the failing check**

The tool does not exist yet. This is the test for the task:

```bash
t="$(mktemp -d)"
bash ~/.dotfiles/scripts/glw907-vendor.sh "$t" --sync 2>&1 | grep -q 'vendored glw907' && echo PASS || echo FAIL
rm -rf "$t"
```

Expected: `FAIL` (no such script).

- [ ] **Step 2: Write the script**

Create `~/.dotfiles/scripts/glw907-vendor.sh`:

```bash
#!/usr/bin/env bash
# glw907-vendor.sh: vendor the canonical glw907 Vale style into a consumer repo,
# or check a repo's vendored copy for drift against the canonical source. The
# canonical home is the dotfiles repo; every other repo carries a committed copy
# so Vale runs the same rules in CI and on a fresh machine.
set -uo pipefail

canon="$HOME/.dotfiles/vale/.config/vale/styles/glw907"

usage() {
  echo "usage: glw907-vendor.sh <repo-root> [--sync]" >&2
  echo "  default: check the repo's vendored copy against the canonical style" >&2
  echo "  --sync:  overwrite the repo's copy from the canonical style" >&2
}

repo="${1:-}"
mode="${2:-check}"
[ -n "$repo" ] || { usage; exit 2; }
[ -d "$canon" ] || { echo "canonical style missing: $canon" >&2; exit 2; }

dest="$repo/.vale/styles/glw907"

case "$mode" in
  --sync)
    mkdir -p "$repo/.vale/styles"
    rm -rf "$dest"
    cp -r "$canon" "$dest"
    echo "vendored glw907 -> $dest"
    ;;
  check)
    if [ ! -d "$dest" ]; then
      echo "DRIFT: no vendored glw907 at $dest; run with --sync" >&2
      exit 1
    fi
    if diff -r "$canon" "$dest" >/dev/null; then
      echo "glw907 vendored copy is in sync"
    else
      echo "DRIFT: $dest differs from $canon; run with --sync" >&2
      diff -r "$canon" "$dest" >&2
      exit 1
    fi
    ;;
  *)
    usage
    exit 2
    ;;
esac
```

Then make it executable:

```bash
chmod +x ~/.dotfiles/scripts/glw907-vendor.sh
```

- [ ] **Step 3: Prove sync, then re-run the check from step 1**

```bash
t="$(mktemp -d)"
bash ~/.dotfiles/scripts/glw907-vendor.sh "$t" --sync
test -f "$t/.vale/styles/glw907/EmDash.yml" && echo "FILES OK" || echo "FILES MISSING"
bash ~/.dotfiles/scripts/glw907-vendor.sh "$t" --sync 2>&1 | grep -q 'vendored glw907' && echo PASS || echo FAIL
rm -rf "$t"
```

Expected: `vendored glw907 -> ...`, then `FILES OK`, then `PASS`.

- [ ] **Step 4: Prove the check passes in sync and fails on drift**

```bash
t="$(mktemp -d)"
bash ~/.dotfiles/scripts/glw907-vendor.sh "$t" --sync >/dev/null
bash ~/.dotfiles/scripts/glw907-vendor.sh "$t" && echo "CHECK-CLEAN PASS" || echo "CHECK-CLEAN FAIL"
echo "# drift" >> "$t/.vale/styles/glw907/Slop.yml"
bash ~/.dotfiles/scripts/glw907-vendor.sh "$t"; rc=$?
[ "$rc" -ne 0 ] && echo "DRIFT-DETECTED PASS" || echo "DRIFT-DETECTED FAIL"
bash ~/.dotfiles/scripts/glw907-vendor.sh "$t" --sync >/dev/null
bash ~/.dotfiles/scripts/glw907-vendor.sh "$t" && echo "RESYNC PASS" || echo "RESYNC FAIL"
rm -rf "$t"
```

Expected: `glw907 vendored copy is in sync` then `CHECK-CLEAN PASS`; then a `DRIFT:` message and `DRIFT-DETECTED PASS`; then `RESYNC PASS`.

- [ ] **Step 5: Commit**

```bash
cd ~/.dotfiles
git add scripts/glw907-vendor.sh
git commit -m "Add the glw907 vendor-and-drift-check script for consumer repos" \
  -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 2: poplar adopts the charter for its Go comments

poplar carries a committed `glw907` copy and an in-tree `.vale.ini` that lints its `.go` comment prose. The config maps `[*.go]` to the overlay only; the `docs/**/*.md` to Google mapping is the prose arm's job and arrives in plan 06, noted in the file so the next reader knows it is deliberate, not forgotten. The proof runs Vale over poplar's real Go and over one throwaway file that carries a planted tell, confirming the rule fires on comment text and never on code.

**Files:**
- Create: `~/Projects/poplar/.vale.ini`
- Create: `~/Projects/poplar/.vale/styles/glw907/**` (vendored by the Task 1 script)
- Modify: `~/Projects/poplar/CLAUDE.md` (a short authoring pointer)

**Interfaces:**
- Consumes: `glw907-vendor.sh` from Task 1; the pinned Vale binary; the `glw907` style.
- Produces: a poplar repo where `cd ~/Projects/poplar && vale <file>.go` lints comment prose through `glw907`. Every later prose tool, including the cutover plan's PostToolUse hook, resolves this in-tree config when it runs inside poplar.

- [ ] **Step 1: Branch poplar off master**

```bash
cd ~/Projects/poplar
git switch -c authoring/vale-go-comment-arm
git status --short
```

Expected: a clean working tree on the new branch.

- [ ] **Step 2: Confirm `.vale/` is not ignored, then vendor the style**

```bash
cd ~/Projects/poplar
git check-ignore .vale/styles/glw907/Slop.yml && echo "IGNORED, fix .gitignore" || echo "not ignored, good"
bash ~/.dotfiles/scripts/glw907-vendor.sh ~/Projects/poplar --sync
ls .vale/styles/glw907
```

Expected: `not ignored, good`; then `vendored glw907 -> ...`; then the rule files (`BannedPhrases.yml`, `EmDash.yml`, `Filler.yml`, `Judgment.yml`, `Marketing.yml`, `Openers.yml`, `Slop.yml`). If the path is ignored, add a negation (`!.vale/styles/glw907/`) to poplar's `.gitignore` before continuing.

- [ ] **Step 3: Write poplar's in-tree audience map**

Create `~/Projects/poplar/.vale.ini`:

```ini
StylesPath = .vale/styles
MinAlertLevel = suggestion

# Comment-scoped linting: extract Go comment text and lint it as Markdown.
[formats]
go = md

# Go comments: the house overlay. The em dash stays banned (no opt-out section).
# Vale lints only the comment text and ignores code tokens.
[*.go]
BasedOnStyles = glw907

# The docs/**/*.md to Google + glw907 mapping arrives with the prose arm (plan 06).
# It is left out here on purpose so this arm stays scoped to Go comments.
```

- [ ] **Step 4: Confirm the config parses and resolves its styles**

```bash
cd ~/Projects/poplar
vale ls-config | grep -E 'StylesPath|MinAlertLevel'
```

Expected: the resolved `StylesPath` ends in poplar's `.vale/styles`, and `MinAlertLevel` is `suggestion`. A parse error here means a glob or key is malformed.

- [ ] **Step 5: Proof A, no em dash in real poplar Go comments**

Real, audited poplar code should carry no em dash in any comment, since `scripts/voice-check.sh` already bans the form (T33). Vale should agree:

```bash
cd ~/Projects/poplar
n="$(vale --output=line $(git ls-files '*.go') 2>/dev/null | grep -c 'glw907.EmDash')"
echo "em-dash findings in real Go comments: $n"
[ "$n" -eq 0 ] && echo "PROOF-A PASS" || echo "PROOF-A FAIL"
```

Expected: `0`, then `PROOF-A PASS`. A non-zero count is a real finding to read and fix, not a tooling fault; record it and clean the comment before continuing.

- [ ] **Step 6: Proof B, a planted tell fires on the comment and not the code**

Place one throwaway file inside poplar's tree so the in-tree config governs it, then delete it. The em dash is written from its bytes so the literal character is exact and the plan file itself stays clean:

```bash
cd ~/Projects/poplar
mkdir -p .vale-proof
printf 'package proof\n\n// Build a seamless pipeline %s fast.\n\nfunc Leverage() {}\n' \
  "$(printf '\xe2\x80\x94')" > .vale-proof/x.go
out="$(vale --output=line .vale-proof/x.go)"
echo "$out"
grep -q 'x.go:3:.*glw907.EmDash' <<<"$out" && echo "EM-DASH-ON-COMMENT PASS" || echo "EM-DASH FAIL"
grep -q 'x.go:3:.*glw907.Slop'   <<<"$out" && echo "SLOP-ON-COMMENT PASS"    || echo "SLOP FAIL"
grep -q 'x.go:5:' <<<"$out" && echo "SCOPE LEAK on code line" || echo "SCOPE-HOLDS PASS"
rm -rf .vale-proof
```

Expected: `Slop` and `EmDash` both fire on line 3 (the comment); nothing fires on line 5 (`func Leverage`, where `Leverage` is a Judgment token sitting in code). So `EM-DASH-ON-COMMENT PASS`, `SLOP-ON-COMMENT PASS`, `SCOPE-HOLDS PASS`. Confirm `.vale-proof` is gone with `ls -d .vale-proof 2>&1`.

- [ ] **Step 7: Add the authoring pointer to poplar's CLAUDE.md**

Append this section to `~/Projects/poplar/CLAUDE.md` (place it after the existing top-level conventions content, before any closing material):

```markdown
## Authoring

Claude's drafting on this repo follows the workstation authoring charter at
`~/.claude/docs/authoring-charter.md`. The Go comment audience is wired: the in-tree
`.vale.ini` lints `.go` comment prose through the vendored `glw907` overlay in
`.vale/styles/glw907`, which catches the em dash and the banned lexicon inside comments.
The semantic layer stays the `/simplify` Go voice lens (the T-numbered catalogue in
`~/.claude/docs/go-comment-voice.md`). Re-sync the overlay after a canonical change with
`~/.dotfiles/scripts/glw907-vendor.sh ~/Projects/poplar --sync`. The docs prose mapping
arrives with the charter's prose arm.
```

- [ ] **Step 8: Confirm the pointer lints clean through poplar's own config**

The new section is a `.md` file, so poplar's `.vale.ini` does not lint it (no `[*.md]` section yet). Confirm it carries no em dash by hand:

```bash
cd ~/Projects/poplar
grep -nP '\xe2\x80\x94' CLAUDE.md && echo "EM-DASH PRESENT, fix it" || echo "CLAUDE.md em-dash clean"
```

Expected: `CLAUDE.md em-dash clean`.

- [ ] **Step 9: Commit on the poplar branch**

```bash
cd ~/Projects/poplar
git add .vale.ini .vale/styles/glw907 CLAUDE.md
git commit -m "Adopt the Vale Go comment arm: in-tree config and vendored glw907" \
  -m "Lints .go comment prose through the glw907 overlay; the em dash and the banned lexicon now fire on comments and ignore code. Proven against real poplar Go and a planted tell." \
  -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 3: Confirm the `/simplify` Go voice lens still names tells

Vale now gives Go comments a deterministic net for the em dash and the `glw907` lexicon. The `/simplify` voice lens stays the semantic layer, the tells Vale cannot see (a comment paraphrasing the next five lines, a godoc on a self-evident unexported symbol). This task confirms the lens still reads its catalogue and emits findings by number, then records the new division of labor so a future reader does not wonder which layer owns the em dash.

**Files:**
- Modify: `~/.dotfiles/claude/.claude/docs/go-comment-voice.md` (a short tooling note)

**Interfaces:**
- Consumes: the poplar `/simplify` skill (`~/Projects/poplar/.claude/skills/simplify/SKILL.md`, Agent 4) and `~/.claude/docs/go-comment-voice.md`.
- Produces: a confirmation that the lens names tells, and a recorded note that Vale is the deterministic net for the em dash and the lexicon in `.go` comments while the lens keeps the semantic tells.

- [ ] **Step 1: Confirm the lens and its catalogue are intact**

```bash
echo "=== voice doc present with the gate and catalogue ==="
grep -qE '§0|paraphrase test' ~/.claude/docs/go-comment-voice.md && echo "GATE OK" || echo "GATE MISSING"
grep -qE 'T3[0-9]|T4[0-9]' ~/.claude/docs/go-comment-voice.md && echo "CATALOGUE OK" || echo "CATALOGUE MISSING"
echo "=== lens emits numbered findings ==="
grep -q 'T<n> at path/to/file.go:LINE' ~/Projects/poplar/.claude/skills/simplify/SKILL.md && echo "FORMAT OK" || echo "FORMAT MISSING"
grep -q 'go-comment-voice.md' ~/Projects/poplar/.claude/skills/simplify/SKILL.md && echo "READS VOICE DOC OK" || echo "READS VOICE DOC MISSING"
```

Expected: `GATE OK`, `CATALOGUE OK`, `FORMAT OK`, `READS VOICE DOC OK`.

- [ ] **Step 2: Empirically confirm the lens names a tell**

Dispatch one voice-review agent that performs the Agent 4 job on a scratch diff carrying a clear semantic tell, and confirm it returns a `T<n>` finding. Use a `general-purpose` agent with this prompt:

> Read `~/.claude/docs/go-comment-voice.md` to load the §0 gate and the tell catalogue. Then review this Go snippet as the `/simplify` voice agent would, citing each finding as `T<n> at file:line` with the one-line avoidance rule. Snippet (`demo.go`):
> ```go
> package demo
>
> // Add adds a and b and returns the sum.
> func Add(a, b int) int { return a + b }
> ```
> Return only the findings.

Expected: the agent flags the comment as a WHAT-comment that restates the signature, citing T1 (or the closest catalogue number), with the avoidance rule. The point is that the lens still produces a numbered tell; the exact number is secondary.

- [ ] **Step 3: Record the division of labor in the voice doc**

Add a short note to `~/.dotfiles/claude/.claude/docs/go-comment-voice.md`. Read the file first to find the tooling or overview section near the top, and insert this paragraph there:

```markdown
Vale now lints `.go` comment prose in repos that adopt the charter (poplar first), through
the `glw907` overlay. It is the deterministic net for the em dash and the banned lexicon
inside comments, alongside `scripts/voice-check.sh`. This lens keeps the semantic tells Vale
cannot see: the paraphrase test, the doc-on-a-self-evident-symbol, the uniform comment
rhythm. When a finding is a plain lexical hit, expect Vale or the voice-check script to have
caught it already; spend this lens on the judgment calls.
```

- [ ] **Step 4: Confirm the voice doc lints clean, then commit**

The voice doc is under `claude/.claude/`, so the dotfiles in-tree config lints it through `glw907`:

```bash
cd ~/.dotfiles
vale claude/.claude/docs/go-comment-voice.md | tail -3
```

Expected: a clean or advisory-only run, no `error`-level findings on the new paragraph.

```bash
cd ~/.dotfiles
git add claude/.claude/docs/go-comment-voice.md
git commit -m "Note Vale's deterministic net for Go comment lexicon next to the voice lens" \
  -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 4: Record the Go arm as built

**Files:**
- Modify: `~/.dotfiles/claude/.claude/docs/authoring-charter.md` (the build-state line)

**Interfaces:**
- Consumes: everything above.
- Produces: a charter build-state line that names the Go arm as live and points the next plan at TypeScript.

- [ ] **Step 1: Update the charter build-state line**

In `~/.dotfiles/claude/.claude/docs/authoring-charter.md`, in the Pointers section, replace the bullet that begins "The Vale foundation is built" with:

```markdown
- The Vale foundation is built and the Go comment arm is live. The pinned binary, the split
  `glw907` overlay, the vendored Google and Microsoft baselines, the global config, and the
  fixture suite came first. poplar is the first consumer adopter: its in-tree `.vale.ini`
  lints `.go` comment prose through a committed `glw907` copy, proven against its real code,
  and `scripts/glw907-vendor.sh` vendors that copy and checks it for drift. Go now has all
  three layers, golangci-lint for structure, Vale on `.go` comments for the lexicon, and the
  `go-conventions` skill plus the `/simplify` voice lens for the semantic tells. TypeScript,
  Svelte, Python, and the prose arm are the next plans.
```

- [ ] **Step 2: Confirm the charter still lints clean**

```bash
cd ~/.dotfiles
vale claude/.claude/docs/authoring-charter.md | tail -3
```

Expected: a clean or advisory-only run, no `error`-level findings.

- [ ] **Step 3: Commit**

```bash
cd ~/.dotfiles
git add claude/.claude/docs/authoring-charter.md
git commit -m "Record the Go comment arm as built in the charter" \
  -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```

- [ ] **Step 4: Merge the poplar branch back to master**

The poplar change is additive config with no Go code, and `make check` is unaffected. Merge when the proofs are green:

```bash
cd ~/Projects/poplar
git switch master
git merge --no-ff authoring/vale-go-comment-arm \
  -m "Merge the Vale Go comment arm adoption" \
  -m "Co-Authored-By: Claude <noreply@anthropic.com>"
git branch -d authoring/vale-go-comment-arm
```

Expected: a clean merge, the branch deleted. Leave the push to Geoff.

---

## Self-Review

Run after the last task.

1. **Tool proven:** `glw907-vendor.sh` syncs a copy, passes the check in sync, fails on drift, and re-syncs clean (Task 1 steps 3 and 4).
2. **poplar adopts:** `cd ~/Projects/poplar && vale ls-config` resolves the in-tree `.vale/styles`; `.vale.ini` maps `[*.go]` to `glw907`; the vendored style is committed.
3. **Scope holds:** the planted-tell proof fires `EmDash` and `Slop` on the comment line and nothing on the code line (Task 2 step 6); real poplar Go carries no em dash in comments (Task 2 step 5).
4. **Lens intact:** the `/simplify` voice doc still carries the gate and catalogue, the lens still emits `T<n>` findings, and the new note records that Vale owns the lexical net in comments while the lens owns the semantic tells (Task 3).
5. **Charter accurate:** the build-state line names the Go arm as live and points at TypeScript next (Task 4).
6. **Nothing else moved:** poplar's `.golangci.yml`, `make check`, `scripts/voice-check.sh`, and the `/simplify` skill are unchanged; `prose-guard` is untouched; the global Vale config is unchanged.
