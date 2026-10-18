#!/usr/bin/env bash
set -euo pipefail
umask 077  # every temp and cache file is born private, no chmod race

# Workstation secrets sync — decrypts values.age and pushes secrets to local and Cloudflare targets.
#
# Authenticates to 1Password at most ONCE per login session: the age private key is
# fetched on first use and cached in tmpfs (same shared cache as secret-set.sh), then
# reused by later runs: no repeat desktop-approval prompts. The cache is wiped on
# reboot, when the `claude` shell function exits, or via secret-session-clear.sh.
#
# Usage:
#   sync.sh               # Sync local + all workers
#   sync.sh --local       # Local secrets only (no worker push)
#   sync.sh --worker NAME # Push to a single named worker
#   sync.sh --local PATH  # Local secrets only, written to PATH (a next argument not starting --)
#   sync.sh --values PATH # Decrypt PATH, not the main checkout's values.age
#   sync.sh --dry-run     # Show what would be pushed, no changes made
#   sync.sh --verify      # Diff targets vs registry; exits non-zero if mismatch
#
# Design notes:
#   - Private age key persists only in 1Password and the tmpfs session cache.
#   - Decrypted secrets written to /dev/shm (tmpfs, not persisted to disk).
#   - Trap ensures shred cleans up temp files even if script exits early.
#   - Use count=$((count + 1)) not ((count++)) — the latter aborts under set -e.

DOTFILES_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SECRETS_FILE="${VALUES:-$DOTFILES_DIR/secrets/values.age}"
LOCAL_SECRETS="${LOCAL_SECRETS:-$HOME/.local/secrets}"

CACHE="${CACHE:-/dev/shm/.age-key-$(id -u)}"      # session-cached age key (RAM, chmod 600; shared with secret-set.sh)
DECRYPTED_FILE="$(mktemp /dev/shm/secrets-XXXXXX)"

# Cleanup on any exit. The session cache deliberately survives, since secret-session-clear.sh owns its lifecycle.
OUT_FILE=""  # push_local's staging file; shredded by the same trap
trap 'shred -u "$DECRYPTED_FILE" "$OUT_FILE" 2>/dev/null || true' EXIT

# --- Worker routing table ---
# Maps worker name -> space-separated list of secrets to push
declare -A WORKER_SECRETS
# cairn-cms admin (shared GitHub App — one app installed on both repos). Per-site
# MAGIC_LINK_SECRET/SESSION_SECRET are NOT managed here (worker-only, rotatable —
# set directly via `wrangler secret put`; they must differ per site for session isolation).
WORKER_SECRETS["907-life"]="CLOUDFLARE_API_TOKEN RESEND_API_KEY GITHUB_APP_ID GITHUB_APP_INSTALLATION_ID GITHUB_APP_PRIVATE_KEY_B64"
# ecxc.ski's worker, renamed from "ecnordic" at the ECXC rebrand (Rename 4, 2026-06-08).
# The Waymark rebuild commits appId/installationId in cairn.config.ts (public identifiers),
# so unlike 907-life only the App PRIVATE KEY is a worker secret here. GOOGLE_SA_KEY_B64 is
# the registration-roster Sheets writer (registry.md has the scope). ANTHROPIC_API_KEY
# powers the cairn editor's tidy copy-edit (site.config.yaml tidy.enabled). RESEND_API_KEY
# switches the site's dual-transport email layer to Resend (2026-07-14 cutover; the Resend
# account's verified domain is ecxc.ski).
WORKER_SECRETS["ecxc"]="GITHUB_APP_PRIVATE_KEY_B64 GOOGLE_SA_KEY_B64 ANTHROPIC_API_KEY RESEND_API_KEY"
# The ASC cairn site (dev.aksailingclub.org until the apex cutover). Its GitHub App and
# Stripe secrets live in the ASC per-project store; only the workstation-scoped Anthropic
# key routes from here (the cairn editor's tidy copy-edit, same as ecxc).
WORKER_SECRETS["asc-site"]="ANTHROPIC_API_KEY"
# The xcathletes team platform (xcathletes.org), a cairn consumer sharing the same GitHub App
# installation as ecxc and 907-life, so the App private key routes from here alongside the Twilio
# credentials its member OTP layer sends sign-in codes through. TURNSTILE_SECRET_KEY is worker-only
# by the ecxc precedent: it is recoverable from the Turnstile API, so it never enters this store.
# VAPID_PRIVATE_KEY signs Web Push messages; it routes from here because it is NOT recoverable from
# any API, and rotating it silently invalidates every device subscription (see registry.md).
# CONTACT_EMAIL is the /contact form's destination inbox (public-design pass, 2026-08-26);
# an address, not a credential, but managed here so it is config rather than a source literal.
WORKER_SECRETS["xcathletes"]="GITHUB_APP_PRIVATE_KEY_B64 TWILIO_ACCOUNT_SID TWILIO_API_KEY_SID TWILIO_API_KEY_SECRET TWILIO_AUTH_TOKEN VAPID_PRIVATE_KEY CONTACT_EMAIL"

