# Follow a failed modification

Begin with a valid meeting scheduled for tomorrow for one hour. Write down the original start and end from its private term, as the test fixture does. Configure the repository to return this exact aggregate when the handler requests the meeting identifier. Configure the member context with the group owner so authorization is not the cause of failure.

Construct a change command starting three days from now with its end equal to its start. Enter Handle and record the repository lookup. Next, evaluate the arguments intended for ChangeMainAttributes. The MeetingTerm factory delegates to its constructor, which checks the new rule. At this point the comparison detects equality and throws.

Mark the aggregate mutation call as not entered. Observe the rejected task through Assert.ThrowsAsync, then read the original aggregate again. Its dates should still equal the original values. The regression does not need a timing delay because the awaited task defines the completion boundary.

Repeat the trace with an end four hours after the requested start. Construction succeeds, the aggregate method runs, and the new interval is retained. Finally, deliberately substitute TermStartDate for TermEndDate in a disposable copy and predict the valid-change test failure. This mutation demonstrates why the handler assertion protects the original bug rather than merely restating the new rule. Restore the correct mapping before accepting any evidence or packaging the project.

## Source excerpt

From [modular-monolith-with-ddd/src/Modules/Meetings/Tests/UnitTests/Meetings/MeetingTermCommandHandlerTests.cs](../modular-monolith-with-ddd/src/Modules/Meetings/Tests/UnitTests/Meetings/MeetingTermCommandHandlerTests.cs).

```cs
        public void ChangeMeeting_InvalidDuration_PreservesExistingTerm()
        {
            var fixture = CreateFixture();
            var originalStart = DateTime.UtcNow.AddDays(1);
            var originalEnd = originalStart.AddHours(1);
            var meeting = fixture.Group.CreateMeeting(
                "Original",
                MeetingTerm.CreateNewBetweenDates(originalStart, originalEnd),
                "Description",
                MeetingLocation.CreateNew("Room", "Street", "00-001", "City"),
                null,
                0,
                Term.NoTerm,
                MoneyValue.Undefined,
                [],
                fixture.MemberId);
            fixture.MeetingRepository.GetByIdAsync(Arg.Any<MeetingId>()).Returns(Task.FromResult(meeting));
            var changedStart = DateTime.UtcNow.AddDays(3);

            Assert.ThrowsAsync<BusinessRuleValidationException>(async () => await InvokeHandler<ChangeMeetingMainAttributesCommand>(
                "CompanyName.MyMeetings.Modules.Meetings.Application.Meetings.ChangeMeetingMainAttributes.ChangeMeetingMainAttributesCommandHandler",
                [fixture.MemberContext, fixture.MeetingRepository],
                ChangeCommand(meeting.Id.Value, changedStart, changedStart)));

            GetTerm(meeting).StartDate.Should().Be(originalStart);
            GetTerm(meeting).EndDate.Should().Be(originalEnd);
        }

        private static Fixture CreateFixture()
        {
            var memberId = new MemberId(Guid.NewGuid());
            var proposal = MeetingGroupProposal.ProposeNew("Group", "Description", MeetingGroupLocation.CreateNew("City", "PL"), memberId);
            proposal.Accept();
            var group = proposal.CreateMeetingGroup();
            group.SetExpirationDate(DateTime.UtcNow.AddYears(1));
            var groupRepository = Substitute.For<IMeetingGroupRepository>();
            groupRepository.GetByIdAsync(Arg.Any<MeetingGroupId>()).Returns(Task.FromResult(group));
            var meetingRepository = Substitute.For<IMeetingRepository>();
            var memberContext = Substitute.For<IMemberContext>();
            memberContext.MemberId.Returns(memberId);
```

## Course navigation

[README](README.md) / [01-CODEBASE-MAP](01-CODEBASE-MAP.md) / [02-CONCEPTS](02-CONCEPTS.md) / [03-WORKED-CHANGE](03-WORKED-CHANGE.md) / [04-TESTING-AND-DEBUGGING](04-TESTING-AND-DEBUGGING.md) / [05-PRACTICE](05-PRACTICE.md) / [06-SOLUTIONS-AND-REVIEW](06-SOLUTIONS-AND-REVIEW.md) / [07-TRACE-LAB](07-TRACE-LAB.md) / [VERIFICATION](VERIFICATION.md)
