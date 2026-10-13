# Approval queue pass plan

Design: `docs/superpowers/specs/2026-10-12-approval-queue-design.md` (approved in the queue 2026-10-12, with Geoff's two chat rulings recorded in it). Mock-ups, settled decisions, and the audit ledgers: `docs/superpowers/specs/2026-10-12-approval-queue-mockups/`. Class: `runner`. Adapter: `dotfiles-pass`. Design estimate: 420 path minutes; standing approval to 1260.

Every task's acceptance includes the adapter gate, `bash scripts/gate.sh`, green at the task's commit.

"Avoid over-engineering. Only make changes that are directly requested or clearly necessary. Keep solutions simple and focused: - Scope: Don't add features, refactor code, or make "improvements" beyond what was asked. A bug fix doesn't need surrounding code cleaned up. A simple feature doesn't need extra configurability. ... - Defensive coding: Don't add error handling, fallbacks, or validation for scenarios that can't happen. Trust internal code and framework guarantees. Only validate at system boundaries (user input, external APIs). - Abstractions: Don't create helpers, utilities, or abstractions for one-time operations. Don't design for hypothetical future requirements. The right amount of complexity is the minimum needed for the current task." (<https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices>)

"Deliver what was asked, at the scope intended. Make routine judgment calls yourself, and check in only when different readings of the request would lead to materially different work. If the request seems mistaken or a better approach exists, say so in a sentence and continue with the task as asked rather than quietly narrowing, widening, or transforming it. Finish the whole task, and stop short of actions that are clearly beyond what was asked." (<https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5>)

## T1. Rename review-desk to approval-queue (60 min, runner)

**Outcome.** No live file names `review-desk`, "review desk", or `claude-desk-reminder`. A new gate leg keeps it that way.

**Files.**
- `review-desk/` moves to `approval-queue/` by `git mv`, including `package.json` `name`. The env var `REVIEW_DESK_STATE` becomes `APPROVAL_QUEUE_STATE`.
- `bin/.local/bin/review-desk` becomes `approval-queue`. Its state root becomes `${XDG_STATE_HOME:-$HOME/.local/state}/approval-queue`, its usage and error strings use the new name, and its `pkill` pattern becomes `approval-queue/[b]uild`.
- `bin/.local/bin/claude-desk-reminder` becomes `claude-approval-queue-reminder`. Its context text calls the tool by the new name and the app "Design & PR Approvals", and never says "desk".
- Edit in place: `claude/.claude/settings.json` (the hook command), `scripts/check.sh` (the leg names, the `check_review_desk` function, and the app path), `tests/review-desk.test.sh` and `tests/claude-desk-reminder.test.sh` (renamed to match), `claude/.claude/skills/pass-core/SKILL.md` (every `review-desk` and "desk" use), `docs/STATUS.md`, and `ROADMAP.md`. Visible UI strings that say "Review desk" become "Design & PR Approvals".
- New gate leg in `scripts/check.sh`: `git grep -n -I -i -E 'review[- ]desk|claude-desk-reminder'`, excluding `docs/superpowers/` and `docs/HISTORY.md`. It fails the gate on any match.

**Acceptance.**
- The new leg passes.
- `git grep -i 'review[- ]desk'` outside the two excluded paths prints nothing.
- `bash tests/approval-queue.test.sh` and `bash tests/claude-approval-queue-reminder.test.sh` pass.
- `npm --prefix approval-queue run check` and `npm --prefix approval-queue test` pass.

**Test.** The renamed shell tests already cover the command's flow; their expectations change only for the new names and the new state path.

## T2. The brief parser and triage shape (90 min, runner), pair with T3

**Outcome.** `approval-queue/src/lib/brief.ts` parses the design's brief contract from a PR body or a design doc, and the triage file takes the `{headline, lede, rows}` shape. Both report every missing required part by name.

**The contract, exactly.** T4's register teaches this same shape.

- `## Brief` opens the document.
- The first paragraph under it is the headline, then the lede: the first sentence of that paragraph is the headline and the rest is the lede. If the paragraph has one sentence, the next paragraph is the lede.
- Required subsections: `### What changes` (a list), `### If you approve` (an ordered list).
- Optional subsections:
  - `### Worth knowing`: a paragraph.
  - Zero or more `### Decide: <title>`, each holding a paragraph, an optional `Source: <text>` line, and a list of options. One option may end in `(recommended)`.
  - Zero or more `### <label>` detail sections, whose first sentence is the row summary.
- The brief ends at the next `## ` heading. Everything after it is the technical notes.
- A triage file is `{headline, lede, rows: [{action, why, detail, proposed}]}`, where `proposed` keeps today's values, `now`, `defer`, or `drop`. The page labels them Do now, Do later, and Don't do.

**Files.** `approval-queue/src/lib/brief.ts` and `brief.test.ts`; `approval-queue/src/lib/triage.ts` and its test, for the new row fields; `approval-queue/src/lib/server/items.ts`, for the triage shape; fixtures under `approval-queue/src/lib/fixtures/`. The fixtures are the PR #40 brief and the drafter Pass 0 triage, both taken from `generate.py` in the mock-ups folder.

**Acceptance.**
- `brief.test.ts` parses both fixtures to the expected structure.
- One case per required part shows a document missing that part reports it by name.
- A `### Decide:` block with a `(recommended)` option parses its options in order.

## T3. The writing register and its pointers (60 min, runner), pair with T2

**Outcome.** Sessions learn the brief format where they write it.

**Files.**
- New: `claude/.claude/docs/voice/approval-brief.md`.
  - The standards: the inverted pyramid; the Federal Plain Language Guidelines (<https://www.plainlanguage.gov/guidelines/>); and Nielsen Norman Group on writing for the web and on progressive disclosure, both cited by URL.
  - The exact contract from T2.
  - Three exemplars: the PR #40 brief, the triage brief, and a before-and-after pair from one real PR body in `docs/superpowers/plans/`.
  - The naming rule: "Design & PR Approvals" or "approval", never "the desk".
- Edit: the `claude/.claude/skills/writing-voice/SKILL.md` router table gains an "Approval-queue brief" row. `claude/.claude/docs/voice/commit-and-pr.md` gains one sentence pointing PR bodies at the register for their `## Brief`. `pass-core` Close names the register where it hands a PR over. The hook's context text names the register path.

**Acceptance.**
- The register's exemplars parse cleanly under T2's parser. After both tasks merge, T4 runs that check.
- `tellgrader` and `vale-hook` report nothing blocking on the new file.

## T4. The command refuses an item without a brief (45 min, runner)

**Outcome.** `approval-queue pr|design|triage` exits 2 before queuing an item whose brief is missing or incomplete. Its stderr names each missing part and the register path.

**Files.** `bin/.local/bin/approval-queue` calls a check entry point in the app, run with `node`, that shares T2's parser. The executor picks the entry form that the app's build and test setup already supports, and states the choice in the commit. Tests go in `tests/approval-queue.test.sh`.

**Acceptance.** Shell tests cover four cases:
- A PR with a full brief queues.
- A PR body with no `## Brief` exits 2, naming the brief and the register path.
- A design missing `### If you approve` exits 2, naming it.
- A triage file in the old array shape exits 2.

The register's exemplars pass the check.

## T5. The page: layout, PR view, decision bar (150 min, runner)

**Outcome.** The PR page matches `pr-clean.html` and `pr-problem.html` from the mock-ups, built from stock DaisyUI 5 components and the desk theme's tokens, with every fix in the three audit ledgers applied.

**What it covers.**
- The sidebar shows "Design & PR Approvals" and lists each queued item by its headline.
- The headline block holds the headline, lede, "What changes", and "If you approve", with "Worth knowing" as its footnote line.
- The "Decide first" cards cover two sources:
  - the brief's `### Decide:` blocks;
  - the app's own: a failing check, a review verdict of `fix` or `escalate`, and a `## Before merge` section.
- Details and Evidence render as chevron disclosure rows.
- The floating decision bar carries the status summary. Approve stays disabled until every card has a choice.

**Decision output.** An approve decision adds `choices: [{title, choice}]` for each card. A "send back" choice turns the bar's primary action into Send back.

**Files.** `approval-queue/src/routes/+layout.svelte`, `ItemPanel.svelte`, `PrView.svelte`, `app.css`, `pr-summary.ts`, and the PR branch of `item/[id=id]/+page.server.ts` with its tests.

**Acceptance.**
- Server tests cover the load data for both fixtures, including the auto-promoted cards.
- A rendered read at 390, 1024, and 1440 in both themes matches the mock-up screenshots.
- `daisyui-a11y-reviewer` and `svelte-reviewer` accept.

## T6. Triage and design views (90 min, runner)

**Outcome.** The triage page matches `triage.html`: the headline block; Do now, Do later, and Don't do groups; each row with Do now / Do later / Don't do choices, a Note button, and a Technical detail toggle; and the bar's "Submit calls". The design page shows the brief's headline block above the document.

**Decision output.** Each submitted row returns `{action, disposition, note}`, and the session's `why` is never overwritten.

**Files.** `TriageView.svelte`, `DesignView.svelte`, `triage.ts`, the triage and design branches of `+page.server.ts`, and their tests.

**Acceptance.** Server tests cover a submit with a changed disposition and a note. A rendered read matches `triage.html` at 390 and 1440 in both themes.

## T7. End to end and visual verification (60 min, runner)

**Outcome.** The design's end-to-end check passes against the built app.

**Acceptance.**
- The design doc, given in the queue, renders with its brief on top.
- A copy with `## Brief` removed is refused.
- The drafter triage in the new shape renders as the mock-up does.
- `visual-verifier` grades each page against the mock-up screenshots and finds no STRUCTURAL difference.

## Path

T1 (60) → T2 ‖ T3 (90) → T4 (45) → T5 (150) → T6 (90) → T7 (60) = 495 path minutes.

That's under the 840-minute default stop and the 1260-minute standing approval.

## Before merge (for the PR body)

1. Confirm no live cairn-cms or dubplate session still needs `review-desk`. Check `claude agents --json` and each project's STATUS. Or send each live session the new command name, and wait for its acknowledgment.
2. Stop the running app with `pkill -f 'review-desk/[b]uild'`, once `~/.local/state/review-desk/items` holds no `item.json` without a `decision.json`.
3. Move the state folder with `mv ~/.local/state/review-desk ~/.local/state/approval-queue`.

## After merge

- `stow -R bin`, then confirm `~/.local/bin/review-desk` and `claude-desk-reminder` are gone and the new names resolve.
- `claude-tooling-sync apply`.
- The first `approval-queue` call builds the app.

## Later

- Generating briefs with a model.
- A fallback layout for briefless items.
