# Regenerate the live inventory

```bash
AID=120c269ad6d3dfbe6d63a0bb53758ca0; T="Authorization: Bearer $CLOUDFLARE_API_TOKEN"
curl -s -H "$T" "https://api.cloudflare.com/client/v4/accounts/$AID/d1/database"          # D1
curl -s -H "$T" "https://api.cloudflare.com/client/v4/accounts/$AID/r2/buckets"           # R2
curl -s -H "$T" "https://api.cloudflare.com/client/v4/accounts/$AID/workers/scripts"      # Workers
curl -s -H "$T" "https://api.cloudflare.com/client/v4/accounts/$AID/access/apps"          # Access
cd <a repo bound to the worker> && npx wrangler secret list                               # secret NAMES
```
