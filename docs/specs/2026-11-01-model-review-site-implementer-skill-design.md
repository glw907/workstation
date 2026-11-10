# Give site-implementer a working path to the DaisyUI skill

## Brief

`site-implementer` must read the `standards:daisyui` skill before writing admin markup, and since
the plugin cutover it can't. Its tool list has no `Skill` tool, and the skill no longer has a path
it could `Read`. This design adds `Skill` to its tools and corrects the reach rule in
`claude-infra`. Approving it adds one line to one pass.

## Gap

`claude/.claude/agents/site-implementer.md:4` lists `Read, Write, Edit, Bash, Grep, Glob`. Lines
44-45 require the skill. `claude/.claude/skills/claude-infra/SKILL.md:63` still says a skill on disk
"reaches every agent, including the implementer and reviewer subagents that run a fixed tool list".
That held when skills were readable paths. A plugin skill reaches a fixed-list agent only through
the `Skill` tool or a preload.

## Evidence

The Claude Code subagents page gives two routes
(<https://code.claude.com/docs/en/sub-agents>). The `skills` field preloads a skill and "the full
skill content is injected". Without it, a subagent "can still discover and invoke project, user,
and plugin skills through the Skill tool", which needs that tool on the `tools` list.

## Proposed change

1. Add `Skill` to the `tools` line in `site-implementer.md`.
2. Word lines 44-45 as "invoke the `standards:daisyui` skill". This amends the audit's hunk for
   those lines.
3. Rewrite `claude-infra:63` to say a fixed-list agent reaches a plugin skill through `Skill` or a
   `skills:` preload.

I chose `Skill` over the preload. Most site tasks write no DaisyUI markup, and a preload would add
the skill's 114 lines to every dispatch. The contestable point is a missed invocation, which a
preload rules out. If a close review catches one, the next pass switches to the preload.

The acceptance test is one dispatch on an admin-markup task whose transcript shows the skill
invoked. This is `runner`, and it lands inside the audit-fixes pass.

## Audit findings taken

The flag `site-implementer.md:4, 44` (tools list has no `Skill`). It also settles the medium finding
`site-implementer.md:44-45`.
