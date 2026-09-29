# Change request exercise

## The request (as a PM would write it)

> "When a member RSVPs to a paid meeting, we create a `MeetingFee` in Payments and give them a
> deadline. Right now, if they never pay and the fee expires, Payments quietly marks the fee
> `Expired` (`MeetingFeeExpiredDomainEvent` in
> `src/Modules/Payments/Domain/MeetingFees/Events/MeetingFeeExpiredDomainEvent.cs`) and nothing else
> happens — the attendee is still shown as attending in Meetings, with no fee paid and no follow-up.
> We want Meetings to automatically move that attendee to a 'payment expired' state (or remove them
> from the attendee list, whichever the existing domain model already supports) when this happens,
> the same way it already reacts to `MeetingFeePaidIntegrationEvent` today."

## Evidence already in the repo confirming this is a real gap, not a hypothetical

- `MeetingFeeExpiredDomainEvent` exists and is applied to the `MeetingFee` aggregate
  (`src/Modules/Payments/Domain/MeetingFees/MeetingFee.cs`), so Payments *does* model expiry.
- There is **no** `MeetingFeeExpiredIntegrationEvent` under `src/Modules/Payments/IntegrationEvents/`
  (only `MeetingFeePaidIntegrationEvent.cs` and `SubscriptionExpirationDateChangedIntegrationEvent.cs`
  exist there today) — confirm this yourself with
  `ls src/Modules/Payments/IntegrationEvents/` before you start.
- Meetings already has the *paid* side of this wired up end-to-end:
  `MeetingFeePaidIntegrationEventHandler.cs` →
  `MarkMeetingAttendeeFeeAsPayedCommand` — your job is to find (or confirm the absence of) its
  natural counterpart for the expired case.

## What you must write down before touching code

Answer these in writing. Don't open `_answers/07-change-request-answer.md` until you have:

1. **Which module needs a new type, and where exactly does it go?** (Which project — `.Domain`,
   `.Application`, or `.IntegrationEvents` — and in which existing folder, following the pattern of
   the `MeetingFeePaid` sibling flow.)
2. **What is the minimum new integration event, and what fields does it need?** (Look at what
   `MeetingFeePaidIntegrationEvent` carries and decide what `Expired` actually needs — is `PayerId`
   + `MeetingId` enough, or do you need more?)
3. **Which existing Meetings command handles "remove/downgrade an attendee," and does one already
   exist you can reuse, or do you need a new one?** (Search
   `src/Modules/Meetings/Application/Meetings/` for anything attendee-removal-shaped before writing
   a new command.)
4. **Where does the translation from domain event → integration event happen for the `Paid` case,
   and is that the right template to copy for `Expired`?** (Hint: it isn't inside `MeetingFee.cs`
   itself — trace where `MeetingFeePaidDomainEvent` actually turns into
   `MeetingFeePaidIntegrationEvent` the same way `navigation/03-*.md` traced
   `MeetingAttendeeAddedDomainEvent` → `MeetingAttendeeAddedIntegrationEvent`.)
5. **What tests prove this works, at minimum?** (One Payments-side unit test that
   `MeetingFee.Create(...).Expire()`-equivalent still raises the domain event correctly; one
   Meetings-side handler test, `NSubstitute`-style like
   `src/Modules/Meetings/Tests/UnitTests/Meetings/MeetingTermCommandHandlerTests.cs`, proving the
   integration event handler enqueues the right command.)
6. **What do you explicitly NOT change?** (Should you touch the outbox/inbox job infrastructure
   itself? Should you touch `ArchTests`? State your answer and why.)

Write your answers, then check `_answers/07-change-request-answer.md`.
