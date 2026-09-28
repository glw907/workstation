# Infra sweep spec review: current Anthropic practice

Reviewer lens: current Anthropic guidance, fetched live on 2026-09-28. Target:
`/var/home/glw907/.dotfiles/docs/superpowers/specs/2026-09-28-claude-infra-sweep-design.md`
(dotfiles `3f41deb`). Evidence read: the audit record, the global CLAUDE.md, every agent's
frontmatter, every authored skill's frontmatter and length, `settings.json` hooks, and the repo
CLAUDE.md sizes. Local Claude Code: v2.1.284.

Anthropic's own warning governs the ranking. From
<https://code.claude.com/docs/en/best-practices>: "A reviewer prompted to find gaps will usually
report some, even when the work is sound, because that is what it was asked to do. Chasing every
finding leads to over-engineering." The spec is sound on the whole. Most of its design responses
match current guidance, several almost word for word. The findings below are the places where the
guidance names a mechanism or target that the spec does not use.

**Counts:** 0 blocker, 3 major, 9 minor, 1 owner fork. Four of the minors are scope increases,
marked.

## Sources fetched

Each page was fetched on 2026-09-28. Most pages show no publish date; the version or date marker
each one carries is given instead. Quotes from pages 1 to 3, 5 to 16 are verbatim from the
fetched text. Pages 4 and 17 came back through the fetch tool's summarizer, so only their
double-quoted spans are treated as verbatim, and each load-bearing fact from them is
corroborated on another page.

| # | URL | Date or version marker |
|---|---|---|
| 1 | https://code.claude.com/docs/en/best-practices | Cites Claude Code v2.1.283 (auto mode default) |
| 2 | https://code.claude.com/docs/en/memory | Cites v2.1.283 (`/doctor prompt-audit`) |
| 3 | https://code.claude.com/docs/en/skills | Cites v2.1.281 |
| 4 | https://code.claude.com/docs/en/sub-agents | Cites v2.1.271 (`omitClaudeMd`); summarized fetch |
| 5 | https://code.claude.com/docs/en/features-overview | No marker |
| 6 | https://code.claude.com/docs/en/hooks-guide | Cites v2.1.210 |
| 7 | https://code.claude.com/docs/en/workflows | Cites v2.1.271 |
| 8 | https://code.claude.com/docs/en/output-styles | Cites v2.1.269 |
| 9 | https://code.claude.com/docs/en/goal | Cites v2.1.269 |
| 10 | https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices | Covers Opus 5.5 and Fable 5.1 |
| 11 | https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5-5 | Beta headers dated 2026-08-18 and 2026-08-21 |
| 12 | https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5 | No marker |
| 13 | https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5-5 | Beta header dated 2026-08-18 |
| 14 | https://platform.claude.com/docs/en/build-with-claude/effort | Lists `claude-opus-5-5` |
| 15 | https://platform.claude.com/docs/en/models/opus-5-5/whats-new-opus-5-5 | Account cutoff "August 31, 2026" |
| 16 | https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices | No marker |
| 17 | https://claude.com/blog/steering-claude-code-skills-hooks-rules-subagents-and-more | June 18, 2026 (before Opus 5.5); summarized fetch |
| 18 | https://www.anthropic.com/engineering | Index; its 2026 posts end at April 23, 2026, and none is on CLAUDE.md, skills, or context budgets |

No Anthropic engineering post since the Opus 5.5 release addresses this infra class. The current
guidance lives in the Claude Code docs and the platform prompting pages, which are versioned
past the release.

## Question 1: what the guidance says

**CLAUDE.md size and content.**

- "Size: target under 200 lines per CLAUDE.md file. Longer files consume more context and reduce
  adherence." (2)
- "Splitting into `@path` imports helps organization but doesn't reduce context, since imported
  files load at launch." (2)
- "You also see a warning when files that are each within that length add up past a combined
  limit at session start." (2)
- "If an entry is a multi-step procedure or only matters for one part of the codebase, move it to
  a skill or a path-scoped rule instead." (2)
- "For each line, ask: 'Would removing this cause Claude to make mistakes?' If not, cut it.
  Bloated CLAUDE.md files cause Claude to ignore your actual instructions!" (1)
- "Consistency: if two rules contradict each other, Claude may pick one arbitrarily." (2)
- `/doctor prompt-audit` "looks for problems such as instructions written for older models,
  references to files or commands that don't exist, and files that contradict each other." It
  "requires Claude Code v2.1.283 or later." (2)
