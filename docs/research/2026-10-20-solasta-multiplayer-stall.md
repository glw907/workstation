# Solasta on pavilion: the multiplayer load stall, and how to pick it up again

Written 2026-10-20 at the end of a session that set up Solasta modding on pavilion and chased
three separate problems. Two are solved. The third, a stall on the campaign loading screen when
the host starts a multiplayer game, is parked until the 32 GiB RAM kit and the Intel AX210 card
arrive. This note holds the evidence, what was ruled out, and the next steps, so troubleshooting
can resume without the session transcript.

## State of the machine when this was written

| Item | Value |
|---|---|
| Game | Steam Flatpak, app id 1096530, version 1.5.97, folder `~/.var/app/com.valvesoftware.Steam/.local/share/Steam/steamapps/common/Slasta_COTM` |
| Mods | UMM 0.27.10a (Doorstop method, installed by hand) and Unfinished Business 1.5.97.127 in `Mods/` |
| Launch option | `WINEDLLOVERRIDES="winhttp=n,b" %command%` |
| Proton | Proton Experimental, chosen in Steam's UI. GE-Proton11-11 is installed in `compatibilitytools.d` and plays the title video; either works with the mods |
| Steam overlay | Off for this game (`OverlayAppEnable 0` in `userdata/364362109/config/localconfig.vdf`) |
| UMM settings | `Solasta_Data/Managed/UnityModManager/Params.xml` has `CheckUpdates` 0. Keep it 0 after any reinstall |
| Video settings | 2560 x 1440, fullscreen window, Medium quality, half-resolution textures, TAA, FSR off. The High and full-texture set is held back until the RAM arrives |
| Network | Pavilion on the 5 GHz SSID `Warwick 4070 5G` (profile priority 20, band `a`). RTL8821CE power-save workaround persisted in `bluefin/etc/modprobe.d/rtw88-no-lps-deep.conf` (retired 2026-10-25) and `bluefin/etc/NetworkManager/conf.d/wifi-powersave-off.conf` (kept) |
| RAM | 15 GiB usable (2 x 8 GB DDR4-3200). 2 x 16 GB kit on order |
| Wi-Fi card | Realtek RTL8821CE (rtw88). Replaced by the Intel AX210 (iwlwifi) on 2026-10-25 |

The game's own files live in the Proton prefix:
`.../steamapps/compatdata/1096530/pfx/drive_c/users/steamuser/AppData/LocalLow/Tactical Adventures/Solasta/`.
`Player.log` is the Unity log and `UserPreferences.xml` the settings; Steam Cloud syncs both. The
mod loader's log is `Solasta_Data/Managed/UnityModManager/Log.txt`.

## Solved today, so don't re-chase these

**Wi-Fi latency of 1 to 3 seconds.** The RTL8821CE wedges its firmware in deep power save
(`rtw_power_mode_change` warnings, "firmware failed to leave lps state"); each beacon loss on the
crowded 2.4 GHz channel could trigger it. Fixed by the two drop-ins above and the move to 5 GHz.
Symptom check: `journalctl -k -b | grep -c rtw88/ps.c` should stay at 0. Live fix if it ever
returns: `sudo -A iw dev wlp4s0 set power_save off`, then reload with
`sudo -A modprobe -r rtw88_8821ce && sudo -A modprobe rtw88_8821ce`.

Retired 2026-10-25: the Intel AX210 replaced the RTL8821CE, so the rtw88 modprobe drop-in was
removed. The NetworkManager power-save drop-in stays. The case has one antenna cable, so the
AX210 runs on one antenna; its empty second port is expected.

**"Steam is Not Responding" after quitting the game.** The game took 85 seconds to exit because
UMM's update check waited out a network timeout, and Steam blocks while a game process is alive.
Exit takes 1 second with `CheckUpdates` 0. Measured both ways on the same day. The overlay and the
Proton version were changed during the chase and made no difference.

**Steam's interface stalling during a game launch.** Memory. The launch pushed free memory under
600 MB and the kernel's full-stall pressure counter spiked; Steam's UI went quiet until the swap
settled. Not a hang. Choose "Wait" on the dialog or ignore it.

## The open problem

Joining a multiplayer game works up to a point: the lobby loads, the other players are listed,
the character is selectable. When the host starts the game, this client goes to the campaign
loading screen and never leaves it. Seen twice on 2026-10-20 (around 13:46 and again later),
both after a Steam invite launched the game with a join command. Earlier the same day, at 11:40,
a join through the same path worked and the game was played for over an hour, with lag that
turned out to be the Wi-Fi problem above.

