# An interval must have positive duration

The invariant is end greater than start. Equal boundaries describe zero duration and are rejected; reversed boundaries are rejected for the same reason. A positive interval preserves the exact dates supplied by the caller. This change does not normalize time zones, round minutes, impose a maximum duration, or alter RSVP timing.

A value object is a useful place for this rule because every ordinary factory caller receives the same validation. The factory cannot return an invalid MeetingTerm and hope that a later handler remembers to check it. The established CheckRule mechanism throws BusinessRuleValidationException with the broken rule attached, keeping the failure consistent with other domain invariants.

Parameter mapping remains a separate concern. Passing start twice produces an invalid term even when the original command contains a valid end. Adding validation without correcting that mapping would turn valid create and change requests into errors. Correcting mapping without validation would still permit other callers to supply nonpositive intervals.

Consider a request starting at nine with an end at twelve. The handler must preserve twelve, and the value object must accept it. Now replace twelve with nine: construction must fail before repository addition or aggregate mutation. These two examples explain why both the mapping tests and the boundary tests are necessary. Read the assertions below and identify which responsibility each assertion protects.

## Source excerpt

From [modular-monolith-with-ddd/src/Modules/Meetings/Tests/UnitTests/Meetings/MeetingTermTests.cs](../modular-monolith-with-ddd/src/Modules/Meetings/Tests/UnitTests/Meetings/MeetingTermTests.cs).

```cs
using CompanyName.MyMeetings.BuildingBlocks.Domain;
using CompanyName.MyMeetings.Modules.Meetings.Domain.Meetings;
using CompanyName.MyMeetings.Modules.Meetings.Domain.Meetings.Rules;
using FluentAssertions;
using NUnit.Framework;

namespace CompanyName.MyMeetings.Modules.Meetings.Domain.UnitTests.Meetings
{
    [TestFixture]
    public class MeetingTermTests
    {
        [Test]
        public void CreateNewBetweenDates_WithPositiveDuration_PreservesBothBoundaries()
        {
            var start = new DateTime(2026, 10, 1, 9, 0, 0, DateTimeKind.Utc);
            var end = start.AddHours(2);

            var term = MeetingTerm.CreateNewBetweenDates(start, end);

            term.StartDate.Should().Be(start);
            term.EndDate.Should().Be(end);
        }

        [TestCase(0)]
        [TestCase(-1)]
        public void CreateNewBetweenDates_WithoutPositiveDuration_BreaksRule(int endOffsetMinutes)
        {
            var start = new DateTime(2026, 10, 1, 9, 0, 0, DateTimeKind.Utc);

            var exception = Assert.Throws<BusinessRuleValidationException>(() =>
                MeetingTerm.CreateNewBetweenDates(start, start.AddMinutes(endOffsetMinutes)));

            exception.BrokenRule.Should().BeOfType<MeetingTermMustEndAfterStartRule>();
        }
    }
}
```

## Course navigation

[README](README.md) / [01-CODEBASE-MAP](01-CODEBASE-MAP.md) / [02-CONCEPTS](02-CONCEPTS.md) / [03-WORKED-CHANGE](03-WORKED-CHANGE.md) / [04-TESTING-AND-DEBUGGING](04-TESTING-AND-DEBUGGING.md) / [05-PRACTICE](05-PRACTICE.md) / [06-SOLUTIONS-AND-REVIEW](06-SOLUTIONS-AND-REVIEW.md) / [07-TRACE-LAB](07-TRACE-LAB.md) / [VERIFICATION](VERIFICATION.md)
