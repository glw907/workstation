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
| Workstation `CLAUDE.md` | `~/.dotfiles/claude/.claude/` (stowed) | the file itself | stow |
| `settings.json` (hooks, plugins, env) | tracked at `~/.dotfiles/claude/.claude/settings.json`, generated into `~/.claude/settings.json` (a real file, never stowed) | the tracked file | `claude-tooling-sync apply` |
| Plugins | Claude Code's plugin cache | `settings.json` `enabledPlugins` + `extraKnownMarketplaces` | `claude plugin install` |
| MCP servers, user scope | `~/.claude.json` (not in git; holds other state) | `~/.claude/tooling/mcp-servers.json` (stowed) | `claude-tooling-sync apply` |
| MCP servers, project scope | a repo's `.mcp.json` | that repo | the repo's own CLAUDE.md names it |
| Secrets a server needs | the age store, `~/.local/secrets` | `~/.dotfiles/secrets/registry.md` | `secret-receive`, `sync.sh` |
| Memory | `~/.claude/projects/<repo>/memory/` | `MEMORY.md` index per repo | the session |
| Workflows | `claude/.claude/workflows/` in `~/Projects/drafter`, installed by its `make install` (invoked by name; see "Workflows" below) | the directory | the Workflow tool |

## Rules

The rules for adding or changing any piece live in the `claude-infra` skill.

## Model pins

Model pins (2026-09-22, aligned with Anthropic's model guidance 2026-09-23; the seats are in
`pass-core` "Models"): every reviewer agent under `agents/` and the workflow script
`docs-page-chain.js` (source repo `~/Projects/drafter`, linked into the live
workflows directory by `make install`) names `claude-opus-5-5` explicitly (`diff-reviewer`, the four domain
reviewers, `engine-triage`, `go-architecture-reader`, `figure-verifier`, `visual-verifier`,
`prose-voice-reviewer`, `cairn-register-editor`, `plan-reviewer`). `cairn-docs-drafter` (the docs page chain's
default drafter, `effort: high`) also pins `claude-opus-5-5` explicitly and carries no `skills:`
line; the page-inputs step's output (job, page type, exemplar excerpts, fact ids, claim inventory)
arrives in the dispatch prompt, never a separate profile arg or file. No agent pins Fable 5.1; it
is reached only by a per-dispatch escalation. Implementers stay on `sonnet` at effort `medium`; the
docs page chain drafts published pages on `claude-opus-5-5` (its `drafterModel` default, Geoff
2026-09-22). A frontmatter pin is read at session start, so a repin reaches a running session only
through a per-dispatch `model`; verify a repin from a fresh headless session by grepping the
subagent transcript's `"model"` field, never from the agent's own answer.

`worktree.baseRef: "head"` in the tracked `settings.json` applies in every repo, so subagent and
`--worktree` branches start from the local `HEAD`, not the remote default (code.claude.com/docs/en/
worktrees, "Choose the base branch").

## Model defaults

`CLAUDE_CODE_SUBAGENT_MODEL=sonnet` sits in `~/.claude/settings.json` `env`. It reaches only
dispatches with no model of their own: `general-purpose`, `claude`, unpinned custom agents, and
Workflow `agent()` without `model`. Frontmatter pins and a per-dispatch `model` both win over it,
and a settings value outranks a shell export, so it also reapplies to running sessions. Forcing it
onto `Explore` or `Plan` would override every frontmatter pin. `/effort` persists per model into
`modelSettings` in the generated `~/.claude/settings.json`, which is outside git, so reset it at
the end of a session that raised it.

`~/.claude/settings.json` is generated, not stowed: `claude/.stow-local-ignore` names the tracked
file, and `claude-tooling-sync apply` writes the live file as the tracked keys over the live
keys. A key the tracked file does not set, such as `model`, `effortLevel`, and `modelSettings`,
keeps its live value. The tracked keys win at `apply`: a Claude Code command that writes a tracked
key, such as `/tui` (`tui`) or `/memory` (`autoMemoryEnabled`), shows as `verify` drift until the
change is committed to the tracked file, and the next `apply` reverts it. A merge that changes the
tracked file reaches the live one only through `apply`.

