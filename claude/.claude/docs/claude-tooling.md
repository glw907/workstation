# Claude Code tooling on this workstation

Where every piece of Claude Code infrastructure lives, what owns it, and the rule that keeps
it tidy: **every install records itself in its manifest in the same session, and
`claude-tooling-sync verify` (also run by `check-drift`) reconciles the manifests against the
machine.** The manifests record intent; the script reports what happened.

## Layout

| Piece | Lives at | Manifest | Applied by |
| --- | --- | --- | --- |
| Skills (authored here) | `~/.dotfiles/claude/.claude/skills/<name>/` (stowed) | the directory itself | stow |
| Skills (vendored, third party) | same directory | `~/.claude/tooling/vendored-skills.json` (stowed) | `claude-tooling-sync update-skills` |
| Agents | `~/.dotfiles/claude/.claude/agents/<name>.md` (stowed) | the directory itself | stow |
| Docs (this file and its siblings) | `~/.dotfiles/claude/.claude/docs/` (stowed) | the directory itself | stow |
| Instructions (cross-repo reference docs, linked from consumer CLAUDE.md files) | `~/.dotfiles/claude/.claude/instructions/` (stowed) | the directory itself | stow |
| Workstation `CLAUDE.md`, `settings.json` (hooks, plugins, models) | `~/.dotfiles/claude/.claude/` (stowed) | `settings.json` | stow |
| Plugins | Claude Code's plugin cache | `settings.json` `enabledPlugins` + `extraKnownMarketplaces` | `claude plugin install` |
| MCP servers, user scope | `~/.claude.json` (not in git; holds other state) | `~/.claude/tooling/mcp-servers.json` (stowed) | `claude-tooling-sync apply` |
| MCP servers, project scope | a repo's `.mcp.json` | that repo | the repo's own CLAUDE.md names it |
| Secrets a server needs | the age store, `~/.local/secrets` | `~/.dotfiles/secrets/registry.md` | `secret-receive`, `sync.sh` |
| Memory | `~/.claude/projects/<repo>/memory/` | `MEMORY.md` index per repo | the session |
| Workflows | `~/.claude/workflows/` (invoked by name, never from a scratchpad copy) | the directory | the Workflow tool |

## Rules

- **Scope by reach.** A skill on disk reaches every agent, including the implementer and
  reviewer subagents that run a fixed tool list; an MCP server reaches only the main loop and
  unrestricted agents. When a library offers both, take the skill first and the server for
  on-demand retrieval or tools the skill cannot carry.
- **User scope for stack-wide, project scope only for repo-specific.** Everything the
  cairn-family stack shares (Svelte, Playwright, DaisyUI) is user scope and in the manifest.
  A repo's `.mcp.json` carries only what that repo alone needs, and its CLAUDE.md says so.
- **Prefer a vendored skill to a plugin when the plugin brings hooks or servers that
  duplicate workstation pieces** (Vale's plugin ships an edit hook the workstation
  `vale-hook` already covers, so its skills are vendored and the plugin is not installed).
  Record the source, commit, and license in the manifest.
- **Credentials come from the age store.** A server's env values stay in `${VAR}` form in
  the manifest and resolve from `~/.local/secrets` at session start; launch Claude Code from
  a shell that sourced them. Never a value in `.mcp.json`, a manifest, or a transcript.
- **Read a third-party skill before vendoring it.** It is instructions injected into every
  future session. Check the license, the maintainer, and the text.
