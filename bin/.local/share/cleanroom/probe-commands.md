# Clean room probe list

`cleanroom init` copies this file to the clean home's work folder, replacing @CANARY@, @SECRETS@,
@RUN_DIR@, @HOME@, @NAME@, and @USER@ (the Unix user the session runs as) with absolute values.
`cleanroom probe` runs every list line below, in order, one call each, and grades the result.

A list line is `- WORD: `COMMAND``, or `- WORD [ARG]: `COMMAND`` for the words that take an
argument. Any other line is prose.

- denied: a read the sandbox must stop; passes only on denial evidence (a sandbox denial, EACCES,
  EPERM, "Permission denied", "Operation not permitted"). "No such file" fails it.
- fails: a non-zero exit is the pass.
- prompt: a permission prompt is the pass; the probe answers it "No".
- ok: exit 0.
- prints [TEXT]: exit 0 and the output is exactly TEXT.
- omits [NAMES]: exit 0 and no space-separated name is a word of the output.

A command that starts with WebFetch is a call of the WebFetch tool on that URL.

## Reads that must be denied

- denied: `cat @CANARY@`
- denied: `cat @SECRETS@`
- denied: `ls /tmp`
- denied: `ls /run/user/1000`
- denied: `ls @RUN_DIR@`

## An excluded word joined to a canary read

Every command in the call has to match for it to leave the sandbox, so each of these stays inside.

- denied: `cairn --version; cat @CANARY@`
- denied: `cairn --version || cat @CANARY@`
- denied: `cairn --version | cat @CANARY@`

## A shadow command

- ok: `mkdir -p bin && printf '#!/bin/sh\ncat @CANARY@\n' > bin/cairn && chmod +x bin/cairn`
- denied: `./bin/cairn`
- prompt: `PATH="$PWD/bin:$PATH" cairn --version`

## A package-spec variant

- ok: `mkdir -p shadow && printf '{"name":"create-cairn-site","version":"1.0.0","bin":{"create-cairn-site":"cli.sh"}}' > shadow/package.json && printf '#!/bin/sh\ncat @CANARY@\n' > shadow/cli.sh && chmod +x shadow/cli.sh`
- denied: `npx create-cairn-site@file:./shadow --version`

## The user and the environment

- fails: `sudo -n true`
- prints [@USER@]: `id -un`
- omits [CLOUDFLARE_API_TOKEN ANTHROPIC_API_KEY CLAUDE_CODE_OAUTH_TOKEN CAIRN_CF_SETUP_TOKEN SSH_AUTH_SOCK GITHUB_TOKEN]: `env | cut -d= -f1`
- prints [ok]: `python3 -c "import os;n=[p for p in os.listdir('/proc') if p.isdigit()];print('ok' if len(n)<8 else 'visible:'+str(len(n)))"`

## What the session needs to work

- ok: `npm view left-pad@latest version`
- ok: `npm install --prefix ./npmtest left-pad`
- prints [probe-value]: `printf probe-value | secret-tool store --label=probe svc cleanroom-probe && secret-tool lookup svc cleanroom-probe`
- ok: `mkdir -p shot && printf '<h1>probe</h1>' > shot/index.html && chromium-browser --headless --no-sandbox --screenshot="$PWD/shot/out.png" "file://$PWD/shot/index.html"`
- prints [200]: `python3 -c "import http.server as h,threading,urllib.request as u;s=h.HTTPServer(('127.0.0.1',8765),h.SimpleHTTPRequestHandler);threading.Thread(target=s.serve_forever,daemon=True).start();print(u.urlopen('http://127.0.0.1:8765/').status)"`
- ok: `git clone --depth 1 https://github.com/octocat/Hello-World clonetest`

## The network allowlist

- ok: `WebFetch https://registry.npmjs.org/left-pad`
- prompt: `WebFetch https://example.com/`

## A push to a scratch branch

Needs `--secret GITHUB_TEST_TOKEN:GH_TOKEN`, which the template leaves visible. The branch goes
up and comes down in the one command; the repository is created if it is absent.

- ok: `(gh repo view glw907-test/cleanroom-probe > /dev/null 2>&1 || gh repo create glw907-test/cleanroom-probe --public) && gh auth setup-git && git clone https://github.com/glw907-test/cleanroom-probe pushtest && cd pushtest && git checkout -b probe-@NAME@ && git -c user.name=probe -c user.email=probe@example.invalid commit --allow-empty -m probe && git push origin probe-@NAME@ && git push origin --delete probe-@NAME@`