## Workflows

`docs-page-chain.js` and its `cairn-docs-outline` helper live in `~/Projects/drafter`
(`claude/.claude/workflows/`, `bin/.local/bin/`), and `make -C ~/Projects/drafter install` links them
into the live workflows directory and `~/.local/bin/`. This repo keeps no workflow script. A
machine that still has the old stow links restows (`stow -R bin claude`) before running the install,
which refuses to write through a symlink.

Invoke a workflow by name, never from a scratchpad copy, so every run executes the
committed script. By-name resolution can serve a stale copy after the script changed in the same
session (2026-10-01: run `wf_55b254af-82a` ran an earlier commit and redrafted six pages). Before
relying on a run, `cmp` the persisted script the tool returns against the committed file. On a
mismatch, stop the run, copy the committed file over that returned path, and relaunch with
`scriptPath`. When the tool refuses that path (2026-10-03, after the session's working directory
changed), copy the committed file into the session scratchpad, `cmp` it, and relaunch from there.

## Procedures

```
claude-tooling-sync apply                 # add manifest servers missing at user scope
claude-tooling-sync verify                # drift report; exit 1 on drift (check-drift runs it)
claude-tooling-sync verify --home <dir> --projects-root <dir>  # point verify at an injected tree
claude-tooling-sync update-skills [name]  # re-fetch vendored skills, rewrite the pinned commit
claude-tooling-sync lint --root <tree>    # tree-only manifest and unmanifested-skill checks;
                                           # check.sh runs `lint --root .` from a worktree's own
                                           # checkout, never through ~/.claude
claude mcp list                           # connection health per server
claude plugin details <plugin>            # a plugin's components and token cost
```

`verify` also fails when a personal skill's name equals a `~/Projects/*/.claude/skills/<name>`
project skill (personal shadows project); `--projects-root` points the collision check at an
injected tree instead of the real `~/Projects`.

Adding a user-scope server: write its entry in `mcp-servers.json` (with a `_why`), run
`apply`, verify with `claude mcp get <name>` (with the secrets sourced), add a CLAUDE.md line only
for a fact that applies every turn, commit. Removing one: delete the entry, `claude mcp remove -s user <name>`, verify.

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
- **Spec and plan review:** the authored `spec-plan-review` skill (2026-10-10 rewrite), the review
  every spec or plan takes before owner approval; its depth scales with the design's size, and it
  dispatches the `plan-reviewer` agent. `pass-core` points at it.
- **Svelte:** the official server (user scope, remote).
- **Playwright:** Microsoft's server (user scope, stdio).
- **Vale:** five official skills (vendored). The workstation `vale-hook` stays the edit hook.
- **Cobra:** one community skill (vendored, MIT) for the cairn Go tool; `go-conventions`
  and `elm-conventions` stay mandatory.
- **TUI work:** the order of use is the house skills (`elm-conventions`, `bubbletea-design`,
  `tui-visual-verify`), then Charm's agent guide for the Crush UI (pinned in `elm-conventions`),
  then the `tui-design` plugin. `tui-design` (gfargo, MIT) is consulted for layout and
  discoverability patterns; the house skills win on any conflict.
- **Plugins:** superpowers, code-review, code-simplifier, frontend-design, skill-creator
  (Anthropic); cloudflare; tui-design.

Decided against: a docs-only cairn MCP server (the tarball docs plus a skill reach every
agent), the GitHub MCP server (the `gh` CLI covers it at a third of the tokens), Tailwind,
Vite, Vitest, CodeMirror, unified, and ESLint servers (none official, no gap). Survey:
cairn session record of 2026-09-13.
