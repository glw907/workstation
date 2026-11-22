# Settled design: notes search

The owner said: "I want to find a note without scrolling through the whole list."

Decided in conversation, and not open:

- A new command, `bin/notes search <word>`, prints every note that contains the word, oldest first.
- The match ignores case. The word is plain text, never a pattern.
- No match prints nothing and exits 1. A missing word exits 2 with the usage line, which names the new command.
- The work changes `bin/notes` and `tests/run.sh`, and the README names the new command.
- The work is one task and ends in one pull request.
- It is done when the search works as above, the gate passes, and `grep -c notes README.md` prints 1 or more.
