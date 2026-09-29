# Exercise actual handlers with controlled repositories

The fixture builds an accepted meeting group owned by the current member. Its repositories return known aggregates, and its member context supplies the matching identifier. These arrangements satisfy unrelated business prerequisites so the assertions focus on interval mapping and rejection. They are not database adapters and should not be described as persistence integration coverage.

The create success case captures the object supplied to AddAsync and checks both boundaries. Two invalid-create cases use equal and reversed ends, expect BusinessRuleValidationException, and verify AddAsync was not called. This establishes that rejection happens before the handler publishes an aggregate to its repository.

The change success case begins with an existing meeting and checks that a new, longer interval reaches it. The invalid-change case retains the original dates and verifies they survive the failed attempt. That assertion concerns in-memory aggregate mutation, not SQL rollback.

When a test fails during setup, inspect group ownership and expiration before changing the interval rule. When reflection reports a missing type or method, compare the helper's fully qualified handler name with the application assembly. Await the returned Task so asynchronous domain exceptions are observed. The recorded successful command builds the relevant project references and runs the unit test assembly; earlier style failures remain separate failed attempts in the campaign history.

## Source excerpt

From [modular-monolith-with-ddd/src/Modules/Meetings/Tests/UnitTests/Meetings/MeetingTermCommandHandlerTests.cs](../modular-monolith-with-ddd/src/Modules/Meetings/Tests/UnitTests/Meetings/MeetingTermCommandHandlerTests.cs).

```cs
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
            return new Fixture(memberId, group, memberContext, groupRepository, meetingRepository);
        }

        private static CreateMeetingCommand CreateCommand(Guid groupId, DateTime start, DateTime end) =>
            new(groupId, "Meeting", start, end, "Description", "Room", "Street", "00-001", "City", null, 0, null, null, null, null, []);

        private static ChangeMeetingMainAttributesCommand ChangeCommand(Guid meetingId, DateTime start, DateTime end) =>
            new(meetingId, "Changed", start, end, "Description", "Room", "Street", "00-001", "City", null, 0, null, null, null, null);

        private static MeetingTerm GetTerm(Meeting meeting) =>
            (MeetingTerm)typeof(Meeting).GetField("_term", BindingFlags.Instance | BindingFlags.NonPublic).GetValue(meeting);

        private static async Task<TResult> InvokeHandler<TCommand, TResult>(string typeName, object[] constructorArgs, TCommand command)
        {
            var type = typeof(CreateMeetingCommand).Assembly.GetType(typeName, throwOnError: true);
            var handler = Activator.CreateInstance(type, BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic, null, constructorArgs, null);
            var task = (Task<TResult>)type.GetMethod("Handle").Invoke(handler, [command, CancellationToken.None]);
            return await task;
        }

        private static async Task InvokeHandler<TCommand>(string typeName, object[] constructorArgs, TCommand command)
        {
            var type = typeof(CreateMeetingCommand).Assembly.GetType(typeName, throwOnError: true);
            var handler = Activator.CreateInstance(type, BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic, null, constructorArgs, null);
            var task = (Task)type.GetMethod("Handle").Invoke(handler, [command, CancellationToken.None]);
            await task;
        }

        private sealed record Fixture(
            MemberId MemberId,
            MeetingGroup Group,
            IMemberContext MemberContext,
            IMeetingGroupRepository GroupRepository,
            IMeetingRepository MeetingRepository);
    }
}
```

## Course navigation

[README](README.md) / [01-CODEBASE-MAP](01-CODEBASE-MAP.md) / [02-CONCEPTS](02-CONCEPTS.md) / [03-WORKED-CHANGE](03-WORKED-CHANGE.md) / [04-TESTING-AND-DEBUGGING](04-TESTING-AND-DEBUGGING.md) / [05-PRACTICE](05-PRACTICE.md) / [06-SOLUTIONS-AND-REVIEW](06-SOLUTIONS-AND-REVIEW.md) / [07-TRACE-LAB](07-TRACE-LAB.md) / [VERIFICATION](VERIFICATION.md)
