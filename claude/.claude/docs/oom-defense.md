# Memory-pressure defense (OOM guard) design

Research report, 2026-09-03, produced after two kernel-OOM incidents killed whole
Ptyxis scopes (and the Claude Code sessions inside them) during browser-based test
gates. Staged configs live in `~/.dotfiles/bluefin/etc/systemd/`. Deployment status
is tracked in the dotfiles commits; read `bluefin-admin.md` for the /etc install
convention.

## Recommendation Report: Memory-Pressure Defense for This Workstation

### 1. Mechanism findings (confirmed against this machine, not inferred)

**systemd-oomd never fired.** `journalctl -u systemd-oomd` shows only the service starting; no "killed X due to memory pressure" log lines around either incident. Confirmed the pure kernel OOM killer acted both times:

```
kernel: Out of memory: Killed process 791778 (chrome-headless) ... anon-rss:4353044kB oom_score_adj:300
kernel: Out of memory: Killed process 1035243 (chrome-headless) ... anon-rss:5627040kB oom_score_adj:300
```

The kernel picked correctly: every user-session process on this box (claude, bash, 1password) carries `oom_score_adj=200` (systemd's default bump for `user.slice` processes, less critical than system services); Chromium's headless process was 100 points hotter at 300 (Chromium's own OOM-priority manager biases its own processes), so it had the highest `oom_score` of any candidate and was the deterministically correct victim.

**The collateral damage is a separate, second mechanism: `OOMPolicy=` on the scope, not systemd-oomd.** ~45 seconds after each kernel kill:

```
systemd[3855]: ptyxis-spawn-<uuid>.scope: Failed with result 'oom-kill'.
```

Confirmed live: `systemctl --user show <ptyxis-scope> -p OOMPolicy` → `OOMPolicy=stop`, and `systemctl --user show -p DefaultOOMPolicy` → `stop`. Mechanism: systemd's per-user manager watches each unit's cgroup `memory.events` `oom_kill` counter (unrelated to systemd-oomd, which is a *separate* pressure-based pre-emptive killer). When that counter increments and the unit's `OOMPolicy=stop` (the manager-wide default), systemd cleanly terminates **every remaining process in that scope's cgroup** — which is claude, its background agents, and the shell, none of which were ever OOM candidates. This is a known, well-documented systemd behavior: [systemd/systemd#25376](https://github.com/systemd/systemd/issues/25376) describes the identical symptom. It was mitigated in systemd 253 by giving **login-session scopes** (`session-N.scope`, created by `pam_systemd`) a default of `OOMPolicy=continue` — but Ptyxis's own transient scopes (`ptyxis-spawn-*.scope`, created via `systemd-run --user --scope`) are ordinary app.slice scopes, not login-session scopes, so they still inherit the global `DefaultOOMPolicy=stop`. This machine runs systemd 259.8 (Fedora 44) and is squarely still exposed.

**systemd-oomd is active and configured, just never reached its trigger.** `app.slice` carries `ManagedOOMMemoryPressure=kill`, `ManagedOOMMemoryPressureLimit=` an internal fixed-point value equal to 80% (from `/usr/lib/systemd/user/slice.d/10-oomd-per-slice-defaults.conf`, a Fedora-shipped drop-in, not upstream systemd's 60% compiled default), with `DefaultMemoryPressureDurationSec=20s` (`/usr/lib/systemd/oomd.conf.d/10-oomd-defaults.conf`, also Fedora-shipped, tighter than upstream's 30s). Both incidents evidently ramped too fast (or swap absorbed the pressure signal) for a sustained 20s/80%-pressure window to trip before the kernel's hard OOM fired first. So oomd's per-slice pressure kill (which *does* respect `ManagedOOMPreference`/cgroup selection and would have killed only the browser's own cgroup if wired that way) is present but was outrun by the kernel path in this race.

**Current headroom is already thin at baseline.** `free -h` while only ~5 Claude processes were running (no browser) showed `Swap: 8.0Gi total, 5.0Gi used`. zram is capped at Bluefin's shipped default `zram-size = min(ram, 8192)` = 8GB (`/usr/lib/systemd/zram-generator.conf`), no `/etc` override present, algorithm `lzo-rle` (not `zstd`).

---

### 2. Option table

| Layer | Option | Catches | Trade-off |
|---|---|---|---|
| Headroom | Raise zram size (e.g. `ram*1.25`≈19GB, or piecewise formula) | Buys time before any OOM path fires | Zram is RAM-backed compressed swap, not free capacity — a true leak still exhausts it, just later; more CPU spent compressing under pressure (the worst time to add CPU load) |
| Headroom | Switch `compression-algorithm = zstd` | ~20-30% more effective capacity at same physical zram size vs `lzo-rle` | Slightly more CPU per page-in/out; needs `zstd` kernel module loaded at boot (usually built-in on Fedora kernels, verify) |
| Pressure response | Loosen `ManagedOOMMemoryPressureLimit`/duration on app.slice | Nothing here — already generous (80%/20s) relative to upstream | Loosening further delays oomd's *correct* per-cgroup selective kill in favor of the kernel's blunter global one — **wrong direction**, do not do this |
| Pressure response | Tighten oomd instead (lower limit / shorter duration, or add `ManagedOOMPreference=avoid` on the Claude scopes) | Lets oomd win the race against the kernel killer more often, so its cgroup-scoped kill (chrome's own cgroup only) fires before the kernel's system-wide one | oomd killing "too early" during a legitimate but transient spike; needs the containment layer below to actually give oomd a chrome-only cgroup to target |
| Blast-radius containment | Wrap browser-heavy test runs in `systemd-run --user --scope -p MemoryMax=... -p MemoryHigh=...` | Chromium throttles/dies **alone**, inside its own scope, never touching the Claude session's scope or cgroup | Needs a wrapper at the right call site (below); a hard `MemoryMax` kills chrome itself if undersized — must be tuned against real usage (5.6GB peak observed) |
| Session protection | `DefaultOOMPolicy=continue` for the user manager (staged in dotfiles at `bluefin/etc/systemd/user.conf.d/10-oom-continue.conf`, then installed to `/etc/systemd/user.conf.d/`) | Directly fixes the confirmed failure: an OOM kill inside a scope no longer force-stops the whole scope | Global for every user unit; means a unit whose *only* process gets OOM-killed no longer gets systemd's clean-stop bookkeeping — acceptable trade for a multi-process interactive scope, matches what systemd 253+ already does by default for login sessions |
| Session protection | Negative `oom_score_adj` for claude via `choom` or `OOMScoreAdjust=` | Lowers claude's kill priority specifically | Address's a symptom the kernel already got right (claude was never the kernel's target — chrome was); doesn't fix the actual collateral-damage bug; skip |
| Session protection | `MemoryLow=` on the Claude-hosting scope | Soft-protects claude's cgroup memory from reclaim/pressure-based eviction | Only matters for the oomd pressure path, not the kernel-hard-OOM + `OOMPolicy=stop` path that actually fired; secondary, not primary |
| Alternative pressure monitor | earlyoom or a small PSI-watcher service | Could pre-empt with more control than oomd, e.g. explicitly target `chrome-headless` by name | Not installed, adds a second OOM daemon alongside systemd-oomd (redundant complexity); Fedora's oomd is already PSI-based and present — prefer tuning it, or the scoped `MemoryMax` containment, over a third daemon |

---

### 3. Recommended layered design

Four layers, ordered by which one should catch the problem first. Layer 3 (containment) is the one that actually prevents recurrence; layer 4 (session protection) is the one that prevents the confirmed collateral damage if containment is ever bypassed (an ad hoc `npx vitest` run outside the wrapper, a different heavy child process, etc). Do both.

**Layer 1 — headroom: zram**
File: `~/.dotfiles/bluefin/etc/systemd/zram-generator.conf.d/10-larger-zram.conf`, then installed to `/etc/systemd/zram-generator.conf.d/10-larger-zram.conf` (never edit `/etc` directly, per this workstation's convention).

```ini
[zram0]
zram-size = min(ram * 5 / 4, 20480)
compression-algorithm = zstd
```
15GB × 1.25 ≈ 19GB, capped at 20GB. Requires a **reboot** (zram device is set up by a generator at early boot; `systemctl restart systemd-zram-setup@zram0.service` *may* work live but resizing an active swap device is fiddlier and riskier to attempt read-write outside a controlled window — recommend reboot). Verify the `zstd` kernel module is present (`modinfo zstd` — almost certainly built-in on Fedora's kernel, no `/etc/modules-load.d` entry needed on recent Fedora kernels, but confirm before relying on it).

**Layer 2 — pressure response: leave oomd's existing config alone, do not loosen it.** Fedora's shipped 80%/20s on `app.slice` is already stricter (more protective) than upstream defaults. The fix here is structural, not a threshold change: layer 3 gives oomd (and the kernel) a chrome-only cgroup to aim at, so when either mechanism does fire, it naturally only removes chrome.

**Layer 3 — blast-radius containment: scope the browser test run**
This is the one that should have prevented the incident. Wrap the heavy child specifically, not every `npm` invocation. Two candidate call sites, prefer the second:

- *Narrow*: a `test:integration`/`test` script change in each repo's `package.json` (cairn-cms, ecxc-ski, 907-life) that runs vitest's browser project under a scope:
  ```json
  "test": "systemd-run --user --scope -p MemoryMax=3200M -p MemoryHigh=2800M -- vitest run"
  ```
  MemoryMax sized below the ~5.6GB single-process peak observed at OOM time (headless Chromium unconstrained can clearly climb well past that) — set deliberately low enough that Chromium gets throttled/killed by its own cgroup limit before the kernel's system-wide OOM killer ever needs to choose a victim. Tune from real numbers: rerun the suite once locally, watch `systemd-run`'s scope RSS via `systemd-cgtop`, then set `MemoryMax` a bit above legitimate peak and `MemoryHigh` ~85% of that.
- *Broad, but requires code, so treat as a stretch*: a shared shim script that any repo's `npm test`/CI-adjacent script can call, avoiding N copies of the same `systemd-run` incantation across repos. Given three repos today, start narrow (per-repo `package.json` edit) and only build the shim if a fourth consumer needs it — do not build the general form speculatively.

This requires **no reboot, no daemon-reload** — it's a per-invocation wrapper, live immediately once the script changes are committed.

Secondary, cheaper mitigation worth doing alongside: the vitest browser project's config (`vitest.config.ts` in cairn-cms) should be checked for browser-instance reuse settings — [vitest-dev/vitest#9437](https://github.com/vitest-dev/vitest/issues/9437) documents Chromium resource accumulation across test files in browser mode on long runs; restarting/recycling the browser context between files (or capping `test.browser` instance count) reduces the peak this containment has to absorb, rather than just raising the fence around it.

**Layer 4 — session protection: fix the confirmed `OOMPolicy=stop` collateral-kill bug**
File: `~/.dotfiles/bluefin/etc/systemd/user.conf.d/10-oom-continue.conf`, installed to `/etc/systemd/user.conf.d/10-oom-continue.conf` (system-wide for the user, covers every terminal/session, not just Ptyxis).

```ini
[Manager]
DefaultOOMPolicy=continue
```

This is a **manager-level** setting (not a per-unit drop-in — confirmed `OOMPolicy` is not recognized under `[Slice]` or as a scope drop-in key, so a slice-level override doesn't work; it has to be the manager default). Applying it: **requires `systemctl --user daemon-reexec` (or log out/in) to take effect**, not merely `daemon-reload` — `[Manager]` section changes need the manager itself to re-exec. No reboot needed. Effect: matches what systemd 253+ already gives login-session scopes by default, extended to Ptyxis's own transient scopes too — an OOM kill inside any user scope is logged but no longer force-stops surviving siblings. This directly closes the observed failure ("claude died because the scope was stopped," confirmed above) even on a future run that somehow bypasses the layer-3 wrapper.

**Deployment order**: land layer 4 first (cheapest, directly fixes the confirmed bug, no reboot); land layer 3 next (prevents the trigger from firing programmatically); land layer 1 last or opportunistically at a natural reboot (headroom, not a fix by itself). Layer 2 is a no-op by design — resist the urge to touch it.

**Flag**: nothing above loosens systemd-oomd's kill posture on a 15GB laptop — the one option that would (raising `ManagedOOMMemoryPressureLimit`) is explicitly rejected in the table. `DefaultOOMPolicy=continue` is the one setting with a real, if narrow, downside: any single-process user unit that dies to the OOM killer now logs-and-continues rather than transitioning cleanly through systemd's normal failure/restart bookkeeping for that unit; for interactive multi-process terminal scopes (this machine's actual failure mode) that trade is correct and matches upstream's own post-253 choice for login sessions.

---

### 4. Sources

- [systemd/systemd#25376 — built-in OOM killer kills entire scope on kernel OOM, doesn't respect OOMPolicy=](https://github.com/systemd/systemd/issues/25376)
- [systemd.scope(5) — OOMPolicy=, DefaultOOMPolicy= semantics](https://man7.org/linux/man-pages/man5/systemd.scope.5.html)
- systemd 253 release notes / PR #25385, #25725 — login-session scopes default to `OOMPolicy=continue` (via web search summary; verify against `NEWS`/release notes for exact wording if citing precisely)
- Local evidence: `journalctl -k`, `journalctl -u systemd-oomd`, `systemctl --user show -p OOMPolicy/DefaultOOMPolicy`, `/usr/lib/systemd/user/slice.d/10-oomd-per-slice-defaults.conf`, `/usr/lib/systemd/oomd.conf.d/10-oomd-defaults.conf`, `/usr/lib/systemd/zram-generator.conf`, `zramctl`, `free -h` — all read on this machine during this investigation
- [Fedora zram-generator defaults and zstd compression-algorithm guidance](https://wiki.archlinux.org/title/Zram) (ArchWiki, cross-referenced against this machine's shipped `/usr/lib/systemd/zram-generator.conf`)
- [zram-generator.conf.example (upstream)](https://github.com/systemd/zram-generator/blob/main/zram-generator.conf.example)
- [vitest-dev/vitest#9437 — Chromium resource accumulation across test files in browser mode](https://github.com/vitest-dev/vitest/issues/9437)
- [ublue-os/bluefin Discussion #2848 — RAM recommendations, zram present by default](https://github.com/ublue-os/bluefin/discussions/2848)

---

**Files touched by this investigation**: none — read-only throughout (`systemctl show`, `journalctl`, `cat`/`find` over `/usr/lib/systemd`, `/etc/systemd`, `/proc/*/oom_score_adj`, `~/.dotfiles`). No system state was changed.
