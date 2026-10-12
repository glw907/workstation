# drafter pipeline spec: fold record

Target: `docs/superpowers/specs/2026-10-12-drafter-pipeline-design.md`, revised in place from
commit 1e92788. Reviews folded: `2026-10-12-drafter-pipeline-review-mechanics.md` (M),
`-contract.md` (C), and `-integrity.md` (I). Each finding was verified against source, docs, or a
probe before it was acted on. Section names below are the revised spec's.

Totals: 75 dispositions. 61 folded, 11 refused, 3 owner forks. Mechanics finding 24 counts as five
(24a to 24e).

## Probes and sources the fold ran

- goja: `export function` and `export const` both fail with `SyntaxError: Unexpected reserved
  word`. A script's completion value returns an object whose functions goja calls. `typeof` of
  `require`, `fetch`, `process`, `console`, and `setTimeout` is `undefined`.
- The chain with the three `DRAFTER_HOST` edits, an outline set, and a resolved page: goja and Node
  rendered six prompts byte-identical (`cmp`). Probe at the session scratchpad `foldprobe/`.
- `gopkg.in/yaml.v3`: a `#` in a plain scalar truncates the value and lands in `LineComment`; a
  `|` block keeps it; `Note: ...` is a parse error; `no` decodes as `"no"`.
- `cairn-run-gate` header, lines 1-90: exit 75 re-issue, vanish, the terminal `vanished 3 times`,
  `RUN_GATE_IF_BUSY=defer` exit 76, lanes.
- `~/.local/secrets` exports `ANTHROPIC_API_KEY` (name only); `secrets/registry.md:330-336` lists
  its users.
- `anthropic-sdk-go` v1.80.0 `client.go`: `DefaultClientOptions` reads `ANTHROPIC_API_KEY`,
  `ANTHROPIC_AUTH_TOKEN`, profiles, federation, and `ANTHROPIC_BASE_URL`;
  `option.WithoutEnvironmentDefaults` skips all of them. `option.WithBaseURL`,
  `option.WithRequestTimeout`, and `option.WithResponseInto` exist (`go doc`).
- platform.claude.com, fetched 2026-10-12. Batch processing: the 24-hour expiry, 29-day results,
  workspace-scoped batches with a list endpoint, "batches may go slightly over your Workspace's
  configured spend limit", and `errored`, `canceled`, and `expired` unbilled. Rate limits: the
  monthly calendar cap, the 429 `enforced_spend_limit_reached` with no `retry-after`, and the 400
  workspace-limit message. Workspaces: spend limits set only in the Console, monthly, and the
  `anthropic-workspace-id` response header. Pricing: Opus 5.5 at $4 and $20 base, batch $2 and
  $10, one-hour write 2x, cache read 0.05x; Haiku 5.5 tiered above 100,000 tokens.
- A workflow run file (`wf_7ef2ce8f-59b.json`) holds `args` and the chain's return object in
  `result`.
- The spike's `run-rotate-edit2.log` and `batchchain.py:381-431` confirm the spurious refusal; all
  four `record.json` files end `escalate`. Spike output tokens: drafting seats up to 43,995, reads
  up to 11,648.
- cairn's facts: 1,550 Source lines, about 1,030 with a line range and 620 with a declaration.
- No saved gate log has a failing `check:provenance` section. A docs-gate log failing on tellgrader
  was copied to `~/.local/share/drafter/spike/gate-logs/`.

## Mechanics review

