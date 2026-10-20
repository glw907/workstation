# Prompt audit: workstation Claude Code configuration, Fable 5.1

Produced 2026-09-04 by the `claude-api` skill's prompt-audit procedure
(`shared/prompt-audit.md`), run read-only. Nothing in the audited surface was
edited, and no diff accompanies this report.

## Assumptions

**Target model.** Claude Fable 5.1 (`claude-fable-5-1`), the session model on this
workstation since 2026-09-04. Reviewer pins stay `claude-opus-5` and implementer
pins stay `sonnet`, so findings about dispatched agent files are judged against
those models where the file carries a pin.

**Scope.** Four groups, 39 files, 6,016 lines:

1. `claude/.claude/CLAUDE.md` (364 lines).
2. Every `*.md` under `claude/.claude/agents/` (11 files, 859 lines).
3. Every `SKILL.md` under `claude/.claude/skills/` (22 files, 4,326 lines).
4. Every file under `claude/.claude/docs/voice/` (5 files, 467 lines).

Reference files inside skill directories (`references/`, `evals/`, `assets/`,
`scripts/`) sit outside the scope and were not audited. Paths below are relative
to the repository root at `~/.dotfiles`.

## Tagging rule

`[keep]` is the default for any rule that cites a person and a date, a "Born"
incident, or a named failure. Those rules are incident-born and out of scope for
trimming, whatever pattern they also match. `[trim]` marks step-by-step
scaffolding that enumerates how to work where a goal and its constraints would
carry the same instruction.

## Summary

The surface is far cleaner than a typical accreted prompt estate. It carries none
of the classic API-era fossils: no "think step by step", no `<scratchpad>` or
`<thinking>` tag instructions, no assistant-turn prefill or JSON-forcing scaffold,
no numeric word caps, no interim-update cadences, no narration suppressors, and no
retired model names outside two deliberate citations. Emphasis density is low in
most files, and where it is high the surrounding rule almost always names the
incident that earned it.

Two dispositions dominate. The incident-born core, roughly two thirds of the
findings, is exactly the content the audit's keep list protects: environment
facts, quality bars, and constraints with their reasons attached. The trimmable
residue is concentrated in the procedural skills, where a task the model already
sequences correctly has been written out as a numbered script.

The three highest-impact items are the two backlog skills and `ship`. Between
them, `log-issue`, `log-project`, and `ship` spend 437 lines scripting file edits
and shell commands that a goal statement plus the file format would specify in a
fraction of the space, and the scripting is the pattern the migration guidance
names as actively degrading on current models.

One factual fossil deserves separate mention. `content-draft/SKILL.md:36` explains
a `model: sonnet` dispatch by saying an unpinned subagent "would otherwise inherit
the main-loop model". Task 1 of this pass moved `CLAUDE_CODE_SUBAGENT_MODEL` to a
settings `env` entry of `sonnet`, so the stated reason is now wrong even though
the instruction itself is still right.

## Findings

Ordered by confidence, highest first.

### High confidence

- `claude/.claude/skills/log-issue/SKILL.md:20` numbered Steps 1 through 6 (lines 20 to 171) script a capture task end to end: locate the config, gather six fields, assign the next number, write the entry, confirm, commit. Group 1c step-by-step choreography for a judgment task; Fable 5.1 plans this sequence unaided and the script costs 150 lines on every trigger. Confidence high. [trim]
- `claude/.claude/skills/log-issue/SKILL.md:44` first-run setup enumerates four verbatim interview questions and a four-step post-answer procedure. Group 1c over-specification of an interaction the model shapes better from the config schema alone. Confidence high. [trim]
- `claude/.claude/skills/log-project/SKILL.md:22` numbered Steps 1 through 4 plus four further named procedures (Updating, Commit and push, Closing, Auto-closing) restate the same file-edit mechanics as `log-issue` in a second 178-line script. Group 1c choreography compounded by cross-file duplication. Confidence high. [trim]
- `claude/.claude/skills/ship/SKILL.md:17` "Run these steps sequentially. Stop on failure." then four steps, three of which are a single command. Group 1c step-by-step scaffolding; the goal plus the stop-on-failure constraint is the whole instruction. Confidence high. [trim]
- `claude/.claude/skills/vhs-cli-demos/SKILL.md:98` "The core workflow" numbers five steps that restate "The essentials" at line 39 of the same file. Group 1c near-duplicate plus procedure; duplicated rules make the model spend effort reconciling wordings. Confidence high. [trim]
- `claude/.claude/agents/cairn-implementer.md:34` the numbered Workflow 1 through 6 narrates process the model runs unprompted, and its steps 1, 4, and 6 restate the verification contract stated above at line 18. Step 1 ("Ask any clarifying question before you start") is also unenforceable under `pass-execute.js`, where the dispatch is non-interactive. Group 1c plus Group 1d unenforced instruction. The TDD ordering, the scope fence, and the "never `git add -A`" constraint must survive as prose. Confidence high. [trim]
- `claude/.claude/agents/site-implementer.md:34` the same numbered Workflow in the same shape, with the same unenforceable clarifying-question step. Confidence high. [trim]
- `claude/.claude/skills/content-draft/SKILL.md:36` justifies pinning `model: sonnet` on the grounds that an unpinned dispatch "would otherwise inherit the main-loop model". The settings `env` entry added by task 1 of this pass routes model-less dispatches to `sonnet`, so the stated reason is stale for Fable 5.1 sessions. Group 1d model-version fossil. Confidence high. [keep]

