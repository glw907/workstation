# docs-infra currency pass

> **For agentic workers:** execute through `~/.claude/workflows/pass-execute-chains.js`. Each
> task runs as an implementer, `diff-reviewer`, gate chain. The conductor reads reports, never
> diffs.

**Goal:** close the remaining findings of the 2026-09-19 docs-infra audit, so the workstation's
always-loaded Claude context sits inside both budgets that govern it, the two over-length
skills obey the published 500-line guidance, the Vale layer is current with its versions
recorded, and an external trigger has a machine watcher instead of prose.

**Audit (this plan's spec):** `~/.claude/docs/record/2026-09-19-docs-infra-audit.md`. The plan
argues from that document; an executor reads both. Findings covered here: 1, 3, 4, 5, plus the
two vestigial items below the audit's table and finding 13 as a filing.

**Landed before this plan (the SMALL tier, applied and committed by a concurrent agent; do not
re-plan any of it):** audit finding 2 (`~/Projects/cairn-cms/.tellgrader.json` created with the
`docs-register` profile), finding 6 (`user_invocable` deleted from `content-draft` and
`content-review`), finding 9's URL repoints (`docs.anthropic.com` to `code.claude.com` across
`docs/voice/agent-facing.md` and `docs/authoring-charter.md`), and two sentence corrections,
findings 10 (`authoring-charter.md` "Build state" present tense) and 11 (cairn `CLAUDE.md`
"Authoring", the `src/lib/components/*.svelte` ESLint sentence). Also landed: the two vestigial references (the `vale-hook` `MultiEdit` branch and the
`tellgrader` `~/.claude/commands/` register home, dotfiles commit `4cb4d62`), the `vale-ci` example
bump, and the `evals.json` tool name; findings 7 and 8 (`context: fork`, `skills:`) landed in the
same commit, so decision 5 below is settled as recommended. Findings 7 and 8 were assumed
landed with that tier; decision 5 below settles it.

