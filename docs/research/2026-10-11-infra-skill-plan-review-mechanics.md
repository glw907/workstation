# Infra skill plan review: mechanics and feasibility (2026-10-11)

Target: `docs/superpowers/plans/2026-10-11-infra-skill.md` at `4c3816e` (branch
`worktree-infra-skill-plan`). Lens: mechanics and feasibility. Read with the approved design and
its research record. Every probe ran from scratch files under
`/var/home/glw907/.claude/jobs/18d567d3/tmp/`; nothing in the repo changed except this file.

## Findings, ranked by consequence

### 1. major, correctness: T3 never says where in a stage the guarded command must sit

- **Location:** plan:251-255 (the guarded list), plan:270-276 (the test cases).
- **Defect:** "When a gate or CI-watch command is piped into `tail` or `head`" does not say whether
  `scripts/check.sh` must be the command being run or can be any word in the stage. A substring or
  any-token match denies everyday reads: `cat scripts/check.sh | head -20`,
  `git diff -- scripts/gate.sh | head`, `grep -n run scripts/check.sh | tail`. None of the
  allowed cases would catch that. A false deny exits 2, which blocks the call. Every session on the
  workstation hits this once the PR merges.
- **Evidence:** hooks page (https://code.claude.com/docs/en/hooks): "Exit with code 2 to block the
  action. ... a `PreToolUse` hook blocks the tool call". The design names commands that run
  something, not files a stage happens to mention.
- **Proposed fold:** define a stage as guarded when its command word, after any `VAR=x` prefix and
  a `timeout N` prefix, is one of these: `cairn-run-gate`; `ci-green`; `npm test`;
  `npm run check` or `npm run check:<x>`; `gh pr checks`; or `bash`, `sh`, or direct execution of
  `scripts/check.sh` or `scripts/gate.sh` (an optional `./` prefix is fine). Add these allowed
  cases: `cat scripts/check.sh | head -20`, `git diff -- scripts/gate.sh | head`, and
  `grep -n run scripts/check.sh | tail`.

### 2. major, correctness: T3's parsing failures go unspecified, and the natural parser trips on common input

- **Location:** plan:244-255 and the test list at plan:270-276.
- **Defect:** The obvious parser for "a later stage of the same pipeline" is Python's `shlex`. It
  causes two failures the test list would not catch:
  - It treats a newline as whitespace. The plan says a newline ends a pipeline, but
    `npm test\ngit log | head` tokenizes as one pipeline and gets denied.
  - It raises on a heredoc that holds an apostrophe, such as any commit message written with
    `<<'EOF'` that says "doesn't". An uncaught exception exits 1. The hooks page calls that a
    non-blocking error, so a "hook error" notice lands in the transcript on every such call, all
    day, in every session.
- **Evidence:** a probe (`shlex_probe.py`, `shlex_probe2.py`):
  - `'npm test\ngit log | head' -> ['npm', 'test', 'git', 'log', '|', 'head']`
  - the heredoc with `doesn't` raised `ValueError: No closing quotation`
  - `npm test |& tail` tokenizes `|&` as one token, so a check for `|` alone misses it.

  Hooks page: "When your hook exits with a code other than 0 or 2 ... You see a `<hook name> hook
  error` notice in the transcript".
- **Proposed fold:** in T3's outcome, state three rules:
  - an input the script cannot parse exits 0 with no output;
  - a cheap pre-filter runs first: no guarded command name and no `tail` or `head` word means exit
    0 before any parsing, the same regex-first shape `claude-block-op` uses;
  - `|&` counts as a pipe.

  Add tests:
  - allowed: `npm test` + newline + `git log | head`;
  - allowed: a `git commit -F - <<'EOF'` heredoc containing an apostrophe, with exit 0 and no
    output;
  - denied: `npm test |& tail`.

### 3. major, correctness: T2's pass-core growth bound is ambiguous, and only a tight edit meets it

- **Location:** plan:228-229 (and the design's end-to-end check).
- **Defect:** "The line count of the quote block" is not defined. It could mean the `>` lines only,
  or also the blank line and the lead-in sentence. Separately, the non-quote edits have to net to
  zero lines or less. That covers the lead-in sentence for the prompts, the risk-class rewrite, the
  tripwire, and the two pointers. A natural draft overshoots, so a Sonnet executor is likely to
  meet a red it cannot read, or to pass by choosing the generous reading.
- **Evidence:** I applied all four T2 pass-core edits to a scratch copy at the file's 100-column
  wrap (`draft_edit.py`). The result was 181 lines, 20 more than 161. The quote block, both prompts
  as the research quotes them plus their two URL lines and one `>` separator, came to 17 `>` lines.
  The overshoot came from three lines: the lead-in (+1), a blank line before the quote (+1), and
  the Lifecycle rewrite (+1). The pointer in step 3 saved one line, and step 4 held even with the
  tripwire. A tighter version meets 17 exactly:
  - the lead-in folds into step 1's last line, for +1;
  - no blank line, because a CommonMark block quote may interrupt a paragraph;
  - the Lifecycle rewrite nets 0, step 3 nets -1, and step 4 nets 0.
- **Proposed fold:** define the quote block as the contiguous `>` lines, URL lines included. Then
  give a line budget per edit:
  - the lead-in adds at most 1 line, with no blank line before the quote;
  - the Lifecycle rewrite adds 0 lines net;
  - the step 3 pointer removes at least 1 line;
  - the step 4 pointer plus the tripwire add 0 lines net.

  The commit body records the growth and the `>` count, as the plan already requires.

### 4. major, correctness: pass-core step 2 will contradict the new spec-plan-review depth

- **Location:** plan:209-212 (reading 2), plan:218-224, and plan:230-231 (the diff-scope
  acceptance). The file affected is `claude/.claude/skills/pass-core/SKILL.md:26-27`.
- **Defect:** After T2, `spec-plan-review` says "a design of a page or less needs no separate
  spec". But pass-core step 2 still says "An agent writes the approved design at the length
  precision needs", and step 1 caps every design at a page. The two skills then disagree on whether
  a spec gets written, which is the disagreement reading 2 exists to prevent. The acceptance at
  plan:230-231 forbids touching step 2.
- **Evidence:** pass-core:23-27 as it stands, read against T2's outcome at plan:218.
- **Proposed fold:** extend reading 2 to step 2. Add one clause to step 2, for example "when
  `spec-plan-review` calls for one", and add step 2 to the diff acceptance. This touches a pass-core
  line the design did not name, but it is the same consistency latitude the plan already takes in
  reading 2, and it changes nothing the design decided. If the fold reads it as beyond the design's
  "Out of scope", it goes to Geoff as one question.

### 5. major, correctness: every commit carries `anthropic.com`, so a loose matcher makes T4 vacuous

- **Location:** plan:283-290 (the URL rule) and plan:303-311 (the tests).
- **Defect:** Every commit body on this repo ends with `Co-Authored-By: Claude ...
  <noreply@anthropic.com>`. The plan's rule is right: an `http://` or `https://` URL whose host is
  one of the named domains. The tests, though, would also pass an implementation that greps for
  `anthropic\.com` or `claude\.com` anywhere in the text. That implementation never warns on any
  real branch. The `example.com/claude.com` case does not catch it, because the trailer is an email
  address, not a URL path.
- **Evidence:** `git log --format='%h %B' origin/main..HEAD` on this branch. All three bodies end
  `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`, and none holds an `http` URL.
- **Proposed fold:** add a test where a commit touching `claude/.claude/skills/x/SKILL.md` has no
  URL, only the `Co-Authored-By: ... <noreply@anthropic.com>` trailer. It must print `WARNING:`.

### 6. minor, correctness: a base with no merge base fails git, and the skip path does not cover it

- **Location:** plan:289-293.
- **Defect:** The skip covers only a `<base>` that does not resolve. When the base resolves but
  shares no history with HEAD, `git diff <base>...HEAD` exits 128. A script that passes that status
  through, or runs under `set -e`, fails `run`, and so fails the gate. That breaks "The step never
  fails the gate."
- **Evidence:** fixture probe (`t4_probe.sh`): `fatal: lonely...HEAD: no merge base`,
  `nomergebase diff rc=128`. For an unresolved base, `diff rc=128` and `log rc=128`. `check.sh:15-23`
  sets `fail=1` on any non-zero step.
- **Proposed fold:** skip with the same one line on any git failure: `rev-parse --verify` of the
  base, then `merge-base`. Add a test with an orphan-branch base.
- **Confirmed as stated:** in a linked worktree, and in a worktree branched from it the way a pair
  subagent's is, `origin/main` resolves (`pair origin/main rc=0`). After the close merges
  `origin/main` into the branch, `diff origin/main...HEAD` still lists only the branch's file, and
  `log origin/main..HEAD` adds only the merge commit.

### 7. minor, correctness: "in full" asks for text the research record does not hold

- **Location:** plan:26-33, plan:150-152 (T1 step 4), plan:203-205 (T2 step 1), and plan:113-114
  (the Citations rule).
- **Defect:** The research quotes the "Avoid over-engineering" prompt with an elision: "... A
  simple feature doesn't need extra configurability. ... - Defensive coding". T1 and T2 ask for it
  "in full", but the Citations convention says every quote is copied from the research record. Both
  cannot hold. The plan's own Scope quote also drops the `...`, so it is not verbatim.
- **Evidence:** research:20-23 holds the elided text, and plan:29 has the same span without the
  `...`.
- **Proposed fold:** say "as the research quotes it, its `...` kept" in T1, in T2, and in the Scope
  paragraph, and restore the `...` at plan:29.

### 8. minor, correctness: the PR body says the change goes live "at the merge", but it goes live at the pull

- **Location:** plan:333-336 and plan:341-343.
- **Defect:** A GitHub merge does not change `~/.dotfiles`. The stow links change only at the
  conducting session's `pull`. Between the pull and `stow -R bin`, `settings.json` names a hook
  that is not on PATH yet. Per the hooks page, that call is non-blocking, so nothing breaks, but
  every Bash call in every live session shows a hook error notice until the stow runs.
- **Evidence:** hooks page: "A hook that can't start is a non-blocking error too. In shell form,
  when the script path doesn't exist or isn't executable, the shell exits with a code like 127 ...
  To block the action instead, set `onFailure: "block"`." `ls -la ~/.local/bin` shows per-file
  links (`ci-green -> ../../.dotfiles/bin/.local/bin/ci-green`), so a new script needs a stow.
  `~/.claude/skills`, `settings.json`, and `CLAUDE.md` are each one link into the checkout, so
  they need no stow. The fixture probe (`pull_probe.sh`) confirms the ordering note: with a dirty
  file the merge touches, `pull --ff-only` printed "Your local changes to the following files would
  be overwritten by merge: settings.json ... Aborting" and `rc=1`, and it printed `rc=0` when only
  an untouched file was dirty.
- **Proposed fold:** change "at the merge" to "at the conducting session's pull". Run step 2 as one
  command, `git -C ~/.dotfiles pull --ff-only && stow -d ~/.dotfiles -R bin`, so the 127 window is
  that command's duration. Never set `onFailure: "block"` on this hook.

### 9. minor, correctness: T1's trigger check hides the skills that compete in a real session

- **Location:** plan:175-190.
- **Defect:** `--setting-sources project` hides the personal and plugin skills, including
  `pass-core`, `spec-plan-review`, `writing-skills`, and `skill-creator`. Bundled skills stay. So
  the table measures `claude-infra` against `update-config` only. For "Change the pass process so
  ...", the real competitor is `pass-core`, which is absent unless someone copies it in.
- **Evidence:** three probes, each one plain command in the plan's exact form, run from this
  worktree-isolated session. The isolation guard accepted all three, even with "git push --force"
  in the prompt. Each run took about 23 seconds. The draft skill is at `trig/hook/.claude/skills/`.
  - The `init` event's `"skills"` list held `claude-infra` plus bundled skills, `update-config`
    among them, and no personal or plugin skills.
  - "Make a hook for blocking git push --force in every session." gave
    `"name":"Skill","input":{"skill":"claude-infra"}`, count 1. `update-config` did not fire.
  - "Add a rule that every pass plan names its rollback step." gave
    `"name":"Skill","input":{"skill":"claude-infra","args":"..."}`, count 1. `skill` precedes
    `args`, so the plan's grep string still matches.
  - "Change the pass process so a plan with two tasks skips the clock file.", with copies of
    `pass-core` and `dotfiles-pass` beside the draft, gave `claude-infra`, count 1.
  - No run wrote a file; out-of-directory Bash and Read calls were recorded as
    `permission_denials`.
- **Proposed fold:** each run's `.claude/skills/` also holds copies of `pass-core` (from
  `claude/.claude/skills/`) and `dotfiles-pass` (from `.claude/skills/`). It costs two `cp` calls
  per run, and the table then measures the competition a real session meets. The grep string needs
  no change.

