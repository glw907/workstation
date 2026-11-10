# Prompt audit of the standards plugin: path-form probe

Run 2026-11-10 with `claude -p --model opus --effort medium "/doctor prompt-audit plugins/standards"`
from a detached checkout of `glw907/standards` at `origin/main` (`148d5fd`). The path form read the
plugin's files: the report cites `file:line` evidence from the 9 agents and the process skills, so
the design's step 1 stands. The report follows unedited.

---

I audited `plugins/standards` against Opus 5.5. It's mostly clean: 14 findings, none of them severe, and nothing that fails on the target model. I didn't edit any files; the proposed diff is below, one finding per hunk.

## Assumptions

- **Scope.** Everything under `plugins/standards` (150 files). I read all 9 agents and the process skills in full. The rest I covered with the pattern greps. The vendored DaisyUI component pages, the cobra skill, and the vale skills only got the greps, and none of them hit. I didn't audit `bin/`, the brainstorming server scripts, or the VHS TypeScript assets, since they aren't prompt text.
- **Target model.** Opus 5.5 throughout. Every agent sets `model: claude-opus-5-5`. The skills run under the session model, which is the one running this audit.
- **Vendored files.** `receiving-code-review` and `brainstorming` come from obra/superpowers at `bb92a77`, per `THIRD-PARTY-NOTICES`. Taking hunks there means the files drift further from upstream.

## Summary

There are three findings worth acting on:
- **`spec-plan-review` rests on the Opus 5 prompting page.** That's where its "no verification read" rule comes from. Anthropic's Opus 5.5 guidance lists exactly those over-verification instructions as ones to re-test.
- **`plan-reviewer`'s checklist is growing one item per incident.** It got about 20 items in ten days, and two of them repeat the lens rule above them.
- **Three skills shout in all caps:** `visual-fidelity` (26 words), `design-refinement` (25) and `receiving-code-review` (21). Nearly none of it marks a real constraint.

| Group | Findings |
|---|---|
| 1. Dated prompt text | 6 |
| 2. Brittle skill and config files | 5, plus 3 flagged |
| 3. Descriptions | 0 (the agent and skill descriptions are routing text and fine) |
| 4. Request config | Not applicable: there's no request code. The 9-agent roster has no redundant pair. |

## Findings

| # | Location | Evidence | Pattern | Why it no longer fits | Conf. | Action |
|---|---|---|---|---|---|---|
| 1 | `skills/tui-visual-verify/SKILL.md:49-50` | "The host's ImageMagick has no X11 delegate and the GNOME screenshot portal is denied…" | G2 volatile specifics | Describes one workstation. The README says the plugin assumes "no machine-specific tool or path." | High | rewrite |
| 2 | `skills/spec-plan-review/SKILL.md:14-16, 36-41` | "(Opus 5 prompting page)"; "the Opus 5 page says to remove 'separate verification steps'" | 1d workaround for an older model; G2 pinned model name | Opus 5.5 guidance says Opus 5's over-verification instructions "may no longer be needed… re-test each." Keep the rule, but ground it in cost, not in an older model's page. | Medium | rewrite |
| 3 | `agents/plan-reviewer.md:28, 90-92` | "quoted from the docs or the source"; "carries the `file:line` that shows it" | 1c repetition | Both repeat the lens rule at lines 22-23 ("never from memory"). | Medium | rewrite (merge) |
| 4 | `agents/plan-reviewer.md:14-18` | "Anthropic's guidance for this agent: 'Define a custom subagent when…'" | Step 3 / G2 verbose | This explains to the maintainer why the agent exists. The agent can't act on it. | Medium | remove |
| 5 | `skills/visual-fidelity/SKILL.md` (26 words) | "matching ALL features", "READS", "a LOOP, not a line", "FRESH", "SEPARATE LABELED" | 1a pressure language | Current models over-apply emphasis. With this many caps, none of them carries signal. | Medium | rewrite |
| 6 | `skills/design-refinement/SKILL.md` (25 words) | "DISCOVER", "ONE batched question", "PROBE PAGE", "RATIFIED", "WIDEN" | 1a | Same as #5. | Medium | rewrite |
| 7 | `skills/receiving-code-review/SKILL.md:27-38, 139-148` | "**NEVER:** 'You're absolutely right!'"; "DELETE IT." | 1e list of banned phrases | A list of tics written against older models' sycophancy. State the wanted reply in one line. | Medium | rewrite |
| 8 | `skills/receiving-code-review/SKILL.md:30` | "(explicit instruction-file violation)" | G2 stale fact | Points to an instruction file from the upstream author's setup. No such rule exists here or in a consumer repo. | Medium | rewrite (in #7's hunk) |
| 9 | `skills/receiving-code-review/SKILL.md:16-25` | "1. READ … 6. IMPLEMENT" pseudocode | 1c step-by-step choreography | A scripted sequence for a judgment task. The outcome stated in prose does the same work. | Medium | rewrite |
| 10 | `skills/visual-fidelity/SKILL.md:12-15, 81-85`; `design-refinement/SKILL.md:49-51, 80-81`; `agents/visual-verifier.md:32-33`; `agents/plan-reviewer.md:96-97` | "Born from production visual misses…"; "The ASC register round is the proven exemplar"; "three verifiers missed … (2026-07-06)"; "ran five rounds this way" | G2 history narratives | A rule's authority comes from the behavior it prescribes. "ASC" also means nothing to an outside user of the plugin. | Medium | rewrite |
| 11 | `skills/brainstorming/SKILL.md:118` | "describe that part back in about 200-300 words" | 1b numeric length cap | A fixed word count tuned to an older model's verbosity. Describe the size instead. | Medium | rewrite |
| 12 | `agents/plan-reviewer.md:25-97` | About 20 items added from 2026-10-31 to 2026-11-09, one commit per incident | 1d patch accretion; G2 recency trap | Each item records a real miss, so this is context only you have. Whether to regroup it under a few principles is your call. | Low | flag |
| 13 | `agents/plan-reviewer.md:59-62` | "anthropics/claude-code#73453 ends the run" | G2 volatile specific | Goes stale once the issue is fixed. Check it whenever this file changes. | Low | flag |
| 14 | `visual-fidelity:4-5`, `tui-visual-verify:114-124` vs `spec-plan-review:36-41` | "fresh-context verifiers outperform self-critique" vs "do not use subagents to verify" | G2 conflict (scoped) | Each rule is scoped to its own task, so this is an override, not a conflict. But they cite Anthropic in opposite directions. #2 removes the side that's out of date. | Low | flag |

