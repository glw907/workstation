# Point the Playwright allow rules at the real server

## Brief

Two permission rules for read-only browser tools name an MCP server that doesn't exist here, so they
never match. This design renames them. Approving it starts one small `runner` pass that changes two
lines in `settings.json`.

## Gap

`claude/.claude/settings.json:66-67` allows `mcp__playwright-chromium__browser_take_screenshot` and
`mcp__playwright-chromium__browser_snapshot`. Commit `cf0c100` added them on 2026-10-17, for
read-only calls that had stopped sessions.

The server's key in `claude/.claude/tooling/mcp-servers.json` has been `playwright` since 2026-09-13.
Its tools reach a session as `mcp__playwright__*`. `playwright-chromium` appears nowhere else on
`main`, in `~/.claude.json`, or in `ecxc-ski/.mcp.json`, the one such file among the six repos I
checked. I checked `thinkpad-x1` only.

## Evidence

Changelog 2.1.299: "Changed MCP allow rules to reach only the server they name"
(<https://code.claude.com/docs/en/changelog>). A rule with the wrong server name allows nothing.

## Proposed change

1. Replace both rules with `mcp__playwright__browser_take_screenshot` and
   `mcp__playwright__browser_snapshot`.
2. Run `claude-tooling-sync apply`.
3. Before the edit, confirm `pavilion` has no `playwright-chromium` server, with
   `grep -c playwright-chromium ~/.claude.json`. If it does, the fix is to rename that server to
   match the manifest, and these rules stay.

The rename restores what `cf0c100` meant to allow, and both tools only read a page. This is `runner`,
since it changes a permission rule, so it lands only on your approval.

## Audit findings taken

None. The audits don't read settings files.
