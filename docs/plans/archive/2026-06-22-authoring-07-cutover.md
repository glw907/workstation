# Cutover Implementation Plan (authoring plan 07)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Flip the workstation from `prose-guard` to the live Vale-based prose system: a lean always-on output style, a CLAUDE.md routing layer, an on-demand `writing-voice` Skill, the wired `vale-hook`, the resolved em-dash policy, and `prose-guard` retired from the always-on hooks.

**Architecture:** The six-layer prose system (spec `2026-06-22-ai-drafting-prose-system-design.md`) goes live. Layers 1 through 3 (output style, CLAUDE.md table, the Skill router) are rewritten to lead on the registers and point at Vale. Layer 5 (the `vale-hook`, built and proven in plan 06) gets wired into `settings.json` and `prose-guard`'s always-on hooks come out. The registers, the reviewer subagent, and the comment arms already shipped in plans 01 through 06; this plan wires them together as the live default.

**Tech Stack:** Vale 3.15.1 with the vendored Google and Microsoft packages and the `glw907` overlay, the Claude Code output-style and Skill primitives, the `settings.json` hook config, and the dotfiles repo's git.

## Global Constraints

- **Behavior-preserving except one policy.** The cutover is a mechanism swap. The single intended behavior change is the em-dash policy for developer and planning docs: it moves from banned (prose-guard) to allowed (planning docs are throwaway; long-term docs follow the Google standard). Every other register keeps today's stance: discouraged in replies, commit messages, agent-facing files, and editor copy; banned in code comments; allowed sparing in polished site content.
- **No feedback window.** `vale-hook` is wired and proven live (Task 7) before any `prose-guard` hook comes out (Task 8). `vale-hook` covers docs prose continuously; the per-repo comment arms cover code comments. There is no gap in docs feedback.
- **The prose-guard script stays on disk, deprecated.** Its always-on hooks come out, but the script remains as the content skills' explicit backstop (`content-review`, `web-content-method` call `prose-guard <file>`) until the ECXC and 907 site sessions migrate content to Vale, which is when it is deleted. A deprecation header records this.
- **Live edits are main-loop, not the workflow.** Tasks 7 and 8 edit `settings.json`, the active hooks this session runs under, so the main loop executes and verifies them directly. Tasks 1 through 6 are workflow-executable; the output style and CLAUDE.md are cached for the current session, so editing them cannot break it.
- All changes commit to dotfiles `main` directly; there is no consumer branch. The working tree carries two unrelated uncommitted files (`claude/.claude/settings.json`, `claude/.claude/skills/cairn-pass/SKILL.md`) left for Geoff. Do not touch them, and `git add` only the files each task names. Note that `settings.json` is both one of those untouched files AND the target of Tasks 7 and 8; the main loop reconciles this by applying only the hook change there and leaving Geoff's other edits to that file intact (Tasks 7 and 8 are main-loop for this reason).
- Commit footer: `Co-Authored-By: Claude <noreply@anthropic.com>`.
- Every new or rewritten file must pass the active `prose-guard` PreToolUse hook (still wired through Task 7) and Vale at error level. The embedded bodies below are authored clean: no em dash in prose (only inside fenced examples, which both linters skip), and no raw marketing or slop word outside a fence.

## What is in plan 07, and what is deferred

In plan 07 (the workstation cutover):

1. The `writing-voice` Skill, the on-demand register router (layer 3).
2. The leaned output style (layer 1), pointing at the Skill and Vale.
3. The rewritten global CLAUDE.md voice section (layer 2), the routing table.
4. The `.vale.ini` docs em-dash change (allow it in planning docs).
5. The repoint of the `prose-guard` reference surface (docs, agents, the reviewer, the vale-hook docstring).
6. Retiring `prose-voice.md` (its content distributes into the Skill, output style, and CLAUDE.md).
7. Wiring `vale-hook` into `settings.json` and proving the loop live (main loop).
8. Retiring `prose-guard`'s always-on hooks, deprecating the script (main loop).

Deferred, with reasons:

- **The /simplify wiring** (naming the TS, Svelte, and Python tells by number in the simplify lens). A code-comment-arm tail, separable and low-risk, better as its own small follow-up than bloating this high-blast-radius plan.
- **The reply and email registers.** They encode Geoff's daily voice and are their own calibration session.
- **The built-in `Vale` spelling style, its `Vocab`, and the Readability floor.** They need a curated corpus, which the dotfiles repo lacks.
- **The cairn and site applications** (cairn per-path baseline, ECXC migrate, 907 define-then-wire), each its own repo session after the cutover. The content skills (`content-review`, `web-content-method`) keep their `prose-guard` calls until then.

## Pilot findings carried into this plan

1. `vale-hook` is built and proven end to end (plan 06): an error-tier finding on a changed line exits 2 with the finding on stderr; a clean-line edit exits 0 silent with a pre-existing tell suppressed; it fails open. Task 7 wires it; the live proof is a real PostToolUse invocation.
2. `prose-guard` runs as both a PreToolUse and a PostToolUse `Write|Edit` hook (`prose-guard --hook`, `prose-guard --post-hook`). It blocks a write on the lexical and structural tier and skips fenced code blocks and inline code, so an embedded file body in a `~~~` fence is not scanned during a plan write, but the body is scanned when the implementer writes it to its real file.
3. The `glw907.EmDash` rule is toggled per `.vale.ini` section (`glw907.EmDash = NO` turns it off). The Google package's own em-dash rule governs spacing only, so with `glw907.EmDash` off the em dash is allowed under a no-spaces convention.
4. `ts-conventions` and `python-conventions` already describe `prose-guard` as retired (written ahead in plans 03 and 05); they need no change.

