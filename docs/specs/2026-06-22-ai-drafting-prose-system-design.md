# The AI-drafting prose system: audience-based guidance with a Vale honesty check

Status: SUPERSEDED 2026-06-22 by `2026-06-22-authoring-standards-design.md` (the external-standards
redesign). Kept as history; it describes the earlier personal-voice design. It in turn superseded the
removed `2026-06-21-prose-guard-to-vale-migration` spec and plan.
Owner: Geoff.
Scope: workstation-wide. This is **Claude's prose-drafting discipline**, not a product feature.

## What this is, and what it is not

The system has two jobs. It guides Claude to draft effective, audience-fitting prose (feedforward),
and it keeps Claude honest when something slips (feedback). Good prose comes from the first job; the
linter is the cheaper, secondary backstop.

This is the discipline Claude writes under. It is separate from cairn's product prose features: the
cairn **tidy** copy-edit, the shipped spellcheck, and the admin `check:prose` gate are untouched by
this work. Both this and tidy improve prose, which is the conflation to avoid, but tidy is a runtime
feature cairn ships to its editors and this governs how Claude drafts.

The design rests on two five-agent research sweeps (2026), recorded in the plan's post-mortem. The
load-bearing findings are that drafting is steered best by a distilled rule-card plus a few positive
exemplars (not a pasted style guide), that the Claude Code primitives have an official division of
labor that maps cleanly onto a voice system, that enforcement belongs in a PostToolUse feedback hook
rather than a blocking wall, and that one source should generate both the prompt guidance and the
linter rules so they cannot drift.

## Principles

1. **Audience-based.** Style and structure fit the reader. Rules are not global. They split into
   universal tells (machine artifacts, bad in every register) and audience-conditional style choices
   (the em dash, contractions, reading grade, warmth), which each register sets for itself.
2. **No audience, no system.** Every artifact Claude drafts has an audience, code as much as prose,
   and each audience carries a style guide, its Claude infra, and its linting. A project declares its
   audience map, carries a content-guide where it serves a content audience, and holds its own Vale
   config before the system applies. It fails closed rather than defaulting to a generic register,
   because a generic default is the audience-blind behavior this removes. The workstation charter at
   `~/.claude/docs/authoring-charter.md` states this principle for any project to point at, and this
   spec is its prose arm.
3. **Feedforward first.** Draft clean the first time from a lean rule-card and register exemplars;
   let the linter catch the residue. A clean linter run is necessary, never sufficient, since the
   linter cannot judge voice.
4. **One source of truth.** A single machine-readable house-style source, per register, generates
   both the Vale config and the distilled rule-card. Regenerate both on a change; never hand-maintain
   two copies.

## The architecture: six layers, one job each

Each Claude Code primitive carries exactly one job, chosen so no rule is stated twice.

1. **Always-on minimum: the `writing-voice` output style.** Carries only the audience-invariant voice
   that must apply every turn, including chat replies: the universal tell rules, vary sentence length,
   and the instruction to name the audience and load its register. It edits the system prompt and is
   prompt-cached after the first turn. Keeps `keep-coding-instructions: true` (the workstation drafts
   prose and code together). It does not grow per-audience material.
2. **Always-on routing: the global `CLAUDE.md`, kept lean.** Holds the highest-frequency tells inline
   and the routing table that maps audience to register to style-guide baseline. A table is cheap and
   makes audience selection reliable. The full lists do not live here. A plain path reference is used,
   never an `@import` (imports expand at launch and do not defer cost).
3. **On-demand registers: one `writing-voice` Skill.** Wraps the routing and the per-audience registers.
   `SKILL.md` (under 500 lines) is the router: the audience-to-register table plus the shape rules,
   pointing one level deep to a reference file per register. Each register carries its persona and its
   3-5 positive exemplars, loaded only when that audience is in play (about 100 idle tokens until
   triggered). The skill `description` is the trigger: third person, specific, disjoint. The
   skill-creator harness tunes its hit rate.
4. **Style-guide baselines: vendored under Vale.** The Google and Microsoft guides live where they are
   machine-checkable, not as text the agent reads. Per audience, selected by file glob:
   `BasedOnStyles = Vale, Google, glw907` for developer and planning docs;
   `BasedOnStyles = Vale, Microsoft, glw907` for end-user product copy. House deviations ride in the
   `glw907` style and a `Vocab` (`accept.txt`/`reject.txt`), documenting only what departs from the
   baseline, the way Google's own precedence model and Red Hat's "overrides or supplements" prescribe.
