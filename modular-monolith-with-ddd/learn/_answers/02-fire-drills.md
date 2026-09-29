# SEALED — attempt `learn/02-fire-drills.md` first

All five answers are code-reading deductions (static trace, 2026-09-26, HEAD `a7d111a`). None was reproduced at runtime.

## FD1 — duplicate fee after a restart
- **Where:** `MeetingAttendeeAddedPublishEventNotificationHandler.cs:18-19` mints `Guid.NewGuid()` for the integration event.
  `ProcessOutboxCommandHandler.cs:62` (publish) and `:64-68` (mark processed) are not atomic.
- **Mechanism:** the pod dies after publishing but before marking the row processed. The next poll republishes the same
  outbox row. The notification Id is stable, but the handler builds a *new* integration event with a *new* Guid. The Payments
  inbox PK (`InboxMessages.sql:8`) sees a different Id, so it accepts a second row, and the inbox job creates a second
  `CreateMeetingFeeCommand`.
- **Confirm:** `SELECT JSON_VALUE(Data,'$.AttendeeId') a, JSON_VALUE(Data,'$.MeetingId') m, COUNT(*) FROM payments.InboxMessages WHERE Type LIKE '%MeetingAttendeeAdded%' GROUP BY JSON_VALUE(Data,'$.AttendeeId'), JSON_VALUE(Data,'$.MeetingId') HAVING COUNT(*)>1;`
  Correlate with pod restart times.
- **Fix:** carry the stable notification/domain-event Id into the integration event (`notification.Id`), and treat a
  duplicate-key error on the inbox insert as "already received". Defense in depth: make `CreateMeetingFee` idempotent on
  (payer, meeting). **Test:** publish the same notification twice and assert one inbox row.
- See [01](../../../../opusorganize/apprenticeship/curriculum/01-transactional-outbox.md) and
  [02](../../../../opusorganize/apprenticeship/curriculum/02-idempotency.md).

## FD2 — end date equals start date
- **Where:** HEAD `CreateMeetingCommandHandler.cs` (~line 24) and HEAD `ChangeMeetingMainAttributesCommandHandler.cs`
  (~line 32). Both pass `request.TermStartDate` twice. Two handlers are affected.
- **Why CI was green:** no end-after-start rule on HEAD, and domain tests build `MeetingTerm` directly
  (`MeetingTestsBase.cs:60-61`), so no test executes the handler mapping line.
- **Confirm:** `SELECT COUNT(*) FROM meetings.Meetings WHERE TermStartDate = TermEndDate;` Check the real column names in
  `Structure/meetings/Tables/Meetings.sql`.
- **Fix:** pass `TermEndDate`, add a `MeetingTermMustEndAfterStartRule`, and add a handler-level test. The user's uncommitted
  working tree and `astraupskill/` already contain exactly this fix, so compare, don't duplicate. **Data repair:** existing rows
  can't be fixed from the DB alone because the end time was never stored. You need a product decision (for example, default
  duration) plus organizer notification. That's the senior part of the answer.

## FD3 — poison message blocks the whole outbox
- **Where:** `DomainNotificationsMapper.GetType` returns `null` for an unknown name (`:19`). The old rows still hold the *old*
  class name registered in `MeetingsStartup.cs`. `JsonConvert.DeserializeObject(data, null)` gives a `JObject`, and
  `as IDomainEventNotification` makes that `null` (`ProcessOutboxCommandHandler.cs:58`). `_mediator.Publish(null)` then throws
  `ArgumentNullException` (`:62`).
- **Why all messages are stuck:** there's no try/catch per message, no attempt counter and no dead-letter state. The loop
  aborts at the first bad row. `ORDER BY OccurredOn` (`:42`) puts that same row first on every poll. That's head-of-line blocking.
- **Confirm:** `SELECT TOP 5 Type, OccurredOn FROM meetings.OutboxMessages WHERE ProcessedDate IS NULL ORDER BY OccurredOn;`
  The oldest row's `Type` won't be present in the startup map.
- **Fix:** keep the old name as an alias in the map (renames are schema changes for messages; see
  [07 expand/contract](../../../../opusorganize/apprenticeship/curriculum/07-zero-downtime-migrations.md)). Per-message
  try/catch with `Attempts` + `Error` columns and a poison threshold. Alert on pending count and oldest age.
  **Test:** seed an outbox row with an unknown `Type` followed by a good row, then assert the good row gets processed.

## FD4 — duplicates after scaling to 2 replicas
- **Where:** `[DisallowConcurrentExecution]` (`ProcessOutboxJob.cs:5`, same on the inbox job) is a **per-scheduler** guarantee
  for an in-memory Quartz scheduler. Two replicas means two schedulers. Both handlers `SELECT ... WHERE ProcessedDate IS NULL`
  without a claim or lock, so both replicas read the same rows and both publish.
- **Confirm:** log lines with the same `OutboxMessage:<id>` context (the enricher at `ProcessOutboxCommandHandler.cs:85`) from
  two different hosts within seconds.
- **Fix:** an atomic claim (`UPDATE TOP(n) ... OUTPUT` with `READPAST`, or `UPDLOCK, READPAST` inside a transaction), a
  clustered Quartz job store, or a single dedicated worker. Idempotent consumers are still required. See
  [03](../../../../opusorganize/apprenticeship/curriculum/03-concurrency-races.md) and
  [14](../../../../opusorganize/apprenticeship/curriculum/14-load-backpressure-timeouts.md).
- Note: `training/navigation/04` flags this as "safe for single-instance only". The drill checks whether you'd catch it when
  someone *else* scales out.

## FD5 — fee snapshot at join time
- **Code facts:** each attendee's `_fee` is computed once at join (`MeetingAttendee.cs:73`) and sent to Payments in the
  `MeetingAttendeeAddedDomainEvent` → integration event. `CreateMeetingFeeCommand` is created at that moment (Payments handler
  `:19-26`). `ChangeMainAttributes` only changes `_eventFee` for **future** attendees (`Meeting.cs:148`). Nothing re-prices
  existing attendees or their `MeetingFee`. Adding a guest after the change: there's no "change guests" path in `Meeting`, so
  check whether the UI re-joins the attendee. If it did, `MemberCannotBeAnAttendeeOfMeetingMoreThanOnceRule` would block it.
- **Missing guard:** `ChangeMainAttributes` doesn't check `MeetingCannotBeChangedAfterStartRule`. `AddAttendee` does (`:158`).
  Only the attendee-limit rule is checked (`:138-140`).
- **PM question:** "When the fee changes, should existing attendees keep the price they agreed to (price lock) or be
  re-priced? If re-priced, do we notify them and let them withdraw?" Either answer is valid. Silently doing one is the bug.
- **Grading:** full marks for noticing that this is a *product decision encoded by accident*, plus the missing guard.
