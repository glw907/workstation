# /tmp is a quota'd tmpfs

`/tmp` is a tmpfs mounted with `usrquota`: 8G total, 6275M per user. Claude session
scratchpads (`/tmp/claude-1000/`) and the Go toolchain's build and link directory (`$TMPDIR`)
both live there. Near the quota, a Go build fails with `link: mapping output file failed: disk
quota exceeded` while `df` shows free space and a large write into the repo succeeds;
`GOTMPDIR` does not help, since the failing write is the linker's own output mapping (seen
2026-09-21, when two stale 1.1G repo copies from a leak check had the user at 6168M). On that
error, run `quota -s -f /tmp`; if `space` is near `limit`, find the bulk with
`du -sh /tmp/* | sort -h | tail` and delete stale scratch (old session scratchpads, experiment
copies). A long session that writes gigabytes to its scratchpad eats the same quota.
