#!/usr/bin/env bash
# check-guidance-cite.sh [base]: warn when a branch changes Claude guidance files (skills, agents,
# settings.json, CLAUDE.md) and no commit message cites an Anthropic page. Warning only: always
# exits 0, and a base that does not resolve is skipped, so check.sh's `run` never fails on it.
set -uo pipefail
cd "$(dirname "$0")/.."
base="${1:-origin/main}"

skip() { echo "guidance citation check skipped: $1"; exit 0; }

git rev-parse --verify -q "$base^{commit}" >/dev/null || skip "base '$base' does not resolve"
changed=$(git diff --name-only "$base"...HEAD 2>/dev/null) || skip "git diff against '$base' failed"
messages=$(git log --format=%B "$base"..HEAD 2>/dev/null) || skip "git log against '$base' failed"

guidance=$(grep -E '^(claude/\.claude/(skills|agents)/|claude/\.claude/(settings\.json|CLAUDE\.md)$)' <<<"$changed" || true)
[ -n "$guidance" ] || exit 0

# A cite is a URL whose host is anthropic.com, claude.com, or a subdomain of either. A bare
# address such as the Co-Authored-By trailer carries no scheme and never matches.
while IFS= read -r url; do
    host=${url#*://}
    host=${host%%[/?#]*}
    host=${host##*@}
    host=${host%%:*}
    host=${host,,}
    case "$host" in
        anthropic.com|claude.com|*.anthropic.com|*.claude.com) exit 0 ;;
    esac
done < <(grep -oiE 'https?://[^[:space:]<>")]+' <<<"$messages")

echo "WARNING: guidance changed with no Anthropic page URL in a commit message: $(tr '\n' ' ' <<<"$guidance" | sed 's/ $//')"
exit 0
