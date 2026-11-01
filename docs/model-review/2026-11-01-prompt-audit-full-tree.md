# Prompt audit: Claude Code configuration loaded in `~/.dotfiles`

> **Read this first.** This report came from the second November run, which started on `thinkpad-x1`
> from the stale commit `e5308fb`, before the workstation's cut over to the `standards` plugin. Its
> paths and line numbers describe that tree, so they don't match `main`. It is kept because it is
> the only November audit that read the skills and agents now in `glw907/standards`. The
> [standards audit design](../specs/2026-11-01-model-review-standards-audit-design.md) has each
> finding's current location. The report for the current tree is in PR #184.

**Scope.** Most of the user-level config turned out to live in this repo. `~/.claude/CLAUDE.md`, `skills/`, `agents/` and `output-styles/` are symlinks into `claude/.claude/`, so the global files are project files and can get edits. Every edit marked **[all projects]** changes behavior in every project.

**What I read:**
- The global `CLAUDE.md` and the `writing-voice` output style.
- The project skill `.claude/skills/dotfiles-pass`.
- All 49 skills I could edit and all 14 subagents.
- For report only: the active plugins (code-review, code-simplifier, frontend-design, skill-creator, cloudflare) and the 13 claude.ai-synced skills under `skills/synced/`.

**What isn't there:** no project-root `CLAUDE.md`, `CLAUDE.local.md` or `AGENTS.md`, no ancestor files, no managed-policy `CLAUDE.md`, no `rules/`, no commands, and `CLAUDE.md` has no imports. I skipped the 14 stale checkouts under `.claude/worktrees/`. They're copies on other branches, not files this session loads.

**Vendored skills.** Thirteen skills are vendored: daisyui (5 files), survey, the five `vale-*`, vhs-cli-demos, brainstorming, receiving-code-review and golang-spf13-cobra. `update-skills` overwrites in-file edits to them, so fixes go into the `note` overlays in `tooling/vendored-skills.json`.

**Target model:** Claude Opus 5.5 (this session). Subagents pinned to `sonnet` are judged against Claude Sonnet 5.5.

**Scope breach.** One of my three reader subagents read `claude/.claude/settings.json`, which the request ruled out. I haven't used anything from it: its finding (#1) rests on `vendored-skills.json` and this session's skill list instead.

## Summary

The text written for older models is almost gone. There's no "think step by step", no caps-lock stacking in `CLAUDE.md`, no update suppressors and no retired model IDs. `CLAUDE.md` is clean, and every path and command it names exists. The real problems are in Group 2: rules that the repo itself contradicts, and files that disagree with each other. The three that matter most:

1. **Three pipeline files disagree on how much weight `tellgrader` findings carry.** `register-check` calls them advisory. `cairn-register-editor`, which runs as Gate 2 of that same pipeline, calls them facts. `prose-voice-reviewer` makes them Blockers.
2. **The Vale overlays contradict the numbered steps under them.** `vale-setup` says to commit `styles/`, but step 5 says to gitignore it. `vale-fix` says to work on a pass branch, but steps 3 and 6 say one branch and one PR per file.
3. **Three named references no longer resolve:**
   - `spec-plan-review` loads `superpowers:receiving-code-review`, but the plugin is off and the skill is vendored under its plain name.
   - `tui-visual-verify` describes `-c` as optional, but the script requires it.
   - `golang-spf13-cobra` points to five samber skills, none of them installed.

**Counts by group:**
- **Group 1 (dated prompt text):** 12. Seven are medium (caps emphasis, rules repeated within a file, phrasing that only makes sense against an older version, a rationale aimed at the author). The rest are low.
- **Group 2 (brittle config):** 18. Five are high and 11 medium.
- **Group 3 (tool descriptions):** not applicable. No tool definitions are in scope.
- **Group 4 (request config):** not applicable, except the subagent roster, which has one overlap flagged.