| # | Finding | Disposition |
|---|---|---|
| M1 | Prompts-module contract can't work in goja | Folded: "Beside the chain" (`DRAFTER_HOST` short-circuit, `DRAFTER_SEATS`, early return; no marker or cut) and "At cutover" (completion-value script). Probed. |
| M2 | Handoff incomplete; transcription transport | Folded: "The handoff" (args, resolved pages and index, worktree; read from the workflow run file). The checksum sub-part refused: no model retypes the handoff, so there is nothing to check. |
| M3 | Seat inputs reverse-engineered from prose | Folded: "Input assembly" (declared files and commands, `git ls-files`, real `git hash-object` baseline). The rendered-prompt command scanner refused as new machinery with no measured defect; the no-tools note already turns an unsupplied step into a recorded finding. |
| M4 | Gate wrapper and in-flight attribution | Folded at root I6 and I15: "Shared worktree", "The gate wrapper". |
| M5 | Stop-rule gaps | Folded: "Stop rules" table; coverage misses trigger stage 5; gate and coverage after every redraft; the edit contract's accumulated resolutions. |
| M6 | Cold read isn't cold | Folded: two-turn final reader in "Input assembly". |
| M7 | Task-guide reader can't run steps | Owner fork: ruling 2. |
| M8 | `ANTHROPIC_API_KEY` collides | Folded at root I1. |
| M9 | Model call inside `check-plan` | Folded at root C15; the dry-run part at root C16. |
| M10 | YAML `#` truncates silently | Folded: "The plan format" (line-comment rejection). Probed. |
| M11 | Caps don't bound spend | Folded at root I2 (reservation of input plus `max_tokens`). Its cache-read price correction (0.05x, verified) also carries the "Caching" revision: at verified prices continuation caching loses money. |
| M12 | Batch result types unhandled | Folded at root I7. |
| M13 | Spike evidence on tmpfs | Folded: evidence at `~/.local/share/drafter/spike/`, cited in "The spike". |
| M14 | No run reached accepted | Folded: stated in "The spike"; synthetic accept row in "Testing". The pilot floor is ruling 1. |
| M15 | Prompt caching loses money (optional) | Refused as optional; the same change lands through M11. |
| M16 | Backstop resolves to a Console step | Folded: open item closed in "A server-side backstop"; the month mismatch feeds ruling 3. |
| M17 | `fact` item needs a section mapping | Folded at root C20. |
| M18 | Reader-state walk proves consistency only | Folded: limit stated in "The plan format". |
| M19 | Edit-contract details | Folded at root C8. The structured-brief-operations sub-part is optional and dropped. |
| M20 | Rework and figure guard | Folded: the chain refuses them at start, drafter refuses them on decode ("The handoff", "Scope"). |
| M21 | One executor per worktree | Folded at root I5. |
| M22 | Smaller gaps | Folded: run IDs at root I12, friction at root I13, the check-prompts binary and fixtures at root C17. |
| M23 | Plan format in the same pilot (optional fork) | Refused as optional; the spec keeps one pilot. |
| M24a | Fold coverage into round 1 (optional) | Refused as optional. |
| M24b | Stage 1 needn't rerun consistency (optional) | Refused as optional; the double run is removed at root C15. |
| M24c | Defer the stock module (optional) | Refused as optional. |
| M24d | YAML for config (optional) | Refused as optional. |
| M24e | The $40 run cap is redundant | Folded: "Caps". Geoff allowed dropping it if redundant; the ceiling bounds total spend and the page cap a runaway page. Dropping it also removes the run-cap parts of C19 and I2. |

## Contract review

