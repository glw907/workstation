# drafter pipeline spec: mechanics and feasibility review

Target: `docs/superpowers/specs/2026-10-12-drafter-pipeline-design.md` at `1e92788`. Reviewer: the
`plan-reviewer` agent, 2026-10-12. Saved verbatim by the dispatching session.

**Verdict.** The core approach holds up: batched seats, goja rendering, the edit contract, and caps.
Six parts of the spec don't work as written: the prompts-module contract, the handoff record, how
each seat's inputs are found, the gate integration, the stop rules, and the API key name. The spike
evidence also lives on tmpfs and will be lost at the next reboot.

**Claims confirmed against source or docs:** Batch API results stay available for 29 days and a
batch expires after 24 hours; Opus 5.5 batch pricing is $2/$10 per MTok, matching the spike's
`0.5*(4,20)` formula. Structured output and `output_config.effort` both work in batches; every spike
response parsed, all with `end_turn`. Token counting is free, an estimate, with rate limits separate
from message creation. `claude-haiku-5-5` supports effort, so the smoke target is sound.
`goja.txt` and `node.txt` are byte-identical (`cmp`). The chain had 28 commits since 2026-09-12
(`git log`). `cairn-run-gate` locks per lane.

## Findings, ranked by consequence

### 1. BLOCKER, correctness: the prompts-module contract can't work as written (spec:115-123)

- goja rejects `export`: a probe of `export function draftPrompt(c){...}` returned `SyntaxError:
  Unexpected reserved word`. The Workflow runtime needs `export const meta`, so the chain file can't
  "gain that export" in a form both runtimes load. The probe got around this with source surgery: it
  stripped `export const meta`, cut the file at the comment `// A small slot pool`, and wrapped the
  rest in an async function (gojaprobe/main.go).
- The builders aren't pure functions of a context object. They close over top-level state built
  from `args`: `WT`, `GATE`, `OUTLINE`, `INDEX`, `OPTION_MAP`, `common`, `REGISTER`
  (docs-page-chain.js:507-540).
- The top level calls `agent()`: `await resolvePages()` (704-723) whenever `args.outline` is set,
  the normal cairn case, and `await reworkProbe()` (732-756) for rework pages. The goja probe stubs
  `agent` to panic and only worked because its job.json had no outline and no rework.
- Dropping the outline changes the prompts: `structurePrompt` loses its cross-links check (1611),
  `readerPrompt` changes how it gets the job (1739), `indexLinkLine` goes empty (1022), and
  `docMapLine` changes (1183).
- Fold: define the contract as goja-loadable, a script whose completion value or a `drafter` global
  maps each seat to `fn(ctx)`, cut at an explicit marker such as `// === DRAFTER EXPORT ===`. For
  the beside-the-chain period, drafter evaluates the chain with injected `args` from the handoff and
  a host `agent` stub that answers only the outline and rework probes, from probe results the
  handoff carries. `check-prompts` must render with an outline set. The refactor to pure `ctx`
  functions happens at cutover, and the spec should say so.

### 2. MAJOR, correctness: the handoff leaves out what the builders read, and its transport is a model transcription (spec:128-131)

- Builders read `args.worktree`, `gate`, `gateLane`, `toolGate` (appended for `pinned` pages,
  895-898), `valeErrorRules` (538), `registerPath`, `optionMap`, `outline`, `bothReviewers`, and the
  resolved `INDEX`. The handoff lists only the page config, inputs, and plan and framing paths.
- "The planning session writes the records" means Claude retypes about 14 KB of JSON per page. The
  chain itself refuses to trust model transcription: its probes carry FNV checksums (612-646).
- The Workflow persists its return value verbatim as `result` in
  `~/.claude/projects/<proj>/<session>/workflows/wf_<id>.json` (observed in `wf_7ef2ce8f-59b.json`).
- Fold: the handoff carries `{args, resolved pages, index, per-page inputs, paths, checksum}`;
  drafter reads it from the `wf_*.json` (`drafter page --workflow-run <file>`) or at least verifies
  a chain-computed checksum; records live outside the worktree.

### 3. MAJOR, correctness: each seat's inputs are reverse-engineered from agentic prose (spec:82, 159-163, 286-287)

- The prompts tell seats to run `vale` (1521), `git hash-object` (1403-1406), `git cat-file blob
  <baseline> | diff` (1497-1503), read the option map live (1548), run `cairn-docs-outline link`
  (1024), run the gate (900-911), and read exemplars under `~/.local/share/cairn/exemplars/`,
  outside the repo, which "every repository file the prompt names" misses.