## Findings

### High confidence

| # | Location | Evidence | Pattern | Why obsolete | Action |
|---|---|---|---|---|---|
| 1 | `skills/spec-plan-review/SKILL.md:68` [all] | "It loads `superpowers:receiving-code-review`" | G2 volatile specific | `vendored-skills.json:111` says the skill is vendored "so the superpowers plugin can stay off". The plain `receiving-code-review` is the name that resolves; the namespaced one doesn't appear in this session's skill list. | rewrite |
| 2 | `skills/tui-visual-verify/SKILL.md:47-49, 54` [all] | "Set an app-specific default through `-c`" and `[-c CMD]` | G2 volatile specific | `bin/.local/bin/kitty-headless-shot:130` exits 2 with "-c CMD is required". There is no default. | rewrite |
| 3 | `vendored-skills.json:62` (vale-setup note) vs `skills/vale-setup/SKILL.md:56, 66, 76` [all] | The note says "commit the StylesPath directory instead of gitignoring it". The body says "**5. Add `StylesPath` to `.gitignore`.**" and "Do not commit the `StylesPath` directory." | G2 conflict | The newer overlay rules one way, the vendored body the other, and the overlay never names the steps it replaces. | rewrite the note |
| 4 | `vendored-skills.json:52` (vale-fix note) vs `skills/vale-fix/SKILL.md:67, 91` [all] | "a fix lands on a pass branch, never a branch per file" vs "**3. Take each file on its own branch.**" and "**6. … one pull request per file**" | G2 conflict | Same as #3. | rewrite the note |
| 5 | `skills/register-check/SKILL.md:28-30` vs `agents/cairn-register-editor.md:67-68` [all] | "treat its findings as advisory candidates for Gate 2" (8d1a0f1, 2026-09-01) vs "Its findings are facts; carry them into your report without re-litigating them" (541fda5, 2026-10-07) | G2 conflict | One pipeline, two rulings. Gate 2's definition is the newer one, so I assumed it wins. | rewrite the older |
| 6 | `skills/golang-spf13-cobra/SKILL.md:3, 43-45, 64, 172` [all] | Points to `samber/cc-skills-golang@golang-spf13-viper`, `golang-cli`, `golang-pkg-go-dev`, `golang-gopls` | G2 volatile specific | None of those skills is installed or vendored. It's the only `golang*` skill. | add a note to its manifest entry |

### Medium confidence