### 10. minor, optional: the launch reads a prompt file that is not on the branch yet

- **Location:** plan:74 and plan:82-92.
- **Defect:** `docs/superpowers/plans/2026-10-11-infra-skill-prompt.txt` does not exist at
  `4c3816e`. Only `...-planning-prompt.txt` does. If it is missing at launch, `$(git show ...)`
  prints an error and launches `claude --bg` with an empty prompt.
- **Proposed fold:** add a launch check, `git -C ~/.dotfiles cat-file -e
  worktree-infra-skill-plan:docs/superpowers/plans/2026-10-11-infra-skill-prompt.txt` (must exit
  0).

### 11. minor, optional: the close's `claude-tooling-sync verify` proves nothing about the branch

- **Location:** plan:325.
- **Defect:** The plan says so itself: verify reads the main checkout, so before the merge it
  checks a state this branch does not touch. The gate already runs `lint --root .` on the branch.
  This is ceremony at the close.
- **Proposed fold:** move `claude-tooling-sync verify` into the post-merge steps, after the pull
  and stow, where it does check the merged state. Drop it from close step 3.

### 12. minor, optional: "`claude-tail-guard` last" asserts an order that does nothing

- **Location:** plan:256-258 and plan:265-266.
- **Defect:** Matching hooks run in parallel, so list position has no effect.
- **Evidence:** hooks page: "All matching hooks run in parallel."
- **Proposed fold:** the acceptance checks that the Bash matcher lists `claude-tail-guard`, not
  where.