- **Every addition gets three lines:** the manifest entry, a line in the workstation
  `CLAUDE.md` section that governs it (or the repo's), and, when a rule of use came with it,
  that rule in its execution path (the agent definitions or skills that use the piece, else
  this file's inventory), never a memory. Then `claude-tooling-sync verify` and commit the
  dotfiles.
- **A restart loads new servers; skills and agents load live.** Restart at a session
  boundary, never mid-run (a Workflow run dies with its session).

Model pins (2026-09-22, aligned with Anthropic's model guidance 2026-09-23; see
`model-economy.md`): every reviewer agent under `agents/` and every workflow script under
`workflows/` names `claude-opus-5-5` explicitly (`diff-reviewer`, the four domain reviewers,
`engine-triage`, `go-architecture-reader`, `figure-verifier`, `visual-verifier`,
`prose-voice-reviewer`, `cairn-register-editor`; `pass-execute.js`, `pass-execute-chains.js`,
`docs-page-chain.js`). `cairn-docs-drafter` (the docs page chain's default drafter, `effort: high`)
also pins `claude-opus-5-5` explicitly and carries no `skills:` line; the page-inputs step's
output (job, page type, exemplar excerpts, fact ids, claim inventory) arrives in the dispatch
prompt, never a separate profile arg or file. No agent pins Fable 5.1; it is reached only by a per-dispatch escalation.
Implementers stay on `sonnet` at effort `high`; the docs page chain drafts published pages on
`claude-opus-5-5` (its `drafterModel` default, Geoff 2026-09-22). A frontmatter pin is read at session start, so a repin reaches a
running session only through a per-dispatch `model`; verify a repin from a fresh headless session
by grepping the subagent transcript's `"model"` field, never from the agent's own answer.

## Procedures

```
claude-tooling-sync apply                 # add manifest servers missing at user scope
claude-tooling-sync verify                # drift report; exit 1 on drift (check-drift runs it)
claude-tooling-sync update-skills [name]  # re-fetch vendored skills, rewrite the pinned commit
claude mcp list                           # connection health per server
claude plugin details <plugin>            # a plugin's components and token cost
```

Adding a user-scope server: write its entry in `mcp-servers.json` (with a `_why`), run
`apply`, verify with `claude mcp get <name>` (with the secrets sourced), add the CLAUDE.md
line, commit. Removing one: delete the entry, `claude mcp remove -s user <name>`, verify.

Adding a vendored skill: read it at the source, add its entry to `vendored-skills.json`, run
`update-skills <name>`, review the diff, point the agents that need it at the skill file,
commit skills and manifest together.

## Inventory of third-party pieces (2026-09-13)

- **DaisyUI:** the official skill (vendored) and the licensed Blueprint server (user scope).
  The server entry runs `daisyui-blueprint-mcp` (dotfiles bin), which sources `~/.local/secrets`
  at spawn and maps the license pair to `LICENSE` and `EMAIL`; a `${VAR}` env entry resolves from
  the launching shell, and a terminal older than the secret leaves it empty (born 2026-09-14).
  The license serves DaisyUI work in every project on this workstation (Geoff, 2026-09-13).
  The license pair lives in the age store (registry entry in `~/.dotfiles/secrets/registry.md`),
  never in a committed `.mcp.json`. Rule of use: the skill at `~/.claude/skills/daisyui/` (one
  guide per component) is what reaches implementer and reviewer subagents, which run without
  MCP, so `cairn-implementer` and `daisyui-a11y-reviewer` point at it; for any DaisyUI markup,
  read the component guide first and ask Blueprint from the main loop when the guide is thin.
  The DaisyUI-first rule itself is the workstation CLAUDE.md section "Claude tooling:
  manifests, scopes, and the DaisyUI-first rule". Standing uses (Geoff, 2026-09-13; audit record
  `~/Projects/cairn-cms/docs/internal/record/2026-09-13-blueprint-audit.md`): a pre-cut admin
  audit (first run 2026-09-21), `component_syntax_expert` during plan authorship for a new admin
  component, a rerun after every DaisyUI bump, and the same audit over the consumer sites' admin
  screens; the converters and greenfield design tools stay unused. **Owed, not built:** a
  dotfiles command `blueprint-audit <files>` that drives the server over stdio with the secrets
  sourced (initialize, `setup_expert` with a workflowId and the repo root, `rules_enforcer`,
  `quality_inspector` in report-only mode), filtering the known false positives (tag names
  matched inside doc comments; utilities and documented custom classes reported as unknown),
  and wired in as an advisory step of the per-task gate for admin-markup tasks.
- **Dependency upgrades:** the authored `dependency-upgrade` skill (2026-09-14), the procedure every
  bump in every repo follows; the global CLAUDE.md "Dependencies" section is the standing rule.
- **Spec and plan review:** the authored `spec-plan-review` skill (2026-09-23), the lens fan-out,
  fold, verification read, and prose review every spec or plan takes before owner approval; the
  global CLAUDE.md "Conducting a pass" section points at it.
- **Svelte:** the official server (user scope, remote).
- **Playwright:** Microsoft's server (user scope, stdio).
- **Vale:** five official skills (vendored). The workstation `vale-hook` stays the edit hook.
- **Cobra:** one community skill (vendored, MIT) for the cairn Go tool; `go-conventions`
  and `elm-conventions` stay mandatory.
- **Plugins:** superpowers, code-review, code-simplifier, frontend-design, skill-creator
  (Anthropic); cloudflare; tui-design.

Decided against: a docs-only cairn MCP server (the tarball docs plus a skill reach every
agent), the GitHub MCP server (the `gh` CLI covers it at a third of the tokens), Tailwind,
Vite, Vitest, CodeMirror, unified, and ESLint servers (none official, no gap). Survey:
cairn session record of 2026-09-13.