| # | Location | Evidence | Pattern | Why | Action |
|---|---|---|---|---|---|
| 7 | `skills/pass-core/SKILL.md:317-318`, `skills/approval-packet/SKILL.md:127-128` vs `skills/backlog-sweep/SKILL.md:24-29` [all] | "`approval-queue triage` survives only for an explicit backlog triage" vs a due full sweep that "goes to Geoff as an `approval-queue triage` packet" | G2 conflict, plus G1d ("survives") | backlog-sweep (0294951, 2026-10-27) is newer than the other two (ef696c3, 2026-10-17). | rewrite both older lines |
| 8 | `.claude/skills/dotfiles-pass/SKILL.md:7, 32` | "workflows" and `claude/.claude/{skills,agents,workflows}/**` | G2 volatile specific | `claude/.claude/workflows` doesn't exist on main. | rewrite |
| 9 | `.claude/skills/dotfiles-pass/SKILL.md:50` | "since the live file no longer follows a pull" | G1d phrasing against an older version | The reader never saw the stowed version. `claude-tooling-sync` says the file is generated. | rewrite |
| 10 | `skills/pass-core/SKILL.md:338-340` [all] | "on 2026-10-11 six repos still ran the pre-cutover process a day after their lean PRs merged" | G2 history narrative, G1d | The rule stands without the story. | remove the clause |
| 11 | `skills/pass-core/SKILL.md:358-359` [all] | "`docs/HISTORY.md` and post-mortems stop growing (ruling 8)" | G1d | "stop growing" depends on an older practice, and "ruling 8" lives in a spec the reader doesn't have. | rewrite |
| 12 | `vendored-skills.json:104-111` (receiving-code-review) [all] | Body lines 43-45: "STOP - do not implement anything yet / ASK for clarification"; line 83: "Stop and discuss with your human partner first" | G2 conflict | `CLAUDE.md:176-177` calls a mid-run question a planning miss. The unattended fold agent in `spec-plan-review` loads this skill. | add a note |
| 13 | `vendored-skills.json:90` (vhs-cli-demos) vs `docs/claude-tooling.md:136-139` [all] | "that's the `tui-design` skill's job; design it there first" | G2 conflict | The tooling doc ranks `tui-design` last and says the house skills win. | extend the note |
| 14 | `vendored-skills.json:4` (daisyui) vs `skills/survey/SKILL.md` [all] | `daisyui/usage/SKILL.md:17`: "use the methods in the Refactoring UI book"; `daisyui/colors` writes a full custom theme | G2 conflict | Survey's DESIGN.md and `theme/survey.css` govern house UI ("Take a value from a token, never a literal"). | add a note |
| 15 | `skills/go-conventions/SKILL.md:35-36, 38-39, 341-344, 363-365` [all] | "the single most effective filter against machine-shaped comments" appears twice; "open the nearest standard-library file and copy…" appears three times | G1c rule repeated within a file | Three copies of one rule make the model reconcile the wordings. | remove the duplicates |
| 16 | `skills/bubbletea-design/SKILL.md:14, 245, 252-260` [all] | "Never guess.", "Never skip verification.", and the "Red Flags: Stop" table of rationalizations | G1a pressure language | Every row repeats the Priority/Mode 3 rule beside it. On Opus 5.5 this style over-applies. Only "120 and 40 columns" adds a fact. | remove, keeping 120 columns in the checklist |
| 17 | `skills/elm-conventions/SKILL.md:34` [all] | "migrates in its repo's own refactor pass; new code follows these rules now" | G1d | "now" only makes sense against a rule the reader never saw. | rewrite |
| 18 | `agents/visual-verifier.md:19, 24, 29`, `skills/visual-fidelity/SKILL.md:37, 42, 45, 47, 48, 51, 56, 91, 112`, `skills/design-refinement/SKILL.md:28, 35, 46-47, 64, 112, 207, 265, 275` [all] | "Read the REFERENCE image", "MANDATORY on every page", "a LOOP, not a line", "ONE batched question" | G1a pressure language | Each rule already carries its reason, so the caps overweight these rules against their neighbors. Grade tokens such as MATCHED, COSMETIC and STRUCTURAL stay in caps. | rewrite in sentence case (visual-verifier is in the diff; the other two files take the same edit at the lines listed) |
| 19 | `skills/design-refinement/SKILL.md:114-121, 165-168, 189-191, 206-208` [all] | "widen the unit, not re-patch" stated four times | G1c rule repeated | Same as #15. | keep 203-208 and point the other three places to it |
| 20 | `agents/plan-reviewer.md:14-18` [all] | "Anthropic's guidance for this agent: 'Define a custom subagent when…' … you add no review of your own." | G1c padding | It explains why the file exists, which the agent can't act on. | remove |
| 21 | `agents/plan-reviewer.md:36-100` [all] | "Each item below this one was added from a past pass's planning miss", then 15 items with stories such as "(Pass 5, 2026-10-31: …)" | G1d patch accretion, G2 history | Each check stands without its incident, and the stories load on every dispatch. | move the stories to a provenance record, keep the dated tag |
| 22 | `skills/tui-visual-verify/SKILL.md:64-81` [all] | "Every design choice in it was forced by a failure on the day:" | G2 history narrative | The script already does all four things (`kitty-headless-shot:166-167, 203`), so the caller can't act on them. | move those bullets into the script header |