- "If your CLAUDE.md sets commit or pull request rules, turn off the built-in ones with
  `includeGitInstructions` and set the attribution text with `attribution`." (2)

**Skills and progressive disclosure.**

- "Unlike CLAUDE.md content, a skill's body loads only when it's used, so long reference material
  costs almost nothing until you need it." (3)
- "the combined `description` and `when_to_use` text is truncated at 1,536 characters in the skill
  listing"; the listing budget "scales at 1% of the model's context window", and on overflow
  "Claude Code drops descriptions starting with the skills you invoke least." (3)
- "Keep `SKILL.md` under 500 lines. Move detailed reference material to separate files." (3, 16)
- "Keep references one level deep from SKILL.md." Nested references can be read partially. (16)
- "Don't include information that will become outdated." (16)
- "Use `disable-model-invocation: true` for skills with side effects. This saves context and
  ensures only you trigger them." (5)
- "Enterprise over personal, and personal over project" for skills sharing a name. (3)
- "Seeing a skill trigger tells you Claude found it, not that it did what you intended." Measure
  triggering with a baseline comparison in fresh sessions. (3)

**Subagent definitions.**

- A non-fork subagent loads "CLAUDE.md and git status, except the built-in Explore and Plan agents
  omit both, and an agent whose definition sets `omitClaudeMd` skips the user, project, and local
  CLAUDE.md files." (5)
- "The body becomes the system prompt that guides the subagent's behavior. Subagents receive only
  this system prompt plus basic environment details." (4)
- `effort` is a frontmatter field; `model` accepts aliases, a full ID, or `inherit`. (4)
- Subagents resolve "managed > CLI flag > project > user > plugin"; skills resolve "managed > user
  > project". (5) For workflows, "If a project workflow and a personal workflow share a name, the
  project one runs." (7)

**Hooks against instructions.**

- "Unlike CLAUDE.md instructions which are advisory, hooks are deterministic and guarantee the
  action happens." (1)
- "If a rule must hold every time, make it a hook rather than a prompt instruction." (5)
- "Hook output lands in context. A `PostToolUse` hook that runs your linter feeds results back as
  text Claude reads." (5)
- "If Claude already does something correctly without the instruction, delete it or convert it to
  a hook." (1)

**Prompt style for current models.**

- "If you emphasize many lines, none of them stands out." (1)
- "Where you might have said 'CRITICAL: You MUST use this tool when...', you can use more normal
  prompting like 'Use this tool when...'." (10)
- "Providing context or motivation behind your instructions ... can help Claude better understand
  your goals." (10)
- "Tell Claude what to do instead of what not to do." (10, format section)
- On Opus 5: "If your prompt contains explicit verification instructions ... remove them"; and "If
  your review prompt says 'only report high-severity issues' or 'be conservative,' the model may
  follow that instruction literally and report less." (12)

**Effort and context budget.**

- Opus 5.5: "`medium` is the default"; "at its default `medium` effort the model matched or beat
  Claude Opus 5 at `high` effort"; "Reserve `xhigh` and `max` for work where you've measured a
  quality gain." (11, 14)
- Sonnet 5.5: "For agentic coding and multistep tool use, start at `medium` for well-specified
  tasks and move to `high` for harder or longer ones." (13)
- "The context window is the most important resource to manage." (1)

**Multi-agent orchestration.**

- "Delegation pays off on genuinely independent, sizeable tracks of work, but it multiplies cost
  and time when applied to small tasks." "Do not delegate work you can finish yourself in a
  handful of tool calls." (12)
- "A reviewer running in a fresh subagent context sees only the diff and the criteria you give it."
  (1, "Add an adversarial review step")
- A workflow "can have independent agents adversarially review each other's findings." (7)
- `/goal`: "If a subagent or a background shell command is still running when a turn ends, Claude
  Code skips the evaluation for that turn," with check-ins after 30 minutes. (9)

## Question 2: grading the design responses