### 13. minor, optional: the worktree guard refuses ad-hoc git probes in T4

- **Location:** plan:303-311 (T4 test), and the Conventions section.
- **Defect:** From a worktree-isolated session, `git -C ~/.dotfiles ...` was refused ("points git
  at a directory computed at runtime"). So was an inline `python3 -c` that merely contained the
  word git ("names git in a form too complex to verify"). A T4 executor that probes fixture repos
  inline will be refused and may loop. Running the same steps as `bash <script file>` worked.
- **Proposed fold:** one sentence in T4: fixture work lives in `tests/check-guidance-cite.test.sh`
  or a scratch script run as `bash <file>`, never as inline git against a temp path.

### 14. minor, optional: the repo's supersession rule wants T2's retired phrases listed

- **Location:** plan:200-212 and plan:225.
- **Defect:** `claude/.claude/tooling/retired-phrases.txt` says: "Every ruling that supersedes text
  adds the superseded phrase here in the same commit". T2 supersedes "The design's class is a
  floor" and the plan-depth sentence ("Plan review runs the mechanics lens and a verification
  read"). This is a repo convention, not a design requirement.
- **Proposed fold:** if the fold takes it, add those two phrases to `retired-phrases.txt` in T2's
  commit and list the file under T2's Files. It stays disjoint from T1, and `grep` shows no other
  hit outside pass-core.

### 15. minor, optional: the path map does not list the new hook script

- **Location:** plan:17-20.
- **Defect:** The `dotfiles-pass` path map (`.claude/skills/dotfiles-pass/SKILL.md:29-36`) puts its
  hook siblings under `auth-data` and lists named `runner` scripts, but `claude-tail-guard` is in
  neither. A later change to it alone would class as `ordinary`, even though a false exit 2 blocks
  every Bash call on the workstation.
- **Proposed fold:** add an item to "Later": list `claude-tail-guard` in the `dotfiles-pass`
  runner map. Editing that file is outside this design.

## Confirmed as the plan states (no finding)

- **Hooks:** a `PreToolUse` exit 2 blocks the call and sends stderr as the reason. An exit of 127
  (not on PATH) is a non-blocking error with a notice. Matchers run in parallel. The `if` filter is
  best-effort. All quoted from https://code.claude.com/docs/en/hooks.
- **T1 grep:** the string is right for `claude-infra`. The bundled `update-config` stays visible
  under `--setting-sources project` and did not win against the draft. The run form passes the
  isolation guard.
- **T3 tests and lint:**
  - The repo has no `pytest.ini`, `pyproject.toml`, `setup.cfg`, `tox.ini`, or `conftest.py`, so
    pytest's default `test_*.py` discovery picks up `tests/test_claude_tail_guard.py` with no
    `check.sh` change.
  - `scripts/check-py-comments.sh` globs `bin/.local/bin/*` for a python shebang, so it lints the
    extensionless script whether or not it is tracked.
  - `ruff.toml` ignores `D` under `tests/**`, and ignores D100-D107, so the docstring is a
    convention, not a gate.
- **T4:** `git diff --name-only` and `git log --format=%B` behave as stated in a linked worktree,
  after a merge of `origin/main`, and from a nested worktree.
- **Close:** `pull --ff-only` refuses a dirty file the merge touches, so the plan's order (restore,
  then pull) is right. Skills, `CLAUDE.md`, and `settings.json` need no stow; a `bin` script does.
