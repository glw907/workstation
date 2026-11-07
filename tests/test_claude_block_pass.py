"""Tests for the claude-block-pass PreToolUse hook and the Proton token pattern in claude-secret-guard."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

BIN = Path(__file__).resolve().parent.parent / "bin/.local/bin"
BLOCK = BIN / "claude-block-pass"
GUARD = BIN / "claude-secret-guard"

DENIED = [
    "pass-cli item view pass://Age key/key/key",
    "pass-cli login",
    "PROTON_PASS_SESSION_DIR=/tmp/x pass-cli info",
    "cd ~ && pass-cli item list",
    "echo hi; pass-cli logout",
    "env FOO=1 pass-cli agent create x",
    "sudo pass-cli info",
    "(pass-cli info)",
    "x=$(pass-cli item view pass://a/b/c)",
    "secret-tool lookup service proton-pass-agent host pavilion",
    "echo go && secret-tool lookup service x",
    "keyctl print 123",
    "keyctl pipe 123",
    "keyctl read 123",
    "sudo keyctl print @u",
    "ls $XDG_RUNTIME_DIR/pass-ws",
    "cat /run/user/1000/pass-ws/session",
    "ls /run/user/1000/pass-recv.AbC123",
    "cat ~/.local/share/proton-pass-cli/.session/data",
    "tar c ~/.local/share/proton-pass-cli",
    # Wrappers, shell keywords, and nesting.
    "bash -c 'pass-cli info'",
    'bash -c "pass-cli info"',
    "echo info | xargs pass-cli",
    "eval pass-cli info",
    "watch pass-cli info",
    "stdbuf -o0 pass-cli info",
    "sudo -u glw907 pass-cli info",
    "nice -n 5 pass-cli info",
    "timeout -s KILL 5 pass-cli info",
    "timeout 5 pass-cli info",
    "if pass-cli info; then :; fi",
    "! pass-cli info",
    "{ pass-cli info; }",
    "for i in 1; do pass-cli info; done",
    # Path prefixes and options before the subcommand.
    "/home/linuxbrew/.linuxbrew/bin/pass-cli info",
    "$(brew --prefix)/bin/pass-cli info",
    "/usr/bin/secret-tool lookup service x",
    "/usr/bin/keyctl print 1",
    "keyctl -v print 1",
    # secret-tool search prints the secret too.
    "secret-tool search service proton-pass-agent",
    "secret-tool search --all service x",
    # Quoting and continuation tricks.
    "'pass-cli' info",
    '"pass-cli" info',
    "p''ass-cli info",
    "\\pass-cli info",
    "pass\\\n-cli info",
    # Session directories by glob or the count script's own.
    "ls $XDG_RUNTIME_DIR/pass-count.abc",
    "cat $XDG_RUNTIME_DIR/pass-w*/session",
    "ls ~/.local/share/proton-pass-*",
    "cd $XDG_RUNTIME_DIR && cat pass-ws.abc/session",
    # Combined and leading shell flags, other pass-through wrappers.
    'bash -lc "pass-cli info"',
    "sh -ec pass-cli",
    "zsh -ic pass-cli",
    'bash -x -c "pass-cli"',
    "bash --norc -c pass-cli",
    'busybox sh -c "pass-cli"',
    "ionice -c 3 pass-cli info",
    "strace -f pass-cli info",
    "unbuffer pass-cli info",
    # More session-directory globs.
    "cat /run/user/1000/pass-*/session",
    "cat /run/user/1000/pass-c*/x",
    "cat /run/user/1000/pass-w?.abc/x",
    "cat /run/user/1000/pass-[w]s.a/x",
    # claude-pass's own session directory: Claude goes through claude-pass, never into its dir.
    "ls $XDG_RUNTIME_DIR/pass-agent.Xy12Ab",
    "cat /run/user/1000/pass-agent.Xy12Ab/session",
    "cat /run/user/1000/pass-a*/session",
    # Bare pass-cli stays denied next to the claude-pass route.
    "claude-pass --status && pass-cli item list",
    # claude-pass run is a wrapper, so a pass-cli after it is still a command.
    "claude-pass run -- env -u PROTON_PASS_SESSION_DIR pass-cli item list",
    "claude-pass run -- bash -c 'pass-cli vault list'",
    "claude-pass run pass-cli info",
    # A heredoc that feeds a shell still runs its body.
    "bash <<'EOF'\npass-cli info\nEOF",
    "ssh geoff@ward.907.life <<EOF\npass-cli info\nEOF",
    "cat > /tmp/x <<'EOF'\nnotes\nEOF\npass-cli info",
    # An unescaped pipe is still a pipe.
    "echo x | pass-cli info",
    # pass-sitting's session directory, by name and by glob.
    "ls $XDG_RUNTIME_DIR/pass-sitting.AbC123",
    "cat $XDG_RUNTIME_DIR/pass-s*/session",
    "cat /run/user/1000/pass-s?/x",
    "cat $XDG_RUNTIME_DIR/pass-sitting*/session.json",
    "ls $XDG_RUNTIME_DIR/pass-sitting*",
    "ls -d $XDG_RUNTIME_DIR/pass-si*/",
    "cat $XDG_RUNTIME_DIR/pass-sitt*/session.json",
    "d=$(ls -d $XDG_RUNTIME_DIR/pass-sitting?*)",
    "ls $XDG_RUNTIME_DIR/pass-agent*",
    "ls $XDG_RUNTIME_DIR/pass-co*",
    "ls $XDG_RUNTIME_DIR/pass-ag*",
    "ls -d $XDG_RUNTIME_DIR/pass-{agent,ws}.*",
    "ls ~/.local/share/proton*",
    # A fake heredoc start in a comment, a quote, or arithmetic must not hide the next line.
    "# <<EOF\npass-cli info",
    "echo '<<EOF'\npass-cli info",
    "echo $((1<<x))\npass-cli info",
    # A redirection before the command or glued to its name, ANSI-C quoting, case arms, coproc.
    "</dev/null pass-cli info",
    "2>&1 pass-cli info",
    "pass-cli>&2 item list",
    "pass-cli>/tmp/o item list",
    "secret-tool>&2 lookup service proton-pass-agent-claude host x",
    "</dev/null secret-tool lookup service x",
    "keyctl>&2 print 123",
    "$'pass-cli' info",
    '$"pass-cli" info',
    "case 1 in 1) pass-cli info;; esac",
    "coproc pass-cli info",
    "/bin/bash <<EOF\npass-cli info\nEOF",
    # A session name stays a match when a bare prefix or a short suffix ends the component.
    "ls $XDG_RUNTIME_DIR/pass-ws/",
    # A script names a session directory with a variable, a long tail, or odd characters.
    "cat $XDG_RUNTIME_DIR/pass-ws.$id/session",
    "cat $XDG_RUNTIME_DIR/pass-agent.${s}/x",
    "cat $XDG_RUNTIME_DIR/pass-sitting.$x/session",
    "ls -d $XDG_RUNTIME_DIR/pass-recv.XXXXXXXXXXXXX",
    "ls $XDG_RUNTIME_DIR/pass-count.ab_cd",
    "ls $XDG_RUNTIME_DIR/pass-ws.abc-1",
    "cp -r $XDG_RUNTIME_DIR/pass-agent.abc:/tmp",
    "echo ${d:-$XDG_RUNTIME_DIR/pass-ws.abc}",
    "ls {$XDG_RUNTIME_DIR/pass-ws.abc,x}",
    "ls $XDG_RUNTIME_DIR/pass-ws.abc,",
    "ls $XDG_RUNTIME_DIR/pass-ws.",
    "find $XDG_RUNTIME_DIR -name pass-agent.\\*",
    # A variable, substitution, or backtick glued to the command name.
    "pass-cli$x info",
    "pass-cli${x} info",
    "pass-cli$() info",
    "pass-cli`` info",
    # ANSI-C quoting that spells the name with hex or octal escapes.
    "$'pass\\x2dcli' info",
    "$'pass\\055cli' info",
    "$'\\x70ass-cli' info",
    # A glob or brace on the command name, and on the session prefix.
    "~/.local/bin/pass-cl? info",
    "pass-cl{i,} info",
    "ls $XDG_RUNTIME_DIR/pas?-agent.x",
    "ls $XDG_RUNTIME_DIR/*-agent.*",
    "builtin pass-cli info",
    # An escaped << and $[...] arithmetic open no heredoc, so the next line runs.
    "echo x \\<<EOF\npass-cli info\nEOF",
    "echo $[1<<x]\npass-cli info\nx",
    # A glob or brace before or inside pass- on the command word expands to pass-cli.
    "p*-cli info",
    "pa?s-cli info",
    "[p]ass-cli info",
    "{pass-cli,} info",
    "~/.local/bin/p?ss-cli info",
    "/usr/bin/*ass-cli info",
    # A heredoc piped into a shell runs its body; a fake one inside ${...} hides nothing.
    "cat <<EOF | bash\npass-cli info\nEOF",
    "cat <<'EOF' | sh -s\npass-cli info\nEOF",
    "tee /dev/null <<EOF | bash\npass-cli info\nEOF",
    "echo ${x:-<<EOF}\npass-cli info\nEOF",
    # The default session directory by a bare name after a cd, a trailing slash, or a glob.
    "cd ~/.local/share && tar c proton-pass-cli",
    "cd ~/.local/share; cat proton-pass-cli/.session/data",
    "ls ~/.local/*/proton-pass-cli",
    "ls ~/.local/share/p*-pass-cli",
    "ls ~/.local/share/*pass-cli",
]

# Geoff alone runs pass-sitting, so the hook refuses it to Claude in every form, with a reason
# that says so.
SITTING = [
    "pass-sitting plan.jsonl",
    "pass-sitting --apply plan.jsonl",
    "~/.local/bin/pass-sitting x",
    "/var/home/glw907/.local/bin/pass-sitting x",
    "$HOME/.local/bin/pass-sitting x",
    "./bin/.local/bin/pass-sitting x",
    "bash bin/.local/bin/pass-sitting x",
    "source ~/.local/bin/pass-sitting",
    ". ~/.local/bin/pass-sitting",
    "~/.local/bin/pass-s* x",
    "env A=1 pass-sitting x",
    "bash -c 'pass-sitting x'",
    "echo x | xargs pass-sitting",
    "cd ~ && pass-sitting x",
    '"pass-sitting" x',
    "p''ass-sitting x",
    "nohup pass-sitting x",
    "x=`pass-sitting`",
    "~/.local/bin/pass-sit* x",
    "~/.local/bin/pass-sittin? x",
    "~/.local/bin/pass-sitting? x",
    "/usr/bin/bash ~/.local/bin/pass-sitting --apply x",
    "/bin/sh ~/.local/bin/pass-sitting x",
    "busybox sh ~/.local/bin/pass-sitting x",
    "bash < ~/.local/bin/pass-sitting",
    "bash -s < ~/.local/bin/pass-sitting",
    "bash -o errexit ~/.local/bin/pass-sitting x",
    "bash -n +n ~/.local/bin/pass-sitting --apply f",
    "# <<EOF\npass-sitting --apply f",
    ">/tmp/o pass-sitting --apply f",
    "bash -O extglob ~/.local/bin/pass-sitting x",
    "bash <<'EOF'\npass-sitting x\nEOF",
    "pass-sitting$x --apply f",
    "pass-sitting${IFS}--apply f",
    "pass-sitting$(true) --apply f",
    "$'pass\\x2dsitting' --apply f",
    "$'pass-sitt\\151ng' --apply f",
    "~/.local/bin/pass-sittin{g,} x",
    "cat \\<<EOF\npass-sitting --apply f\nEOF",
    "bash -n +o noexec ~/.local/bin/pass-sitting --apply f",
    "bash -o noexec +o noexec ~/.local/bin/pass-sitting",
    "cat ~/.local/bin/pass-sitting | bash -s -- --apply f",
    "bash <(cat ~/.local/bin/pass-sitting) --apply f",
    "bash /dev/stdin --apply f < ~/.local/bin/pass-sitting",
    # -n excuses a shell only when no + option turns it back off.
    "cat ~/.local/bin/pass-sitting | bash -n +o noexec -s -- --apply f",
    "cat ~/.local/bin/pass-sitting | bash -n +n -s -- --apply f",
    # The stdin forms with a bare name, after a cd.
    "cd ~/.local/bin && cat pass-sitting | bash -s -- --apply f",
    "cd ~/.local/bin && bash <(cat pass-sitting) --apply f",
    "cd ~/.local/bin; bash /dev/stdin --apply f < pass-sitting",
    "cd ~/.local/bin; busybox sh -s < pass-sitting",
    "cd ~/.local/bin; rbash -s < pass-sitting",
    # A glob before or inside pass- on the command word.
    "*-sitting --apply f",
    "~/.local/bin/p*-sitting --apply f",
    "~/.local/bin/p?ss-sitting x",
    # A heredoc piped into a shell runs its body.
    "cat <<EOF | bash\npass-sitting --apply f\nEOF",
    "cat <<'EOF' | sh -s -- --apply f\npass-sitting --apply f\nEOF",
    "tee /dev/null <<EOF | bash -s\npass-sitting --apply f\nEOF",
]

ALLOWED = [
    "ws-pass-key --status",
    "secret-receive FOO",
    "secret-tool store --label x service y",
    "secret-tool --help",
    "keyctl show",
    "keyctl list @u",
    "grep -n passcli notes.txt",
    "cat docs/pass-cli-notes.md",
    "brew pin proton-pass-cli",
    "git commit -m 'mention pass-cli in the docs'",
    "echo 'run pass-cli later'",
    "ls ~/Projects/pass-client",
    "bash tests/ws-pass-key.test.sh",
    "ssh-add -l",
    # claude-pass is Claude's route into Proton Pass (Geoff, 2026-10-20).
    "claude-pass --status",
    "claude-pass item list --vault-name Infrastructure",
    "claude-pass item create login --vault-name Infrastructure --from-template - < /tmp/x.json",
    "printf '%s' \"$tmpl\" | claude-pass item create login --vault-name Projects --from-template -",
    "CLAUDE_PASS_REASON='rotate a key' claude-pass item view pass://Projects/x/password > /tmp/out",
    "claude-pass share list --output json",
    "bash tests/claude-pass.test.sh",
    "micro bin/.local/bin/claude-pass",
    # A session name is a whole path component: a file that only starts with one passes.
    "bash tests/pass-count.test.sh",
    "git log -- tests/pass-count.test.sh",
    # The pass-sitting source, its test, and mentions of it are not a run.
    "bash tests/pass-sitting.test.sh",
    "cat bin/.local/bin/pass-sitting",
    "git diff -- bin/.local/bin/pass-sitting",
    "shellcheck bin/.local/bin/pass-sitting",
    "bash -n bin/.local/bin/pass-sitting",
    "git commit -m 'add pass-sitting'",
    # False positives from real sessions (2026-10-19 to 2026-10-21).
    "command -v pass-cli pass-count ws-pass-key secret-receive; ",
    "grep -n -i 'never calls\\|pass-cli' ~/.claude/docs/bluefin-admin.md | head -8",
    "grep -rn -i 'proton-pass-cli\\|pass-cli' ~/.dotfiles/bluefin/Brewfile* 2>/dev/null | head -3",
    "cat > bin/.local/bin/claude-pass <<'EOF'\n#!/usr/bin/env bash\npass-cli \"$@\"\nEOF",
    "python3 -I - <<'EOF'\nold='''Claude never runs `pass-cli`; the hook denies it.'''\n- pass-cli in command position\nEOF",
    # Commands that look near the hook's patterns but run nothing it guards.
    "pass-access",
    "ls *",
    "cat docs/*.md",
    "brew pin proton-pass-cli",
    "bash -n bin/.local/bin/pass-sitting && shellcheck bin/.local/bin/pass-sitting",
]


def run(script, payload):
    return subprocess.run(
        [sys.executable, str(script)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        check=False,
    )


def bash(cmd):
    return {"tool_name": "Bash", "tool_input": {"command": cmd}, "session_id": "t"}


@pytest.mark.parametrize("cmd", DENIED)
def test_denied(cmd):
    result = run(BLOCK, bash(cmd))
    assert result.returncode == 0
    decision = json.loads(result.stdout)["hookSpecificOutput"]
    assert decision["permissionDecision"] == "deny"
    assert "ws-pass-key" in decision["permissionDecisionReason"]
    assert "claude-pass" in decision["permissionDecisionReason"]


@pytest.mark.parametrize("cmd", SITTING)
def test_pass_sitting_denied_to_claude(cmd):
    result = run(BLOCK, bash(cmd))
    assert result.returncode == 0
    decision = json.loads(result.stdout)["hookSpecificOutput"]
    assert decision["permissionDecision"] == "deny"
    assert "Geoff" in decision["permissionDecisionReason"]
    assert "pass-sitting" in decision["permissionDecisionReason"]


@pytest.mark.parametrize("cmd", ALLOWED)
def test_allowed(cmd):
    result = run(BLOCK, bash(cmd))
    assert result.returncode == 0
    assert result.stdout == ""


def test_denies_every_time_not_a_rate_limit():
    for _ in range(5):
        assert "deny" in run(BLOCK, bash("pass-cli info")).stdout


def test_ignores_non_bash_tools():
    payload = {"tool_name": "Write", "tool_input": {"content": "pass-cli info"}}
    assert run(BLOCK, payload).stdout == ""


def test_malformed_payload_fails_open():
    result = subprocess.run(
        [sys.executable, str(BLOCK)], input="not json", capture_output=True, text=True, check=False
    )
    assert result.returncode == 0
    assert result.stdout == ""


# The token literals are split so this file carries no token-shaped string itself.
PROTON_TOKEN = "pst_" + "a1B2c3D4e5F6g7H8" + "::" + "k9L0m1N2o3P4q5R6s7T8"


def test_secret_guard_blocks_proton_token():
    result = run(GUARD, {"tool_name": "Write", "tool_input": {"content": f"token {PROTON_TOKEN}\n"}})
    assert result.returncode == 2
    assert "Proton" in result.stderr


def test_secret_guard_blocks_proton_token_in_bash():
    result = run(GUARD, bash(f"curl -H 'x: {PROTON_TOKEN}' https://example.test"))
    assert result.returncode == 2


@pytest.mark.parametrize(
    "text",
    [
        "pst_ is the prefix of a Proton token",
        "the token looks like pst_xxxx::KEY in the docs",
        "set PROTON_PASS_PERSONAL_ACCESS_TOKEN before pass-cli login",
        "pst_short::tiny",
    ],
)
def test_secret_guard_passes_lookalikes(text):
    result = run(GUARD, {"tool_name": "Write", "tool_input": {"content": text}})
    assert result.returncode == 0