| # | Finding | Disposition |
|---|---|---|
| C1 | Cutover passes with zero accepted pages | Owner fork: ruling 1. |
| C2 | Criterion 2 can't be decided from the record | Folded: `faults` and escalation findings in "Records"; criterion 2 in "The pilot". |
| C3 | Criterion 3 rewards early escalation | Folded: criterion 3 in "The pilot"; the `cap` row in "Testing". |
| C4 | Criterion 4 has no procedure | Folded: criterion 4 in "The pilot" (Console cost for the workspace over UTC dates; no Admin key exists in the stores, so the Console is the source); ledger idempotence at root I2; key tests at root I1. |
| C5 | Estimate counts input only | Folded at root I2. |
| C6 | Coverage miss doesn't trigger redraft | Folded at root M5. |
| C7 | Coverage quotes never checked | Folded: "Coverage"; coverage rows in "Testing". |
| C8 | Edit-contract rules incomplete | Folded: "The edit contract"; one test row per rule plus the spike's attempt-1 answer. |
| C9 | Resume and ledger untested | Folded: resume rows in "Testing"; hashes in "Resume". |
| C10 | Result types and unreadable reads | Folded at root I7; "never counts as accept" in "The pipeline". |
| C11 | Source-pointer forms | Folded: "Input assembly" source excerpts; rows in "Testing". |
| C12 | Plan-check tests negative only | Folded: clean twins and the added rows in "Testing"; slug rule named. |
| C13 | Fixtures in a throwaway scratchpad | Folded: "The spike" (durable location, copy to `testdata/`, fail on missing, provenance log regenerated in the build). |
| C14 | Handoff has no schema or test | Folded: versioned strict decode, the `handoffFor` node test, figure and rework refusal. The published handoff JSON Schema refused: the strict Go decode against the shared fixture does the same job at less cost. |
| C15 | Consistency read in the writer's loop | Folded: `check-plan` offline; the read runs once in stage 1 with a defined JSON output. The smoke check on the choose plan refused: it costs a real Opus call per release; the pilot records which check caught each cause instead. |
| C16 | Dry-run test needs the live endpoint | Folded: `httptest` through `option.WithBaseURL` in "Testing". |
| C17 | `check-prompts` proves only no-throw | Folded: "Checking the prompts" (matrix, content assertions, Node comparison, gate fails on a missing binary). |
| C18 | Shared-worktree leftovers | Folded at root I6: "Shared worktree". |
| C19 | Reset clock and cap effects | Folded: UTC reset and month-end clamp in "Caps"; resumable stop on the ceiling. The run cap is gone (M24e). |
| C20 | Section mapping for `fact` items | Folded: plan sections name their heading; "Coverage" normalization. |
| C21 | Prices unsourced | Folded: dated price table in "The ledger"; cost rows in "Testing". |
| C22 | Pruning loses pilot evidence | Folded: "Records" (drafter prunes nothing). |
| C23 | Markdown fallback disables checks | Folded: YAML required for pilot pages; `plan_format` recorded. |
| C24 | Cairn-specific extraction and silent drops | Folded: log patterns and lane in `drafter.toml`, `gate_log: unparsed`, `not inlined` blocks, `git ls-files` path detection. |
| C25 | Cold read untested | Folded: reader isolation row in "Testing". |
| C26 | Blind grader has no bar (optional fork) | Refused as optional; the grader stays a second opinion. |
| C27 | Caching break-even (optional) | Refused as optional; the same change lands through M11. |
| C28 | Rework pages unaddressed (offered as a fork) | Folded, not a fork: rework is out of scope ("Scope"). The spike never ran a rework page and no pilot criterion covers one, so exclusion is the only answer the evidence supports. |
| C29 | Smoke has no assertion | Folded: `make smoke` in "Testing". |

## Integrity review

| # | Finding | Disposition |
|---|---|---|
| I1 | Key name collides | Folded: `DRAFTER_API_KEY`, `WithoutEnvironmentDefaults`, refusal, workspace-header check ("A server-side backstop"); tests in "Testing". |
| I2 | Caps bypassable | Folded: reserve and settle lines under `flock`, worst-case estimate, spend derived by run ID ("Caps", "The ledger"). |
| I3 | Orphaned batch after `create` | Folded: intent before `create`, list-and-adopt on resume ("Resume"). |
| I4 | Resume can corrupt page and brief | Folded: pre- and post-write hashes, atomic writes, round-1 snapshot file ("Resume", "Input assembly"). |
| I5 | No one-executor enforcement | Folded: "One run per worktree". |
| I6 | Sibling pages poison the gate | Folded: "Shared worktree". |
| I7 | Errors misclassified | Folded: "Failures" table. |
| I8 | Backstop counts calendar months | Owner fork: ruling 3. Option (c) is impossible: the docs set workspace spend limits only in the Console. |
| I9 | Output uncommitted (offered as a fork) | Folded, not a fork: drafter never commits ("Outcome"); final page and brief kept in the record; drafter deletes only files it created. The workstation rule "Two sessions never both close, merge, or release one branch" and one-executor-per-worktree settle it. |
| I10 | Inputs change mid-run | Folded: "Run inputs". |
| I11 | Cost drifts from the Console | Folded at root C21. |
| I12 | Run identity undefined | Folded: run IDs and exclusive directories in "Records". |
| I13 | Friction dropped | Folded: `friction` in "Records". |
| I14 | Handoffs in the worktree | Folded: the handoff is read from the workflow run file and never lands in the tree. |
| I15 | Gate protocol and suspend | Folded: "The gate wrapper"; per-request timeout in "Failures". |
| I16 | Inline any named file (optional) | Refused as optional; `git ls-files` detection lands through C24. |
| I17 | Pruning deletion path (optional) | Refused as optional; pruning is removed through C22. |
| I18 | Token count per request (optional) | Refused as optional; the counting endpoint stays for the input half of the reservation. |

## Owner forks

Consolidated as the spec's "Owner rulings": 1 (C1, with M14's pilot half), 2 (M7), and 3 (I8,
with M16's verified Console-only limit).
