# Preserve the requested meeting interval

A meeting requested from nine until eleven should retain both boundaries. The create and change handlers previously passed the start date twice when constructing MeetingTerm. That mapping silently discarded the requested end. Fixing only a user interface would leave both application entry points capable of constructing the wrong interval.

The repair has two parts. Both handlers now pass TermEndDate as the second argument. The value object also rejects an end equal to or earlier than its start through the repository's business-rule mechanism. This places the invariant at the shared domain boundary, while the handler regressions prove the requested values actually reach that boundary.

Read the codebase map before running the exercises. Concepts explains strict interval ordering; the worked change follows the two argument mappings. Testing shows how the actual internal handlers are invoked without changing their production visibility. Practice asks you to predict repository and aggregate behavior, and the separate solutions explain those predictions.

The accepted run passed ninety-seven unit test cases. Eight of them are new: three in `MeetingTermTests` and five in `MeetingTermCommandHandlerTests` ([how the 97 is made up](VERIFICATION.md#how-the-97-is-made-up)). Repository substitutes keep this check local. It does not establish database transaction rollback, HTTP response formatting, or deployed scheduling behavior. Treat those as separate boundaries when extending the project. The original source snapshots and recorded command evidence accompany this course so the change can be reviewed against the prior implementation.

## Source excerpt

From [modular-monolith-with-ddd/src/Modules/Meetings/Tests/UnitTests/Meetings/MeetingTermCommandHandlerTests.cs](../modular-monolith-with-ddd/src/Modules/Meetings/Tests/UnitTests/Meetings/MeetingTermCommandHandlerTests.cs).

```cs
using System.Reflection;
using CompanyName.MyMeetings.BuildingBlocks.Domain;
using CompanyName.MyMeetings.Modules.Meetings.Application.Meetings.ChangeMeetingMainAttributes;
using CompanyName.MyMeetings.Modules.Meetings.Application.Meetings.CreateMeeting;
using CompanyName.MyMeetings.Modules.Meetings.Domain.MeetingGroupProposals;
using CompanyName.MyMeetings.Modules.Meetings.Domain.MeetingGroups;
using CompanyName.MyMeetings.Modules.Meetings.Domain.Meetings;
using CompanyName.MyMeetings.Modules.Meetings.Domain.Members;
using CompanyName.MyMeetings.Modules.Meetings.Domain.SharedKernel;
using FluentAssertions;
using NSubstitute;
using NUnit.Framework;

namespace CompanyName.MyMeetings.Modules.Meetings.Domain.UnitTests.Meetings
{
    [TestFixture]
    public class MeetingTermCommandHandlerTests
    {
        [Test]
        public async Task CreateMeeting_MapsRequestedEndDateIntoAddedAggregate()
        {
            var fixture = CreateFixture();
            Meeting added = null;
            fixture.MeetingRepository.AddAsync(Arg.Do<Meeting>(meeting => added = meeting)).Returns(Task.CompletedTask);
            var start = DateTime.UtcNow.AddDays(2);
            var end = start.AddHours(3);

            await InvokeHandler<CreateMeetingCommand, Guid>(
                "CompanyName.MyMeetings.Modules.Meetings.Application.Meetings.CreateMeeting.CreateMeetingCommandHandler",
                [fixture.MemberContext, fixture.MeetingRepository, fixture.GroupRepository],
                CreateCommand(fixture.Group.Id.Value, start, end));

            added.Should().NotBeNull();
            GetTerm(added).StartDate.Should().Be(start);
            GetTerm(added).EndDate.Should().Be(end);
        }

        [TestCase(0)]
        [TestCase(-1)]
        public void CreateMeeting_InvalidDuration_DoesNotAddAggregate(int endOffsetMinutes)
        {
            var fixture = CreateFixture();
            var start = DateTime.UtcNow.AddDays(2);

            Assert.ThrowsAsync<BusinessRuleValidationException>(async () => await InvokeHandler<CreateMeetingCommand, Guid>(
                "CompanyName.MyMeetings.Modules.Meetings.Application.Meetings.CreateMeeting.CreateMeetingCommandHandler",
                [fixture.MemberContext, fixture.MeetingRepository, fixture.GroupRepository],
                CreateCommand(fixture.Group.Id.Value, start, start.AddMinutes(endOffsetMinutes))));

            fixture.MeetingRepository.DidNotReceive().AddAsync(Arg.Any<Meeting>());
        }

        // ... ChangeMeeting_MapsRequestedEndDateIntoExistingAggregate, ChangeMeeting_InvalidDuration_PreservesExistingTerm
        // and the reflection helpers follow in the full file.
```

## Course navigation

[README](README.md) / [01-CODEBASE-MAP](01-CODEBASE-MAP.md) / [02-CONCEPTS](02-CONCEPTS.md) / [03-WORKED-CHANGE](03-WORKED-CHANGE.md) / [04-TESTING-AND-DEBUGGING](04-TESTING-AND-DEBUGGING.md) / [05-PRACTICE](05-PRACTICE.md) / [06-SOLUTIONS-AND-REVIEW](06-SOLUTIONS-AND-REVIEW.md) / [07-TRACE-LAB](07-TRACE-LAB.md) / [VERIFICATION](VERIFICATION.md)

## Advanced invariant engineering workshop

[Continue with the advanced pack](advanced/README.md): command-to-aggregate diagrams, strict boundary worksheets, a disposable real-source failure lab, reflection diagnostics, independent domain-rule exercises, separate solutions, and an all-fields rejection rubric.
