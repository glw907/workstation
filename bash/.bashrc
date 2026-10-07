# ~/.bashrc: executed by bash(1) for non-login shells.
# see /usr/share/doc/bash/examples/startup-files (in the package bash-doc)
# for examples

# If not running interactively, don't do anything
case $- in
    *i*) ;;
      *) return;;
esac

# don't put duplicate lines or lines starting with space in the history.
# See bash(1) for more options
HISTCONTROL=ignoreboth

# append to the history file, don't overwrite it
shopt -s histappend

# for setting history length see HISTSIZE and HISTFILESIZE in bash(1)
HISTSIZE=1000
HISTFILESIZE=2000

# check the window size after each command and, if necessary,
# update the values of LINES and COLUMNS.
shopt -s checkwinsize

# If set, the pattern "**" used in a pathname expansion context will
# match all files and zero or more directories and subdirectories.
#shopt -s globstar

# make less more friendly for non-text input files, see lesspipe(1)
[ -x /usr/bin/lesspipe ] && eval "$(SHELL=/bin/sh lesspipe)"

# set variable identifying the chroot you work in (used in the prompt below)
if [ -z "${debian_chroot:-}" ] && [ -r /etc/debian_chroot ]; then
    debian_chroot=$(cat /etc/debian_chroot)
fi

# set a fancy prompt (non-color, unless we know we "want" color)
case "$TERM" in
    xterm-color|*-256color) color_prompt=yes;;
esac

# uncomment for a colored prompt, if the terminal has the capability; turned
# off by default to not distract the user: the focus in a terminal window
# should be on the output of commands, not on the prompt
#force_color_prompt=yes

if [ -n "$force_color_prompt" ]; then
    if [ -x /usr/bin/tput ] && tput setaf 1 >&/dev/null; then
	# We have color support; assume it's compliant with Ecma-48
	# (ISO/IEC-6429). (Lack of such support is extremely rare, and such
	# a case would tend to support setf rather than setaf.)
	color_prompt=yes
    else
	color_prompt=
    fi
fi

if [ "$color_prompt" = yes ]; then
    PS1='${debian_chroot:+($debian_chroot)}\[\033[01;32m\]\u@\h\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\]\$ '
else
    PS1='${debian_chroot:+($debian_chroot)}\u@\h:\w\$ '
fi
unset color_prompt force_color_prompt

# If this is an xterm, title the tab with the directory the shell started in.
# The title stays fixed after a cd; programs that set their own title still
# override it until the next prompt.
case "$TERM" in
xterm*|rxvt*)
    if [ "$PWD" = "$HOME" ]; then
        TAB_TITLE='~'
    else
        TAB_TITLE=${PWD##*/}
        TAB_TITLE=${TAB_TITLE:-/}
    fi
    PS1='\[\e]0;${TAB_TITLE}\a\]'"$PS1"
    ;;
*)
    ;;
esac

# enable color support of ls and also add handy aliases
if [ -x /usr/bin/dircolors ]; then
    test -r ~/.dircolors && eval "$(dircolors -b ~/.dircolors)" || eval "$(dircolors -b)"
    alias ls='ls --color=auto'
    #alias dir='dir --color=auto'
    #alias vdir='vdir --color=auto'

    alias grep='grep --color=auto'
    alias fgrep='fgrep --color=auto'
    alias egrep='egrep --color=auto'
fi

# colored GCC warnings and errors
#export GCC_COLORS='error=01;31:warning=01;35:note=01;36:caret=01;32:locus=01:quote=01'

# some more ls aliases
alias ll='ls -alF'
alias la='ls -A'
alias l='ls -CF'

# Add an "alert" alias for long running commands.  Use like so:
#   sleep 10; alert
alias alert='notify-send --urgency=low -i "$([ $? = 0 ] && echo terminal || echo error)" "$(history|tail -n1|sed -e '\''s/^\s*[0-9]\+\s*//;s/[;&|]\s*alert$//'\'')"'

