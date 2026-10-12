You are the conductor for drafter Pass 0. The planning session (dotfiles-5a) prepared the pass and
closed. Your job is to launch the executor, watch it, put its two PRs before Geoff, merge them on
his approval, and finish the close. You write no feature code.

Load `pass-core` and read its "Conductor", "Execute", and "Close" sections. Then read the plan
whole: `docs/superpowers/plans/2026-10-12-drafter-pass0-plan.md` in `~/.dotfiles`, especially
"Standing approvals", "Close", and "Launch". The design behind it is
`docs/superpowers/specs/2026-10-12-drafter-pipeline-design.md`.

Already done by the planner: the spec, plan, and reviews are merged to dotfiles `main`; the
checkout is on `main`; `~/Projects/drafter` exists with `go.mod` and a README on `main`, pushed to
the public repo `glw907/drafter`. The dotfiles repo's GitHub name is `glw907/workstation`. The
uncommitted `bash/.bashrc` change in `~/.dotfiles` belongs to another session: never touch it.

1. Pre-launch. Run pass-core "Execute"'s checks on `~/.dotfiles`: `git -C ~/.dotfiles fetch origin`,
   the checkout on `main`, `git -C ~/.dotfiles rev-list --count HEAD..origin/main` printing 0, and
   `.claude/worktrees/` ignored. Confirm with `claude agents --json` that no other session is
   executing in `~/.dotfiles` or `~/Projects/drafter`. Any failure is a stop: tell Geoff with
   `notify-send -u normal` and wait.
2. Launch, from `~/.dotfiles`:
   `claude --bg --model sonnet --effort medium --name drafter-pass0 --add-dir ~/Projects/drafter "$(cat docs/superpowers/plans/2026-10-12-drafter-pass0-executor-prompt.md)"`
   Record the session's name and id.
3. Watch with the Monitor tool over `claude agents --json`, reading each field with `.get`. When the
   executor stops, read its STATUS question. Answer from the plan's standing approvals where they
   apply (an overrun continues while the pass stays under 900 task-minutes). Bring Geoff only
   design, product, or priority calls, by `notify-send -u normal`. Never send the executor an
   approval Geoff didn't give; it refuses peer approvals, rightly.
4. When both PRs are open, put them on the review desk as background Bash commands, drafter first:
   `review-desk pr glw907/drafter "<title>" <n>`, then
   `review-desk pr glw907/workstation "<title>" <n>`, then the dotfiles PR's "Found, not done" items
   as one `review-desk triage` item. Wait for each decision.
5. On approval, merge in order, per pass-core "Close": the drafter PR first with
   `gh pr merge <n> -R glw907/drafter --merge --match-head-commit <head>`, running its
   `## Before merge` steps as that section says (switch `~/Projects/drafter` to `main`, pull, and
   `make -C ~/Projects/drafter install`); then the dotfiles PR the same way on `glw907/workstation`.
   Then `git -C ~/.dotfiles pull --ff-only` when pass-core's conditions hold, and run `check-drift`.
   On a reject, relaunch or message the executor with Geoff's note to fix forward.
6. Act on the triage rows as pass-core says. The cairn follow-up the plan names (cairn's review page
   must read `.plan.yaml` before the next chain run uses YAML plans) has disposition "now": file it
   where Geoff's triage puts it.
7. Tell the cairn docs sessions (`cairn-cms-aa`, `draft-docs-2b-part1`, if still running) the merge
   time and that `planFormat: "markdown"` keeps the old behavior for a run in flight. Note that
   Geoff intends to have `cairn-cms-aa` prepare YAML plans next.
8. Report to Geoff in one short message what landed, then end.
