# Authoring standards: external standards, linters, and Claude best practices

Status: design agreed 2026-06-22. Supersedes `2026-06-22-ai-drafting-prose-system-design.md` and
`2026-06-22-code-comment-standards-design.md`, which described an earlier personal-voice design.
Owner: Geoff. Scope: workstation-wide. This governs how Claude drafts; it is not a product feature.

## The principle

Claude writes to well-researched external standards, not a house voice. The one exception is website
content, which carries a site's own voice and lives in that site's repo, not on the workstation. For
every other audience the standard is external and published, and Claude reaches it two ways:

- A linter that encodes the standard. This is the deterministic feedback.
- Claude best practices plus the standard's own canonical exemplars. This is the feedforward.

There is no workstation house style, no per-model tell catalogue, and no personal calibration loop.
The published standard is the authority, the linter is its enforcement, and the exemplars plus the
prompt are how Claude reaches it.

## Why this supersedes the earlier design

The earlier two specs built a personal system: a `glw907` Vale overlay layered on the public
baselines, per-model tell catalogues (T1-T43, TS1-15, S1-10, T-P1-13), and registers that encoded
Geoff's voice with a calibration loop that rebuilt on his edits. That conflated two goals. For
website content the voice is the site's, and a calibration loop is right. For docs,
comments, agent-facing files, and commits, the goal is conformance to a published standard, so a
house overlay is unnecessary and a standing cost: the overlay and the rule-card drift, the catalogues
need per-model re-derivation, and the bespoke Svelte extractor is fragile. This design keeps the
voice loop only where it belongs and uses external standards everywhere else.

## The audiences

| Audience | Well-researched standard | Linter | Exemplars |
|---|---|---|---|
| Developer docs | Google Developer Documentation Style Guide | Vale Google package | Google's own docs |
| End-user and editor docs | Microsoft Writing Style Guide | Vale Microsoft package | Microsoft Learn |
| Go comments | Go Doc Comments, Effective Go | gofmt, go vet | the standard library |
| TypeScript and Svelte comments | TSDoc, plus the Svelte `@component` convention | ESLint jsdoc + tsdoc | well-regarded libraries |
| Python comments | PEP 257, PEP 8 | ruff `D` | the standard library |
| Agent-facing (CLAUDE.md, skills, agents) | Anthropic / Claude Code best practices | guidance, no linter | Anthropic's docs |
| Commit messages, PR bodies | Conventional Commits, the git-commit canon | commitlint (optional) | the convention's examples |
| Replies, email | plain technical communication | none | Claude best practices |

Website content is the only personal voice, and it is out of the workstation's scope. It lives in the
site repo with that site's `content-guide.md` and its own tooling. The workstation system covers the
standards-based audiences above.

## The two layers

Feedforward is Claude best practices. For every audience the recipe is the same: name the audience,
load that standard's canonical exemplars, draft to the standard, and reread once before saving. Lead
with exemplars, because the model generalizes from a good example better than from a rule list, and
keep only the dozen rules that actually fire near the top. This is the Anthropic prompt-engineering
recipe applied per audience. The always-on output style carries its audience-invariant core, and a
per-audience reference (a register or a conventions skill) carries the standard's pointer and its
exemplars.

Feedback is the external linter. Vale with the Google and Microsoft packages for docs; the
language-native linters for comments (gofmt and go vet for Go, ESLint with jsdoc and tsdoc for
TypeScript, ruff `D` for Python); an optional commit-message linter. Linters run as feedback (a hook
on save for the file types they cover, plus CI), never as a personal blocking wall. A clean linter run
is necessary and never sufficient, since a linter checks the mechanical standard, not whether the
writing is good.

## What this removes

- The `glw907` house overlay, everywhere. It is a house standard, not an external one.
- The four per-language tell catalogues. The external standards already state their semantic
  principles (comment the why, document the contract, do not paraphrase the code), and the canonical
  exemplars show them.
- The bespoke Svelte comment extractor. The `<script>` block is TypeScript and follows TSDoc; the
  `@component` block follows the Svelte convention.
