# Catch an unattended session that stops early

## Brief

Nothing on this workstation restarts an unattended session that ends its turn with work still owed.
Anthropic now names this failure and says `/goal` or a `Stop` hook is the fix. This design trials
`/goal` on the one session nobody watches, the monthly model review, and records the result that the
2026-09-28 sweep owed. Approving it starts one small `runner` pass.

## Gap

The sweep's item 9 said C2 would evaluate `/goal` against the `/loop` wake-up and record the result
in the guards doc. No such record exists: `unattended-work-guards.md` and the skills never mention
`/goal`, and the settings have no `Stop` hook. The `/loop` wake-up answers a different failure, a
session the link left unwoken. `model-review-notify` launches `claude -p` once, so a text-only end
of turn ends the run.

## Evidence

- Prompting Claude Opus 5.5: "An unattended agent loop that treats such a turn as the end of the
  task stops running there." It advises a checklist or a separate smaller model that checks the
  completion condition at each end of turn
  (<https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5-5>).
- Best practices: "for runs nobody's watching, `/goal` or a `Stop` hook enforces it"
  (<https://code.claude.com/docs/en/best-practices>).
- The `/goal` page: "Setting a goal with `-p` runs the loop to completion in a single invocation."
  The evaluator uses the small fast model, its cost is "typically negligible", and a condition can
  run to 4,000 characters (<https://code.claude.com/docs/en/goal>).

This workstation has no recorded early stop in a monthly run, and this is the first full one. The
evidence is Anthropic's guidance and the missing mechanism, not an incident.

## Proposed change

1. In `bin/.local/bin/model-review-notify`, launch the review as `/goal`, with a condition that
   names the end state: every step of `docs/model-review/prompt.txt` is done and the final message
   names the PR URL or says the run was a quiet month. The prompt stays a file and the session reads
   it. `--permission-mode auto` stays, which the page requires for unattended goal turns.
2. Add a short `/goal` section to `claude/.claude/docs/unattended-work-guards.md`: `/loop` wakes a
   session the link left idle, `/goal` continues one that stopped early, and the two are
   complementary.
3. Use `--dry-run` as the test. It must commit and stop, so its condition has to allow that end.

`pass-core` executors and conductors stay as they are for now. They already arm the `/loop` wake-up,
and they run under a conductor. If the December review shows `/goal` helped or changed nothing, that
review says whether to extend it.

This is `ordinary` by `dotfiles-pass` (`bin/.local/bin/model-review-notify` and a doc).

## Audit findings taken

None. This came from re-grading the sweep's cited pages.
