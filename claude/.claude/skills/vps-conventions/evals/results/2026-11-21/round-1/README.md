# vps-conventions, round 1

Round 1 ran the first four queries, each on Haiku, Sonnet, and Opus, once with the skill on and
once with it off. It fails on loading, so its behaviors were not graded.

The skill now carries a `paths:` key for `**/*.service`, `**/*.timer`, and `**/user-data.yaml`.
Claude Code leaves a skill with `paths:` out of the session's skill list until the session works
with a matching file. These queries named no file, so `"listed": false` holds in all 12 skill-on
files. Only `2-haiku-on` loaded the skill, by finding its `SKILL.md` with Glob and reading it.

Round 2 gives each in-scope query a fixture under `evals/files/` that matches one glob:
`backup.service`, `user-data.yaml`, and `prune-uploads.timer`. Each query asks the session to read
its file. The expected behaviors did not change.
