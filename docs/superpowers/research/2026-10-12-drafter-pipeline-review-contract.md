Contract-and-criteria review of `docs/superpowers/specs/2026-10-12-drafter-pipeline-design.md`, commit 1e92788 (`drafter-pipeline-spec`).

Counts: 1 blocker, 17 major, 11 minor. Three findings carry an OWNER FORK (1, 26, 28).

Checked from source, not from memory:

- The spike harness `spike/batchchain.py:60-135` (input assembly), `:157-187` (request, batch, cost), `:214-232` (gate-log extraction), `:381-431` (edit contract), and `:442-525` (stop rules).
- Every `spike/run-*/record.json` and `*.response.json` usage block, plus `spike/run-rotate-edit2.log`.
- `spike/response1.json`, the one-hour cache write.
- `scratchpad/gojaprobe/main.go`, and `node.txt` against `goja.txt` (`cmp`: identical, one prompt of 14,920 bytes).
- `~/.claude/workflows/docs-page-chain.js:1778-1781`, `:1866-1897`, `:1967-2031`.
- cairn's `docs/internal/facts/*.md` Source pointers and status tags, counted by script.
- `~/.claude/skills/go-conventions/SKILL.md:233-273`.
- `claude/.claude/docs/fable-post-cutoff-system.md:97-104` (pricing).
- `scripts/check.sh`. The dotfiles repo has no `.github/workflows`, so its gate is local only.
- The surviving gate logs under `/tmp/cairn-gate-1000/`.

Spike's directory below means `/tmp/claude-1000/-var-home-glw907--dotfiles/b6b1bee0-93e5-49ed-9a9e-00f74b3bd0e8/scratchpad/spike/`.

## 1. Blocker: every cutover criterion passes with zero accepted pages

- **Tag:** correctness
- **Location:** `docs/superpowers/specs/2026-10-12-drafter-pipeline-design.md:299-312`
- **Defect:** Criterion 1 reads "Geoff accepts every page drafter accepted". With zero accepted pages it holds vacuously. Criterion 2 holds if every escalation names an input cause. Criterion 3 gets easier as pages escalate early, because escalated pages are cheap (finding 3). Criterion 4 doesn't depend on outcomes at all. So a pipeline that escalates all five pilot pages meets cutover. This is the likely case, not a corner case. All four recorded spike runs escalated: `run-rotate-the-github-app-key/record.json` ("second fix verdict"), `-edit` (same), `-edit2` ("a scoped read returned fix after the reader redraft"), and `run-choose-an-ai-posture-c` ("second fix verdict"). The spec reports that the October 7 chain escalated 5 of 5 (`:47-48`). Neither path has yet shown a page reaching `accepted`, and nothing in the pilot asks for one. The stated bar, "current quality is the base standard" (`:16-17`), has no throughput half.
- **OWNER FORK:** this is a priority choice about what cutover must show.
  - (a) A floor on acceptances: at least 3 of the 5 or more pilot pages reach `accepted`.
  - (b) Parity with the chain: drafter's accept rate on the pilot is no lower than the chain's on the same pass's pages. Today that rate is 0/5, so this is vacuous too.
  - (c) An acceptance floor plus a pipeline-fault ceiling: at least 1 page per page type reaches `accepted`, and zero pipeline faults.
  - Recommendation: (a). It is the only option that can fail on the evidence above, and it still lets input-caused escalations count as correct behavior under criterion 2.

## 2. Major: criterion 2 can't be decided from the record the spec defines

- **Tag:** correctness
- **Location:** `docs/superpowers/specs/2026-10-12-drafter-pipeline-design.md:304-305,250-253`
- **Defect:** The record holds "stages, verdicts, findings, resolutions, cost, final status". Its `reason` names the stop rule that fired, never an input cause. The spike's records say "second fix verdict" or "a scoped read returned fix after the reader redraft". Nothing names a plan gap, fact conflict, or missing fact, and the spec names nobody who classifies. "A pipeline fault, such as a dropped finding or a broken edit" is also judged by eye. Yet the spike log shows a fault the pipeline caused itself (finding 8), on a run that then counted as an input-caused escalation. As written, the criterion is graded by whoever reads the findings, with no rule.
- **Fold:**
  - drafter computes `record.faults[]` mechanically on every page. It records a blocking finding with no resolution in the final contract state, an edit refused for a reason the answer didn't cause (finding 8), a read that returned nothing or didn't parse (finding 10), and a coverage quote that isn't on the page (finding 7).
  - An escalated record carries `escalation.findings`, the seat and finding numbers that triggered the stop.
  - Criterion 2 becomes two checks. Every escalated record has an empty `faults`. The planning session writes one cause per escalation into the pass record, citing those finding numbers, and Geoff confirms it in the PR.

