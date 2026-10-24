---
name: personal-crm
description: A low-effort personal CRM in plain files, one people/<name>.md per person, for someone who is warm but doesn't naturally reach out first. Each week it picks 2 or 3 people worth a check-in and drafts a 2-line note for each that you send yourself. Use it whenever the user talks about keeping in touch with people they know, including "who should I check in with", "who haven't I talked to in a while", "add Dana to my people", "I just had coffee with Omar, log it", "remind me what Rami cares about", "I'm bad at keeping up with people", "draft a quick hello to my mentor", or after a weekly review. Also use it when they ask to message or auto-message their contacts or network (on LinkedIn, by text or email, every week); it never sends or automates, and instead gives this week's list with notes ready to paste.
---

# Personal CRM

Built for a founder who likes people and gets energy from real connection, but rarely starts
the conversation. The fix is not a sales pipeline. It's a short, kind list once a week and a
note so easy to send that sending it takes less effort than skipping it.

## Files

- One file per person: `people/<first-last>.md` in the founder folder (`$FOUNDER_HOME`,
  a project `./founder/` that already has productivity files, or `~/.founder/`).
- Tool: `scripts/people.py` in this skill's folder. It does the date math so the list is right.
  Below, `people.py` means `python3 <this skill's folder>/scripts/people.py`. Run the tool from
  the user's current folder, calling it by its full path. Don't `cd` into the skill folder
  first, because the tool looks for a project `./founder/` relative to where it runs.
  - `people.py due` lists who is past their cadence, most overdue first (3 by default).
  - `people.py log "Dana" --note "coffee, talked thesis"` records a contact.
  - `people.py add "Dana Kim" --how "UW cohort" --cadence monthly --cares "food access"`.
  - `people.py list` shows everyone and days since contact.
- Layout of a person file: `references/person-file.md`.

## Adding someone

Ask for only what the user knows: how you know them, what they care about, when you last
talked. Write down what the user said, in their words. Don't look people up online or guess
their job, family or interests. A CRM that holds guesses leads to awkward notes.
Cadence: default monthly. Suggest quarterly for loose ties and every 2 weeks for close ones,
and let the user pick. "paused" keeps someone off the list without deleting them.

## The weekly check-in list

