#!/usr/bin/env bash
set -eo pipefail
umask 077  # every temp and cache file is born private, no chmod race

# Add or update ONE secret in values.age, then regenerate ~/.local/secrets.
#
# Fetches the age private key at most ONCE per login session: ws-pass-key reads it through
# the host's Proton agent token on first use and caches it in tmpfs (/dev/shm, RAM-backed,
# chmod 600), then later runs in the same
# session reuse it, with no repeat prompts.
# The cache is wiped on reboot, when the `claude` shell function exits
# (claude-sudo-clear pattern), or explicitly via secret-session-clear.sh.
#
# This is the supported way to install secret material — never leave loose key
# files on disk. values.age is the source of truth; sync.sh pushes to Workers.
#
# Usage:
#   secret-set.sh NAME --stdin             # prompt for the value, no echo (preferred
#                                          #   interactive form: keeps the value out of
#                                          #   shell history, /proc cmdline, transcripts)
#   secret-set.sh NAME --value 'literal'   # single-line value on the command line
#                                          #   (non-interactive callers only)
#   secret-set.sh NAME --file PATH         # raw file contents (must be single-line)
#   secret-set.sh NAME --b64-file PATH     # base64-encode a file → single line
#                                          #   (use for PEMs / any multi-line material;
#                                          #    decode with atob()/base64 -d at the consumer)
#   secret-set.sh --sync                   # just regenerate ~/.local/secrets, no edit
#   secret-set.sh NAME --delete            # remove NAME from values.age (git keeps history)
#   secret-set.sh --dry-run NAME --value … # show what would change, write nothing
#   secret-set.sh … --values PATH          # read and write this store, not the main checkout's
#   secret-set.sh … --local PATH           # regenerate this file, not ~/.local/secrets
#
# Every run holds an exclusive flock on $XDG_RUNTIME_DIR/secret-store.lock for its whole
# read-modify-write, and fails, leaving the store alone, unless every name in the old store
# is still in the new one (the name a --delete run removes excepted).
#
# After adding, document the secret in registry.md and (for Workers) add it to the
# routing table in sync.sh, then run sync.sh --worker NAME.

# Each path can be overridden from the environment, so a test or a worktree edit can point the
# script at a scratch store without touching the live one.
RECIP="${RECIP:-age197mcd2m3z90t49n9t5v3ujjntw7krfkw5y9sjfc545v28qvezugshg7jgk}"
VALUES="${VALUES:-$HOME/.dotfiles/secrets/values.age}"
LOCAL_SECRETS="${LOCAL_SECRETS:-$HOME/.local/secrets}"
CACHE="${CACHE:-/dev/shm/.age-key-$(id -u)}"      # session-cached age key (RAM, chmod 600)
WS_PASS_KEY="${WS_PASS_KEY:-$(cd "$(dirname "$0")/../.." && pwd -P)/bin/.local/bin/ws-pass-key}"

die() { echo "Error: $*" >&2; exit 1; }

usage() { sed -n '4,37p' "$0" | sed 's/^# \{0,1\}//'; exit "${1:-0}"; }

# A --values or --local path must be given once and hold no "..", so a rule that allows a
# worktree prefix cannot be steered to the main checkout's store.
flag_path() {
    [[ -n "$2" && "$2" != --* ]] || die "$1 needs a path"
    [[ "$2" != *..* ]] || die "$1 path may not contain '..': $2"
    printf '%s' "$2"
}

