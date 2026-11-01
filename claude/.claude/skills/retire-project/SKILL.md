---
name: retire-project
description: The standard practice for retiring a project on this workstation: inventory, dry run, encrypted archive, approved teardown, and reference sweep. Use when Geoff asks to retire, sunset, shut down, decommission, or delete a repo, site, Worker, or domain, or when an initiative closing leaves a project with no use.
---

# Retire a project

Retirement is irreversible, so it runs in this order and stops at each boundary. Never reorder the
archive and the teardown. The sources are in "Why this order".

## 1. Inventory, read-only

List everything the project owns, and mark each item sole-owner or shared. A shared item stays.

- **Repo:** unpushed branches, stashes, each worktree's `git status`, open PRs and issues, releases,
  Actions secrets, and other sessions working it (`claude agents`, `git status`).
- **Cloudflare:** Workers, custom domains, D1, R2, KV, Queues, Turnstile widgets, Access apps, Email
  Routing rules, Workers Builds triggers, DNS records, and the registrar's expiry and auto-renew.
- **Vendors:** every service that bills or holds a credential for it, such as phone numbers and API
  keys. `wrangler secret list` and the secrets registry name them.
- **References:** grep `~/.dotfiles`, `~/.claude/docs`, `~/Projects/*/CLAUDE.md`, the initiatives
  repo, and the registry. A note that uses the project as a test target needs a new target.

## 2. Archive and prove it

Write one age-encrypted file named `<project>-<date>.tar.age`, using the workstation key. It holds:

- a `git bundle create --all`, verified
- every D1 export, and R2 objects
- issues and PRs as JSON, and the Worker config

Uncommitted work in any worktree gets committed or dropped first, since a bundle doesn't carry it.
Never archive a secret value. Restore the file somewhere scratch: decrypt, clone the bundle, and
load each SQL export into SQLite. Store it at `~/Documents/retired-projects/` and at
`servers-archive/retired-projects/` in R2, confirming the R2 copy with `rclone check`. Stop on a
failed or empty export. The file's sha256 goes in the retirement record.

## 3. Approval

Send the inventory as a dry run through `approval-packet`, listing each delete by its id. Each
irreversible step is an `[irreversible]` step in "If you approve". A domain's fate is Geoff's call.

## 4. Teardown, in this order

Rerun the inventory for each id before deleting it, and stop if it's no longer sole-owner.

1. Take traffic off: remove the custom domain and DNS records before deleting the Worker.
2. Delete the Worker, then Turnstile, Builds triggers, D1, and R2.
3. Stop vendors: release numbers, and revoke each key at its issuer. Deleting a Worker secret
   revokes nothing. Then remove the secrets from the store and the registry.
4. A kept domain gets parked: no Email Routing (the dashboard turns it off; no workstation token can), `MX 0 .`, `v=spf1 -all`, and `v=DMARC1; p=reject;`
   at the apex. A domain with no use lapses at expiry with auto-renew off, and stays parked until then.
5. Delete the GitHub repo (`gh auth refresh -s delete_repo` if needed), then the local checkout and
   its worktrees.

## 5. Close

Clear the references from step 1, close the initiative, and add a row to the `README.md` beside the
archives with the date, sha256, and what went. Rerun the Cloudflare inventory and show it empty.

## Why this order

- GOV.UK's [retiring a repo](https://docs.publishing.service.gov.uk/manual/retiring-a-repo.html):
  README, close issues, remove DNS, archive, remove references. A private project with one owner
  deletes the repo, since the archive already holds its history.
- CMS's [Retire phase](https://www.cms.gov/data-research/cms-information-technology/tlc/retire):
  a disposition checklist the owner attests to, with data archived first.
- Microsoft's [dangling DNS guidance](https://learn.microsoft.com/azure/security/fundamentals/subdomain-takeover):
  DNS goes before the resource it points at.
- [RFC 7505](https://www.rfc-editor.org/rfc/rfc7505.txt) for null MX, and M3AAWG's
  [parked domains practice](https://m3aawg.org/M3AAWG-Protecting-Parked-Domains-BCP-update-2022-06).