What the stalled client looked like, measured over seven seconds with the game process at
pid 3771810:

- Resident memory 2.77 GiB and unchanged; 1.26 GiB of the process in compressed swap (zram) and
  unchanged. The first session of the day had 31 MB swapped.
- CPU 15 ticks (about 2% of a core). GPU 1%. No swap-in or swap-out. `Player.log` not written
  since the mods finished loading.
- Main thread sleeping in `futex_wait_multiple`; no thread above 5%.
- A UDP connection to the Photon game server (port 5056) still established.

So it was blocked, not slow: waiting for something, with memory tight but not actively thrashing
at the moment of measurement.

### What changed between the working join and the stalled ones

- Video settings went from 1440 x 900, Medium, half textures to 2560 x 1440, High, full textures
  (since reverted to Medium and half textures, 1440p kept).
- Memory got tighter: Discord, Steam's interface (about 1.5 GiB), and several Claude Code
  sessions (about 3.8 GiB across servers, drafter, and idle spares) were open.
- The Steam overlay was turned off, UMM's update check turned off, and the Proton version moved
  Experimental, then GE, then Experimental. None of these touch scene loading.

### Hypotheses, most likely first

1. **Memory.** Loading the host's campaign scene needs more than the machine has free, and the
   load blocks rather than fails. The evidence fits but doesn't prove it: the stalled process
   wasn't paging at the moment of measurement. The 32 GiB kit settles this one way or the other.
2. **Host-side wait.** Solasta loads clients in step with the host. If the host is mid-transition
   or hasn't admitted the joiner, the client waits with no timeout. The 11:40 join worked, so this
   would be about timing, not configuration. Ask the host whether they saw the client in the
   lobby and whether they were on a loading screen themselves.
3. **Mod mismatch.** Unfinished Business requires the same version on every client and syncs the
   host's settings at join. A mismatch normally shows a message, not a stall, but it hasn't been
   excluded. Ask the host for their UB version; this client is 1.5.97.127.
4. **DLC content.** Steam holds a license ticket for Palace of Ice only, none for Lost Valley,
   Inner Strength, or Primal Calling. The lobby normally refuses a joiner missing the host's DLC,
   and this one admitted him, so this is unlikely, but a campaign scene that references missing
   DLC assets would be the one place it could surface as a hang.

### Ruled out

- Network: 5 GHz link at 2 to 4 ms to the router, Photon reachable, connection held.
- Wi-Fi driver: no kernel warnings during the stall.
- The join command itself: a lobby join from inside the game hasn't been tried, but the lobby
  stage works either way.
- Steam overlay, Proton version, UMM update check: all changed, stall unchanged.

## Next steps, in order

1. **After the RAM is in**: confirm `free -g` shows about 31 GiB and the zram swap sits at its
   20 GiB cap. Restore the High settings and full textures in `UserPreferences.xml` with the
   game and Steam closed. Join a game and let the host start. If it loads, memory was the cause.
2. **If it still stalls with memory to spare**: before killing the game, capture the same
   measurements as above (`/proc/<pid>/status` for VmRSS, VmSwap, Threads; `top -H` for hot
   threads; `ss -uanp | grep Solasta`), then ask the host the two questions under hypotheses 2
   and 3. Try a lobby join from inside the game (Multiplayer, Join) instead of the Steam invite.
3. **If the host is on a different UB version**: match it. The release page is
   https://github.com/EnderWiggin/SolastaUnfinishedBusiness/releases; unzip over
   `Mods/SolastaUnfinishedBusiness/`.
4. **If a DLC is in play**: the host says which campaign; the Steam store lists each DLC.

## Recovery commands

When a game process is stuck and Steam stops responding:

```
pkill -9 -f 'Solasta.exe'
flatpak run com.valvesoftware.Steam -shutdown
```

Edit `UserPreferences.xml` or Steam's config files only with the game and Steam closed; both
rewrite their files on exit. Valid option names for the video settings come from the UB
translation keys (for example AntiAliasingMode is `None`, `FastApproximateAntialiasing`, or
`TemporalAntialiasing`; TextureQuality is `FullRes`, `HalfRes`, or `QuarterRes`).

## Related

- Memory notes `solasta-modding` and `home-network` in the Claude memory directory carry the
  short form of this setup.
- Backlog #26: router API access, blocked on the TP-Link local admin password.
- `claude/.claude/docs/bluefin-admin.md`, "/etc drift discipline", for the Wi-Fi drop-ins.
