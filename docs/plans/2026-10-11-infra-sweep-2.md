# Infra sweep 2, the content: implementation plan

**Design:** `docs/specs/2026-10-11-infra-sweep-2-design.md` (approved by Geoff,
2026-10-11, with unattended planning). It is one page, so no separate spec was written
(`spec-plan-review` "Depth scales with risk"). **Evidence:** the probed facts,
`docs/research/2026-10-11-infra-sweep-2-facts.md` (cited below as "facts"), which gives
each finding's current lines and quotes; the survivor ledger,
`docs/research/2026-10-11-infra-sweep-survivor-ledger.md`; the audit,
`claude/.claude/docs/record/2026-09-28-claude-infra-audit.md` section 5. **Review:** the mechanics
lens and the fold record,
`docs/research/2026-10-11-infra-sweep-2-{review-mechanics,plan-fold}.md`.

**Outcome.** Every surviving content finding is fixed, and the ratchet baseline holds no entries.
`pass-core` carries pre-approved planning, the conductor role, self-merge for `ordinary` passes, and
the commit-id rule, and `go-ship` carries the serial simplifier dispatch. The monthly review
launches itself, `/effort` no longer dirties `~/.dotfiles`, and `elm-conventions` and
`bubbletea-design` rest on Charm's published model.

**Pass class:** `runner` (design, "All are `runner` class"). Every task but F touches
`claude/.claude/{skills,agents}/**`, `claude/.claude/tooling/**`, `claude/.claude/settings.json`,
`.claude/skills/**`, `bin/.local/bin/claude-tooling-sync`, or `tests/**`; F's files map to
`ordinary`, and it is `runner` because it launches unattended sessions. No `live-account` flag
(design, "Risk and size"). No `auth-data` path is touched. The only account call is D's read-only token verify.

**Out of scope:** the design's list (other repos, poplar's refactor, `fetch_skill`'s atomic writes
and head-SHA race, the R2 checks, a per-rule basis record, a quarterly prune). Also out: any edit to
the global `claude/.claude/CLAUDE.md` (195 of its 200 lines; DC-22 needs none, facts "D"), the
audit record, and a refetch of any vendored skill.

**Task boundaries moved from the design, by file.** These keep each pair's files disjoint and
change no item's content:

- CS-3, CS-5, CS-12, and DC-10's retirement of `docs/bubbletea-conventions.md` move from A to I.
  I rewrites `elm-conventions` and `bubbletea-design`, and `elm-conventions` is the only live file
  citing the retired doc.
- PS-08's `content-review` half and the `svelte-check` description move from C to B. Each pair's
  baseline removals then sit on one side, so the shared `ratchet-baseline.json` merges cleanly.
- `figure-verifier`'s `omitClaudeMd` line moves from D to B, which edits that file for AW-15.
- `tui-visual-verify`'s description trim joins A: its `description-cap` entry must clear for the
  empty baseline, and A already edits the file for CS-7. Charm's review (I) leaves it unchanged, as
  the design says.

**End-to-end check.** On the close head:

1. `bash scripts/gate.sh` prints `gate exit: 0`.
2. `python3 -I -c 'import json; print(json.load(open("claude/.claude/tooling/ratchet-baseline.json"))["entries"])'`
   prints `[]`.
