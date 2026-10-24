# Person file layout

One file per person in `people/`, named with lowercase and dashes: `people/dana-kim.md`.
The tool reads the `key: value` lines at the top and the dated lines under `## Log`.
Everything else is free text for the user.

```markdown
# Dana Kim
how we know each other: UW entrepreneurship cohort, fall 2026
businesses: quizpal
cadence: monthly
channel: text
last contact: 2026-09-10
cares about: her thesis on food access; trail running
coming up: thesis defense 2026-11-12

## Notes
- Prefers texts to email.

## Log
- 2026-09-10 coffee after class, talked about her thesis
```

Fields:
- `cadence`: weekly, every 2 weeks, monthly, every 2 months, quarterly, twice a year, yearly,
  every N days, or paused. Missing means monthly.
- `channel`: how the user usually reaches them (text, email, LinkedIn, WhatsApp). The note matches it.
- `last contact`: the tool keeps it in step with the newest log line.
- `coming up`: dated news. Use an absolute date so it still makes sense next month.

Only write what the user told you. Leave a field blank rather than guessing.
