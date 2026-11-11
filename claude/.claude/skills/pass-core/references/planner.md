# Planner

Read after `pass-core` `SKILL.md`. A plan review adds this file's "Stops" and
"Pre-flight" items to the `standards:plan-reviewer` prompt.

## Design

The design is the page or less `running-passes` "Design" sets out, opening with `## Brief` per
`~/.claude/docs/voice/approval-brief.md`, with an owner fork as a `### Decide:` block. It names its
initiative or says none applies; cross-repo specs, plans, and research go in
`~/Projects/initiatives/<id>/`. It names the published practice and vendor docs it drew on.
After a pass misses its bar, the next design reads that pass's final artifacts against the code
and traces each wrong claim to its source.

A design that adds a project, a service, or running infrastructure names where it runs and why,
after weighing Cloudflare against the Hetzner servers orpheus and ward: what
fails together, what the host already carries, cost, and how backup and restore cover it. It never
defaults to the host at hand (Geoff, 2026-10-22).

Every design runs the `standards:backlog-sweep` scoped sweep, and its full sweep when one is due.
The design lists the verdicts, and approving it approves the backlog edits; a backlog round takes
its scope from the verdicts and lists each drop with its reason (Geoff, 2026-10-27 and
2026-10-25). A polish
loop's rounds are commits on one branch and one PR, with one whole-branch review after the last.

The estimate is in path minutes, set from the actual-against-planned path in recent scores. A plan
over twice the estimate returns to Geoff with the reason before launch; the path sets that
stop, never the sum over every task (Geoff, 2026-10-12). A test never cuts a
release candidate (Geoff, 2026-11-09): a run that needs a published build publishes a snapshot, a
`dev` prerelease under a test dist-tag, with no GitHub release, rc tag, or
changelog heading
(<https://github.com/changesets/changesets/blob/main/docs/snapshot-releases.md>).

## Stops

The design's approval asks how to answer each stop the run can foresee, including an estimate
overrun up to a named ceiling, and records each answer as a standing approval. A stop with no
standing answer still stops (Geoff, 2026-10-12).

No count cap stops the line on its own (Geoff, 2026-10-19). Past one, the run goes on while each
retry fixes a traced cause inside the ceiling, each fix a reversible change listed in
`## Decisions`. A cause that returns gets one structural fix that
replaces the unit the patches kept missing; if it returns again, the session escalates the item
in the PR and goes on, where the plan allows that item's escalation. The run stops only on the
spend or path ceiling, an untraced cause, or an escalation the plan doesn't allow.

## Pre-flight

The plan opens with a `## Pre-flight` list, and every necessary permission is gathered there, up
front (Geoff, 2026-11-01). It carries a `Permissions checked:` line and a `Reviewed:` line, which
`claude-launch-guard` requires.

- The list names every step only Geoff can do (a sign-in, a `secret-receive` value, a dialog, a
  permission rule, a physical action) with the check that shows it done. The design's packet
  carries the foreseen ones as `[you: ...]` steps for its sitting. An item the plan adds holds
  the launch for a pre-launch packet and is a planning miss.
- Every value the run needs is looked up in the stores first.
- Each task's writes are read against auto mode. A write to Claude's settings, a credential file,
  or new public surface gets a `[you]` item or a path a probe proved in a `claude --bg` session,
  and so does a credential with Geoff's login or a sourced-secret command. A step the merges
  need is settled before launch, never between merges.
- A bulk Proton Pass edit is a `[you]` step through `pass-sitting` (`proton-pass` skill).
- An open `[you]` item at an armed launch is checked at arm time, and the standing answer says
  what a proof step does once the run has moved live state (Pass 5, 2026-10-31).
- A launch in a directory no session has opened lists the workspace trust prompt, checked by a
  launch that doesn't print "Workspace not trusted" (2026-11-10).
- A workstation-config pass states what each host gets; one ending in a reboot or `check-drift`
  has a standing answer for reversible drift.

## Launch

A design approved with unattended planning lets the planner run steps 2 to 4 and launch without
Geoff. A plan over twice the estimate, or a finding that changes the design, stops it: STATUS
carries one question, and `notify-send -u normal` tells Geoff. The planner writes the initiative
record once, when it commits the design, plan, and prompts.

Before the launch, every `## Pre-flight` item is checked, and the main checkout is on its default
branch with `git -C <repo> rev-list --count HEAD..origin/<default>` printing 0 after a fetch. Where
`git -C <repo> check-ignore -q .claude/worktrees/x` fails, append `.claude/worktrees/` to the file
`git -C <repo> rev-parse --path-format=absolute --git-path info/exclude` names. Launch from the
main checkout:

```
claude --bg --model sonnet --effort medium --name <project>-<pass> "$(cat <prompt file>)"
```

The prompt goes before any `--add-dir`, which is variadic. Then read
`~/.claude/jobs/<id>/state.json`: `needs: "send a prompt to start"` is a failed launch. A stray
job ends with `claude stop <id>`. A conductor's hand-off is in the conductor reference.

The prompt carries the goal, the scope, the plan path, the checkout, and the push target. It
tells a session that hands its PR over to send its packet through `approval-packet` and merge on
approval.
