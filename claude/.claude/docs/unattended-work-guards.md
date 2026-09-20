# Guards on long unattended work

Full procedures for the two mandatory guards the global CLAUDE.md names. Read this when
arming either one.

## Runaway guard (any workflow expected to run past ~30 minutes)

Nothing intervenes unless the main loop watches from outside (proven 2026-07-02: a sweep
agent burned ~5 hours grooming its own agent-memory index). At launch, arm a background
Bash guard that first reads the workflow's `journal.jsonl` for completed agents, then polls
the transcript dir every ~5 minutes for either signature: the newest `agent-*.jsonl` idle
past ~25 minutes (stall; `journal.jsonl` only records agent starts and finishes, so a
long-running task looks idle there; poll the agent transcripts, learned 2026-09-02, and
filter out any agent `journal.jsonl` already marks complete, or every finished chain agent
reads as a stall, learned 2026-09-12), or any `agent-*.jsonl` past ~900KB and still
growing (token runaway; ~3.5-4 chars/token; an implementer polling its own background
gate run also inflates its transcript, so confirm with a tail sample before killing). The
rule in one line: journal for completion, transcripts for idle and size. Arm it with
`claude-wf-guard <transcript-dir> <tier> [run-id]` (`bin/.local/bin/claude-wf-guard`), which
implements exactly this journal-then-transcript check against tiered, measured size limits
(`implementer` 1.8MB, `writer` 4MB, `build` 5MB, `visual` 24MB) rather than hand-written
thresholds.
Intervention: TaskStop, relaunch with `resumeFromRunId` (done steps replay from cache;
give the re-run task a note to review and keep-or-revert any partial uncommitted work).
Prevention rides the prompts: memory-keeping agentTypes get an explicit "skip
agent-memory maintenance" line, and each step states a scope expectation so an agent
that blows past it self-reports. For expensive sweeps, add a hard turn-level token
target, which makes `agent()` calls throw at the ceiling.

## Battery floor (unattended work on battery; Geoff, 2026-09-02)

GNOME suspends this laptop after 15 idle minutes ON BATTERY (AC never suspends), which
freezes agents mid-flight and can kill their API streams (proven 2026-09-02: a suspend
orphaned an implementer's stream and stalled a pass ~2 hours). Size hold durations from
the clock, never as a round number of hours: an overnight hold ends around 09:00 local
(Geoff, 2026-09-03; compute `sleep` seconds as time-until-09:00), and a daytime hold ends
when the dispatched work is expected done, renewing if it runs long. Long unattended work
arms BOTH: a sleep inhibitor held for the duration (background Bash, self-expiring, released
at pass end; hold BOTH channels, since GNOME's idle logic honors its own session
inhibitors while logind honors systemd ones: `systemd-inhibit --what=sleep ... sleep NNN`
AND `gnome-session-inhibit --inhibit suspend ... sleep NNN`; inhibit `suspend` ONLY, never
`suspend:idle`: the `idle` flag stops the session from ever counting as idle, which keeps
the DISPLAY awake for the whole hold (Geoff caught this live 2026-09-02), while `suspend`
alone blocks auto-suspend and lets the screen blank), and a battery watchdog polling
`/sys/class/power_supply/` every ~2 minutes. Test mains power by supply `type`, never by
an `AC*` name glob: on this laptop `AC` reads `type=Mains`, while
`ucsi-source-psy-USBC000:001` and `:002` read `type=USB`; a name glob misses that an
underpowered USB-C or dock supply can read `online` while the battery still drains, which
is the one plugged-in case that still reaches 0%. The mains test is "any supply whose
`type` reads `Mains` reads `online` 1". Verify it once per machine while plugged in over
USB-C, since every supply reads 0 unplugged and the question cannot be settled from an
unplugged session. The battery reads `Not charging` on AC under the charge threshold, so
`status` alone is not a drain signal, and a supply reading online does not prove the
battery is charging. Trigger the alarm at 11% on a disjunction: no `Mains`-type supply is
online, or `capacity` fell across two consecutive polls (silent on AC only when neither
half fires; 11% so state is saved by 10%). On trigger, stand
down: TaskStop the workflow and guards, WIP-commit partial work on the feature branch,
write STATUS with the exact resume prompt (including any `resumeFromRunId`), release the
inhibitor so the machine may sleep, and report. Suspend evidence lives in `journalctl`;
check it before diagnosing any long-running background work as slow or stalled.

## A wake-up that does not depend on the API link (born 2026-09-20, five hours lost)

Every guard above watches the machine or the agents. None of them wakes the CONDUCTOR. A
workflow's completion or failure reaches the main loop only as a task notification, and a
notification that fires while the API link is down is not retried on a timer: the session sits
until a human types. On 2026-09-20 an `EAI_AGAIN` drop killed a fold implementer at about 04:00,
the chain halted, and the conductor sat unwoken until Geoff's 09:16 message, with no suspend in
`journalctl` and every inhibitor held. So any run left unattended arms a scheduled wake-up as
well: start `/loop` with no interval (dynamic pacing) once the first workflow is launched, with
the workflow's own notification as the primary signal and a 1200 to 1800 second fallback. The
fallback tick checks the journal for a dead or halted run and relaunches with `resumeFromRunId`.
A tick that fires while the link is still down fails and the next one retries, which is the
property the notification lacks. Arm it at launch, not when something already looks slow.

## Restart recovery re-arms the FULL set (born of a 7% near-miss, 2026-09-03)

A harness process restart orphans every background guard at once. Recovery after ANY
restart re-arms ALL layers as one checklist, never just the guard for the work being
relaunched. The set: (1) the workflow runaway guard, (2) the battery watchdog, (3) both sleep
inhibitors. "It's on AC right now" is not a reason to skip the battery layer: the
watchdog is silent on AC by design so it is already armed when someone later unplugs.
The one recorded failure: a session re-armed only the transcript guard after a crash,
the laptop was unplugged hours later, and the battery hit 7% with nothing watching (caught by Geoff, not the machinery).

## Concurrent sessions (Geoff runs several at once)

Guards are per-session and stack safely: the machine stays awake while ANY session holds
an inhibitor, and sleep returns when the last one releases. At the battery floor every
session's watchdog fires and each saves its OWN state; no cross-session coordination is
needed. Two rules follow. Name each inhibitor for its initiative (`--who` /
`--app-id`) so ownership is legible in `systemd-inhibit --list`. And touch only your
own guards: never TaskStop, kill, or release an inhibitor, runaway guard, or watchdog
another session armed; `pgrep` and inhibitor listings will show siblings, and a
same-named process from another session is theirs, not a leak.

## The lid switch ignores the sleep inhibitor (born 2026-09-12, 18 minutes lost)

logind handles a lid close even while `systemd-inhibit --what=sleep` and the GNOME session
inhibitor are held (`LidSwitchIgnoreInhibited=yes` is the default). A run that must survive a
closed lid also holds `systemd-inhibit --what=handle-lid-switch --who=<initiative> sleep NNN`,
which stops logind from acting on the lid at all. Arm it alongside the sleep pair whenever the
laptop may be closed or carried; `journalctl | grep "time jump detected"` shows the gap if it
happens anyway.