3. `wc -l claude/.claude/skills/go-conventions/SKILL.md claude/.claude/skills/elm-conventions/SKILL.md`
   prints two counts under 500. Every `elm-conventions` rule carries a Charm citation or a
   "House departure" line (I's acceptance).
4. Each trigger table in the PR body shows every should-trigger prompt triggering and no
   should-not prompt triggering, after the change.
5. F's dry run completed unattended through `systemd-run` and left a quiet-month line or a design
   on a local branch (F's acceptance).
6. G's pytest case passes: after `apply` on the fixture home, a `modelSettings` write into the
   generated live file leaves `verify` passing and the fixture's tracked `settings.json` byte for
   byte unchanged (G's acceptance). The live check, a real `/effort` change leaving `git -C
   ~/.dotfiles status --porcelain` empty, follows the merge, since the stowed tree is `main`'s (PR
   body, "What goes live").
7. `grep -n 'no sub-agents' claude/.claude/skills/go-ship/SKILL.md` and `grep -n 'merge commit'
   claude/.claude/skills/pass-core/SKILL.md` each print a line.

**Clock estimate:** 975 task-minutes: A 175, I 110, B 160, C 55, D 105, F 145, E 80, G 70, close
75. The pairs run in four waves: A with I, B with C, D with F, and E with G. The path is about
175 + 160 + 145 + 80 + 75 = 635 minutes.

## Launch

Prompt file: `docs/plans/2026-10-11-infra-sweep-2-prompt.txt`. The plan lives on
branch `worktree-infra-sweep-2` (planning commits). The executor continues that branch: its first
act after `EnterWorktree` (name `infra-sweep-2-build`) is `git merge --no-edit
worktree-infra-sweep-2` (pass-core "Execute"). Launch from the main checkout, after every check
prints what its comment names:

```bash
git -C ~/.dotfiles fetch origin
git -C ~/.dotfiles branch --show-current                # must print main
git -C ~/.dotfiles rev-list --count HEAD..origin/main   # must print 0 (not behind)
git -C ~/.dotfiles rev-list --count origin/main..HEAD   # must print 0 (not ahead)
git -C ~/.dotfiles status --porcelain                   # must print nothing
git -C ~/.dotfiles rev-parse worktree-infra-sweep-2 origin/worktree-infra-sweep-2   # two equal lines
claude agents --json                                    # no live session with cwd in ~/.dotfiles/.claude/worktrees/infra-sweep-2-build
cd ~/.dotfiles && claude --bg --model sonnet --effort medium --name infra-sweep-2-build \
  "$(git -C ~/.dotfiles show worktree-infra-sweep-2:docs/plans/2026-10-11-infra-sweep-2-prompt.txt)"
```

The prompt is read with `git show` because the plan is not on `main` until this pass's PR merges.
If the local branch `worktree-infra-sweep-2` is absent (the planning worktree was removed), run
`git -C ~/.dotfiles branch worktree-infra-sweep-2 origin/worktree-infra-sweep-2` first.

## Conventions every task follows

- **Gate.** `bash scripts/gate.sh`, with the Bash tool's `timeout: 600000`, re-issued on exit 75
  until it prints `gate exit:`. It is also the fast lane. A focused leg (a single pytest file) may
  run between edits; the task's acceptance is the gate.
- **The main checkout stays untouched.** Every tool runs from the worktree's own path
  (`bin/.local/bin/<tool>`, `scripts/<tool>`), never as a bare name: `~/.local/bin/<tool>` is a stow
  link to the main checkout's copy. No command writes `~/.dotfiles` outside `.claude/worktrees/`,
  and no command writes a tracked or configuration file in `~/.claude` (G's fixtures use scratch
  homes; the transcripts every `claude -p` run leaves under `~/.claude/projects` are expected).
- **Commits.** One commit per task, subject starting with the task id (`A: Split go-conventions
  and fix CS-1 to CS-13`), imperative mood, specific files only. The pre-commit hook runs the
  ratchet's `hook` mode.
- **Ratchet removals.** A fix that clears a violation removes its baseline entry in the same
  commit; the gate fails on a stale entry ("remove this baseline entry", `ratchet.py:322-324`).
  Edit `ratchet-baseline.json` by hand: delete only the removed entries' own lines and fix the
  comma the last remaining entry carries, never reflow the file. The `checks` registry stays as
  is. Each task's entries are listed in its acceptance.
- **Trigger checks** (design "Anthropic practice" item 7, through the parent spec). Before the
  edit, `mktemp -d /tmp/infra-sweep-2-<task>.XXXXXX` makes the task's scratch directory, with the
  printed path written literally in every later command. For each prompt, a run directory under it
  holds `.claude/skills/<skill>/`, a copy of the skill directory under test: the base copy for the
  "before" run (copied before the first edit), the edited copy for "after". Each run is one plain
  command, `cd <scratch>/<run> && timeout 180 claude -p --model sonnet --setting-sources project
  --output-format stream-json --verbose "<prompt>" > <scratch>/<run>.jsonl`, with no pipe, heredoc,
  or inline script. A separate step reads each file with `grep -c
  '"name":"Skill","input":{"skill":"<skill>"'`. This is sweep 1's probed method
  (`docs/plans/2026-10-11-infra-sweep-1-guard.md` T2). After the change, every
  should-trigger prompt triggers and no should-not prompt does. One reword of the description is
  allowed; a second miss is a stop, returned with the table. The before and after rows go in the
  task's commit body, and the session copies them into the PR body.
- **Prose.** Skill and agent text is agent-facing: load `writing-voice` for that audience before
  drafting. The gate's Vale and `tellgrader` legs are the net. Charm's guide is FSL-1.1-MIT: cite
  it by URL and pinned commit, distill in the house's own words, and never paste its text.
- **Clock.** At each wave's start the session writes `pass-task-clock` in its own pass worktree's
  git dir (`git rev-parse --absolute-git-dir`) with `task=<ids>`, `start=<epoch>`, and
  `estimate=<the wave's longer task>`. It checks the overrun when both return, then removes the
  file (pass-core "Clock stop"). Pair worktrees hold no clock file.
- **Pairs.** Each wave dispatches two Agent-tool subagents (`subagent_type: "general-purpose"`,
  `isolation: "worktree"`, model `sonnet`, effort `medium`) after the session's last commit. Each
  gets its task's full text and this section verbatim. Each commits and never pushes. The session
  merges both, runs the gate, and pushes. A merge conflict is a stop.
- **Stops.** A red the session cannot fix in two attempts, a merge conflict, a second trigger
  miss, or a clock stop: write `docs/STATUS.md` on the branch (task in flight, what failed, the one
  question), run `notify-send -u normal "infra-sweep-2: stopped"`, and wait. A pair subagent that
  hits one returns its work uncommitted, and the session applies this rule before merging either
  half.
- **Scope.** A defect found outside a task goes to the PR body's "Found, not done" list, each with
  a proposed now, defer, or drop and a one-line reason. A pair subagent lists such defects in its
  final report.

## Tasks

### Wave 1: A and I (a pair)

### A. Go skills

- **Outcome.**
  - CS-1: the cobra root template sets `SilenceErrors: true` beside `SilenceUsage`, and its note
    says `main()` is the only error printer (facts "CS-1").
  - CS-2: one line in the CLI Framework section says `go-conventions` wins over the vendored
    `golang-spf13-cobra` skill on any conflict, naming the four (package-level `rootCmd`, testify,
    output streams, viper). The vendored skill is not edited.
  - CS-4: no pinned Go version (:84 and :592 become version-neutral, clearing `currently 1.26`);
    the `check-deep` sentence (:363) and the ADR-0230 citation (:335) go; :408 bans build tags in
    product code and allows test-only tags the gate vets.
  - CS-13: the Error Handling section is the one home for error strings and the unexported-godoc
    paragraph at :499-502 the one home for that default; rubric item 6, `### Error strings`, and
    `### Unexported godoc default` go.
  - Size: `go-conventions/SKILL.md` under 500 lines, with reference material moved one level down
    to `go-conventions/references/<topic>.md` files, each linked from the section it left
    (candidates: facts "Size"). The description drops under 500 code points and keeps its trigger
    terms.
  - CS-7: `tui-visual-verify` calls `kitty-headless-shot` directly; the copy-in instruction, `-d`,
    and the `import -window` fallback go, and `scripts/kitty-shot` is deleted. Its description
    drops under 500 code points.
  - CS-11: `ts-conventions`' inline ESLint config gives way to a pointer at
    `~/Projects/cairn-cms/eslint.config.js` as the copy-in source, keeping the adjust-globs note.
  - `docs/bluefin-admin.md:245` and the `bin/.local/bin/kitty-headless-shot:52` comment stop citing
    the deleted template.
- **Files.** `claude/.claude/skills/go-conventions/SKILL.md`,
  `claude/.claude/skills/go-conventions/references/*.md` (new),
  `claude/.claude/skills/tui-visual-verify/SKILL.md`,
  `claude/.claude/skills/tui-visual-verify/scripts/kitty-shot` (deleted),
  `claude/.claude/skills/ts-conventions/SKILL.md`, `claude/.claude/docs/bluefin-admin.md`,
  `bin/.local/bin/kitty-headless-shot`, `claude/.claude/tooling/ratchet-baseline.json`.
- **Risk class.** `runner`.
- **Acceptance.**
  - Baseline entries removed: `retired-phrase` `go-conventions` `currently 1.26` (CS-4), and
    `description-cap` for `go-conventions` and `tui-visual-verify` (GA-06).
  - `wc -l` on `go-conventions/SKILL.md` prints under 500; every `references/` file is linked from
    `SKILL.md`.
  - `grep -n 'SilenceErrors: true' claude/.claude/skills/go-conventions/SKILL.md` prints a line;
    `grep -rn 'kitty-shot\b' claude/.claude/skills/tui-visual-verify claude/.claude/docs/bluefin-admin.md`
    prints nothing.
  - Trigger checks, before and after, for `go-conventions` and `tui-visual-verify` (the global
    CLAUDE.md "Go Development" section depends on both):
    - `go-conventions` should trigger: "Add a --json flag to the validate subcommand of my Go cobra
      CLI."; "Write a table-driven test for the atomic file-write helper in internal/store."; "Review
      this Go diff: fmt.Errorf(\"failed to open config: %w\", err) and a new Option builder type."
      Should not: "Add a TSDoc comment to this TypeScript loadConfig function."; "Fix the wording of
      this Python docstring."
    - `tui-visual-verify` should trigger: "I changed the sidebar theme in my Bubble Tea app. Confirm
      the new colors really render before I merge."; "The goldens pass for my terminal UI's compose
      screen, but the owner says the border looks wrong. Check what the terminal paints.";
      "Capture evidence of my TUI list view's live-resize behavior for the pass gate." Should not:
      "Write a unit test for the date-parsing helper in my Go CLI."; "Take a screenshot of my
      SvelteKit site's landing page in Chromium."
  - The gate prints `gate exit: 0`.
- **Test.** The trigger checks; the gate's reference, retired-phrase, description-cap, and prose
  legs.
- **Pair.** Wave 1, with I.
- **Estimate.** 175 minutes.

### I. Charm's model for `elm-conventions` and `bubbletea-design`

- **Outcome.**
  - `elm-conventions` rests on Charm's agent guide for Crush's UI
    (<https://github.com/charmbracelet/crush/blob/f02ffbcec15a9f95cb9bcff895833df10f829aae/internal/ui/AGENTS.md>,
    pinned; facts "I" lists its rules by line). Secondary sources: the Bubble Tea v2 discussion
    (<https://github.com/charmbracelet/bubbletea/discussions/1374>) and the releases page (v2.1.0).
    Every rule cites one of them, or carries a "House departure" line saying why the house differs.
  - It adopts Charm's model: one top-level Bubble Tea model; child components are plain structs
    with imperative methods, returning a `tea.Cmd` where a side effect is needed; no nested models;
    no command used to send a message when the parent can mutate the child directly. This replaces
    Rule 1 ("Every component is a `tea.Model`"), Rule 4's Msg-signalling, and the Parent-Child
    Update Delegation Pattern, and the description drops "children signal parents via Msg types".
    One line says existing nested-model code migrates in its repo's own refactor pass (poplar's is
    planned), and new code follows the rule.
  - Its scope is generic Bubble Tea v2 UI code, with no poplar paths or helpers (CS-3); root `View()`
    examples return `tea.View` (CS-12). The file is under 500 lines; reference material, including
    any checklist kept from the retired doc, sits one level down in
    `elm-conventions/references/*.md`.
  - `claude/.claude/docs/bubbletea-conventions.md` is deleted (DC-10), and its two `relative-link`
    entries leave the baseline.
  - `bubbletea-design`: Live Preview's kitty launch on the desktop and the tmux-capture
    verification go, pointing at `tui-visual-verify` instead (CS-5). Width measurement follows
    Charm's `ansi.StringWidth` and `elm-conventions`, never `lipgloss.Width` alone for glyphs. Its
    rules cite Charm or say why the house departs.
  - `docs/claude-tooling.md` records the order of use for TUI work (the house skills, then Charm's
    guide, then the installed `tui-design` plugin, gfargo, MIT) and gives `tui-design` its rule of
    use: it is consulted for layout and discoverability patterns, and the house skills win on any
    conflict.
- **Files.** `claude/.claude/skills/elm-conventions/SKILL.md`,
  `claude/.claude/skills/elm-conventions/references/*.md` (new),
  `claude/.claude/skills/bubbletea-design/SKILL.md`,
  `claude/.claude/docs/bubbletea-conventions.md` (deleted), `claude/.claude/docs/claude-tooling.md`,
  `claude/.claude/tooling/ratchet-baseline.json`.
- **Risk class.** `runner`.
- **Acceptance.**
  - The guide is read with `gh api repos/charmbracelet/crush/contents/internal/ui/AGENTS.md?ref=f02ffbcec15a9f95cb9bcff895833df10f829aae
    -H 'Accept: application/vnd.github.raw'`, never from memory.
  - Baseline entries removed: both `relative-link` entries in `bubbletea-conventions.md` (DC-10).
  - `wc -l` on `elm-conventions/SKILL.md` prints under 500. `grep -n -i 'poplar\|displayCells\|bubbletea-conventions'
    claude/.claude/skills/elm-conventions/SKILL.md` prints only the one migration line.
  - Each `## Rule` heading's section in `elm-conventions` holds a Charm URL or a "House departure"
    line (a reviewer can check by reading each section).
  - No sentence of Charm's guide appears verbatim beyond a short quoted rule with its citation.
  - Trigger checks, before and after, for `elm-conventions` (the global CLAUDE.md names it, and its
    description changes). Should trigger: "Add a help-overlay component to my Bubble Tea v2 app's
    UI."; "Review this Bubble Tea Update function: it makes an HTTP request inline before returning
    the model."; "How should my Bubble Tea list component tell the top-level model the selection
    changed?" Should not: "Write a cobra subcommand that prints the version."; "Style a React
    dropdown with Tailwind classes."
  - The gate prints `gate exit: 0`.
- **Test.** The trigger checks; the gate's reference, relative-link, and prose legs.
- **Pair.** Wave 1, with A.
- **Estimate.** 110 minutes.

### Wave 2: B and C (a pair)

### B. Cairn-facing skills and agents

- **Outcome** (each finding's current lines: facts "B").
  - PS-02: `cairn-release`'s gate is `npm run check:close` plus `npm test`; the hand-listed checks
    go, and the `npm version` and consumer-build steps stay.
  - PS-03: `docs/guides/upgrade-cairn.md` becomes `docs/extend/upgrade-cairn.md`.
  - PS-28: the `cairn-release` and `visual-fidelity` descriptions drop to about 300 code points,
    keeping their trigger terms.
  - PS-05: `cairn-figure`'s restated alt rules become a pointer to the register's "Visuals"
    section (cairn-cms `docs/internal/docs-register.md`), and the "gates do not exist yet" section
    says `npm run check:visuals` exists and drops the `check:figures` claim.
  - PS-06: `register-check` (a `context: fork` skill) takes the files, an `apply: yes/no`
    argument, and any sanctioned phrases as explicit arguments, and reports new tells for the
    caller to file; nothing in it assumes a conversation.
  - PS-19: "three-gate" becomes "four-gate" at :3 and :9, and the description names the fourth
    gate.
  - PS-17: `engine-consult` defines "Facts consulted" once. The plan-template half is gone with
    the template (facts "PS-17").
  - PS-18: ", including a prior pass's pass-end draft" goes.
  - AW-22: `engine-consult`'s copy of the engine standard becomes a pointer to the `engine-triage`
    agent's "The standard" section, and that agent's "do not let the two drift" comment goes.
  - AW-14: `daisyui-a11y-reviewer`'s two ledger paths are written under `~/Projects/cairn-cms/`.
  - AW-15: `figure-verifier` reads `docs/internal/docs-register.md` under the checkout its dispatch
    names, falling back to the main checkout's path only when none is named. It also sets
    `omitClaudeMd: true` (design D; the subagents page: "Use it for subagents that take everything
    they need from the delegation prompt").
  - PS-20: `content-review` ends at its report; step 7's ask-and-apply goes.
  - PS-08 (`content-review` half): when the site has no `docs/content-guide.md`, the skill runs on
    the shared method alone and says so.
  - `svelte-check`: its description is quoted (or a folded block) so a strict YAML parse passes,
    and drops under 500 code points.
- **Files.** `claude/.claude/skills/{cairn-release,visual-fidelity,cairn-figure,register-check,engine-consult,content-review,svelte-check}/SKILL.md`,
  `claude/.claude/agents/{daisyui-a11y-reviewer,figure-verifier,engine-triage}.md`,
  `claude/.claude/tooling/ratchet-baseline.json`.
- **Risk class.** `runner`.
- **Acceptance.**
  - Baseline entries removed: `retired-phrase` `cairn-figure` (PS-05); `description-cap` for
    `cairn-release`, `visual-fidelity` (PS-28), and `svelte-check` (GA-06); all four `fork-skill`
    entries (PS-06, PS-20).
  - `python3 -I -c 'import yaml, sys; t = open(sys.argv[1]).read().split("---")[1]; yaml.safe_load(t)'
    claude/.claude/skills/svelte-check/SKILL.md` exits 0 (system PyYAML).
  - `grep -n 'three-gate' claude/.claude/skills/register-check/SKILL.md` prints nothing.
  - The `register-check` and `content-review` bodies contain none of the fork-skill phrases
    (`claude-tooling-sync` `FORK_PHRASES`, counted as lowercase substrings): `under discussion`,
    `during the session`, `delegated`, `ask the user`, `ask "`. `grep -n -i 'under
    discussion\|during the session\|delegated\|ask the user\|ask "'` on both files prints nothing.
  - Trigger checks, before and after, for `visual-fidelity` and `cairn-release` (design B):
    - `visual-fidelity` should trigger: "Port our club site's old WordPress theme to SvelteKit so it
      looks the same."; "This chip sits a pixel low beside the card title. Fix the vertical
      alignment so it is optically centred."; "Rebuild the home page in the new stack, matching the
      current live site." Should not: "Add a server-side redirect from /old to /new in the SvelteKit
      hooks."; "Write the copy for the volunteer sign-up page."
    - `cairn-release` should trigger: "Publish cairn to npm; main is green."; "Cut a cairn release
      so ecxc-ski can pick up the new export."; "Pick the next cairn version and finalize the
      CHANGELOG for the release." Should not: "Deploy the ecxc-ski site to Cloudflare."; "Finish the
      current cairn-cms pass and open its PR."
  - The gate prints `gate exit: 0`.
- **Test.** The trigger checks and the YAML parse; the gate's description-cap, fork-skill,
  retired-phrase, and reference legs.
- **Pair.** Wave 2, with C.
- **Estimate.** 160 minutes.

### C. Site and generic skills

- **Outcome** (facts "C").
  - PS-08 (`content-draft` half): the absent-guide branch, as in B.
  - PS-10: `log-issue` honors `"backlog": false` in `.claude/project-tracking.json` (it creates no
    file and says the repo keeps no backlog), never creates a missing backlog unasked, and stages
    `<backlog_path>` instead of `BACKLOG.md`.
  - PS-21: `dependency-upgrade` names cairn-cms's `docs/internal/record/`, and otherwise the
    records directory the repo's CLAUDE.md or STATUS names.
  - PS-09 residual: `site-pass` reads the plan, spec, archive, and architecture-doc paths from the
    site's CLAUDE.md or STATUS, giving `docs/` and `docs/architecture.md` as the usual
    case, never the only one.
  - PS-11 residual: the `## Done` block leaves `log-project`'s example roadmap.
- **Files.** `claude/.claude/skills/{content-draft,log-issue,dependency-upgrade,site-pass,log-project}/SKILL.md`.
- **Risk class.** `runner`.
- **Acceptance.** `grep -n 'git add BACKLOG.md' claude/.claude/skills/log-issue/SKILL.md` and
  `grep -n '## Done' claude/.claude/skills/log-project/SKILL.md` print nothing. The gate prints
  `gate exit: 0`. No baseline entry is C's.
- **Test.** The gate's reference and prose legs.
- **Pair.** Wave 2, with B.
- **Estimate.** 55 minutes.

### Wave 3: D and F (a pair)

### D. Docs and agents

- **Outcome** (facts "D").
  - DC-07: `cloudflare-estate-inventory.md`'s canonical token record names "Cloudflare Admin
    2026-07" and its id as the live token, the workstation `~/.dotfiles/secrets/values.age` as its
    origin store (`~/.local/secrets` regenerated from it), and `48efe6a4...` only as the deleted
    predecessor; "ONE" agrees with the second, read-only token. The live id is taken from the
    read-only `GET https://api.cloudflare.com/client/v4/user/tokens/verify` with the bearer from
    `~/.local/secrets` (sourced in the same command); the token value is never printed. If the
    call cannot run, the record takes the id from `secrets/registry.md` and the PR body says it is
    unverified.
  - DC-16: `claude-tooling.md:86-88` and `claude-infra/SKILL.md:79-80` add a CLAUDE.md line only for
    a fact that applies every turn, matching the skill's "strongest form first".
  - DC-22: `claude-md-archive.md:34-42`, the restated visual-fidelity rule set, goes; the skill
    holds every rule.
  - DC-23: `web-content-method.md`'s rubric anchors (:155-160, :169) speak of "each audience the
    site names" and "the site's voice", with no ECXC audience. The ECXC anchors are filed to
    ecxc-ski in the PR's "Found, not done".
  - GA-04, GA-05: `oom-defense.md:45` names only the staged
    `bluefin/etc/systemd/user.conf.d/10-oom-continue.conf`; :76 names no path for the unbuilt shim.
  - DC-06 residual: `fable-post-cutoff-system.md:45` drops "budget #3" and :27 drops "Opus
    5-conducted", pointing at `pass-core` "Models" where a pointer is needed. `model-economy.md` is
    a retired phrase and is never cited.
  - AW-21: the shared measures paragraph moves into a "Reporting" section of
    `skills/writing-voice/evals/tellgrader/MEASURES.md`. Each agent keeps a two-line pointer that
    still carries its report-as-a-table duty and its no-measures fallback inline.
  - `prose-voice-reviewer.md:3`: "the workstation tell catalogue" becomes "the writing-voice
    standard's tells".
  - `omitClaudeMd: true` on `cairn-docs-drafter`, `diff-reviewer`, and `visual-verifier`.
  - `claude-context-budget` joins the `runner` brace list in `.claude/skills/dotfiles-pass/SKILL.md`.
- **Files.** `claude/.claude/docs/{cloudflare-estate-inventory,claude-tooling,claude-md-archive,web-content-method,oom-defense,fable-post-cutoff-system}.md`,
  `claude/.claude/skills/claude-infra/SKILL.md`,
  `claude/.claude/skills/writing-voice/evals/tellgrader/MEASURES.md`,
  `claude/.claude/agents/{cairn-register-editor,prose-voice-reviewer,cairn-docs-drafter,diff-reviewer,visual-verifier}.md`,
  `.claude/skills/dotfiles-pass/SKILL.md`, `claude/.claude/tooling/ratchet-baseline.json`.
- **Risk class.** `runner`.
- **Acceptance.**
  - Baseline entries removed: both `dead-reference` entries in `oom-defense.md` (GA-04, GA-05).
    The `entries` list is now `[]`.
  - `grep -c 'omitClaudeMd: true' claude/.claude/agents/{cairn-docs-drafter,diff-reviewer,visual-verifier,figure-verifier}.md`
    prints 1 for each.
  - `grep -n '48efe6a4' claude/.claude/docs/cloudflare-estate-inventory.md` prints only
    predecessor lines.
  - `grep -n 'tell catalogue' claude/.claude/agents/prose-voice-reviewer.md` prints nothing.
  - The gate prints `gate exit: 0`.
- **Test.** The gate's dead-reference, retired-phrase, and prose legs.
- **Pair.** Wave 3, with F.
- **Estimate.** 105 minutes.

### F. A monthly alignment review that runs itself

- **Outcome.**
  - `model-review.timer` (unchanged, monthly) starts `model-review.service`, whose script
    `bin/.local/bin/model-review-notify` now launches an unattended review instead of only
    notifying. The script finds its repo from its own resolved path, puts the Homebrew bin on
    `PATH` (`claude` is `/home/linuxbrew/.linuxbrew/bin/claude`), and runs `git -C "$repo" pull
    --ff-only` so the run's worktree branches from current `main` (`worktree.baseRef` is `"head"`,
    and the worktree session's isolation checks block a `git -C` into the main checkout, so the
    session cannot pull after its own self-merge). The script keeps `set -uo pipefail` without
    `-e`, so a refused pull leaves the checkout as is and the review runs from local `HEAD`. Then it
    makes two print-mode calls from the repo. The first is `claude -p --model opus --effort medium
    "/doctor prompt-audit"`. The facts probed that form unattended with one path (facts "Probe
    results": 8 turns, $0.78); with no path its default covers `~/.claude` and the repo's
    `.claude/` (the memory page), so the whole-tree cost and duration are unmeasured until the dry
    run. Its report is saved to a temporary file. The second runs `--model opus --effort high` with
    `--permission-mode auto` in a fresh worktree (`-w model-review-<YYYY-MM>`), with the prompt's
    text passed as `"$(cat "$repo/docs/model-review/prompt.txt")"` (pass-core "Launch prompt"), not
    as a path, followed by the report's path. Its one optional argument, `--dry-run`, skips the
    pull and appends a line telling the session to commit locally and stop (no push, no PR, no
    notification). The service's `Description=` says it runs the review.
  - The prompt, in order: read the audit report; read `docs/model-review/state.json` (model ids, Claude Code version, and a
    digest per page) and compare it with the current `claude --version` and model ids; on a change,
    or with no state file, re-fetch the release notes and the pages the parent spec's "Anthropic
    practice" section cites (`docs/specs/2026-09-28-claude-infra-sweep-design.md:608-678`)
    and grade the workstation's rules against them; run the "Monthly review checklist" items
    (`docs/specs/2026-09-04-fable-5-1-infra-update-design.md:124-154`) that still apply
    (items naming retired files are skipped with a reason in the hand-over). A gap becomes a
    one-page design in `docs/specs/` on the branch, with the audit findings it takes,
    pushed to `glw907/workstation` with `notify-send -u normal`, for Geoff's approval. A quiet month appends one line to
    `docs/model-review/log.md`. Either way the run rewrites `state.json` and commits on its branch.
    A quiet month's commit is a hand-over and merges itself (pass-core "Ledgers").
  - ROADMAP "Active", the monthly review entry, says the timer launches the review from the
    committed prompt and drops "raises a reminder".
- **Files.** `bin/.local/bin/model-review-notify`, `upkeep/.config/systemd/user/model-review.service`,
  `docs/model-review/prompt.txt` (new), `docs/model-review/log.md` (new, header only),
  `ROADMAP.md`.
- **Risk class.** `runner` (it launches unattended sessions from a timer).
- **Acceptance.**
  - `systemd-analyze --user verify upkeep/.config/systemd/user/model-review.service` reports no
    error.
  - F commits its files before the dry run, so the run's `-w` worktree, branched from the pair's
    `HEAD`, holds them. The dry run goes through the systemd user manager's environment:
    `systemd-run --user --wait --collect <worktree>/bin/.local/bin/model-review-notify --dry-run`,
    launched with the Bash tool's `run_in_background: true`, since it can outlast the 600-second
    foreground cap. The pair waits for the completion notification (sub-agents page: "When that
    command ends, Claude Code sends the subagent a notification"), and the command exits 0. Its
    worktree's branch, `worktree-model-review-<YYYY-MM>` (the worktrees page: "a new branch named
    `worktree-<name>`"), holds `state.json` and either a `log.md` line or a design, and nothing
    was pushed (`git ls-remote origin 'refs/heads/worktree-model-review-*'` prints nothing). The
    pair reads the hand-over and records the outcome by amending its commit's body. It then runs
    `git worktree unlock` on the dry-run worktree (a `-p` run "leaves the lock it took", the
    worktrees page), `git worktree remove`, and deletes the local branch.
  - The gate prints `gate exit: 0`.
- **Test.** The dry run and the unit verify.
- **Pair.** Wave 3, with D.
- **Estimate.** 145 minutes.

### Wave 4: E and G (a pair)

### E. Chaining in `pass-core`, with H

- **Outcome.**
  - E1, pre-approved designs: Lifecycle step 1 says a design Geoff approves ahead of its pass,
    with unattended planning approved, lets the planning session run steps 2 to 4, write the
    executor's launch prompt, and launch the executor after the "Execute" pre-launch checks,
    without him (design E1: "and the executor's launch unattended"). A plan over twice the design's estimate, or a finding
    that changes the design, stops it with one question in STATUS and `notify-send -u normal`.
  - E2, a "Conductor" section: the conductor watches unattended passes with the Monitor tool over
    `claude agents --json`, opens each PR or design for Geoff in Firefox, merges a PR with `gh pr
    merge <n> --merge` after he approves, pulls the checkout ("Close"), and launches the next
    committed prompt from the main checkout after the "Execute" pre-launch checks. It brings Geoff
    only designs, PR reads, and product or priority calls. No `pass-watch` script exists, so none
    is dropped (facts "E").
  - E3, self-merge: step 6 and "Close" say a pass whose highest class is `ordinary` merges its own
    PR after a green full-suite home and an accepted whole-branch review, when its "Found, not
    done" list is empty; a non-empty list, or a `runner` or `auth-data` pass, keeps Geoff's read.
    Any adapter line that says every PR waits for Geoff is qualified the same way.
  - H(b): "Ledgers" says a cited commit id is one that survives a merge, a merge commit or an id
    on the default branch, since a squash or rebase rewrites ids.
  - H(a): `go-ship` step 2's `code-simplifier` dispatch says "no sub-agents, work serially, one
    gate, one commit".
- **Files.** `claude/.claude/skills/pass-core/SKILL.md`, `claude/.claude/skills/go-ship/SKILL.md`,
  and only if the grep below finds an unqualified line,
  `claude/.claude/skills/{cairn-pass,site-pass}/SKILL.md`. Today it matches only
  `pass-core/SKILL.md:60`. `.claude/skills/dotfiles-pass/SKILL.md` is G's in this wave.
- **Risk class.** `runner`.
- **Acceptance.**
  - `grep -n 'no sub-agents' claude/.claude/skills/go-ship/SKILL.md`, `grep -n 'merge commit'
    claude/.claude/skills/pass-core/SKILL.md`, and `grep -n 'claude agents --json'
    claude/.claude/skills/pass-core/SKILL.md` each print a line.
  - `grep -rn -i 'geoff reads the pr\|geoff merges' claude/.claude/skills .claude/skills` prints
    only lines that carry the `ordinary` exception or sit in `pass-core`'s qualified text.
  - The gate prints `gate exit: 0`.
- **Test.** The gate's reference and prose legs.
- **Pair.** Wave 4, with G.
- **Estimate.** 80 minutes.

### G. `/effort` no longer dirties the repo

- **Method** (facts "G"). The settings page: "If you can't write to that file, for example because
  another tool generates it or links it to a read-only copy ... Set the key in the tool that
  generates the file, or replace the file with one you can write to." So `~/.claude/settings.json`
  becomes a real file that `claude-tooling-sync apply` generates, and Claude Code's own writes land
  in it, outside git. A git clean filter was probed and fails (facts "G").
- **Outcome.**
  - The tracked `claude/.claude/settings.json` drops the machine-local preference keys `model`,
    `effortLevel`, and `modelSettings`, and stow no longer links it: `claude/.stow-local-ignore`
    names it, keeping every default ignore the `claude` package relies on.
  - `claude-tooling-sync apply` writes `<home>/.claude/settings.json` as the tracked file's keys
    over the live file's keys (a key the tracked file does not set keeps its live value), reading
    through and then replacing a symlink with a real file in one `os.replace`. `verify` reports
    drift when the live file is missing or a link, or when a tracked key's live value differs.
    Both take the existing `--home`.
  - `bluefin/bootstrap.sh` runs `apply` after stow if it does not already. `claude-tooling-sync`'s
    docstring and `claude-tooling.md` say the file is generated, not stowed: the layout row
    "Workstation `CLAUDE.md`, `settings.json`", "in the stowed `settings.json`", and "`/effort`
    persists per model into `settings.json` through the stow link" (cited by phrase, since I and
    D edit the file first). The same doc says the tracked keys win at `apply`: a Claude Code
    command that writes a tracked key, such as `/tui` (`tui`) or `/memory` (`autoMemoryEnabled`)
    (settings reference), shows as `verify` drift until the change is committed to the tracked
    file, and the next `apply` reverts it.
  - dotfiles-pass "Close checklist" gains one line: a merge that touches
    `claude/.claude/settings.json` is followed by `claude-tooling-sync apply`, since the live file
    no longer follows a pull.
- **Files.** `claude/.claude/settings.json`, `claude/.stow-local-ignore` (new),
  `bin/.local/bin/claude-tooling-sync`, `tests/test_claude_tooling_sync.py`,
  `claude/.claude/docs/claude-tooling.md`, `.claude/skills/dotfiles-pass/SKILL.md`, and
  `bluefin/bootstrap.sh` if needed.
- **Risk class.** `runner`.
- **Acceptance.**
  - `claude/.stow-local-ignore` names the file as `^/\.claude/settings\.json$`. In a scratch home
    holding a real `.claude/` directory (the live layout: `bootstrap.sh` pre-creates `~/.claude`
    in `STOW_SHARED_DIRS` so stow does not fold it), `stow -n -v -d <worktree> -t <scratch-home>
    claude` lists no `.claude/settings.json` link and still lists every other `claude/.claude`
    entry. An empty scratch home folds `.claude` whole and cannot show this.
  - The pytest cases below pass. No manual `apply` runs: `apply` reads the tracked file from
    `<home>/.dotfiles/` and runs the real `claude mcp add-json` for any manifest server missing
    from `<home>/.claude.json`, so only the fixture home, with its empty servers manifest and
    stub `claude`, is safe.
  - The gate prints `gate exit: 0`.
- **Test.** In `tests/test_claude_tooling_sync.py`, by subprocess like the existing tests.
  `fixture_home` also writes a live `<home>/.claude/settings.json`, so
  `test_verify_passes_with_no_collision` survives the missing-file rule. Cases: `apply` replaces a
  symlink with a real file and keeps live-only keys; a second `apply` changes nothing; `verify`
  fails on a missing file, a link, and a changed tracked key, and passes on a live-only key. The
  cutover case: a live real file holding an old tracked copy with `model`, `effortLevel`, and
  `modelSettings`; `apply` leaves the new tracked keys plus those three, and `verify` passes; the
  test then writes a new `modelSettings` entry into the live file, `verify` still passes, and the
  fixture's tracked `settings.json` is byte for byte unchanged.
- **Pair.** Wave 4, with E.
- **Estimate.** 70 minutes.

### Close

Per pass-core "Close" and dotfiles-pass "Close checklist", in order:

1. `git fetch origin` and merge `origin/main` into the branch (a conflict is a stop). Then the gate
   on the close head prints `gate exit: 0` (the full-suite home).
2. `diff-reviewer` at whole-branch scope reads the branch against this plan and the design,
   loading `python-conventions` (`bin/.local/bin/claude-tooling-sync` and the tests). One batched
   fix chain follows if it returns `fix`, each finding quoted verbatim as the fix's acceptance, then
   the gate again.
3. `claude-tooling-sync verify` (the stowed `main` copy, a machine-state check) passes, and one
   `gitleaks git` branch-history scan is clean.
4. The next step's prompt, committed as
   `~/Projects/poplar/docs/plans/2026-10-11-poplar-adapter-planning-prompt.txt` in the shape of
   `docs/plans/2026-10-11-infra-sweep-2-planning-prompt.txt`: an attended planning
   session in `~/Projects/poplar` that designs, with Geoff, poplar's `pass-core` adapter (ROADMAP
   "Planned", "Poplar adopts `pass-core`", including its CLAUDE.md "Conducting a pass" section and
   the agent repins), and logs poplar's refactor to Charm's Bubble Tea model (`elm-conventions` as
   this pass leaves it) as its own pass in poplar's ROADMAP. It carries Anthropic's two scope
   samples verbatim (pass-core step 1).
5. `docs/STATUS.md`: the infra sweep line moves to "merged" on Geoff's merge. The next action
   starts with G's two pre-merge cutover commands (step 6), to run before the merge. It then names
   that prompt with the exact line `cd ~/Projects/poplar && claude --model opus --effort high --name
   poplar-adapter-plan "$(git -C ~/.dotfiles show main:~/Projects/poplar/docs/plans/2026-10-11-poplar-adapter-planning-prompt.txt)"`.
6. Push `glw907/workstation`, open the PR (draft until the close is done), and write its body. Its
   first line tells the merger to run G's two pre-merge commands before merging, because whoever
   merges pulls at once (pass-core "Close"), and a pull while `~/.claude/settings.json` is still a
   link would drop today's preferences or be refused over a dirty file:
   - what landed (task id, commit), the review verdict, and every trigger table;
   - "What goes live": the skill and agent text at once; the timer's next monthly fire launching
     the review; and G's cutover, in order. Before the merge, `cp --remove-destination "$(readlink
     -f ~/.claude/settings.json)" ~/.claude/settings.json` turns the link into a real file that
     keeps today's `model`, `effortLevel`, and `modelSettings` (the merged tracked file no longer
     holds them), and `git -C ~/.dotfiles checkout -- claude/.claude/settings.json` drops any
     `/effort` write the link left in the tracked file, which the real file now holds. Then the
     merge and its pull. Then `~/.local/bin/claude-tooling-sync apply` lays the tracked keys over
     the real file. The live check follows: a `/effort` change leaves `git -C ~/.dotfiles status
     --porcelain` empty. Rollback is `git revert -m 1 <merge>` on `main`, a pull, `rm
     ~/.claude/settings.json`, and `stow -R claude` to restore the link;
   - "Found, not done", each with now, defer, or drop and a reason: DC-23's ECXC anchors (ecxc-ski
     ROADMAP); aksailingclub-org's `project-tracking.json` taking `"backlog": false`; the review's
     dry-run findings; plus anything the tasks found;
   - the score rows (pass-core "Score"; `cairn-run-gate --records <toplevel> <branch>` for gate and
     lock time).

   Open the PR in Geoff's browser (`gh pr view <n> -R glw907/workstation --web`) and stop: a
   `runner` pass keeps Geoff's read, and the session never merges. No `stow -R bin` is owed (no new
   script).
- **Estimate.** 75 minutes.

## Later

Raised while planning, beyond the design, never a task here: a spend cap (`--max-budget-usd`) on
the monthly review; pointing the 2026-10-11 conductor prompt file at `pass-core`'s new section;
poplar's copy of `kitty-shot`, which `tui-visual-verify` no longer ships.
