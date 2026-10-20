# Infra sweep 2: probed facts (2026-10-11)

The planning session read each sweep-2 finding against the tree at `40fcae1` (branch
`worktree-infra-sweep-2`). Three read-only Sonnet agents covered A, B and C, and D. The session
probed E to I itself. Paths are under `claude/.claude/` unless they start with `.claude/`,
`bin/`, `docs/`, or `~`. The audit is `claude/.claude/docs/record/2026-09-28-claude-infra-audit.md`
section 5, and several of its line numbers have moved; the lines below are current.

## A. Go skills

- `go version` prints `go1.27.2`. cairn `tool/go.mod:3` says `go 1.26.0`; poplar `go.mod:3` says
  `go 1.26`.
- **CS-1.** `skills/go-conventions/SKILL.md:219-232` is the cobra root template; it sets
  `SilenceUsage: true` (:228) and not `SilenceErrors`. `main.go` (:255-259) prints the error, and
  :263 says `main()` is the only printer. Cobra v1.10.2 `command.go:1159` prints unless
  `SilenceErrors` is set, so every error prints twice. cairn `tool/cmd/cairn/root.go:191-195` sets
  both fields.
- **CS-2.** No precedence line in `go-conventions`. The `_why` half is already fixed
  (`tooling/vendored-skills.json:21` names no `elm-conventions`). Contradictions with the vendored
  `skills/golang-spf13-cobra/SKILL.md`: a package-level `rootCmd` (:71, :134) against
  `newRootCmd()` and "Avoid" init (go-conventions :220, :64); testify (:135-137) against "No
  third-party assertion libraries" (:319); `cmd.OutOrStdout()` (:126) against stderr/stdout rules
  (:296, :584-585); viper in `PersistentPreRunE` (:62, :147) against "cobra for CLI, nothing else
  assumed" (:457-458).
- **CS-4.** `:592` "(currently 1.26.1)" (the ratchet `retired-phrase` fingerprint `currently
  1.26`); `:84` "The Go we have is 1.21–1.26."; `:363` "Poplar runs `make check-deep`
  (gremlins)" (poplar's Makefile has neither); `:335` cites "ADR-0230's Pass 40.1" (only in
  poplar's archived plans); `:408` "No code generation, no build tags, no CGO." Poplar's gate uses
  test-only tags: `Makefile:131-133` `tagged-vet` (`-tags "conformance live"`, `-tags perf`),
  `:187` `go test -tags perf`.
- **CS-7.** `skills/tui-visual-verify/SKILL.md:37-39` tells a repo to copy `scripts/kitty-shot` in;
  `:59-64` documents `-d`, the on-desktop path; `:66` is its usage line; `:143-144` names an
  `import -window` fallback. `bin/.local/bin/kitty-headless-shot` exists with the same step
  vocabulary and no `-d` (usage at its :11-13). `magick -list configure` DELEGATES has no x11. The
  template `skills/tui-visual-verify/scripts/kitty-shot` (145 lines) wraps the headless tool and
  keeps `-d`. Other mentions: `docs/bluefin-admin.md:245`, `bin/.local/bin/kitty-headless-shot:52`.
- **CS-11.** `skills/ts-conventions/SKILL.md:86-122` carries an inline copy-in ESLint config
  (`files: ['src/lib/**/*.ts']`, no em-dash rule, no `.svelte` block). `~/Projects/cairn-cms/eslint.config.js`
  has the `house/no-em-dash-in-comments` rule (:10-29, :61, :89) and a `.svelte` block (:91-107).
- **CS-13.** Error strings stated three times: Error Handling (:265-296, canonical), rubric item 6
  (:529-530), `### Error strings` (:558-571). The unexported-godoc default three times: :499-502,
  rubric steps 1-2 (:509-513), `### Unexported godoc default` (:552-556).
- **Size.** `go-conventions` is 592 lines. Reference-shaped sections: Modern Stdlib Idioms
  (:82-189, 108 lines), Build System (:383-409, 27), Linting (:410-454, 45), Comments (:472-581,
  110). The skill dir holds only `SKILL.md`. No file cites a `go-conventions` heading by name, so a
  split breaks no citation.
- **Descriptions.** `go-conventions` 530 code points, `tui-visual-verify` 534; neither has `paths:`.
  Both carry `description-cap` baseline entries (GA-06, pass D).

## B. Cairn-facing skills and agents

- **PS-02.** `skills/cairn-release/SKILL.md:52-66` hand-lists the release gate. cairn-cms
  `package.json:85` has `check:close` (`scripts/checks/close-prebuilt.mjs`, 40 components including
  `check:version`, `check:facts`, `check:vale`, `check:visuals`; not `npm test`).