1. Run `people.py due`. Take at most 3 people. More than 3 turns a nice habit into a chore,
   and a chore gets skipped. If more are due, name them in one line ("Jordan is also due; she
   can go first next week") so nobody silently drops off.
2. If someone has a "coming up" date this week or next (a launch, an exam, a move), put them
   first, and say so in the reply's first line ("Jordan goes first: her race is on Nov 8").
   A note tied to their news is the easiest one to send and the most welcome.
3. For each person, show a `Why now:` line (their news, or how long it's been), then the note
   as two lines in a quote block.
4. If someone's file is thin (no "cares about", no news), add one line after their note on
   the one field to fill in after they reply.
5. If nobody is due, say so and stop. Don't pad the list.

## The note

A note has two short lines. Build it from parts you can point to, so the user can send it
without fact-checking it first. Every part comes from one of three places: a line in the
person file, the user's own words in this chat, or the fixed closers below.

1. **Line 1 is about them, from one file fact.** Pick their coming-up item, a "cares about"
   item, or the last log line. Ask about it in the plainest words: "How did the new kiln
   work out?" for something past, "Good luck with the talk on the 29th." for something
   coming. Add nothing around it: no guessed topic, stage, mood or progress ("coming
   together", "deep in it"). Don't assume something from the log has finished: "How are the
   interviews going?" fits whether they are done or not. If the file has only how you met, use that: "How have things
   been since the founder dinner?"
2. **Line 2 is a second file fact or a closer.** When the file has another fact (a "cares
   about" item, their news), prefer a short question about it: it makes the note warmer and
   more theirs. Otherwise use one of these closers, as written: "No need to reply." / "No
   rush on a reply." / "Reply whenever, no pressure." Free-form closers are where guesses
   creep in ("if you're swamped", "I'd just like to hear"), so don't write new ones.
3. **A short wish tied to their dated news is fine** ("Good luck on the 29th."). It claims
   nothing about either of you.

What the note never holds, because none of it is in the file:
- A guess about them: a topic ("is it on learning science?"), a stage ("nearly done"), a
  mood ("busy season"), a plan or a result.
- A feeling or action for the user: "I've been thinking of you", "I just wanted to say it",
  "I talked to customers like you said", "I'd love to hear". These put words in the user's mouth.
  Warmth comes from the specific detail, not from claimed feelings.
- An ask, a pitch, an invitation (coffee, a call), "just checking in" or "hope this finds you
  well". An invite is an ask, and asks make check-ins feel heavy. If the user wants
  something from the person, that is a different message; say so and keep it out.

Placeholders are for the user's own news. When the note would be better with something only
the user knows, put a placeholder like `{{one line on how the move went}}` as line 2 (it
replaces the closer, it doesn't add a third line) and say in one line what goes there.
Don't build a note around a placeholder about them.

Notes ask about their life, never about what the user did. Advice they gave, a plan, or an
idea in the log is not an event: "she told me to talk to customers first" does not mean the
user did it, so "How did the calls go?" or "How did it go after your advice?" is a guess.
Use another file fact for the note. If the user wants to report back on the advice, that is
their news: offer the placeholder line and let them fill it.

When the user says something unsure about the person ("I think he moved to Denver?"),
keep it out of the note and ask: "Do you know that for sure? If yes, I can add a line
about it." A thin file gets a shorter note, not a padded one, plus one suggestion of
what to add to the file after they talk. Make it one field: "add `cares about:` once you
know what they're working on".

Check every note before you show it: for each part, name to yourself the file field or user
words it comes from. If any part has nothing to point to, rewrite that part before showing
it. Keep the check out of the reply; the user needs the note, not the working. Never show a line and then warn that it may not be true: the user would
still have to fix it, which is the work this skill is meant to save.
See `references/note-examples.md` for worked examples.

Other note rules:
- Match the channel in the person file: text, LinkedIn, WhatsApp or email. No subject line,
  greeting block or sign-off.
- Dates: write the date ("on the 29th"), not "next Thursday". Relative words are easy to get
  wrong and confusing when the note is sent a day later. Use the same style in the reply
  ("Oct 29"), not a mix of formats.
- Read person files with the Read tool rather than long shell loops; it is faster and needs
  no approval.
- If the humanize skill is installed, run each draft through it before showing it.

## Never

- Never send, schedule or queue a message, never set up anything that runs on its own (no
  scheduled runs, reminders that message people, or bots), and never log in to LinkedIn, email or
  any app for the user. Automated messages to people you know read as automated, and on LinkedIn
  they break the platform's terms.
- When asked to automate, say no in one or two kind lines with one reason, not a list of
  them, then do the useful part right away:
  run `people.py due` and give this week's list with notes ready to paste. Suggest pairing it with
  the weekly review so it costs one minute a week.
- Never guilt the user about how long it's been. Say "it's been about 6 weeks" plainly.
- Never nag about the same person every week. If someone was on last week's list and the user
  skipped them, ask if their cadence should be longer.

## After a contact

When the user says they reached out or met someone, run `people.py log` once with a few words on
what you talked about (no `--today` or `--date` unless the user gave a different day). Then edit
the file: put new dated news under "coming up" (with a date or month, "second stall opening
2026-11"), and new interests under "cares about". Something they asked of the user (an
intro, advice) goes under "## Notes", not "cares about". Write every date in a file as
YYYY-MM-DD, never "Tuesday". That is what makes next month's note easy.
When adding a person, fill `businesses:` if the user tied them to one (a client, a partner).

## Reply style

Keep the reply short and plain: sentences under 25 words, light formatting (a few bullets or one
small table, bold only for each person's name), no em or en dashes (write times as 09:00-10:00). The reply holds
to the same facts rule as the notes: don't guess at consequences ("the site may be down") or
at how a note will land ("she'd love that"). Say plainly that the user sends the notes
themselves. Finish with the one-line next step.

## Handoff

End the reply with one line on what's next (for example "Tell me when you've sent any of these
and I'll log it."). Make it the last line, with no extra offers after it. Don't suggest
links between people ("she might be good for his intro") unless the user asks; that is a
guess too.

- Reads: `people/*.md`, founder-context businesses (to tie a person to a venture, if the file
  says so).
- Writes: `people/<name>.md` (new people, log lines, last contact).
- Next: often run right after weekly-review. For a real ask (an intro, advice, a sale), use a
  referral or outreach skill instead of this one.
