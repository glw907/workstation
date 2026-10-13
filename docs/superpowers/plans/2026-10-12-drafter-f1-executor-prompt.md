You are the executing session for drafter F1: the plan-format additions from cairn's 11-plan test.

Load `pass-core`, then the `dotfiles-pass` adapter, then `go-conventions` before writing any Go.
Follow them. Where they and this prompt disagree, this prompt's specifics win.

Plan, the source of every task: `docs/superpowers/plans/2026-10-12-drafter-f1-plan.md` in
`~/.dotfiles`. Read it whole first. The interim format sheet it folds in is
`/var/home/glw907/.local/share/drafter/plan-format-v1.md`. The Pass 0 plan,
`docs/superpowers/plans/2026-10-12-drafter-pass0-plan.md`, is background only.

How to work:
- Your first act is `EnterWorktree` in `~/.dotfiles`. Your working directory stays in that worktree
  for the whole pass, and the clock file lives in its git dir. You change nothing in dotfiles.
- drafter lives at `~/Projects/drafter`, on `main` at `140bc00`. Before F1.1, create an `f1` branch
  there with `git -C`. Every drafter command takes a path (`git -C`, `make -C`, `go -C`). Never
  `cd` there.
- Push target: `glw907/drafter`. Push only the `f1` branch.
- The drafter repo is public. Keep every workstation path, account detail, key, and copied cairn
  content out of it. Fixtures are synthetic, like Pass 0's fictional "Lumen" project.
- Never touch `bash/.bashrc` in the dotfiles main checkout. Its uncommitted change belongs to
  another session.
- Gate: `bash scripts/drafter-gate.sh` from your dotfiles worktree. The full-suite home is that
  gate, once, on the close head.
- A stop the plan doesn't answer (a finding that changes the design, or a blocker you can't
  resolve) runs `notify-send -u normal`, names the question in your final message, and waits.
  Under 330 task-minutes (twice the estimate), an overrun continues without a stop.
- Arm the API-drop wake-up (`/loop` with no interval) per `~/.claude/docs/unattended-work-guards.md`.

At close, follow the plan's "Close" section. It merges the PR itself only when the review accepted
and "Found, not done" is empty. Otherwise it stops at PR-ready. Don't run `review-desk`. The
conductor session that launched you, `drafter-conductor`, handles the desk. End with one message
naming the PR, whether it merged, and the merge commit if it did.
