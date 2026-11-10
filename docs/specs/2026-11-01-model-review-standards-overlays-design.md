# Give workstation rules a home the plugin skills load

## Brief

The cutover to the `standards` plugin removed the notes that corrected vendored skills for this
workstation, because the plugin must stay portable. A session running `vale-setup` now follows steps
this workstation rejects. This design adds one path-scoped rule, one sentence in `spec-plan-review`,
and one description overlay. Approving it starts one small `runner` pass here and a one-sentence
change in `glw907/standards`.

## Gap

`vendored-skills.json` now says of a `home: standards` entry that "its `note` overlay never applies".
Commit `322d136` deleted the `vale-fix`, `vale-setup`, `vale-ci`, and `vhs-cli-demos` notes. Their
text moved to `claude/.claude/docs/claude-tooling.md`, which no skill loads. In the plugin:

- `vale-setup:52, 72` says to gitignore `StylesPath` and not to commit it, but these repos commit it.
- `vale-fix:59, 83` says one branch and one PR per file, but a fix here lands on the pass branch.
- `receiving-code-review:44-45, 83` says to stop and ask, and the unattended fold in
  `spec-plan-review` loads it. A mid-run question is a planning miss under `CLAUDE.md`.
- `golang-spf13-cobra`'s description names two samber skills that aren't installed, and it rides in
  every session's listing.

## Evidence

- Claude Code memory: "Personal rules in `~/.claude/rules/` apply to every project on your machine",
  and "A path-scoped rule loads when Claude uses the Read, Write, or Edit tool on a matching file"
  (<https://code.claude.com/docs/en/memory>). So the rule reaches `vale-setup` at the moment it
  writes `.vale.ini`, before its gitignore step.
- The same page: "if two instructions contradict each other, Claude may pick one arbitrarily".
- `glw907/standards` README: "Anything in it works in any repository, with no machine-specific tool
  or path assumed." A workstation rule can't go in the plugin's skills.

## Proposed change

1. Add `claude/.claude/rules/vale.md`, scoped with `paths:` to `**/.vale.ini` and `**/styles/**`. It
   states that a repo here commits its styles and pins Vale in CI, that this replaces `vale-setup`
   step 5 and `vale-fix` steps 3 and 6, and that a fix lands on the pass branch.
2. Cut the Vale sentence in `claude-tooling.md` to a pointer at that rule, so it has one home.
3. In `standards:spec-plan-review`, add to the fold step: "An unattended fold records an unclear
   finding as refused or as an owner fork, and never stops to ask." This is portable, so the
   vendored skill stays untouched.
4. Add a `description` overlay for `golang-spf13-cobra` in `vendored-skills.json` that drops the two
   "see" sentences. The overlay still applies to plugin skills, and it helps PR #184's listing budget.
5. Probe in a scratch repo: run `vale-setup` and check that the rule loads when `.vale.ini` is
   written, and that `styles/` stays out of `.gitignore`.

`claude/.claude/rules/` would be the workstation's first rule file. `claude-tooling-sync` and
`claude-context-budget` don't scan a rules directory, and the 2026-09-28 sweep dropped that support
because no rule existed. The pass adds the directory to the budget check and the layout table in
`claude-tooling.md`, with no new script.

Two audit findings take no change. On #13, `vhs-cli-demos:24` defers to `tui-design`, and the tool
order in `claude-tooling.md` governs, while a missing `vhs` fails loudly. On #14, `CLAUDE.md` already
says the admin design system beats the daisyUI skill, and the `survey` skill routes other house UI.

This is `runner` by `dotfiles-pass`.

## Audit findings taken

From the full-tree report: 3, 4, 6, 12, 13, and 14.