- **PS-03.** `cairn-release/SKILL.md:149` names `docs/guides/upgrade-cairn.md`; cairn-cms has
  `docs/extend/upgrade-cairn.md`.
- **PS-05.** `skills/cairn-figure/SKILL.md:132` heading "## The gates do not exist yet", body
  :134-140 and :143. cairn-cms `package.json:59` defines `check:visuals` (it checks mermaid
  `accTitle:`/`accDescr:`, captions, alt length, `repro` fences); `check:figures` does not exist.
  Restated alt rules at :67-74. The register's section is `## Visuals (every page that carries one)`
  at cairn-cms `docs/internal/docs-register.md:687`.
- **PS-06.** `skills/register-check/SKILL.md` (`context: fork`): :10 "the file under discussion",
  :11 "unless Geoff has delegated application", :28 "session-specific sanctioned phrases", :62
  "(apply if delegated)", :74 "during the session", :76 "before the session ends".
- **PS-17.** `skills/engine-consult/SKILL.md:30` and :33-37 define "Facts consulted" two ways;
  `site-pass/SKILL.md:16-17` points at `engine-consult`. `site-pass/plan-template.md` no longer exists
  (deleted in `d732c42`), so the template half is gone.
- **PS-18.** `engine-consult/SKILL.md:18-19` ", including a prior pass's pass-end draft".
- **PS-19.** `register-check/SKILL.md:3` and :9 say "three-gate"; the body runs four gates (:13,
  :25, :31, :41).
- **PS-28.** `cairn-release` description 849 code points (:3-12), `visual-fidelity` 672 (:3);
  neither has `paths:`.
- **AW-14.** `agents/daisyui-a11y-reviewer.md:85` cites `docs/internal/engine-rulings.md` and
  `docs/internal/admin-design-system.md` bare; both exist only under `~/Projects/cairn-cms/`.
- **AW-15.** `agents/figure-verifier.md:14-15` and :18 read the register at the main checkout's
  absolute path.
- **AW-22.** The engine standard is quoted in `agents/engine-triage.md:31-57` (its :34 comment says
  the same block lives in `engine-consult`) and `skills/engine-consult/SKILL.md:70-101`.
- **PS-20.** `skills/content-review/SKILL.md:46-48` (`context: fork`), step 7: Ask "apply all,
  apply some (specify), or skip?".
- **svelte-check.** `skills/svelte-check/SKILL.md:3`, an unquoted plain scalar of 599 code points;
  `yaml.safe_load` fails at line 3, column 487 (`Scope:`).

## C. Site and generic skills

- **PS-08.** `skills/content-draft/SKILL.md:12-13` and `skills/content-review/SKILL.md:13-14`
  require `docs/content-guide.md`; only ecxc-ski has one.
- **PS-10.** `skills/log-issue/SKILL.md` finds the backlog through `.claude/project-tracking.json`'s
  `backlog_path`; :39-42 creates a missing file, :168 hardcodes `git add BACKLOG.md`, :201 says it
  lives at the root. aksailingclub-org's `project-tracking.json` `note` says the repo keeps no
  BACKLOG by doctrine; no repo sets a `backlog` flag yet.
- **PS-21.** `skills/dependency-upgrade/SKILL.md:60-61` names `docs/internal/record/` family-wide;
  only cairn-cms has it.
- **PS-09 residual.** `skills/site-pass/SKILL.md:14-15` and :64-65 hardcode `docs/`;
  aksailingclub-org uses `docs/plans/`, cairn-pub has neither. :62 also hardcodes
  `docs/architecture.md` (aksailingclub-org has none).
- **PS-11 residual.** `skills/log-project/SKILL.md:98-103`, a `## Done` block in the example
  roadmap; the close procedure (:117, :146-151) is already fixed.

## D. Docs and agents

