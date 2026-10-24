---
name: decision-log
description: Logs a business decision in decisions.md with the context, the options you weighed, what you chose and why, what would change your mind, and a date to revisit. Also finds past decisions and lists the ones due for a second look. Use it when the user says "I decided to", "we're going with", "log this decision", "should I raise prices or not, help me write it down", "why did I pick Stripe again", "what decisions are due for review", "let's revisit the pricing call", or after a meeting where something big was agreed. Works for any business in founder-context.
---

# Decision log

Founders running several ventures make many calls a week and forget why. A short written record
stops the same debate from happening three times, and a revisit date turns a gut call into
something you can check.

## File

`decisions.md` in the founder folder. `python3 <this skill's folder>/../tasks/scripts/tasks.py
context`
prints the folder; run it from the user's current folder (don't `cd` into the skill folder; the tool
looks for `./founder/` where it runs). Newest entry at the top, under a `# Decisions` heading.
Create the file if
it is missing. Entry layout: `references/entry-format.md`.

## Logging a decision

Get these from the user. If the user gave the decision and a reason, write the entry right away
with `{{placeholders}}` for missing fields, and ask for those in the same reply. If they gave
less, ask once, in one message, before writing.
- **Business**: a slug from founder-context.
- **Decision**: one sentence, what was chosen.
- **Context**: why this came up now, in two or three lines.
- **Options**: the choice plus what else the user says was on the table. Don't add options they
  didn't name. If they only had one option, write that down; it's useful later.
- **Why**: the reasons in the user's words. Don't add reasons they didn't give.
- **What would change my mind**: a signal that would make this the wrong call. This is what the
  revisit checks.
- **Revisit on**: an absolute date. Suggest one that fits: about 2 weeks for a small test, 1 to
  3 months for pricing or a hire, 6 months for a big direction. The user picks.
- **Reversible?**: yes or no. A one-way door deserves a slower look.

If the user is still deciding, help them lay out the options and the questions that decide it,
but leave the choice to them. Don't hint at a lean, suggest a default, or weigh one side's
downsides more than the other's; asking you to decide is a sign they need the questions, not your
vote. Don't write an entry until they choose. Stick to facts in the files or that the
user gave; don't assume their state, permits or risks. Write the entry only once they choose.
Where a decision has legal,
tax or financial weight (a contract, an entity, an investment), say this is not legal, tax or
financial advice and name who to ask (a lawyer, an accountant).

Never invent numbers, quotes or facts in the context. Missing numbers become placeholders like
`{{current monthly price}}`.

## Revisit

- "What's due for review": list entries whose revisit date is today or earlier, oldest first.
  Say which ones are not due yet only if asked.
- For each one, show the decision and "what would change my mind", then ask what happened. If the
  user already said what happened, compare it to that signal in one line ("41 a week, above the
  35 line, so it held") and write the outcome.
- Add an `Outcome (date):` line under the entry: kept, changed, or reversed, and what was
  learned. Never delete or rewrite the original reasons. The point of a log is seeing what you
  thought at the time.
- If changed, log the new decision as a new entry that points back to the old one.

## Finding past decisions

Search decisions.md by business tag, keyword or date. Quote the entry; don't paraphrase the
reasons into something the user didn't say.

## Reply style

Keep the reply short and plain: sentences under 25 words, light formatting (a few bullets or one
small table, little bold), no em or en dashes (write times as 09:00-10:00). Don't guess at
consequences ("the site may be down") that the files don't show. Finish with the one-line next step.

## Handoff

End the reply with one line on what's next (for example "weekly-review will flag this on its
revisit date.").

- Reads: founder-context businesses, decisions.md.
- Writes: decisions.md. Offer to add a "revisit <decision>" task to tasks.md on the revisit date
  (`python3 <this skill's folder>/../tasks/scripts/tasks.py add ...`).
- Next: weekly-review reads revisit dates, so a due decision shows up in the week it's due.
