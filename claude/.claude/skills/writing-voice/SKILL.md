---
name: writing-voice
description: Use when drafting or revising any substantial prose (a doc, plan, spec, README, design note, commit message, PR body, or site content) to load the audience's external standard, its canonical exemplars, and the shape rules. The on-demand router for the workstation voice system.
---

# Writing voice: the on-demand router

Every audience starts from a published external standard. A repo may carry a named house voice on top
of it as a recorded overlay, which never replaces the base standard's structure and records each
departure with its provenance and Geoff's ruling; cairn's docs voice is the named example. The
always-on `writing-voice` output style carries the audience-invariant core: vary sentence length, one
idea per sentence, avoid the AI-writing tells. This skill is the router. Name the audience, open the
register or conventions skill that holds its standard and exemplars, and follow the shape rules below. Load it
before drafting anything longer than a paragraph, and imitate the standard's canonical exemplars
rather than reaching for more rules. The model generalizes from a good example better than from a
rule list, so the exemplars are the stronger attractor. This router is the entry point to the
authoring charter (`~/.claude/docs/authoring-charter.md`).

## Pick the standard

| Artifact | Standard | Where the exemplars live |
|---|---|---|
| Developer docs, README, or design doc in a Go repo | Google Developer Documentation Style Guide | `~/.claude/docs/voice/technical-doc-go.md` |
| Developer docs, README, or design doc in a SvelteKit or web repo | Google Developer Documentation Style Guide | `~/.claude/docs/voice/technical-doc-web.md` |
| Published cairn-cms docs (`docs/admin/`, `docs/extend/`, `docs/reference/`, the front door, the changelog) and cairn.pub's own prose | Google, with the cairn docs voice overlay | the developer-docs drafting brief in cairn-cms `docs/internal/docs-register.md` |
| Published cairn-cms editor docs (`docs/editors/`) | Microsoft Writing Style Guide, with the cairn docs voice overlay | the editor-docs drafting brief in cairn-cms `docs/internal/docs-register.md` |
| Changelog entry, GitHub release note, or upgrade-guide entry | Google Developer Documentation Style Guide (the developer reading the changelog is the same reader as the docs) | `~/.claude/docs/voice/technical-doc-web.md` (Go repo: `technical-doc-go.md`) |
| End-user and editor product copy, UI-only walkthroughs with no terminal step | Microsoft Writing Style Guide | `~/.claude/docs/voice/editor.md` |
| CLAUDE.md, skills, agent definitions, hook text | Anthropic Claude Code best practices | `~/.claude/docs/voice/agent-facing.md` |
| Commit messages and PR bodies | Conventional Commits and the git-commit canon | `~/.claude/docs/voice/commit-and-pr.md` |
| Go code comments | Go Doc Comments, Effective Go | the go-conventions skill |
| TypeScript code comments | TSDoc | the ts-conventions skill |
| Svelte code comments | TSDoc plus the Svelte `@component` convention | the svelte-conventions skill |
| Python comments and docstrings | PEP 257, PEP 8 | the python-conventions skill |
| Site content (pages, posts, form copy) | the site's own content guide | the site repo's `docs/content-guide.md`, via the content-draft skill |

Site content is the one personal voice, and it lives in the site repo, out of the workstation's
scope. Every other audience starts from its external standard. The web dialect follows the repo's stack;
a project CLAUDE.md may override with an explicit register line.

## Document shape

Shape-level tells read as machine-written even when every sentence is clean.

- Paragraphs over bullets. A bullet list is for a true enumeration (options, fields), not for prose
  that happens to carry three points. If the items read as sentences with a shared subject, write
  the paragraph. A sequence of actions is a numbered list, never a paragraph.
- No scaffold headers. "Overview", "Introduction", "Conclusion", and "Summary" are filler in anything
  shorter than a book chapter. A header serves a reader who navigates by it.
- Do not open every bullet or paragraph with a bolded lead phrase. Sparingly it signposts; by reflex it
  is the machine list default.
- One register per artifact. Do not drift from runbook to essay mid-document.

## Facts discipline

Register fluency invites invention. Prose that reads like the standard's author tends to fill
gaps with confident specifics, and the polish makes them convincing. In every register, work
only from facts you were given or verified: a detail the source does not state (an option, a
command, a behavior, a number) is a fabrication, and leaving it out beats completing the
picture. Fidelity outranks fluency; the 2026-09-01 benchmark found invented specifics were
this system's one systematic failure mode, costing otherwise-winning drafts their blind
comparisons.

## Author-facing prose

A stated length, count, or format in the brief is a requirement, not a suggestion. Terseness
trims padding; it does not license undershooting a floor the brief sets (the 2026-09
benchmark lost drafts to this exact trade). When the given facts run out before the floor,
meet it by saying more about those facts: what the reader sees when a command runs, why a
step matters, what a value controls. Never meet it by inventing new facts, and never treat
brevity as permission to deliver less than the brief asked for.

A page for an outside reader needs a brief file before it needs an outline: what the page
must carry, who reads it, and what its type does not already cover. The outline is reviewed
against that brief before any sentence is drafted or reviewed, because prose work on a page
whose shape is wrong is wasted, and a page with no brief has no outline to check against.

Draft one section per read for the cairn front door only (`why-cairn.md`, `docs/README.md`, the
arm READMEs); a front-door page is never drafted end to end in an autonomous run: stop after each
section and let a reader see it before the next one starts. An unread run is how a page can pass
every mechanical gate and still fail the reader who opens it first. Every other page, including a
cairn narrative arm, is drafted whole by its chain.

## The em dash

The `writing-voice` output style owns the em-dash policy: banned in code comments (the comment linter
enforces it), Google's no-space form in developer docs, sparing in editor copy, none in a reply or a
commit message, and the site's own voice in site content. Overuse is a tell in any register.

## Where the rules are encoded

- The registers under `~/.claude/docs/voice/` and the four conventions skills: each names its external
  standard, its linter, and its canonical exemplars. Lean on the exemplars harder than on any rule list.
- Vale, per repo `.vale.ini`, with the Google package on developer docs and the Microsoft package on
  editor copy: the deterministic net on docs prose. The `vale-hook` feeds its findings back as advisory
  context on save, and CI runs the same config. The native comment linters cover code comments (gofmt and
  go vet, ESLint jsdoc and tsdoc, ruff `D`).
- `tellgrader` (`~/.local/bin`, source in this skill's `evals/tellgrader/`): the register-aware
  AI-tell scanner, evidence-grounded in `evals/research/`. It catches what Vale does not (contrast
  frames, connector openers, the slop lexicon, scaffold headers, flat cadence, per-register em-dash
  rules) and runs on save via its `--hook` mode alongside `vale-hook`. The `prose-voice-reviewer`
  agent runs it as the deterministic floor before spending judgment.
- The `writing-voice` output style: the always-on audience-invariant core.
- This skill: the router and the shape rules.