# --- Parse arguments ---
SAW_VALUES=""
SAW_LOCAL=""
NAME=""
MODE=""
SRC=""
DRY_RUN=false
SYNC_ONLY=false
DELETE=false
while [[ $# -gt 0 ]]; do
    case "$1" in
        --stdin)    MODE="stdin";    shift ;;
        --value)    MODE="value";    SRC="${2:?--value needs an argument}"; shift 2 ;;
        --file)     MODE="file";     SRC="${2:?--file needs a path}";       shift 2 ;;
        --b64-file) MODE="b64-file"; SRC="${2:?--b64-file needs a path}";   shift 2 ;;
        --sync)     SYNC_ONLY=true;  shift ;;
        --delete)   DELETE=true;     shift ;;
        --dry-run)  DRY_RUN=true;    shift ;;
        --values)   [[ -z "$SAW_VALUES" ]] || die "--values given twice (repeated flag refused)"
                    SAW_VALUES=1; VALUES="$(flag_path --values "${2:-}")"; shift 2 ;;
        --local)    [[ -z "$SAW_LOCAL" ]] || die "--local given twice (repeated flag refused)"
                    SAW_LOCAL=1; LOCAL_SECRETS="$(flag_path --local "${2:-}")"; shift 2 ;;
        -h|--help)  usage 0 ;;
        -*)         die "unknown option: $1" ;;
        *)          [[ -z "$NAME" ]] && NAME="$1" || die "unexpected arg: $1"; shift ;;
    esac
done

# --- Serialize every read-modify-write: two writers must not each re-encrypt from the same read ---
LOCK="${XDG_RUNTIME_DIR:-/dev/shm}/secret-store.lock"
exec 9>"$LOCK"
flock 9

# --- Fetch age key once per session, cache in tmpfs ---
# ws-pass-key reads the host's Proton agent token from the keyring; a host with none reads op.
ensure_key() {
    if [[ ! -s "$CACHE" ]]; then
        echo "Fetching age key (once per session)…" >&2
        WS_PASS_CALLER=secret-set.sh CACHE="$CACHE" "$WS_PASS_KEY" \
            || die "could not fetch age key; is the agent token valid (ws-pass-key --status)?"
    fi
}

