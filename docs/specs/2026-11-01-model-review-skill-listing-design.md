# Bring the skill listing back under budget

## Brief

Claude Code's skill listing is over budget by about 7,400 characters, so it drops descriptions in
every session. Today the loss falls on claude.ai skills Geoff rarely uses, but the rule that picks
them depends on usage and could reach a workstation skill. This design hides the descriptions of
the skills that lose them today, plus a few unused Cloudflare ones, at no context cost. Approving it
starts one small `runner` pass.

## Gap

A probe on 2026-11-01 with `claude -p --debug-file` logged:
`Skill listing over budget: 92 skills, 37422 chars > 30000 budget`.

This session's listing shows ten `anthropic-skills:` entries with no description: `docs`, `pptx`,
`xlsx`, `computer-use`, `docx`, `built-in-browser`, `chrome-browser`, `pdf`, `morning`, and
`skill-creator`. Those ten descriptions total 7,466 characters, which accounts for the overage.

`claude-tooling-sync` caps each description at 500 characters, and nothing checks the total.

## Evidence

Skills page (<https://code.claude.com/docs/en/skills>): "When the listing overflows, Claude Code
drops descriptions starting with the skills you invoke least", which "removes the keywords Claude
needs to match your request". The budget "scales at 1% of the model's context window". The same page
offers `skillListingBudgetFraction` and a `skillOverrides` state, `"name-only"`, that lists a skill
"without a description".

## Proposed change

1. Add a `skillOverrides` block to `claude/.claude/settings.json` that sets those ten skills to
   `"name-only"`.
2. Set `cloudflare:k2`, `cloudflare:basin`, `cloudflare:nextjs-on-cloudflare`, and the three
   `cloudflare:sandbox-*` skills to `"name-only"` as well. No `package.json` or wrangler config under
   `~/Projects` references those products, and they free about 1,400 characters of margin.
3. Run `claude-tooling-sync apply`, then repeat the probe. The acceptance test is that the warning
   is gone. Confirm the key form for a plugin skill in that probe.
4. Add one line to `docs/model-review/prompt.txt`: run the probe each month and treat the warning as
   a gap.

I chose `skillOverrides` over raising the fraction. The higher fraction would add about 1,900 tokens
to every session to carry descriptions nobody here triggers. The names stay listed, so `pdf` and
`docx` still match by name, and every skill stays in the `/` menu.

This is `runner`. It adds no script and no gate.

## Audit findings taken

None. The audit checked plugins by grep signals and doesn't run the listing.
