# Training materials — modular-monolith-with-ddd (READ tier)

This is Kamil Grzybek's reference implementation (github.com/kgrzybek/modular-monolith-with-ddd,
verified via `git remote -v`, 330 real upstream commits). It is cloned wholesale — nothing under
`src/` was modified to build this pack. All added material lives here, under `training/`.

Tier: **READ** (Phase 4 only — codebase navigation). No incidents, no ladder, no source edits,
per the apprenticeship brief's OSS-clone rule.

A separate, older single-exercise pack (`astraupskill/`) already exists one level up, at
`..\..\astraupskill\` (i.e. `Desktop\.netarchitectureproject\astraupskill\`, outside this clone).
It is a bounded "worked change" course on a planted `MeetingTerm` end-date mapping bug in the
Meetings module's `CreateMeeting`/`ChangeMeetingMainAttributes` handlers. It does not overlap with
this navigation pack (different focus: one bug walkthrough vs. whole-system architecture) — see
the verdict in the batch report.

## Working tree note

`git status` shows 6 pre-existing modified/untracked files under
`src/Modules/Meetings/{Application,Domain}` (a `MeetingTerm` interval fix + new tests/rule file —
the same defect the `astraupskill` pack documents). These were **not created or touched by this
pass** and are left exactly as found. Only `training/` was written and committed here.

## Suggested reading order (~2–2.5 hours total)

1. `navigation/01-module-boundaries.md` (30 min) — how the 5 modules are separated and how
   `ArchTests` enforces it mechanically, not just by convention.
2. `navigation/02-command-flow-create-meeting.md` (30 min) — trace one HTTP request from
   controller to database row, file by file.
3. `navigation/03-integration-event-flow-meeting-attendee-added.md` (35 min) — trace one
   cross-module business event: Meetings raises it, Payments reacts to it, via outbox → bus →
   inbox/internal-command, without either module referencing the other's assembly.
4. `navigation/04-outbox-inbox-processing.md` (25 min) — the two Quartz jobs and SQL tables that
   make step 3 reliable (at-least-once delivery, idempotent processing).
5. `navigation/05-why-modular-monolith-vs-microservices.md` (20 min) — the senior "why?" analysis:
   what this architecture buys you, what it costs, and when the trade flips.
6. `navigation/06-first-change-onboarding.md` (10 min) — what to read before your first PR here.
7. `navigation/07-change-request.md` (10 min, exercise) — a realistic feature request; write your
   placement plan before checking `_answers/07-change-request-answer.md`.

## Layout

```
training/
  README.md                    (this file)
  navigation/
    01-module-boundaries.md
    02-command-flow-create-meeting.md
    03-integration-event-flow-meeting-attendee-added.md
    04-outbox-inbox-processing.md
    05-why-modular-monolith-vs-microservices.md
    06-first-change-onboarding.md
    07-change-request.md
  _answers/
    07-change-request-answer.md
```

**B08 additions:** a junior study route, on-ramp, reading fire drills and agentic drills now live in `../learn/` (start at
`learn/README.md`). A mini interview kit was added at `interview/QUESTIONS.md` (sealed: `_answers/interview-questions.md`).

No `ladder/`, `review/`, `incidents/`, or `agentic/` — out of scope for READ tier
per the brief (`LAB = 2,3,4,5 · DRILL = 3 · READ = 4`).