**Repos:** `~/.dotfiles` (tasks 1a, 2, 4, and task 5's dotfiles half) and
`~/Projects/cairn-cms` (tasks 1b, 3, and task 5's cairn half). No other repo is touched.

**Sequencing:** this pass runs after extend-1 and extend-2 land on cairn `main`, and before the
docs rebuild that follows the site round (Geoff, 2026-09-19: "we'll need it before the docs
work"). Its position relative to the one cut is decision 9.

**Budget:** ceiling **2.4M tokens**. Checkpoint interval four tasks, so at the segment boundary
after task 2 and again at close.

| Line item | Ceiling | Why |
| --- | --- | --- |
| Task 1a, workstation `CLAUDE.md` restructure | 0.50M | 399 lines read, judged, redistributed across new rules and skills, then probed |
| Task 1b, cairn `CLAUDE.md` restructure | 0.50M | 364 lines, same shape, plus the cairn gate |
| Task 2, the two skill splits | 0.25M | 1,174 lines moved with a rule-set union proof |
| Task 3, the Vale layer | 0.45M | a corpus-wide suggestion-tier run, per-rule triage, the cairn gate |
| Task 4, the watcher routine | 0.10M | one routine, one registration |
| Task 5, close | 0.20M | one dispatch plus the conductor's ledger writing |
| Fix rounds and `diff-reviewer` reads | 0.40M | six reads plus one re-dispatch allowance per chain |

**Segments.** Segment 1: tasks 1a, 1b, 2. Segment 2: tasks 3, 4, 5. Every boundary sits on a
commit its gate proved green.

**Split point, if the pass runs past its ceiling: task 4, whole.** It is a watcher for a trigger
that fires roughly monthly, nothing downstream reads it, and task 5's ledger runs without it.
Cutting it leaves 1a, 1b, 2, 3, 5 with no edge to repair.

**Independence, and what serializes anyway.** Tasks 2, 3, and 4 are independent of task 1 and of
each other. Task 1a and task 1b are independent of each other. Two things still serialize work:

- **Task 1a must run in the real `~/.dotfiles` checkout, never a worktree.** Its acceptance
  probes require the stowed live surface, because `~/.claude/CLAUDE.md` and `~/.claude/rules/`
  are stow symlinks into `~/.dotfiles/claude/.claude/`, and a worktree is not stowed. Tasks 2
  and 4 share that checkout, so all three run as one sequential chain.
- **A cairn task never runs while another executor holds the cairn main checkout.** Tasks 1b and
  3 share one worktree off `main` and share `cairn-run-gate`'s machine lock, so they run as one
  sequential chain. Verify before dispatch: `pgrep -f cairn-cms`, `git -C ~/Projects/cairn-cms
  status`, and cairn's `docs/STATUS.md` for an in-flight pass.

**Execution mode.** Two chains through `~/.claude/workflows/pass-execute-chains.js`, tasks
sequential inside each chain:

- **Chain A, `~/.dotfiles`, the real checkout:** task 1a, task 2, task 4.
- **Chain B, `~/Projects/cairn-cms`, a worktree off `main`:** task 1b, task 3.
- **Task 5, close:** conductor-led after both chains report green, with one `cairn-implementer`
  dispatch for the cairn half.

---

## Decisions for Geoff

Nine readings this plan could not settle from its inputs. Each leads with a recommendation.

**1. The cairn trim moves blocks into `.claude/rules/` with `paths:` frontmatter, not into
`docs/internal/` pointers.** Recommended. The `docs/internal/` pointer pattern is what the
2026-09-08 and 2026-09-12 rounds used, and it works, though it trades a loaded block for a file
an agent has to decide to open, which is the failure mode the four durable-gotcha sections exist
to prevent. A path-scoped rule fires when the file the gotcha is about is read, which is the
trigger the gotcha already names in prose. cairn's own Watch-items doctrine argues the same way:
promote a next-time-you-touch-X note to the mechanism that can detect the trigger. The cost is
that `.claude/` becomes a tracked directory in cairn for the first time, and worktrees each get
their own checked-out copy. Say no and task 1b falls back to `docs/internal/` pointers, which
clears the hook but not the 200-line target.

**2. The workstation's Go block becomes a path-scoped rule; Cloudflare and Secrets become
skills.** Recommended, because the three blocks have different triggers. Go work always reads a
`.go` file or a `go.mod`, so `paths:` catches it reliably. Cloudflare and secrets work often
begins from a question with no file read at all ("is that token still scoped for D1"), so a
path-scoped rule would silently miss, and an on-demand skill with a trigger-rich description is
the mechanism that fires on the prompt. Two sentences stay inline in `CLAUDE.md` either way: the
never-commit rule, and check the stores before claiming a secret is missing. Say all-rules and
the Cloudflare and Secrets blocks become unconditional rules, which is the same token cost as
today and buys only tidiness.

**3. Take all five new Google rules at their stock upstream tier, with no downgrade and no
promotion.** Recommended, on a measurement: four of the five ship at `suggestion`
(`Anthropomorphism`, `ExcessiveClaims`, `Jargon`, `Timeless`) and one at `warning`
(`WordListCase`), while cairn's `check:vale` gates at `--minAlertLevel=error`. Taking them
therefore cannot break the gate. They surface only through the `vale-hook` at save time, where
advisory findings are the intended product. The upstream files are already conservatively tuned,
with in-file comments recording false-positive counts on a 950-file corpus, so the tuning work
this decision might otherwise fund is done. Say promote-any-to-error and task 3 owes a
corpus-wide fix round that this ceiling does not fund.

**4. The watcher also watches the Claude Code docs changelog, as a fourth source.** Recommended.
This audit exists because three published Anthropic docs moved under the infrastructure without
anything noticing, which is exactly the trigger class the routine is being built for, and adding
a fourth source to one routine is cheaper than a second routine later. The cost is a noisier
ping, since that changelog moves more often than Google's whats-new. Say no and the routine
watches three sources and the Anthropic drift stays on a human re-audit.

**5. Treat audit findings 7 and 8 as landed with the SMALL tier, and file finding 13 in task 5.**
Recommended. Findings 7 (`context: fork` on `register-check` and `content-review`) and 8
(`skills: [writing-voice]` on `prose-voice-reviewer` and `cairn-register-editor`) are frontmatter
additions, which is what the SMALL tier was described as covering. Finding 13 is a filing, not a
change, so it becomes one cairn-pub ROADMAP line in task 5. Task 1a and task 5 both verify the
frontmatter rather than assume it, and if either is missing it is one line added in that task
with the addition named in the report. Say they are not in that tier and the plan gains a
seventh task.

**6. `~/.claude/rules/` is a stow-symlinked directory like its siblings, and task 1a proves it
loads before moving anything into it.** Recommended, because every other directory under
`~/.claude` is already a folded stow symlink and an exception would be the odd one out. One
documented caveat makes the proof mandatory rather than optional: Anthropic's memory doc says a
Cowork desktop session skips a symlinked `~/.claude/rules/` directory that points outside the
session's working directory. Claude Code in the terminal is unaffected, and 2.1.273 is well past
the 2.1.198 symlink-matching floor. Task 1a's first acceptance criterion is a behavioral probe
that the rule loaded; on a failure the fallback is real files under `~/.claude/rules/` with a
`.stow-local-ignore` entry, which costs a manifest line in `claude-tooling.md`. Say
real-files-from-the-start and task 1a skips the probe and pays the manifest line up front.

**7. The 200-line target is a direction for this pass and the 6,000-token hook is the hard
acceptance criterion.** Recommended. The hook is machine-enforced and the line target is
published guidance with no gate behind it, and the arithmetic is very different: the workstation
file must shed 2,083 bytes to clear the hook and roughly half its 399 lines to reach 200. This
plan's criteria therefore read "hook green, and a recorded line count with the residue named and
routed", not "under 200 or the task fails". Say hard-200 and both halves of task 1 grow by
roughly a third, most of it judgment about which broad rules survive.

**8. Re-sync cairn's vendored Vale packages from the hub, using the machine-local copy at
`~/.config/vale/styles` as the verification oracle.** Recommended. That copy is already current
at 36 Google rules and 47 Microsoft rules, and a byte diff against a fresh `vale sync` proves the
sync pulled the same release rather than a cached or mirrored variant. The hub is the source of
record; the local copy is what makes the sync checkable offline. Say copy-the-local-tree and the
sync is faster and unverified, and the recorded version numbers become an assertion rather than a
reading.

**9. Run this pass after the one cut, not before it.** Recommended, weakly, and this is the
reading the inputs genuinely do not settle. cairn's `docs/STATUS.md` puts one cut immediately
after extend-1 and extend-2, then the site round, then the docs rebuild; Geoff's instruction is
that this pass lands before the docs work. Both hold if the pass runs after the cut and before
the site round. Running it before the cut instead would put a `CLAUDE.md` restructure and a Vale
re-sync into the release window, and a Vale re-sync can move findings on published docs that the
release ships. Say before-the-cut and task 3 carries a named risk that the cut waits on its
triage.

---

## Global constraints (every task)

- **Live-surface rule, chain A.** A write under `~/.dotfiles/claude/.claude/` takes effect in
  every session on this machine at the moment of the write, with no restow and no staging. Edit
  the stow sources, never the `~/.claude/` symlinks. Every chain A task names in its report what
  a session in another repo sees differently after its commit.
- **`@path` imports are not a trim mechanism.** Anthropic's memory doc states that imported files
  are expanded into context at launch, so an import reduces file length and not token cost.
  Displacement means a path-scoped rule, a skill, or deletion. No task may claim budget relief
  from an import.
- **The em dash is banned in prose this pass writes**, and banned in code comments by
  `house/no-em-dash-in-comments`. No "not X but Y" contrast frames. No reflexive three-item
  lists.
- **Nothing in this pass raises a budget.** `CLAUDE_MD_BUDGET` stays 6000 and
  `check-skill-budget.mjs` stays at its current threshold. A task that cannot fit stops and
  reports rather than widening the ceiling.
- **Preserve every rule that moves.** A displacement that drops a rule is a task failure, whether
  the rule moved to a skill, a path-scoped rule, or a reference file. Each displacing task
  carries a union proof as an acceptance criterion.
- **No task commits a locally biased visual baseline**, and no task in this pass regenerates one.
- Plans and records this pass writes are not register-graded and carry no prose receipt.

## Measured baseline (read before task 1)

| File | Lines | Bytes | Approx tokens | Hook ceiling | Must shed |
| --- | --- | --- | --- | --- | --- |
| `~/.dotfiles/claude/.claude/CLAUDE.md` | 399 | 26,083 | 6,520 | 24,000 bytes | 2,083 bytes |
| `~/Projects/cairn-cms/CLAUDE.md` | 364 | 25,508 | 6,377 | 24,000 bytes | 1,508 bytes |

`claude-context-budget FILE...` is the check, measuring bytes divided by four. Installed Claude
Code is 2.1.273, past every version floor the rules mechanism needs (2.1.198 for symlink path
matching, 2.1.206 for `/doctor`'s trim proposals, 2.1.211 for rule loading under
`--setting-sources`).

---

### Task 1a: The workstation `CLAUDE.md` restructure

**Chain:** A, first. **Repo:** `~/.dotfiles`, the real checkout, never a worktree.
**Independent of:** tasks 1b, 3. **Deliverables:** 4 (the trimmed file, the new rules, the new
skills, the probe record).

**Outcome.** `~/.dotfiles/claude/.claude/CLAUDE.md` carries only rules that apply to every task
on this machine. Every other block reaches the session that needs it through a path-scoped rule
under `~/.dotfiles/claude/.claude/rules/` or through an on-demand skill, and each moved block's
trigger is stated and proved.

**Files:**

- Modify: `claude/.claude/CLAUDE.md`
- Create: `claude/.claude/rules/*.md`, one file per moved path-scoped block, each with `paths:`
  frontmatter
- Create: one or more `claude/.claude/skills/<name>/SKILL.md` for the blocks decision 2 routes to
  skills
- Modify: `claude/.claude/docs/claude-tooling.md`, the Layout table, adding the `rules/` row and
  any new skill
- Create: `docs/record/2026-09-19-claude-md-restructure-probes.md`, the probe record

**Blocks that must stay inline.** Each applies to work that may read no file first, so no
`paths:` pattern catches it, and each governs the opening move of an arbitrary task: Work
Autonomously Until Done; Search before you spelunk; One executor per worktree; Machine
Environment; Git Conventions; Dependencies; API-First Policy; Claude tooling and the DaisyUI-first
rule; Claude Code Agent Usage; Multi-agent workflows; and Writing voice's inline tell list, which
the file's own text says is inline so it is unmissable. Trimming prose inside these is allowed;
moving them is not.

**Candidate blocks to move, measured, with the trigger each would fire on.** The implementer
rules each one take or keep, and records the ruling with its reason.

| Block | Lines | Bytes | Proposed home | Trigger |
| --- | --- | --- | --- | --- |
| Conducting a pass, Gate economy, Pass sizing, Process proportionality, Compact instructions, Initiative-scoped sessions | 120 | 8,578 | one `conducting-a-pass` skill, with a stub of at most 8 lines inline naming the thin-conductor rule, the chain shape, the model and effort defaults, and the single human gate | a pass is being planned, conducted, sized, or checkpointed; the stub's own pointer |
| Secrets | 37 | 2,983 | a `workstation-secrets` skill, with the never-commit rule and the check-the-stores-first rule kept inline | installing, receiving, rotating, or hunting a credential |
| Sysadmin Preferences, System Organization, Dotfiles Management | 27 | 1,290 | `rules/workstation-admin.md`, with the `sudo -A` line and the software-tiers line kept inline | `paths:` over `**/.dotfiles/**`, `**/bluefin/**`, `**/*.stow-local-ignore` |
| Project ledgers | 24 | 1,627 | `rules/project-ledgers.md`, with the one-sentence three-file split kept inline | `paths:` over `**/docs/STATUS.md`, `**/docs/HISTORY.md`, `**/ROADMAP.md` |
| Cloudflare / Wrangler | 11 | 654 | a skill, or the existing `cloudflare-estate-inventory.md` with a two-line stub | a Cloudflare, Wrangler, or estate question; see decision 2 |
| Google Docs / Drive (gws) | 9 | 640 | a `gws-workspace` skill | a Google Docs, Drive, or Sheets request |
| Browsers | 7 | 387 | two sentences inline, the rest to the existing `bluefin-admin.md` | a browser or extension task, via the stub's pointer |
| Email (poplar) | 6 | 239 | `rules/poplar.md` | `paths:` over `**/poplar/**` |
| Go Development | 3 | 383 | `rules/go.md` | `paths:` over `**/*.go`, `**/go.mod`, `**/Makefile` |
| Visual fidelity, Engine-level UI mechanics | 16 | 959 | one 4-line inline block naming `visual-fidelity`, `engine-consult`, and the one-check rule | the merged stub's pointers |

Shedding 2,083 bytes needs one row. Reaching 200 lines needs the first row plus most of the
rest, which is why the first row is the task's centre of gravity.

**Acceptance criteria.** Each is a command's output or a recorded transcript.

1. `claude-context-budget ~/.dotfiles/claude/.claude/CLAUDE.md` exits 0.
2. The probe record states the file's line count after the trim, and for every line over 200
   names the block responsible and why it stayed, referring to the must-stay list above. Under
   decision 7 the count is recorded, not gated.
3. **Union proof.** The probe record carries one row per moved block: its heading, its byte
   count, its new file, and the operative rule it carries, with every rule from the original
   block accounted for in exactly one destination. No rule is dropped and none is silently
   reworded.
4. **Trigger proof, one probe per moved block.** For a path-scoped rule, a `claude -p` run that
   reads a file matching the rule's `paths:` and is asked to state the rule's operative fact
   returns that fact; the same prompt with the rule file temporarily renamed does not. For a
   skill, a `claude -p` run using the trigger phrasing from the skill's own description shows the
   skill invoked. Both transcripts, or the relevant excerpt, land in the probe record.
5. **Rules-directory load proof** (decision 6). A probe confirms that a rule under the
   stow-symlinked `~/.claude/rules/` loads in a terminal session. If it does not, the task
   switches to real files with a `.stow-local-ignore` entry, records the switch, and adds the
   manifest line.
6. `claude/.claude/docs/claude-tooling.md`'s Layout table carries a `rules/` row naming where
   rules live, their manifest, and what applies them, and any new skill is recorded per that
   file's own "every addition gets three lines" rule.
7. `bash ~/.dotfiles/scripts/check.sh` exits 0 and `claude-tooling-sync verify` reports no drift.

**Gate:** `bash ~/.dotfiles/scripts/check.sh`, then `claude-tooling-sync verify`, both through
`cairn-run-gate '<string>'` with the exit-75 reattach protocol.

**Commit:** one commit on `~/.dotfiles` `main`, message `Restructure the workstation CLAUDE.md
into path-scoped rules and skills`, naming the byte and line delta and every moved block. Commit
the named files, never `git add -A`.

**Report must name:** what a session in another repo sees differently after this commit, every
block ruled keep against the candidate table, and any probe that had to be redesigned.

---

### Task 1b: The cairn `CLAUDE.md` restructure

**Chain:** B, first. **Repo:** `~/Projects/cairn-cms`, a worktree off `main`.
**Independent of:** tasks 1a, 2, 4. **Deliverables:** 3 (the trimmed file, the new rules, the
probe record).

**Outcome.** cairn's `CLAUDE.md` carries durable orientation and the charter boundary only.
Repo-specific domain knowledge reaches the session that needs it through `.claude/rules/*.md`
with `paths:` frontmatter, per decision 1, and every moved block's trigger is stated and proved.

**Files:**

- Modify: `CLAUDE.md`
- Create: `.claude/rules/*.md`, one per moved block, each with `paths:` frontmatter
- Modify: `.gitignore` if needed, so `.claude/rules/` is tracked while `.claude/agent-memory/`,
  `.claude/worktrees/`, and `.claude/settings.local.json` stay ignored
- Create: `docs/internal/record/2026-09-19-claude-md-restructure-probes.md`

**Blocks that must stay inline.** What cairn is, the canonical-scope section, because it
adjudicates any scope question and a scope question can arrive with no file read. The one-line
pointer at `engine-consult` and `docs/internal/engine-rulings.md`. The "How to run this project"
orientation paragraph naming the functional spec, `docs/STATUS.md`, and the `cairn-pass` skill.
Most of Authoring, because the TSDoc contract and the Vale layering govern every file the repo
writes. Trimming prose inside these is allowed; moving them is not.

**Candidate blocks to move, measured, with the trigger each would fire on.**

| Block | Lines | Bytes | Proposed home | Trigger (`paths:`) |
| --- | --- | --- | --- | --- |
| Documentation is a pass dimension | 48 | 3,584 | `.claude/rules/docs.md`, with 4 lines kept inline: docs are a pass dimension, the four arms exist, the narrative freeze, and `check:reference` plus `check:facts` gate | `docs/**/*.md` |
| The four durable-gotcha sections | 38 | 2,638 | `.claude/rules/gotchas.md`, or one rule per gotcha | `examples/showcase/**`, `e2e/**`, `scripts/build/**`, `src/lib/email.ts`, `wrangler.jsonc`, `playwright.config.*` |
| Releases (cadence and scheme) | 31 | 2,166 | the existing `cairn-release` skill, with 4 lines kept inline: a pass never bumps or publishes, the two cut triggers, SemVer not CalVer, verify the next number is free | `CHANGELOG.md`, `package.json` |
| Visual work | 26 | 2,004 | `.claude/rules/visual.md`, with 3 lines kept inline naming `visual-fidelity`, the one-check rule, and the five-viewport bar | `e2e/**`, `src/lib/components/**`, `examples/**` |
| Watch items | 20 | 1,362 | `.claude/rules/watch-items.md` | `ROADMAP.md`, `docs/STATUS.md`, `scripts/checks/**` |
| Diagnosing a running site | 19 | 1,251 | 3 lines inline (logs first, the vocabulary lives in `docs/reference/log-events.md`, a new diagnosable path earns an event), the symptom mapping to that reference page | the inline stub's pointer |
| Tooling for the rebuild | 28 | 1,940 | the `cairn-pass` skill, which every pass invokes at start | the skill's own trigger |
| Credentials | 12 | 735 | a one-line pointer at `~/.dotfiles/secrets/registry.md`, already ruled candidate 1 by `2026-09-08-claude-md-displacement-candidates.md` | none needed |
| Admin interface design | 9 | 731 | `.claude/rules/admin-design.md` | `src/lib/components/**/*.svelte`, `src/lib/**/*.css` |
| Pointing a consumer at unreleased engine work | 10 | 524 | `.claude/rules/link-consumer.md` | `scripts/**`, `examples/**` |
| The extending-developer lens | 11 | 809 | one 3-line inline block, the persona and the seam list to `docs/internal/extending-developer-lens.md`, which it already names | the inline stub's pointer |

Shedding 1,508 bytes needs one row. Reaching 200 lines needs roughly the first four.

**Acceptance criteria.**

1. `claude-context-budget ~/Projects/cairn-cms/CLAUDE.md` exits 0, run from the worktree path
   and from the main path after merge.
2. The line count is recorded, with every line over 200 attributed to a must-stay block.
3. **Union proof**, the same shape as task 1a criterion 3, in the record file.
4. **Trigger proof**, one probe per moved block, the same shape as task 1a criterion 4, run with
   the worktree as the working directory so the project rules resolve.
5. The three ignored `.claude/` paths stay ignored and `.claude/rules/*.md` is tracked:
   `git check-ignore -v` on each of the four confirms it.
6. cairn's `CLAUDE.md` still states, in one place, that `docs/STATUS.md` is the rolling status
   and `docs/HISTORY.md` the per-pass ledger. The restructure may not orphan the ledger rule.
7. A fresh-session cold-start test: a `claude -p` run in the worktree, given only the first task
   this plan's chain B would run next, produces a first move consistent with the rules the task's
   own file paths load. The transcript excerpt is recorded.

**Gate:** the cairn gate for the touched surface through `cairn-run-gate '<string>'`:
`npm run check:docs`, `npm run check:vale`, `npm run check:arm-indexes`, and `npm run
check:rulings-format`, plus `scripts/checks/gate-tier.mjs` for the tier this change lands in.
Serialize on the machine lock; one full gate at a time.

**Commit:** one commit on the worktree branch, message `Restructure cairn's CLAUDE.md into
path-scoped rules`, naming the byte and line delta and every moved block.

**Report must name:** each block ruled keep with its reason, whether `.claude/` becoming tracked
required a `.gitignore` change, and any probe whose `paths:` pattern had to be widened.

---

### Task 2: Split `go-conventions` and `elm-conventions` under 500 lines

**Chain:** A, second. **Repo:** `~/.dotfiles`, the real checkout.
**Independent of:** tasks 1a, 1b, 3, 4. **Deliverables:** 3 (the two splits, and the two
vestigial removals below).

**Outcome.** Each SKILL.md body is under 500 lines and carries the gate, the rubric, and the
shape rules. The exemplar catalogues and the config copy-ins live in a `references/` directory
that SKILL.md lists by name and purpose, and no rule is lost in the move.

**Files:**

- Modify: `claude/.claude/skills/go-conventions/SKILL.md` (592 lines today)
- Create: `claude/.claude/skills/go-conventions/references/*.md`
- Modify: `claude/.claude/skills/elm-conventions/SKILL.md` (582 lines today)
- Create: `claude/.claude/skills/elm-conventions/references/*.md`
- Create: `docs/record/2026-09-19-skill-split-union.md`, the union proof

**Constraints.**

- Anthropic's skills doc names the layout as supporting files the SKILL.md lists by name and
  purpose. This task uses a `references/` directory, and SKILL.md carries an "Additional
  resources" section naming each file and when to load it. A reference file is never loaded
  eagerly.
- **What stays in SKILL.md:** the mandatory-invocation statement, the gate or Makefile targets,
  the anti-pattern rubric, the naming and error-wrapping rules, the comment standard pointer,
  and for `elm-conventions` the numbered rule headings themselves. A rule's heading and its
  one-line statement stay; its worked example and its long code listing move.
- **What moves:** the long code listings, the exemplar catalogues, the copy-in configs, and the
  per-rule before-and-after pairs.
- Neither skill's `description` or `when_to_use` changes meaning. A trigger that fires today
  still fires.

**Acceptance criteria.**

1. `wc -l` on each SKILL.md is under 500.
2. **Union proof, mechanical.** `docs/record/2026-09-19-skill-split-union.md` carries, per skill,
   a list of every rule and every named heading in the pre-split file, each mapped to its
   post-split location, generated by comparing the pre-split file at its git blob against the
   post-split tree. Every entry resolves to SKILL.md or to a named `references/` file. An
   unmapped entry fails the task.
3. Each SKILL.md's "Additional resources" section names every file in its `references/`
   directory, and every file in that directory is named in that section. No orphan file and no
   dangling link.
4. A `claude -p` probe per skill: the skill's own trigger phrasing invokes it, and a question
   whose answer now lives only in a `references/` file gets the right answer, proving the
   pointer is followed.
5. `uv run ... pytest tests/ -q` for `vale-hook` still passes (its `MultiEdit` branch was
   removed before this plan; nothing here reopens it).
6. `bash ~/.dotfiles/scripts/check.sh` exits 0 and `claude-tooling-sync verify` reports no drift.
   Both skills are authored, not vendored, so `verify` confirms the vendored manifest is
   unaffected rather than checking the split itself.

**Gate:** `bash ~/.dotfiles/scripts/check.sh`, then `claude-tooling-sync verify`.

**Commit:** one commit, message `Split go-conventions and elm-conventions under 500 lines`,
naming the before and after line counts and the two vestigial removals.

**Note on scope.** Three deliverables, disclosed at dispatch. The two vestigial removals join
this task because they are one-line deletions in the same repo behind the same gate, and the
`vale-hook` deletion needs that gate's pytest suite either way.

---

### Task 3: The Vale layer, current and recorded

**Chain:** B, second. **Repo:** `~/Projects/cairn-cms`, the same worktree off `main`.
**Independent of:** tasks 1a, 1b, 2, 4. **Deliverables:** 4 (the package re-sync, the version
record, the CI and feed repoints, the triage record).

**Outcome.** cairn's vendored Google and Microsoft packages match the current hub releases, their
versions are recorded beside `Packages =`, CI runs a current Vale, no vendored feed points at a
renamed org, and every new finding over the whole corpus carries a fix, downgrade, or off ruling
with a reason.

**Procedure.** This is a dependency bump, so it runs through the `dependency-upgrade` skill: the
survey precedes the take, every new capability gets a take-now, file, or refactoring-pass ruling,
and the record is a dated file under `docs/internal/record/`. The Vale style packages are the
dependency; the five new rules are the new capability.

**Measured inputs, already read, so the survey extends rather than rediscovers them.**

- Current hub releases, read via `gh api` on 2026-09-19: Google **v0.7.1** (2026-08-04),
  Microsoft **v0.15.1** (2026-08-04). Current Vale: **v3.22.0** (2026-09-17).
- cairn's vendored Google carries 31 rules; the current package carries 36. Microsoft matches at
  47 and needs no rule additions, though its version is still unrecorded.
- The five missing Google rules, by file: `Anthropomorphism.yml`, `ExcessiveClaims.yml`,
  `Jargon.yml`, `Timeless.yml`, `WordListCase.yml`. Upstream tiers: `suggestion` for the first
  four, `warning` for `WordListCase`.
- `npm run check:vale` gates at `--minAlertLevel=error` over `docs README.md
  examples/showcase/README.md`, so none of the five fires at the gate at stock tier. cairn's
  `.vale.ini` sets `MinAlertLevel = suggestion`, so all five reach the `vale-hook` on save.
- The `errata-ai/*` release feeds in both vendored `meta.json` files redirect; `vale-cli/Google`
  and `vale-cli/Microsoft` answer 200 directly. The org was renamed. `test.yml`'s Vale download
  URL also names `errata-ai`.
- `~/.config/vale/styles` on this machine already carries 36 Google rules and 47 Microsoft rules,
  which is the verification oracle per decision 8. Its Google `meta.json` still carries the old
  feed, so the feed fix applies there too.

**Files:**

- Modify: `.vale/styles/Google/*` (the five additions, plus any changed existing rule)
- Modify: `.vale/styles/Google/meta.json`, `.vale/styles/Microsoft/meta.json`, the feed URLs
- Modify: `.vale.ini`, recording both package versions beside `Packages =` and preserving the
  version-arbiter comment with its pin updated
- Modify: `.github/workflows/test.yml`, the Vale pin and its download URL
- Modify: `~/.dotfiles/vale/.config/vale/.vale.ini` and the machine-local `meta.json` feeds, so
  the two corpora on this machine do not diverge again. This is a chain A repo, so it lands as a
  separate commit under task 5's dotfiles half if chain A has already closed; otherwise task 3
  reports it and task 5 takes it.
- Modify: `~/.dotfiles/claude/.claude/skills/vale-ci/SKILL.md`, the pre-commit `rev` example, if
  the SMALL tier did not already bump it. Verify first; take it only if it still reads v3.17.0.
- Create: `docs/internal/record/2026-09-19-vale-resync.md`, the survey and triage record

**Acceptance criteria.**

1. `.vale/styles/Google` carries 36 rules and `.vale/styles/Microsoft` 47, and a byte diff of
   each against a fresh `vale sync` of the same release is empty.
2. `.vale.ini` records `Google v0.7.1` and `Microsoft v0.15.1` beside `Packages =`, with the
   date read and the command that read it.
3. Neither vendored `meta.json` names `errata-ai`, and each recorded feed returns 200 without a
   redirect.
4. `test.yml` installs Vale v3.22.0 from a `vale-cli` URL, and the version-arbiter comment in
   `.vale.ini` names the new pin rather than 3.15.1.
5. `npm run check:vale` exits 0. The gate tier is unchanged by this task, which is the point of
   decision 3.
6. **Full-corpus triage.** `vale --minAlertLevel=suggestion` over the same paths `check:vale`
   covers, plus `docs/editors/**`, is run before and after. The record enumerates every new
   finding grouped by rule, with a count, and gives each rule one ruling of fix, downgrade, or
   off through the `vale-triage` skill's decision, with a recorded reason. A rule left at stock
   tier is an explicit "take as-is" ruling with its count, never an omission.
7. The survey and refactor-decision shape the `dependency-upgrade` skill requires is present: the
   before and after table, the per-capability ruling, and any filed item as a `ROADMAP.md` line.
8. `~/.dotfiles/tests/vale/run-fixtures.sh` still passes on this machine, so the dotfiles fixture
   and the re-synced packages agree.

**Gate:** through `cairn-run-gate '<string>'`: `npm run check:vale`, `npm run check:docs`, and
the `gate-tier.mjs` tier for a docs and config change. One full gate at a time.

**Commit:** one commit on the worktree branch, message `Re-sync the Vale style packages and bump
the CI pin`, naming both package versions, the five added rules, and the triage rulings.

**Report must name:** every rule whose ruling was anything other than take-as-is, the dotfiles
half if it was not taken here, and whether any existing vendored rule changed in the re-sync.

---

### Task 4: The style and linter watcher routine

**Chain:** A, third. **Repo:** `~/.dotfiles`. **Independent of:** tasks 1a, 1b, 2, 3.
**Deliverables:** 2 (the routine, its registration).

**Outcome.** One scheduled cloud routine watches the external triggers this pass just satisfied
and pings only on a delta, so the next drift arrives as a notification rather than as another
audit.

**Procedure.** Created through the `schedule` skill, which is a built-in and is not a file on
disk. The implementer invokes it and does not hand-write a cron entry.

**Sources the routine checks.** Four, per decision 4:

1. Google's developer-documentation whats-new page, https://developers.google.com/style/whats-new,
   which carries a dated changelog and revises roughly monthly.
2. Vale's releases, `gh api repos/vale-cli/vale/releases/latest`, compared against the pin
   recorded in cairn's `.vale.ini`.
3. The two hub package releases, `gh api repos/vale-cli/Google/releases/latest` and the
   Microsoft equivalent, compared against the versions task 3 recorded beside `Packages =`.
4. The Claude Code docs changelog, compared against the last-checked marker the routine keeps.

**Registration.** Mirror the shape of the existing monthly Cloudflare capability-review routine,
which is recorded in two places and read by the routine itself:

- `~/Projects/cairn-cms/ROADMAP.md` carries the watched list under an exact heading the routine
  reads by name, the pattern "Platform watch: Cloudflare" set.
- `~/Projects/cairn-cms/docs/STATUS.md`, under "Active watches", carries one line naming the
  routine's trigger id and what it reads.

This routine's watched list is a workstation concern, not a cairn one, so its list lives in
`~/.dotfiles/docs/STATUS.md` under an exact heading, with the STATUS line naming the trigger id.
Keep the pair: a heading the routine reads by name, and a STATUS line naming the id.

**Files:**

- Modify: `~/.dotfiles/docs/STATUS.md`, the watched-source list under its own exact heading, plus
  an "Active watches" line naming the trigger id
- Modify: `~/.claude/docs/claude-tooling.md`, one line recording the routine as a workstation
  piece with its id

**Acceptance criteria.**

1. The routine exists and its id is recorded. `claude` routine listing shows it with its cron
   schedule.
2. A manual run of the routine against the current state produces **no ping**, because task 3
   just made every version current. A ping on a no-delta run is a false positive and fails the
   task.
3. A manual run with one recorded version deliberately stale, reverted afterward, produces a ping
   that names the source, the recorded version, and the current version. The transcript excerpt
   lands in the commit message or the STATUS line's supporting record.
4. `~/.dotfiles/docs/STATUS.md` carries the exact heading the routine reads by name, and the
   routine's prompt names that heading and that file path.
5. `bash ~/.dotfiles/scripts/check.sh` exits 0 and `claude-tooling-sync verify` reports no drift.

**Gate:** `bash ~/.dotfiles/scripts/check.sh`, then `claude-tooling-sync verify`.

**Commit:** one commit, message `Add a scheduled watcher for the style and linter sources`,
naming the trigger id, the four sources, and the schedule.

---

### Task 5: Close

**Chain:** neither. Conductor-led after chains A and B both report green, with one
`cairn-implementer` dispatch for the cairn half. **Deliverables:** 4.

**Outcome.** The audit carries a resolved ledger, the tooling inventory matches what moved, both
repos' ledgers are current per the workstation's three-file rule, and `check-drift` is green.

**Files:**

- Modify: `~/.claude/docs/record/2026-09-19-docs-infra-audit.md`, a "Resolved" section appended
- Modify: `~/.claude/docs/claude-tooling.md`, the inventory and Layout table for every artifact
  this pass moved or added
- Modify: `~/.dotfiles/docs/HISTORY.md`, one newest-first entry
- Modify: `~/.dotfiles/docs/STATUS.md`, present tense only, with the pass's carry-forwards
- Modify: `~/Projects/cairn-cms/docs/HISTORY.md` and `docs/STATUS.md` (the cairn half, dispatched)
- Modify: `~/Projects/cairn-cms/ROADMAP.md`, retiring the "CLAUDE.md sits over the 6000-token
  `claude-context-budget` hook" entry and filing audit finding 13 as a cairn-pub line

**Acceptance criteria.**

1. The audit's resolved ledger carries one row per finding in this plan's scope (1, 3, 4, 5, the
   two vestigial items, 13) with its disposition, the commit that closed it, and for anything not
   closed the reason and where it is now filed. Findings the SMALL tier closed are listed as
   landed-before with their commits, verified by reading the commits rather than assumed.
2. `claude-tooling.md`'s Layout table and inventory name every artifact this pass created: the
   `rules/` directories in both repos, each new skill, the `references/` directories, and the
   watcher routine with its id.
3. `~/.dotfiles/docs/STATUS.md` is present tense and at most 60 lines. Anything past tense moved
   to `HISTORY.md` rather than being deleted.
4. The cairn ROADMAP entry that ruled the trim "a dedicated trim task with its own
   `diff-reviewer` read" is marked done and removed from the live tiers, and finding 13 is one
   cairn-pub line in the tier where it bites.
5. `check-drift` exits clean, including the `claude-tooling-sync verify` it runs.
6. The cairn half lands by PR off the worktree branch onto `main`, merged before this task
   closes, with CI green. No direct write to the cairn main checkout.
7. `claude-context-budget` on both `CLAUDE.md` files exits 0 from their post-merge paths, the
   pass's headline result re-proved after every merge.

**Gate:** `bash ~/.dotfiles/scripts/check.sh` and `check-drift` for the dotfiles half; the cairn
tier gate plus CI for the cairn half.

**Commit:** one commit per repo. Dotfiles: `Close the docs-infra currency pass`. cairn: `Record
the docs-infra currency pass in the ledgers`. One independent `diff-reviewer` read over the
close's diff.

---

## Task ledger

| Task | Chain | Repo | Size | Independent of | Status |
| --- | --- | --- | --- | --- | --- |
| 1a, workstation `CLAUDE.md` | A | `~/.dotfiles` (real checkout) | large | 1b, 3 | not started |
| 1b, cairn `CLAUDE.md` | B | cairn worktree | large | 1a, 2, 4 | not started |
| 2, the two skill splits | A | `~/.dotfiles` | medium | 1a, 1b, 3, 4 | not started |
| 3, the Vale layer | B | cairn worktree | medium-large | 1a, 1b, 2, 4 | not started |
| 4, the watcher routine | A | `~/.dotfiles` | small | 1a, 1b, 2, 3 | not started |
| 5, close | neither | both | small-medium | depends on all | not started |

## Audit coverage

| Finding | Task | Note |
| --- | --- | --- |
| 1, both `CLAUDE.md` over budget | 1a, 1b | one task per file, each with its own `diff-reviewer` read, per the cairn ROADMAP ruling |
| 2, missing `.tellgrader.json` | none | landed before this plan |
| 3, the two over-length skills | 2 | |
| 4, the Vale packages and CI pin | 3 | |
| 5, no scheduled watcher | 4 | |
| 6, `user_invocable` frontmatter | none | landed before this plan |
| 7, `context: fork` | none | assumed landed; decision 5, verified in 1a and 5 |
| 8, agent `skills:` key | none | assumed landed; decision 5, verified in 1a and 5 |
| 9, retired URLs and the two best practices | none | URL half landed; the reviewer-scope tightening is one line in `prose-voice-reviewer`, verified in task 5 |
| 10, charter "Build state" | none | landed before this plan |
| 11, cairn Authoring sentence | none | landed before this plan |
| 12, `vale-ci` pre-commit `rev` | 3 | verified first, taken only if still stale |
| 13, llms.txt, hedged against | 5 | filed as a cairn-pub ROADMAP line, no docs-standard change |
| vestigial, `vale-hook` `MultiEdit` and the `tellgrader` register home | 2 | |

## Risks

- **A live-surface mistake in chain A breaks every session on the machine.** Task 1a rewrites the
  file every session loads. Mitigation: the probes are the acceptance criteria, the commit is one
  revert away, and the task runs first in its chain so a failure is caught before tasks 2 and 4
  build on it.
- **A path-scoped rule with a trigger that never fires is worse than the inline block.** The rule
  is invisible and the session proceeds without it. Mitigation: criterion 4 of tasks 1a and 1b is
  a per-block trigger probe with a negative control, and a block whose probe cannot be made to
  pass stays inline with that recorded as its ruling.
- **The Vale re-sync can move findings on published docs inside a release window.** Mitigation:
  decision 9's recommendation puts the pass after the cut. If Geoff rules before-the-cut, task 3
  reports its corpus delta before the triage so the cut can wait on it.
- **The 200-line target may not be reachable without cutting a rule that earns its place.** The
  must-stay lists exist to make that visible rather than to lose an argument quietly. Under
  decision 7 the residue is recorded and routed, and the hook stays the hard line.
- **Two executors in one checkout.** Chain A runs in the real `~/.dotfiles`, which is the same
  checkout a stray inline edit would touch. Before dispatch: `pgrep -f dotfiles`, `git -C
  ~/.dotfiles status`, and a read of `~/.dotfiles/docs/STATUS.md`. Warm uncommitted changes are a
  stop-and-investigate signal.

## Self-review

Audit coverage is the table above, one row per finding, with the landed tier called out rather
than re-planned. No task carries a TBD, a "handle edge cases", or a "similar to task N"; the two
`CLAUDE.md` tasks repeat their criteria in full because they will be read by separate
implementers who see only their own task. The names each task hands the next are consistent: the
probe record paths, `claude-context-budget`, `cairn-run-gate`, `claude-tooling-sync verify`, and
`check-drift` appear with the same spelling throughout. The one cross-task name to watch is
task 3's dotfiles half, which may land in task 3's report or in task 5's dotfiles commit; both
tasks name that fork explicitly.