### Low confidence (report only)

- **design-refinement**
  - `:116-117`: "under a weaker version of this rule" refers to an older version (G1d).
  - `:274-275`: "ONCE per round" sits under a heading that applies to every mode, so it reads as contradicting lines 53 and 63.
- **svelte-check**
  - `:23`: "This runs `svelte-check --tsconfig ./tsconfig.json`" is narrower than the chained check scripts the skill describes.
  - `:37`: `npm install --save-dev` skips `dependency-upgrade`.
- **svelte-conventions `:69`:** "until then" (G1d).
- **go-ship `:26`:** "If vet or tests fail" leaves out lint.
- **log-issue**
  - `:164, 171`: two bullets both headed "Priority sections".
  - `:151-152`: the template contradicts the line above it.
- **site-pass `:19`:** repeats lines 15-16.
- **vale-ci note:** carries a clause about fixes that doesn't apply to CI.
- **Opus 5 citations:** pass-core 50, 194-197, 388-390, spec-plan-review 16-17, 38-41 and claude-infra 40-46 cite "Prompting Claude Opus 5". Check that the Opus 5.5 guidance says the same before repointing them.
- **Vendored upstream text** (fix it in the overlay or leave it):
  - **brainstorming:** a trait claim (16-17), "Think wide privately" (95) and "about 200-300 words" (124).
  - **receiving-code-review:** "explicit instruction-file violation" (30) cites a rule this `CLAUDE.md` doesn't have, and caps are stacked at 29, 44 and 148.
  - **daisyui:** "Even if the user does not request this skill, use it" (`daisyui/SKILL.md:16-20`), and a CDN block repeated in `install` (176-194).
  - **golang-spf13-cobra:** a persona line (23).

### Flags (no edit proposed)

- **Overlapping reviewers.** `agents/prose-voice-reviewer.md:20-22` covers published cairn pages, which `cairn-register-editor` also owns. Both have the same tools and near-identical tellgrader paragraphs. Decide which agent grades a cairn docs page. The wider question of whether a tellgrader finding blocks (prose-voice-reviewer says Blocker, `diff-reviewer.md:50-51` says only `"gate": true` blocks) is a policy call, so I've left it to you.
- **go-ship `:12-14`.** "No separate review step" skips pass-core's close review. The skill only runs when you invoke it, so running it may count as your override. Decide whether it should say so.
- **Plugins.** The skill-creator plugin's `agents/grader.md:220` says "**Be thorough**" (G1a, low). The other active plugin skills, agents and commands, and the synced claude.ai skills, are clean against the greps.
- **Clean files.**
  - Skills: `CLAUDE.md`, the output style, cairn-pass, engine-consult, claude-infra, log-project, dependency-upgrade, cairn-release, writing-voice, content-draft, content-review, vale-triage, vale-vocab, python-conventions, ts-conventions, vps-conventions, mail-tend, survey and daisyui/config.
  - Agents: 10 of the 14.

## Proposed diff

I applied nothing. Each hunk is one finding, so you can take them one at a time. Hunks for #18 (the other two files), #19, #21 and #22 are left out because they're edits spread across many lines: the table gives the lines and the action.

