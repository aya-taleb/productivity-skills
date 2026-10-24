# Note examples

Each example shows a person file, a draft that slips, and the note to show. The slips are
the common ones: a guessed detail, a guessed mood, or a feeling the user never stated.

## A file with dated news

```markdown
# Jordan Lee
channel: text
cares about: the community garden on 14th
coming up: half marathon 2026-11-08
## Log
- 2026-09-20 lunch, she just started at the city library
```

Slips:
> Saw the half marathon is coming up, you must be deep in training!
> No need to reply if you're swamped.

"Deep in training" and "if you're swamped" are guesses. "Saw" claims the user saw something.

Show:
> Good luck at the half marathon on the 8th.
> How's the new job at the library going?

The check (not shown to the user): coming up, log.

## A thin file

```markdown
# Theo Grant
how we know each other: met at a founders meetup
channel: LinkedIn
last contact: 2026-09-02
```

Slips:
> Loved our chat at the meetup! How's the startup going?

The user never said they loved it, and the file says nothing about a startup.

Show:
> How have things been since the founders meetup?
> No rush on a reply.

The check: how we know each other, closer.

Then one line to the user: "Theo's file is thin. After he replies, tell me what he's working
on and I'll add it."

## When the best part is the user's own news

```markdown
# Sara Ito
cares about: early customer interviews
## Log
- 2026-08-30 call, she told me to talk to 10 customers before building
```

Slips:
> I talked to 10 customers like you said, and it changed everything.

The file doesn't say the user did it, or what happened.

Show:
> Your advice to talk to 10 customers first: {{one line on how that went}}.
> No need to reply.

The check: log, closer. The user fills the placeholder or cuts the line. Don't write "How did the
customer calls go?": the file doesn't say the user made them.

## When the user is unsure

The user says: "I think he moved to Denver?" The file doesn't say so.

Don't write "How's Denver treating you?", and don't leave "{{his new city}}" in the note.
Write the note from the file, then ask: "Do you know he moved? If yes, I can swap line 1
for: How's the move to Denver going?"