---

### Task 1: The writing-voice Skill (the router)

Build the on-demand router, layer 3. It carries the audience-to-register table, the shape rules, and the em-dash matrix, pointing one level deep to the register files. It changes no live behavior (a new skill is inert until triggered). The content is shown in a tilde fence; copy the inner Markdown verbatim into the file.

**Files:**
- Create: `~/.dotfiles/claude/.claude/skills/writing-voice/SKILL.md`

**Interfaces:**
- Produces: the `writing-voice` skill, the router the output style and CLAUDE.md point at in Tasks 2 and 3.

- [ ] **Step 1: Write the failing check**

```bash
test -f ~/.dotfiles/claude/.claude/skills/writing-voice/SKILL.md && echo PASS || echo FAIL
```

Expected: `FAIL`.

- [ ] **Step 2: Create the skill**

Create the directory and write `~/.dotfiles/claude/.claude/skills/writing-voice/SKILL.md` with exactly this content:

~~~markdown
---
name: writing-voice
description: Use when drafting or revising any substantial prose (a doc, plan, spec, README, design note, commit message, PR body, or site content) to load the audience's register, its exemplars, and the shape rules. The on-demand router for the workstation voice system.
---

# Writing voice: the on-demand router

The always-on `writing-voice` output style carries the audience-invariant voice: vary sentence
length, one idea per sentence, the universal tells, and the em-dash stance for replies. This skill is
the router. Name the audience, open the register that holds its persona and exemplars, and follow the
shape rules below. Load the register before drafting anything longer than a paragraph, and imitate its
exemplars rather than reaching for more rules. A tell is usually a register misapplied, so the
register is the stronger attractor.

## Pick the register

| Artifact | Register |
|---|---|
| Developer docs, README, or design doc in a Go repo | `~/.claude/docs/voice/technical-doc-go.md` |
| Developer docs, README, or design doc in a SvelteKit or web repo | `~/.claude/docs/voice/technical-doc-web.md` |
| End-user and editor product copy, admin walkthroughs | `~/.claude/docs/voice/editor.md` |
| CLAUDE.md, skills, agent definitions, hook text | `~/.claude/docs/voice/agent-facing.md` |
| Commit messages and PR bodies | `~/.claude/docs/voice/commit-and-pr.md` |
| Go code comments | the go-conventions skill |
| TypeScript and Svelte code comments | `~/.claude/docs/voice/ts-svelte-comments.md`, plus the ts-conventions and svelte-conventions skills |
| Python comments and docstrings | `~/.claude/docs/voice/python-comments.md`, plus the python-conventions skill |
| Site content (pages, posts, form copy) | the site repo's `docs/content-guide.md`, via the content-draft skill |

The dialect follows the repo's stack; a project CLAUDE.md may override with an explicit register line.

## Document shape

Shape-level tells read as machine-written even when every sentence is clean.

- Paragraphs over bullets. A bullet list is for a true enumeration (options, steps, fields), not for
  prose that happens to carry three points. If the items read as sentences with a shared subject, write
  the paragraph.
- No scaffold headers. "Overview", "Introduction", "Conclusion", and "Summary" are filler in anything
  shorter than a book chapter. A header serves a reader who navigates by it.
- Do not open every bullet or paragraph with a bolded lead phrase. Sparingly it signposts; by reflex it
  is the machine list default.
- One register per artifact. Do not drift from runbook to essay mid-document.

## The em-dash policy by audience

The em dash is the worked example of an audience-conditional rule. It is not banned outright, and
overuse is the real failure, flagged everywhere as a density signal.

| Audience | Em dash |
|---|---|
| Developer and planning docs (specs, plans, STATUS, post-mortems) | allowed; planning docs are throwaway, and long-term docs follow the Google standard |
| Polished or literary site content | allowed, sparing, per the site content-guide |
| End-user and editor product copy | discouraged |
| Agent-facing docs and commit messages | discouraged |
| Code comments | banned, enforced by the per-repo comment arm |
| Replies to Geoff | discouraged, a terminal reply has no em-dash key |

## Where the rules are encoded

- The registers under `~/.claude/docs/voice/`: persona, traits, and exemplars per audience. Registers
  are model-stable, so lean on them harder than on any rule list.
- Vale, per repo `.vale.ini` (the `glw907` overlay on the Google or Microsoft baseline): the
  deterministic lexical and structural net on docs prose and code comments. The `vale-hook` feeds its
  findings back as advisory context on save, and CI runs the same config.
- The `writing-voice` output style: the always-on audience-invariant voice.
- This skill: the router, the shape rules, and the em-dash matrix.
~~~

- [ ] **Step 3: Re-run the check and confirm shape**