5. **Enforcement: a Vale PostToolUse feedback hook.** Runs Vale on a saved prose file (markdown docs
   and site content) on `Write|Edit`, never on code comments (the comment arm owns those, see
   below), scopes the findings it acts on to the lines just written, and returns them as `additionalContext`
   phrased as facts, never commands, under the 10,000-character cap. Error-tier findings drive a fix
   (exit 2, the only channel Claude reads back); warnings ride along as advisory. It fails open. CI
   runs the same Vale config so artifacts the local hook never touched are still gated. A PreToolUse
   blocker for a tiny zero-tolerance, context-independent set is an option, deferred until a specific
   tell is shown to slip through, because hard-blocking fights the agent and the fragment a PreToolUse
   hook sees lacks file context.
6. **The second opinion: a read-only `prose-voice-reviewer` subagent.** Forked from the code-reviewer
   template (`tools: Read, Grep, Glob`), pinned to a strong model for a high-judgment, low-frequency
   gate. Given the specific register and tell-list, bounded to flag register violations and tells and
   to treat style preferences as optional, so it does not nitpick. It runs after the linter floor and
   before a human read on a substantial artifact. The fresh context is what earns it a place: it judges
   the result rather than the reasoning that produced it.

### How the layers route, end to end

Drafting starts under the output style (always-on voice) and the CLAUDE.md routing table (name the
audience). The agent names the audience, the `writing-voice` Skill loads that register and its
exemplars, and the strongest tone levers (examples plus persona) are now in context, scoped to the
reader. On save, the Vale hook checks the file against that audience's vendored baseline plus the
house layer and feeds findings back as facts. For a substantial artifact, the reviewer subagent gives
the fresh-context second opinion. CI re-runs Vale on anything the local hook missed.

### Code comments: their own arm

Code comments are an audience under the charter, with the same three layers: a structure linter
native to the language, Vale on the comment prose, and a per-language Claude tell catalogue. The full
design across Go, TypeScript, Svelte, and Python lives in the companion spec,
`2026-06-22-code-comment-standards-design.md`. Two facts touch this hook: comment prose is out of its
scope, because the comment arm runs its own Vale config against the comment scopes, and the em-dash
ban reaches code comments through that arm rather than through this prose hook.

## The audience model and the em-dash matrix

The em dash is the worked example of an audience-conditional rule. It is not banned per se. It fits a
professional or literary register and reads wrong in a deliberately plain, warm voice, and overuse is
the real failure mode, flagged everywhere as advisory.

| Audience / register | Em dash | Note |
| --- | --- | --- |
| Developer docs, and internal planning docs (specs, plans, STATUS, post-mortems) | allowed | planning docs are throwaway, so optimize for effective output and do not gate; long-term developer docs follow the Google standard |
| Polished or literary site content | allowed, sparing | the magazine register |
| Editor / admin product copy | discouraged (default) | plain, warm, short-sentence |
| ECXC coach voice and similar informal content | per the site content-guide | ECXC already bounds it: spaced, one per paragraph, true interruption only |
| Agent-facing docs and commit messages | discouraged | terse registers |
| Code comments | banned | resolved 2026-06-22: the comment arm ships it banned (Vale glw907.EmDash on .go, .ts, .py plus the Svelte extractor) |
| Claude's replies to Geoff | discouraged | resolved 2026-06-22: authorship plausibility, a terminal reply has no em-dash key |

A site's own content-guide is the authority for its content; the workstation matrix governs only the
workstation registers. Overuse is flagged everywhere via a density check, not a per-instance rule.

## Guidance design (feedforward)

Per the research: do not paste the full Google or Microsoft guide (it gets buried in the lost middle
and hurts conformance). Lead with a distilled, imperative rule-card and 3-5 positive exemplars per
register, wrapped in example tags, each with a one-line reason, since the model generalizes from the
reason better than from the bare rule. The deterministic class (terminology, casing, banned words,
person) goes to crisp rules the linter also enforces; the weak class (voice, structure, audience-fit)
goes to the exemplars and the reviewer. The off-voice contrast blocks in the registers are a house
extension beyond Anthropic's positive-only exemplar guidance, so keep them as a secondary rubric that
doubles as the Vale and reviewer reference, and lead each register on its positive exemplars. The full
guide is retrieved on demand for an unusual construction, placed near the top of that turn.

## Style-guide and Vale specifics

