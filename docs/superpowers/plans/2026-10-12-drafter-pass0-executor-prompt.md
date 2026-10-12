You are the executing session for drafter Pass 0: the YAML plan format and the `drafter check-plan`
validator, plus the docs page chain's switch to YAML plans.

Load `pass-core`, then the `dotfiles-pass` adapter, then `go-conventions` before writing any Go.
Follow them; where they and this prompt disagree, this prompt's specifics win.

Plan, the source of every task: `docs/superpowers/plans/2026-10-12-drafter-pass0-plan.md` in
`~/.dotfiles` (read it whole first, including "Standing approvals" and "Launch"). Spec section it
builds: "The plan format" in `docs/superpowers/specs/2026-10-12-drafter-pipeline-design.md`.

How to work:
- Your first act is `EnterWorktree` in `~/.dotfiles`. Your working directory stays in that worktree
  for the whole pass, and the clock file lives in its git dir, per the plan.
- drafter lives at `~/Projects/drafter` (already created: `go.mod` and a README on `main`, pushed to
  the public repo `glw907/drafter`). Before T1, create a `pass0` branch there with `git -C`. Every
  drafter command takes a path (`git -C`, `make -C`, `go -C`); never `cd` there.
- Push targets: `glw907/drafter` for `~/Projects/drafter`, and `glw907/workstation` for
  `~/.dotfiles` (the dotfiles repo's GitHub name is `glw907/workstation`; `glw907/dotfiles` only
  redirects). Push only branches you created.
- The drafter repo is public. Keep every workstation path, account detail, key, and copied cairn
  content out of it; fixtures are synthetic, per the plan.
- Never touch `bash/.bashrc` in the main checkout. Its uncommitted change belongs to another
  session.
- Do not edit `docs-page-chain.js` outside your dotfiles worktree. Other sessions run the live
  chain from the main checkout.
- Gates: `bash scripts/gate.sh` for dotfiles, and from T1 `bash scripts/drafter-gate.sh` for
  drafter, both from your dotfiles worktree. Each full-suite home is that gate, once, on the close
  head. There is no CI watch.
- Apply the plan's standing approvals in place of stopping. A stop with no standing answer (a
  finding that changes the design, a blocker you can't resolve) writes `docs/STATUS.md` with one
  question, runs `notify-send -u normal`, and waits.
- Arm the API-drop wake-up (`/loop` with no interval) per `~/.claude/docs/unattended-work-guards.md`.

At close, run everything the plan's "Close" section names, then open both PRs (`glw907/drafter`
first, then `glw907/workstation`), each body naming the other and carrying what pass-core "Close"
requires. Do not merge either PR and do not run `review-desk`: the conductor session that launched
you puts both PRs before Geoff and merges them. Report both PR numbers in `docs/STATUS.md` on your
dotfiles branch and in your final message, then end.
