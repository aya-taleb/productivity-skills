# productivity-skills

Helps a founder run several small ventures and school at once without dropping things.

## What do you want to do?

| I want to... | run this |
| --- | --- |
| See all my businesses in one place each week and pick what matters | /weekly-review |
| Get every to-do out of my head and onto one list | /tasks |
| Know what to do today, with my classes and calls in the way | /daily-plan |
| Stay in touch with people without it feeling like a chore | /personal-crm |
| Turn meeting notes into who does what, by when | /meeting-actions |
| Write down why I made a call, and check it later | /decision-log |
| Hand a task to a VA, freelancer or helper | /delegation-brief |
| Tell every skill about my businesses once | /founder-context |

## Install

```
/plugin marketplace add aya-taleb/productivity-skills
/plugin install productivity-skills@productivity-skills
```

## Start here

Run `/founder-context` once to add each business. Then brain dump into `/tasks`.
On Friday or Sunday, run `/weekly-review`. It reads your tasks and decisions and sets one
focus per business. On Monday, `/daily-plan` picks it up.

Everything lives in plain files in `~/.founder/`: `tasks.md`, `decisions.md`,
`weekly/`, `daily/`, `people/`. You can open and edit any of them by hand.

## Good to know

- Nothing is sent for you. Note drafts and follow-ups are for you to copy and send.
- No numbers are made up. Missing numbers stay as `{{placeholders}}` until you fill them.
- No app or account needed. Two small Python tools (standard library only) keep the files tidy.
- Your calendar is read only if you have a calendar connector on. Otherwise the plan asks you.
- Decisions with legal, tax or money weight get a "not advice, ask an accountant or lawyer" note.

## Credits

Made by Aya Taleb (github.com/aya-taleb). The tasks skill is changed from Anthropic's
productivity plugin (Apache 2.0). Thanks to thecraighewitt for the personal CRM idea.
See CREDITS.md. MIT.