| Design response | Grade | Evidence |
|---|---|---|
| RC1, one owner per rule, tool output first (spec:71-84) | Matches | "Hook output lands in context" (5); "Make validation scripts verbose with specific error messages" (16) |
| RC2 and pass A, the guard (spec:86-90, 144-280) | Matches, with a free complement unused | `/doctor prompt-audit` covers dead references and contradictions (2); see M3 |
| RC3, supersession sweep (spec:92-109) | Matches | Directly answers "if two rules contradict each other, Claude may pick one arbitrarily" (2). The strongest-form order agrees with (1) and (5) |
| RC4, repo-neutral runners (spec:111-124) | Matches | No guidance contradicts it |
| RC5, fork skills take explicit arguments (spec:128-131) | Matches | "The subagent doesn't see your conversation history, so the skill's instructions have to stand on their own." (3) |
| RC7, no dated facts in always-loaded files (spec:135-138) | Matches | "Don't include information that will become outdated." (16) |
| RC8, always-loaded context (spec:139-142) | Partial | No line target; destinations are other always-loaded files; subagent loading unaddressed. See M1 and M2 |
| A1 description cap of 500 characters (spec:188-190) | Matches, stricter than native | Native cap is 1,536 (3); the API cap is 1,024 (16). The stricter cap is justified by the listing-budget drop rule (3) |
| A1 skill name collision (spec:181-184) | Matches | "personal over project" (3) |
| Seat check (spec:193-196) and PS-15 at `medium` (spec:432-433) | Matches | Opus 5.5 default and guidance (11, 14) |
| diff-reviewer chain (spec:461-464, pass-core) | Matches | "Add an adversarial review step" (1). Not the over-verification Opus 5 warns against (12), which concerns a model re-checking its own work |
| Emphatic caps | No action needed | Grep over CLAUDE.md, agents, authored skills, output styles: two `MANDATORY` lines in total (`CLAUDE.md:82`, `agents/visual-verifier.md:28`). The infra already follows (1) and (10) |
| B4 DC-29 owner question (spec:435-439) | Contradicts | The documented owner is the `attribution` setting (2). See m1 |
| B5 as its own chain (spec:350-353) | Over-ceremony | (12) on delegation. See m8 |

## Findings

Ranked by consequence. Each carries severity, location, defect, and proposed fold.

### Major

**M1. RC8 moves always-loaded text into other always-loaded files, with no size target.**
`spec:139-142`, `spec:409-410` (E: DC-19, DC-21), `spec:418` (F: cairn-cms).

Defect: DC-19's disposition moves cairn-only sections from the global CLAUDE.md into cairn and
site CLAUDE.md files. `cairn-cms/CLAUDE.md` is already 326 lines, `aksailingclub-org` 262,
`dubplate` 294, and the global file 280, all past Anthropic's "target under 200 lines" (2). The
move relocates the cost rather than removing it, for every cairn session. The spec's budget tool
cannot catch this. `claude-context-budget` budgets 6,000 tokens per CLAUDE.md and 4,000 per
import, about 400 and 270 lines of this prose, and it has no combined budget. Claude Code warns on
both the per-file target and a combined limit (2). E's success test (spec:33-35) counts only
baseline entries.

Fold:

1. E's outcomes route each moved section by Anthropic's order. A procedure goes to a skill (the
   pass rules to `pass-core`, already planned). A rule that matters only for certain files goes
   to a path-scoped rule in `.claude/rules/` with `paths:` frontmatter (2), for example the
   cairn-family UI rules scoped to `src/lib/components/**`. Only facts every session needs go
   to a repo CLAUDE.md.
2. E's success test adds: the global CLAUDE.md and each in-scope repo CLAUDE.md is at or under
   200 lines, or carries a recorded reason. Claude Code's startup length warning is the
   observable check (2).
3. A3's context-budget step gains a line cap per file at the documented 200 and a combined
   budget across the CLAUDE.md chain and its imports.

Scope: item 1 introduces `.claude/rules/`, a new artifact kind for this workstation (no
`~/.claude/rules` exists today). `claude-tooling-sync` and the reference checker's scan scope
must learn it. This is a **small scope increase to E**, not a new pass.

**M2. The full CLAUDE.md chain loads into every subagent, and the spec does not account for it.**
`spec:139-142`; every agent under `claude/.claude/agents/`.

Defect: each implementer, reviewer, and drafter dispatch loads the global CLAUDE.md (280 lines,
about 4,200 tokens) plus the repo's CLAUDE.md (5). No agent sets `omitClaudeMd`. The global file
carries rules scoped to the conductor, such as "it never reads a source file, a diff, a test
log," which an implementer must do. That is the "two rules contradict" condition (2), paid on
every dispatch. The audit knew subagents load the Git Conventions section (audit:118), but RC8
reasons only about the main session. `cairn-docs-drafter.md` already states that "the dispatch
prompt carries everything directly," which makes it the clearest `omitClaudeMd` candidate.

