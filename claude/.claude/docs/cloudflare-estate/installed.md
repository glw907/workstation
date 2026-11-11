# What's installed (snapshot 2026-07-07; verify live before acting)

**D1 databases:** asc-club (the phase-2 club domain — members/assets/classes/events/email),
asc-ops + asc-ops-staging (the legacy ops stack, READ-ONLY during absorption, retiring),
asc-staging (the retired sveltekit shell), cairn-asc-auth (the ASC site's magic-link auth),
cairn-907-auth, cairn-ecxc-auth (+ the old cairn-ecnordic-auth pending delete), cairn-pub-auth,
cairn-pub-app, daily-tracker.

**R2 buckets:** asc-site-media (the ASC site's media library), asc-event-images (+ -staging, the
legacy ops event photos), 907-life-media, ecxc-media, cairn-pub-media.

**Workers:** asc-site (the NEW cairn ASC site, served at dev.aksailingclub.org; the apex is the
legacy site until cutover), aksailingclub-org (build worker), asc-ops (+ -dev, -staging; the
retiring dashboard), asc-handbook, asc-uptime, 907-life, ecxc, cairn-pub, eudaimonia.

**Zero Trust organization:** "Wright Family", team domain `907wrights.cloudflareaccess.com` (renamed 2026-10-18 from "Alaska Sailing Club" and `aksailingclub`). Each identity provider's callback is `https://907wrights.cloudflareaccess.com/cdn-cgi/access/callback`; the Google Workspace provider's OAuth client (`450617487145-hqf3h2ge…`, the club's Google Cloud project) must list it.

**Access apps** (live 2026-10-10): ASC Staging, ASC Handbook (+ its CMS), Ops Dashboard (ops +
staging), the Ops Schema API (public, consumed cross-origin by the handbook — do not lock it),
and `phonebook` (+ `phonebook-prov`) on phonebook.907.life. The ASC CMS Admin app on
dev.aksailingclub.org/admin is gone.
The `phonebook` Worker serves phonebook.907.life (live 2026-10-26, version `ea6005d4`), with
`workers_dev` and `preview_urls` off. Its D1 is `phonebook` (`3d877e5b...`). Its secrets (names):
`WARD_USER`, `WARD_BOOK_URL`, `WARD_PASSWORD`, `SIP_PASSWORD_OFFICE`. The `phonebook` Access app
also admits the service token `phonebook-automation` (id `0ecd00bf-…`, 8760h, expires
2027-10-27) through a Service Auth policy that includes it alone; the Worker logs it as the actor
`automation` (registry entry `PHONEBOOK_ACCESS_CLIENT_ID`). Phonebook's `scripts/cloudflare/deploy.sh` and
`scripts/cloudflare/provision.sh` read `CF_ZT_TOKEN` for the Access values, so `ci-deploy` must
repoint them before it deletes that token. The `phonebook-probe` Worker, its route, and its D1
were deleted 2026-10-25.

**asc-site worker secrets (names):** GITHUB_APP_ID, GITHUB_APP_INSTALLATION_ID,
GITHUB_APP_PRIVATE_KEY_B64, STRIPE_SECRET_KEY + STRIPE_WEBHOOK_SECRET (Stripe SANDBOX test keys,
set 2026-07-07; the sandbox webhook endpoint `we_...` targets /api/stripe/webhook). **Not yet
set:** TURNSTILE_SECRET_KEY, CONTACT_EMAIL.
