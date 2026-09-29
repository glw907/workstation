# Register: SvelteKit/web developer documentation

The reader is a competent web developer adopting or operating the system, who has not read the
code. Applies to the developer-facing docs in the web repos (the SvelteKit sites and the
non-published docs of cairn-cms): READMEs, guides, reference pages, explanation pages, and
design notes. A published cairn-cms page, and cairn.pub's own prose, does not take its brief
from this file: it follows the developer brief in cairn-cms `docs/internal/docs-register.md`,
which supplements the same Google guide with the cairn docs voice. Code comments have their own
standard in the ts-conventions and svelte-conventions skills; this register covers prose at the
document level.

The standard is the **Google Developer Documentation Style Guide**
(https://developers.google.com/style), the same standard as the Go-prose register; this file
carries the web dialect and its exemplars. The linter is the **Vale Google package**, selected
per glob in each repo's `.vale.ini`. The exemplar corpus is **Google's own developer
documentation**. This register is the web-prose arm of the authoring charter
(`~/.claude/docs/authoring-charter.md`).

The `tellgrader` cadence measures are report-only and defined in
`~/.claude/skills/writing-voice/evals/tellgrader/MEASURES.md`.

## What the standard asks for

- Second person and the imperative for instructions. Use "you" for the reader; start a step
  with a verb. Reserve "we" for the rare case where the writer and reader act together.
- Present tense and active voice throughout. "SvelteKit renders the route", not "the route
  will be rendered".
- Example first for a how-to. Show the code, then say in plain terms what happens when the
  reader runs it.
- One idea per sentence, short sentences. Put a reason in a brief parenthetical rather than a
  separate justification sentence.
- Lead with the outcome. State what a feature does before its internals.
- Plain words, no filler. Cut "simply", "easily", "just", and marketing adjectives. Name the
  concrete case (the marketing page, the login form), not "various scenarios".
- Write only what you know to be true of the system. A confident specific the source material
  does not state (a config option, a default, a flag, a behavior) is an invention the reader
  will act on. Where a detail is unknown, leave it out; fluency in this register makes
  invented specifics sound authoritative, which makes them worse, not better.

## Exemplars

Each passage is written in the Google developer-documentation style, in a web/JavaScript
context. The one-line note says which trait of the standard it shows.

Example first, then the consequence in plain terms (the standard's task pattern: show, then
explain):

```
To read a query parameter, call the get method on the request URL's searchParams. The
following handler returns the value of the page parameter, or 1 if the parameter is absent.
When a request arrives without a page parameter, the handler uses the default.
```

Concept explanation, active voice, outcome first (the standard's "lead with what it does"
rule, reason in a parenthetical):

```
Server-side rendering generates the HTML for a page on each request. The browser receives a
complete page, so the content is available before JavaScript loads (which improves the
experience on a slow connection and for search-engine crawlers).
```

Precise action verbs for a setup procedure, second person, one action per numbered step (the
standard's UI- and command-verb guidance, and its rule that a sequence of steps is a numbered
list):

```
To add the integration, install the package and register the plugin:

1. In your terminal, run npm install.
2. In vite.config.js, import the plugin.
3. Add the plugin to the plugins array.
```

Reference prose for an option, declarative, the default and the edge case stated plainly (the
standard's reference register):

```
The prerender option controls whether SvelteKit renders the page at build time. The default is
false. When you set it to true, SvelteKit generates the HTML during the build and serves the
static file, so the page cannot read per-request data.
```

A note that states a constraint and its consequence directly (the standard's note style):

```
Load functions run on the server and in the browser. Do not access private environment
variables or a database connection in a shared load function, because that code also runs on
the client. Put server-only data access in a +page.server.js file instead.
```

## Off-voice contrast

The same content in the register this file exists to prevent (marketing tone, filler,
future tense, vague abstraction):

```
SvelteKit takes a unique, modern approach to rendering that gives you the best of both worlds.
With its powerful and flexible options, you can effortlessly optimize your app for any use
case. Your pages will load lightning-fast, and you'll be able to focus on what really matters:
building an amazing experience for your users.
```