### Medium confidence

- `claude/.claude/skills/bubbletea-design/SKILL.md:228` the "Iteration Loop" states a generic Identify, Analyze, Fix, Verify, Report cycle plus "Analyze before touching code". Group 1c planning choreography; current models plan without being told, and the good/bad example pair below it already carries the real instruction. Confidence medium. [trim]
- `claude/.claude/skills/bubbletea-design/SKILL.md:170` Mode 1 wraps four positional checks in a numbered instantiate-render-strip-iterate procedure. The ANSI regexp and the four checks are mechanics worth keeping; the numbered wrapper is scaffolding. Group 1c. Confidence medium. [trim]
- `claude/.claude/skills/content-review/SKILL.md:17` numbered Steps 1 through 7. Steps 3 and 4 carry the gates and the site guide's rules; steps 1, 2, 5, 6, and 7 enumerate an order the model sequences from the gates themselves. Group 1c. Confidence medium. [trim]
- `claude/.claude/skills/content-draft/SKILL.md:18` numbered Steps 1 through 5, whose load-bearing contracts (the brief comes first, a gap is an `[ASK]`, budgets are constraints) are restated as Hard rules at line 54. Group 1c step scaffolding over content the file already states as constraints. Confidence medium. [trim]
- `claude/.claude/skills/ts-conventions/SKILL.md:53` the four-branch numbered "Decision rubric" restates the three-question §0 gate at line 34 as a decision tree. Group 1c near-duplicate; the gate is already the mechanical test the register asks for. Confidence medium. [trim]
- `claude/.claude/skills/python-conventions/SKILL.md:49` the same four-branch rubric restating the same §0 gate at line 36. Confidence medium. [trim]
- `claude/.claude/skills/go-conventions/SKILL.md:504` a six-step numbered rubric restating the write-time gate at line 481, the unexported default at line 552, and the error-string rules at line 558. Group 1c repetition as reinforcement, which inflates adaptive-thinking spend on a skill invoked before every Go file. Confidence medium. [trim]
- `claude/.claude/skills/ts-conventions/SKILL.md:147` the "Output" section restates the order of operations ("run the §0 gate first, then the rubric, then write only what survives"), duplicated at `python-conventions/SKILL.md:123` and `svelte-conventions/SKILL.md:73`. Group 1c procedure narration across three files. Confidence medium. [trim]
- `claude/.claude/skills/site-pass/SKILL.md:34` "Starting a pass" numbers five steps that mix real preconditions with execution choreography. Group 1c. Task 5 of this pass already restates lines 34 to 72 and 198 to 210 as outcomes and constraints, so the fix is in flight and this entry records the finding rather than proposing a second edit. Confidence medium. [trim]
- `claude/.claude/skills/visual-fidelity/SKILL.md:10` cites "Anthropic's Fable 5 prompting guide" as the authority for fresh-context verification. Group 2 pinned model name, which degrades silently after a release. The claim still holds on Fable 5.1 and the rule is incident-born from two 2026-07-05 production misses, so refresh the citation rather than the rule. Confidence medium. [keep]
- `claude/.claude/agents/visual-verifier.md:9` states "Anthropic's Fable guidance is your mandate", and the frontmatter pins `model: claude-fable-5-1` at line 4. Group 2 pinned model name in both the rationale and the pin. The pin is deliberate and current; the prose authority will age. Confidence medium. [keep]
- `claude/.claude/CLAUDE.md:3` "Work Autonomously Until Done" restates proactivity, which Fable 5.1 exhibits by default. Group 1a restatement of a trained default. It also encodes a standing owner preference recorded in the `geoff-works-autonomously` memory, which makes it context rather than cruft under keep-list item 1. Confidence medium. [keep]
- `claude/.claude/CLAUDE.md:200` the section heading carries migration-relative phrasing ("supersedes the 2026-07-26 Opus-executes rule"), a diff against a prompt version the model never saw. Group 1d. The provenance is deliberate here, since the superseded rule still circulates in older plans. Confidence medium. [keep]
- `claude/.claude/skills/cairn-pass/SKILL.md:282` the same "revised 2026-08-21; supersedes the 2026-07-26 Opus-executes rule" phrasing inside a paragraph of live instruction. Group 1d migration-relative phrasing. Confidence medium. [keep]
- `claude/.claude/skills/cairn-pass/SKILL.md:16` states the rebuild-has-landed fact twice, at lines 16 to 21 and again at lines 23 to 27. Group 1c near-duplicate paragraphs. The two copies agree, so this is a refactoring preference rather than a dated pattern. Confidence medium. [keep]
- `claude/.claude/skills/engine-consult/SKILL.md:154` a "First run" section instructs the first live consultation to delete the section from the skill. Group 2 time-sensitive content whose trigger nothing checks, so it persists until a session happens to notice it. Confidence medium. [keep]
- `claude/.claude/CLAUDE.md:90` "MANDATORY: Invoke the `go-conventions` skill before writing ANY Go code" uses caps emphasis on two words. Group 1a pressure language by the letter, but Group 3's trigger split sanctions calibrated urgency in routing text, and this line routes rather than instructs. Confidence medium. [keep]
- `claude/.claude/skills/visual-fidelity/SKILL.md:17` opens the highest caps-emphasis density on the surface, 58 all-caps emphasis words across 131 lines. Group 1a inflated emphasis, which on a highly steerable model can produce rigid application. Every rule in the file names a dated incident or a named production miss, so the emphasis carries provenance rather than volume. Confidence medium. [keep]