**Kept on purpose.** Five agents say "report every finding… coverage beats self-filtering," which matches current guidance. `design-refinement:285-291` names specific AI-default looks, the form the audit guide says to keep. `web-auth-security-reviewer` says "Default to suspicion," and that's a real stance. The incident lessons in `tui-visual-verify:63-98` are part of the tool's contract.

## Proposed diff

```diff
--- a/plugins/standards/skills/tui-visual-verify/SKILL.md   [#1]
@@ -47,6 +47,4 @@
 app-specific default through `-c` (for example, point the command at an
 isolated XDG store so a second instance never fights the real one's lock).
-The host's ImageMagick has no X11 delegate and the GNOME screenshot portal
-is denied or interactive, so no on-desktop route exists to fall back on.
+Prefer the container over an on-desktop capture route: it never touches the owner's display.

--- a/plugins/standards/skills/spec-plan-review/SKILL.md   [#2]
@@ -13,5 +13,5 @@
 them without over-engineering the document. The reviewers stay wide and the fold stays selective.
 Reviewers asked to report only high-severity issues "may follow that instruction literally and
-report less; ask it to report everything and filter in a separate pass instead" (Opus 5 prompting
-page). Claude Code best practices name the opposite risk: "Chasing every finding leads to
+report less; ask it to report everything and filter in a separate pass instead" (Anthropic's
+prompting guidance). Claude Code best practices name the opposite risk: "Chasing every finding leads to
@@ -36,6 +36,5 @@
 **Depth scales with risk.** A design of a page or less needs no separate spec. A plan gets the
 mechanics lens and the fold only. A spec otherwise takes the three lenses and the fold, with no
-verification read: the Opus 5 page says to remove "separate verification steps" and "do not use
-subagents to verify or double-check your own work" (Prompting Claude Opus 5,
-<https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5>).
+verification read, because on an ordinary pass a second read costs more than the defects it
+catches.
 The three lenses and the verification read are kept for `auth-data` and `live-account` passes

--- a/plugins/standards/agents/plan-reviewer.md   [#3]
@@ -22,3 +22,4 @@
 Does every mechanism behave as stated? Verify empirically (a scratch module in a temp directory, a
-probe run with Bash) or by quoting the docs or source (WebFetch, Read), never from memory.
+probe run with Bash) or by quoting the docs or source (WebFetch, Read), never from memory. Every
+mechanism of existing code the plan asserts carries the `file:line` that shows it.
@@ -28,1 +28,0 @@
-- Every library or stdlib behavior a task relies on is quoted from the docs or the source.
@@ -90,3 +89,0 @@
-- Every mechanism of existing code that the design or plan asserts (where a file lives, how an
-  auth flow binds a token, what a permission can read, what a consumer loads, what a release step
-  packs) carries the `file:line` that shows it.

--- a/plugins/standards/agents/plan-reviewer.md   [#4]
@@ -13,7 +13,2 @@
 dispatching session saves it.
-
-Anthropic's guidance for this agent: "Define a custom subagent when you keep spawning the same kind
-of worker with the same instructions" (<https://code.claude.com/docs/en/sub-agents>). A subagent is
-"an isolated worker with its own context", and "a quick, focused worker: research a question,
-verify a claim, review a file" (<https://code.claude.com/docs/en/features-overview>). You replace
-the lens prompt each planner retypes, and you add no review of your own.
+You hold the lens prompt each planner would otherwise retype, and add no review of your own.

--- a/plugins/standards/skills/visual-fidelity/SKILL.md   [#5]
@@ -19,3 +19,3 @@
-1. **The original manifest is the backbone** (be aggressive about reviewing the
-   original and matching ALL features and content). The original is the
+1. **The original manifest is the backbone**: review the original and match every
+   feature and all of its content. The original is the
@@ -35,1 +35,1 @@
-2. **Device catalogue.** An agent that reads images READS the references plus the
+2. **Device catalogue.** An agent that reads images reads the references plus the
@@ -38,1 +38,1 @@
-   stamps, links, quotes, code), color PLACEMENT (where each hue actually lands). Exact
+   stamps, links, quotes, code), color placement (where each hue actually lands). Exact
@@ -40,1 +40,1 @@
-3. **Build with the canonical loop.** The builder gets reference IMAGES (not descriptions)
+3. **Build with the canonical loop.** The builder gets reference images (not descriptions)
@@ -43,1 +43,1 @@
-   faces; STRUCTURE requires building the structure — a theme layer over a mismatched
+   faces; structure requires building the structure — a theme layer over a mismatched
@@ -45,3 +45,3 @@
-4. **Fresh-context verifier gate — a LOOP, not a line.** A verifier agent that did NOT
-   build grades each page: reference and render as SEPARATE LABELED image blocks (Anthropic
+4. **Fresh-context verifier gate, run as a loop.** A verifier agent that did not
+   build grades each page: reference and render as separate labeled image blocks (Anthropic
@@ -49,1 +49,1 @@
-   then a FRESH verifier grades the fixed state — a fix agent confirming its own fixes is
+   then a fresh verifier grades the fixed state — a fix agent confirming its own fixes is
@@ -54,1 +54,1 @@
-5. **The one-check rule (deploy gate).** The main loop READS the final renders itself, and
+5. **The one-check rule (deploy gate).** The main loop reads the final renders itself, and
@@ -59,1 +59,1 @@
-   by the canonical CI runner (never trust a local render as canonical; regen by FILE PATH,
+   by the canonical CI runner (never trust a local render as canonical; regen by file path,
@@ -64,1 +64,1 @@
-   exposed coupling, and lying removal note folds back into the STARTING CHASSIS (the
+   exposed coupling, and lying removal note folds back into the starting chassis (the
 (lines 97-129: lowercase DECLARED, ACHIEVED, INK, GEOMETRY, MARK, BOX, BASELINES, CENTRE,
  OWNS THE LINE BOX, NO, STABILITY, ALL THREE, RIGHT the same way; keep MATCHED/IMPROVED/
  DEFERRED-WITH-SANCTION/COSMETIC/STRUCTURAL, which are verdict tokens)

--- a/plugins/standards/skills/design-refinement/SKILL.md   [#6]
@@ -28,1 +28,1 @@
-On invocation, do not open with a questionnaire. First DISCOVER what the project already
+On invocation, do not open with a questionnaire. First discover what the project already
@@ -35,1 +35,1 @@
-Then ask ONE batched question covering only what is genuinely owner-held and still missing —
+Then ask one batched question covering only what is genuinely owner-held and still missing —
@@ -46,2 +46,2 @@
-The deciding predicate is the WORK's state, not the owner's presence: while the owner's
-design notes are still arriving — taste unconverged — the work is an ARC and iterations must
+The deciding predicate is the work's state, not the owner's presence: while the owner's
+design notes are still arriving — taste unconverged — the work is an arc and iterations must
 (same treatment for PROBE PAGE, RATIFIED, REAL, CURRENT, CANDIDATE, ONE, DIRECTLY, ROUND,
  BETWEEN, SAME, WIDEN, DEPLOYED, LEDGER, QUESTIONS, DIRECTING, IN, ARC, MAJOR, ONCE, EVERY)

--- a/plugins/standards/skills/receiving-code-review/SKILL.md   [#7, #8]
@@ -27,12 +27,5 @@
-## Forbidden Responses
-
-**NEVER:**
-- "You're absolutely right!" (explicit instruction-file violation)
-- "Great point!" / "Excellent feedback!" (performative)
-- "Let me implement that now" (before verification)
-
-**INSTEAD:**
-- Restate the technical requirement
-- Ask clarifying questions
-- Push back with technical reasoning if wrong
-- Just start working (actions > words)
+## How to Respond
+
+Answer feedback with substance: restate the technical requirement, ask about what is unclear,
+push back with reasoning where it is wrong, or make the fix. Praise and agreement carry no
+information, and announcing a change before you have verified it promises what you have not checked.
@@ -139,10 +132,3 @@
-❌ "You're absolutely right!"
-❌ "Great point!"
-❌ "Thanks for catching that!"
-❌ "Thanks for [anything]"
-❌ ANY gratitude expression
 ```
 