- Baselines: Google Developer Documentation Style Guide (developer and planning docs), Microsoft
  Writing Style Guide (end-user copy), both CC BY 4.0 with official Vale packages, plus an advisory
  `Readability` grade-8 floor for end-user prose (prose only, never gates, skips microcopy).
- House overlay: the `glw907` style staged at `~/.dotfiles/vale/.config/vale/styles/glw907/`, layered
  on the baseline, plus a shared `Vocab` for accepted product nouns. GitLab's guide is the cited
  precedent and a rule donor (it already bans the em dash) but not a baseline (CC BY-SA, monorepo-only).
- Distribution: vendor the private `glw907` style into each repo with a drift-check; `vale sync` the
  public baselines pinned to a version.
- Vale `v3.15.1`, repo `vale-cli/vale`, global config at the XDG path `~/.config/vale/.vale.ini` with
  no `VALE_CONFIG_PATH` env var (it overrides in-tree configs). Lookarounds are supported (a regexp2
  superset). The Microsoft Vale package is an unofficial implementation in the Vale org; note it.

## Per-context applications (the proofs)

The foundation is proven across the real repos, each a distinct audience.

- **cairn-cms:** developer docs and code comments (Google baseline) plus the editor surface, the admin
  copy and editor walkthrough guides (Microsoft baseline). The dev-plus-editor proof. Its Vale config
  selects the baseline per path; its CLAUDE.md carries the audience map.
- **ECXC (ecxc-ski):** the coach-voice content-guide already exists and is calibrated, with its own
  bounded em-dash rule. Migrate its enforcement from prose-guard to the audience-based Vale system, and
  move its `content-draft`/`content-review` skills and the shared `web-content-method.md` reference off
  prose-guard. The coach-voice proof. Executes in the ECXC repo session.
- **907-life:** no content voice is defined yet. Defining its personal-essay register is its own
  brainstorm in the 907 repo session (it encodes Geoff's voice and needs his calibration), then the
  wiring follows. The personal-voice proof, and the clean demonstration of "no audience, no system."

## Evaluation

Two tracks. The deterministic rules are measured by the Vale pass-rate (binary, cheap, CI-shaped). The
voice and structure are measured by a small LLM-judge rubric run pairwise against the register
exemplars, only when a doc arm changes materially. No off-the-shelf benchmark measures
named-style-guide conformance, so the voice eval is build-your-own.

## Sequence

1. Foundation: install Vale `3.15.1`, build the `glw907` overlay (universal tells plus the
   audience-conditional rules as separately toggleable), vendor the baselines, write the global config,
   and pass the fixtures.
2. Restructure the feedforward: the `writing-voice` Skill (registers as on-demand references, leading
   on positive exemplars), the lean output style, the CLAUDE.md routing table.
3. The Vale PostToolUse hook, scoped to changed lines; flip `settings.json`; prove the loop.
4. The `prose-voice-reviewer` subagent.
5. Repoint the docs and memories from prose-guard to the new system.
6. cairn-cms application and its CI gate (the first proof).
7. Retire prose-guard once the new hook is live and proven.
8. The site applications (ECXC migrate, 907 define-then-wire) in their own repo sessions.

## Risks and open items

- **The two open matrix rows are resolved (2026-06-22).** Code comments stay banned (the comment arm
  ships it). Replies to Geoff stay discouraged on authorship plausibility. Planning and throwaway docs
  are not gated on the em dash, and long-term developer docs follow the Google standard. The cutover
  (plan 07) carries these settings.
- **PreToolUse blocker.** Deferred by default. Revisit only if a zero-tolerance tell repeatedly slips
  past the PostToolUse feedback.
- **Single-source generation.** Auto-distilling one house-style source into both the Vale config and
  the rule-card is a validated direction for code linters, not a turnkey prose tool. Start with a
  hand-maintained single source and a regenerate discipline; automate later if it earns it.
- **Comment voice, the residual gap.** The comment arm gives comments a deterministic lexical check:
  the native linter for structure, and Vale on the comment scopes for the em dash and the lexicon, on
  `.go`, `.ts`, and `.py`. The one hole is the Svelte `<script>` block, which Vale cannot reach; a
  tiny extractor covers it (see the comment spec). Voice judgment past the lexicon stays with the
  register and the reviewer.
- **Changed-line scoping accuracy.** Locating the edited text in the saved file can be ambiguous (a
  repeated string, a `replace_all`); the hook handles multiple matches and falls back to whole-file
  scoping, erring toward surfacing rather than missing.
