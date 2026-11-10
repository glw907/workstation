# Make the secret guards fail closed

## Brief

The two guards that protect secrets let a command through if the guard crashes or times out. Claude
Code 2.1.295 added a setting that blocks the action instead, and `claude-merge-guard` already uses
it. This design adds that setting to `claude-secret-guard` and `claude-block-pass`. Approving it
starts one `runner` pass that needs your read, since a broken guard would then stop every Bash call.

## Gap

The live `settings.json` registers `claude-merge-guard` with `onFailure: "block"`. The registrations
of `claude-secret-guard` (Bash and Write|Edit) and `claude-block-pass` (Bash) set no `onFailure`.
These are the two policy hooks whose job is to keep credentials safe.

## Evidence

Hooks reference (<https://code.claude.com/docs/en/hooks>):

- "A policy hook with a wrong path or a crashing script then lets everything through."
- "don't count on a stalled hook to act as a gate."
- `"onFailure": "block"` covers a hook that can't start, times out, or exits with an unexpected code.

Features overview: "If a rule must hold every time, make it a hook rather than a prompt
instruction" (<https://code.claude.com/docs/en/features-overview>). The setting is what makes that
hold when the hook itself fails.

## Proposed change

1. Add `"onFailure": "block"` to the three registrations in `claude/.claude/settings.json`.
2. Raise the `claude-secret-guard` Bash timeout from 10 to 30 seconds, matching the merge guard.
   That hook scans a commit's tree, and a timeout now refuses the commit.
3. Run `claude-tooling-sync apply`, then test with a `--settings` file in a scratch session that
   points a registration at a script that exits 1. The Bash call must be refused.

`claude-tierguard`, `claude-tail-guard`, and `claude-memory-write-check` stay as they are. They are
slip guards, and a failure there costs little.

The contestable point is recovery. If `claude-secret-guard` breaks, Claude can't run Bash or edit a
file, including the fix. You would repair it from a plain terminal. That's the right trade for a
hook born from a committed token, but it's your call.

This is `runner` for `settings.json`. The pass changes no guard code, so it doesn't reach the
`auth-data` paths.

## Audit findings taken

None. The audit didn't read settings files. This came from the changelog.