Fold: E gains one outcome. For each agent, decide `omitClaudeMd` and record the decision in
`seats.json` next to model and effort, so A1's seat check holds it. Candidates are the drafter,
`diff-reviewer`, `visual-verifier`, and `figure-verifier`, whose dispatches carry their inputs. An
agent that needs repo conventions (the domain reviewers, the implementers) keeps the chain until
M1 shrinks it. This is an architecture call, Claude's to make per the workstation rule. **Small
scope increase to A1's seat schema and to E.**

**M3. The spec does not use Anthropic's own audit for this infra class.**
`spec:151-166` (seeding), `spec:411` (E close), `spec:413-423` (F).

Defect: `/doctor prompt-audit` (2) reads CLAUDE.md, rules, skills, subagents, and output styles
under `~/.claude` and `.claude/`. It "looks for problems such as instructions written for older
models, references to files or commands that don't exist, and files that contradict each other."
The local build (v2.1.284) has it. Its third category is RC3's defect class, and its first is the
Opus-5.5-staleness lens the owner asked for. Neither the audit nor pass A checks that lens. The
tool proposes edits and changes nothing on its own. `/doctor` also "proposes trims for a
checked-in CLAUDE.md" (2), which is pass F's job.

Fold: the tool is model-judged, so it is an audit input, never a gate, and pass A's deterministic
checks stay as designed.

1. Pass A's seeding runs `/doctor prompt-audit` once over `~/.claude`. Each finding the checks do
   not already cover becomes a `GA-nn` entry or a C or D item, listed in A's close.
2. E's close runs it again as a confirmation read.
3. Each pass F chore runs `/doctor prompt-audit` and the `/doctor` trim proposal over that repo's
   CLAUDE.md, triaged in the chore.

No new pass.

### Minor

**m1. DC-29 names the wrong owner for the trailer.** `spec:347`, `spec:435-439`.
Defect: "If Geoff prefers the generic form, the bullet stays and the harness defers to it." The
documented mechanism is the `attribution` setting, and a CLAUDE.md commit rule competes with the
built-in git instructions (2). Fold: delete the bullet in both cases. Geoff's choice becomes the
`attribution` value in `settings.json`, default (model-named) or the generic string. Also note
that the Git Conventions section competes with built-in git guidance and can be trimmed in E. The
taste question and the recommendation are unchanged.

**m2. The seat values sit two references deep.** `spec:193-195`, `spec:345` (PS-14).
Defect: after A1, `model-economy.md` "Current state" points at `seats.json` for values, and B4
points `pass-core` at "Current state." A reader follows two hops to reach a value. "Keep references
one level deep" (16), because nested references are read partially. Fold: `pass-core` and the
global CLAUDE.md model line cite `seats.json` for values and `model-economy.md` for the why.

**m3. Two convention skills exceed the 500-line body target, and pass D grows one.**
`spec:398-404` (D: DC-10 folds checklists into elm-conventions).
Defect: `go-conventions` is 592 lines and `elm-conventions` 582, against "Keep `SKILL.md` under
500 lines" (3, 16). DC-10's fold adds bubbletea checklists to elm-conventions. Fold: D lands the
DC-10 checklists in a reference file under `elm-conventions/`, linked one level from SKILL.md,
and splits go-conventions the same way. Optionally add a 500-line body check to A1, baselined to
D.

**m4. Description trims have no trigger check.** `spec:188-190`, C and D. **Scope increase.**
Defect: the 500-character cap forces trims on about eight skills. Anthropic's guidance is to
measure triggering in fresh sessions (3, 16). DC-24 shows trigger loss is a live failure class
here. Fold: for each trimmed skill that a CLAUDE.md rule depends on (`go-conventions`,
`dependency-upgrade`, `visual-fidelity`, `tui-visual-verify`, `cairn-release`), C or D runs three
should-trigger prompts and two should-not prompts in fresh `claude -p` sessions, before and after
the trim. The rest get no eval.

**m5. The retired-phrase and dead-reference checks fire only at commit and close.** `spec:210-260`.
**Scope increase.** Defect: an edit to a repo CLAUDE.md outside dotfiles meets the check only at
that repo's close. Anthropic: "A `PostToolUse` hook that runs your linter feeds results back as
text Claude reads" (5). The workstation already does this for `claude-context-budget`,
`vale-hook`, and `tellgrader`. Fold: A2 gains a single-file `--hook` mode, limited to the retired
phrase and dead-reference checks, with no baseline logic. It is wired as a `PostToolUse` hook on
Write and Edit for CLAUDE.md files and paths under `.claude/`.

