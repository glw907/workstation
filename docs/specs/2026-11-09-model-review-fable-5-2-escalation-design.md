# Move the Fable escalation to Fable 5.2

## Brief

Fable 5.2 shipped on 2026-11-09, and the `fable` alias now resolves to it. Claude Code runs it at
`medium` effort unless a dispatch names a level, so the last rung of the `pass-core` escalation
ladder would think less than the Opus `xhigh` rung before it. This design makes every `fable`
dispatch name `high`. It also proposes dropping the Opus `max` adjudication, since Anthropic reports
Fable 5.2 at `high` scoring level with Opus 5.5 at `max` for about half the cost per task. That second
change trades general usage for Fable allowance, so it's flagged for your ruling. Approving starts
one direct wording change, after Claude Code reaches 2.1.321.

## Gap

`pass-core` "Models" says an unsettled decision "re-runs at `xhigh`, then `max` (one session-only
adjudication), then one `fable` dispatch". The dispatch names no effort. It was written for Fable
5.1, whose Claude Code default was `high`.

The installed Claude Code is 2.1.319. Fable 5.2 needs 2.1.321, and the Homebrew
`claude-code@latest` cask still serves 2.1.319 (npm has 2.1.321). Until the cask catches up, a
`fable` dispatch still gets 5.1.

## Evidence

- Model configuration: "Fable 5.2, Opus 5.5, Sonnet 5.5, and Haiku 5.5 default to `medium`", and
  the `fable` alias "resolves to ... Fable 5.2 everywhere else". The same page says Fable 5.2
  "requires Claude Code v2.1.321 or later" (<https://code.claude.com/docs/en/model-config>).
- Effort page, on Fable 5.2: "Start with `high`. Most of the gain in capability is already present
  at `high`", and `max` is for "the rare task where time and tokens don't matter"
  (<https://platform.claude.com/docs/en/build-with-claude/effort>).
- Announcement: Fable 5.2 at High effort on FrontierCode 2.0 is about level with Opus 5.5 at Max,
  for roughly half the cost per task
  (<https://www.anthropic.com/claude-fable-and-mythos-5-2>).
- Fable on your plan: Max may spend up to half its weekly limit on Fable models, which "use them
  faster than other Claude models"
  (<https://support.claude.com/en/articles/15424964-claude-fable-models-on-your-plan>). Anthropic
  publishes no draw rate, so the cost comparison holds in API dollars and is unmeasured in plan
  usage.

The [subagent effort design](2026-11-01-model-review-subagent-effort-design.md) would set
`CLAUDE_CODE_SUBAGENT_EFFORT=medium`. A `fable` dispatch that names no effort would then run at
`medium` by that route too, so naming `high` is needed either way.

## Proposed change

1. Take Claude Code 2.1.321 or later through `standards:dependency-upgrade` once the cask serves
   it. Confirm `/model fable` reports Fable 5.2 in a fresh session.
2. In `pass-core` "Models", make the dispatch "one `fable` dispatch at `high`".
3. **For your ruling:** replace "then `max` (one session-only adjudication), then one `fable`
   dispatch" with "then one `fable` dispatch at `high`". My recommendation is yes. The `max` rung
   costs a full session of Opus at its slowest setting, and the evidence puts Fable `high` at the
   same quality for less. The risk is the 50% Fable cap, and escalations are rare enough that it
   shouldn't bind.
4. Update `claude-tooling.md:37`, which names Fable 5.1, to name the `fable` alias without a
   version.

`pass-core` sits under `claude/.claude/skills/`, which makes this `runner`. Steps 2 to 4 change
wording only, so they can land as a direct change after the gate (`dotfiles-pass` "Risk-class path
map").

## Audit findings taken

None. This came from checklist item 1 and the Fable 5.2 release.