- **DC-07.** `docs/cloudflare-estate-inventory.md:11-13` names "Cloudflare Admin" `48efe6a4...` as
  the one live token in the ASC store; :17-19 names the live "Cloudflare Admin 2026-07"
  `1d508f1a...`; :28-29 records `48efe6a4...` as deleted; :36 adds a second, read-only token. The
  origin store is the workstation `~/.dotfiles/secrets/values.age` (`scripts/secrets/secret-set.sh:34`,
  `secrets/registry.md:4`, :219-246). A read-only `GET
  https://api.cloudflare.com/client/v4/user/tokens/verify` returns the live id (the `user/` path,
  per the inventory's :46).
- **DC-16.** `docs/claude-tooling.md:86-88` "add the CLAUDE.md line" for every new server, against
  `skills/claude-infra/SKILL.md:22` and :55-56 (strongest form first).
- **DC-22.** `docs/claude-md-archive.md:34-42` restates the visual-fidelity rule set the skill
  already holds (`skills/visual-fidelity/SKILL.md:9-10`, :19, :34, :56). `CLAUDE.md:133-135` is
  already a pointer; the global CLAUDE.md stays untouched (195 of 200 lines).
- **DC-23.** `docs/web-content-method.md:155-160` and :169 anchor the rubric on ECXC's two audiences
  and coach voice.
- **GA-04, GA-05.** `docs/oom-defense.md:45` names `~/.config/systemd/user.conf.d/` (never adopted;
  the tree stages `bluefin/etc/systemd/user.conf.d/10-oom-continue.conf`); :76 names
  `~/.local/bin/scoped-test` (never built).
- **DC-06 residual.** `docs/fable-post-cutoff-system.md:45` "budget #3"; :27 "the Opus
  5-conducted session". `model-economy.md` is a retired phrase (`tooling/retired-phrases.txt:129`);
  the live home is `pass-core` "Models".
- **AW-21.** `agents/cairn-register-editor.md:72-81` and `agents/prose-voice-reviewer.md:35-44`
  carry the same measures paragraph; both link
  `skills/writing-voice/evals/tellgrader/MEASURES.md`, which defines the measures and holds no
  reporting instruction.
- **prose-voice-reviewer.** `agents/prose-voice-reviewer.md:3` "the workstation tell catalogue";
  `docs/authoring-charter.md:22-23` says the workstation keeps no house lexicon.
- **omitClaudeMd.** None of `cairn-docs-drafter`, `diff-reviewer`, `visual-verifier`,
  `figure-verifier` sets it. The subagents page
  (<https://code.claude.com/docs/en/sub-agents>): "Set to `true` to launch this subagent without
  the user, project, and local CLAUDE.md files ... Use it for subagents that take everything they
  need from the delegation prompt ... Requires Claude Code v2.1.271 or later". Installed: 2.1.296.
- **Path map.** `.claude/skills/dotfiles-pass/SKILL.md:30-32`, the `runner` brace list lacks
  `claude-context-budget`.

## E and H. Chaining and the dubplate facts

- The conductor prompt is `docs/plans/2026-10-11-conductor-prompt.txt`. No `pass-watch`
  script exists in the tree, so dropping it is a no-op.
- **H(a).** `skills/go-ship/SKILL.md:28-34`, step 2 "Simplify", dispatches
  `code-simplifier:code-simplifier` with no serial or single-commit instruction.
- **H(b).** `skills/pass-core/SKILL.md` "Ledgers" has no commit-id rule.

## F. The monthly review

- `upkeep/.config/systemd/user/model-review.timer` (`OnCalendar=monthly`, `Persistent=true`) runs
  `model-review.service`, whose `ExecStart=%h/.local/bin/model-review-notify` only calls
  `notify-send`.
- The checklist is "Monthly review checklist" in
  `docs/specs/2026-09-04-fable-5-1-infra-update-design.md:124-154`; ROADMAP "Active"
  carries the release-trigger line (`ROADMAP.md:10-24`). The pages to re-fetch are those the
  "Anthropic practice" section cites
  (`docs/specs/2026-09-28-claude-infra-sweep-design.md:608-678`).
- The memory page (<https://code.claude.com/docs/en/memory>): "run `/doctor prompt-audit` in a
  session ... You get a report of findings with proposed edits, and nothing in your files changes
  until you ask Claude to apply them." "By default, the audit covers your CLAUDE.md ... plus the
  rules, skills, commands, subagents, and output styles under `.claude/` and `~/.claude/`." It
  "requires Claude Code v2.1.283 or later". The headless page: "Built-in commands that only run in
  the terminal interface, such as `/login`, aren't available." The unattended probe is recorded
  below under "Probe results".

## G. `/effort` and the tracked settings file

- `~/.claude/settings.json` is a stow link to `~/.dotfiles/claude/.claude/settings.json`, which holds
  `model`, `effortLevel`, and `modelSettings` beside the hooks and permissions.
- The settings-reference page: "When you run `/effort low`, `medium`, `high`, or `xhigh` in an
  interactive session on your machine, Claude Code saves the level for the active model under
  `modelSettings`". The settings page: "When you save a choice for new sessions from inside Claude
  Code, such as a default model with `/model`, Claude Code writes it to your user settings file,
  `~/.claude/settings.json`. If you can't write to that file, for example because another tool
  generates it or links it to a read-only copy, the change applies to the current session and is
  gone in the next one. Set the key in the tool that generates the file, or replace the file with
  one you can write to." User settings is the lowest level; `--settings` and managed settings both
  outrank it, so neither can hold the tracked hooks without a launch wrapper or `/etc` policy.
- Probe: a git clean filter that drops the preference keys leaves `git diff` empty but `git status
  --porcelain` still lists the file (scratch repo, 2026-10-11), so it fails the design's check.

## I. Charm's model

- Primary source: `charmbracelet/crush` `internal/ui/AGENTS.md`, blob `d21034fe`, last changed in
  commit `f02ffbcec15a9f95cb9bcff895833df10f829aae` (2026-07-31), 239 lines, read with `gh api`.
  The repo's `LICENSE.md` is "Functional Source License, Version 1.1, MIT Future License"
  (FSL-1.1-MIT): cite and distill, never copy.
- Its load-bearing rules, by line: "Never use commands to send messages when you can directly
  mutate children or state." (:5-6); "Create files if needed to separate logic; do not nest
  models." (:8); "Never do IO or expensive work in `Update`; always use a `tea.Cmd`." (:9); "Never
  change the model state inside of a command." (:10-11); ANSI-safe string handling through
  `charmbracelet/x/ansi` (:12-18); "The `UI` model is the **sole Bubble Tea model**" with
  sub-components as "stateful structs with imperative methods that the main model calls directly"
  (:58-61); new components "Expose imperative methods for state changes (not `Update(tea.Msg)`)",
  "Return `tea.Cmd` from methods when side effects are needed", render via `Render(width int)
  string` or `Draw(scr, area)`, and "Let the main `UI.Update()` decide when and how to call into
  the component" (:71-77); lipgloss v2 `Width(n)` is the total box width, size to the content area,
  pad never margin, render styled segments individually (:165-191); "Use `tea.Batch()` when
  returning multiple commands", prefer methods over inline `tea.Cmd` functions (:217-222).
- Secondary: the Bubble Tea v2 discussion (<https://github.com/charmbracelet/bubbletea/discussions/1374>,
  "Bubble Tea v2: What's New in v2") and the latest release, `v2.1.0` (2026-10-08).
- `skills/elm-conventions/SKILL.md` is 582 lines; its description and Rule 4 carry "children signal
  parents via Msg types"; it cites `~/.claude/docs/bubbletea-conventions.md` (:332) and poplar
  research paths (:270, :329, :345) and helpers (`displayCells`, :300, :571). Root `View() string`
  examples sit at :68, :203, :276, :308, :434 (CS-12). `docs/bubbletea-conventions.md` (648 lines)
  is cited only by `elm-conventions` and records.
- `skills/bubbletea-design/SKILL.md` (285 lines): CS-5's live-desktop kitty launch at :19-27, tmux
  captures as verification at :212-216, `lipgloss.Width()` for icon width at :54, :70, :183, :275,
  :279.
- The `tui-design` plugin (gfargo, MIT, <https://github.com/gfargo/tui-design-skill>) is installed
  and enabled at user scope (`claude plugin list`: version 1.6.0). `docs/claude-tooling.md:125-128`
  lists it among the plugins with no rule of use, and :125-126 says `go-conventions` and
  `elm-conventions` "stay mandatory" beside the cobra skill.

## Probe results

- **Prompt audit, unattended.** `claude -p --model opus --effort medium --output-format
  stream-json --verbose "/doctor prompt-audit claude/.claude/skills/go-ship"`, run from this
  worktree, invoked the bundled `doctor` skill (listed in the init event's slash commands), took
  8 turns at an estimated $0.78, and returned a findings table with proposed edits and no file
  changes. So the audit runs in print mode as a slash-command prompt. The run printed a notice that
  `ANTHROPIC_API_KEY` takes precedence over the claude.ai login in this shell.
- **CLI.** The CLI reference lists `--worktree`/`-w` ("Start Claude in an isolated git worktree at
  `<repo>/.claude/worktrees/<name>`"), `--permission-mode` (`default`, `acceptEdits`, `plan`,
  `auto`, `dontAsk`, `bypassPermissions`), and `--max-budget-usd` ("print mode only").
- **PATH.** `claude` resolves to `/home/linuxbrew/.linuxbrew/bin/claude`. `model-review-notify`
  sets `PATH="$HOME/.local/bin:/usr/bin:$PATH"`, which does not include the Homebrew bin, so a
  launcher run by the systemd user manager must add it.
- **Reference scan.** `scripts/check-claude-refs.py` excludes `docs/record` (its :129), so the
  audit record's mention of `bubbletea-conventions.md` cannot fail `dead-reference` after the file
  is deleted.
