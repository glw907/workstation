---
name: claude-infra
description: >
  Use when adding or changing a rule, hook, skill, agent, workflow, CLAUDE.md text, settings.json,
  MCP server, plugin, or the pass process on this workstation. Create a skill when you keep pasting
  the same instructions, checklist, or multi-step procedure into chat, or when a section of
  CLAUDE.md has grown into a procedure rather than a fact. Covers where a rule lives and how to
  land it.
---

# Claude infrastructure changes

Follow this for any change to how Claude Code behaves on this workstation. Layout, manifests, and
the inventory are in `~/.claude/docs/claude-tooling.md`.

## Procedure

1. **Cite the Anthropic page the change follows, and prefer a built-in.** Name the page's URL
   before writing. If Claude Code already does it, configure that rather than build a copy. To
   write a hook or setting into `settings.json`, use the built-in `update-config` skill for the
   mechanics; this skill only decides whether a hook or setting is the right home.
2. **Choose the strongest home: hook, then skill or agent, then CLAUDE.md.** Anthropic's
   features overview (<https://code.claude.com/docs/en/features-overview>): "If a rule must hold
   every time, make it a hook rather than a prompt instruction." And: "Put it in a skill if it's
   reference material Claude needs sometimes". CLAUDE.md carries only a fact that applies every
   turn.
3. **Keep one home per rule, with its manifest.** Which manifest is the "Layout" table in
   `claude-tooling.md`. Run `claude-tooling-sync verify` after.
4. **Trace scope to a stated need.** Every change, and every plan or executing dispatch for one,
   applies Anthropic's own words. Prompting best practices
   (<https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices>):
   "Avoid over-engineering. Only make changes that are directly requested or clearly necessary.
   Keep solutions simple and focused: - Scope: Don't add features, refactor code, or make
   "improvements" beyond what was asked. A bug fix doesn't need surrounding code cleaned up. A
   simple feature doesn't need extra configurability. ... - Defensive coding: Don't add error
   handling, fallbacks, or validation for scenarios that can't happen. Trust internal code and
   framework guarantees. Only validate at system boundaries (user input, external APIs). -
   Abstractions: Don't create helpers, utilities, or abstractions for one-time operations. Don't
   design for hypothetical future requirements. The right amount of complexity is the minimum
   needed for the current task." Prompting Claude Opus 5
   (<https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5>):
   "Deliver what was asked, at the scope intended. Make routine judgment calls yourself, and check
   in only when different readings of the request would lead to materially different work. If the
   request seems mistaken or a better approach exists, say so in a sentence and continue with the
   task as asked rather than quietly narrowing, widening, or transforming it. Finish the whole
   task, and stop short of actions that are clearly beyond what was asked." Anything beyond the
   request goes in "Later", never into a task.
5. **Land the change through a PR** whose commit messages and body cite the guidance URL.
6. **Audit** with `/doctor prompt-audit`, `/skill-doctor`, and Anthropic's `skill-creator`. Run
   them; their output is the audit, not a restatement here.

## A rule lives where it executes (Geoff, 2026-09-20)

A rule reaches an agent only through its definition, its dispatch prompt, its runner, or a
tool's output; a side doc reaches nobody. Land a rule the same session, strongest form first:
tool, agent definition or skill, then CLAUDE.md (Geoff, 2026-09-27). Anything recorded routes
by default: initiative state to STATUS or ROADMAP; a repo fact to its docs; a workstation fact
to `~/.claude/docs`. Memory holds only a preference or a ruling's why that no file can. Act on
a tool's NOTE before the next dispatch.

## Rules for tooling

- Scope by reach. A skill on disk reaches every agent, including the implementer and
  reviewer subagents that run a fixed tool list; an MCP server reaches only the main loop and
  unrestricted agents. When a library offers both, take the skill first and the server for
  on-demand retrieval or tools the skill cannot carry.
- User scope for stack-wide, project scope only for repo-specific. Everything the
  cairn-family stack shares (Svelte, Playwright, DaisyUI) is user scope and in the manifest.
  A repo's `.mcp.json` carries only what that repo alone needs, and its CLAUDE.md says so.
- Prefer a vendored skill to a plugin when the plugin brings hooks or servers that
  duplicate workstation pieces (Vale's plugin ships an edit hook the workstation
  `vale-hook` already covers, so its skills are vendored and the plugin is not installed).
  Record the source, commit, and license in the manifest.
- Credentials come from the age store. A server's env values stay in `${VAR}` form in
  the manifest and resolve from `~/.local/secrets` at session start; launch Claude Code from
  a shell that sourced them. Never a value in `.mcp.json`, a manifest, or a transcript.
- Read a third-party skill before vendoring it. It is instructions injected into every
  future session. Check the license, the maintainer, and the text.
- Every addition gets the manifest entry and, when a rule of use came with it,
  that rule in its execution path (the agent definitions or skills that use the piece, else
  the inventory in `claude-tooling.md`), never a memory. Then `claude-tooling-sync verify` and
  commit the dotfiles.
- A restart loads new servers; skills and agents load live. Restart at a session
  boundary, never mid-run (a Workflow run dies with its session).
