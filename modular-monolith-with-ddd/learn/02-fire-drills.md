# Reading fire drills (READ tier: find the cause in code, don't run anything)

Each drill gives you a production symptom. For each one, write:
1. the suspect file:line,
2. the mechanism in two sentences,
3. one SQL query or log line that would confirm it in production,
4. a fix outline plus the test that would have caught it.

Answers are sealed in `learn/_answers/02-fire-drills.md`. **Don't read `training/navigation/04-outbox-inbox-processing.md`
before FD1 and FD4**, because it contains their answers. Budget about 15 minutes per drill.
These are code-reading deductions. None of them has been reproduced on a running system (see the batch-1 report). Your answers
should say what evidence would *confirm* each one.

---

### FD1 — Two fees for one attendee
> **Finance, 09:40:** "Attendee 7f3c… has two open `MeetingFee`s for the same meeting, both 25 EUR. It happened once last week
> too. Both times the API pod was restarted by the platform a few seconds after the attendee joined. The inbox table shows two
> rows with identical `Data` apart from the `Id`."

Start from `src/Modules/Meetings/Infrastructure/Configuration/Processing/Outbox/ProcessOutboxCommandHandler.cs` and follow the
`MeetingAttendeeAddedNotification` until you reach an `INSERT` into `payments.InboxMessages`.

### FD2 — "Every meeting lasts zero minutes"
> **Support:** "The calendar export shows every meeting created or edited since launch as ending at its start time. Nobody
> noticed because the web page only displays the start time."

Look at the **committed** code (`git show HEAD:...`), not the working tree. How many handlers are affected? Why did CI stay green?

### FD3 — Payments stopped creating fees on Tuesday
> **On-call:** "Since Tuesday's deploy, no new `MeetingFee`s. `SELECT COUNT(*) FROM meetings.OutboxMessages WHERE ProcessedDate
> IS NULL` climbs all day, from 3 to 4,100. The Meetings log shows the same `ArgumentNullException` from `ProcessOutboxJob`
> every 15 seconds. The deploy renamed a notification class in Meetings."

Read `ProcessOutboxCommandHandler.cs:55-69`,
`src/BuildingBlocks/Infrastructure/DomainEventsDispatching/DomainNotificationsMapper.cs:17-20` and where the map is filled
(`src/Modules/Meetings/Infrastructure/Configuration/MeetingsStartup.cs`, the `domainNotificationsMap.Add(...)` lines). Why are
*all* messages stuck, and not just the renamed one?

### FD4 — Duplicates appear right after scaling out
> **Platform:** "We moved from 1 to 2 API replicas for Black Friday. Duplicate welcome emails and a handful of duplicate fees
> started within the hour. `ProcessInboxJob` has `[DisallowConcurrentExecution]`, so it can't run twice, right?"

Read `ProcessOutboxJob.cs:5` and the `SELECT ... WHERE ProcessedDate IS NULL` in both processing handlers. What does
`[DisallowConcurrentExecution]` actually guarantee?

### FD5 — "Why do I owe less than everyone else?"
> **Support:** "An organizer raised the fee from 10 to 20 EUR a week before the meeting. Early attendees are asked for 10 EUR
> and later ones for 20 EUR. One early attendee also added a guest after the change. Is this a bug?"

Read `Meeting.ChangeMainAttributes` (`src/Modules/Meetings/Domain/Meetings/Meeting.cs:128-153`), `MeetingAttendee.cs:71-78`
and the Payments handler `src/Modules/Payments/Application/MeetingFees/MeetingAttendeeAddedIntegrationEventHandler.cs:19-26`.
This drill is half code and half product. Write the **question you'd ask the PM** as part of your answer. Also compare
`ChangeMainAttributes` with `AddAttendee` (`Meeting.cs:158`): which guard is missing?