- The personal-calibration framing in the docs registers, and the glw907 rule that treated the em
  dash as a tell in every register. The em dash now splits by audience: banned in code comments (a
  keyboard, grep, and monospace hygiene rule the comment standards omit, enforced by the comment
  linter where it can be), used per Google in developer docs (Google recommends it, with no
  surrounding spaces), per Microsoft in editor copy, and dropped in replies and commits.

"Write cleanly, avoid the AI tells" survives, but as Claude-best-practice feedforward, not as a house
linter.

## Per audience

Developer docs follow the Google Developer Documentation Style Guide. The Vale Google package is the
linter; Google's own published docs are the exemplar corpus.

End-user and editor docs follow the Microsoft Writing Style Guide. The Vale Microsoft package is the
linter; Microsoft Learn is the exemplar corpus.

Go comments follow Go Doc Comments and Effective Go. gofmt and go vet are the linters; the standard
library is the exemplar corpus, the best in any language.

TypeScript and Svelte comments follow TSDoc, with the Svelte `@component` convention for the component
block. ESLint with the jsdoc and tsdoc plugins is the linter; well-regarded libraries are the
exemplars. Two deterministic rules ride on it: `eslint-plugin-jsdoc`'s `informative-docs`, which flags
a comment that only restates the symbol name (the paraphrase tell), and an em-dash-in-comments ban (a
small local rule over comment tokens, since the one published plugin is an obscure v1.0.0). cairn is
the proving ground, and the bar is explicit: cairn's comments should be indistinguishable from
professional-grade TSDoc in a well-run TypeScript and Svelte codebase.

Python comments follow PEP 257 and PEP 8. ruff's `D` rules are the linter; the standard library is the
exemplar corpus.

Agent-facing files (CLAUDE.md, skills, agent definitions, hook text) follow Anthropic's Claude Code
best practices. There is no deterministic linter; the standard is guidance plus Anthropic's own
published examples.

Commit messages and PR bodies follow Conventional Commits and the established git-commit canon
(imperative mood, a concise subject, a body that explains why). commitlint is the optional linter.

Replies and email follow plain technical-communication norms as Claude best practice; there is no
linter.

## The reviewer

A read-only reviewer subagent gives the fresh-context second opinion on a substantial artifact. Its
question is conformance: does this read like the named standard's canonical examples? It does not
check a personal voice.

## Evaluation

The standard is the bar, and it is fixed and externally validated, so there is no moving target to
chase and no bespoke eval harness to build. Conformance is checked two ways: the linter
(deterministic, in CI) and a human or fresh-context read against the standard's exemplars. For a
single-author, human-in-the-loop workstation matching a published standard, the human reading the
output is the measure. An LLM-judge voice eval would be circular, since it asks a model to grade the
tells it produces, and it is not warranted here. A measurement harness is application-at-scale
practice, not doc-authoring practice.

## The refactor (separate plan, run as a workflow)

A refactor pass will drop `glw907` from the comment, docs, and agent-facing paths; delete the four
tell catalogues and the Svelte extractor; repoint the docs registers to canonical Google and Microsoft
exemplars; re-anchor the conventions skills as standard-plus-exemplar pointers; name and wire the
standards for agent-facing (Claude Code best practices) and commits (Conventional Commits); set the
vale-hook config to the external packages only; and keep the native comment linters. It then applies
the standard to cairn: a pass over cairn's TypeScript and Svelte comments to bring them to
professional-grade TSDoc, verified against the linter and a fresh-context read.

## Open items

- Svelte `<script>` comment linting. eslint-plugin-svelte needs the TypeScript sub-parser; until it is
  wired, the `<script>` block has no deterministic comment linter, only the TSDoc feedforward. This is
  the one comment-linter gap.
- Agent-facing has no deterministic linter, by nature. Accept guidance-only, or build a light
  CLAUDE.md and skill checker later.
- Commit linting is optional. Decide whether to wire commitlint.
