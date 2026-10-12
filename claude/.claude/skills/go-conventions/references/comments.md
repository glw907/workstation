# Comment placement and shape

Reference for the `go-conventions` skill's Comments section, which holds the write-time gate and
the unexported-symbol default. Comments follow **Go Doc Comments** (https://go.dev/doc/comment);
the exemplar is the standard library.

## Decision rubric

Apply before writing any comment:

```
1. Unexported symbol?
   YES → Step 2.   NO → Doc comment required (Step 3).

2. Does the unexported symbol have unobvious behavior the name
   doesn't convey?
   YES → Short doc.   NO → No comment.

3. Is the public API contract fully implied by name + signature?
   YES → One sentence. Period.
   NO  → One sentence + what the caller needs to know. No
         implementation detail.

4. Concurrency hazard, surprising default, platform-specific
   behavior?
   YES → Add it.   NO → Stop.

5. Inside a function: does this block differ from what the name /
   control flow implies?
   YES → One-line why-comment.   NO → No comment.
```

A comment that restates the code, describes what the name already
conveys, or explains an internal algorithm to a caller has failed
this rubric.

## Doc comment shape

- **Doc comments end with a period.** Always.
- **Name-first.** First word is the identifier name. Type docs may
  use "A" / "An" as article.
- **Boolean returns:** use "reports whether": `// HasPrefix reports
  whether s begins with prefix.`
- **Length proportional to non-obvious behavior.** 1 sentence is
  the floor; expand only when there is a contract, hazard, or
  surprising default to communicate. Never expand to fill space.
- **No first person.** Third-person declarative for godoc. "We"
  permitted only at package-doc level (project voice). No "you".
- **No hedging.** "maybe", "perhaps", "should probably", "might",
  "could" are forbidden in doc comments.

## Comment review

Review comments against Go Doc Comments and the standard library, not a
fixed checklist. Read the doc comments next to the same kind of code in
the stdlib and ask whether yours match their density, shape, and candor.
The recurring failure mode is the paraphrase comment that restates the
code; run the write-time gate's mechanical test on every in-function
comment before saving. `/simplify` runs a quality lens over the diff and
flags comments that paraphrase the code or restate a type.