# --- Write ~/.local/secrets from a decrypted plaintext file (mirrors sync.sh) ---
write_local() {
    local dec="$1"
    local out
    out="$(mktemp /dev/shm/local-secrets-XXXXXX)"
    {
        echo "# Workstation secrets — generated by ~/.dotfiles/scripts/secrets/sync.sh"
        echo "# DO NOT EDIT — re-run sync.sh to update"
        echo ""
        while IFS='=' read -r k v; do
            [[ -z "$k" || "$k" =~ ^# ]] && continue
            echo "export ${k}=${v}"
        done < "$dec"
    } > "$out"
    cp "$out" "$LOCAL_SECRETS"
    chmod 600 "$LOCAL_SECRETS"
    shred -u "$out" 2>/dev/null || rm -f "$out"
}

# Fail unless every name in the old plaintext ($DEC) is in the new ciphertext. $1 is the one name
# a --delete run may drop.
check_no_drops() {
    local new_names missing
    new_names="$(age --decrypt -i "$CACHE" "$VALUES.tmp" | cut -d= -f1)"
    missing="$(cut -d= -f1 "$DEC" | grep -v '^$' | grep -vxF -- "${1:-}" | grep -vxFf <(printf '%s\n' "$new_names") || true)"
    if [[ -n "$missing" ]]; then
        rm -f "$VALUES.tmp"; die "the new store would drop: $(echo "$missing" | tr '\n' ' ')— $VALUES left untouched"
    fi
}

DEC="$(mktemp /dev/shm/values-dec-XXXXXX)"
NEW="$(mktemp /dev/shm/values-new-XXXXXX)"
trap 'shred -u "$DEC" "$NEW" 2>/dev/null; rm -f "$VALUES.tmp" 2>/dev/null' EXIT

ensure_key
age --decrypt -i "$CACHE" "$VALUES" > "$DEC" || die "decrypt failed (stale cached key? run secret-session-clear.sh)"
chmod 600 "$DEC"

# --- Sync-only: just regenerate local from current values.age ---
if [[ "$SYNC_ONLY" == true ]]; then
    if [[ "$DRY_RUN" == true ]]; then
        echo "[dry-run] would regenerate $LOCAL_SECRETS from values.age"
        exit 0
    fi
    write_local "$DEC"
    echo "Regenerated $LOCAL_SECRETS ($(grep -c '^export ' "$LOCAL_SECRETS") secrets)."
    exit 0
fi

[[ -n "$NAME" ]] || die "missing secret NAME (or use --sync). See --help."
[[ "$NAME" =~ ^[A-Z][A-Z0-9_]*$ ]] || die "NAME must be UPPER_SNAKE_CASE: '$NAME'"
# --- Delete: drop NAME, verify the new ciphertext no longer carries it ---
if [[ "$DELETE" == true ]]; then
    [[ -z "$MODE" ]] || die "--delete takes no value option"
    grep -q "^${NAME}=" "$DEC" || die "$NAME is not in values.age"
    grep -v "^${NAME}=" "$DEC" > "$NEW" || true
    chmod 600 "$NEW"
    if [[ "$DRY_RUN" == true ]]; then
        echo "[dry-run] would delete $NAME from values.age and regenerate $LOCAL_SECRETS"
        exit 0
    fi
    age -r "$RECIP" -o "$VALUES.tmp" "$NEW"
    check_no_drops "$NAME"
    if ! age --decrypt -i "$CACHE" "$VALUES.tmp" | grep -q "^${NAME}=" \
        && [[ "$(age --decrypt -i "$CACHE" "$VALUES.tmp" | grep -c '=')" -eq "$(grep -c '=' "$NEW")" ]]; then
        mv "$VALUES.tmp" "$VALUES"
    else
        rm -f "$VALUES.tmp"; die "verification failed: values.age left untouched"
    fi
    write_local "$NEW"
    echo "OK: ${NAME} deleted from values.age + $LOCAL_SECRETS. Remember to update registry.md."
    exit 0
fi

[[ -n "$MODE" ]] || die "need one of --stdin / --value / --file / --b64-file (or --sync, --delete)"

# --- Build the value (always single-line) ---
case "$MODE" in
    stdin)    IFS= read -rsp "Value for ${NAME} (no echo): " VAL; echo >&2 ;;
    value)    VAL="$SRC" ;;
    file)     [[ -f "$SRC" ]] || die "no such file: $SRC"; VAL="$(cat "$SRC")" ;;
    b64-file) [[ -f "$SRC" ]] || die "no such file: $SRC"; VAL="$(base64 -w0 "$SRC")" ;;
esac
[[ "$VAL" == *$'\n'* ]] && die "value is multi-line — use --b64-file for PEMs/multi-line material"

# --- Replace any existing line for NAME, append the new one ---
grep -v "^${NAME}=" "$DEC" > "$NEW" || true
[[ -s "$NEW" && -n "$(tail -c1 "$NEW")" ]] && echo >> "$NEW"
printf '%s=%s\n' "$NAME" "$VAL" >> "$NEW"
chmod 600 "$NEW"

if grep -q "^${NAME}=" "$DEC"; then
    EXISTED="updated"
else
    EXISTED="added"
fi
if [[ "$DRY_RUN" == true ]]; then
    echo "[dry-run] would $EXISTED $NAME (${#VAL} chars) in values.age and regenerate $LOCAL_SECRETS"
    exit 0
fi

# --- Re-encrypt, verify the new ciphertext before swapping ---
age -r "$RECIP" -o "$VALUES.tmp" "$NEW"
check_no_drops
if age --decrypt -i "$CACHE" "$VALUES.tmp" | grep -q "^${NAME}="; then
    mv "$VALUES.tmp" "$VALUES"
else
    rm -f "$VALUES.tmp"; die "verification failed — values.age left untouched"
fi

write_local "$NEW"
echo "OK: ${NAME} ${EXISTED} in values.age + $LOCAL_SECRETS. Remember to update registry.md."