- **T1 lint checks:**
  - `dead-reference` exempts a single-segment slash span, so `/doctor prompt-audit` and
    `/skill-doctor` are safe.
  - `description-cap` is `len()` > 500, which counts code points.
  - `lint` flags only a skill dir that carries a `LICENSE` file, so a new authored skill passes.
  - No `~/Projects/*/.claude/skills/claude-infra` exists, so `verify`'s collision check passes.
- **CLAUDE.md:** the section body drops from 7 lines to 1, giving about 193 lines, under both the
  plan's 199 and `claude-context-budget`'s 200 cap.
- **Disjoint files:** T1 (new skill, `CLAUDE.md`, `claude-tooling.md`) and T2 (pass-core,
  spec-plan-review) share none. T3 (hook, `settings.json`, pytest file) and T4 (`check.sh`, new
  script, its test) share none. No other skill restates review depth; only `claude-tooling.md:140`
  does, and T1 owns that line.
- **Clock:** 245 task-minutes is under the design's 360 tripwire. Five trigger runs at about 23
  seconds each fit T1's 70 minutes.

## Summary

The plan's mechanisms mostly behave as it says. The hook exit codes, the trigger-check form and
grep string, the T4 git semantics, the pytest and ruff pickup, the stow layout, and the pull-order
note all check out by probe or by quoted docs. The real risk is in T3: a guarded command's position
in a stage is undefined, and parse failures are unspecified. A plausible implementation would
either block everyday reads such as `cat scripts/check.sh | head` or put a hook error notice on
every heredoc commit, workstation-wide, at merge. Two of T2's mechanics also need work: the
pass-core growth bound is ambiguous, and only a tight edit meets it (a natural draft came to 20
lines against 17). Pass-core step 2 would contradict the new "no separate spec" depth, a fix the
fold can take under reading 2 or send to Geoff. T4 needs a test for the `noreply@anthropic.com`
trailer, or a loose matcher makes the warning vacuous on every branch. Counts: 9 `correctness`
(5 major, 4 minor) and 6 `optional` (all minor). No blocker. Finding 4 may touch a pass-core line
the design did not name.