**m6. go-ship's trigger fix has a documented form.** `spec:181-184`. See the owner fork below.

**m7. DC-04 names `/loop` where `/goal` is the documented primitive.** `spec:306`, `spec:344`.
Defect: `/goal` defers evaluation while "a subagent or a background shell command is still
running" and issues check-ins after 30 minutes (9). That is the job the `/loop` wake-up does by
hand in `unattended-work-guards.md:105`. Fold: B4's DC-04 text stays tool-neutral ("arm the
wake-up the guards doc names") so it need not change again. C2 evaluates `/goal` with the pass's
acceptance as the condition against `/loop`, and records the result in the guards doc.
**Evaluation only, in C.**

**m8. B5 is a handful of tool calls run as a full chain.** `spec:350-353`.
Defect: deleting one workflow file and its listing entry gets an implementer, a diff-reviewer,
and a gate. Opus 5 guidance: "Do not delegate work you can finish yourself in a handful of tool
calls" (12). The workstation's own "Small tasks skip the ceremony" rule agrees. Fold: merge B5
into B4 as one docs task.

**m9. The seat table will freeze effort values that current guidance questions.** `spec:193-196`.
Defect: the implementers sit at `high`. Sonnet 5.5 guidance starts well-specified agentic coding
at `medium` (13). The escalation ladder (`xhigh`, then `max`, then `fable`) is unmeasured, while
Opus 5.5 guidance says to "Reserve `xhigh` and `max` for work where you've measured a quality
gain" (11). This is not the sweep's defect, and A1 is right to encode the current table. Fold:
`seats.json` carries a one-line `why` for each non-default effort. The effort sweep itself is
filed to `model-economy.md`'s owner. No change to the sweep's scope.

Two smaller notes need no severity.

- **Collision direction.** A1's collision check covers skills only. Agents (project over user)
  and workflows (project over personal) collide in the opposite direction (5, 7). No such
  collision exists today. Generalizing is cheap but optional.
- **Native frontmatter validation.** `claude plugin validate ~/.claude/skills` (3, v2.1.233) parses
  skill frontmatter. A1 can call it rather than re-implement skill frontmatter parsing.

### Considered and rejected

- **Trimming emphatic caps.** Only two remain. A pass for this would be over-engineering.
- **Adding `paths: ["**/*.go"]` to go-conventions.** It would drop the skill's description from
  the listing until a `.go` file is read, which recreates DC-24's trap for a new Go file. Keep the
  CLAUDE.md trigger line.
- **Dropping diff-reviewer on the Opus 5 over-verification advice.** That advice (12) targets a
  model re-checking its own work. A fresh-context reviewer is the documented pattern (1).

## Owner fork

**Side-effect skills and model invocation.** Anthropic recommends `disable-model-invocation: true`
for "workflows with side effects that you want to trigger manually" (1, 5). Two skills qualify:
`go-ship` (commit, push, install) and `cairn-release` (npm publish). With the flag, a skill leaves
the listing and runs only when typed as `/name`.

Recommendation: set it on `go-ship`. The spec already strips its generic triggers (PS-01), and
the flag is the documented form of that fix. Keep `cairn-release` model-invocable. Its description
is written for intent phrases ("publish cairn"), carries explicit negative triggers, and its
publish still passes through `gh release create`.

## Question 3: draft text for the spec's "Anthropic practice" section

Replace the stub at `spec:441-445` with the following.

