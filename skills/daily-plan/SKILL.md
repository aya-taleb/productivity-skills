---
name: daily-plan
description: Plans today from tasks.md and your fixed commitments, across every business you run. Picks 1 to 3 focus blocks for the work that matters most and batches the small stuff into one or two slots. Uses a connected calendar if there is one; otherwise asks for today's classes, calls and other fixed times. Use it when the user says "plan my day", "what should I do today", "I have 4 hours, what first", "morning plan", "help me prioritize today", "I'm overwhelmed, where do I start", "plan tomorrow", or opens the day with a task dump. Saves the plan to daily/YYYY-MM-DD.md.
---

# Daily plan

A founder with several ventures and classes has more tasks than hours every single day. The plan
picks the few things that move a business forward, protects time for them, and puts everything
else in one batch so it doesn't leak into the focus time.

## Inputs

1. Find the files: `python3 <this skill's folder>/../tasks/scripts/tasks.py context`. Below,
   `tasks.py` means `python3 <this skill's folder>/../tasks/scripts/tasks.py`, run from the
   user's current folder (don't `cd` into the skill folder; the tool looks for `./founder/`
   where it runs).
2. Tasks: `tasks.py list --overdue`, `tasks.py list --due-by +2d`, and the full `tasks.py list`.
3. This week's focus: the newest `weekly/YYYY-Www.md` file, if there is one. The overall focus
   and per-business focus lines decide ties.
4. Fixed commitments for today:
   - If a calendar tool is connected in this session (for example a Google Calendar or Outlook
     connector), read today's events. Only read; never create, move or accept events unless the
     user asks.
   - If none is connected, ask: "What's fixed today? Classes, calls, shifts, pickups, with times."
     Don't guess a schedule and don't assume a 9 to 5 day.
5. Today's date and weekday: get them from a command (`date +%F`), not from memory.

If the user already listed their commitments in the message, use those and don't ask again.

When you have to ask about commitments, still give the picks: the 1 to 3 focus tasks in order and
the batch list, without times. Then ask for the fixed times so you can place them. Keep to three
picks even here; a list of six "candidates" is not a plan.

## Pick the focus blocks

- 1 to 3 focus blocks. Fewer when the day is full. Three blocks on a day with four hours free is
  a plan that fails by noon, and a failed plan teaches the user to stop planning.
- Each block: one task, its business tag, a start and end time, and the outcome that means done
  ("draft sent to Sam", not "work on deck").
- Pick in this order:
  1. Things due today, or overdue, that hurt if missed: a person waiting on the user (a tasting,
     a client, a call), money (an invoice), or a legal or permit date. A meeting-like task due
     today (a tasting, a demo) is a fixed commitment; if it has no time yet, ask for one.
  2. Things due tomorrow that need real work (a bug fix before a demo).
  3. This week's focus for the overall-focus business, then other weekly focus lines.
  Small overdue admin (renew a domain, send an invoice) usually fits the batch, not a focus block.
- If the user scopes the day ("mostly corner lunch"), pick from that business. Bring in another
  business only for something due today or overdue that costs money or a person, and say why.
- Put the hardest block in the user's best hours if they've said when that is. If they haven't,
  ask once and remember it in the plan file notes.
- Leave buffer: at least 15 minutes between a fixed commitment and any block, and plan no more
  than about 70 percent of the free time. Count the batch slot in that 70 percent.

## Batch the rest

Small tasks (emails, invoices, quick replies, errands) go into one or two batch slots, grouped by
type, not by business. Replying to all emails at once is faster than switching between ventures.
Anything that doesn't fit today stays in tasks.md. Say plainly what is not getting done today.

## Output

Show a short plan: the time-ordered day, focus blocks marked, the batch list, and "not today".
Block lengths come from the user's free time, not from guesses about how long a task takes.
If a task's length matters and is unknown, give it a block and say "adjust if it runs long".
Never invent a time for a commitment the user didn't time (a tasting with no hour); ask for it
and leave that slot open.
Before showing the plan, check it: every block has 15 minutes clear on both sides of each fixed
commitment, the blocks fit the free time, and any count you state ("5 tasks due this week")
matches the tool's output. Leave counts out rather than estimate them.
Show the time math in one line ("free 8.5 h, planned 5.5 h"), so the user can trust the plan fits.
Then save it to `daily/YYYY-MM-DD.md` in the founder folder (layout in
`references/plan-file.md`), even when it is still waiting on times; mark it "draft". If today's
file exists, update it.

Don't change due dates in tasks.md on your own. If an overdue task won't fit, list it under
"needs a new date" and ask.

## End of day (when the user comes back)

If the user says how the day went, mark finished tasks done with `tasks.py done`, add a line to
the plan file on what happened, and carry unfinished focus items into tomorrow's candidates.

## Reply style

Keep the reply short and plain: sentences under 25 words, light formatting (a few bullets or one
small table, little bold), no em or en dashes (write times as 09:00-10:00). Don't guess at
consequences ("the site may be down") that the files don't show. Finish with the one-line next step.

## Handoff

End the reply with one line on what's next (for example "Tell me how it went tonight and I'll
mark things done.").

- Reads: tasks.md, newest weekly review, today's calendar (only if connected), founder-context.
- Writes: `daily/YYYY-MM-DD.md`; tasks.md only to mark done when the user says so.
- Next: tasks to capture anything new; weekly-review at the end of the week.