# --- Argument parsing ---
MODE="all"
WORKER_TARGET=""
DRY_RUN=false
VERIFY=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --local)
            MODE="local"
            shift
            if [[ -n "${1:-}" && "$1" != --* ]]; then
                LOCAL_SECRETS="$1"
                shift
            fi
            ;;
        --values)
            if [[ -z "${2:-}" || "$2" == --* ]]; then
                echo "Error: --values requires a path argument." >&2
                exit 1
            fi
            SECRETS_FILE="$2"
            shift 2
            ;;
        --worker)
            if [[ -z "${2:-}" ]]; then
                echo "Error: --worker requires a worker name argument." >&2
                exit 1
            fi
            MODE="worker"
            WORKER_TARGET="$2"
            shift 2
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --verify)
            VERIFY=true
            shift
            ;;
        *)
            echo "Unknown option: $1" >&2
            echo "Usage: sync.sh [--local [PATH]] [--values PATH] [--worker NAME] [--dry-run] [--verify]" >&2
            exit 1
            ;;
    esac
done

# --- Verify mode: diff targets vs registry ---
if [[ "$VERIFY" == true ]]; then
    echo "=== Verify mode ==="
    FAILED=false

    # Check local secrets
    if [[ -f "$LOCAL_SECRETS" ]]; then
        echo "Local ($LOCAL_SECRETS): present"
        # List keys present in local secrets
        while IFS='=' read -r key _; do
            [[ "$key" =~ ^export\ ([A-Z0-9_]+)$ ]] && echo "  ✓ ${BASH_REMATCH[1]}"
        done < "$LOCAL_SECRETS"
    else
        echo "Local ($LOCAL_SECRETS): MISSING" >&2
        FAILED=true
    fi

    echo ""

    # Check each worker
    for worker in "${!WORKER_SECRETS[@]}"; do
        echo "Worker: $worker"
        EXPECTED_KEYS="${WORKER_SECRETS[$worker]}"
        ACTUAL_KEYS=$(npx wrangler secret list --name "$worker" 2>/dev/null \
            | grep '"name"' | sed 's/.*"name": "\([^"]*\)".*/\1/' | sort)

        for key in $EXPECTED_KEYS; do
            if echo "$ACTUAL_KEYS" | grep -q "^${key}$"; then
                echo "  ✓ $key"
            else
                echo "  ✗ $key MISSING" >&2
                FAILED=true
            fi
        done

        # Report extra keys (present on worker but not in registry)
        for actual_key in $ACTUAL_KEYS; do
            if ! echo "$EXPECTED_KEYS" | grep -qw "$actual_key"; then
                echo "  ~ $actual_key (extra — not managed by this registry)"
            fi
        done
    done

    if [[ "$FAILED" == true ]]; then
        echo ""
        echo "Verification FAILED — run sync.sh to push missing secrets." >&2
        exit 1
    else
        echo ""
        echo "Verification PASSED"
        exit 0
    fi
fi

# --- Serialize with secret-set.sh: one writer at a time across every store ---
exec 9>"${XDG_RUNTIME_DIR:-/dev/shm}/secret-store.lock"
flock 9

