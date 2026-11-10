# Clean room probe list

`cleanroom init` copies this file to the clean home's work folder, replacing @CANARY@, @SECRETS@,
@RUN_DIR@, @HOME@, @NAME@, and @USER@ (the Unix user the session runs as) with absolute values.
`cleanroom probe` runs every list line below, in order, one call each, and grades the result.

A list line is `- WORD: `COMMAND``, or `- WORD [ARG]: `COMMAND`` for the words that take an
argument. Any other line is prose.

- denied: a read the sandbox must stop; passes on denial evidence (a sandbox denial, EACCES,
  EPERM, "Permission denied", "Operation not permitted") or on masking: the sandbox hides a
  denied path, so a "No such file" that names, as a whole path, one a denied item names and that
  exists outside the sandbox before the session starts passes too, and so does an empty listing
  of a directory that is non-empty outside. A "No such file" for any other path fails it.
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
- prints [200]: `python3 -c "import http.server as h,threading,urllib.request as u;s=h.HTTPServer(('127.0.0.1',8765),type('Q',(h.SimpleHTTPRequestHandler,),{'log_message':lambda *a:0}));threading.Thread(target=s.serve_forever,daemon=True).start();print(u.urlopen('http://127.0.0.1:8765/').status)"`
- ok: `git clone --depth 1 https://github.com/octocat/Hello-World clonetest`

## The network allowlist

- ok: `WebFetch https://registry.npmjs.org/left-pad`
- prompt: `WebFetch https://example.com/`

## A push to a scratch branch

The repository is `glw907-test/cleanroom-push`, created with a README so `main` is its default branch (the first branch pushed to an empty repository becomes the default and cannot be deleted). Needs `--secret GITHUB_TEST_TOKEN:GH_TOKEN`, which the template leaves visible. The branch goes
up and comes down in `push.sh`, which `init` writes into the work folder from
`probe-push.sh` because Claude Code asks before it runs a chain of shell operators; the
repository is created if it is absent.

- ok: `sh ./push.sh`

## The launcher resolves the gate candidate

`create-cairn-site@latest` is the retired 0.99.0-rc.4 wizard, which prints a "Retired:" notice when it
runs, so a call that reaches it fails these items. The first item asks the registry for the resolved
version from inside the sandbox, where `npm view` matches no exclusion. The next two run the launcher
outside it. The last item is the positive one: it reads the versions the clean home's npx cache holds,
apart from the shadow package an earlier item writes, and prints `gate` only when every one is a 2.x
build. It prints `other-<version>` for any other version and an empty line for an empty cache, and the
item passes on `gate` alone, so it fails on an empty cache, on the wizard, and on any other version. The
`omits` items pass on an empty output, which makes them negative checks only.

- omits [0.99.0-rc.4]: `npm view create-cairn-site version`
- omits [Retired:]: `npm create cairn-site -- --help`
- omits [Retired:]: `npx create-cairn-site --help`
- prints [gate]: `node -e "const g=require('fs').globSync('@HOME@/.npm/_npx/*/node_modules/create-cairn-site/package.json');console.log([...new Set(g.map(f=>require(f).version).filter(v=>v!=='1.0.0').map(v=>v.startsWith('2.')&&'gate'||'other-'+v))].join(','))"`

## An excluded command stays out of reach of every credential

`npx create-cairn-site` matches an excluded pattern, so it runs outside the sandbox with the setup
token. The first item chains it to commands that match no pattern, so the whole call stays in the
sandbox and reports the canary `DENIED`. Three items then try to plant code the launcher would run
outside the sandbox. Writing into the clean home's npx cache or a work-folder `.npmrc` makes Claude
Code ask first, so those two items expect the prompt and the probe answers it "No": they prove the
plant needs an approval, and nothing runs afterward. A hand-written package under `./node_modules`
plants with no prompt, so the last item runs it. Its code prints `probe-run`, the user it runs as, and
`READABLE` or `DENIED` for `test -r` on the canary, never the canary's value, and the item passes only
on exactly that line with `DENIED`. Every list command is a distinct string, because the probe matches a
call by its command. The planted code uses no `?` and no `!=`, each of which made Claude Code ask before
it ran a printf command.

- omits [READABLE]: `npx create-cairn-site --help && id -un && (test -r @CANARY@ && echo READABLE || echo DENIED)`
- prompt: `for f in @HOME@/.npm/_npx/*/node_modules/create-cairn-site/bin.mjs; do printf 'x\n' >> "$f"; done`
- prompt: `printf 'node-options=--require ./probe.cjs\n' > .npmrc`
- ok: `printf 'console.log("probe-run",require("os").userInfo().username,["READABLE","DENIED"][Math.min(1,require("child_process").spawnSync("test",["-r","@CANARY@"]).status)])\n' > probe.cjs`
- ok: `mkdir -p node_modules/create-cairn-site && printf '{"name":"create-cairn-site","version":"1.0.0","bin":{"create-cairn-site":"cli.cjs"}}' > node_modules/create-cairn-site/package.json && printf '#!/usr/bin/env node\nrequire("../../probe.cjs")\n' > node_modules/create-cairn-site/cli.cjs && chmod +x node_modules/create-cairn-site/cli.cjs && mkdir -p node_modules/.bin && ln -s ../create-cairn-site/cli.cjs node_modules/.bin/create-cairn-site`
- prints [probe-run @USER@ DENIED]: `npx create-cairn-site -h`
- ok: `rm -rf node_modules probe.cjs`
