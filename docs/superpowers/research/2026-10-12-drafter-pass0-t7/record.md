# T7 record: the YAML plan step on `rotate-the-github-app-key`

Run on 2026-10-12 against cairn-cms `origin/main` (`8ab896763`) in a scratch worktree, since
removed. Nothing in cairn-cms was committed.

## Plan step

The chain's YAML-mode `planPrompt` was rendered by the spike's `chainprompts.mjs` from the T6
chain, with `planFormat: "yaml"` and the page's inputs. One Agent dispatch ran it (Opus 5.5, high
effort). The page's committed `.plan.md` served as the prior plan, which exercised the rework
path, and the agent deleted it once the `.plan.yaml` was written.

The plan is `rotate-the-github-app-key.plan.yaml` in this directory (675 lines). The agent ran the
validator once and it passed. The session reran it:

```
drafter check-plan --facts docs/internal/facts --outline docs/internal/outlines/extend.json \
  docs/internal/briefs/extend/rotate-the-github-app-key.plan.yaml
0 errors, 0 warnings
exit 0
```

The built binary included T8, so the plan's format matches the final reference.

## Structural read

The plan-mode `structurePrompt` ran as one Opus 5.5 dispatch at medium effort. Verdict: **fix**,
six blocking findings and three non-blocking. The read confirmed the introduction, the order, the
module types, and the crossLink placement. The blocking findings, which the chain's replan round
would act on:

1. `s-push` can fail at the reader's terminal but has no `canFail` and no `failure` item (line 220).
2. `d-missing` and `d-unusable` end on "push again", and nothing sends the reader back to Verify (450).
3. The rollback is a dead end for a reader who rolled back successfully (506).
4. `x-publish` sends a reader to a check that needs a log record the reader has not reached, and the
   diagnostic list has no fall-through (368).
5. `s3-verify` can fail but has no `canFail` and no `failure` item (554).
6. The scaffold point appears three times, and the introduction front-loads step-level detail (51).

Non-blocking: `old-key-file` is an unconditional precondition though the plan treats it as optional
(88); "Delete the old key" has no hand-off (419); the See also opener claims more than the list
holds (579).

Findings 1 and 5 are the recovery gaps the recovery matrix exists to expose, and the structural
seat caught them because the plan carried addressable `step` and `failure` items. The plan step
did not run the replan round, which is the chain's job and outside T7.

## Plan-step findings for cairn

The plan step reported four `couldNotDo` items for the cairn docs sessions, all about page inputs
and the published page rather than the format: six facts filed after the page inputs were built,
a claim-inventory line that says 200 where the route answers 503 on failure, an inventory line
that says the page does not exist when it does, and the introduction's facts being cited only in
prose, which `--facts` cannot resolve. The last is a format limit: `introduction` takes prose
only.
