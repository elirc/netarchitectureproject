# Outbox / inbox processing — reliability mechanics

Every module (`Administration`, `Meetings`, `Payments`, `Registrations`, `UserAccess`) has its own
`OutboxMessages`, `InboxMessages`, and `InternalCommands` tables (schema-per-module, see
`src/Database/CompanyName.MyMeetings.Database/Structure/*/Tables/`) and its own three Quartz jobs
(`ProcessOutboxJob`, `ProcessInboxJob`, `ProcessInternalCommandsJob`). This doc covers the shape
that's identical across all five — using Meetings/Payments file paths as the concrete example,
same as `navigation/03-*.md`.

## Table shape (identical across modules)

`src/Database/CompanyName.MyMeetings.Database/Structure/meetings/Tables/OutboxMessages.sql`:
```sql
CREATE TABLE [meetings].OutboxMessages (
    [Id] UNIQUEIDENTIFIER NOT NULL,
    [OccurredOn] DATETIME2 NOT NULL,
    [Type] VARCHAR(255) NOT NULL,
    [Data] VARCHAR(MAX) NOT NULL,
    [ProcessedDate] DATETIME2 NULL,
    CONSTRAINT [PK_meetings_OutboxMessages_Id] PRIMARY KEY ([Id] ASC)
)
```
`InboxMessages.sql` is byte-for-byte the same shape (`payments`/`meetings`/etc. schema prefix
only differs). `[Id]` is the primary key; `[ProcessedDate] IS NULL` is the "still pending" marker.
There is **no unique constraint on anything but `Id`** — worth noting before you assume this table
by itself gives you dedup on content.

## Outbox: "at least once, in commit order" — `ProcessOutboxCommandHandler.cs`

```csharp
SELECT [Id],[Type],[Data] FROM [meetings].[OutboxMessages]
WHERE [ProcessedDate] IS NULL ORDER BY [OccurredOn]
...
foreach (var message in messagesList)
{
    var @event = JsonConvert.DeserializeObject(message.Data, type) as IDomainEventNotification;
    await this._mediator.Publish(@event, cancellationToken);          // (A)
    await connection.ExecuteAsync(sqlUpdateProcessedDate, new { Date = DateTime.UtcNow, message.Id }); // (B)
}
```
Ordering is `ORDER BY OccurredOn`, not a strictly-increasing sequence number — under concurrent
writers with clock skew this is only an approximation of commit order. More importantly: **(A) and
(B) are not atomic with each other.** If the process crashes or the job times out between
publishing (A) and marking processed (B), the next poll re-reads the same unprocessed row and
re-publishes it — this is the textbook outbox "at-least-once" guarantee, and it's a *deliberate*
trade (never lose a message) that pushes the duplicate-handling burden onto the subscriber.

## Where the duplicate-handling burden should land — and where it actually lands

The natural place to absorb a redelivered outbox message is the inbox insert on the subscriber
side. But trace what actually happens on redelivery here:

1. `ProcessOutboxCommandHandler` re-publishes the *domain-level* `MeetingAttendeeAddedNotification`
   (deserialized from the outbox row, so it keeps the **same** `Id`).
2. That re-triggers `MeetingAttendeeAddedPublishEventNotificationHandler.Handle`
   (`Meetings/Application/Meetings/SendMeetingAttendeeAddedEmail/
   MeetingAttendeeAddedPublishEventNotificationHandler.cs`), which builds a **new**
   `MeetingAttendeeAddedIntegrationEvent` with `Guid.NewGuid()` as its `Id`:
   ```csharp
   await _eventsBus.Publish(new MeetingAttendeeAddedIntegrationEvent(Guid.NewGuid(), ...));
   ```
3. Payments' `IntegrationEventGenericHandler<T>.Handle` inserts that `Id` into
   `[payments].[InboxMessages]` as the primary key.

Because step 2 mints a fresh `Id` on every republish, a redelivered outbox message produces a
**second, different-Id row** in the inbox with identical business content — the `Id` PRIMARY KEY
does not catch it, because the two rows are not "the same message twice," they're two distinct rows
that happen to describe the same real-world event. Net effect: the crash-window described above can
cause Payments to create **two `MeetingFee`s for one attendee** the one time it actually matters (a
crash between outbox-publish and outbox-mark-processed). This is a real, traceable gap in this
codebase — a good target for a mid-rung "make this idempotent" exercise if this project is ever
promoted past READ tier, and a good interview question in its own right (see `07-change-request.md`
which uses a different, non-destructive feature request instead).

## Inbox: dedup only via `ProcessedDate`, not content

`ProcessInboxCommandHandler.cs` (`Payments/Infrastructure/Configuration/Processing/Inbox/`):
```csharp
SELECT [Id],[Type],[Data] FROM [payments].[InboxMessages] WHERE [ProcessedDate] IS NULL ORDER BY [OccurredOn]
...
foreach (var message in messages)
{
    var request = JsonConvert.DeserializeObject(message.Data, type);
    await _mediator.Publish((INotification)request, cancellationToken);
    await connection.ExecuteScalarAsync(sqlUpdateProcessedDate, new { Date = DateTime.UtcNow, message.Id });
}
```
Same shape as the outbox job, same non-atomicity between publish and mark-processed — a crash here
would redeliver the *same* inbox row (same `Id`, since it's already persisted), which the
`WHERE ProcessedDate IS NULL` filter would correctly pick up again... but nothing stops
`_mediator.Publish` from running twice for the same row across two overlapping job runs, since
`[DisallowConcurrentExecution]` on the Quartz job only prevents concurrent runs of *the same job*,
not a row being claimed by two different worker instances if this were ever scaled out. Worth
flagging in a review: this delivery pattern is safe for a single-instance deployment and would need
a `SELECT ... FOR UPDATE`-style claim (or a status column with an atomic claim) before running two
API instances against one database.

## Internal commands: a third queue, same shape, different purpose

`Payments/Infrastructure/Configuration/Processing/InternalCommands/CommandsScheduler.cs` writes to
`[payments].[InternalCommands]`; `ProcessInternalCommandsJob` (sibling file, same folder) drains it
the same way. This is *not* for cross-module messages — it's how a handler defers work within its
own module (e.g. `MeetingAttendeeAddedIntegrationEventHandler` enqueues `CreateMeetingFeeCommand`
rather than executing it inline) so that an integration-event handler's job stays "translate and
enqueue," never "do the business operation inline inside someone else's inbox-processing
transaction."

## Evidence paths
- `src/Modules/Meetings/Infrastructure/Configuration/Processing/Outbox/ProcessOutboxJob.cs`, `ProcessOutboxCommandHandler.cs`
- `src/Modules/Payments/Infrastructure/Configuration/Processing/Inbox/ProcessInboxJob.cs`, `ProcessInboxCommandHandler.cs`
- `src/Modules/Payments/Infrastructure/Configuration/EventsBus/IntegrationEventGenericHandler.cs`
- `src/Modules/Payments/Infrastructure/Configuration/Processing/InternalCommands/CommandsScheduler.cs`, `ProcessInternalCommandsJob.cs`
- `src/Database/CompanyName.MyMeetings.Database/Structure/{meetings,payments}/Tables/{OutboxMessages,InboxMessages}.sql`
