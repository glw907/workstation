# The authoring charter: write to external standards

This governs how Claude drafts on this workstation, across prose and code. Claude writes to
well-researched external standards, reached through a linter that encodes the standard and the
standard's own exemplars. It is not a quality gate for human-written content, and it is not a product
feature. A project points at this file to adopt the system; the adoption rule is at the end.

## The principle

Every artifact has one audience, and the audience selects a published standard: Google for developer
docs, Microsoft for end-user copy, Go Doc Comments and TSDoc and PEP 257 for code comments, the Claude
Code best practices for agent-facing files, Conventional Commits for commit messages. Name the
audience before drafting anything longer than a paragraph, then write to that standard.

One audience is the exception. Website content carries a site's own voice, and that voice lives in the
site's repo with its content guide, not here. Everywhere else the standard is external, so the
workstation keeps no house voice of its own, no house lexicon, and no per-model tell catalogue.

No audience, no system. A project that has not declared its audience map gets nothing automatic. The
system fails closed rather than falling back to a generic default.

## Two jobs

The system does two things. It guides Claude to write to the standard (feedforward), and it checks the
result against the standard (feedback). Feedforward is Claude best practices: name the audience, load
that standard's canonical exemplars, draft to it, reread once. Feedback is the standard's own linter. A
clean linter run is necessary and never sufficient, since a linter checks the mechanical standard, not
whether the writing is good.

## The audiences

| Audience | Standard | Linter | Exemplars |
|---|---|---|---|
| Developer docs | Google Developer Documentation Style Guide | Vale Google package | Google's own docs |
| Changelog, release notes, upgrade guide | Google Developer Documentation Style Guide | Vale Google package where the path is scoped | Google's own docs, the in-tree CHANGELOG |
| End-user and editor docs | Microsoft Writing Style Guide | Vale Microsoft package | Microsoft Learn |
| Go comments | Go Doc Comments, Effective Go | gofmt, go vet | the standard library |
| TypeScript and Svelte comments | TSDoc, plus the Svelte `@component` convention | ESLint jsdoc + tsdoc | well-regarded libraries |
| Python comments | PEP 257, PEP 8 | ruff `D` | the standard library |
| Agent-facing (CLAUDE.md, skills, agents) | Anthropic / Claude Code best practices | guidance, no linter | Anthropic's docs |
| Commit messages, PR bodies | Conventional Commits, the git-commit canon | commitlint (optional) | the convention's examples |
| Replies, email | plain technical communication | none | Claude best practices |
| Website content | the site's own voice (the sole personal voice) | the site's config | the site's corpus, in its repo |

A new kind of output is a new row, built the same way. The full design lives in the spec linked below.

## Adopt it in a project

A project opts in by pointing at this charter and declaring its audience map.

1. Add a line to the project CLAUDE.md: authoring follows `~/.claude/docs/authoring-charter.md`.
2. Declare the audience map: which paths serve which audience. For example `docs/**` is developer
   docs, `src/**/*.ts` is TypeScript comments, `content/**` follows the site content guide.
3. Carry the configs the map needs: a `.vale.ini` that selects the Google or Microsoft package per
   glob, and the per-language comment linter config (ESLint with jsdoc and tsdoc, ruff).
4. A project that serves a content audience carries its own `content-guide.md`. The charter supplies
   no generic one.

A project that declares nothing gets nothing automatic. That is the fail-closed rule working as
intended.

## What this is not

The discipline here is the workstation's, not any product's. A product that ships prose tooling to its
own users (cairn's editor spellcheck and tidy, for one) does that independently of this charter. A
repo that builds such a product is still an ordinary consumer of the charter for its own developer docs
and code comments.

## Pointers

- The full design is in
  `~/.dotfiles/docs/superpowers/specs/2026-06-22-authoring-standards-design.md`. It supersedes the
  earlier prose-system and code-comment specs, which described a personal-voice design.
- Register routing for prose lives in the `writing-voice` skill, and the registers in
  `~/.claude/docs/voice/`.

## Build state

The cutover landed (plan 07) and the external-standards refactor landed after it: the `vale-hook`
is the live prose feedback hook, the output style and the global CLAUDE.md are leaned to the
audience-invariant core, and the `writing-voice` skill routes the registers to canonical Google
and Microsoft exemplars. The agent-facing and commit standards are wired, the linters run on the
external packages (Vale's Google and Microsoft styles, ESLint's TSDoc config), and cairn's
TypeScript and Svelte comments hold to professional-grade TSDoc.