- The spike coped with a path regex restricted to `docs|scripts|src|examples|.vale`
  (batchchain.py:63), a hard-coded absolute-path regex (64), and a fake baseline `"0"*40` (307).
- `check-prompts` only renders, so a chain edit that adds "run X" silently degrades a seat.
- Fold: each seat declares its inputs (files and commands) in the module or in `drafter.toml`;
  `check-prompts` fails on any backticked command or repo or absolute path in a rendered prompt that
  no assembler covers.

### 4. MAJOR, correctness: the gate package mishandles `cairn-run-gate` (spec:88, 141-143, 154, 263-265)

- `cairn-run-gate` exits 75 ("gate still running") after `CAIRN_GATE_WAIT` (540 s) and on a vanish;
  the caller must re-issue until a `gate exit:` line appears (cairn-run-gate:5-9, 16-22, 49). The
  spike treated any nonzero exit as a red gate (batchchain.py:217, 232).
- The chain's gate rule says a red whole-tree component that names another in-flight page's file,
  or a rule a later task closes, "does not count against this page" (gateLine, 903-910). A
  multi-page run in one worktree would wrongly escalate.
- Fold: loop on 75 until `gate exit:`; parse `check(s) failed:` and the `== component ==` sections;
  discount a component whose failures name only another in-flight page's files; test both.

### 5. MAJOR, correctness: stop-rule gaps (spec:139-155, 165-172)

- (a) Stage 5 redrafts only "if any read returned fix", so coverage misses alone never trigger a
  redraft. (b) A coverage miss that survives the redraft has no outcome. (c) Stage 7 has no gate
  after the reader redraft; the chain escalates on a red gate there (finalRead, 1882-1884). (d)
  Stage 7 has no coverage re-check. (e) "Edits applied, then gate red" is undefined: in the spike
  the retry asked for "only the further edits", the next answer carried no resolutions, the
  resolution check refused it, and $0.58 was wasted (run-rotate-edit2.log 11:49:57-11:54:06).
- Fold: one stop table (trigger, retry budget, escalation reason per stage); coverage misses are
  blocking findings; gate and coverage after every redraft; after applied edits and a red gate,
  roll back and request a full answer, or use a separate gate-fix schema (edits only).

### 6. MAJOR, correctness: the cold read isn't cold (spec:162-163)

The spike put the job in the same user message as the page, inside a `<step3>` label
(batchchain.py:278-283). Fold: two turns, the page with steps 1-2, then the job as the next batch.
The reader's input is about 6.6k tokens (about $0.01); the cost is about 2 minutes of latency.

### 7. OWNER FORK, correctness: the task-guide final reader can't run steps

The chain's `readerPrompt` has a task guide's reader follow the steps in a scratch directory
(1729-1734); a batched reader can only infer. Options: (a) a read-only reader, with the pilot
recording each "inferred, not run" finding; (b) a `claude -p` reader on the key for task guides;
(c) task-guide final reads stay on the chain. Recommendation: (a), with (b) as the remedy if the
pilot's task guides show a gap.

### 8. MAJOR, correctness: the `ANTHROPIC_API_KEY` name collides (spec:238-241)

`~/.local/secrets` exports `ANTHROPIC_API_KEY` (name checked only), and it is in Claude Code's
environment. Per code.claude.com/docs/en/iam, "In non-interactive mode (`-p`), the key is always
used when present". If drafter's key replaces that variable, every `claude -p` bills drafter's
workspace; if not, drafter uses the general key and bypasses the backstop. Fold: a dedicated
`DRAFTER_API_KEY`, loaded by drafter from the age store; refuse to start on `ANTHROPIC_API_KEY`
alone; check the documented `anthropic-workspace-id` response header against config before the
first submission.

### 9. MAJOR, correctness: `check-plan` mixes a model call into a validator (spec:96, 205-209, 217, 293-294)

A batched consistency read inside `check-plan` makes the writer's loop nondeterministic, can exceed
a Workflow agent's 10-minute Bash timeout, needs the key in the plan agent's environment, and makes
the e2e tests spend money. `page --dry-run` also calls the token-counting endpoint. Fold:
`check-plan` stays deterministic and offline; the consistency read moves to drafter's stage 1 or
`check-plan --consistency` as one synchronous call; `--dry-run` gets an offline estimate mode.

### 10. MAJOR, correctness: YAML `#` truncates text silently (spec:186-191)

