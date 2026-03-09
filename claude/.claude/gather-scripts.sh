#!/usr/bin/env bash
# Gather information about user scripts for Claude context
# This script lists custom scripts in common locations

echo "## Custom Scripts"
echo ""

# Check ~/.local/bin
if [[ -d ~/.local/bin ]]; then
    SCRIPTS=$(find ~/.local/bin -maxdepth 1 -type f -executable 2>/dev/null)
    if [[ -n "$SCRIPTS" ]]; then
        echo "### Scripts in ~/.local/bin"
        echo '```'
        ls -1 ~/.local/bin
        echo '```'
        echo ""
    fi
fi

# Check ~/bin
if [[ -d ~/bin ]]; then
    SCRIPTS=$(find ~/bin -maxdepth 1 -type f -executable 2>/dev/null)
    if [[ -n "$SCRIPTS" ]]; then
        echo "### Scripts in ~/bin"
        echo '```'
        ls -1 ~/bin
        echo '```'
        echo ""
    fi
fi
