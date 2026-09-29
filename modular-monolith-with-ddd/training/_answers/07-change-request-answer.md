# Sealed reference answer — 07-change-request.md

Do not read this until you've written your own answers to all 6 questions.

## 1. Which module needs a new type, and where?

Two new files, mirroring the `Paid` sibling exactly:
- **Payments**, `src/Modules/Payments/IntegrationEvents/MeetingFeeExpiredIntegrationEvent.cs` — a
  new public class in the existing `Payments.IntegrationEvents` project (same project that already
  holds `MeetingFeePaidIntegrationEvent.cs`), so Meetings can reference it without reaching into
  Payments' `Application`/`Domain` assemblies (that project is the intentional public contract
  surface between the two modules).
- **Meetings**, a new `MeetingFeeExpiredIntegrationEventHandler.cs` in
  `src/Modules/Meetings/Application/Meetings/` (same folder as the existing
  `MeetingFeePaidIntegrationEventHandler.cs`).

## 2. What does the new integration event need?

Confirmed by reading `MeetingFeePaidIntegrationEvent.cs`: it carries `PayerId` and `MeetingId`
(plus the base `Id`/`OccurredOn`). `MeetingFeeExpiredIntegrationEvent` needs the same two fields —
Meetings only needs to know *which attendee* on *which meeting* to act on, nothing about money.
Constructor shape:
```csharp
public MeetingFeeExpiredIntegrationEvent(Guid id, DateTime occurredOn, Guid payerId, Guid meetingId)
    : base(id, occurredOn) { PayerId = payerId; MeetingId = meetingId; }
```

## 3. Which existing Meetings command handles attendee removal?

`RemoveMeetingAttendeeCommand` / `RemoveMeetingAttendeeCommandHandler.cs`
(`src/Modules/Meetings/Application/Meetings/RemoveMeetingAttendee/`) already exists — **reuse it**,
don't write a new command. This is the whole point of question 3: check before you build. Enqueue
it from the new integration-event handler the same way `MeetingFeePaidIntegrationEventHandler`
enqueues `MarkMeetingAttendeeFeeAsPayedCommand`:
```csharp
public async Task Handle(MeetingFeeExpiredIntegrationEvent @event, CancellationToken ct)
{
    await _commandsScheduler.EnqueueAsync(new RemoveMeetingAttendeeCommand(
        Guid.NewGuid(), @event.MeetingId, @event.PayerId));
}
```
(Verify `RemoveMeetingAttendeeCommand`'s actual constructor parameters and order against the file
before using this — the PM's phrasing left "or mark them as needing to re-RSVP" open; removing is
the more surgical option and matches an already-existing command instead of inventing new attendee
state.)

## 4. Where does the domain→integration translation happen, and is it the right template?

For the `Paid` case it is **not** inside `MeetingFee.cs` and not inside the `IntegrationEventHandler`
naming pattern used for the *inbound* side (`03-*.md`'s step 2) — it's a dedicated
`MeetingFeePaidNotificationHandler`
(`src/Modules/Payments/Application/MeetingFees/MarkMeetingFeeAsPaid/
MeetingFeePaidNotificationHandler.cs`), an `INotificationHandler<MeetingFeePaidNotification>` that:
loads the aggregate fresh via `IAggregateStore` (Payments uses event-sourcing-style
`IAggregateStore.Load`, not the EF-repository pattern Meetings uses — a real architectural
difference between the two modules worth noting, not a mistake to "fix"), takes a snapshot, and
publishes the integration event with data pulled from the snapshot rather than the raw domain
event's fields. **Yes, copy this template** for `MeetingFeeExpiredNotificationHandler` — load via
`_aggregateStore.Load(new MeetingFeeId(notification.DomainEvent.MeetingFeeId))`, use
`GetSnapshot()`, publish `MeetingFeeExpiredIntegrationEvent`. This is a different mechanism than
`MeetingAttendeeAddedPublishEventNotificationHandler` in `navigation/03-*.md` (which reads fields
straight off the domain event, no aggregate reload) — the codebase isn't fully consistent about
which pattern each module uses, which is itself worth naming as a review finding if you're doing a
blind review of this repo.

## 5. Minimum tests

- Payments unit test: confirm `MeetingFee`'s expire-path raises `MeetingFeeExpiredDomainEvent` with
  correct `PayerId`/`MeetingId` (mirror however the existing `Paid` path is tested — check
  `src/Modules/Payments/Tests/UnitTests/` for the sibling test's shape before writing this one).
- Meetings unit test for the new `MeetingFeeExpiredIntegrationEventHandler`: `NSubstitute` a fake
  `ICommandsScheduler`, assert `EnqueueAsync` was called once with a `RemoveMeetingAttendeeCommand`
  carrying the right `MeetingId`/attendee id — same shape as
  `src/Modules/Meetings/Tests/UnitTests/Meetings/MeetingTermCommandHandlerTests.cs`'s use of
  `NSubstitute.Arg.Do<T>` to capture the constructed object.
- One integration test through the actual outbox→bus→inbox path is nice-to-have but not minimum —
  the unit tests above already prove both translation points independently, and
  `navigation/03-*.md`/`04-*.md` already establish that the plumbing itself is uniform across event
  types (you're not testing new infrastructure, just a new event + handler pair riding the existing
  rails).

## 6. What NOT to change

- **Don't touch `ArchTests`.** The new files fit the existing carve-outs
  (`IntegrationEventHandler`-suffixed class, published from the module's `IntegrationEvents`
  project) without any rule change — if you find yourself wanting to edit `ModuleTests.cs`, that's
  a signal you've put a file in the wrong place.
- **Don't touch the outbox/inbox job infrastructure** (`ProcessOutboxJob`, `ProcessInboxJob`,
  `IntegrationEventGenericHandler<T>`) — it's generic over `IntegrationEvent`/`T`, already handles
  any new event type without modification, per `navigation/04-*.md`.
- **Don't "fix" the duplicate-delivery gap** documented in `04-outbox-inbox-processing.md` as part
  of this change — it's a real latent issue but out of scope for a single feature PR; naming it in
  the PR description as a known, pre-existing risk this change inherits is the right call, not
  silently fixing unrelated infrastructure in a feature PR.
