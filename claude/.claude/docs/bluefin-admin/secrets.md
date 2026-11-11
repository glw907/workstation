# Secrets: installing, receiving, and Proton Pass

Moved from the global CLAUDE.md "Secrets" section (2026-09-27); CLAUDE.md keeps the
never-commit rules and a pointer here.

- **Claude's own Proton Pass agent (Geoff, 2026-10-20): Claude works in Proton Pass as it
  did in 1Password, creating and editing items, but only through `claude-pass`.** Each
  host gets an agent, `pavilion-claude` or `thinkpad-claude`, with role editor on
  `Infrastructure`, `Projects`, `ASC`, `Test accounts`, and `Age key` (the
  credential-hygiene layout, 2026-11-03). His Private and family vaults stay out of reach.
  The `proton-pass` skill holds the vault map, the naming rules, and the procedures; the
  grants and token expiries are in `secrets/proton-grants.tsv`. As editor on `Age key`, Claude can read or change the age key too;
  that follows from the ruling. `claude-pass` runs only the
  subcommands item, vault, folder, share, password, totp, info, and user. Under `item` it allows
  list, view, create, update, trash, untrash, and move, so `item share`, `item member`, and
  `item delete` are refused. Under `vault` it allows only list, so `vault share`, `vault
  transfer`, `vault member`, and vault create, update, and delete are refused. Every other
  top-level command (run, login, agent, ssh-agent, invite, ...) is refused too, and `share`
  runs only as `share list` (what `pass-access` reads). Every refusal comes
  before the token is read. The reason must be 1 to 300 characters. `claude-pass <pass-cli args>` reads the agent's token from GNOME
  Keyring (service `proton-pass-agent-claude`, host `<host>`), logs in to a fresh
  `$XDG_RUNTIME_DIR/pass-agent.*` session, runs the one command with an audit reason
  (`CLAUDE_PASS_REASON`, or a default naming the host and subcommand), then logs out and
  removes the directory. A value goes in on stdin (`claude-pass item create login
  --vault-name "Infrastructure" --from-template -`), never on the command line. A secret
  read with `item view` goes to a file or a pipe, never the transcript. `claude-pass
  --status` prints `path=proton|none`, and `check-drift` reports it without failing.
  To grant another vault, Geoff runs `pass-cli agent access grant pavilion-claude
  --vault-name V --role editor` (or `thinkpad-claude`) in a throwaway session. The agent
  expires three months after creation (`pass-cli agent create <name> --expiration 3m`);
  `pavilion-claude` expires 2027-01-20 and `thinkpad-claude` 2027-02-02. To renew it, Geoff creates a fresh token and stores it with
  `secret-tool store --label "Proton Pass claude agent" service proton-pass-agent-claude
  host <host>`. The grant map records each Claude agent's expiry, so `check-drift` warns
  within 30 days of it and fails once past (update the map when you renew).
  Proton throttles the agent's logins after about four quick calls, and `claude-pass` then
  reports "agent login failed (token expired or revoked?)" for 5 to 25 minutes while the token
  is fine, so a batch spaces its calls about 150 seconds apart (2026-10-25).
- **Proton Pass (Pass W, 2026-10-18): Claude never calls bare `pass-cli`**, which would act
  as Geoff's own login and reach every vault. `claude-block-pass` denies `pass-cli`,
  `secret-tool lookup`, `keyctl print|pipe|read`, and any `pass-ws.*`, `pass-recv.*`,
  `pass-agent.*`, or default pass-cli session-directory path. The age key
  reaches `secret-set.sh` and `sync.sh` through `ws-pass-key`: the host's agent token
  (GNOME Keyring, `ws-pass-key --store` keeps a new one), a per-run tmpfs session, a
  read with a reason, then logout. A host with no token fails with a message to run
  `ws-pass-key --store`; there is no `op` fallback. `check-drift` fails such a host and
  reports each host's path and the token's expiry (`ws-pass-key --status`, three-month
  expiry). The `Age key` vault holds one item, the age key; each host has its own agent
  (`pavilion-scripts` and `thinkpad-scripts`, viewer role on that vault only), which Geoff
  creates in a throwaway session with `pass-cli agent create <host>-scripts --expiration 3m
  --vault "Age key"`. The key needs a vault of its own: an item share hides its parent
  vault, so `ws-pass-key`'s `pass://Age key/...` lookup needs a vault grant (2026-11-03). A paper copy of the key also exists. The ASC age key stays in
  its own key file (`~/.config/age/asc-key.txt`); when that is missing, Geoff restores it by
  hand from Proton Pass, never through the agent token. Passkeys route through the browser
  for Geoff's touch, never read directly.
  `secret-receive NAME --pass REF` takes a value from Geoff's own Proton login, and
  `pass-count` prints his per-vault counts (`--hashes` for `Infrastructure`).
  `claude-sudo-setup` takes the sudo password from a dialog; sudo never reads a password
  manager. 1Password was removed from the workstations on 2026-10-19 (Geoff, 2026-10-18).
- **Installing a NEW long-lived secret, every project (Geoff, 2026-07-13): the
  workstation age store is the origin, never a loose file, never only `wrangler secret
  put`.** Flow: `~/.dotfiles/scripts/secrets/secret-set.sh NAME --value|--file|--b64-file`
  (writes `values.age`, regenerates `~/.local/secrets`), document scope and rotation in
  `~/.dotfiles/secrets/registry.md`, add the worker to `sync.sh`'s WORKER_SECRETS routing
  if it consumes one, then `sync.sh --worker NAME` and `sync.sh --verify`. Delete any
  loose key file; the upstream issuer (GCP IAM, GitHub App settings, ...) mints
  replacements. Exception: ASC secrets use `aksailingclub-legacy/secrets/`; per-site
  rotatable HMAC keys (MAGIC_LINK_SECRET, SESSION_SECRET) stay worker-only.
- **Receiving a secret value FROM Geoff (Geoff, 2026-08-31): run `secret-receive NAME
  [--hint …|--pass REF]`**, a desktop paste dialog (or a Proton Pass read through Geoff's own login) piped into the age
  store. Never paste-into-chat or hand-run commands. Wire the name first (manifest,
  registry `pending`, consumer config); flip the registry checkmark after the mint.
- **Check the stores before claiming a secret is missing**, in order: `npx wrangler
  secret list` (per worker), `~/.local/secrets`, the age registry
  (`~/.dotfiles/secrets/registry.md`), per-project stores (a repo's `secrets/` dir plus
  sync script; ASC's is `aksailingclub-legacy/secrets/`), and
  `cloudflare-estate-inventory.md`. None found is the finding, not "Geoff owes a paste."
  Name-only checks, never print values.
- **A create response can carry a secret.** A Cloudflare `cfd_tunnel` create response
  holds the tunnel's `TunnelSecret` and connector `token` beside its id. Pipe it through
  `jq -r .result.id`, or whichever single field the step needs, so the body never reaches a
  transcript, a log, or a report. A body that does is a printed secret: treat the tunnel as
  compromised, then delete and recreate it.