> ## Anthropic practice
>
> Fetched 2026-09-28 against Claude Code v2.1.284. Full quotes and grading:
> `docs/superpowers/research/2026-09-28-infra-sweep-review-anthropic.md`. Items marked
> **scope** widen a pass; none adds a pass.
>
> **Confirmed.**
>
> - One owner per rule, tool output first. "If a rule must hold every time, make it a hook rather
>   than a prompt instruction." "Hook output lands in context."
>   (<https://code.claude.com/docs/en/features-overview>) RC1 and RC3 stand.
> - No contradicting homes. "If two rules contradict each other, Claude may pick one
>   arbitrarily." (<https://code.claude.com/docs/en/memory>) RC3's supersession sweep stands.
> - No dated facts. "Don't include information that will become outdated."
>   (<https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices>) RC7
>   stands.
> - Description cap. The native listing truncates at 1,536 characters and drops the
>   least-invoked descriptions first on overflow (<https://code.claude.com/docs/en/skills>). A1's
>   500-character cap stands.
> - Reviewers at `medium`. Opus 5.5 "at its default `medium` effort ... matched or beat Claude
>   Opus 5 at `high`."
>   (<https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5-5>)
>   PS-15 stands.
> - Emphasis. "If you emphasize many lines, none of them stands out."
>   (<https://code.claude.com/docs/en/best-practices>) The infra carries two `MANDATORY` lines.
>   No trimming pass.
>
> **Changed.**
>
> 1. CLAUDE.md size (E, F; **scope**). "Target under 200 lines per CLAUDE.md file"; imports
>    "still load and enter the context window at launch"; a procedure or file-specific rule
>    moves "to a skill or a path-scoped rule instead" (<https://code.claude.com/docs/en/memory>).
>    E routes DC-19 and DC-21 content by that order, using `.claude/rules/` with `paths:` where
>    content is file-specific. E's success test adds: each in-scope CLAUDE.md at or under 200
>    lines, or a recorded reason. A3's budget step gains the 200-line cap and a combined budget.
>    `claude-tooling-sync` and the reference checker learn `.claude/rules/`.
> 2. Subagent context (A1, E; **scope**). Subagents load the CLAUDE.md chain unless the
>    definition sets `omitClaudeMd` (<https://code.claude.com/docs/en/features-overview>). E
>    decides the field per agent and records it in `seats.json`, which A1's seat check reads.
> 3. Anthropic's audit (A, E, F). `/doctor prompt-audit` finds "instructions written for older
>    models, references to files or commands that don't exist, and files that contradict each
>    other" (<https://code.claude.com/docs/en/memory>). A runs it once before seeding and turns
>    its uncovered findings into `GA-nn` entries or C and D items. E runs it at close. Each F
>    chore runs it and the `/doctor` trim proposal. It is an input, never a gate.
> 4. Attribution (B4). CLAUDE.md commit rules compete with built-in guidance; "set the
>    attribution text with `attribution`" (<https://code.claude.com/docs/en/memory>). The footer
>    bullet goes either way, and the DC-29 answer lands in `settings.json`.
> 5. Reference depth (A1, B4). "Keep references one level deep"
>    (<https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices>).
>    `pass-core` and CLAUDE.md cite `seats.json` for values and `model-economy.md` for the why.
> 6. Skill size (D). "Keep `SKILL.md` under 500 lines" (<https://code.claude.com/docs/en/skills>).
>    D lands DC-10's checklists in a reference file under `elm-conventions/` and splits
>    `go-conventions`.
> 7. Trigger checks (C, D; **scope**). "Seeing a skill trigger tells you Claude found it, not
>    that it did what you intended" (<https://code.claude.com/docs/en/skills>). Each trimmed
>    skill that a CLAUDE.md rule depends on gets three should-trigger and two should-not prompts
>    in fresh `claude -p` sessions, before and after the trim.
> 8. Write-time feedback (A2; **scope**). A2 gains a single-file `--hook` mode for the retired
>    phrase and dead-reference checks, wired as a `PostToolUse` hook on Write and Edit for
>    CLAUDE.md files and `.claude/` paths.
> 9. Delegation (B). "Do not delegate work you can finish yourself in a handful of tool calls"
>    (<https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5>).
>    B5 merges into B4.
> 10. Unattended completion (B4, C2). `/goal` defers evaluation while a subagent or background
>     command runs and issues check-ins (<https://code.claude.com/docs/en/goal>). B4's DC-04
>     text stays tool-neutral. C2 evaluates `/goal` against the `/loop` wake-up and records the
>     result in the guards doc.
> 11. Effort record (A1). Current guidance starts well-specified Sonnet 5.5 coding at `medium`
>     and reserves `xhigh` and `max` for measured gains
>     (<https://platform.claude.com/docs/en/build-with-claude/effort>). `seats.json` carries a
>     one-line `why` per non-default effort. The sweep itself is filed to `model-economy.md`.
>
> **Owner fork.** `disable-model-invocation: true` on side-effect skills
> (<https://code.claude.com/docs/en/best-practices>). Recommendation: set it on `go-ship`, and
> keep `cairn-release` model-invocable.