-**Why no thanks:** Actions speak. Just fix it. The code itself shows you heard the feedback.
-
-**If you catch yourself about to write "Thanks":** DELETE IT. State the fix instead.
+State the fix, not your thanks: the change shows you heard the feedback.

--- a/plugins/standards/skills/receiving-code-review/SKILL.md   [#9]
@@ -14,12 +14,5 @@
 ## The Response Pattern
 
-```
-WHEN receiving code review feedback:
-
-1. READ: Complete feedback without reacting
-2. UNDERSTAND: Restate requirement in own words (or ask)
-3. VERIFY: Check against codebase reality
-4. EVALUATE: Technically sound for THIS codebase?
-5. RESPOND: Technical acknowledgment or reasoned pushback
-6. IMPLEMENT: One item at a time, test each
-```
+Read all the feedback before acting on any of it. Check each item against the code as it
+stands, and decide whether it is sound for this codebase. Then acknowledge or push back with
+reasons, and implement one item at a time, testing each.

--- a/plugins/standards/skills/visual-fidelity/SKILL.md   [#10]
@@ -12,4 +12,3 @@
-Born from production visual misses (typography and structure) whose mechanical gates were all
-green. The failure class: verbal specs lose the design,
-and the builder's own context grades its work "close" (Anthropic's prompting guidance:
+Mechanical gates can all pass on a visual miss. Verbal specs lose the design,
+and the builder's own context grades its work "close" (Anthropic's prompting guidance:
@@ -81,5 +80,3 @@
-Born from a vertical-alignment pass: three audit rounds, a probe condemned
-three times, and the same root error in two disguises. Read this section for ANY vertical
-alignment judgment, not only a port. This defect class is authored, not ported: the three
-rows the pass finally confirmed had been 2.5px wrong since the day they were written,
-through every green test run.
+Read this section for any vertical-alignment judgment, not only a port. This defect class is
+authored, not ported, and it survives every green test run.

--- a/plugins/standards/skills/design-refinement/SKILL.md   [#10]
@@ -48,4 +48,2 @@
 be cheap; only ratified work runs the full machinery. Routing an iterative round into the
-settled-landing pipeline because the owner reviews async is the observed expensive failure
-(three notes-adjudicate-dispatch-gate-regen cycles before the
-owner named it as long, slow, and expensive loops). The full build-gate-baseline cycle runs once per settle, never per iteration.
+settled-landing pipeline because the owner reviews async is slow and expensive. The full
+build-gate-baseline cycle runs once per settle, never per iteration.
@@ -79,3 +77,1 @@
 settle, where the full gate, CI-canonical baseline regeneration, and deploy run exactly
-once. The ASC register round is the proven exemplar: probe page rendered, verdict in
-minutes, one landing commit.
+once.

--- a/plugins/standards/agents/visual-verifier.md   [#10]
@@ -29,5 +29,4 @@
-   MANDATORY on every page with interactive elements: the contrast probe — computed color
+   On every page with interactive elements, run the contrast probe: computed color
    vs background on every button/CTA/link (flag any pair under 3:1; color === background
    is an automatic STRUCTURAL fail). White-on-white text is invisible in full-page
-   screenshots at review scale; three verifiers missed live fireweed-on-fireweed CTAs
-   (2026-07-06) because none ran this check.
+   screenshots at review scale, so only the probe catches it.

--- a/plugins/standards/agents/plan-reviewer.md   [#10]
@@ -94,4 +94,3 @@
   after the whole-branch review: a delta review's Low findings are folded once, with that fold
   checked by the session's own diff read and CI, or filed, and never start another round. Without a
-  floor, each fix's smaller residual holds the merge round after round (a setup pass's security
-  review ran five rounds this way).
+  floor, each fix's smaller residual holds the merge round after round.

--- a/plugins/standards/skills/brainstorming/SKILL.md   [#11]
@@ -117,2 +117,2 @@
 describe it (what it's for and who it serves, say, or how one piece
-behaves), describe that part back in about 200-300 words, then return to
+behaves), describe that part back in a short paragraph or two, then return to
```

Hunks #5 and #6 show the pattern on their first lines and list the rest of the caps words for the same treatment. Hunk #3 renumbers the checklist, so take it before #10's `plan-reviewer` hunk or re-anchor that one. After you apply any of them, run the repo's `validate` check. It covers the reference checker and the skill length limit.
