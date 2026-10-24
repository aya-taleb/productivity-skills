# Decision entry format

Newest entry at the top of `decisions.md`, under `# Decisions`.

```markdown
## 2026-10-23 #quizpal Move from free to a $4/month plan for new users
- Context: 212 signups, 0 revenue. Server costs went up after the September spike.
- Options: keep free; $4/month; one-time $15; do nothing until 500 users.
- Chose: $4/month for new users, current users stay free until January.
- Why: closest to what 3 of 5 interviewed students said they'd pay; easy to test.
- What would change my mind: fewer than 5 percent of new signups convert in 4 weeks.
- Reversible: yes
- Revisit on: 2026-11-20
```

When it's revisited, add below the entry (never edit the lines above):

```markdown
- Outcome (2026-11-20): kept. 7 percent converted. Next: test $6.
```

Keep the heading line in this shape: `## <date> #<business> <decision>`. weekly-review and search
depend on it.