```bash
S=~/.dotfiles/claude/.claude/skills/writing-voice/SKILL.md
test -f "$S" && echo PASS || echo FAIL
grep -qE '^name: writing-voice' "$S" && grep -qE '^## Pick the register' "$S" && echo "SHAPE OK" || echo "MISSING"
```

Expected: `PASS` and `SHAPE OK`.

- [ ] **Step 4: Lint clean and commit**

```bash
cd ~/.dotfiles
vale --minAlertLevel=error claude/.claude/skills/writing-voice/SKILL.md | tail -2
git add claude/.claude/skills/writing-voice/SKILL.md
git commit -m "Add the writing-voice Skill, the on-demand register router" \
  -m "Layer 3 of the prose system: the audience-to-register table, the shape rules, and the em-dash matrix, pointing to the registers under voice/. Additive; no live behavior changes until the output style and CLAUDE.md point at it." \
  -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```

Expected: a clean or advisory-only Vale run, then the commit.

---

### Task 2: Lean the output style

Rewrite the always-on `writing-voice` output style (layer 1) to the audience-invariant core: name the audience and load the register through the Skill, vary sentence length, the structural tells, and the audience-conditional em-dash rule. The exhaustive word lists move to Vale and the registers. Repoint it from `prose-voice.md` to the Skill and from `prose-guard` to Vale. Editing the output style does not affect the current session (it is prompt-cached); it takes effect next session.

**Files:**
- Modify (overwrite): `~/.dotfiles/claude/.claude/output-styles/writing-voice.md`

**Interfaces:**
- Consumes: the `writing-voice` Skill (Task 1).
- Produces: the leaned output style; no longer references `prose-voice.md` or `prose-guard`.

- [ ] **Step 1: Confirm the current file references the old system**

```bash
cd ~/.dotfiles
grep -c -E 'prose-voice\.md|prose-guard' claude/.claude/output-styles/writing-voice.md
```

Expected: a non-zero count (the current file references both).

- [ ] **Step 2: Overwrite the output style**

Overwrite `~/.dotfiles/claude/.claude/output-styles/writing-voice.md` with exactly this content:

~~~markdown
---
name: writing-voice
description: Always-on plain-voice prose guidance; avoids AI-writing tells
keep-coding-instructions: true
---

# Writing voice

Apply this to all prose you produce: docs, code comments, commit messages, error
strings, and replies. It does not change code, tool use, or file edits.

Before drafting anything longer than a paragraph, name the audience and load its
register through the `writing-voice` skill, which routes each audience to a register
file under `~/.claude/docs/voice/`. Each register carries a persona and exemplars to
imitate, and imitating an exemplar beats consulting a rule. The tell rules below are
audience-invariant; the register sets everything else.

Write in a plain, varied human voice. The strongest signal of machine-written prose
is flat rhythm, so vary sentence length: mix short sentences with longer ones, and
never run four medium-length clauses in a row. Carry one idea per sentence.

Em dashes are audience-conditional. They are discouraged in your replies, in commit
messages, in agent-facing files, and in editor copy, and banned in code comments; a
register sets its own stance and the per-repo Vale config enforces it. Developer and
planning docs allow them under the Google standard, and polished site content allows
a sparing one under the site's content guide. Where a register discourages the em
dash, end the sentence instead, or use a colon, a comma, or parentheses.

Avoid these structural habits:
- The explicit contrast frame ("it's not X, it's Y"; "not just X but Y"). Prefer an
  implicit contrast, or just state the point.
- Tricolons by reflex. Keep the one item that earns its place.
- The setup-colon payoff ("The point: ...") and the short-clause-then-colon-list
  ("The standard is clear: a, b, c"). Fold the list into the sentence with a word
  like "including", or write the items as their own sentences.
- Opening with a participial bridge ("Building on this, ...") or a connector
  ("Moreover, ..."). Start with the subject.
- Restating a paragraph's point at its end.
- Bullet lists where prose belongs. Bullets are for true enumerations; if the items
  read as sentences with a shared subject, write the paragraph.
- Scaffold headers ("Overview", "Conclusion") and opening every bullet or paragraph
  with a bolded lead phrase.
- The definitional pivot ("the honest test…", "the real question…") that stages a
  point instead of stating it. Say the point plainly.

The marketing, slop, and filler words are tells everywhere. The registers carry the
per-audience lexicon and Vale's `glw907` overlay is the machine net on docs prose and
code comments, with the `vale-hook` feeding its findings back on save. Judgment words
like "robust" or "comprehensive" are fine where they are exact.

Code comments also follow their stack's conventions: the go-conventions skill for
Go, the surrounding file's idiom for TypeScript/Svelte, PEP 257 for Python.

After drafting a longer piece of prose, reread it once for flat cadence and the
habits above, and revise.

## Before / after

```
- Before: "This isn't just a linter, it's a philosophy — clean, consistent, and clear."
  After:  "This is a linter. It enforces one writing standard across the repo."
- Before: "Moreover, the cache serves as a buffer, reducing latency significantly."
  After:  "The cache also buffers reads, so latency drops."
- Before: "The result? A faster, leaner, more maintainable system."
  After:  "The system ends up faster and easier to maintain."
```
~~~

- [ ] **Step 3: Confirm the rewrite**

