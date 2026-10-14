# Thunderbird tools

These tools prove the theme layer's look without touching a live profile.

| Path | What it does |
|------|--------------|
| `tb-shots` | Builds a scratch profile from the test messages, installs this checkout's layer into it, runs Thunderbird headless, and writes the screenshot set |
| `tb_shots.py` | The Marionette driver `tb-shots` runs: sets message states, switches light and dark and the two list views, and takes the screenshots |
| `fixtures/messages/*.eml` | Invented test messages (`example.com` and `example.org` only), joined into one mbox in file order |
| `fixtures/prefs.js` | The scratch profile's preferences, with the working set for a wizard-free Local Folders profile commented in the file |

## Taking screenshots

```bash
thunderbird/tools/tb-shots [--keep] <outdir>
```

`<outdir>` must be new or empty. The run takes about 80 seconds and needs port
28282 free, so it refuses to start while another Thunderbird holds it. It
writes the scratch profile to
`~/.var/app/org.mozilla.thunderbird/.thunderbird/tb-nord-harness`, the only
part of the home directory the Flatpak sandbox sees, and deletes it on exit
unless `--keep` is given. It stops its own Thunderbird by instance id and
never touches another one.

The files are named `<view>-<mode>.png` or `reader-<case>-<mode>.png`, with
mode `light`, `dark`, or `dark-reader-off`:

- `list-cards`, `list-table`, `list-cards-selected` (one selected row, one
  hovered), and `list-table-tagged` (a focused, selected, tagged row). The list
  shots use a 1600 by 2000 window so every card shows.
- `reader-plain`, `reader-flowed`, `reader-html-cite`, `reader-gmail`,
  `reader-yahoo`, `reader-outlook`, and `reader-flagged-tagged` (the header),
  in light and dark at 1600 by 1000. The `reader-<case>-dark-reader-off` shots
  (plain, flowed, HTML cite, Gmail) use a dark system with the dark reader
  toggled off.

## Checking an install

`thunderbird-theme-sync --profile <dir>` installs this checkout's layer into one
folder, and `--check --profile <dir>` compares it. Both leave the theme clone
and every live profile alone. A profile left behind by `--keep` carries a stale
`lock` symlink, since the harness ends Thunderbird with SIGKILL. The install
refuses such a folder, and the check does not mind it.

```bash
bin/.local/bin/thunderbird-theme-sync --check --profile \
    ~/.var/app/org.mozilla.thunderbird/.thunderbird/tb-nord-harness
```

## Contrast check

`contrast_check.py` measures every role against every background in both
modes. Run `python3 thunderbird/tools/contrast_check.py`; it exits 0 when no
role fails.
