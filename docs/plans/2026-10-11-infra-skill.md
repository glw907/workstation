# Infrastructure skill and proportionality rules: implementation plan

**Design:** `docs/superpowers/specs/2026-10-11-infra-skill-and-proportionality-design.md`, approved
by Geoff 2026-10-11 (under a page, so no separate spec), with Geoff's amendment item 3a (the
`plan-reviewer` agent, `fe26a9b`), which T2 builds. **Evidence:**
`docs/superpowers/research/2026-10-11-anthropic-guidance-proportionality.md` (cited below as
"research"). **Review:** the mechanics lens and its fold record,
`docs/superpowers/research/2026-10-11-infra-skill-plan-{review-mechanics,fold}.md`.

**Outcome.** A session that changes local Claude Code infrastructure loads a `claude-infra` skill
that sends it to Anthropic's guidance first and to the strongest home for each rule. `pass-core`
carries Anthropic's anti-over-engineering prompts verbatim, takes risk class from the path map, and
sends an over-budget plan back to Geoff. `spec-plan-review` tags findings, scales its depth to
the design's size, and dispatches a `plan-reviewer` agent for the mechanics lens. A hook denies a gate or CI-watch command piped into `tail` or `head`. The gate
warns when a branch changes Claude infrastructure without citing Anthropic. The global `CLAUDE.md`
gets shorter.

**Pass class:** `runner` (the design's class, from the dotfiles-pass path map: every task touches
`claude/.claude/skills/**`, `claude/.claude/settings.json`, `scripts/**`, or `tests/**`). No task
touches an `auth-data` path: the tail guard is a new hook script, not an edit to `claude-block-op`
or `claude-secret-guard`, which the path map classes `auth-data`. No `live-account` flag: the
design names none, and Geoff's approval set this plan's review at the mechanics lens. Pushing the
branch and opening the PR on `glw907/workstation` is the standard close. (Sweep 1 flagged that same
act `live-account`; the "Later" list carries the question.)

**Scope.** Every planning and executing dispatch for this pass applies Anthropic's own words, which
the design adopts: "Avoid over-engineering. Only make changes that are directly requested or
clearly necessary. Keep solutions simple and focused: - Scope: Don't add features, refactor code,
or make "improvements" beyond what was asked. A bug fix doesn't need surrounding code cleaned up. A
simple feature doesn't need extra configurability. ... - Defensive coding: Don't add error handling,
fallbacks, or validation for scenarios that can't happen. Trust internal code and framework
guarantees. Only validate at system boundaries (user input, external APIs). - Abstractions: Don't
create helpers, utilities, or abstractions for one-time operations. Don't design for hypothetical
future requirements. The right amount of complexity is the minimum needed for the current task."
And: "Deliver what was asked, at the scope intended. ... If the request seems mistaken or a better
approach exists, say so in a sentence and continue with the task as asked rather than quietly
narrowing, widening, or transforming it." Anything beyond the design goes in "Later", never into a
task.

**Out of scope** (design): any change to another repo, and any rewrite of `pass-core` beyond the
lines T2 names. The design's own "Later, not built here" list stays unbuilt.

**Readings taken.** Four places where the design leaves a detail open, each settled by the nearest
existing text:

1. The research record carries no suggested trigger text for the skill's description. T1 draws the
   description from the design's own trigger prompts and the skills page's create-a-skill line.
