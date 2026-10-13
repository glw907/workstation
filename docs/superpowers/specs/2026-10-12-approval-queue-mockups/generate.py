"""Round 5 desk mock-ups: stock DaisyUI 5, hierarchy by type and spacing, quiet variants for secondary controls."""

import pathlib
import sys

OUT = pathlib.Path(sys.argv[1])
OUT.mkdir(parents=True, exist_ok=True)

ICON = {
    "alert": '<path d="M12 3 2 20h20L12 3zM12 10v4M12 17h.01"/>',
    "info": '<circle cx="12" cy="12" r="9"/><path d="M12 11v5M12 8h.01"/>',
    "check": '<path d="m5 12 5 5 9-10"/>',
    "chev": '<path d="m9 6 6 6-6 6"/>',
    "undo": '<path d="M9 14 4 9l5-5M4 9h11a5 5 0 0 1 0 10h-3"/>',
    "pencil": '<path d="m4 20 4-1 11-11-3-3L5 16l-1 4zM14 6l3 3"/>',
}


def icon(name, cls="size-5"):
    return (f'<svg class="{cls} shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICON[name]}</svg>')


PAGES = [("pr-clean.html", "PR, all clear"), ("pr-problem.html", "PR with a problem"), ("triage.html", "Triage")]
QUEUE = [
    ("pr-clean.html", "PR · workstation #40", "4m", "Every PR a session opens will now come to you for approval."),
    ("pr-problem.html", "PR · workstation #41", "2m", "Illustration: the same change with a failing check."),
    ("triage.html", "Triage · drafter Pass 0", "1h", "One follow-up needs doing before the next docs run."),
]


def shell(current, tab, body, bar):
    tabs = "".join(f'<a role="tab" class="tab{" tab-active" if f == current else ""}" href="./{f}">{label}</a>'
                   for f, label in PAGES)
    menu = "".join(
        f'<li><a class="{"menu-active bg-base-300 text-base-content" if href == current else ""}" href="./{href}"><div class="w-full">'
        f'<div class="flex justify-between gap-2 text-xs text-(--color-muted)"><span>{meta}</span><span>{age}</span></div>'
        f'<div class="mt-0.5 leading-snug">{title}</div></div></a></li>'
        for href, meta, age, title in QUEUE)
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{tab} · Design &amp; PR Approvals</title>
<link href="../_app/immutable/assets/0.Bp3r8Oyv.css" rel="stylesheet">
<link href="./mock.css" rel="stylesheet">
</head>
<body class="font-body">
<div class="drawer lg:drawer-open">
  <input id="q" type="checkbox" class="drawer-toggle">
  <div class="drawer-content flex min-h-dvh flex-col">
    <main class="flex-1 px-5 pt-4 pb-8 lg:px-12">
      <div class="max-w-3xl">
        <div role="tablist" class="tabs tabs-border tabs-sm mb-5 [&>.tab:not(.tab-active)]:text-(--color-muted)">{tabs}</div>
        {body}
      </div>
    </main>
    <div class="sticky bottom-0 z-10 bg-linear-to-t from-base-100 from-60% to-transparent px-5 pt-8 pb-4 lg:px-12">
      <div class="flex max-w-3xl flex-wrap items-center gap-x-4 gap-y-3 rounded-box border border-base-300 bg-base-100 px-5 py-3.5 shadow-[0_8px_28px_-6px_rgb(0_0_0/0.22),0_2px_6px_-2px_rgb(0_0_0/0.10)]">{bar}</div>
    </div>
  </div>
  <div class="drawer-side">
    <label for="q" class="drawer-overlay" aria-label="Close the queue"></label>
    <nav class="flex min-h-full w-72 flex-col bg-base-200" aria-label="Queue">
      <div class="px-4 pt-5 pb-2">
        <p class="font-semibold">Design &amp; PR Approvals</p>
        <p class="text-sm text-(--color-muted)">3 waiting</p>
      </div>
      <ul class="menu w-full gap-1 p-2 text-sm">{menu}</ul>
      <div class="grow"></div>
      <p class="p-4 text-xs text-(--color-muted)">Mock-up: choices, tabs, and disclosures work; Approve, Submit, and Send back do nothing.</p>
    </nav>
  </div>
