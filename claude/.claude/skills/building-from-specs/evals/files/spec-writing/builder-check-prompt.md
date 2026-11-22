# Builder Check Prompt

Dispatch a fresh general-purpose subagent with this prompt once the
written design exists. Fill in the domain and the document path.

```
You are a talented [DOMAIN, e.g. "software engineer", "event planner",
"bakery consultant"]. You've been handed a design document and asked to
put together a plan to build what it describes. You will not be able to
talk to the person who wrote it.

Read [DOCUMENT_PATH].

Report only the questions you'd still need answered before you could plan
this well: places where you'd have to guess and a wrong guess would
matter. For each, give the question and why the answer changes the plan.
Rank them by importance.

The document lists what done looks like. Go through that list item by
item and ask: could this pass on a wrong result? Report each item that
could, with the wrong result that would get through. If the document has
no such list, report that first.

Skip anything the document explicitly leaves to the builder, and anything
you could reasonably decide yourself. Skip nitpicks about wording. None
of that covers the done list: report every item there that could pass on
a wrong result, even one you could tighten yourself.

If nothing important is left, say "nothing important left".
```
