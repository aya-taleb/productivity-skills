---
name: weekly-review
description: One weekly review across every business you run, plus school or anything else you track. Looks back (wins, numbers, what slipped, last week's focus) and sets one focus per business and one overall for next week, then saves it to weekly/YYYY-Www.md. Use it at the end or start of a week, or whenever the user says "weekly review", "let's do my week", "how did this week go", "plan next week", "what should I focus on next week", "Friday wrap-up", "Sunday reset", "I feel scattered across my projects", "what slipped this week". Reads tasks.md, decisions.md and last week's review, so run it even if the user only gives a few numbers.
---

# Weekly review

The anchor of this repo. Someone running several small ventures while studying needs one place,
once a week, to see all of them side by side and pick what matters. One focus per business
keeps each venture moving. One overall focus says which venture gets the best hours.

## Find the files

Run `python3 <this skill's folder>/../tasks/scripts/tasks.py context`. Below, `tasks.py` means
`python3 <this skill's folder>/../tasks/scripts/tasks.py`, run from the user's current folder
(don't `cd` into the skill folder; the tool looks for `./founder/` where it runs). It prints the
founder
folder (`$FOUNDER_HOME`, a project `./founder/` that already has these files, or
`~/.founder/`), the businesses from founder-context and the tasks file. If Python is
not there, look in `./founder/` and then `~/.founder/` yourself.

Read, in this order:
1. Businesses: `businesses/<slug>.md` (name, stage, goals). This is the list of rows in the review.
2. Last week's review: `weekly/<last ISO week>.md`. Its focus lines are what you check first.
3. Tasks: `tasks.py list --done-since <Monday of this week>`, `tasks.py list --overdue`, and
   `tasks.py list --due-by +7d`. Use `--json` if you want to count.
4. Decisions: `decisions.md`, for any entry whose revisit date is in this week or earlier.

Work out dates with a command (`date +%G-W%V`, or Python), not in your head. The file name is
the ISO week, such as `weekly/2026-W43.md`. A wrong week number breaks next week's review.

## If something is missing

- No founder-context: ask once for the businesses (short name and stage for each) and say that
  running the founder-context skill will save them for next time. Never make up a business or
  its goals.
- No last week's review: say this is the first one and skip the "did last week's focus happen"
  check.
- No tasks.md or an empty one: say so. Ask what got done, don't guess.
- Batch every question into one message. A review that asks five times does not get finished.

## Numbers

Use only numbers the user gives or that are written in the files. Copy them exactly. Basic math
on those numbers is fine if you show it ("241, up 29 from 212"). When a
business has no number this week, write `{{signups this week}}` or similar and ask for it once.
Never estimate, round up or fill a trend from memory. A review with a made-up number is worse
than one with a blank, because next week builds on it.

## The review

For each business:
- **Wins**: done tasks this week (from Done), plus anything the user says.
- **Numbers**: the user's numbers, or placeholders.
- **Slipped**: tasks whose due date is before today, and last week's focus if it did not happen.
  Something due today or later has not slipped yet. Name slips plainly. Ask why only if the
  user wants to talk about it; the point is to see the slip, not to judge it.
- **Next week's focus**: one line, one outcome that can be checked next Friday.
  "Ship the paywall test to 50 users" beats "work on growth". Pick it from the business goals,
  the overdue list and what the numbers say. A focus is a step forward, not catch-up admin;
  overdue chores go under "Carry or drop".

Then overall:
- **Overall focus**: which one business gets the first and best hours next week, and why in one
  sentence. Say which business can idle at maintenance level. Trying to push all of them at once
  is how all of them stall.

Always commit to your best pick for every focus line, overall included, and write it in the file.
Mark it `(suggested)` until the user agrees, then remove the mark. A blank focus line means next
week's review has nothing to check.
- **Revisit**: decisions due for a second look, with the date they were due.
- **Carry or drop**: overdue tasks to reschedule, move to Someday or drop. List them with how late
  each is, and ask. Don't recommend which way; the user knows what each one costs.

Be honest. If the week was thin, say so in a plain, kind sentence and move to next week.
Don't invent wins to cheer the user up. Real progress, even small, is better encouragement.

Keep the review short enough to read in two minutes: about one screen per business at most.

## Save it

Write `weekly/<YYYY>-W<WW>.md` in the founder folder with the layout in
`references/review-template.md`. Use the save tool so it lands in the same folder the other
skills read and never overwrites by accident. Write it in the project first, then put it in
place and delete the project copy:
`tasks.py save weekly/<YYYY>-W<WW>.md --from <project file>`. If the file for this week
already exists, read it, merge, and save with `--replace` rather than making a second one.
Show the user the focus lines and the path.

Then offer, don't do without a yes:
- To add each focus as a task due Friday (`tasks.py add ... --due friday`).
- To run `tasks.py rollover` and work through the overdue list.

## Reply style

Keep the reply short and plain: sentences under 25 words, light formatting (a few bullets or one
small table, little bold), no em or en dashes (write times as 09:00-10:00). Don't guess at
consequences ("the site may be down") that the files don't show. Finish with the one-line next step.

## Handoff

End the reply with one line on what's next (for example "On Monday, run daily-plan; it reads
these focus lines.").

- Reads: founder-context businesses, tasks.md, decisions.md, last week's `weekly/` file.
- Writes: `weekly/YYYY-Www.md`; tasks.md only after the user says yes.
- Next: daily-plan on Monday morning picks up the focus lines. personal-crm's weekly check-in
  list fits well right after the review. decision-log for anything due to revisit.
