# Testing

Scores come from my own grading of self-run outputs, so treat them as a guide, not a measurement.
Each case ran headless (`claude -p`) in a fresh folder with only this plugin loaded. A separate
headless pass graded it against the case's graders and the rubric in TEST-PROTOCOL.md. The
grader saw the transcript, the files before and after, and the SKILL.md in force for that round.
Run-to-run noise is about plus or minus 4 points, so small moves between rounds mean little.
Aya can rerun the same cases with `claude plugin eval`.

Raw outputs, grades and the harness are in `/home/claude/build/_work/productivity-skills/`
(not in this repo).

| skill | baseline | final | rounds | beats baseline? |
| --- | --- | --- | --- | --- |
| tasks | 50.0 | 91.3 | 5 | yes |
| weekly-review | 78.6 | 89.7 | 3 | yes |
| personal-crm | 71.0 | 81.8 | 5 | yes |
| daily-plan | 54.6 | 89.3 | 5 | yes |
| meeting-actions | 67.4 | 89.7 | 4 | yes |
| decision-log | 66.3 | 91.2 | 3 | yes |
| delegation-brief | 56.7 | 90.3 | 3 | yes |

Baselines for "ours" skills had no skill at all and no description to check, so their score
is scaled from 90 points to 100. The tasks baseline is Anthropic's upstream task-management
SKILL.md on the same cases (its description scored 8.3 of 10 on triggers).

Unit tests: 43 tests for `tasks.py` and `people.py`, all passing (`python3 -I -m unittest discover -s tests`).

### tasks  (reworked)
baseline: 50.0 (upstream task-management SKILL.md: wrote TASKS.md in the wrong place, no tags, pushed overdue dates)
final: 91.3 after 5 rounds. Stopped because r4 and r5 each gained under 5.
rounds:
- r1: 64.2, v1 SKILL.md plus tasks.py. Runs cd'd into the skill folder so the tool missed the project file; overdue dates pushed without asking.
- r2: 80.4, the tool finds founder/ from any subfolder and prints the file it wrote; "push everything" asks first; no connector offers; closing next-step line.
- r3: 88.0, tag from context and add now instead of holding tasks back; answer the question before making changes; reply style section.
- r4: 90.7, overdue tasks get three choices each (new date, Someday, drop), answerable in one line.
- r5: 91.3, show each list once; no guessing at consequences.
open issues: replies still sometimes guess why an overdue item matters.

### weekly-review  (ours)
baseline: 78.6 (no skill: decent reviews, but wrong weekdays, no file saved in one case, ranked list instead of one focus per business)
final: 89.7 after 3 rounds. Stopped because r2 and r3 each gained under 5.
rounds:
- r1: 86.1, v1.
- r2: 85.6, "slipped" means due before today; a focus is a step forward, not admin; always commit every focus line, marked (suggested); next-step line.
- r3: 89.7, basic math on given numbers is fine if shown; carry-or-drop lists without recommending; reply style.
open issues: sentences sometimes run long in the saved review.

### personal-crm  (ours)
baseline: 71.0 (no skill: gave 4 people and no notes; never read the files in the auto-send case)
final: 81.8 after 5 rounds. Stopped because r4 and r5 each gained under 5.
rounds:
- r1: 73.7, v1 plus people.py. Notes put facts in the user's mouth; it offered to schedule Monday runs; the auto-send case never loaded the skill.
- r2: 73.4, wider no-automation rule (decline, then give the list); no invitations in notes; tool finds founder/ from subfolders.
- r3: 83.1, description now covers "auto-message my contacts", so the skill loads; log edits "coming up"; no subject lines.
- r4: 80.2, named the claimed-feeling phrases to avoid.
- r5: 81.8, absolute dates in notes; a line-by-line check of each note against the person file.
open issues: the weakest skill here. In about 2 of 3 runs a note still adds a small unsupported clause (a guessed talk topic, "if you're swamped"). The tool, ranking and logging work; the note wording needs more work, maybe a worked example file.

### daily-plan  (ours)
baseline: 54.6 (no skill: ignored tasks.md, generic template, went along with an overpacked 2-hour day)
final: 89.3 after 5 rounds. Stopped because r4 and r5 each gained under 5.
rounds:
- r1: 82.1, v1.
- r2: 78.7, pick order (person waiting, money, permit dates first); small admin goes to the batch; untimed picks when asking for commitments.
- r3: 85.4, stay inside the business the user names; one-line time math; save a draft plan file even while waiting on times.
- r4: 87.9, no invented task durations or times for untimed commitments.
- r5: 89.3, self-check buffers and counts before showing.
open issues: a task due today with no time (a tasting) is still handled unevenly.

### meeting-actions  (ours)
baseline: 67.4 (no skill: never touched tasks.md, skipped the follow-up draft and meeting record)
final: 89.7 after 4 rounds. Stopped because r3 and r4 each gained under 5.
rounds:
- r1: 79.1, v1. Stopped at the confirmation step with no draft and no record.
- r2: 90.0, add tasks when the user already asked; always write the draft, in the user's voice; always save the meeting record.
- r3: 89.6, reply style and next-step line.
- r4: 89.7, check tasks.md for duplicates before adding; unsure dates stay unsure in the draft.
open issues: none major. It held the prompt-injection line in the transcript as content every round.

### decision-log  (ours)
baseline: 66.3 (no skill: in the LLC case it picked for the user and logged it, with no not-advice note)
final: 91.2 after 3 rounds. Stopped because r2 and r3 each gained under 5.
rounds:
- r1: 92.8, v1.
- r2: 88.6, no lean when asked to decide; compare the outcome to "what would change my mind"; list only due entries.
- r3: 91.2, write the entry right away with placeholders when the decision and a reason are given; options are only the user's; reply style.
open issues: trigger 9.2 of 10. "summarize the meeting where we chose the price" routes here instead of meeting-actions.

