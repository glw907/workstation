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
