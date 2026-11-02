#!/usr/bin/env bash
# Surface shell-environment drift for Claude context: exports, aliases, and
# shell functions, after a line naming the host. The machine inventory lives in
# CLAUDE.md; this exists to catch what changed since that file was last updated.

# Two workstations share this config, so the host is read here, never from a doc.
case $(cat /sys/class/dmi/id/chassis_type 2>/dev/null) in
    8|9|10|14|31|32) form=laptop ;;
    3|4|5|6|7|13|15|35|36) form=desktop ;;
    *) form=unknown ;;
esac
echo "## Host: $(hostname) ($(cat /sys/class/dmi/id/product_name 2>/dev/null), $form)"
echo ""
# Initiatives that touch this session's repo. The repo is named by the origin
# remote, read through the common git dir so a worktree reports its parent and
# the ~/.dotfiles checkout reports "workstation". Never fails the hook.
initiatives() {
    local common url repo dir f st line out=""
    common=$(git rev-parse --path-format=absolute --git-common-dir 2>/dev/null) || return 0
    url=$(git --git-dir="$common" config remote.origin.url 2>/dev/null) || return 0
    repo=$(basename "${url%/}")
    repo=${repo%.git}
    [[ -n $repo ]] || return 0

    dir=${INITIATIVES_DIR:-$HOME/Projects/initiatives}
    if [[ ! -d $dir ]]; then
        echo "## Initiatives ($repo)"
        echo "initiatives: no clone at ~/Projects/initiatives"
        echo ""
        return 0
    fi
    if ! command -v yq >/dev/null 2>&1; then
        echo "## Initiatives ($repo)"
        echo "initiatives: yq not found"
        echo ""
        return 0
    fi

    for f in "$dir"/*/initiative.yaml; do
        [[ -f $f ]] || continue
        if ! st=$(yq -r '.status' "$f" 2>/dev/null); then
            out+="initiatives: unreadable $f"$'\n'
            continue
        fi
        [[ $st == active || $st == proposed ]] || continue
        yq -r '.repos[]' "$f" 2>/dev/null | grep -qxF -- "$repo" || continue
        line=$(yq -r '"- " + .id + ": " + .summary' "$f" 2>/dev/null) || {
            out+="initiatives: unreadable $f"$'\n'
            continue
        }
        out+="$line"$'\n'
    done
    [[ -n $out ]] || return 0
    echo "## Initiatives ($repo)"
    printf '%s\n' "$out"
}
initiatives || true

# Fast-forward the checkouts this workstation runs its skills, tools, and secrets from, since the
# other workstation pushes to them (Geoff, 2026-10-28: thinkpad-x1 ran 113, 98, and 34 commits
# behind). A checkout is pulled only on its default branch with no other live session in it, and
# --ff-only refuses a dirty or diverged one; each that stays behind is named. FRESH_CHECKOUTS
# replaces the list and CLAUDE_AGENTS_CMD the session listing, for tests. Never fails the hook.
fresh_checkouts() {
    local self=$1 live repo name def old behind out=""
    local list=${FRESH_CHECKOUTS-"$HOME/.dotfiles $HOME/Projects/approval-queue $HOME/Projects/servers $HOME/Projects/initiatives"}
    [[ -n $list ]] || return 0
    local -a agents
    read -ra agents <<<"${CLAUDE_AGENTS_CMD:-claude agents --json}"
    live=$(timeout 10 "${agents[@]}" 2>/dev/null |
        jq -r --arg self "$self" '.[] | select(.sessionId != $self) | .cwd // empty' 2>/dev/null)
    for repo in $list; do
        [[ -d $repo/.git ]] || continue
        name=${repo##*/}
        if ! timeout 8 git -C "$repo" fetch -q origin 2>/dev/null; then
            out+="- $name: the fetch failed, so it may be behind"$'\n'
            continue
        fi
        def=$(git -C "$repo" symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null)
        def=${def#origin/}
        def=${def:-main}
        behind=$(git -C "$repo" rev-list --count "HEAD..origin/$def" 2>/dev/null) || continue
        [[ $behind -gt 0 ]] || continue
        old=$(git -C "$repo" rev-parse HEAD)
        if [[ $(git -C "$repo" branch --show-current) != "$def" ]]; then
            out+="- $name: $behind behind origin/$def, not pulled: the checkout is on another branch"$'\n'
        elif grep -qxF -- "$repo" <<<"$live"; then
            out+="- $name: $behind behind origin/$def, not pulled: another session is live in it"$'\n'
        elif git -C "$repo" merge -q --ff-only "origin/$def" >/dev/null 2>&1; then
            if [[ $behind -eq 1 ]]; then out+="- $name: pulled 1 commit"$'\n'; else out+="- $name: pulled $behind commits"$'\n'; fi
            if git -C "$repo" diff --name-only "$old" HEAD | grep -qx 'secrets/values.age'; then
                out+="- $name: the secret store changed; run scripts/secrets/secret-set.sh --sync"$'\n'
            fi
        else
            out+="- $name: $behind behind origin/$def, not pulled: the fast-forward was refused"$'\n'
        fi
    done
    [[ -n $out ]] || return 0
    echo "## Checkouts"
    printf '%s\n' "$out"
}
session_id=""
[[ -t 0 ]] || session_id=$(timeout 2 jq -r '.session_id // empty' 2>/dev/null)
fresh_checkouts "$session_id" || true

echo "## Shell Environment (drift check; canonical inventory is CLAUDE.md)"
echo ""

# Redacts the value of any export ANYWHERE in a line, not only line-anchored
# ones, so a one-line function body or alias carrying an export cannot leak
# a value into session context (this channel once carried a real token).
redact() {
    sed -E 's/(export[[:space:]]+[A-Za-z_][A-Za-z0-9_]*)=[^;)}&|]*/\1=<value redacted>/g'
}

if [[ -f ~/.bash_aliases ]]; then
    echo "### Aliases (~/.bash_aliases)"
    echo '```bash'
    (grep -E '^alias ' ~/.bash_aliases || echo "# none") | redact
    echo '```'
    echo ""
fi

if [[ -f ~/.bashrc ]]; then
    echo "### Exports and functions (~/.bashrc)"
    echo '```bash'
    (grep -E '^export |^[a-zA-Z_][a-zA-Z0-9_-]*\(\)' ~/.bashrc || echo "# none") | redact
    echo '```'
    echo ""
fi

if [[ -f ~/.profile ]] && grep -q '^export' ~/.profile; then
    echo "### Exports (~/.profile)"
    echo '```bash'
    grep '^export' ~/.profile | redact
    echo '```'
    echo ""
fi