```bash
cd ~/.dotfiles
O=claude/.claude/output-styles/writing-voice.md
grep -c -E 'prose-voice\.md|prose-guard' "$O"
grep -qE 'keep-coding-instructions: true' "$O" && grep -qE 'writing-voice` skill' "$O" && echo "REPOINTED OK" || echo "MISSING"
```

Expected: `0` (no reference to the old system remains), then `REPOINTED OK`.

- [ ] **Step 4: Lint clean and commit**

```bash
cd ~/.dotfiles
vale --minAlertLevel=error claude/.claude/output-styles/writing-voice.md | tail -2
git add claude/.claude/output-styles/writing-voice.md
git commit -m "Lean the writing-voice output style to the audience-invariant core" \
  -m "Layer 1: name the audience and load the register through the writing-voice skill, vary sentence length, the structural tells, and the audience-conditional em-dash rule. The exhaustive lexicon moves to Vale and the registers. Repointed off prose-voice.md and prose-guard." \
  -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```

Expected: a clean or advisory-only Vale run, then the commit. The em dash in the `Before` example sits inside a fenced code block, which Vale skips, so the file lints clean.

---

### Task 3: Rewrite the global CLAUDE.md voice section

Rewrite the `## Writing voice` section of the global CLAUDE.md (layer 2) as the routing layer: the highest-frequency tells inline plus the audience-to-register routing through the Skill. Repoint off `prose-voice.md` and `prose-guard`. Editing the global CLAUDE.md does not affect the current session (it is loaded at session start).

**Files:**
- Modify: `~/.dotfiles/claude/.claude/CLAUDE.md` (the `## Writing voice` section)

**Interfaces:**
- Consumes: the `writing-voice` Skill (Task 1).
- Produces: the lean CLAUDE.md routing layer; no longer references `prose-voice.md` or `prose-guard`.

- [ ] **Step 1: Confirm the current section**

```bash
cd ~/.dotfiles
sed -n '/^## Writing voice/,/^## Neovim/p' claude/.claude/CLAUDE.md | grep -c -E 'prose-voice\.md|prose-guard'
```

Expected: a non-zero count.

- [ ] **Step 2: Replace the section**

In `~/.dotfiles/claude/.claude/CLAUDE.md`, replace this exact block:

```markdown
## Writing voice

The `writing-voice` output style is always on (set in settings.json) and carries the
full prose standard: plain voice, varied sentence length, no AI-writing tells.

**Audience first.** Every piece of prose has a register. Before drafting, name the
audience and open its register file under `~/.claude/docs/voice/` (routing table in
`prose-voice.md`): site readers use the site's own content guide, Go and web developer
docs each have a dialect, agent-facing text and commit messages have their own files.
Imitate the register's exemplars; the tell rules are the same in every register.

**Pre-flight, not cleanup.** Before composing any doc, plan, spec, ADR, or longer
commit body, read `~/.claude/docs/prose-voice.md` first. It holds the full banned-
construction list and the first-draft rule. The `prose-guard` hook
(`~/.local/bin/prose-guard`) rejects the whole file on a violation, so a dirty draft
costs a full rewrite. Drafting clean on the first pass is the cheap path.

The highest-frequency tells, inline so they are unmissable without opening the file:
- No em dashes in prose. End the sentence, or use a colon, a comma, or parentheses.
- One idea per sentence. Do not bridge two or three clauses into one.
- No "not X but Y" contrast frame. No reflexive three-item lists. No setup-colon payoff.
- No participial or connector openers ("Building on this", "Moreover", "Additionally").

Code comments also follow their stack's conventions (go-conventions for Go, file idiom
for TS/Svelte, PEP 257 for Python).
```

with this block:

```markdown
## Writing voice

The `writing-voice` output style is always on (set in settings.json) and carries the
audience-invariant voice: plain voice, varied sentence length, the universal tells. The
`writing-voice` skill is the on-demand router: it maps each audience to its register and
states the shape rules and the em-dash matrix.

**Audience first.** Every piece of prose has a register. Before drafting, name the
audience and load its register through the `writing-voice` skill: site readers use the
site's own content guide, Go and web developer docs each have a dialect, end-user and
editor copy has its own register, and agent-facing text and commit messages have theirs.
Imitate the register's exemplars.

**Draft clean; Vale catches the residue.** The per-repo Vale config (the `glw907`
overlay on the Google or Microsoft baseline) is the deterministic net on docs prose and
code comments, and the `vale-hook` feeds its findings back as advisory context on save. A
clean Vale run is necessary, never sufficient, since it cannot judge voice. Draft clean
the first time from the register, and treat the hook feedback as a revision trigger for
prose you just wrote.

The highest-frequency tells, inline so they are unmissable without opening the register:
- One idea per sentence. Do not bridge two or three clauses into one.
- No "not X but Y" contrast frame. No reflexive three-item lists. No setup-colon payoff.
- No participial or connector openers ("Building on this", "Moreover", "Additionally").
- Em dashes are audience-conditional: discouraged in replies, commits, agent files, and
  editor copy, banned in code comments, allowed in developer and planning docs and (sparing)
  in site content.

Code comments also follow their stack's conventions (go-conventions for Go, file idiom
for TS/Svelte, PEP 257 for Python).
```

- [ ] **Step 3: Confirm the rewrite**

