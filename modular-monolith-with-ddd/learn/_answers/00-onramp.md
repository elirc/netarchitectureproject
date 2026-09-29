# SEALED — attempt `learn/00-onramp.md` first

## 1.
`IsBroken() = limit.HasValue && limit < active + 1 + guests`
- a) `null` → **false** (no limit, so the rule short-circuits).
- b) 10 < 8+1+1 = 10 → **false** (exactly at the limit is allowed).
- c) 10 < 11 → **true** (broken).
- d) 5 < 4+1+0 = 5 → **false**.
The `+ 1` is the new member themself. `guestsNumber` counts only their guests. The test comment says the creator counts
because `Meeting.cs:124` adds the creator as a `Host` attendee when no host list is given. With limit 5, that's creator (1) +
member with 3 guests (4) = 5 = full, so the next member breaks the rule (5 < 5+1+0).

## 2.
- a) `(1 + 2) * 10 EUR = 30 EUR` (`MeetingAttendee.cs:73`, via `operator *` at `MoneyValue.cs:24-27`).
- b) `ValueObject` overrides `==`/`!=` (`ValueObject.cs:11-29`) to call `Equals`, which compares every property and field by
  value (`:36-45`). Two separate `Undefined` instances are equal because both have `Value = null, Currency = null`.
- c) With reference equality, `!=` would always be true, so the code would compute `(1+g) * Undefined`. That's
  `new MoneyValue(null * n, null)`, and `null * n` is `null` for `decimal?`. The result is a value that *looks exactly like*
  `Undefined`. Nobody would notice. The lesson: a wrong comparison can be masked by null-propagating arithmetic, and a bug can
  sit silently until someone changes the arithmetic. Tests that only check the output wouldn't see it. Only reading the code would.

## 3.
- a) Both `StartDate` and `EndDate` are 18:00. HEAD passes `request.TermStartDate` twice.
- b) No. HEAD has no end-after-start rule. `MeetingTermMustEndAfterStartRule.cs` exists only as the user's untracked WIP.
- c) `MeetingTestsBase` builds `MeetingTerm.CreateNewBetweenDates(...)` directly and calls `meetingGroup.CreateMeeting`,
  bypassing the command handler. No committed unit test goes through `CreateMeetingCommandHandler`, so the mapping line is
  never executed by a test. Green tests prove nothing about lines they don't run
  ([05](../../../../opusorganize/apprenticeship/curriculum/05-verify-before-trust.md)).
- d) `ChangeMeetingMainAttributesCommandHandler.cs` (around line 32 of HEAD's version). Same bug. The user's uncommitted diff
  and `Desktop\.netarchitectureproject\astraupskill\` fix both.

## 4.
`BusinessRuleValidationException` (with `BrokenRule` set), asserted by `TestBase.AssertBrokenRule<TRule>`. A new rule
implements `IBusinessRule`: `bool IsBroken()` and `string Message`.

## 5.
- a) handler `Handle` → (`CommitAsync`) → `_mediator.Publish(domainEvent)` for each event → `_outbox.Add(...)` for each
  notification → `SaveChangesAsync`.
- b) Neither is saved. The exception propagates out of `DispatchEventsAsync` before `SaveChangesAsync` (`UnitOfWork.cs:23-25`),
  and the whole command fails. In-process handlers are effectively *inside* the unit of work, so a failing email handler blocks
  the business write. That's worth a review comment: it's a coupling trade-off, not a bug.
- c) `domainEventNotification.Id`, which was built from `domainEvent.Id` (`DomainEventsDispatcher.cs:50`). It's stable. The
  outbox row keeps the *domain* event's Id. The new-Guid problem appears one hop later (see FD1).

## 6.
- a) The message was received but not processed yet. It's pending.
- b) `SELECT [Type], COUNT(*) AS Pending, MIN(OccurredOn) AS Oldest FROM [payments].[InboxMessages] WHERE ProcessedDate IS NULL GROUP BY [Type] ORDER BY Oldest;`
- c) Only `PK_payments_InboxMessages_Id` on `[Id]`. It deduplicates **identical Ids**, not identical business content.
- d) `WITH (UPDLOCK, READPAST, ROWLOCK)` on the `SELECT` inside a transaction, or an atomic `UPDATE ... OUTPUT` that sets a
  claim column. This is SQL Server's version of Postgres `FOR UPDATE SKIP LOCKED`
  ([22 SQL Server for Postgres devs](../../../../opusorganize/apprenticeship/curriculum/22-sqlserver-for-postgres-devs.md)).

## 7.
The static `_customDate` would leak into every later test in the same process. Tests that compare against `SystemClock.Now`,
such as "meeting has started" (`MeetingCannotBeChangedAfterStartRule`), would pass or fail depending on which test ran first.
That's order-dependent flakiness, and it usually shows up in CI (different order or parallelism) but not locally.

## 8. Reference test (UNVERIFIED: written for this pass, not compiled. Docs-only pass, SDK 8 absent)
```csharp
[Test]
public void AddNotAttendee_WhenAttendeeDropsOut_PromotesEarliestWaitlistMemberWithZeroGuests()
{
    var creatorId = new MemberId(Guid.NewGuid());
    var data = CreateMeetingTestData(new MeetingTestDataOptions { CreatorId = creatorId });

    var memberB = new MemberId(Guid.NewGuid());
    data.MeetingGroup.JoinToGroupMember(memberB);
    data.Meeting.AddAttendee(data.MeetingGroup, memberB, 0);

    var memberA = new MemberId(Guid.NewGuid());
    data.MeetingGroup.JoinToGroupMember(memberA);
    data.Meeting.SignUpMemberToWaitlist(data.MeetingGroup, memberA);

    data.Meeting.AddNotAttendee(memberB);

    var added = AssertPublishedDomainEvents<MeetingAttendeeAddedDomainEvent>(data.Meeting)
        .Where(e => e.AttendeeId == memberA).ToList();
    added.Should().HaveCount(1);
    added[0].GuestsNumber.Should().Be(0);
}
```
Grading: +1 for going through the aggregate's public methods only. +1 for asserting on the *event*, because
`_attendees` is private. +1 for asserting `GuestsNumber == 0`, the surprising part of the behavior. −1 if you called
`AddAttendee` for A (that tests a different path). If you noticed that promotion skips the attendee-limit rule, that's a good
review question, not a bug to fix here.
