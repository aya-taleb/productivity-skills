# Build notes

Short list of what's unfinished, what needs Aya, and calls to review.

## Unfinished

- founder-context is not in `skills/` yet. It is listed in `skills.json` as synced from
  entrepreneur-skills, which did not exist when this repo was built. The sync step copies it in.
  Until then, every skill here still works: they read `businesses/*.md` if present and ask once
  if not.
- personal-crm is the weakest skill (81.8). Its notes still sometimes add a small unsupported
  clause (a guessed topic, "if you're swamped"). It beats the no-skill baseline (71.0), but the note
  wording deserves another pass, maybe with a worked example. It stopped by the plateau rule, not
  because it was good enough.
- Scores in TESTING.md come from my own headless runs, graded by a separate headless pass. They
  are not from `claude plugin eval`. Rerun them with the CLI before trusting small differences.

## Needs Aya

- Add `humanize` to this repo? personal-crm, meeting-actions and delegation-brief write words a
  person sends. CONVENTIONS section 4 says those run through humanize, but REPO-MAP lists only
  founder-context as synced here. Right now they say "if the humanize skill is installed, run the
  draft through it". If you want it guaranteed, add humanize to "Synced in" for productivity.
- Two folders the map doesn't name: meeting-actions writes `meetings/YYYY-MM-DD-<topic>.md` and
  delegation-brief writes `delegation/<slug>-<task>.md`, both in `~/.founder/`. Rename if
  you prefer something else.
- The ISO week file name is `weekly/2026-W43.md` (with a W). The map says `weekly/YYYY-WW.md`.
  I added the W so it can't be read as a month. Say if you want it without.

## Calls to review

- Fictional names only. After the coordinator's note, two real business names in a unit test were
  renamed (to Curbside Lunch Club and Tiny Tale Studio). Evals use QuizPal, Corner Lunch, Tidepool.
- Shared tool location: the other skills call `../tasks/scripts/tasks.py` (for `context`, `add`,
  `list`). That works because they ship in one plugin. If someone installs one skill alone, they
  fall back to reading the files directly.
- Project folder override: besides `$FOUNDER_HOME` and `~/.founder/`, the tools use a
  `founder/` folder at or above the current folder, but only if it already holds productivity
  files (tasks.md, people/, weekly/ and so on). This lets a project keep its own set and made the
  tests possible, since headless runs couldn't write under `~/.claude/`, where the files lived before the fix round. A `founder/` folder that only
  has other skills' files (market.md) is left alone.
- personal-crm ranks who's due: people with dated news in the next 14 days first, then most
  overdue. People with no logged contact come after anyone truly overdue. Default cadence is monthly.
- tasks `rollover` archives Done items older than 7 days into `tasks-archive.md` (upstream said
  "clear after about a week"; I keep them instead of deleting).
- daily-plan only reads a calendar. It never creates or moves events unless asked.

## Fix round after review

- User data moved out of `~/.claude` (protected by Claude Code) to `~/.founder`: business files, social folders and the media ledger. Tools honor `FOUNDER_HOME`; tests use a temp one.
- tasks.py and people.py fall back to `~/.founder` (they already honored `FOUNDER_HOME`); tests updated.