2. `pass-core` steps 2, 3, and 4 restate the spec and review depth that design item 3 changes.
   Step 2 gains one clause (a spec is written only when `spec-plan-review`'s depth calls for one),
   and the depth sentences in steps 3 and 4 become pointers to `spec-plan-review`, so the skills
   cannot disagree on every pass. This is the only `pass-core` text T2 touches beyond the design's
   three edits.
3. The design keeps "the three lenses and the verification read" for `auth-data` and
   `live-account` passes and says a plan otherwise gets the mechanics lens only. It says nothing new
   about a spec on other passes. T2 keeps the three lenses and the fold for any spec and drops the
   verification read from it outside `auth-data` and `live-account`, per the Opus 5 guidance against
   separate verification steps.
4. "Hooks" in design item 5 reads as `claude/.claude/settings.json`, which wires every hook. The
   hook scripts themselves live in `bin/.local/bin/`; a change to one alone goes unwarned ("Later").

**End-to-end check** (design). On the close head:

1. `bash scripts/gate.sh` prints `gate exit: 0`.
2. `tests/test_claude_tail_guard.py` (run by the gate's pytest leg) shows the hook denying
   `cairn-run-gate 'bash scripts/check.sh' | tail -5` and allowing the bare command and a redirect
   to a file.
3. T1's trigger table shows `claude-infra` triggering on all three should-trigger prompts and on
   neither should-not prompt.
4. `wc -l claude/.claude/CLAUDE.md` prints fewer than 199 lines, and T2's line count for `pass-core`
   holds (growth no larger than the quoted prompts).

**Clock estimate:** 270 task-minutes (T1 70, T2 50, T3 55, T4 45, close 50), under the design's
tripwire of 360. The two pairs run in turn, so the path is about 70 + 55 + 50 = 175 minutes.

## Launch

Prompt file: `docs/superpowers/plans/2026-10-11-infra-skill-prompt.txt`. The plan lives on branch
`worktree-infra-skill-plan`, which already carries the design branch `worktree-infra-skill`. The
executing session continues it: its first act after `EnterWorktree` is `git merge --no-edit
worktree-infra-skill-plan`, so its PR carries the design, the plan, and the build. Its worktree
name is `infra-skill-build`, because the name `infra-skill` already holds the design branch
`worktree-infra-skill`. Launch from the main checkout, after every check prints what its comment
names:

```bash
git -C ~/.dotfiles fetch origin
git -C ~/.dotfiles branch --show-current                # must print main
git -C ~/.dotfiles rev-list --count HEAD..origin/main   # must print 0 (not behind)
git -C ~/.dotfiles rev-list --count origin/main..HEAD   # must print 0 (not ahead)
git -C ~/.dotfiles status --porcelain                   # must print nothing
git -C ~/.dotfiles/.claude/worktrees/infra-skill-plan status --porcelain   # must print nothing
git -C ~/.dotfiles rev-parse worktree-infra-skill-plan origin/worktree-infra-skill-plan   # two equal lines
claude agents --json                                    # no live session with cwd in ~/.dotfiles/.claude/worktrees/infra-skill-build
cd ~/.dotfiles && claude --bg --model sonnet --effort medium --name infra-skill-build \
  "$(git -C ~/.dotfiles show worktree-infra-skill-plan:docs/superpowers/plans/2026-10-11-infra-skill-prompt.txt)"
```

The prompt is read with `git show` because the plan is not on `main` until this pass's PR merges.
The ahead check matters because `worktree.baseRef: "head"` branches from local `HEAD`.

## Conventions every task follows

- **Gate.** `bash scripts/gate.sh`, with the Bash tool's `timeout: 600000`, re-issued on exit 75
  until it prints `gate exit:`. It is also the fast lane. A focused leg (`uv run --with pytest
  --no-project python -m pytest tests/test_claude_tail_guard.py -q`, or one test script) may run
  between edits; the task's acceptance is the gate.
- **The main checkout stays untouched.** Every tool runs from the worktree's own path
  (`bin/.local/bin/<tool>`, `scripts/<tool>`), never as a bare name: `~/.local/bin/<tool>` is a stow
  link to the main checkout's copy. No command writes `~/.dotfiles` outside `.claude/worktrees/`.
  The new hook and skill go live only when the PR merges; nothing in this pass stows or installs.
- **Commits.** One commit per task, subject starting with the task id (`T1: Add the claude-infra
  skill`), imperative mood, specific files only. A commit that touches `claude/.claude/skills/`,
  `claude/.claude/agents/`, `claude/.claude/settings.json`, or `claude/.claude/CLAUDE.md` names in
  its body the Anthropic page it follows, as a full URL (for example
  `https://code.claude.com/docs/en/skills`). T4's warning reads those bodies.
- **Citations.** Every quote placed in a skill or doc is copied from the research record, which
  quotes each page verbatim, and carries that page's URL. Nothing is quoted from memory.
- **Clock.** At each pair's start the session writes `pass-task-clock` in its own pass worktree's
  git dir (`git rev-parse --absolute-git-dir`) with `task=<ids>`, `start=<epoch>`,
  `estimate=<minutes>` (`task=T1+T2`, `estimate=70`; then `task=T3+T4`, `estimate=55`), checks the
  overrun when both halves return, and removes the file (pass-core "Clock stop"). The close writes
  its own file (`task=close`, `estimate=50`). Pair worktrees hold no clock file, and the pair
  subagents write none.
- **Stops.** A red the session cannot fix in two attempts, a merge conflict, a clock stop, or T1's
  trigger check missing twice: write `docs/STATUS.md` on the branch (task in flight, what failed,
  the one question), run `notify-send -u normal "infra skill: stopped"`, and wait. A pair subagent
  that hits one of these returns its work to the session uncommitted, with the evidence (for T1,
  the trigger table), and the session applies this rule before merging either half of the pair.
- **Scope.** A defect found outside a task goes to the PR body's "Found, not done" list. A pair
  subagent lists such defects in its final report, and the session carries them to the PR body.

## Tasks

### T1. The `claude-infra` skill, replacing CLAUDE.md and `claude-tooling.md` text

- **Outcome.**
  - A new authored skill, `claude/.claude/skills/claude-infra/SKILL.md`, about 60 lines of
    procedure plus the rules moved into it, under 120 lines in all. Its frontmatter has `name:
    claude-infra` and a `description` under 500 code points that triggers on adding or changing a
    rule, hook, skill, agent, workflow, `CLAUDE.md` text, `settings.json`, MCP server, plugin, or
    the pass process on this workstation. The description draws on the design's trigger prompts and
    the skills page line "Create a skill when you keep pasting the same instructions, checklist, or
    multi-step procedure into chat, or when a section of CLAUDE.md has grown into a procedure
    rather than a fact."
  - Its procedure is design item 1, as a numbered list:
    1. Cite the Anthropic page the change follows, and prefer a built-in.
    2. Choose the strongest home: hook, then skill or agent, then CLAUDE.md. It quotes the
       features-overview lines from the research ("If a rule must hold every time, make it a hook
       rather than a prompt instruction"; "Put it in a skill if it's reference material Claude
       needs sometimes").
    3. Keep one home per rule, with its manifest, pointing at `claude-tooling.md`'s "Layout" table
       for which manifest.
    4. Trace scope to a stated need, with the two sample prompts quoted verbatim from the research
       ("Avoid over-engineering ..." and the Opus 5 "Deliver what was asked ..." paragraph, each as
       the research quotes it, its `...` elisions kept).
    5. Land the change through a PR whose commit messages and body cite the guidance URL.
    6. Audit with `/doctor prompt-audit`, `/skill-doctor`, and Anthropic's `skill-creator`, named
       and pointed to, never restated.
  - The text it replaces moves into it. Every sentence of global `CLAUDE.md`'s "A rule lives where
    it executes" section lands in the skill (the record routing and "Act on a tool's NOTE before
    the next dispatch" included). That section's body becomes one line pointing at the skill; the
    heading stays. `claude-tooling.md`'s "Rules" bullet list moves into the skill, and its place
    becomes one line pointing at the skill. The "Model pins" and `worktree.baseRef` paragraphs that
    follow the bullets stay in `claude-tooling.md` under a heading that names them ("Model pins").
  - Two pointer fixes, needed because the text moved: the global `CLAUDE.md` "Claude tooling" line
    "layout and rules in `~/.claude/docs/claude-tooling.md`" names the skill for the rules, and
    `claude-tooling.md`'s inventory line for `spec-plan-review` (now "the three lenses, probing
    fold, and verification read every spec or plan takes") says its depth scales with the design's
    size and that it dispatches the `plan-reviewer` agent, matching T2. The "Model pins" list of
    reviewer agents that name `claude-opus-5-5` gains `plan-reviewer`.
- **Files.** `claude/.claude/skills/claude-infra/SKILL.md` (new), `claude/.claude/CLAUDE.md`,
  `claude/.claude/docs/claude-tooling.md`.
- **Risk class.** `runner`.
- **Acceptance.**
  - `wc -l claude/.claude/CLAUDE.md` prints fewer than 199 lines; the skill is under 120 lines.
  - `grep -c "rule lives where it executes" claude/.claude/CLAUDE.md` prints 1 (the heading only),
    and `claude-tooling.md` has no bulleted rule left under a "Rules" heading.
  - `bin/.local/bin/claude-tooling-sync lint --root .` exits 0 (the gate runs it).
  - Trigger check, the mechanism sweep 1's T2 proved (commit `6a27ff2`). At task start, `mktemp -d
    /tmp/infra-skill-t1.XXXXXX` makes the scratch directory, its printed path written literally in
    every later command. Each prompt runs in a fresh session from its own subdirectory
    `<scratch>/<run>`, whose `.claude/skills/` holds a copy of the skill under test beside copies
    of `pass-core` (`claude/.claude/skills/pass-core/`) and `dotfiles-pass`
    (`.claude/skills/dotfiles-pass/`), so the run measures the competition a real session has.
    `--setting-sources project` hides the personal and plugin skills; the bundled ones,
    `update-config` among them, stay visible (review probe).
    Each run is one plain command, `cd <scratch>/<run> && timeout 180 claude -p --model sonnet
    --setting-sources project --output-format stream-json --verbose "<prompt>" >
    <scratch>/<run>.jsonl`, with no pipe, no heredoc, and no inline script. A separate step counts
    triggers with `grep -c '"name":"Skill","input":{"skill":"claude-infra"' <scratch>/<run>.jsonl`.
    - Should trigger: "Add a rule that every pass plan names its rollback step."; "Make a hook for
      blocking git push --force in every session."; "Change the pass process so a plan with two
      tasks skips the clock file."
    - Should not trigger: "Write a Python function that parses an ISO 8601 date. Reply with the code
      only."; "Fix the spelling in this sentence: We recieve mail daily."
    - All three should-trigger prompts trigger and neither should-not prompt does. One reword of the
      description is allowed. A second miss is a stop. The result, one row per prompt, goes in T1's
      commit body, and the session copies it into the PR body.
  - The gate prints `gate exit: 0`.
- **Test.** The trigger check above. The gate's ratchet leg covers the moved text's references
  (`dead-reference`, `relative-link`) and its description (`description-cap`).
- **Pair.** Runs as a pair with T2 (disjoint files).
- **Estimate.** 70 minutes.

### T2. `pass-core` and `spec-plan-review` edits, and the `plan-reviewer` agent

- **Outcome.**
  - `pass-core`, "Lifecycle" opening paragraph: "The design's class is a floor" becomes a task's
    class from the adapter's path map, raised only by Geoff's ruling, which the design states in one
    sentence. "A pass takes its highest task's class" stays.
  - `pass-core` step 1, Design: the two sample prompts from the research go in verbatim as one
    quote block ("Avoid over-engineering ..." and the Opus 5 "Deliver what was asked ..."
    paragraph, each as the research quotes it, its `...` elisions kept), each with its page URL.
    One sentence says every planning dispatch prompt carries them, and extras are listed as "Later"
    and never built.
  - `pass-core` step 4, Plan: one sentence of the estimate tripwire. A plan whose task-minutes
    exceed twice its design's estimate goes back to Geoff with the reason before launch.
  - `pass-core` steps 3 and 4: the sentences that state review depth ("runs three Opus lenses in
    parallel, then a probing fold and one verification read"; "Plan review runs the mechanics lens
    and a verification read; an `auth-data` or `runner` pass ... runs all three lenses") become
    pointers to `spec-plan-review` for depth. Step 2 gains one clause: a spec is written only when
    `spec-plan-review`'s depth calls for one. Reading 2 above.
  - `spec-plan-review`, findings: every lens reports everything and tags each finding as
    `correctness` (it affects correctness or a stated requirement) or `optional`. The fold drops
    the optional ones, in the best-practices page's words: "flag only gaps that affect correctness
    or the stated requirements, and treat the rest as optional." The dispatch ask and the fold
    section both say so.
  - `spec-plan-review`, depth: a design of a page or less needs no separate spec. A plan gets the
    mechanics lens and the fold only. The three lenses and the verification read are kept for
    `auth-data` and `live-account` passes. A spec otherwise takes the three lenses and the fold,
    with no verification read (reading 3). It cites the Opus 5 page's guidance against separate
    verification steps from the research. "The sequence", the "Depth scales" paragraph, and the two
    stale "Common mistakes" rows (the skipped verification read, the small-plan row) change to
    match; nothing else in the skill does, beyond the dispatch line below.
  - The `plan-reviewer` agent (design item 3a), `claude/.claude/agents/plan-reviewer.md`, about 40
    lines, in the shape of `diff-reviewer.md`'s frontmatter: `name: plan-reviewer`, a one-sentence
    `description` (every agent description takes up context), `tools: Read, Grep, Glob, Bash,
    WebFetch` (read-only, with Bash for probes and WebFetch for quoting docs), `model:
    claude-opus-5-5`, `effort: medium`. Its body is the mechanics lens prompt that
    `spec-plan-review` holds today (the lens row, the plan checklist, and the finding shape),
    plus the `correctness` or `optional` tag on every finding. It never edits a file: its report is
    its final reply. The body cites the two pages design item 3a quotes, with their URLs
    (`https://code.claude.com/docs/en/sub-agents`: "Define a custom subagent when you keep
    spawning the same kind of worker with the same instructions";
    `https://code.claude.com/docs/en/features-overview`), copied from the design.
  - `spec-plan-review` dispatches `plan-reviewer` for the mechanics lens in place of the retyped
    lens prompt, and the dispatching session saves its reply as
    `docs/superpowers/research/<date>-<target>-review-mechanics.md`. The skill keeps the procedure;
    the lens prompt lives in the agent alone. The agent adds no review (design item 3a).
- **Files.** `claude/.claude/skills/pass-core/SKILL.md`,
  `claude/.claude/skills/spec-plan-review/SKILL.md`, `claude/.claude/agents/plan-reviewer.md` (new).
- **Risk class.** `runner`.
- **Acceptance.**
  - `pass-core` growth: `wc -l` after the edit, minus 161, is no more than the number of lines
    starting with `>` (the quote block, its URLs included). The commit body records both numbers.
    The budget is tight (the review's draft grew 20 lines against a 17-line block), so the edits
    keep to it this way: the quote block follows step 1's last line with no blank line before it
    (a CommonMark block quote may interrupt a paragraph); the sentence introducing it and the
    "Later" sentence ride in step 1's existing lines; the risk-class, step 2, tripwire, and pointer
    edits net to zero lines, the pointers being shorter than the depth sentences they replace.
  - `git diff -- claude/.claude/skills/pass-core/SKILL.md` touches only the "Lifecycle" opening
    paragraph and steps 1 to 4.
  - `grep -n "verification read" claude/.claude/skills/pass-core/SKILL.md` prints nothing (depth now
    lives in `spec-plan-review` alone).
  - `spec-plan-review` names the tags `correctness` and `optional`, quotes the "flag only gaps"
    line with `https://code.claude.com/docs/en/best-practices`, and its depth paragraph states the
    four cases above.
  - `plan-reviewer.md` is under 50 lines, its frontmatter names no write tool (`Write`, `Edit`,
    `NotebookEdit`), and `spec-plan-review` names `plan-reviewer` where it dispatches the mechanics
    lens.
  - One live dispatch: from T2's worktree, an Agent-tool call with `subagent_type:
    "plan-reviewer"` on this plan (`docs/superpowers/plans/2026-10-11-infra-skill.md`) returns
    findings, each tagged `correctness` or `optional`, and leaves `git status --porcelain` empty.
    The agent file loads live through the folded `~/.claude/agents` link only after the merge, so
    this dispatch passes the agent's body as a `general-purpose` prompt with `model: opus`, effort
    `medium`, if `plan-reviewer` is not yet listed; the commit body says which form ran.
  - The gate prints `gate exit: 0`.
- **Test.** The acceptance greps and line counts, and the live dispatch; the gate's ratchet leg
  covers the edited skills and the agent.
- **Pair.** Runs as a pair with T1.
- **Estimate.** 50 minutes.

### T3. The tail guard

- **Outcome.**
  - A new `PreToolUse` hook script, `bin/.local/bin/claude-tail-guard` (Python, standard library,
    executable, with a module docstring per `python-conventions`), reads the hook input JSON on
    stdin and looks at `tool_input.command`. It exits 2, with a stderr line telling the session to
    run the command bare or redirect it to a file, when a gate or CI-watch command is piped into
    `tail` or `head`. Otherwise it exits 0 with no output. The match happens inside the script,
    because the hooks page says the `if` filter is best-effort.
  - The commands it guards are the design's list: `cairn-run-gate`, `ci-green`,
    `scripts/check.sh`, `scripts/gate.sh`, `npm test`, `npm run check` (with or without a
    `:suffix`, such as `npm run check:cairn`), and `gh pr checks`. A pipeline stage is guarded only
    when its command word is one of these, after any `VAR=value` assignments and an optional
    `timeout <n>`; `bash scripts/check.sh` and `bash scripts/gate.sh` count, since `bash` runs the
    script. A stage that merely names a gate file (`cat scripts/check.sh`, `grep -n run
    scripts/check.sh`, `git diff -- scripts/gate.sh`) is not guarded. "Piped into" means a later
    stage of the same pipeline starts with `tail` or `head`. `|` and `|&` are pipes; `||`, `;`,
    `&&`, and a newline end a pipeline.
  - A cheap regex pre-filter runs first, the shape `claude-block-op` uses: a command that names no
    guarded command, or no `tail` or `head`, exits 0 at once. Input the script cannot parse (for
    example a heredoc whose body holds an unpaired quote, on which `shlex` raises `ValueError: No
    closing quotation`, review probe) exits 0 silently. Any other exit but 2 is a non-blocking
    error, which the hooks page says puts a notice on the call, so it would show on every such
    command in every session.
  - `claude/.claude/settings.json` adds `{"type": "command", "command": "claude-tail-guard",
    "timeout": 10}` to the `Bash` matcher's `hooks` list, after `claude-secret-guard`, named bare
    like its siblings.
- **Files.** `bin/.local/bin/claude-tail-guard` (new), `claude/.claude/settings.json`,
  `tests/test_claude_tail_guard.py` (new).
- **Risk class.** `runner`.
- **Acceptance.**
  - The test file passes under the gate's pytest leg (`uv run --with pytest --no-project python -m
    pytest tests/ -q`), which picks it up with no `check.sh` change.
  - `python3 -I -c 'import json; json.load(open("claude/.claude/settings.json"))'` exits 0, and the
    `Bash` matcher lists four hooks, `claude-tail-guard` last.
  - The gate prints `gate exit: 0`.
- **Test.** `tests/test_claude_tail_guard.py`, driving the worktree's own script by subprocess with
  hook JSON on stdin, like `tests/claude-clock-stop.test.sh` drives its hook.
  - Denied (exit 2, stderr names a redirect): `cairn-run-gate 'bash scripts/check.sh' | tail -5`;
    `bash scripts/gate.sh 2>&1 | head -40`; `ci-green 12 | tail -1`; `npm test | tail -20`; `npm run
    check:cairn 2>&1 | tail`; `gh pr checks 7 --watch | tail -3`; `bash scripts/check.sh | tee
    out.log | tail`; `bash scripts/gate.sh |& tail -5`; `timeout 600 cairn-run-gate 'bash
    scripts/check.sh' | tail`.
  - Allowed (exit 0, no output): `bash scripts/gate.sh`; `cairn-run-gate 'bash scripts/check.sh' >
    /tmp/gate.log 2>&1`; `npm test; git log --oneline | head -5`; `npm test || echo failed`; `tail
    -5 gate.log`; `git log | head`; `cat scripts/check.sh | head -20`; `git diff -- scripts/gate.sh
    | head`; `grep -n run scripts/check.sh | tail`; `npm test` and `git log | head` on two lines; a
    `git commit` heredoc whose body holds an apostrophe and the words `npm test | tail`; input with
    no `tool_input.command`.
- **Pair.** Runs as a pair with T4 (disjoint files).
- **Estimate.** 55 minutes.

### T4. The guidance warning

- **Outcome.**
  - A new script, `scripts/check-guidance-cite.sh [base]` (base defaults to `origin/main`), reads
    the files the branch changed (`git diff --name-only <base>...HEAD`) and the branch's commit
    messages (`git log --format=%B <base>..HEAD`). When a changed path is under
    `claude/.claude/skills/` or `claude/.claude/agents/`, or is `claude/.claude/settings.json` or
    `claude/.claude/CLAUDE.md`, and no message carries an `http://` or `https://` URL whose host is
    `anthropic.com`, `claude.com`, or a subdomain of either (`code.claude.com`,
    `platform.claude.com`), it prints one `WARNING:` line naming the changed paths. It always exits
    0. When `<base>` does not resolve, or either git command fails (a base with no shared history
    makes `git diff` exit 128, review probe), it prints one line saying the check was skipped and
    exits 0, so the step can never fail the gate through `check.sh`'s `run`.
  - `scripts/check.sh` runs it as a step (`run "guidance citation (warning only)" bash
    scripts/check-guidance-cite.sh`) and runs its test (`run "guidance citation test" bash
    tests/check-guidance-cite.test.sh`). The step never fails the gate. The design makes it a hard
    block only if the warning is skipped twice, which this pass does not build ("Later").
- **Files.** `scripts/check-guidance-cite.sh` (new), `tests/check-guidance-cite.test.sh` (new),
  `scripts/check.sh`.
- **Risk class.** `runner`.
- **Acceptance.**
  - The test passes inside the gate.
  - In T4's worktree, which holds T1's and T2's commits, the gate's guidance step prints no
    `WARNING:` line, since the Commits convention puts a URL in each body.
  - The gate prints `gate exit: 0`.
- **Test.** `tests/check-guidance-cite.test.sh`, in the `claude-clock-stop.test.sh` pattern, with
  temporary repos whose `main` branch stands in as the base:
  - a commit touching `claude/.claude/skills/x/SKILL.md` with no URL prints `WARNING:` and exits 0;
  - the same with `https://code.claude.com/docs/en/skills` in the body is silent;
  - `settings.json` with a `platform.claude.com` URL, and `CLAUDE.md` with an `anthropic.com` URL,
    are silent;
  - a URL on another host (`https://example.com/claude.com`) still warns;
  - a branch touching only `docs/` is silent;
  - a skill change whose only `anthropic.com` mention is the `Co-Authored-By: ...
    <noreply@anthropic.com>` trailer every commit here carries still prints `WARNING:` (a loose host
    grep would pass the other cases and never warn on a real branch);
  - a missing base, and an orphan-branch base with no shared history, each print the skip line and
    exit 0.
- **Pair.** Runs as a pair with T3.
- **Estimate.** 45 minutes. Pair B starts after pair A merges and its gate is green.

### Close

Per pass-core "Close" and dotfiles-pass "Close checklist", in order:

1. `git fetch origin` and merge `origin/main` into the branch (a conflict is a stop). The gate on
   the close head prints `gate exit: 0` (the full-suite home), with no `WARNING:` line from the
   guidance step.
2. `diff-reviewer` at whole-branch scope reads the branch against this plan and the design,
   loading `python-conventions` for `claude-tail-guard`. One batched fix chain follows if it returns
   `fix`, each finding quoted verbatim as the fix's acceptance, then the gate again.
3. `claude-tooling-sync verify` passes (it reads the main checkout, so it is a machine-state check);
   one `gitleaks git` branch-history scan is clean.
4. `docs/STATUS.md` names this pass's PR as waiting on Geoff's read, and its next action is the
   conducting session's post-merge steps (step 5's list).
5. Push to `glw907/workstation`, open the PR (draft until the close is done), write its body, mark
   it ready, and open it in Geoff's browser with `gh pr view <n> -R glw907/workstation --web`. The
   body carries:
   - what landed (task id, commit), the review verdict, and T1's trigger table;
   - "What goes live": at the conducting session's pull into `~/.dotfiles`, the skills,
     `CLAUDE.md`, and `settings.json` change at once through their stow links. The `settings.json`
     hook names `claude-tail-guard`, which reaches `~/.local/bin` only after `stow -R bin`; until
     then every Bash call carries a non-blocking hook-error notice (exit 127, hooks page), so the
     pull and the stow run as one command. Rollback is
     `git revert -m 1 <merge>` on `main`, then a pull;
   - "Post-merge steps for the conducting session" (the design's "Conductor restart"; the executor
     performs none of them), in this order. The settings restore comes before the pull, because
     this PR changes `settings.json` and `git pull --ff-only` refuses a file with an uncommitted
     change that the merge touches:
     1. Restore the stowed `settings.json` from Geoff's one-discussion `/effort high`.
     2. Pull `~/.dotfiles` and stow the new hook script in one command: `git -C ~/.dotfiles pull
        --ff-only && stow -d ~/.dotfiles -R bin`.
     3. Write the conductor's state into `docs/STATUS.md`: work in flight with session names and
        watchers, the next steps in order, decisions pending with Geoff, and post-merge steps owed
        (for example, dubplate's memory prune).
     4. Commit a conductor launch prompt beside it.
     5. Stop its loop.

     Geoff then starts the new conductor with the STATUS launch line.
   - "Found, not done": anything the tasks found;
   - the score rows (pass-core "Score"; `cairn-run-gate --records <toplevel> <branch>` for gate and
     lock time).

   Geoff reads and merges.
- **Estimate.** 50 minutes.

## Later, not built here

- The design's list: estimate calibration from recorded actuals, effort per role, subagent spawn
  limits, and time budgets for multi-agent runs.
- Making the guidance warning a hard failure if it is skipped twice (design item 5). Nothing counts
  skips yet.
- A guidance warning for a change to a hook script in `bin/.local/bin/` that leaves
  `settings.json` alone (reading 4).
- `claude-tooling.md`'s moved rule "Every addition gets three lines", one of which is a line in the
  workstation `CLAUDE.md`, pulls against the shrinking `CLAUDE.md`. T1 moves it as written; a later
  pass may reconcile it.
- Whether pushing a branch and opening a PR sets `live-account`. Sweep 1 said yes. That answer would
  put almost every pass on the full review depth, and `pass-core`'s definition does not settle it.