# Alias definitions.
# You may want to put all your additions into a separate file like
# ~/.bash_aliases, instead of adding them here directly.
# See /usr/share/doc/bash-doc/examples in the bash-doc package.

if [ -f ~/.bash_aliases ]; then
    . ~/.bash_aliases
fi

# enable programmable completion features (you don't need to enable
# this, if it's already enabled in /etc/bash.bashrc and /etc/profile
# sources /etc/bash.bashrc).
if ! shopt -oq posix; then
  if [ -f /usr/share/bash-completion/bash_completion ]; then
    . /usr/share/bash-completion/bash_completion
  elif [ -f /etc/bash_completion ]; then
    . /etc/bash_completion
  fi
fi
export PATH="$HOME/.local/bin:$PATH"
# cld: the Claude launcher at ~/.local/bin/cld

# Claude sudo helper setup
export SUDO_ASKPASS="$HOME/.local/bin/claude-askpass"

# Claude wrapper function - adds browser tools in web repos, clears sudo token on exit.
# Browser tools cost context in every session, so only the web repos opt in; Go work
# (poplar, jrnl-md) stays lean. Override either way with an explicit --chrome / --no-chrome.
claude() {
    local args=("$@")

    case "$1" in
        # Subcommands take their own flags; never inject --chrome into them.
        mcp|config|plugin|update|doctor|install|setup-token|migrate-installer) ;;
        *)
            case " $* " in
                *" --chrome "*|*" --no-chrome "*) ;;
                *)
                    case "$PWD/" in
                        "$HOME"/Projects/ecxc-ski/*|\
                        "$HOME"/Projects/907-life/*|\
                        "$HOME"/Projects/cairn-*/*|\
                        "$HOME"/Projects/aksailingclub-*/*|\
                        "$HOME"/Projects/asc-*/*|\
                        "$HOME"/Projects/smallbusinessak-org/*|\
                        "$HOME"/Projects/hugo-blog-template/*)
                            args+=(--chrome)
                            ;;
                    esac
                    ;;
            esac
            ;;
    esac

    command claude "${args[@]}"
    claude-sudo-clear 2>/dev/null
    ~/.dotfiles/scripts/secrets/secret-session-clear.sh >/dev/null 2>&1
}

# Hugo blog management functions (works across all blogs in ~/Projects)
if [ -f ~/.bash_blog_functions ]; then
    . ~/.bash_blog_functions
fi

# Android SDK
export ANDROID_HOME="$HOME/Android"
export PATH="$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools:$PATH"

# SSH Agent (auto-start for GitHub authentication)
if [ -z "$SSH_AUTH_SOCK" ]; then
    eval "$(ssh-agent -s)" > /dev/null
    ssh-add ~/.ssh/id_ed25519 2>/dev/null
fi

# Google Workspace API Configuration
export GOOGLE_APPLICATION_CREDENTIALS="$HOME/.config/google-workspace/credentials.json"
export WORKSPACE_ADMIN_EMAIL="geoff.wright@aksailingclub.org"

# age key for ASC project encryption
export AGE_KEY_FILE="$HOME/.config/age/asc-key.txt"

# MusicBrainz contact for the dubplate harness User-Agent (public per MB terms)
export DUBPLATE_HARNESS_CONTACT="geoff@907.life"


# Load workstation secrets (decrypted by ~/.dotfiles/scripts/secrets/sync.sh)
# Run sync.sh after any credential rotation to update this file.
[ -f "$HOME/.local/secrets" ] && source "$HOME/.local/secrets"

# Homebrew (Bluefin DX and any other machine with linuxbrew installed)
[ -x /home/linuxbrew/.linuxbrew/bin/brew ] && eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"

# mise (Bluefin DX Node/tool version manager)
command -v mise > /dev/null 2>&1 && eval "$(mise activate bash)"