### delegation-brief  (ours)
baseline: 56.7 (no skill: no saved brief, no quality bar or decision rights, wrong weekday)
final: 90.3 after 3 rounds. Stopped because r2 and r3 each gained under 5.
rounds:
- r1: 89.9, v1.
- r2: 85.9, anything the skill adds is marked (suggested); a password typed in chat stays out of files.
- r3: 90.3, every added rule, including decision rights, is marked; a not-advice line whenever money, books or contracts are involved; reply style.
open issues: briefs run a little over one page.

## Calls I made

- Test fixtures live in a project `founder/` folder, not `~/.founder/`, because headless
  runs couldn't write under `~/.claude/` (the home folder before the fix round). Both tools look for a `founder/` folder (at or above the
  current folder) that already holds productivity files before falling back to `~/.founder/`.
- Fixture dates are tokens (`@D+3@`, `@W-1@`) that `place-files.sh` turns into real dates on the
  day a case runs, so the cases still make sense when rerun later.
- Cases whose only inputs are the founder/ fixtures don't end with an "Input files:" line. A real
  user wouldn't name their own task file. Cases with a transcript or notes file do name it.
- Fictional businesses only: QuizPal (app), Corner Lunch (local food), Tidepool Studio (service),
  plus #school. No real company or person names.
- Rounds 2 and 3 included repo-wide changes (a closing next-step line, a reply style section) along
  with each skill's own fixes.
- The grader was improved once (it now sees unchanged input files). Rounds 0 and 1 were regraded
  with it, against the SKILL.md each was run under, so every round uses the same grader.
- A few runs died at startup or mid-run when the machine was busy. They were rerun; the harness
  now retries any run with no final result.

## Independent review (blind)

A second agent reviewed personal-crm, the weakest skill here. Goal: notes use only what is in
the person's file and what the user said; anything else becomes a placeholder or a question.
Same harness as above (fresh `claude -p` runs, own HOME, separate grader), outputs in
`/home/claude/build/_work/review/weakest/`. A new case, thin-file-note, was added: a person
file that holds only "met at a founder dinner", and a user who is unsure of a detail.

| skill | case | winner | ours score | baseline score | fix rounds | one-line reason |
| --- | --- | --- | --- | --- | --- | --- |
| personal-crm | app-weekly-checkins | ours (both label orders) | 43 / 46 | 42 / 43 | 3 | start version's notes say "that's great" and "I'd just like to hear"; ours sticks to file facts |
| personal-crm | thin-file-note | ours (both label orders) | 43 / 44 | 36 / 38 | 3 | start version puts the unsure climate guess and "just curious" in the text; ours asks the user |

Baseline = the personal-crm version this review started from (builder's r5). Scores are the
blind judge's 0 to 50 totals (5 criteria x 10), one per label order. Before the fixes, ours
lost app-weekly-checkins three times with ours as label A and won once as label B, so the
judge leans toward label B; every pair was judged in both orders from then on.

### personal-crm  (review rounds, 4 cases)
start: 79.7 on the 3 old cases (builder's last was 81.8); 78.1 on all 4 cases.
final: 88.2 (shipped version, one run of all 4 cases). Best round: r5 at 93.0. Stopped
because r4 (+0) and r5 (+1.6) both gained under 5; then 3 fix rounds for the head-to-head.
rounds:
- r1: 89.2, the note is built from parts: line 1 from one file fact, line 2 a second file fact or one of three fixed closers; placeholders for the user's own news; a worked example file (references/note-examples.md).
- r2: 85.5, plainest-question wording, unsure user claims asked back, the reply follows the same facts rule, say the user sends.
- r3: 91.4, advice in the log is not an event; a placeholder replaces line 2; one-field file suggestion; examples moved off the test fixtures' names.
- r4: 91.4, name extra due people in one line; the next step is the last line; no guessed links between people.
- r5: 93.0, one reason when declining automation; bold only for names.
- fix 1: notes ask about their life, never what the user did; a "Why now:" line per person.
- fix 2: the source check stays out of the reply; prefer a second file fact over a closer; don't assume a log item has finished; one date style.
- fix 3: say who goes first and why; one line naming the field to fill for a thin file.
open issues: a note can still lean on a file fact a little ("the Portland move planning" for a spring move). Line 1 sometimes holds two questions.

## Polish round (Oct 24)

Method: each fix was rerun in fresh, isolated `claude -p` runs (own HOME, own project folder,
only the skill plus founder-context and humanize where the repo has them). The new version ran
against the current version (the last commit) on the same eval case. A separate `claude -p`
judge saw both outputs as A and B and scored them out of 50, once in each label order. A fix
ships only if it wins or ties in both orders. Scores are new / current. Runs, judge packets
and keys: `/home/claude/build/_work/polish/`.

| skill | case | round | order A-new | order A-current | result |
| --- | --- | --- | --- | --- | --- |
| personal-crm | app-weekly-checkins | r1 | tie 47/47 | won 46/44 | shipped |

What changed:
- personal-crm 0.1.1: keep a file fact in its own words and its own time (a plan months away
  is a plan, not work under way), no added stage or activity word, one question per line.
  Rania's note went from "How's the Portland move looking for the spring?" (smoke run) and
  "How is the ceramics studio going?" (current) to "Is the move to Portland still on for the
  spring?".
