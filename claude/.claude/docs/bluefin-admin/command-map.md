# Command map

- `ujust update` — updates system image, Flatpaks, and Homebrew together. The normal
  update path; prefer it over invoking `rpm-ostree upgrade`, `flatpak update`, and
  `brew upgrade` separately.
- `ujust rebase-helper` — switch streams (`gts`/`stable`/`latest`) or roll back to a
  specific date-tagged build. Use this for rollback, not a manual `bootc` invocation,
  unless you need something the helper doesn't expose.
- `ujust dx-group` — adds the user to developer groups (docker, libvirt, etc.). Needed
  on `stable`; not needed on `gts`, which ships them by default. Run once after a
  fresh install if group-gated tools (docker without sudo, for example) fail.
- `ujust devmode` — developer-mode toggle; consult `ujust --list` for what it changes
  before relying on it for anything specific.
- `ujust enroll-secure-boot-key` — re-enroll the MOK if Secure Boot state needs
  repair after a kernel or driver change.
- `bootc status` / `bootc switch` — inspect and change the underlying ostree image
  directly. Both `bootc` and `rpm-ostree` are live in 2026 and community docs mix
  them; `bootc` is the newer, more direct tool, `rpm-ostree` remains standard for
  layering packages (`rpm-ostree install <pkg>`). Use `rpm-ostree install` for
  layering, `bootc status` for a quick "what image am I on" check, and the `ujust`
  wrappers for anything that has one.

Claude Code's Bash tool does not source `~/.bashrc`, so an env var it sets (a Cloudflare
token, for example) comes back empty unless a command sources it explicitly per invocation:
`bash -c 'source ~/.local/secrets && echo -n $VAR'`. Working directory persists between Bash
tool calls; sourced files and exported variables do not.

The Bash tool runs each command through a wrapper shell (`bash -c ... eval`) whose argv carries
the command text, so `pgrep -f PATTERN` or `pkill -f PATTERN` matches that wrapper whenever
PATTERN appears in the command itself. `pkill` then kills its own shell (exit 144; found
2026-09-15 when an overnight `pkill -f` killed the command that issued it), and `pgrep`
reports a phantom process. Build the pattern so its literal text never appears: a bracket
class (`pgrep -f 'chromium_headless_shel[l]'`), two variables joined at run time
(`a=theme; b=-identity; pgrep -f "$a$b"`), or `pgrep -x`/`pkill -x` on the binary name. Treat a
lone `pgrep` hit that is the query itself as no match.