Probed with `gopkg.in/yaml.v3`: `claim: Push the new key first # then delete the old` decodes to
`"Push the new key first"` with no error (the comment lands in `LineComment`). `claim: Note: the old
key still works` fails. `claim: no` stays `"no"`. Fold: `check-plan` walks the `yaml.Node` tree and
rejects plain-style prose scalars with a `LineComment`, or requires `|` or quoted style there.

### 11. MAJOR, correctness: caps don't stop spend before it happens (spec:225-233)

Token counting covers input only; output was 6-60% of request cost in the spike (`draft1-0`:
31,972 output tokens, $0.32 of $0.53). Other pages' in-flight batches go uncounted. A resume
re-fetches results and double-counts. Opus 5.5 cache reads are 0.05x, not 0.1x. Batches "may go
slightly over your Workspace's configured spend limit". Fold: estimate = counted input +
`max_tokens` × output price; reserve in-flight estimates against every cap; key ledger lines by
`(batch_id, custom_id)` and dedupe; name `max_tokens` per seat.

### 12. MAJOR, correctness: batch result types aren't all handled (spec:267-270)

Missing: `expired` (24 hours, not billed), `canceled`, and `stop_reason: max_tokens`, which truncates
structured JSON. Fold: a table of result type and stop reason to action, with tests.

### 13. MAJOR, correctness: the spike evidence lives on tmpfs (spec:53-54, 293)

`/tmp` is tmpfs; the 13 MB spike directory disappears at reboot. Fold: copy it to
`~/Projects/drafter/testdata/` or `~/.local/share/drafter/spike/` and cite the path.

### 14. MINOR, correctness: no run reached "accepted"

All four spike `record.json` files say `escalate`, and the runs were stitched (draft1 supplied,
round-1 reads reused). Fold: say so, add a synthetic accept fixture, and require at least one
accepted page in pilot criterion 1.

### 15. MINOR, optional: prompt caching probably loses money (spec:243-246)

`cache_control` must sit on the request whose prefix is reused, which is sent before anyone knows a
continuation will happen. With a 1-hour cache on Opus 5.5 (2x write, 0.05x read), one continuation
costs 2.05x against 2x uncached; two cost 2.1x against 3x. Fold: leave caching out of the first
build and revisit with the pilot's retry frequency.

### 16. MINOR, correctness: the backstop open item resolves to a Console step (spec:321-322)

Workspace spend limits are set only in the Console; the Admin API covers create, list, archive, and
members. The limit is "monthly" and may not follow the billing cycle; record the mismatch.

### 17. MINOR, correctness: the `fact` item check needs a section mapping (spec:198)

The brief has no section field. Fold: locate the sentence in the page and take the nearest
preceding heading.

### 18. MINOR, correctness: the reader-state walk proves consistency, not completeness (spec:205-212)

A page with no deploy step passes unless a step declares `requires: deployed`. Fold: state the
limit and keep the plan-mode structural read as the completeness check.

### 19. MINOR, correctness: edit contract details (spec:165-172)

Sequential application and overlapping edits are undefined; "declined only when factually wrong"
can't be enforced mechanically; raw JSON spans broke the brief once (choose-c, 11:39:30). Fold:
define application order; pass decline reasons to the round-2 seat; optionally use structured brief
operations.

### 20. MINOR, correctness: rework and figure pages need a guard

Nothing refuses them. Fold: the chain errors on `backHalf: "drafter"` for a `rework` or `figure`
page.

### 21. MINOR, correctness: one executor per worktree

drafter writes into the planning session's worktree and may be queued for the night. Fold: refuse
to start on uncommitted changes drafter didn't make, or take a lease; name queueing as sub-project
2's job.

### 22. MINOR, correctness: smaller gaps

Run directories collide on a same-day rerun (add a run id). Friction entries have no stated home
(the record carries them; the planning session files them). The dotfiles `check-prompts` step needs
the binary installed and fixtures in `~/.dotfiles/tests/fixtures/`.

### 23. OWNER FORK, optional: the plan format ships in the same pilot as drafter

Options: (a) same pilot; (b) YAML plans first on the chain for one page. Recommendation: (a), with
each escalation record noting which plan check caught it.

### 24. Over-ceremony, all optional

(a) Fold the coverage read into the round-1 batch. (b) Stage 1 needn't rerun the consistency read
the plan step ran. (c) Defer the stock Google-register module to sub-project 4. (d) Use YAML for
config too, one parser. (e) The $40 per-run cap is redundant with the page cap and the ceiling.
