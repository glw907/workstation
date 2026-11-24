# Tidying

A tidy of code the task touches, such as a rename, an extracted function, or removed dead code, goes in its own
commit and changes no behavior (Beck, *Tidy First?*, <https://www.oreilly.com/library/view/tidy-first/9781098151232>).
A refactor larger than a tidy never rides a feature task. It goes to the backlog through `standards:log-issue` as
a task that changes no behavior, and the item names the failing check or the review finding that calls for it.
