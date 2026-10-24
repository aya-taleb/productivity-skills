---
name: tasks
description: Keeps one plain tasks.md for every business you run, each task tagged by business, with real due dates. Use it whenever the user wants to capture, check or finish a to-do, even in passing. Triggers include "add a task", "remind me to", "put this on my list", "brain dump", "what's on my plate", "what's due this week for the lunch business", "what am I waiting on", "mark the invoice done", "I finished X", "push that to next week", "clean up my tasks". No app, account or dashboard needed. The file lives in ~/.founder/tasks.md and other skills (daily-plan, weekly-review, meeting-actions) read it.
---

> Changed by Aya Taleb from Anthropic's task-management (Apache 2.0): one tasks.md under ~/.founder/, tagged by business, with due dates and a small tool, no dashboard or external app.

# Tasks

One file holds every task for every business. A founder with three ventures and classes
loses things when tasks live in five apps. One file, tagged by business, fixes that and
stays readable by hand.

## Where things live

- Tasks file: `tasks.md` in the founder folder. The tool finds it: `$FOUNDER_HOME`, then
  `./founder/` if it already holds productivity files, then `~/.founder/`.
- Tool: `scripts/tasks.py` in this skill's folder. Standard library Python, no setup.
  Below, `tasks.py` means `python3 <this skill's folder>/scripts/tasks.py`. Run the tool from
  the user's current folder, calling it by its full path. Don't `cd` into the skill folder
  first, because the tool looks for a project `./founder/` relative to where it runs.
- Businesses: the founder-context files (`<founder folder>/businesses/<slug>.md`, the
  `active` file, or a project-local `founder/context.md`).

Start every run with `tasks.py context`. It prints the folder, the business
slugs it found and any tags in tasks.md that match no business. Use the tool for every change
so the file keeps one format. Edit by hand only if Python is not available, following the
format below.

## The format

```markdown
# Tasks

## Active
- [ ] **Send the menu to the print shop** #corner-lunch due:2026-10-26 added:2026-10-23 - ask about the matte option
  - sub-bullets stay with the task when it moves

## Waiting on
- [ ] **Logo files from Sam** #tidepool since:2026-10-20 added:2026-10-20

## Someday

## Done
- [x] ~~Renew the food permit~~ #corner-lunch done:2026-10-22
```

Why each part: the bold title is what people scan. The `#tag` lets every other skill split work
by business. `due:` dates are absolute so a task written on Friday still means the right day
next month. `added:` and `since:` let reviews spot tasks that have sat too long.

## Tag every task with a business

- Use the slugs from founder-context. A task with no tag is invisible to per-business reviews.
- If the business is clear from the words ("the lunch menu"), from related tasks already in the
  file (a person or project that only shows up under one tag), or from the brain dump's context,
  tag it and say which tag you used. Add the task now; the user can fix a tag in a second.
- If it could truly be two businesses, add it with your best tag and ask in the readback. Don't
  hold a task back waiting for an answer; a task that isn't written down gets lost. If it fits
  none, use a tag the user names, such as
  `#school` or `#personal`. Never make up a business that isn't in founder-context.
- If there is no founder-context at all, ask the user for short names of their businesses and
  suggest running founder-context to set them up properly. Don't block on it: use the names
  they give you as tags.

## Capture

- Brain dumps: split them into one task per action. Start each title with a verb. Keep the
  user's words where you can; they recognize their own phrasing faster.
- Add each task with the tool:
  `tasks.py add "Call the print shop" --biz corner-lunch --due monday --note "matte?"`
- Dates: pass what the user said (`today`, `tomorrow`, `friday`, `+2w`, `2026-11-03`) and let
  the tool turn it into a date. Only set a due date the user gave or clearly implied. "Soon" or
  "at some point" gets no date. A made-up deadline is worse than none, because it trains the user
  to ignore dates.
- Things someone else owes the user go in Waiting on (`--section waiting`). Ideas with no
  commitment go in Someday.
- After adding, read back a short list: title, tag, due date. That is the user's chance to fix a
  wrong tag or date.

## Check and report

- When one message asks a question and asks for changes ("what's due, and mark X done"),
  answer the question from the file as it was, then make the changes and confirm them.
- "What's on my plate": `list`, grouped by business. Lead with overdue, then due this week, then
  waiting items older than a week. Keep it short; a full dump of 40 tasks helps no one.
- One business: `list --biz <slug>`. This week: `list --due-by +7d`. Overdue: `list --overdue`.
- Use `list --json` when another step needs to count or sort.

## Finish, change, clean up

- Done: `tasks.py done "invoice"` (a piece of the title or the id from `list`).
  If more than one task matches, the tool lists them; ask which one.
- Change: `edit <match> --due friday`, `--section someday`, `--biz <slug>`, `--note "..."`.
- Weekly cleanup: `rollover` moves Done items older than 7 days to `tasks-archive.md` and lists
  overdue and 30-day-old tasks. For each overdue task ask: new date, Someday, or drop? Don't
  push dates forward on your own. Quietly moving deadlines hides the slip the user needs to see.
- "Just push everything to next week": don't run the edits yet. Show the overdue list with how
  late each one is, and for each one offer the three choices: a new date, Someday, or drop.
  Make it easy to answer in one line ("1 Monday, 2 drop, 3 Someday", or "push all"). Then apply
  what they say. One question is cheap; a silently moved deadline hides the slip.

## Tasks found elsewhere

When a conversation or document shows a commitment ("I'll send that over"), offer to add it. Ask
first, unless the user asked you to capture tasks from it. meeting-actions does this for meetings.

## What this skill does not do

- No syncing with Todoist, Asana, Notion or any app, and no dashboard. The plain file is the point.
  If asked, say so in one line and don't offer to set up a connector; offer what the file can do.
- No reminders or notifications. daily-plan and weekly-review are where tasks surface.

## Reply style

Keep the reply short and plain. Show each list once; after a change, say what changed instead
of repeating the list. Report what the user asked about plus anything overdue. Sentences under
25 words, light formatting (a few bullets or one small table, little bold), no em or en dashes.
Don't guess at consequences ("the domain may lapse") that the files don't show. Finish with the
one-line next step.

## Handoff

End every reply with one short line on what to run next, when it fits (for example "Run
daily-plan to fit these into today."). If `context` showed tags that match no business, mention
them once.

- Reads: founder-context businesses, tasks.md.
- Writes: tasks.md, tasks-archive.md (rollover only).
- Next: daily-plan to pick today's focus, or weekly-review at the end of the week.