</div>
</body></html>"""


def head(meta, headline, lede, extra=""):
    return (f'<p class="mb-2 text-xs tracking-wide text-(--color-muted)">{meta}</p>'
            f'<div class="rounded-box border-s-4 border-primary bg-base-200 py-6 ps-4 pe-4 lg:-ms-7 lg:ps-6 lg:pe-6">'
            f'<h1 class="desk-title text-[1.75rem] leading-tight text-balance">{headline}</h1>'
            f'<p class="mt-3 max-w-[70ch] text-[1.05rem] leading-relaxed text-pretty opacity-85">{lede}</p>{extra}</div>')


def label(text):
    return f'<h2 class="mb-1 text-[0.7rem] font-semibold uppercase tracking-[0.08em] text-(--color-muted)">{text}</h2>'


def h_act(text, note=""):
    note = f'<span class="text-sm font-normal text-(--color-muted)">{note}</span>' if note else ""
    return f'<h2 class="mb-3 flex items-baseline gap-3 text-base font-semibold">{text}{note}</h2>'


def h_sub(text):
    return f'<h3 class="mb-1.5 text-sm font-semibold">{text}</h3>'


def disclosures(rows, quiet=False):
    name_cls = "shrink-0 text-sm font-medium opacity-80" if quiet else "shrink-0 text-[0.95rem] font-medium"
    sum_cls = "text-xs text-(--color-muted)" if quiet else "text-sm text-(--color-muted)"
    pad = "py-1.5" if quiet else "py-2"
    return "".join(
        f'<details class="group collapse rounded-none border-b border-base-content/10">'
        f'<summary class="collapse-title flex min-h-0 items-baseline gap-x-2 px-0 max-sm:flex-wrap {pad}">'
        f'<span class="self-center transition-transform group-open:rotate-90">{icon("chev", "size-4 text-(--color-muted)")}</span>'
        f'<span class="{name_cls}">{name}</span>'
        f'<span class="ms-1 text-pretty max-sm:ms-6 max-sm:basis-full {sum_cls}">{summary}</span></summary>'
        f'<div class="collapse-content max-w-[70ch] ps-6 pe-0 text-sm leading-relaxed text-pretty opacity-90">{body}</div></details>'
        for name, summary, body in rows)


META = "workstation #{n} · desk-hook &rarr; main · <a class=\"link\">GitHub</a>"
HEADLINE = "Every PR a session opens will now come to you for approval, and approving one will merge it."
LEDE = "Small fixes were skipping your approval, and Claude Code was blocking merges you had already approved. This fixes both."


def panel(steps):
    def col(title, items, kind):
        mark = (lambda i: "&bull;") if kind == "list-disc" else (lambda i: f"{i}.")
        lis = "".join(f'<li class="flex gap-1"><span class="w-3.5 shrink-0 tabular-nums text-(--color-muted)">{mark(i)}</span>'
                      f'<span class="text-pretty opacity-80">{t}</span></li>' for i, t in enumerate(items, 1))
        return (f'<div><h3 class="mb-2.5 text-[0.95rem] font-semibold">{title}</h3>'
                f'<ol class="space-y-2">{lis}</ol></div>')
    return (
        '<div class="mt-6 border-t border-base-content/10 pt-5 text-[0.95rem] leading-snug">'
        '<div class="grid gap-6 sm:grid-cols-2">'
        + col("What changes", ["Every PR a session opens comes here. Before, only full planned passes sent theirs.",
                               "A merge you approved goes through. Before, Claude Code blocked it, as with PR #38."], "list-disc")
        + col("If you approve", steps, "list-decimal")
        + '</div>'
        f'<p class="mt-5 flex max-w-[70ch] items-start gap-2 text-sm text-(--color-muted)">{icon("info", "size-4 mt-px")}'
        '<span>The merge permission checks the command, not your approval; the merge guard keeps a merge from skipping your approval.</span></p>'
        '</div>')


DETAILS = [
    ("The reminder", "Fires whenever a session opens a PR.",
     "<p>A new hook, <code>claude-desk-reminder</code>, runs after each shell command. When the command opened a PR, it tells the session to send it here for your approval and wait. It stays quiet for an executor whose conductor hands the PR over, and for a small pass that merges itself.</p>"),
    ("The merge permission", "Only the exact commit you approved can merge.",
     "<p>A permission rule allows <code>gh pr merge * --match-head-commit *</code>. GitHub refuses the merge if the branch moved after your approval.</p>"),
    ("Testing", "A new test covers the reminder; the full check passed.",
     "<p>Five cases: a PR opened, one opened inside a longer command, a different <code>gh</code> command, a failed open, and unreadable input.</p>"),
]


def evidence(checks):
    return [("Checks", checks, "<p>Today&rsquo;s checks list.</p>"),
            ("Review", "None run.", "<p>The review&rsquo;s verdict and notes, when one runs.</p>"),
            ("Technical notes", "What landed and the gate.", "<p>The PR body's agent-facing sections.</p>"),
            ("Files", "4 files, +127 &minus;1.", "<p>Today&rsquo;s file list and diffs.</p>")]


def details_block(checks):
    return ('<div class="mt-10">' + label("Details") + disclosures(DETAILS) + '</div>'
            '<div class="mt-8">' + label("Evidence") + disclosures(evidence(checks), quiet=True) + '</div>')


STEPS = ["The PR merges.", "This machine&rsquo;s settings rebuild.", "Sessions follow it on their next command."]
def bar_status(dot, title, sub):
    return (f'<div class="mr-auto flex min-w-0 items-start gap-3"><span class="status {"bg-base-content/50" if dot == "neutral" else "status-" + dot} mt-2"></span>'
            f'<div class="min-w-0"><p class="font-semibold leading-tight">{title}</p>'
            f'<p class="mt-0.5 text-sm leading-snug text-(--color-muted)">{sub}</p></div></div>')


KEY = 'kbd kbd-xs border-current/25 bg-transparent text-current opacity-85'
SEND_BACK = f'<button class="btn btn-outline">{icon("undo", "size-4")}Send back<kbd class="{KEY}">R</kbd></button>'


def approve(disabled_tip=None):
    btn = (f'<button class="btn btn-primary"{" disabled" if disabled_tip else ""}>{icon("check", "size-4")}'
           f'Approve and merge<kbd class="{KEY}">A</kbd></button>')
    return f'<div class="tooltip tooltip-top" data-tip="{disabled_tip}">{btn}</div>' if disabled_tip else btn


BAR_OK = bar_status("success", "Ready to approve", "All 3 checks passed. Nothing to decide first.") + '<div class="ms-auto flex flex-wrap gap-3">' + SEND_BACK + approve() + '</div>'

clean = head(META.format(n=40), HEADLINE, LEDE, panel(STEPS)) + details_block("All 3 passed.")


TINT = {"error": "bg-error/7", "warning": "bg-warning/10"}


def decision(name, ic, color, title, source, text, options, checked=None):
    radios = "".join(
        f'<input class="join-item btn btn-sm checked:bg-base-content checked:text-base-100 checked:border-base-content" type="radio" name="{name}" aria-label="{o}"{" checked" if o == checked else ""}>'
        for o in options)
    done = f'<span class="badge badge-ghost badge-sm">{icon("check", "size-3")}Decided</span>' if checked else ""
    return (f'<div role="alert" class="alert alert-soft alert-{color} {TINT[color]} items-start">'
            f'{icon(ic, "size-5 mt-0.5")}'
            f'<div class="text-base-content"><div class="flex items-center gap-2"><h3 class="text-base font-semibold">{title}</h3>{done}</div>'
            f'<p class="mt-1 max-w-[70ch] text-[0.95rem] leading-relaxed text-pretty">{text} <span class="text-(--color-muted)">{source}.</span></p>'
            f'<div class="join mt-3 rounded-field border border-base-300 bg-base-100 max-sm:join-vertical">{radios}</div></div></div>')


problem = (head(META.format(n=41), HEADLINE, LEDE, panel(["The session rebuilds the settings."] + STEPS[:1] + STEPS[2:]))
           + '<div class="mt-8 space-y-3">' + h_act("Decide first", "1 of 2 left")
           + decision("q1", "alert", "error", "A check failed",
                      "Found automatically",
                      "This app&rsquo;s own tests failed on the latest commit, so the reminder may not work as described. The session didn&rsquo;t report it.",
                      ["Send back to fix it", "Approve anyway"])
           + decision("q2", "info", "warning", "A step must run before merging",
                      "From the session",
                      "The live settings have to be rebuilt from this PR, or sessions keep the old rules.",
                      ["The session runs it, then merges", "I&rsquo;ll run it myself"], checked="The session runs it, then merges")
           + '</div>'
           + details_block('1 of 3 failed.'))

BAR_PROBLEM = (bar_status("warning", "1 decision left", 'Decide <a class="link">A check failed</a> to unlock Approve.')
               + '<div class="ms-auto flex flex-wrap gap-3">' + SEND_BACK + approve("Decide the failed check first") + '</div>')

ROWS = [
    ("now", "Teach cairn&rsquo;s docs review page to read the new plan format.",
     "Plans now save as YAML; until this lands the review page shows no plan for a new page, and the next docs run depends on it.",
     "From workstation#36: <code>scripts/docs-review/embed.mjs</code> <code>planPathFor</code> reads only <code>&lt;slug&gt;.plan.md</code>, so it can't show a <code>.plan.yaml</code>. Your ruling, 2026-10-12: land before the next YAML chain run."),
    ("later", "Make the plan checker catch a note written after a title or heading.",
     "A note there silently cuts the title short, with the page link built from it. Not seen in a real plan yet.",
     "From drafter#1: <code>title</code> and <code>heading</code> are not prose fields, so <code>title: X # note</code> is cut at the comment with no finding."),
    ("later", "Flag a link that points only at &ldquo;#&rdquo;.",
     "It passes silently today, and it&rsquo;s rare.",
     "From drafter#1: a bare <code>#</code> link target passes silently."),
    ("later", "Check that each plan&rsquo;s page path points inside the repo.",
     "A path outside the repo sends the link warnings to the wrong place.",
     "From drafter#1: <code>page.path</code> is not validated as repo-relative."),
    ("later", "Replace a needless pattern match with a plain text search.",
     "Tidier code, no change in behavior.",
     "From drafter#1: <code>bracketRe</code> is a regexp for a literal <code>[</code>."),
    ("skip", "Skip the no-facts warning when a facts list is empty.",
     "Harmless as it is; an empty list is rare.",
     "From drafter#1: a <code>sentence</code> with <code>facts: []</code> still gets the warning."),
    ("skip", "Read the facts folder once per run, not once per plan.",
     "Only a speed-up, and runs have few plans.",
     "From drafter#1: <code>LoadFacts</code> re-reads the facts directory for each plan."),
    ("skip", "Move the end-to-end test&rsquo;s program path out of a shared variable.",
     "It&rsquo;s the standard Go test setup; nothing to gain.",
     "From drafter#1: <code>e2e</code> keeps the built binary path in a package global."),
]
GROUPS = [("now", "Do now", "bg-warning", ""), ("later", "Do later", "bg-base-content/40", ""), ("skip", "Don&rsquo;t do", "bg-base-content/20", "dim")]
CHOICES = [("now", "Do now", "checked:bg-warning/25"), ("later", "Do later", "checked:bg-base-300"), ("skip", "Don&rsquo;t do", "checked:bg-base-300")]


def triage_body():
    out = [head("Triage · drafter Pass 0 and workstation #36",
                "One follow-up needs doing before the next docs run.",
                "Pass 0&rsquo;s review found eight small gaps. The session proposes doing one now, four later, and skipping three. Change any call you disagree with.")]
    n = 0
    for key, name, dot, dim in GROUPS:
        rows = [r for r in ROWS if r[0] == key]
        out.append(f'<h2 class="mt-9 mb-0 flex items-center gap-2 text-base font-semibold">'
                   f'<span class="size-2 rounded-full {dot}"></span>{name}'
                   f'<span class="text-sm font-normal text-(--color-muted)">{len(rows)}</span></h2><ul class="list">')
        for disp, act, why, tech in rows:
            n += 1
            radios = "".join(
                f'<input class="join-item btn btn-xs btn-ghost font-normal checked:font-semibold checked:text-base-content checked:border-base-content/55 {cls}" '
                f'type="radio" name="r{n}" aria-label="{text}"{" checked" if k == disp else ""}>'
                for k, text, cls in CHOICES)
            out.append(
                f'<li class="list-row items-start px-0 py-3 after:border-base-content/10">'
                f'<div class="min-w-0 list-col-grow"><p class="max-w-[70ch] text-base font-semibold leading-snug text-pretty{" text-(--color-muted)" if dim else ""}">{act}</p>'
                f'<p class="mt-0.5 max-w-[70ch] text-[0.95rem] leading-relaxed text-pretty text-(--color-muted)">{why}</p>'
                f'<div class="mt-2 flex flex-wrap items-center gap-x-1 gap-y-2">'
                f'<div class="join rounded-field border border-base-300">{radios}</div>'
                f'<button class="btn btn-xs btn-ghost font-normal text-(--color-muted)">{icon("pencil", "size-3")}Note</button>'
                f'</div>'
                f'<details class="group mt-0"><summary class="flex w-fit cursor-pointer list-none items-center gap-1 py-1 text-xs text-(--color-muted) hover:text-base-content">'
                f'<span class="transition-transform group-open:rotate-90">{icon("chev", "size-3.5")}</span>Technical detail</summary>'
                f'<div class="mt-1 max-w-[70ch] text-xs leading-relaxed text-pretty opacity-90">{tech}</div></details></div>'
                f'</li>')
        out.append('</ul>')
    return "".join(out)


BAR_TRIAGE = (bar_status("neutral", "8 calls, none changed", "Submit sends your calls back to the session.")
              + f'<button class="btn btn-primary">{icon("check", "size-4")}Submit calls<kbd class="{KEY}">Ctrl</kbd><kbd class="{KEY}">Enter</kbd></button>')

(OUT / "pr-clean.html").write_text(shell("pr-clean.html", "Every PR a session opens…", clean, BAR_OK))
(OUT / "pr-problem.html").write_text(shell("pr-problem.html", "Every PR a session opens…", problem, BAR_PROBLEM))
(OUT / "triage.html").write_text(shell("triage.html", "One follow-up needs doing…", triage_body(), BAR_TRIAGE))
print("wrote", OUT)
