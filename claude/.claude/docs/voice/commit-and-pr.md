# Register: commit messages and PR bodies

The reader is a future developer skimming `git log` for what changed and why, often years
later and mid-debugging. Applies to every commit message and PR body.

The standard is **Conventional Commits 1.0.0** (https://www.conventionalcommits.org/) layered
on the **git-commit canon** (Tim Pope's note and the Pro Git guidance: a concise imperative
subject, a blank line, then a body that explains why). The optional linter is **commitlint**.
The exemplar corpus is the convention's own published examples and the canonical git
commit-message guidance. This register is the commit arm of the authoring charter
(`~/.claude/docs/authoring-charter.md`).

## What the standard asks for

- Structure the subject as `type(scope): description`. The type is one of `feat`, `fix`,
  `docs`, `refactor`, `test`, `build`, `ci`, `perf`, `chore`, or `style`. The scope is optional
  and names the affected area. The description is imperative and lowercase, with no trailing
  period.
- Keep the subject short, the canonical target being 50 characters or fewer.
- `feat` is a new feature; `fix` is a bug fix. Other types do not affect the version.
- Separate the subject from the body with a blank line. Wrap the body at about 72 characters.
- The body explains what changed and why, not how. The diff already shows how. State the
  motivating fact or fragility, not a narrative of the session.
- Mark a breaking change with a `!` after the type or scope, or a `BREAKING CHANGE:` footer, or
  both. The footer describes what breaks and what a consumer must do.
- Footers hold trailers (the co-author trailer, an issue reference) after a blank line, one per
  line.
- Claim only what the diff and the session evidence. A test plan you did not run, an issue
  number that does not exist, or a motivation the change does not show misleads the future
  debugger who trusts the log. If you did not run it or see it, do not write it.

## Exemplars

Each message is a Conventional Commits message in the git canon. The one-line note says which
part of the standard it shows.

A feature with a scope, body explaining the why (the standard's `feat` with a motivating
reason):

```
feat(auth): add rate limit to the magic-link endpoint

Cap link requests at five per email per hour. Without a cap, a single
address could be used to flood a mailbox or to probe for valid accounts,
since the endpoint answered the same way for any address.
```

A bug fix, the observed failure stated as fact (the standard's `fix` with the prior
fragility):

```
fix(parser): handle a trailing comma in the date list

The list parser dropped the final entry whenever the input ended with a
comma, because the split produced an empty trailing field it then failed
to skip. Skip empty fields before parsing.
```

A docs-only change, no version effect (the `docs` type for documentation work):

```
docs(readme): document the --max-instances flag

Add the flag, its default of 100, and the queueing behavior past the
limit to the configuration table. The flag shipped two releases ago but
was never written up.
```

A refactor that preserves behavior, scope fenced (the `refactor` type, behavior invariant
stated):

```
refactor(render): extract the frontmatter split into one helper

Move the duplicated split-and-parse logic from three call sites into
parseFrontmatter. No behavior change; the helper returns the same shape
the inline code did.
```

A breaking change with the `!` marker and the footer (the standard's breaking-change form,
with a co-author trailer in the footer slot):

```
feat(config)!: require an explicit publish branch

The config no longer defaults the publish branch to main. A site must
set publishBranch, so a misconfigured deploy fails at build time instead
of writing to the wrong branch silently.

BREAKING CHANGE: publishBranch is now required in cairn.config. Add it
to your config before upgrading; there is no default.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
```

## The docs-register measures

The docs-register profile resolves by path, against a repo's declared `include` and
`exclude` globs, and a commit message or a PR body is never a path on disk that profile
resolution can match. `tellgrader` never reports `hinged_pair_share` or
`short_sentence_share` for one, so this section records the measures' existence and this
register's exemption from them rather than a practice to follow.

The definitions, for a reader who reaches this file from the docs-register measures
section in a sibling register, live in
`~/.claude/skills/writing-voice/evals/tellgrader/MEASURES.md`.
They are report-only everywhere they do apply, carry no band, and gate nothing, and the
hinged-pair definition is unsettled; no number in that file is a threshold.

## Off-voice contrast

The same change in the register this file exists to prevent (no type prefix, past tense,
process narration, the diff restated):

```
Refactored the rendering code for better maintainability

In this commit, I noticed that the frontmatter splitting logic was
duplicated, so I went ahead and extracted it into a reusable helper. I
also cleaned things up a bit. This should make future changes easier!
```