### Low confidence

- `claude/.claude/agents/diff-reviewer.md:43` pins an exact output template with fixed field names. Group 1c format pinning, and keep-list item 7 protects it: `pass-execute.js` parses this shape, so the example is a contract. Confidence low. [keep]
- `claude/.claude/agents/cloudflare-workers-reviewer.md:16` "Report every finding ... coverage beats self-filtering" appears verbatim in four reviewer agents. Group 1c repetition across files, but each copy is a separate always-loaded surface carrying its own stated reason, which is working redundancy under keep-list item 8. Confidence low. [keep]
- `claude/.claude/skills/engine-consult/SKILL.md:63` duplicates the engine standard verbatim from `agents/engine-triage.md:33`. Group 1c duplicated content across surfaces. Both copies carry a do-not-drift note naming the spec as the source, and the copies currently agree. Confidence low. [keep]
- `claude/.claude/skills/cairn-release/SKILL.md:25` runs as numbered sections 1 through 7. Group 1c numbered procedure by shape, but the order is load-bearing (verify the number is free before bumping, publish before any site push), which keep-list item 3 protects for fragile operations. Confidence low. [keep]
- `claude/.claude/skills/engine-consult/SKILL.md:125` the cross-repo mini-pass checklist numbers six steps. Same disposition: the order is load-bearing, since the worktree must be registered before the first commit and the release must precede the site merge. Confidence low. [keep]
- `claude/.claude/skills/register-check/SKILL.md:12` numbers four gates. The ordering is cost-driven ("cheapest-first") and the gates dispatch different agents, so the sequence is the instruction. Confidence low. [keep]
- `claude/.claude/docs/voice/agent-facing.md:87` closes with an "Off-voice contrast" block holding a deliberately wrong example, repeated in all four register files. Group 1c example over-indexing by shape. Anthropic's own guidance names the contrasting wrong example as a strong lever, and the block is labeled as contrast rather than as a target. Confidence low. [keep]

### Incident-born rules confirmed in scope

Each of the following matches a pattern the audit scans for and is retained on
provenance. They are listed so a later re-audit does not rediscover them.