## 3. Major: criterion 3 rewards early escalation, and "reaches the $10 cap" has no defined event

- **Tag:** correctness
- **Location:** `docs/superpowers/specs/2026-10-12-drafter-pipeline-design.md:306,225-228`
- **Defect:**
  - The average runs over all pilot pages. A page that escalates at the plan check or after round 1 costs about $1 to $2 (`run-rotate-the-github-app-key-edit/record.json` $1.04, `run-rotate-the-github-app-key/record.json` $1.89), which pulls the mean under $5 regardless of what accepted pages cost.
  - The caps refuse a stage before spending (`:227`), so a page never "reaches" $10 in the ledger. It stops short of it, so "no page reaches the $10 cap" can't fail. Finding 5 shows the estimate can't actually bound the spend either.
- **Fold:** Criterion 3 becomes two checks. Accepted pages average $5 or less in actual ledger cost. No page's record has `reason: cap`, and no page's ledger total exceeds $10. Add one row to the caps test: a stage refused because its estimate would cross the page cap writes `reason: cap`.

## 4. Major: criterion 4 names no reconciliation procedure, and "none of its spend reaches the plan" can't be observed

- **Tag:** correctness
- **Location:** `docs/superpowers/specs/2026-10-12-drafter-pipeline-design.md:307-308,230-241,321-322`
- **Defect:**
  - "Matches the Console's credit usage within 5%" doesn't name the Console figure (a workspace cost report, or the organization's credit balance), the window (the billing cycle or the pilot's dates, in UTC or local time), or how other spend in the workspace is excluded. That other spend includes `make smoke`, check-plan's consistency reads (finding 15), and retried requests.
  - The ledger can drift from the Console. A crash after a batch ends but before its results are appended loses the cost. A `--resume` that re-fetches results can append them twice. Neither case is tested (finding 9).
  - "None of its spend reaches the plan" has no observable. Geoff's Max usage moves with his own interactive sessions, so a subscription meter can't isolate drafter.
- **Fold:**
  - Name the procedure: the Admin API cost report for drafter's workspace over the pilot's UTC dates, compared with `drafter spend` filtered to the same dates.
  - Make the ledger idempotent by batch and custom ID. Have each run reconcile any ended batch it has not ledgered.
  - Restate the plan half as a code-level promise with a test: drafter exits non-zero when `ANTHROPIC_API_KEY` is unset, and never reads `CLAUDE_CODE_OAUTH_TOKEN` or `ANTHROPIC_AUTH_TOKEN`. The test runs with only an OAuth variable set and asserts the refusal.

## 5. Major: the cap estimate counts input only, while output is most of a drafting call's cost

- **Tag:** correctness
- **Location:** `docs/superpowers/specs/2026-10-12-drafter-pipeline-design.md:226-228,289`
- **Defect:** The token-counting endpoint counts input tokens, so "a cap stops a stage before the spend" holds only for input. On the spike's own drafts, output costs more than input. `run-choose-an-ai-posture/draft1-0.response.json` used 106,589 input and 31,972 output tokens: $0.21 of input and $0.32 of output at the batch rate of $2 in and $10 out. `spike/response1.json` used 43,995 output tokens, 31,267 of them thinking. The spike requests `max_tokens: 64000` (`batchchain.py:157`), so one Opus request can add up to $0.64 the estimate never saw. A stage of three reads can add up to $1.92. The caps test, "a stage refused at each cap", passes with an input-only estimate.
- **Fold:** Define the estimate as counted input plus each request's `max_tokens` at the output rate, as a worst case, or plus a per-seat output allowance taken from the ledger's p95. Name which one. Add a test row whose input alone fits under the page cap but whose input plus output allowance doesn't. It must be refused.

## 6. Major: a coverage miss doesn't trigger the redraft, and the post-redraft coverage outcome is undefined

- **Tag:** correctness
- **Location:** `docs/superpowers/specs/2026-10-12-drafter-pipeline-design.md:144-153`
- **Defect:**
  - Stage 3 puts missing items into "round 1's findings". Stage 5 redrafts only "if any read returned fix". If all three round-1 seats accept, a missing `claim` or `handoff` item never reaches a redraft, and the page goes to the final reader. The chain's own gate is `!r1.anyFix && d1.gate === "pass"` (`docs-page-chain.js:2006`), which has no coverage term to inherit.
  - Stage 5 runs "the coverage check again" but doesn't say what a miss then does: escalate, join round 2, or nothing.
  - Stage 7's reader redraft reruns no coverage check. Yet it is a redraft, and the spec cites redraft compression as the cause of three of five October 7 escalations (`:214-215`).
  - The state-machine test (`:290-291`) can't cover transitions the spec never names.
- **Fold:** A coverage miss is a blocking finding from a `coverage` seat with verdict `fix`, so it alone triggers stage 5. A miss after the redraft counts as a second fix verdict and escalates. Stage 7 runs the coverage check after its redraft, with the same rule. Add those three transitions to the state-machine test table by name.

## 7. Major: the coverage read's quotes are never checked against the page, so a claim item can pass vacuously

- **Tag:** correctness
- **Location:** `docs/superpowers/specs/2026-10-12-drafter-pipeline-design.md:144-146,199-201,275`
- **Defect:** The coverage read "quotes the sentence that satisfies each `claim`, `handoff`, and `reason` item". It runs at low effort, and the open item weighs moving it to Haiku (`:323`). The spec doesn't require the quote to exist on the page, or in the item's section. A model that paraphrases or invents a satisfying sentence marks the item covered. This is the check aimed at the October 7 compression failures. No test in `:280-295` covers the coverage check at all, mechanical or read.
- **Fold:**
  - drafter verifies each quote as an exact substring of the page, after a named normalization (whitespace, and Markdown emphasis and code delimiters), inside the section the plan item names. A quote that fails is `missing`, and the event lands in `record.faults`.
  - Add a coverage test block. Use a verbatim item present and absent. Use a fact item cited in the right section and in the wrong one. Use a link in and out of its section. Use a recorded coverage response whose quote isn't on the page, which must come back as missing.

## 8. Major: the edit contract's refusal rules are incomplete, one is unenforceable, and the spike shows a spurious refusal

- **Tag:** correctness
- **Location:** `docs/superpowers/specs/2026-10-12-drafter-pipeline-design.md:165-172,282-283`
- **Defect:**
  - **Spurious refusal on retry.** In `run-rotate-edit2.log`, attempt 0 applied 21 edits and failed the gate. Attempt 1 was then refused ("blocking finding 1 ... has no resolution with an edit"). The continuation asks for "only the further edits" (`batchchain.py:428`), but `apply_edits` checks every blocking finding against that partial answer alone (`:391-395`). The retry cost $0.51 and used the second of three attempts. The spec doesn't say whether resolutions accumulate across attempts, or whether a gate failure after applied edits uses the same two retries (the spike's loop shares them, `:413-431`).
  - **Unenforceable rule.** "A blocking finding may be declined only when it is factually wrong about the page" is not a check drafter can run, and it isn't in the refusal list. The spike accepts any declined blocking finding (`:394`). The round-2 re-read gets only its own round-1 read (`batchchain.py:304-306`), not the decline reason, so nobody judges the decline.
  - **Missing rules.** The spec has no rule for:
    - an `edits` index that a resolution references but doesn't exist
    - an edit no resolution claims, which violates "changed nothing else"
    - a no-op edit (`old == new`) claimed as `edited`
    - duplicate resolutions for one finding (the spike's dict keeps the last)
    - a resolution for a finding number that doesn't exist
    - a missing resolution for an advisory finding (the spike accepts it)
    - a `file` other than `page` or `brief` (the spike raises `KeyError`)
  - **Ambiguous uniqueness.** "Occurs exactly once" is measured against the progressively edited text in the spike (`:385-390`). The spec doesn't say which text, so overlapping edits are undefined.
  - **No terminal state.** The spec doesn't say what happens after the second retry.
- **Fold:**
  - Restate the contract.
    - Resolutions accumulate across attempts. A retry answer adds to or overrides earlier ones, and drafter checks the union.
    - A gate failure after applied edits uses the same two-retry budget. A third failure escalates with `reason: contract`.
    - Uniqueness is measured against the text after the earlier edits in the same answer.
    - Every edit index referenced must exist. Every edit must be claimed by at least one resolution. `old` must differ from `new`. One resolution per finding number, and each number must exist. Every finding, blocking or advisory, needs a resolution.
    - A declined blocking finding is passed, with its reason, to that seat's next read, which must accept or re-raise it.
  - Add one test row per rule, plus the spike's attempt-1 answer (`run-rotate-the-github-app-key-edit2/reader-redraft-1.answer.json`) as a fixture that must now be accepted.

## 9. Major: resume and ledger idempotence carry promises with no test

- **Tag:** correctness
- **Location:** `docs/superpowers/specs/2026-10-12-drafter-pipeline-design.md:255-259,230-234,280-295`
- **Defect:** "`--resume` reattaches to an in-flight batch instead of paying for it twice" is the spec's main protection against double spend. The Testing section has no row for it. Several cases are unspecified and untested:
  - a resume whose batch ended while drafter was down
  - a resume whose worktree changed since the stop (the page edited by hand)
  - a resume after the Batch API's 29-day result expiry
  - whether a resumed run's per-page and per-run caps carry the earlier spend
  - whether the ledger lines from before the crash are appended again
- **Fold:**
  - Add a resume block to the state-machine test, using the fake batch client. Stop after submit and resume to an in-flight batch: no second `Create` call. Stop after the batch ended but before ledgering: exactly one ledger line per custom ID. Resume with prior page spend: the page cap counts it. Resume onto a page file whose hash differs from the stored state: escalate with `reason: worktree changed`.
  - State in the Resume section that state records the page file's hash.

## 10. Major: batch result types other than success, and a truncated or unparseable read, have no rule, so a silent accept is possible

- **Tag:** correctness
- **Location:** `docs/superpowers/specs/2026-10-12-drafter-pipeline-design.md:267-270,290-291`
- **Defect:**
  - The spec names "a server-side request error" and "an invalid request or a model refusal". The Batch API also returns `canceled` and `expired` (a batch not done in 24 hours, which is plausible for a nightly queue in sub-project 2).
  - A `succeeded` message can still be unusable. It can stop at `max_tokens` with truncated JSON, lack the page or brief blocks (`batchchain.py:204-206` exits), or fail its schema.
  - The chain escalates whenever a read "returned nothing" (`docs-page-chain.js:2004-2005`, and the comment "A read that returned nothing is never a silent accept"). The spec carries no equivalent rule, so a Go implementation that treats an unparsed verdict as a missing `fix` passes every listed test.
- **Fold:** Add a Failures rule with one entry per case:
  - `errored` with a server error: retry once.
  - `errored` with an invalid request: escalate.
  - `canceled`: escalate.
  - `expired`: resubmit once.
  - `stop_reason` of `max_tokens`, or a parse or schema failure: escalate with `reason: unreadable <seat>`.
  - A missing or unreadable read never counts as `accept`.

  Each entry gets a row in the state-machine test, with a recorded or hand-built response fixture.

## 11. Major: source excerpts cover only two of the Source-pointer forms cairn's facts use, and the declaration form is resolved by text match

- **Tag:** correctness
- **Location:** `docs/superpowers/specs/2026-10-12-drafter-pipeline-design.md:159-161,176-178,286-287`
- **Defect:**
  - A count of cairn's `docs/internal/facts/*.md` Source pointers gives 849 `path:line`, 460 `path#decl`, 137 bare file paths, 14 directories, 66 prose sources with no path ("SvelteKit routing precedence", `[external: SvelteKit]`), and 24 others. About 15% fit neither tested form.
  - The spike silently emits no excerpt for a bare file or directory (`batchchain.py:108-120`: no spans). Under the agentic exception (`:176-178`), the fact read can't check those facts and escalates.
  - For `path#decl`, the spike takes the first two lines that mention the name anywhere (`:113-115`). That is often an import or a call site, not the declaration.
  - The input-assembly test row names only the two forms, so none of this fails a test.
- **Fold:**
  - Specify the rule for each form. A bare file is inlined whole up to a size limit, then reported as uninlined. A directory or prose source yields an explicit "no excerpt: <form>" block the seat sees.
  - For `#decl`, locate a Go or TypeScript declaration by a declaration pattern, not by any mention.
  - Add test rows: a bare file, a directory, a prose source, and a `#decl` fixture whose name is imported above its declaration. The excerpt must contain the declaration line.

## 12. Major: the plan-check and edit-contract tests are negative rows only, so a check that errors on everything passes

- **Tag:** correctness
- **Location:** `docs/superpowers/specs/2026-10-12-drafter-pipeline-design.md:205-209,282-285`
- **Defect:**
  - Each plan-check row is a failing fixture: an unmet `requires`, a missing handler, a missing anchor, a `[rejected]` fact. A `check-plan` that reports an error for every plan passes all four rows. go-conventions asks what would have to be wrong for a test to fail (`SKILL.md:235-238`).
  - "An unmet `requires`" doesn't separate the specified "produced by an *earlier* step" walk from a set-membership check. A step whose `requires` is produced only by a later step passes the weaker check.
  - "Every placed fact is citable" is tested only against `[rejected]`. cairn's facts also carry `[candidate]` (5) and `[external: …]` tags, and a placed id can be absent from the facts files entirely.
  - The link test has a missing anchor but no missing target file, and doesn't name the slug rule an anchor is matched by.
- **Fold:**
  - Each negative row asserts the exact error code and `file:line`, and pairs with a clean twin that must pass.
  - Add rows for: a `requires` produced only by a later step (must fail), a `requires` satisfied by a listed precondition (must pass), a placed id absent from the facts files, a `[candidate]` fact (state whether it is citable), and a link to a missing file.
  - Name the anchor slug algorithm as the one cairn's site renderer uses.

## 13. Major: the test fixtures live in a throwaway scratchpad, and the provenance gate log was never captured

- **Tag:** correctness
- **Location:** `docs/superpowers/specs/2026-10-12-drafter-pipeline-design.md:53-54,288,293`
- **Defect:**
  - The spec makes "the spike's recorded requests and responses" the parsing fixtures and "a real log, including the spike's provenance case" the gate-extraction fixture. The spike directory lives under the session's `/tmp` scratchpad and is throwaway by the spec's own account.
  - No gate log is saved there. `batchchain.py:222` reads the log in place under `/tmp/cairn-gate-1000/<hash>/gate.log`, and those logs are unnamed and get swept.
  - The provenance case survives only as prose in `spike/oneshot1.friction:3`.
  - go-conventions allows "missing-fixture guards" as conditional skips (`SKILL.md:263-264`). A parsing test written with such a guard turns green with zero coverage once the scratchpad is gone.
- **Fold:**
  - Before the plan is written, copy the named files into a durable place, `~/Projects/drafter/testdata/spike/` or a research folder in this repo, and list them in the spec: the four `run-*` directories' responses and answers, `response1.json`, and one gate log with a failing `check:provenance` section. The log must be found now or regenerated by a deliberate provenance failure.
  - Tests fail, never skip, when a fixture is missing.

## 14. Major: the handoff record has no schema, no fixture, and no test on either side

- **Tag:** correctness
- **Location:** `docs/superpowers/specs/2026-10-12-drafter-pipeline-design.md:126-133,293-294,68-69`
- **Defect:**
  - The handoff is the one interface between the chain and drafter. It is "the page config, the page inputs with the plan's and the framing's dispositions applied, and the plan and framing paths", with no field list and no version.
  - The chain gains `backHalf` in this repo, which has a local gate with node tests for the chain (`scripts/check.sh:60`), but the spec adds no test of the handoff output.
  - `page --dry-run` "on fixtures" needs a handoff fixture that only the not-yet-built chain change can produce.
  - The scope excludes figure pages (`:68`), but nothing makes `drafter page` refuse a handoff with `figure: true`, so a figure page silently loses its figure-verifier seat (`docs-page-chain.js:1778-1781`).
  - The chain's `rework` mode (`:1970-1977`) isn't mentioned at all (finding 28).
- **Fold:**
  - Publish a handoff JSON Schema beside the plan schema, versioned.
  - Add a chain-side node test that runs the handoff derivation on a recorded page and validates the schema.
  - Make `drafter page` refuse a handoff with `figure: true`, or with `rework` until finding 28 is ruled, with a test row each.
  - The dry-run end-to-end test uses a handoff produced by that chain test.

## 15. Major: check-plan's batched consistency read in the writer's loop is costly ceremony and has no contract

- **Tag:** correctness
- **Location:** `docs/superpowers/specs/2026-10-12-drafter-pipeline-design.md:189-191,205-209,139-140,293-294`
- **Defect:**
  - The plan step "ends by running `drafter check-plan` until it reports no errors", and check-plan includes "a batched consistency read". Each loop turn then waits for a batch, two to six minutes per the spike (`:43-44`; `run-rotate-edit2.log` shows 2 to 5 minutes per batch), and spends credits.
  - The read is non-deterministic, so "until no errors" may not converge.
  - Stage 1 runs it again on every page, paying twice.
  - Its output contract (verdict schema, and whether a finding blocks drafting or only warns) is unspecified.
  - No test row covers it.
  - The end-to-end test "runs `check-plan` … on fixtures" inside `make check`, which then either spends money or needs the network.
  - The claim that it "would have caught" both exemplar escalations (`:213-214`) is not tied to a fixture.
- **Fold:**
  - `check-plan` runs the three mechanical tests only, offline and fast, and the writer's loop uses that.
  - `check-plan --consistency`, or pipeline stage 1 alone, runs the read once per plan. A finding escalates before drafting.
  - Define its JSON output.
  - Add a smoke-level check: the read on the spike's `choose-an-ai-posture` plan flags the two recorded fact conflicts. That turns the "would have caught" claim into evidence.

## 16. Major: the `page --dry-run` end-to-end test needs the live token-counting endpoint

- **Tag:** correctness
- **Location:** `docs/superpowers/specs/2026-10-12-drafter-pipeline-design.md:94,227-228,293-294`
- **Defect:** `--dry-run` prints "estimated cost", and estimates come from the token-counting endpoint. The end-to-end test runs `page --dry-run` in `make check`, so it needs a key and the network, or it guards on their absence and skips. The skip is the vacuous case go-conventions forbids for fallible calls (`SKILL.md:240-246`).
- **Fold:** drafter reads its API base URL from config or `ANTHROPIC_BASE_URL`. The end-to-end test points it at an `httptest` server that returns a fixed `input_tokens`, and asserts the printed estimate against a hand-computed figure.

## 17. Major: `check-prompts` proves only that each builder doesn't throw

- **Tag:** correctness
- **Location:** `docs/superpowers/specs/2026-10-12-drafter-pipeline-design.md:96,106-113,120-122`
- **Defect:**
  - "Renders each against fixture inputs" passes if each builder returns any string. The spec's purpose is "a chain edit that breaks drafter fails at commit time". A changed builder signature, or a renamed context field read as `undefined`, renders a plausible non-empty prompt and passes.
  - The byte-identical evidence covers one builder. `gojaprobe` built one prompt (`node.txt`, 14,920 bytes) out of the 28, with one page type and round.
  - The 109 branches mean one fixture per seat leaves most paths unrendered.
  - The dotfiles gate (local only, no CI) would call a binary from another repo. The spec doesn't say whether a missing `drafter` fails the gate or skips it.
- **Fold:**
  - Each seat renders under a named matrix: page type by round by narrowed or not by after-final-read, including the outline and rework variants the chain carries. Each rendered prompt must equal Node's output for the same context. A small node script in the chain's tests writes the expected outputs. They are literal bytes, so a golden is the right tool here.
  - Each prompt must also contain the context's page path and, when given, its findings text.
  - The gate fails when `drafter` is absent.

## 18. Major: what an escalated or in-progress page leaves in the shared worktree is undefined

- **Tag:** correctness
- **Location:** `docs/superpowers/specs/2026-10-12-drafter-pipeline-design.md:24-25,261-265,302`
- **Defect:**
  - Several pages run in one worktree, and the docs gate and index-link command act on the whole tree. Page B's red draft can fail page A's gate. The fix turn then tells A to "fix every failure that names this page" (`batchchain.py:248`), and A uses up its two fix turns on B's failure.
  - The spec doesn't say whether an escalated page's draft and brief stay on disk, are restored, or are moved aside.
  - Criterion 1 judges pages "in the pass's PR", which then may hold escalated drafts or be red.
  - No test covers two pages interacting.
- **Fold:** Specify the following and test it:
  - An escalated page's files are restored to `HEAD` and its draft is kept only in the record.
  - The gate's failing sections are filtered to the current page's paths before a fix turn. Failures elsewhere, while a page's own sections are clean, don't count against it.
  - The state-machine test includes a two-page row where page B's red gate doesn't consume page A's fix turns.

## 19. Minor: billing-cycle reset and the run and ceiling caps' effect on other pages are unspecified

- **Tag:** correctness
- **Location:** `docs/superpowers/specs/2026-10-12-drafter-pipeline-design.md:225-234,289`
- **Defect:**
  - "Resets on the billing-cycle date" has no timezone and no rule for a cycle day of 29 to 31 in a shorter month. The test row "the cycle resetting on the billing date" would likely use a mid-month day and miss both cases.
  - "A page at its cap escalates" says nothing of the per-run or per-cycle cap. When the $40 run cap hits mid-run, the spec doesn't say whether every in-flight page escalates, stops for `--resume`, or finishes its current stage.
- **Fold:** State that the reset is in UTC, and that a cycle day past the month's end clamps to its last day. When a run or cycle cap is hit, every page stops resumably with `reason: run cap` or `reason: cycle cap`. Add test rows for day 31 in February, the exact reset instant, and a run cap hit with two pages in flight.

## 20. Minor: "cited in that section" has no mapping from a brief sentence or plan section to a page heading

- **Tag:** correctness
- **Location:** `docs/superpowers/specs/2026-10-12-drafter-pipeline-design.md:198-200`
- **Defect:**
  - A brief sentence carries only `text` and `id`, with no section (`spike/choose-draft1.brief`, keys `page`, `sentences`, `cuts`). The check must find the sentence's text on the page to learn its heading, and the brief's text can differ from the page's Markdown in emphasis and code spans.
  - A plan section's id must also map to a page heading, and the spec gives no rule.
  - An implementation that fails to find a sentence must either flag a false miss or skip the check silently.
- **Fold:** Each plan section names its page heading text. Brief sentences are located by the normalization from finding 7. A sentence that can't be located is reported, never skipped. Add a test row where the brief sentence and the page differ only in a code span.

## 21. Minor: the cost model's prices are unsourced, and the 5% criterion depends on them

- **Tag:** correctness
- **Location:** `docs/superpowers/specs/2026-10-12-drafter-pipeline-design.md:84,232-233,243-246,323`
- **Defect:**
  - The ledger's cost is computed by drafter, and the spec gives no price source.
  - The spike hard-codes Opus prices, including a cache-read rate of 0.4 (`batchchain.py:181-182`). The workstation's pricing note marks Opus 5.5's cache-read price "not recorded" and gives Haiku 5.5 a tiered price above 100k context (`fable-post-cutoff-system.md:99-100`). The spike's reads run 48k to 248k input tokens.
  - The spike also prices every cache write at the five-minute rate, while the usage block splits `ephemeral_1h_input_tokens`, and `response1.json` wrote 113,918 one-hour tokens.
- **Fold:** Keep a dated price table in `drafter.toml`, citing claude.com/pricing, with the cache-write and cache-read rates per TTL and Haiku's tiers. Add a cost test row each for a one-hour cache write and a Haiku request above 100k.

## 22. Minor: records are pruned at 30 days, but the pilot's evidence may need them longer

- **Tag:** correctness
- **Location:** `docs/superpowers/specs/2026-10-12-drafter-pipeline-design.md:252-253,299-312`
- **Defect:** Criteria 2 and 4 read the records and ledger at cutover. A pilot that spans more than 30 days, or a cutover decided later, loses the early pages' records.
- **Fold:** Prune only records whose page is accepted or whose pass has closed, or exempt runs tagged `--keep`. Tag pilot runs.

## 23. Minor: a markdown-plan fallback silently disables the checks the pilot is meant to judge

- **Tag:** correctness
- **Location:** `docs/superpowers/specs/2026-10-12-drafter-pipeline-design.md:218-219,299-312`
- **Defect:** An existing markdown plan runs "without the plan-dependent checks", so with no coverage check and no plan check. A pilot page on a markdown plan exercises none of the new mechanisms, yet still counts toward the five.
- **Fold:** The pilot section requires a YAML plan for every pilot page, and `record.json` records `plan_format` so the count can be checked.

## 24. Minor: gate-log extraction and path detection are tied to cairn's formats, and size limits drop files silently

- **Tag:** correctness
- **Location:** `docs/superpowers/specs/2026-10-12-drafter-pipeline-design.md:87,99-102,159-161,286-288`
- **Defect:**
  - "Nothing in drafter is cairn-specific", but the spike's extraction depends on `cairn-run-gate`'s `check(s) failed:` and `== name ==` format (`batchchain.py:221-229`). Its path detection uses a cairn-specific prefix list (`:62`).
  - An unparseable log falls back to the tail with no flag.
  - A file of 400 KB or more is neither inlined nor reported (`:73-76`).
  - None of these behaviors is tested.
- **Fold:** `drafter.toml` names the log's section and failure-list patterns and the path roots. An unparseable log is extracted as the tail and recorded as `gate_log: unparsed`. An oversized file gets an explicit "not inlined: N bytes" block. Add a test row for each.

## 25. Minor: the final reader's cold-read isolation is promised but not tested

- **Tag:** correctness
- **Location:** `docs/superpowers/specs/2026-10-12-drafter-pipeline-design.md:162-163,286-287`
- **Defect:** "The final reader gets only the page, with the job held back until its step 3" is a request-shape promise. An assembly that inlines files named in the reader's prompt, as every other seat's does, breaks the cold read and passes every listed test.
- **Fold:** Add an input-assembly row. The reader's request holds exactly one `<file>` block, the page, and the job text appears only inside the `<step3>` block.

## 26. Minor (OWNER FORK, optional): the blind grader and "ordinary fixes" have no bar

- **Tag:** optional
- **Location:** `docs/superpowers/specs/2026-10-12-drafter-pipeline-design.md:302-303`
- **Defect:**
  - "A blind grader reads each against the register as a second opinion" spends a model read per page, but the criterion doesn't say what its verdict does.
  - "After ordinary fixes" separates acceptance from rework with no line between them.
- **OWNER FORK:**
  - (a) The grader gates. A grade below "publishable after ordinary fixes" fails criterion 1 for that page.
  - (b) The grader is advisory and recorded only.
  - (c) Drop the grader. Geoff's PR read is the judgment.
  - Recommendation: (a). It is the only option that gives the grader's cost a purpose. Define "ordinary" as fixes that change no plan item's substance and no fact claim.

## 27. Minor (optional, over-ceremony): prompt caching on continuations is at best break-even

- **Tag:** optional
- **Location:** `docs/superpowers/specs/2026-10-12-drafter-pipeline-design.md:243-246`
- **Defect:**
  - A continuation is a new batch submitted after a gate run. The spike's gate took about 4 to 6 minutes (`run-rotate-edit2.log` 11:30:32 to 11:34:48, and 11:44:01 to 11:49:57), and batches took 2 to 5 minutes. Together they outlast a five-minute cache.
  - A one-hour write costs 2x input, by the spec's own measure. One cache read then costs 0.1x, so a single continuation pays 2.1x against 2x uncached.
  - Only a second continuation breaks even. The spec also gives no criterion or test for caching.
- **Fold:** Leave caching out of the first build, and revisit it on the pilot's ledger if continuations average more than one per page. That saves its implementation, the cost-model branch for it, and its tests.

## 28. Minor (OWNER FORK): rework pages aren't addressed

- **Tag:** correctness
- **Location:** `docs/superpowers/specs/2026-10-12-drafter-pipeline-design.md:56-69,126-133`
- **Defect:** The chain has a `rework` mode with scoped reads and a `git diff`-based scope (`docs-page-chain.js:1970-1977,1990-1994`). The spec neither brings it into drafter nor excludes it. A rework page handed off would run as a fresh draft, with round-1 reads over the whole page.
- **OWNER FORK:**
  - (a) Exclude rework from sub-project 1: rework pages stay on the chain, and drafter refuses them (finding 14).
  - (b) Bring rework in now, with its scope rules as stated stop rules and tests.
  - Recommendation: (a), since the spike never ran a rework page and the pilot criteria don't cover one.

## 29. Minor: `make smoke` names no assertion and may not exercise production's request shape

- **Tag:** correctness
- **Location:** `docs/superpowers/specs/2026-10-12-drafter-pipeline-design.md:294-295`
- **Defect:**
  - "Runs one real Haiku 5.5 batch" doesn't say what it checks.
  - Production requests set `output_config.effort` and a strict JSON schema (`batchchain.py:157-162`). Whether Haiku 5.5 accepts the same shape is unverified here, so the smoke may run a different request than production.
- **Fold:** The smoke submits one request per seat shape, with schema, effort, and system prompt as production builds them, on the cheapest model that accepts that shape. It asserts each result parses to its schema, the ledger gains one line per request, and the line's cost matches the usage block under the price table.
