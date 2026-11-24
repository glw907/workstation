# The task watcher

A session that launches a task outside a chain starts a watcher in the same turn (Geoff, 2026-11-23). The watcher
is a Bash command run with `run_in_background`, and it exits once `claude agents --json` shows the task's session
no longer `working`. Its exit wakes the launching session, which reads the pull request and reports to Geoff.

```bash
until claude agents --json | jq -e --arg n <task-name> \
  '[.[] | select(.name == $n)] | length > 0 and (max_by(.startedAt).state != "working")' >/dev/null
do sleep 60; done
```