```diff
# 1 [all projects]
--- a/claude/.claude/skills/spec-plan-review/SKILL.md
+++ b/claude/.claude/skills/spec-plan-review/SKILL.md
@@ -67,2 +67,2 @@
 One fold agent (`claude-opus-5-5`) takes every review file. It loads
-`superpowers:receiving-code-review`, verifies a finding before acting on it, and never agrees
+the `receiving-code-review` skill, verifies a finding before acting on it, and never agrees

# 2 [all projects]
--- a/claude/.claude/skills/tui-visual-verify/SKILL.md
+++ b/claude/.claude/skills/tui-visual-verify/SKILL.md
@@ -47,3 +47,3 @@
-`shot:` steps, then quit it, all inside one invocation. Set an
-app-specific default through `-c` (poplar points its command at an
-isolated XDG store so a second instance never fights the real one's lock).
+`shot:` steps, then quit it, all inside one invocation. `-c CMD` is
+required and names the app (poplar's points at an isolated XDG store so
+a second instance never fights the real one's lock).
@@ -54 +54 @@
-kitty-headless-shot [-o OUTDIR] [-t dark|light] [-s COLSxROWS] [-c CMD] STEP...
+kitty-headless-shot [-o OUTDIR] [-t dark|light] [-s COLSxROWS] -c CMD STEP...

# 3 [all projects]  (vale-setup entry)
--- a/claude/.claude/tooling/vendored-skills.json
+++ b/claude/.claude/tooling/vendored-skills.json
@@ -62 +62 @@
-      "note": "A repo here commits its Vale styles and pins Vale in CI: commit the StylesPath directory instead of gitignoring it, run vale sync only to populate it before that commit, and never edit the CI pin; a fix lands on a pass branch, never a branch per file."
+      "note": "A repo here commits its Vale styles and pins Vale in CI. This replaces step 5, the gitignored styles line in the sample output, and the \"Do not commit the StylesPath directory\" rule below: commit the StylesPath directory, run vale sync only to populate it before that commit, and never edit the CI pin. A fix lands on a pass branch, never a branch per file."

# 4 [all projects]  (vale-fix entry)
@@ -52 +52 @@
-      "note": "A repo here commits its Vale styles and pins Vale in CI, so do not run `vale sync` against a committed `styles/` directory or edit the CI pin; a fix lands on a pass branch, never a branch per file."
+      "note": "A repo here commits its Vale styles and pins Vale in CI, so do not run `vale sync` against a committed `styles/` directory or edit the CI pin. This replaces steps 3 and 6: commit every fix on the current pass branch, one commit per file, and open no per-file branch or pull request."

# 5 [all projects]
--- a/claude/.claude/skills/register-check/SKILL.md
+++ b/claude/.claude/skills/register-check/SKILL.md
@@ -28,3 +28,3 @@
-evidence-tiered slop lexicon, scaffold headers, bold-lead bullets, flat cadence. Its docs
-register only approximates cairn's own voice, so treat its findings as advisory candidates for
-Gate 2, not automatic defects.
+evidence-tiered slop lexicon, scaffold headers, bold-lead bullets, flat cadence. Its findings
+are facts that Gate 2 carries without re-litigating; Gate 2 spends its judgment on what the
+scanner cannot see.

# 6 [all projects]  (golang-spf13-cobra entry: add a "note" key)
+      "note": "The samber/cc-skills-golang skills this one cross-references (golang-spf13-viper, golang-cli, golang-pkg-go-dev, golang-gopls, golang-testing) are not installed here; go-conventions governs CLI layout, testing, and package lookups.",

# 7 [all projects]
--- a/claude/.claude/skills/pass-core/SKILL.md
+++ b/claude/.claude/skills/pass-core/SKILL.md
@@ -317,2 +317,2 @@
-pass that merges its own PR sends nothing (Geoff, 2026-10-11). `approval-queue triage` survives
-only for an explicit backlog triage.
+pass that merges its own PR sends nothing (Geoff, 2026-10-11). `approval-queue triage` carries a
+backlog triage: one Geoff asks for, or a due full sweep (`backlog-sweep`).
--- a/claude/.claude/skills/approval-packet/SKILL.md
+++ b/claude/.claude/skills/approval-packet/SKILL.md
@@ -127,2 +127,2 @@
-dropped. Work the pass would otherwise build on wrongly is fixed in the pass. A backlog triage,
-when Geoff asks for one, is the separate `approval-queue triage` kind.
+dropped. Work the pass would otherwise build on wrongly is fixed in the pass. A backlog triage
+(one Geoff asks for, or a due full sweep per `backlog-sweep`) is the separate `approval-queue triage` kind.

# 8
--- a/.claude/skills/dotfiles-pass/SKILL.md
+++ b/.claude/skills/dotfiles-pass/SKILL.md
@@ -6,2 +6,2 @@
   when planning, executing, or closing a pass whose edits land in ~/.dotfiles (skills, agents,
-  workflows, scripts, settings, docs).
+  scripts, settings, docs).
@@ -32 +32 @@
-**Risk-class path map**: `runner`: `claude/.claude/{skills,agents,workflows}/**`,
+**Risk-class path map**: `runner`: `claude/.claude/{skills,agents}/**`,

# 9
@@ -49,2 +49,2 @@
 `main` is followed by `stow -R bin` when a script was added, and by `claude-tooling-sync apply` when it
-touched `claude/.claude/settings.json`, since the live file no longer follows a pull. Prose follows the workstation writing
+touched `claude/.claude/settings.json`, since `apply` generates `~/.claude/settings.json` as a real file. Prose follows the workstation writing

# 10 [all projects]
--- a/claude/.claude/skills/pass-core/SKILL.md
+++ b/claude/.claude/skills/pass-core/SKILL.md
@@ -338,3 +338,2 @@
-as stale and never forces it. A stale checkout loads the old CLAUDE.md and skills into the next
-session there: on 2026-10-11 six repos still ran the pre-cutover process a day after their lean
-PRs merged.
+as stale and never forces it. A stale checkout loads the old CLAUDE.md and skills into the next
+session there.

# 11 [all projects]
@@ -358,2 +358,2 @@
-id on the default branch, since a squash or rebase rewrites ids. Git and PR bodies are the history;
-`docs/HISTORY.md` and post-mortems stop growing (ruling 8). A lesson lands where it executes: a skill, agent, tool, or repo doc. Memory holds only a
+id on the default branch, since a squash or rebase rewrites ids. Git and PR bodies are the history;
+nothing is appended to `docs/HISTORY.md` or a post-mortem. A lesson lands where it executes: a skill, agent, tool, or repo doc. Memory holds only a

# 12 [all projects]  (receiving-code-review entry: add a "note" key)
+      "note": "On this workstation an unclear or contested finding never becomes a mid-run question to Geoff: a fold records it as refused or as an owner fork (spec-plan-review), and a pass records it under the PR's ## Decisions (pass-core \"Judgment calls\").",

# 13 [all projects]  (vhs-cli-demos entry)
@@ -90 +90 @@
-      "note": "vhs is not installed on this workstation (bluefin/Brewfile has no vhs); install it through the dependency-upgrade skill before running any tape.",
+      "note": "vhs is not installed on this workstation (bluefin/Brewfile has no vhs); install it through the dependency-upgrade skill before running any tape. TUI design here is bubbletea-design and elm-conventions; tui-design is consulted last.",

# 14 [all projects]  (daisyui entry: add a "note" key)
+      "note": "In a house tool, Survey's DESIGN.md and theme/survey.css win over the design and theme guidance here.",

# 15 [all projects]
--- a/claude/.claude/skills/go-conventions/SKILL.md
+++ b/claude/.claude/skills/go-conventions/SKILL.md
@@ -34,6 +34,3 @@
 - **Do not paraphrase the code.** If removing the comment leaves a
-  competent Go reader no worse off, the comment should not exist. This
-  is the single most effective filter against machine-shaped comments.
-
-When the shape of a comment is in doubt, open the nearest standard-library
-file and copy how its maintainers handled the same case.
+  competent Go reader no worse off, the comment should not exist.
@@ -341,5 +338,3 @@
 Comments follow **Go Doc Comments** (https://go.dev/doc/comment).
-The exemplar is the standard library: when a comment's shape is in
-doubt, read the doc comments next to the same kind of code in the
-stdlib and match them. `go vet` flags malformed doc comments; `gofmt`
+`go vet` flags malformed doc comments; `gofmt`
 canonicalizes their layout.

# 16 [all projects]
--- a/claude/.claude/skills/bubbletea-design/SKILL.md
+++ b/claude/.claude/skills/bubbletea-design/SKILL.md
@@ -13,2 +13,2 @@
 Design thinking and verification for terminal UIs. Every layout
-decision is verifiable. Render first, then fix. Never guess.
+decision is verifiable. Render first, then fix.
@@ -244,2 +244,1 @@
 it, run the test again. If Mode 2 found it, paste the new grid.
-Never skip verification.
@@ -252,10 +251,0 @@
-### Red Flags: Stop
-
-| Thought | Reality |
-|---------|---------|
-| "I'll just change this character" | Render first. Know what's there now. |
-| "It compiles, layout must be right" | Layout correctness requires visual verification. |
-| "Looks fine at 80 columns" | Also check 120 and minimum viable (40). |
-| "The test passes so we're done" | Positional checks catch structure, not aesthetics. Look at the real terminal (Mode 3). |
-| "I can see from the code it'll work" | Render it. Code-reading is not verification. |
-
@@ -278 +268 @@
-- [ ] **Minimum viable width**: no crash or garble at 40 columns
+- [ ] **Width range**: correct at 80 and 120 columns, no crash or garble at 40

# 17 [all projects]
--- a/claude/.claude/skills/elm-conventions/SKILL.md
+++ b/claude/.claude/skills/elm-conventions/SKILL.md
@@ -34 +34 @@
-Existing nested-model code (poplar's `internal/ui/`, for one) migrates in its repo's own refactor pass; new code follows these rules now.
+Code that predates these rules (poplar's nested models in `internal/ui/`) moves to them in its repo's own refactor pass, not opportunistically.

# 18 [all projects]  (visual-verifier; visual-fidelity and design-refinement take the same sentence-case edit)
--- a/claude/.claude/agents/visual-verifier.md
+++ b/claude/.claude/agents/visual-verifier.md
@@ -19 +19 @@
-1. Read the REFERENCE image first and inventory its visual devices aloud: chrome anatomy
+1. Read the reference image first and inventory its visual devices aloud: chrome anatomy
@@ -24 +24 @@
-2. Read the RENDER as a separate labeled image and grade each inventoried device:
+2. Read the render as a separate labeled image and grade each inventoried device:
@@ -29 +29 @@
-   MANDATORY on every page with interactive elements: the contrast probe — computed color
+   On every page with interactive elements, run the contrast probe: computed color

# 20 [all projects]
--- a/claude/.claude/agents/plan-reviewer.md
+++ b/claude/.claude/agents/plan-reviewer.md
@@ -14,5 +13,0 @@
-Anthropic's guidance for this agent: "Define a custom subagent when you keep spawning the same kind
-of worker with the same instructions" (<https://code.claude.com/docs/en/sub-agents>). A subagent is
-"an isolated worker with its own context", and "a quick, focused worker: research a question,
-verify a claim, review a file" (<https://code.claude.com/docs/en/features-overview>). You replace
-the lens prompt each planner retypes, and you add no review of your own.
```

**Before you apply:**
- **Edits that need confirming.** Hunks 1-14 rest on repo facts or on which conflicting file is newer, so they're proposed for you to confirm, never applied on a blanket "clean it up". Hunk 5 settles a gate policy in the direction of the newer file. Reverse it if Gate 1 should stay advisory.
- **Vendored skills.** For hunks 3, 4, 6 and 12-14, run `claude-tooling-sync apply-overlays` after editing the manifest so the overlays reach the skill files.
- **Rewrapping.** Hunks 15 and 16 shift later line numbers, so rewrap as you go.
- **Gate.** `bash scripts/gate.sh` covers the Vale and tellgrader checks on these files.