```bash
cd ~/.dotfiles
sed -n '/^## Writing voice/,/^## Neovim/p' claude/.claude/CLAUDE.md | grep -c -E 'prose-voice\.md|prose-guard'
grep -qE 'writing-voice` skill is the on-demand router' claude/.claude/CLAUDE.md && echo "REPOINTED OK" || echo "MISSING"
```

Expected: `0`, then `REPOINTED OK`.

- [ ] **Step 4: Lint clean and commit**

```bash
cd ~/.dotfiles
vale --minAlertLevel=error claude/.claude/CLAUDE.md | tail -2
git add claude/.claude/CLAUDE.md
git commit -m "Rewrite the global CLAUDE.md voice section as the routing layer" \
  -m "Layer 2: the highest-frequency tells inline plus audience routing through the writing-voice skill, draft-clean-then-Vale instead of the prose-guard pre-flight, and the audience-conditional em-dash rule. Repointed off prose-voice.md and prose-guard." \
  -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```

Expected: a clean or advisory-only Vale run, then the commit.

---

### Task 4: Allow the em dash in planning docs (.vale.ini)

Apply the resolved em-dash policy to the dotfiles docs section: planning docs are throwaway, so the em dash is allowed (`glw907.EmDash = NO`), and Google governs spacing. Only the `[docs/**/*.md]` section changes; the agent-facing and Python sections keep the em dash flagged.

**Files:**
- Modify: `~/.dotfiles/.vale.ini`

**Interfaces:**
- Consumes: the `glw907` overlay's toggleable `EmDash` rule.
- Produces: a docs section that allows the em dash; the agent-facing and Python sections unchanged.

- [ ] **Step 1: Confirm the em dash is currently flagged in docs**

```bash
cd ~/.dotfiles
printf 'A planning note with an em dash\xe2\x80\x94here, mid-sentence.\n' > docs/_emdash_probe.md
vale --output=line docs/_emdash_probe.md | grep -c 'glw907.EmDash'
```

Expected: a non-zero count (the docs section currently flags `glw907.EmDash`). Leave the probe file in place for Step 3.

- [ ] **Step 2: Turn off the em-dash rule for the docs section**

In `~/.dotfiles/.vale.ini`, replace this exact block:

```ini
# Planning docs and specs: the Google developer baseline plus the house overlay.
# The em dash stays banned here (no opt-out section). The built-in Vale style and
# its accept/reject Vocab arrive with the prose arm (plan 06).
[docs/**/*.md]
BasedOnStyles = Google, glw907
```

with this block:

```ini
# Planning docs and specs: the Google developer baseline plus the house overlay.
# Planning docs are throwaway, so the em dash is allowed here (glw907.EmDash off) and
# Google governs its spacing; long-term developer docs follow the Google standard. The
# built-in Vale style and its accept/reject Vocab are deferred until a curated corpus.
[docs/**/*.md]
BasedOnStyles = Google, glw907
glw907.EmDash = NO
```

- [ ] **Step 3: Confirm the em dash is now allowed in docs, then clean up**

```bash
cd ~/.dotfiles
vale --output=line docs/_emdash_probe.md | grep -c 'glw907.EmDash'
rm -f docs/_emdash_probe.md
```

Expected: `0` (the docs section no longer raises `glw907.EmDash`). The probe file is removed.

- [ ] **Step 4: Confirm the other sections are unchanged and the fixtures still pass**

```bash
cd ~/.dotfiles
grep -A2 '\[claude/.claude/\*\*/\*.md\]' .vale.ini | grep -c 'glw907.EmDash = NO'
( cd vale/tests && bash run-fixtures.sh )
```

Expected: `0` (the agent-facing section did not gain the opt-out), then `fixtures: OK`.

- [ ] **Step 5: Commit**

```bash
cd ~/.dotfiles
git add .vale.ini
git commit -m "Allow the em dash in planning docs (glw907.EmDash off for docs)" \
  -m "The resolved policy: planning docs are throwaway, so optimize for output; long-term developer docs follow the Google standard. The agent-facing, register, and Python sections keep the em dash flagged." \
  -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 5: Repoint the prose-guard reference surface

Repoint the docs, agents, and the reviewer that name `prose-guard` or `prose-voice.md` to the live system. The content skills (`content-review`, `web-content-method`) keep their `prose-guard` calls (the script stays as their backstop until the site migrations), and `ts-conventions` and `python-conventions` already say "retired", so neither is touched here.

**Files:**
- Modify: `~/.dotfiles/claude/.claude/docs/authoring-charter.md`
- Modify: `~/.dotfiles/claude/.claude/docs/go-comment-voice.md`
- Modify: `~/.dotfiles/claude/.claude/agents/cairn-implementer.md`
- Modify: `~/.dotfiles/claude/.claude/agents/site-implementer.md`
- Modify: `~/.dotfiles/claude/.claude/agents/prose-voice-reviewer.md`
- Modify: `~/.dotfiles/claude/.claude/docs/voice/calibration-2026-06-09.md`
- Modify: `~/.dotfiles/bin/.local/bin/vale-hook`

**Interfaces:**
- Produces: a reference surface that names the live system. Consumed by no later task; this is durable doc accuracy.