- `claude/.claude/CLAUDE.md:9` "Search before you spelunk (Geoff, 2026-07-13)" instructs one web search before an interactive debugging loop, with "proven twice 2026-07-13" as its evidence. Group 1c strategy coaching by shape, retained on a dated ruling and a stated budget argument. Confidence high. [keep]
- `claude/.claude/CLAUDE.md:19` "One executor per worktree (Geoff, 2026-07-14)" uses caps emphasis on "ANY" and enumerates four checks. Group 1a plus Group 1c by shape. Born 2026-07-14, two workflows racing one worktree at a cost of roughly 1.2M duplicated tokens. Confidence high. [keep]
- `claude/.claude/CLAUDE.md:148` "Check the stores before claiming a secret is missing" lists five stores in a fixed order. Group 1c enumeration. Born 2026-07-07, twice, both false "you still owe me X" reports. Confidence high. [keep]
- `claude/.claude/CLAUDE.md:186` the automatic filing trigger for a repeated local workaround. Born 2026-07-30, a third repeat patch of the same DaisyUI edge, filed only when Geoff asked. Confidence high. [keep]
- `claude/.claude/CLAUDE.md:304` "Pass sizing is the orchestrator's job (Geoff, 2026-07-29)" names three failure modes from poplar pass 1b. Group 1c prohibition list by shape, retained because each prohibition names the failure it prevents. Confidence high. [keep]
- `claude/.claude/CLAUDE.md:359` lists four anti-formatting and anti-phrasing rules. Group 1d anti-formatting rules, which the migration guidance flags because Fable 5.1 already under-formats. Retained because these are register rules tied to published external standards and enforced by `tellgrader` and Vale, not habits tuned against an older model. Confidence medium. [keep]
- `claude/.claude/skills/visual-fidelity/SKILL.md:82` "Ink, not boxes" opens with Born 2026-08-07 and four rules, each marked "earned". Group 1c prohibition and rule enumeration, retained on the incident. Confidence high. [keep]
- `claude/.claude/skills/tui-visual-verify/SKILL.md:8` Born 2026-08-21 at poplar's pass 2 gate, with 159 green goldens that had never looked at a painted frame. The harness section that follows states "Every design choice in it was forced by a failure on the day". Confidence high. [keep]
- `claude/.claude/skills/vps-conventions/SKILL.md:90` the compose-network row of the common-mistakes table. Born 2026-09-01, dubplate subnet pin 502'd Navidrome. Confidence high. [keep]
- `claude/.claude/skills/cairn-release/SKILL.md:78` "derive the size HERE, at the cut" with a prohibition on inheriting a version size from conversation. Born 2026-07-16, a polish pass nearly cut as `0.88.0`. Confidence high. [keep]
- `claude/.claude/skills/design-refinement/SKILL.md:50` the arc-versus-landing predicate, citing ASC basic-polish 2026-07-16 and quoting the owner's ruling verbatim. Group 1c strategy coaching by shape, retained on the dated ruling. Confidence high. [keep]
- `claude/.claude/skills/cairn-pass/SKILL.md:181` "Triage the WHOLE friction log, complete-or-move, every pass (Geoff, 2026-09-01)". Caps emphasis with a person and a date. Confidence high. [keep]
- `claude/.claude/skills/site-pass/SKILL.md:171` "A finished pass always ends by prepping to clear context (Geoff, 2026-08-01)", stated as a ritual step rather than an offer. Confidence high. [keep]
- `claude/.claude/agents/visual-verifier.md:30` the mandatory contrast probe, citing three verifiers who missed live fireweed-on-fireweed CTAs in 2026-07-06. Group 1a caps emphasis ("MANDATORY", "automatic STRUCTURAL fail"), retained on the named failure. Confidence high. [keep]
- `claude/.claude/skills/writing-voice/SKILL.md:56` the facts-discipline rule, citing the 2026-09-01 benchmark finding that invented specifics were this system's one systematic failure mode. Confidence high. [keep]
- `claude/.claude/skills/writing-voice/SKILL.md:63` "The brief is a contract", citing the 2026-09 benchmark drafts lost to undershooting a stated floor. This one is a re-baselining addition rather than a removal candidate, since terseness against a stated floor is a current-model failure mode. Confidence high. [keep]
- `claude/.claude/skills/elm-conventions/SKILL.md:85` "The one recorded exception: a `tea.WithFilter` input coalescer". Group 1d patch accretion by shape, a narrow conditional traceable to one case. Retained because the exception states its mechanism, its bound, and the three conditions that void it. Confidence medium. [keep]
- `claude/.claude/skills/go-conventions/SKILL.md:399` "Never guard a step with `command -v tool || echo \"skipping\"`". Group 1c prohibition, retained because it names the mechanism (a missing tool turns into a green build and the gate decays silently). Confidence high. [keep]

Tally: keep 35, trim 16

## The three highest-confidence trims, restated

1. `claude/.claude/skills/log-issue/SKILL.md:20`. Steps 1 through 6 spend roughly 150 lines scripting a backlog capture: config lookup, a six-field gather table, sequential numbering, the file write, a confirmation line, and a commit command. The file format at line 109 and the format rules at line 145 already specify everything the entry must contain. Replace the steps with the goal, the format, and the three real constraints (infer from context, prompt only for a missing domain or type, commit the file by path).

2. `claude/.claude/skills/log-project/SKILL.md:22`. Steps 1 through 4 plus four further named procedures script the same class of file edit a second time, in a second 178-line skill sharing one config with `log-issue`. The roadmap template at line 73 and the format rules at line 115 carry the contract. The duplication across the two skills is the stronger half of this finding: the same mechanics stated twice can drift apart.

3. `claude/.claude/skills/ship/SKILL.md:17`. Four numbered steps, three of them a single command, wrapped in "Run these steps sequentially. Stop on failure." The whole instruction is the goal (`make check`, `/simplify`, commit and push, `make install`), the ordering constraint, and the stop-on-failure rule. The step scaffolding around them changes nothing about what a Fable 5.1 session does.
