# Cross-module integration-event flow, file by file: Meetings → Payments

Business rule: when a member attends a meeting that has a fee, Payments needs to know so it can
create a `MeetingFee` to collect. Meetings must never call into Payments directly (that would
violate the `ArchTests` boundary in `navigation/01-module-boundaries.md`) — so the two modules
communicate only via a published event, each side owning its own database write.

## 1. Domain event — raised inside the Meetings aggregate

`src/Modules/Meetings/Domain/Meetings/Events/MeetingAttendeeAddedDomainEvent.cs` — a plain
`DomainEventBase` carrying `MeetingId`, `AttendeeId`, `FeeValue`, `FeeCurrency` (nullable — not
every meeting has a fee). Raised somewhere inside `Meeting`/`MeetingAttendee` when an attendee is
added (`src/Modules/Meetings/Domain/Meetings/MeetingAttendee.cs`).

## 2. MediatR notification — the same event, dispatched in-process first

Domain events collected on the aggregate are dispatched via
`DomainEventsDispatcher.DispatchEventsAsync()`
(`src/BuildingBlocks/Infrastructure/DomainEventsDispatching/DomainEventsDispatcher.cs`), called by
`DomainEventsDispatcherNotificationHandlerDecorator<T>` — a MediatR pipeline decorator that runs
**after** the real command handler, once per command. For each domain event it does two things:
```csharp
foreach (var domainEvent in domainEvents)
    await _mediator.Publish(domainEvent);          // (a) in-process notification handlers, e.g. send-email

foreach (var domainEventNotification in domainEventNotifications)
{
    var outboxMessage = new OutboxMessage(id, occurredOn, type, data);
    _outbox.Add(outboxMessage);                      // (b) queued for cross-module publication
}
```
One in-process handler subscribed to `MeetingAttendeeAddedNotification` is
`MeetingAttendeeAddedPublishEventNotificationHandler`
(`src/Modules/Meetings/Application/Meetings/SendMeetingAttendeeAddedEmail/
MeetingAttendeeAddedPublishEventNotificationHandler.cs`):
```csharp
public async Task Handle(MeetingAttendeeAddedNotification notification, CancellationToken ct)
{
    await _eventsBus.Publish(new MeetingAttendeeAddedIntegrationEvent(
        Guid.NewGuid(), notification.DomainEvent.OccurredOn,
        notification.DomainEvent.MeetingId.Value, notification.DomainEvent.AttendeeId.Value,
        notification.DomainEvent.FeeValue, notification.DomainEvent.FeeCurrency));
}
```
This is the **domain event → integration event translation point** — note it's a *different type*
(`MeetingAttendeeAddedIntegrationEvent`, public, in `Meetings.IntegrationEvents` namespace) from
the internal domain event. Other modules only ever see the integration event's shape; the domain
event's internal representation can change without breaking Payments.

## 3. Outbox write — same transaction as the meeting change

Back in `DomainEventsDispatcher`, part (b) above serializes the notification and adds an
`OutboxMessage` row via `IOutbox.Add(...)`. Because this all happens inside
`UnitOfWorkCommandHandlerDecorator`'s single commit (`navigation/02-*.md` step 3), the outbox insert
and the meeting-state change land in **one SQL transaction** — this is what makes the outbox
pattern actually solve the dual-write problem (you cannot commit the business change without also
committing the "I need to tell other modules" record).

## 4. `ProcessOutboxJob` — a Quartz job polls and republishes

`src/Modules/Meetings/Infrastructure/Configuration/Processing/Outbox/ProcessOutboxJob.cs` runs on a
schedule (Quartz), calling `ProcessOutboxCommand` →
`ProcessOutboxCommandHandler.Handle` (`.../Outbox/ProcessOutboxCommandHandler.cs`):
```csharp
SELECT ... FROM [meetings].[OutboxMessages] WHERE [ProcessedDate] IS NULL ORDER BY [OccurredOn]
...
await this._mediator.Publish(@event, cancellationToken);   // republishes the deserialized notification
await connection.ExecuteAsync(sqlUpdateProcessedDate, ...); // marks it processed, one row at a time
```
Publishing `MeetingAttendeeAddedNotification` again re-triggers step 2's handler, which calls
`_eventsBus.Publish(new MeetingAttendeeAddedIntegrationEvent(...))` — this time onto the actual
cross-module bus (`IEventsBus`).

## 5. The bus — `InMemoryEventBusClient` in this build

`src/BuildingBlocks/Infrastructure/EventBus/InMemoryEventBusClient.cs`: `Publish<T>` calls
`InMemoryEventBus.Instance.Publish(@event)`, a static in-process pub/sub — there is no RabbitMQ
wired up in this configuration (the interface `IEventsBus` is designed to be swappable; only the
in-memory implementation is present here). This matters for the "Why?" analysis: the *pattern*
(outbox → bus → inbox) is broker-agnostic, but this particular clone never demonstrates the
distributed-broker failure modes (network partition, broker down) — only the in-process ones.