- [ ] **Step 1: The authoring charter (two spots)**

In `~/.dotfiles/claude/.claude/docs/authoring-charter.md`, replace:

```markdown
- Register routing for prose lives in `~/.claude/docs/prose-voice.md`, and the registers themselves
```

with:

```markdown
- Register routing for prose lives in the `writing-voice` skill, and the registers themselves
```

Then replace:

```markdown
read-only second opinion. The cutover is the next plan: wire the hook in `settings.json`, rewrite
the always-on output style and the global CLAUDE.md, build the `writing-voice` Skill router, retire
`prose-guard`, and repoint `prose-voice.md`.
- `prose-guard` is being retired in full; Vale takes over the feedback layer.
```

with:

```markdown
read-only second opinion. The cutover is complete (plan 07): the `vale-hook` is wired, the output
style and the global CLAUDE.md are leaned to the audience-invariant core, the `writing-voice` skill
routes the registers, `prose-voice.md` is retired, and `prose-guard`'s always-on hooks are removed.
- `prose-guard` is retired from the always-on hooks; Vale, the registers, and the `writing-voice`
  skill carry the feedback and feedforward. The script stays on disk only as the content skills'
  explicit backstop until the site content migrations, then it is deleted.
```

- [ ] **Step 2: The Go comment voice doc (two spots)**

In `~/.dotfiles/claude/.claude/docs/go-comment-voice.md`, replace:

```markdown
- Em-dash in comments: none. The stdlib tolerates a rare aside
  (~0.02 per Go file), but the prose-guard comments tier blocks a
  write on any em dash, so that allowance does not apply here. Use a
  period and a new sentence, or commas. See T33.
```

with:

```markdown
- Em-dash in comments: none. The stdlib tolerates a rare aside
  (~0.02 per Go file), but Vale's `glw907.EmDash` on `.go` comments
  flags any em dash, so that allowance does not apply here. Use a
  period and a new sentence, or commas. See T33.
```

Then replace:

```markdown
**Avoidance rule:** Use a period and a new sentence, or cut the
qualification. Do not use em dashes in comments at all; the prose-guard
comments tier blocks the write on a single one. If a comment needs an
em dash to flow, it is trying to say too much. Split or shorten it.
```

with:

```markdown
**Avoidance rule:** Use a period and a new sentence, or cut the
qualification. Do not use em dashes in comments at all; Vale's
`glw907.EmDash` flags a single one. If a comment needs an
em dash to flow, it is trying to say too much. Split or shorten it.
```

- [ ] **Step 3: The two implementer agents**

In `~/.dotfiles/claude/.claude/agents/cairn-implementer.md`, replace:

```markdown
- **No em dashes anywhere**, including comments and strings. A `prose-guard` hook rejects files
  that contain them. Write in a plain voice.
```

with:

```markdown
- **No em dashes anywhere**, including comments and strings. Cairn's `check:comments` Vale gate flags
  them in comments, and the em dash is a tell here. Write in a plain voice.
```

In `~/.dotfiles/claude/.claude/agents/site-implementer.md`, replace:

```markdown
- **No em dashes anywhere**, including comments and strings. A `prose-guard` hook rejects
  files that contain them. Write in a plain voice.
```

with:

```markdown
- **No em dashes anywhere**, including comments and strings. The em dash is a tell here, and the
  site's Vale config flags it where wired. Write in a plain voice.
```

- [ ] **Step 4: The reviewer subagent**

In `~/.dotfiles/claude/.claude/agents/prose-voice-reviewer.md`, replace:

```markdown
Start by naming the artifact's audience and opening its register. The routing table is in
`~/.claude/docs/prose-voice.md`, and the registers are in `~/.claude/docs/voice/`. Read the
```

with:

```markdown
Start by naming the artifact's audience and opening its register. The `writing-voice` skill is the
router, and the registers are in `~/.claude/docs/voice/`. Read the
```

- [ ] **Step 5: The calibration sample**

In `~/.dotfiles/claude/.claude/docs/voice/calibration-2026-06-09.md`, replace:

```markdown
Treat prose-guard post-hook feedback as a revision trigger, not noise. The feedback fires
```

with:

```markdown
Treat the `vale-hook` post-hook feedback as a revision trigger, not noise. The feedback fires
```

- [ ] **Step 6: The vale-hook docstring**

In `~/.dotfiles/bin/.local/bin/vale-hook`, replace:

```python
Not wired into settings.json yet; prose-guard stays the active hook until the cutover
plan. Invoke by piping the PostToolUse JSON on stdin.
```

with:

```python
Wired into settings.json as the PostToolUse prose hook (the cutover, plan 07). Invoke
by piping the PostToolUse JSON on stdin.
```

- [ ] **Step 7: Confirm the repoint and commit**

