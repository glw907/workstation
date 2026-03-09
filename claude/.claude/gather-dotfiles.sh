#!/usr/bin/env bash
# Gather relevant dotfile configurations for Claude context
# This script outputs key shell configuration details

echo "## Shell Configuration"
echo ""

# Check for bash aliases
if [[ -f ~/.bash_aliases ]]; then
    echo "### Custom Aliases (~/.bash_aliases)"
    echo '```bash'
    cat ~/.bash_aliases
    echo '```'
    echo ""
fi

# Check for bashrc customizations (last 50 lines to avoid too much output)
if [[ -f ~/.bashrc ]]; then
    echo "### Recent .bashrc customizations (last 50 lines)"
    echo '```bash'
    tail -50 ~/.bashrc | grep -v "^#" | grep -v "^$" || echo "# No recent customizations"
    echo '```'
    echo ""
fi

# Check for custom environment variables in .profile
if [[ -f ~/.profile ]]; then
    # Look for export statements
    if grep -q "^export" ~/.profile 2>/dev/null; then
        echo "### Custom Environment Variables (~/.profile)"
        echo '```bash'
        grep "^export" ~/.profile
        echo '```'
        echo ""
    fi
fi
