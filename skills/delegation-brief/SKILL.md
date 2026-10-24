---
name: delegation-brief
description: Writes a clear brief and a step-by-step SOP to hand a task to a contractor, freelancer, VA or helper, with the outcome, steps, quality bar, budget, deadline, check-ins and what they can decide alone. Use it when the user says "I want to hand this off", "write a brief for my VA", "hire someone on Upwork to do X", "turn how I do this into an SOP", "delegate the invoicing", "my cousin is helping with deliveries, write him instructions", "what should I tell the designer". Works for app, service and local businesses in founder-context. Drafts only; the user sends and hires.
---

# Delegation brief

A founder with several ventures runs out of hours first. Handing work off only saves time if the
helper can do it without twenty questions. A good brief says what done looks like, how good is
good enough, what it costs, and when to check in.

## Inputs

- What the task is and which business (slug from founder-context; read that business file for
  tone and off-limits topics).
- Founder folder: `python3 <this skill's folder>/../tasks/scripts/tasks.py context`. Below,
  `tasks.py` means `python3 <this skill's folder>/../tasks/scripts/tasks.py`, run from the
  user's current folder (don't `cd` into the skill folder; the tool looks for `./founder/` where
  it runs).
- How the user does it today. Best is a quick walkthrough: "tell me the steps as you'd do them".
  Existing notes, docs or screenshots the user shares are also good.

Ask in one batch for what's missing: the outcome, deadline, budget (hourly or fixed), who the
helper is (skill level, new or known), tools and accounts they'll need, and what they must never do.

## The brief

Use `references/brief-template.md`. The parts and why:
- **Outcome**: what done looks like, in one or two lines. A helper who knows the goal can solve
  problems the steps didn't cover.
- **Context**: who the customer is and why this matters, three lines at most.
- **Steps (SOP)**: numbered, one action each, written so a new person can follow them. Mark the
  steps where mistakes are expensive.
- **Quality bar**: two or three checks the helper runs before saying done, plus an example of good
  if the user has one. Never invent an example the user didn't give; leave a placeholder.
- **Budget and time**: the user's numbers only. Missing ones become `{{budget}}` and
  `{{deadline}}`. Don't suggest market rates as facts; if the user asks, say rates vary and
  suggest they check a few real listings.
- **Decision rights**: what the helper may decide alone, what needs a quick message first, and what
  is never theirs (refunds, prices, anything legal or with customer money).
- **Check-ins**: a first check early (after the first item or first hour), then a regular rhythm,
  and the channel.
- **Access**: which accounts or files they need. Advise shared or limited access (a separate login,
  view-only links, a password manager share) and never ask the user to paste passwords into the
  brief.
  If the user gives you a password anyway, keep it out of every file and the brief, say so, and
  suggest they change it since it was typed in plain text.

Keep it to about one page. A brief nobody reads is no brief.

Fill the gaps without making the user's process up. Steps, terms, dates and rules the user
gave go in as written. Everything you add is marked `(suggested)`: a draft date, a revision
round, a check-in rhythm, an extra check, and every line in "decide alone", "message me first"
and "never" that the user didn't say. A helper can't tell your guess from the user's rule unless
you mark it. Say in the reply how many lines you marked, so the user knows to review them.

## Legal and money

When the task touches money, books, taxes or contracts (bookkeeping, payroll, invoicing, a first
hire, worker classification), say in the reply that this is not legal, tax or accounting advice,
and suggest an accountant for the setup. Don't draft contracts here.

## Save and hand off

- Save to `delegation/<slug>-<task>.md` in the founder folder.
- Offer to add tasks: "Send brief to <helper>" and each check-in date, with `tasks.py add`,
  tagged by business. Ask first.
- If the user has a person file for the helper in `people/`, offer to note the hand-off there.
- The user sends the brief and hires. This skill never posts jobs or messages anyone.

## Reply style

Keep the reply short and plain: sentences under 25 words, light formatting (a few bullets or one
small table, little bold), no em or en dashes (write times as 09:00-10:00). Don't guess at
consequences ("the site may be down") that the files don't show. Finish with the one-line next step.

## Handoff

End the reply with one line on what's next (for example "Send the brief, then add the first
check-in date to tasks.").

- Reads: founder-context business file, the user's description or notes.
- Writes: `delegation/<slug>-<task>.md`; tasks.md after a yes.
- Next: tasks for check-in dates, personal-crm if the helper is someone to stay in touch with.