```bash
cd ~/.dotfiles
echo "-- these files must no longer name prose-guard or prose-voice.md --"
grep -lE 'prose-guard|prose-voice\.md' \
  claude/.claude/docs/authoring-charter.md \
  claude/.claude/docs/go-comment-voice.md \
  claude/.claude/agents/cairn-implementer.md \
  claude/.claude/agents/site-implementer.md \
  claude/.claude/agents/prose-voice-reviewer.md \
  claude/.claude/docs/voice/calibration-2026-06-09.md \
  bin/.local/bin/vale-hook || echo "ALL REPOINTED"
bash scripts/check-py-comments.sh
vale --minAlertLevel=error claude/.claude/docs/authoring-charter.md claude/.claude/agents/prose-voice-reviewer.md | tail -2
git add claude/.claude/docs/authoring-charter.md claude/.claude/docs/go-comment-voice.md \
  claude/.claude/agents/cairn-implementer.md claude/.claude/agents/site-implementer.md \
  claude/.claude/agents/prose-voice-reviewer.md claude/.claude/docs/voice/calibration-2026-06-09.md \
  bin/.local/bin/vale-hook
git commit -m "Repoint the prose-guard reference surface to the live Vale system" \
  -m "The charter, the Go comment voice doc, the two implementer agents, the prose-voice-reviewer, the calibration sample, and the vale-hook docstring now name the writing-voice skill and Vale. The content skills keep their prose-guard calls until the site migrations." \
  -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```

Expected: `ALL REPOINTED`, then `check:py-comments OK` (the vale-hook docstring edit still passes the Python arm), a clean Vale run, then the commit.

---

### Task 6: Retire prose-voice.md

Delete `prose-voice.md`. Its content distributed into the Skill (router and shape rules), the output style (voice), and CLAUDE.md (highest-frequency tells) in Tasks 1 through 3, and Task 5 repointed the last references. This task runs only after Tasks 2, 3, and 5.

**Files:**
- Delete: `~/.dotfiles/claude/.claude/docs/prose-voice.md`

**Interfaces:**
- Consumes: Tasks 2, 3, 5 (every reference repointed).
- Produces: nothing references `prose-voice.md`.

- [ ] **Step 1: Confirm no references remain**

```bash
cd ~/.dotfiles
grep -rln 'prose-voice\.md' claude/ bin/ scripts/ 2>/dev/null | grep -v 'prose-voice-reviewer' || echo "NO REFERENCES"
```

Expected: `NO REFERENCES`. If any file is listed, repoint it before deleting (do not proceed).

- [ ] **Step 2: Delete the file**

```bash
cd ~/.dotfiles
git rm claude/.claude/docs/prose-voice.md
```

- [ ] **Step 3: Confirm gone and commit**

```bash
cd ~/.dotfiles
test -f claude/.claude/docs/prose-voice.md && echo "STILL PRESENT" || echo "DELETED"
git commit -m "Retire prose-voice.md; its content distributed into the layers" \
  -m "The router and shape rules moved to the writing-voice skill, the voice to the output style, and the highest-frequency tells to CLAUDE.md. Nothing references it." \
  -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```

Expected: `DELETED`, then the commit.

---

### Task 7 (MAIN LOOP): Wire vale-hook into settings.json and prove it live

Add `vale-hook` as a PostToolUse `Write|Edit` hook, alongside `prose-guard` for now, and prove it fires as a real hook. The main loop executes this, because `settings.json` is one of the two untouched working-tree files and the active hook config this session runs under. Apply only the hook addition; leave Geoff's other `settings.json` edits intact.

**Files:**
- Modify: `~/.dotfiles/claude/.claude/settings.json` (the `PostToolUse` hooks array)

**Interfaces:**
- Consumes: `vale-hook` (plan 06), proven end to end.
- Produces: `vale-hook` wired as a PostToolUse hook, both it and `prose-guard` active (no feedback gap).

- [ ] **Step 1: Confirm current state**

```bash
cd ~/.dotfiles
python3 -c "import json;d=json.load(open('claude/.claude/settings.json'));print('valid JSON')"
grep -c 'vale-hook' claude/.claude/settings.json
```

Expected: `valid JSON`, then `0` (vale-hook not yet wired).

- [ ] **Step 2: Add the vale-hook PostToolUse entry**

In the `PostToolUse` array of `~/.dotfiles/claude/.claude/settings.json`, add a second hook entry for `vale-hook` alongside the existing `prose-guard --post-hook` entry. The `PostToolUse` array becomes:

```json
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "prose-guard --post-hook",
            "timeout": 10
          },
          {
            "type": "command",
            "command": "vale-hook",
            "timeout": 15
          }
        ]
      }
    ]
```

- [ ] **Step 3: Verify the JSON and the hook resolves**

```bash
cd ~/.dotfiles
python3 -c "import json;d=json.load(open('claude/.claude/settings.json'));print('valid JSON')"
command -v vale-hook
```

Expected: `valid JSON`, then the `vale-hook` path on PATH.

- [ ] **Step 4: Prove vale-hook fires as a real PostToolUse hook**

```bash
cd ~/.dotfiles
printf 'Clean opening line.\nA seamless tapestry here.\nClean closing line.\n' > docs/_wireproof.md
printf '{"tool_name":"Edit","tool_input":{"file_path":"%s/docs/_wireproof.md","new_string":"A seamless tapestry here."}}' "$PWD" | vale-hook; echo "[exit: $?]"
rm -f docs/_wireproof.md
```

Expected: the slop findings on stderr and `[exit: 2]` (the `glw907.Slop` rule still fires in docs; only the em-dash rule was turned off in Task 4). This confirms the wired command runs.