# --- Decrypt ---
# Fetch the age key from 1Password only on a cache miss. The notesPlain field contains
# the full age key file text; sed strips surrounding quotes that op may add.
if [[ ! -s "$CACHE" ]]; then
    echo "Fetching age private key from 1Password..."
    op item get "Workstation age encryption key" --fields notesPlain --reveal 2>/dev/null \
        | sed 's/^"//;s/"$//' > "$CACHE" || true
    chmod 600 "$CACHE" 2>/dev/null || true
    if [[ ! -s "$CACHE" ]]; then
        rm -f "$CACHE"
        echo "Error: Could not fetch age key from 1Password. Is the app unlocked?" >&2
        exit 1
    fi
else
    echo "Using session-cached age key."
fi

echo "Decrypting secrets..."
age --decrypt -i "$CACHE" "$SECRETS_FILE" > "$DECRYPTED_FILE" \
    || { echo "Error: decrypt failed (stale cached key? run secret-session-clear.sh)." >&2; exit 1; }
chmod 600 "$DECRYPTED_FILE"

# Helper: get a value from the decrypted file
get_secret() {
    local key="$1"
    grep "^${key}=" "$DECRYPTED_FILE" | head -1 | cut -d'=' -f2-
}

# --- Push local secrets ---
push_local() {
    echo ""
    echo "=== Pushing to $LOCAL_SECRETS ==="
    mkdir -p "$(dirname "$LOCAL_SECRETS")"

    if [[ "$DRY_RUN" == true ]]; then
        echo "[dry-run] Would write local secrets:"
    fi

    # Build the output in a temp file to avoid subshell counting issues
    local out_file
    out_file="$(mktemp /dev/shm/local-secrets-out-XXXXXX)"
    OUT_FILE="$out_file"
    count=0

    {
        echo "# Workstation secrets — generated by ~/.dotfiles/scripts/secrets/sync.sh"
        echo "# DO NOT EDIT — re-run sync.sh to update"
        echo ""
    } > "$out_file"

    while IFS='=' read -r key value; do
        # Skip blank lines and comments
        [[ -z "$key" || "$key" =~ ^# ]] && continue
        if [[ "$DRY_RUN" == true ]]; then
            echo "[dry-run]   $key=***"
        else
            echo "export ${key}=${value}" >> "$out_file"
        fi
        count=$((count + 1))
    done < "$DECRYPTED_FILE"

    if [[ "$DRY_RUN" == false ]]; then
        cp "$out_file" "$LOCAL_SECRETS"
        chmod 600 "$LOCAL_SECRETS"
        shred -u "$out_file" 2>/dev/null || rm -f "$out_file"
    fi

    echo "  $count secrets pushed to local"
}

# --- Push worker secrets ---
push_worker() {
    local worker="$1"
    local keys="${WORKER_SECRETS[$worker]:-}"

    if [[ -z "$keys" ]]; then
        echo "Error: Worker '$worker' not found in routing table." >&2
        exit 1
    fi

    echo ""
    echo "=== Pushing to worker: $worker ==="
    count=0
    for key in $keys; do
        value=$(get_secret "$key")
        if [[ -z "$value" ]]; then
            echo "  Warning: $key not found in values.age — skipping" >&2
            continue
        fi
        if [[ "$DRY_RUN" == true ]]; then
            echo "[dry-run]   $key=*** → $worker"
        else
            npx wrangler secret put "$key" --name "$worker" > /dev/null 9>&- <<< "$value"
            echo "  ✓ $key"
        fi
        count=$((count + 1))
    done
    echo "  $count secrets pushed to $worker"
}

# --- Execute based on mode ---
case "$MODE" in
    local)
        push_local
        ;;
    worker)
        push_worker "$WORKER_TARGET"
        ;;
    all)
        push_local
        for worker in "${!WORKER_SECRETS[@]}"; do
            push_worker "$worker"
        done
        ;;
esac

echo ""
if [[ "$DRY_RUN" == true ]]; then
    echo "Dry run complete. No changes made."
else
    echo "Sync complete."
fi
