# Trial an Opus advisor on one Sonnet executor

## Brief

Claude Code's advisor tool lets a Sonnet session consult a stronger model at decision points, such
as before it commits to an approach or declares a task done. Anthropic featured it in the Fable 5.2
launch, and the workstation has never used it. This design runs it once: the next `ordinary` pass's
executing session launches with `--advisor opus`, and the pass's score records whether clock stops
and fix rounds fell enough to pay for the extra usage. Approving adds one flag to one launch. Nothing
in settings changes unless the verdict says to adopt it.

## Gap

`pass-core` "Models" puts the executing session on `sonnet` at `medium`, and moves the next pass to
`high` when a clock stop or CI red traces to executor reasoning. The only stronger model it reaches
mid-pass is a reviewer or an escalation dispatch, both after the fact. The advisor would check the
plan during execution, the point where `pass-core` says executor reasoning fails.

## Evidence

All from the advisor page (<https://code.claude.com/docs/en/advisor>):

- It "fits long, multi-step tasks where most turns are routine but plan quality determines the
  outcome", and "Claude calls the advisor at decision points rather than on every turn".
- A Sonnet 5.5 main model accepts "Fable, Opus 5 or later, Sonnet 5.5" as advisors.
- On subscription plans, "advisor usage counts toward your plan's usage limits".
- "The advisor model's own read of the conversation is not cached. Each advisor call processes the
  full transcript anew". A long executor session makes each call expensive.
- "Subagents inherit the configured advisor". A saved `advisorModel` would reach every pair
  subagent, so the trial uses the per-session flag.
- The feature is labeled experimental, and "behavior, pricing, and availability may change".

## Proposed change

1. Launch the next `ordinary` pass's executing session with `claude --bg --model sonnet --effort
   medium --advisor opus`, and say so in the pass plan's header.
2. At close, record in the pass's score the advisor calls the session shows, the clock stops and
   fix rounds, and the session's usage from `/usage`. Compare them with the last pass of similar size
   in the same repo.
3. Adopt, extend, or drop on that evidence. Adoption is a separate design, because a saved advisor
   reaches subagents.

Opus is the advisor and Fable isn't. An Opus advisor draws from the general pool, and a Fable one
would spend the capped Fable allowance on a trial. This changes no file, so it has no risk class.

## Audit findings taken

None. This came from the Claude Code docs read for the Fable 5.2 release.
