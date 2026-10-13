# Approval queue pass plan

Design: `docs/superpowers/specs/2026-10-12-approval-queue-design.md` (approved in the queue 2026-10-12, with Geoff's chat rulings recorded in it, and the B3 design fold of 2026-10-12). Mock-ups, settled decisions, and the audit ledgers: `docs/superpowers/specs/2026-10-12-approval-queue-mockups/`. The mock-up pages (`pr-clean.html`, `pr-problem.html`, `triage.html`, and their `dark-*.html` variants) are self-contained and open straight from the repo. The reference screenshots are `refs/<page>-<light|dark>-<390|1024|1440>.png`, 18 images. Review: `docs/superpowers/research/2026-10-12-approval-queue-review-mechanics.md`; fold record: `docs/superpowers/research/2026-10-12-approval-queue-fold.md`. Class: `runner`. Adapter: `dotfiles-pass`. Design estimate: 420 path minutes; standing approval to 1260.

Every task's acceptance includes the adapter gate, `bash scripts/gate.sh`, green at the task's commit.

"Avoid over-engineering. Only make changes that are directly requested or clearly necessary. Keep solutions simple and focused: - Scope: Don't add features, refactor code, or make "improvements" beyond what was asked. A bug fix doesn't need surrounding code cleaned up. A simple feature doesn't need extra configurability. ... - Defensive coding: Don't add error handling, fallbacks, or validation for scenarios that can't happen. Trust internal code and framework guarantees. Only validate at system boundaries (user input, external APIs). - Abstractions: Don't create helpers, utilities, or abstractions for one-time operations. Don't design for hypothetical future requirements. The right amount of complexity is the minimum needed for the current task." (<https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices>)

"Deliver what was asked, at the scope intended. Make routine judgment calls yourself, and check in only when different readings of the request would lead to materially different work. If the request seems mistaken or a better approach exists, say so in a sentence and continue with the task as asked rather than quietly narrowing, widening, or transforming it. Finish the whole task, and stop short of actions that are clearly beyond what was asked." (<https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5>)

## The rendered-read harness (T5, T6, T7)

Every rendered read and the end-to-end check run against a private server, never the live one on 7907, never Firefox, and never the command's wait loop:

- Build with `npm --prefix approval-queue run build`, then start `HOST=127.0.0.1 PORT=<a free port> APPROVAL_QUEUE_STATE=<a temp dir> node approval-queue/build` (adapter-node reads `HOST` and `PORT`: `src/index.js` lines 10-11 of `@sveltejs/adapter-node`).
- Seed each item as a directory under `<temp dir>/items/<id>/` in the shape the command writes: `item.json` (with `headline`), plus `body.md`, `pr.json`, and `diff.patch` for a PR, `doc.md` for a design, or `triage.json` for a triage.
- Light screenshots: `chromium-shot -w <width> -H <tall height> -o <file> <url>`. Dark screenshots: `chromium-browser --headless=new --disable-gpu --hide-scrollbars --force-dark-mode --user-data-dir=<temp profile> --window-size=<width>,<height> --screenshot=<file> <url>`, because `chromium-shot` has no dark option. Probed 2026-10-12: `--force-dark-mode` makes headless Chromium match `prefers-color-scheme: dark`, which is how the DaisyUI theme picks dark (`prefersdark: true` in `survey/theme.css`).
- `visual-verifier` compares each screenshot with its `refs/` image at the same page, theme, and width.

## T1. Rename review-desk to approval-queue (75 min, runner)

**Outcome.** No live file names `review-desk`, `REVIEW_DESK_STATE`, "review desk", or `claude-desk-reminder`. A new gate leg keeps it that way.

**Files.** Every file the leg's pattern matches today. On 2026-10-12, `git grep -l -I -i -E 'review[-_ ]?desk|claude-desk-[r]eminder' -- . ':!docs/superpowers/' ':!docs/HISTORY.md'` lists 21:
- `review-desk/` moves to `approval-queue/` by `git mv`. Inside it: `package.json` and `package-lock.json` (`name`, lines 2 and 8); `src/env.ts` and every reader of `REVIEW_DESK_STATE`, which becomes `APPROVAL_QUEUE_STATE`; the `mkdtemp` prefixes in `items.test.ts:17`, `routes/page.server.test.ts:23`, and `item/[id=id]/page.server.test.ts:41`; and the page titles in `+page.svelte:80` and `item/[id=id]/+page.svelte:11`. Visible UI strings that say "Review desk" become "Design & PR Approvals".
- `bin/.local/bin/review-desk` becomes `approval-queue`. Its state root becomes `${XDG_STATE_HOME:-$HOME/.local/state}/approval-queue`, its usage and error strings use the new name, and its `pkill` hint becomes `approval-queue/[b]uild`.
- `bin/.local/bin/claude-desk-reminder` becomes `claude-approval-queue-reminder`. Its context text calls the tool by the new name and the app "Design & PR Approvals", and never says "desk".
- Edit in place: `claude/.claude/settings.json` (the hook command), `scripts/check.sh` (the leg names, `check_review_desk`, and the app path), `tests/review-desk.test.sh` and `tests/claude-desk-reminder.test.sh` (renamed to match), `claude/.claude/skills/pass-core/SKILL.md` (every `review-desk` and "desk" use), `docs/STATUS.md`, and `ROADMAP.md`.
- New gate leg in `scripts/check.sh`: `git grep -n -I -i -E 'review[-_ ]?desk|claude-desk-[r]eminder' -- . ':!docs/superpowers/' ':!docs/HISTORY.md'`. It fails the gate when `git grep` exits 0 (a match) and passes when it exits 1. The bracket in `[r]eminder` and the `[-_ ]?` class keep the leg from matching its own line (probed 2026-10-12: the pattern matches `REVIEW_DESK_STATE`, `reviewdesk`, "Review desk", and `claude-desk-reminder`, and not the line that holds it).

**Acceptance.**
- The new leg passes on the renamed tree.
- The leg fails on a planted match: an intent-to-add file (`git add -N`) holding `review-desk` makes it fail, and the file is then removed. Probed: `git grep` searches an intent-to-add file. The commit message records the planted run.
- `bash tests/approval-queue.test.sh` and `bash tests/claude-approval-queue-reminder.test.sh` pass.
- `npm --prefix approval-queue run check` and `npm --prefix approval-queue test` pass.

**Test.** The renamed shell tests already cover the command's flow. Their expectations change only for the new names and the new state path.

## T2. The brief parser and the triage shape, end to end (120 min, runner), pair with T3

**Outcome.** `approval-queue/src/lib/brief.ts` parses the brief contract from a PR body or a design doc and validates a triage file. Every state in the table below reports as listed. The triage file takes the `{headline, lede, rows}` shape through every reader and writer in the app, so the app compiles and its tests pass at T2's commit.

**The contract, exactly.** T3's register teaches this same shape, and the design's "The brief contract" states it.

- The first `## ` heading outside a code fence is `## Brief`. A `# Title` line above it is allowed. CRLF line endings are normalized to LF before parsing.
- The first paragraph under `## Brief` is the headline, then the lede: the first sentence of that paragraph is the headline and the rest is the lede. If the paragraph has one sentence, the next paragraph is the lede. Sentences split with `Intl.Segmenter('en', {granularity: 'sentence'})` (probed 2026-10-12 on Node 24.20: "e.g.", "U.S.", "PR #40.", and a backticked path split correctly).
- Required subsections: `### What changes` (a bulleted list) and `### If you approve` (a numbered list).
- Optional subsections. The register teaches the design's order (Decide blocks, then Worth knowing, then details); the parser accepts them in any order after the required ones:
  - Zero or more `### Decide: <title>`. Each holds a paragraph, then an optional `Source: <text>` line standing as its own paragraph, then a list of at least two choices. At most one choice ends in `(recommended)`.
  - At most one `### Worth knowing`: a paragraph.
  - Zero or more `### <label>` detail sections. Each opens with a paragraph whose first sentence is the row summary shown while the row is closed.
- Headings match their exact spelling, case included.
- The brief ends at the next `## ` heading. Everything after it is the technical notes.
- A triage file is `{headline, lede, rows: [{action, why, detail, proposed}]}`. `detail` is optional. `proposed` keeps today's values, `now`, `defer`, or `drop`, and the page labels them Do now, Do later, and Don't do.
- Decision output: a submitted triage returns `{decision: 'submit', rows: [{action, disposition, note}]}`, so Geoff's edit arrives as `note` and the session's `why` is never overwritten. An approve returns `{decision: 'approve', choices: [{title, choice}]}` (T5 fills `choices`).

**States.** Each row is one test. "Refuse" means the check exits 2 and prints the message; every refusal also prints the register path, `~/.claude/docs/voice/approval-brief.md`.

| Input | Result |
| --- | --- |
| Empty body, no `## Brief`, `## Brief` only inside a code fence, or another `## ` heading first | Refuse: "no `## Brief`; it must be the first `##` heading" |
| First block under `## Brief` is not a paragraph | Refuse: "missing headline" |
| One-sentence first paragraph and no paragraph after it | Refuse: "missing lede" |
| `### What changes` absent, or its first block is not a bulleted list | Refuse, naming `What changes` and the list it needs |
| `### If you approve` absent, or its first block is not a numbered list | Refuse, naming `If you approve` and the numbered list it needs |
| A required heading twice, or `### Worth knowing` twice | Refuse, naming the duplicate |
| A heading that matches a contract heading only when case is ignored | Refuse: "write it as `### What changes`" (the exact spelling) |
| `### Decide:` with no title, fewer than two choices, or two `(recommended)` | Refuse, naming the block and the defect |
| A `Source:` line joined to the paragraph above it | Refuse: "`Source:` must stand as its own paragraph" |
| A detail section that does not open with a paragraph | Refuse, naming the label |
| CRLF line endings | Accept (normalized) |
| Triage: not valid JSON | Refuse: "not valid JSON" |
| Triage: a JSON array (the old shape) | Refuse: "old triage shape; write `{headline, lede, rows}`" |
| Triage: missing or empty `headline`, `lede`, or `rows` | Refuse, naming the field |
| Triage: a row missing `action` or `why`, or with `proposed` outside now/defer/drop | Refuse, naming the row number and field |
| Triage: a row with no `detail` | Accept |

**Files.**
- New: `approval-queue/src/lib/brief.ts` and `brief.test.ts`, and fixtures under `approval-queue/src/lib/fixtures/`: the PR #40 brief and the drafter Pass 0 triage. `brief.ts` imports no package, since T4 runs it under plain `node` with no `node_modules`. It uses only erasable TypeScript syntax and `type` imports.
- The shape, end to end: `approval-queue/src/lib/triage.ts` and its test; `approval-queue/src/lib/server/items.ts` (the triage type, the `Decision` type, and an optional `headline` on `ItemMeta` that T4's command writes); the triage load and the `submit` action in `approval-queue/src/routes/item/[id=id]/+page.server.ts` and its `page.server.test.ts`; and the field renames that keep `TriageView.svelte` and `ItemPanel.svelte` compiling (the in-place reason edit becomes a note edit, and the hidden `reason` input becomes `note`). T6 keeps the visual and interaction rebuild.
- Fixture copy comes verbatim from `generate.py` (decisions.md rule 11), with three mechanical mappings: HTML entities become their characters (`&rsquo;` becomes ’), `<code>x</code>` becomes `` `x` ``, and the triage keys `later` and `skip` become `defer` and `drop`. Under Geoff's 2026-10-12 expunge ruling, the identifier `claude-desk-reminder` in the PR #40 "The reminder" detail becomes `claude-approval-queue-reminder`.

**Acceptance.**
- `brief.test.ts` parses both fixtures to the expected structure.
- One test per row of the state table passes.
- A `### Decide:` block with a `(recommended)` choice parses its choices in order.
- The item route's server tests seed the new triage shape and cover a submit with a changed disposition and a note, returning `{action, disposition, note}`.

## T3. The writing register and its pointers (75 min, runner), pair with T2

**Outcome.** Sessions learn the brief format, and the new triage and decision shapes, where they read them.

**Files.**
- New: `claude/.claude/docs/voice/approval-brief.md`.
  - The standards: the inverted pyramid; the Federal Plain Language Guidelines (<https://www.plainlanguage.gov/guidelines/>); and Nielsen Norman Group on writing for the web and on progressive disclosure, each cited by URL.
  - The exact contract and state table from T2.
  - Exemplars. Each passing exemplar sits in a fenced block whose info string is `brief` (Markdown) or `brief-triage` (JSON), so T4's test can extract it: the PR #40 brief, the drafter Pass 0 triage brief, and the "after" half of a before-and-after pair from one real PR body in `docs/superpowers/plans/`. The "before" half is a counter-example in a plain `markdown` fence. Exemplar copy follows T2's verbatim-copy rule and its mappings.
  - The naming rule: "Design & PR Approvals" or "approval", never "the desk".
- Edit:
  - The `claude/.claude/skills/writing-voice/SKILL.md` router table gains an "Approval-queue brief" row.
  - `claude/.claude/docs/voice/commit-and-pr.md` gains one sentence pointing PR bodies at the register for their `## Brief`.
  - `pass-core`: step 1 Design says a design doc opens with `## Brief` (after its title) per the register. Close says a PR body opens with `## Brief` per the register. The triage sentences (today lines 221-226 and 230-236) describe the triage file as `{headline, lede, rows: [{action, why, detail, proposed}]}`, the submitted rows as `{action, disposition, note}`, and an approve as carrying `choices: [{title, choice}]`.
  - The hook's context text names the register path.

**Acceptance.**
- `grep -n 'approval-brief.md'` finds the register named in the router table, `commit-and-pr.md`, `pass-core`, and the hook.
- `pass-core` no longer describes a triage row as an item with a disposition and a reason.
- The register's exemplars pass T2's check. After both tasks merge, T4's test runs that check.
- Advisory, not gating: `tellgrader --register agent claude/.claude/docs/voice/approval-brief.md` is run and each finding is read. Dotfiles has no `.tellgrader.json`, so no rule gates here (per `tellgrader --help`).

## T4. The command refuses an item without a brief (60 min, runner)

**Outcome.** `approval-queue pr|design|triage` exits 2 before queuing an item whose brief is missing or incomplete. Its stderr carries the check's messages and the register path. A queued item's `item.json` carries the brief's `headline`.

**Files.**
- New: `approval-queue/src/check-brief.ts`, the entry point, run as `node approval-queue/src/check-brief.ts <kind> <file>`. It imports `brief.ts` and nothing from `node_modules`. It exits 0 and prints the headline as JSON on a valid brief, exits 2 with the state table's messages on a brief defect, and exits 1 on a tool failure (an unreadable file). Node 24 strips the types (probed 2026-10-12 on Node 24.20: a `.ts` entry importing `#lib/brief.ts` through the package's `imports` map runs with no `node_modules`, while an import of `marked` fails `ERR_MODULE_NOT_FOUND`).
- `bin/.local/bin/approval-queue`: runs the check on the body, design, or triage file before `mkdir -p "$item"`, so a refusal leaves no item directory. For a PR, it checks the body from `gh pr view` before writing anything. It writes `headline` into `item.json`. A failure to run `node` is exit 1.
- `tests/approval-queue.test.sh`: its fixtures (today `the body`, `# design`, and the array triage) gain valid briefs, and it extracts each `brief` and `brief-triage` block from the register and runs the check on it.

**Acceptance.** The shell tests cover:
- A PR with a full brief queues, and its `item.json` holds the headline.
- A PR body with no `## Brief` exits 2, names the brief and the register path, and leaves no item directory.
- A design missing `### If you approve` exits 2, naming it.
- A triage file in the old array shape exits 2.
- Every register exemplar passes the check.
- The tests pass in a worktree with no `approval-queue/node_modules`.

## T5. The page: layout, PR view, decision bar (165 min, runner)

**Outcome.** The PR page matches the mock-ups `pr-clean.html` and `pr-problem.html` and their `refs/` screenshots, built from stock DaisyUI 5 components and the app theme's tokens, with every fix in the three audit ledgers applied.

**What it covers.**
- The sidebar shows "Design & PR Approvals" and lists each queued item by `item.json`'s `headline`.
- The headline block holds the headline, lede, "What changes", and "If you approve", with "Worth knowing" as its footnote line.
- The "Decide first" cards, in this order:
  - The app's own: a failing check, a review verdict of `fix` or `escalate`, and a `## Before merge` section, each with the app's own fixed choices. The failing-check and Before merge cards take their copy and choices from `pr-problem.html`. The review-verdict card follows the failing-check card's pattern and choices; its title and text are the one piece of copy the mock-ups lack, so the executor drafts it in the register and names it in the PR body for Geoff's read. "Send back to fix it" on the failing-check and review-verdict cards is the send-back choice; the Before merge card has none.
  - The brief's `### Decide:` blocks, in document order. Their choices are the session's and are never send-back choices; the chosen one returns to the session in `choices`.
- Details and Evidence render as chevron disclosure rows.
- The floating decision bar carries the status summary. Approve stays disabled until every card has a choice, and a send-back choice turns the bar's primary action into Send back.

**The Approve lock holds on the server.** The `approve` action rebuilds the card list from the body, `pr.json`, the review section, and `## Before merge`. The post carries only each card's index and its choice's index. The action refuses with `fail(400)` unless every card has a valid choice and none is a send-back choice, and it writes `choices: [{title, choice}]` from its own card list. `keys.ts` takes the lock into its context, so the `a` key does nothing while Approve is locked. `requestSubmit(submitter)` checks only that the submitter is a submit button of the form, not whether it is disabled (WHATWG HTML, <https://html.spec.whatwg.org/multipage/forms.html#dom-form-requestsubmit>). The tests for this come first.

**Files.** `approval-queue/src/routes/+layout.svelte`, `ItemPanel.svelte`, `PrView.svelte`, `app.css`, `pr-summary.ts`, `keys.ts` and its test, and the PR branch of `item/[id=id]/+page.server.ts` (load and the `approve` action) with its tests. New fixtures: PR #41, the mock-up's problem case, with a `FAILURE` conclusion in `pr.json` and a `## Before merge` section; and its variant, which adds a review section whose verdict `reviewVerdict` reads as `fix` and one `### Decide:` block.

**Acceptance.**
- Server tests load PR #40 with no cards, and PR #41 (the mock-up's problem case) with two cards in order: the failed check, then the Before merge step. A variant of PR #41 that adds a `fix` review section and a `### Decide:` block loads four cards in order: the failed check, the review verdict, the Before merge step, then the session's Decide block.
- An approve post missing a choice, carrying a send-back choice, or carrying an out-of-range index is refused with 400 and writes no `decision.json`. A complete post writes `choices` with titles from the server's list.
- `keys.test.ts`: `a` returns no action while the lock holds.
- Through the harness, screenshots at 390, 1024, and 1440 in both themes, against `refs/pr-clean-*` and `refs/pr-problem-*`, show no STRUCTURAL difference under `visual-verifier`.
- `daisyui-a11y-reviewer` and `svelte-reviewer` accept.

## T6. Triage and design views (75 min, runner)

**Outcome.** The triage page matches the mock-up `triage.html`: the headline block; Do now, Do later, and Don't do groups; each row with Do now / Do later / Don't do choices, a Note button, and a Technical detail toggle; and the bar's "Submit calls". The design page shows the brief's headline block above the document.

**Files.** `TriageView.svelte`, `DesignView.svelte`, `ItemPanel.svelte` (the triage bar and its submit), `triage.ts`, the design branch of `item/[id=id]/+page.server.ts` (the parsed brief beside the document), and their tests. T2 already carries the triage data shape and the submit output.

**Acceptance.**
- Server tests load a design whose brief parses into the headline block's data.
- Through the harness, screenshots at 390, 1024, and 1440 in both themes, against `refs/triage-*`, show no STRUCTURAL difference under `visual-verifier`.

## T7. End to end and visual verification (60 min, runner)

**Outcome.** The design's end-to-end check passes against the built app, through the harness.

**Acceptance.**
- `node approval-queue/src/check-brief.ts design docs/superpowers/specs/2026-10-12-approval-queue-design.md` exits 0. Seeded as a design item, the design renders with its brief on top.
- A copy with `## Brief` removed exits 2 from the same check.
- The drafter triage in the new shape passes the check and, seeded, renders as the mock-up does.
- `visual-verifier` grades each page against its `refs/` screenshots and finds no STRUCTURAL difference.

## Path

T1 (75) → T2 ‖ T3 (120) → T4 (60) → T5 (165) → T6 (75) → T7 (60) = 555 path minutes.

That's under the 840-minute default stop and the 1260-minute standing approval.

## Before merge (for the PR body)

The merge guard returns this section, and the merge runs with `PREMERGE_DONE=<n>` only after both steps.

1. Confirm no live caller of the old command: `pgrep -af '/review-desk (pr|design|triage)'` prints nothing. Note which cairn-cms and dubplate sessions `claude agents --json` lists as live, for the last After merge step.
2. Confirm no item is waiting: every `~/.local/state/review-desk/items/*/item.json` has a `decision.json` beside it. An item left with no live caller is an orphan (a SIGKILL leaves one on the index, per ROADMAP "Review desk hardening"). List each orphan, then remove its `item.json`.

## After merge

In this order:

1. Merge with `--match-head-commit`, then pull the checkout. The pull removes `bin/.local/bin/review-desk`, so the old command is dead from here.
2. Stop the old server: `pkill -f 'review-desk/[b]uild'`.
3. Move the state folder: `mv ~/.local/state/review-desk ~/.local/state/approval-queue`.
4. `stow -R bin`. Confirm `~/.local/bin/review-desk` is gone, and `command -v approval-queue claude-approval-queue-reminder` prints both.
5. `claude-tooling-sync apply`, which writes the live `~/.claude/settings.json` with the renamed hook.
6. Remove the old app's ignored leftovers: `ls -A ~/.dotfiles/review-desk` should show only `build`, `node_modules`, and `.svelte-kit`. Then `rm -rf ~/.dotfiles/review-desk`.
7. Prebuild: `npm --prefix ~/.dotfiles/approval-queue ci && npm --prefix ~/.dotfiles/approval-queue run build`. The first `approval-queue` call starts the server.
8. Send each live session noted in Before merge step 1 one line with `SendMessage` (pass-core's mechanism for a live session): the command is now `approval-queue`, a PR body and a design doc now open with `## Brief`, and the register is `~/.claude/docs/voice/approval-brief.md`.

## Later

- Generating briefs with a model.
- A fallback layout for briefless items.
