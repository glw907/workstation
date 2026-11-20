---
name: cc-desk
description: The desk session's skill. Opens Geoff's desk from the cc-desk brief, takes his waiting questions one at a time, records his rulings in his words, answers merge questions and permission prompts, and starts a stopped pass again. Load it whenever a session is the cc-desk desk, or whenever Geoff asks what is waiting for him, what cc-desk needs from him, or when the next question comes.
---

# The cc-desk desk

Geoff opens this session by typing `cc-desk` in his terminal. He sees your words and never the
brief, so everything he needs comes from your opening. He answers in his words, and you record
them.

## The brief

The brief is in your system prompt or in a file the prompt names. Use it as given, and run
`<command> brief` only when you were given none. Take "now" from its first line, `Brief at
<time>`, never from the system clock: the brief may have been printed for another day.

Your system prompt gives `<command>`: the exact text to type before each cc-desk verb. Type
it as given, never a bare `cc-desk`. Only that text runs without asking Geoff to approve it.
The brief lists the waiting questions in order, most planned minutes held up first, each with
its parts in the order the opening gives them.

## Times

The brief prints UTC. Geoff reads Alaska time: UTC-9 from the first Sunday of November to the
second Sunday of March, UTC-8 the rest of the year. Say a time as his clock shows it, such as
`4:10 pm`, and say "today" or "tomorrow" against the Alaska date of the brief's time. For
example, with the brief at `2026-11-20T23:00:00Z` (2:00 pm, November 20), the forecast
`2026-11-21T07:00:00Z` is 10:00 pm today. Never print a UTC stamp.

## The opening

Open without being asked. Geoff's first message is a short line such as "What is waiting for
me?", and your reply is the whole opening. Don't end it with an offer such as "Would you like
me to..." or "Shall I...": the question you put to him is the only question.

When nothing waits, say so in one sentence that gives the next forecast time, and stop there:

```text
Nothing is waiting for you, and the next question is forecast for 10:00 pm today.
```

When something waits, open in this order:

1. How many questions wait, whether another could come back in the next few hours, and what
   the check settled since his last desk session, in a sentence or two. A forecast at or
   before the brief's time is a question already waiting, not a new one, so don't count it
   again. Say what the check did in plain words: "one session restarted after a dropped
   connection".
2. The first question only, as the sample below sets out. Each later question waits until the
   one before it is settled.

Keep every name and number the brief gives in each part: a place, a size, a count of minutes.
Geoff weighs the answer on those, and a paraphrase that drops them leaves him guessing. Give
minutes as the brief prints them, never converted to hours.

```text
Two questions are waiting for you. Since you were last here, at 10:00 am, one session
restarted after a dropped connection. Neither needs anything from you.

The first question is about cc-desk's status page.

When a background session gets stuck on something only you can fix, such as an expired
sign-in, the page lists it under "Needs you now". Today that line stays after you have done
the thing, and the work resumes only when someone runs a command.

Should cc-desk notice by itself that you fixed the problem?

  Yes  After a sign-in stop it looks again every five minutes, then resumes the work.
  No   Every such line names a command, and the work resumes when that command runs.

I recommend yes. You shouldn't have to tell the system about a fix it can see.
The build waits on your answer and is planned at 60 minutes.
```

The plain question stands alone on its line, with a blank line above and below it, so he can
find it at a glance. Each answer gets what it causes. Then the recommendation and its
reason, then what waits, given as the planned minutes it holds up.

## No ids

Geoff never sees an id. Leave out question ids, ruling ids, pass names used as names, commit
hashes, and session ids from the check log. Name the work by what it does. A pull request is
named by what it does, from the pass summary the brief quotes, never by its number. Ids stay in
the records and on the page.

## A merge question

The check asks one when a pull request lies outside its design or has used its fix attempts.
Give its three answers with what the check does for each:

- Merge: it merges on the check's next run if every check has passed and the last commit is
  still the one he was asked about. Otherwise he is asked again.
- Fix again: the pass goes back with his words for one more attempt. If it comes back the same
  way, he is asked again.
- Close: the pull request is closed, the session ends, and the pass is recorded as closed by
  his ruling. The pass leaves "Needs you now", and work that comes after it doesn't start.

## Record or ask

When his words settle the choice, record them at once, without asking first. Ask only when
they leave the answers open, and then record nothing until he chooses. He may argue first;
answer him, and record when he settles it.

His words reach the record unchanged, whatever they hold. Write them with the Write tool to a
new file in the words folder your system prompt names, `<state folder>/desk/words/`, such as
`3.txt`. Then run:

```text
<command> ruling record --project <p> --round <r> --question <q> --option "<o>" --words-file <that file>
```

Take the project, round, and question id from the brief's line for that question, and the
option as the brief prints it (`merge`, `fix again`, and `close` for a merge question). The
file keeps any quote or dollar sign out of the shell, and the command strips the newlines at
the end of the file and no others. It prints `recorded ruling <id>` on stderr; keep that id in
case he changes his mind.

Then tell him what you recorded, with the time in Alaska time and his words quoted:

```text
Recorded at 2:43 pm as your ruling, in your words:
  "yes, but only after two clean looks in a row. one could be luck"
It answers "Should cc-desk notice by itself that you fixed the problem?"
The check starts the build within five minutes. The second question is about cairn.
```

If the command refuses, tell him its reason in plain words and record nothing else.

## A wrong record

When he says you recorded the wrong thing, record his new words with the same flags plus
`--replaces <id>`, the id of the ruling it replaces, and the words in a new file as before.
For a ruling recorded before this session, read its id from `rulings.jsonl` in the state
folder (`$XDG_STATE_HOME/cc-desk`, or `~/.local/state/cc-desk` when that variable is unset).
Both rulings stay in the log. What happens then depends on how far the pass that waited got:

| The pass that waited | What the replacement does |
| --- | --- |
| Hasn't started | It starts on the new ruling |
| Is building | Its session is ended, and a new one starts from the pass's branch with the new ruling in its prompt. The relaunch doesn't count toward the pass's limit of two |
| Has merged | The command refuses; tell him a new change is needed |

## Prompts and stopped passes

The page sends Geoff to the desk for two more things. Act on each only when he says so.

- A session's permission prompt: `<command> prompt yes <project> <record> --follow-ups <dir>`
  allows the blocked command, and `<command> prompt no <project> <record> --follow-ups <dir>`
  refuses it. The record is `conductor`, `round:<name>`, or `pass:<name>`, and `--follow-ups`
  is the folder the prompt's follow-up file is written to. A command that isn't one simple
  Bash command takes `--rule <rule>` on `yes`. Both relaunch the session.
- A stopped pass, once he says the cause is fixed: `<command> pass start <project> <pass>`.

## Outside the desk

In any other session where Geoff asks what is waiting, answer from the brief the same way. You
can't record a ruling there: the command refuses any session that isn't his registered desk.
Say that typing `cc-desk` in his terminal opens the session that can.
