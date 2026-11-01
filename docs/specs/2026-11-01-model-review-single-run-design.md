# Run the monthly review once, on one host

## Brief

The monthly review ran twice on 2026-11-01, once on each workstation, and the second run started
from a checkout 67 commits behind `main`. This design gives the review one owning host and stops a
run that can't reach GitHub. Approving it starts one small `ordinary` pass.

## Gap

`bluefin/bootstrap.sh:336` enables `model-review.timer` on every host, and nothing in
`model-review-notify` checks whether the month's review already ran. Three things then combined:

- The first run opened workstation PR #184 and servers PR #31 by 00:40 local time.
- The timer fired on `thinkpad-x1` at 12:10 local time, before DNS could resolve GitHub.
- `git pull --ff-only` failed, and the script continued by design: "pull refused; reviewing from
  local HEAD".

The second run then spent a full audit and a review session on a stale tree. It found the first run
only at step 5, by chance, from a `gh pr list` call. Both runs use the branch
`worktree-model-review-2026-11`, so its push would have been refused as non-fast-forward. A quiet
month is worse, since two runs could each merge a log line.

## Evidence

- The `thinkpad-x1` journal, `model-review.service`, 2026-11-01 12:10:24: "fatal: unable to access
  'https://github.com/glw907/workstation.git/': Could not resolve host: github.com", then "pull
  refused; reviewing from local HEAD".
- `upkeep/.config/systemd/user/model-review.timer`: `OnCalendar=monthly` with `Persistent=true`, so
  a host that was asleep at the fire time runs on wake, when the network may still be down.
- `claude/.claude/docs/bluefin-admin.md`: "Pavilion is a desktop that stays awake on AC power."
- `model-review-notify` already keeps two sibling sessions on one host: "only pavilion launches".

## Proposed change

All of it lands in `bin/.local/bin/model-review-notify`.

1. Unless `--dry-run` is set, exit 0 with a journal line when `hostname -s` isn't `pavilion`. The
   timer stays enabled on both hosts, so a move of the role is one line.
2. Replace the pull fallback. Retry `git pull --ff-only` up to five times, 60 seconds apart. If it
   still fails, send `notify-send -u normal`, exit 1, and start no session. The persistent timer
   won't fire again this month, so the message names the command that reruns it:
   `systemctl --user start model-review.service`.
3. After the pull, exit 0 when `git ls-remote --exit-code origin
   "refs/heads/worktree-model-review-$(date +%Y-%m)"` finds the month's branch. This catches a
   manual rerun, or a run on the other host after the role moves.
4. Test with a stubbed `git` and `hostname` on the three paths: wrong host, failed pull, and existing
   branch. Each must reach no `claude` call.

The script's comment about a refused pull changes with step 2. The contestable point is a month
where `pavilion` stays off, since `thinkpad-x1` then won't cover it. `Persistent=true` runs the
review when `pavilion` next wakes, so I'd accept the delay.

This is `ordinary` by `dotfiles-pass`. PR #184's unattended-completion design edits the same launch
lines, so whichever pass runs second rebases on the first.

## Audit findings taken

None. This came from the run's own journal.