## 6. Subscription — set up once per module at startup

`src/Modules/Payments/Infrastructure/Configuration/EventsBus/EventsBusStartup.cs`:
```csharp
SubscribeToIntegrationEvent<MeetingGroupProposalAcceptedIntegrationEvent>(eventBus, logger);
SubscribeToIntegrationEvent<NewUserRegisteredIntegrationEvent>(eventBus, logger);
SubscribeToIntegrationEvent<MeetingAttendeeAddedIntegrationEvent>(eventBus, logger);
```
Each subscription registers a generic `IntegrationEventGenericHandler<T>`
(`.../Payments/Infrastructure/Configuration/EventsBus/IntegrationEventGenericHandler.cs`) whose
*only* job is:
```csharp
INSERT INTO [payments].[InboxMessages] (Id, OccurredOn, Type, Data) VALUES (@Id, @OccurredOn, @Type, @Data)
```
This is the payments module's half of the boundary from `navigation/01-*.md` — the only place
Payments references a Meetings type (`MeetingAttendeeAddedIntegrationEvent`), and it's specifically
excluded from the `ArchTests` ban via the `EventsBusStartup`/`IntegrationEventHandler` carve-outs.

## 7. `ProcessInboxJob` — Payments processes its own inbox on its own schedule

`src/Modules/Payments/Infrastructure/Configuration/Processing/Inbox/ProcessInboxCommandHandler.cs`
(same shape as Meetings' version, `navigation/04-outbox-inbox-processing.md`): reads unprocessed
`[payments].[InboxMessages]`, deserializes by `Type`, calls `_mediator.Publish(...)`. This triggers:

`src/Modules/Payments/Application/MeetingFees/MeetingAttendeeAddedIntegrationEventHandler.cs`:
```csharp
public async Task Handle(MeetingAttendeeAddedIntegrationEvent notification, CancellationToken ct)
{
    if (notification.FeeValue.HasValue)
        await _commandsScheduler.EnqueueAsync(new CreateMeetingFeeCommand(
            Guid.NewGuid(), notification.AttendeeId, notification.MeetingId,
            notification.FeeValue.Value, notification.FeeCurrency));
}
```
Note the `if (FeeValue.HasValue)` guard — a free meeting produces no `MeetingFee` at all, which is
a business rule hiding in an integration-event handler, worth flagging in a code review.

## 8. One more hop — `CreateMeetingFeeCommand` goes through Payments' own internal-command queue

`_commandsScheduler.EnqueueAsync` writes to `[payments].[InternalCommands]`
(`src/Modules/Payments/Infrastructure/Configuration/Processing/InternalCommands/CommandsScheduler.cs`),
picked up later by `ProcessInternalCommandsJob` (a **third** Quartz job, separate from outbox/inbox)
which finally executes `CreateMeetingFeeCommand` and creates the `MeetingFee` aggregate.

## Why three hops (outbox → inbox → internal command) instead of one?

Each hop exists to make one specific failure survivable without a distributed transaction:
- **Outbox** makes "the meeting change committed" and "I will tell Payments" atomic within Meetings.
- **Inbox** makes "Payments received the event" idempotent and durable *before* Payments does
  anything business-visible with it — if the bus redelivers, the inbox row already exists /
  already processed, so the handler doesn't double-fire (see `04-outbox-inbox-processing.md` for
  the exact idempotency mechanism, or its gap).
- **Internal command queue** decouples "react to the event" from "actually create the fee" so the
  event handler's job is just translation (build a command), and a retry of `CreateMeetingFeeCommand`
  execution doesn't require re-processing the inbox message at all.

## Full file trace, in order
1. `Meetings/Domain/Meetings/Events/MeetingAttendeeAddedDomainEvent.cs`
2. `BuildingBlocks/Infrastructure/DomainEventsDispatching/DomainEventsDispatcher.cs`
3. `Meetings/Application/Meetings/SendMeetingAttendeeAddedEmail/MeetingAttendeeAddedPublishEventNotificationHandler.cs`
4. `Meetings/IntegrationEvents/MeetingAttendeeAddedIntegrationEvent.cs`
5. `Meetings/Infrastructure/Configuration/Processing/Outbox/ProcessOutboxJob.cs` + `ProcessOutboxCommandHandler.cs`
6. `BuildingBlocks/Infrastructure/EventBus/InMemoryEventBusClient.cs`
7. `Payments/Infrastructure/Configuration/EventsBus/EventsBusStartup.cs` + `IntegrationEventGenericHandler.cs`
8. `Payments/Infrastructure/Configuration/Processing/Inbox/ProcessInboxJob.cs` + `ProcessInboxCommandHandler.cs`
9. `Payments/Application/MeetingFees/MeetingAttendeeAddedIntegrationEventHandler.cs`
10. `Payments/Infrastructure/Configuration/Processing/InternalCommands/CommandsScheduler.cs` → `ProcessInternalCommandsJob.cs`