- [ ] **Step 5: Commit (stage only the hook change)**

`settings.json` also carries Geoff's uncommitted `model`-line removal. Stage only the vale-hook
addition, never his line. The main loop confirms the settings.json handling with Geoff before this
commit (his `model` change committed on its own, or he applies the flip himself), since `settings.json`
is one of the two files left for him.

```bash
cd ~/.dotfiles
git diff --cached claude/.claude/settings.json   # must show ONLY the vale-hook addition
git commit -m "Wire vale-hook into settings.json as the PostToolUse prose hook" \
  -m "Added alongside prose-guard so there is no feedback gap; the next task removes prose-guard's hooks once this is proven live." \
  -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```

Expected: the staged diff shows only the vale-hook addition.

---

### Task 8 (MAIN LOOP): Retire prose-guard's always-on hooks

Remove the `prose-guard` PreToolUse and PostToolUse hooks from `settings.json`, leaving `vale-hook` as the active prose hook. Keep the `prose-guard` script on disk, marked deprecated, as the content skills' backstop. The main loop executes this.

**Files:**
- Modify: `~/.dotfiles/claude/.claude/settings.json` (remove the prose-guard hooks)
- Modify: `~/.dotfiles/bin/.local/bin/prose-guard` (add a deprecation header)

**Interfaces:**
- Consumes: Task 7 (vale-hook proven live).
- Produces: `vale-hook` as the only prose hook; `prose-guard` unwired but callable.

- [ ] **Step 1: Remove the prose-guard PreToolUse block and the prose-guard PostToolUse entry**

In `~/.dotfiles/claude/.claude/settings.json`, remove the entire `PreToolUse` array (its only hook is `prose-guard --hook`) and remove the `prose-guard --post-hook` entry from the `PostToolUse` array, leaving `vale-hook` as the sole PostToolUse hook. The hooks object keeps `SessionStart`, `Notification`, and the `PostToolUse` array with only `vale-hook`.

- [ ] **Step 2: Verify the JSON and that prose-guard is gone from settings**

```bash
cd ~/.dotfiles
python3 -c "import json;d=json.load(open('claude/.claude/settings.json'));print('valid JSON')"
grep -c 'prose-guard' claude/.claude/settings.json
grep -c 'vale-hook' claude/.claude/settings.json
```

Expected: `valid JSON`, then `0` (no prose-guard), then `1` (vale-hook present).

- [ ] **Step 3: Mark the prose-guard script deprecated (keep it callable)**

In `~/.dotfiles/bin/.local/bin/prose-guard`, add a deprecation note to the module docstring (immediately after the opening `"""` line). The note reads:

```
DEPRECATED 2026-06-22 (cutover, plan 07): retired from the always-on hooks. Vale and the
vale-hook are the live prose feedback. This script remains only as the content skills'
explicit backstop (content-review, web-content-method) until the ECXC and 907 site
content migrations move content to Vale, then it is deleted.
```

- [ ] **Step 4: Confirm the script still runs and the content backstop works**

```bash
cd ~/.dotfiles
printf 'A clean test line.\n' > /tmp/_pg_check.md
prose-guard /tmp/_pg_check.md; echo "[exit: $?]"
rm -f /tmp/_pg_check.md
```

Expected: a clean run and `[exit: 0]` (the script is still callable for the content skills).

- [ ] **Step 5: Commit**

```bash
cd ~/.dotfiles
git add claude/.claude/settings.json bin/.local/bin/prose-guard
git commit -m "Retire prose-guard's always-on hooks; vale-hook is the live prose hook" \
  -m "Removed the PreToolUse and PostToolUse prose-guard hooks; vale-hook is the sole PostToolUse prose hook. The script stays on disk, marked deprecated, as the content skills' backstop until the site content migrations." \
  -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Self-Review

Run after the last task.

1. **The Skill routes:** `writing-voice/SKILL.md` carries the audience-to-register table, the shape rules, and the em-dash matrix (Task 1).
2. **The output style is lean and repointed:** it names the `writing-voice` skill, keeps the audience-invariant voice and the audience-conditional em-dash rule, and no longer references `prose-voice.md` or `prose-guard` (Task 2).
3. **CLAUDE.md routes:** the voice section is the lean routing layer, repointed off the old system (Task 3).
4. **The em-dash policy is applied:** `glw907.EmDash` is off for the docs section only; the agent-facing and Python sections still flag it; the fixtures pass (Task 4).
5. **The reference surface names the live system:** the charter, the Go comment doc, the two implementer agents, the reviewer, the calibration sample, and the vale-hook docstring (Task 5). `ts-conventions` and `python-conventions` were already correct; the content skills are intentionally untouched.
6. **prose-voice.md is gone** and nothing references it (Task 6).
7. **vale-hook is the live prose hook:** wired (Task 7), proven firing, and `prose-guard`'s always-on hooks are removed with the script kept as the content backstop (Task 8).
8. **No feedback gap:** `vale-hook` was live before `prose-guard` came out; docs feedback was continuous; comment coverage is the per-repo arms.
9. **Nothing unintended moved:** each task staged only its named files; `settings.json` carries only the hook change plus Geoff's pre-existing edits; the `cairn-pass/SKILL.md` untouched file is still untouched.
