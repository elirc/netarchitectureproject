# Explain the expected outcomes

The valid create request retains nine and eleven in the captured aggregate. The end-date equality assertion detects the old mapping directly. An identifier assertion would merely prove that some aggregate was created, leaving the incorrect duration invisible.

Both equal and reversed ends break MeetingTermMustEndAfterStartRule and surface as BusinessRuleValidationException. No repository addition occurs because constructing the value object fails before group creation and AddAsync. This is an ordering guarantee within the tested handler, not evidence that a database rolled back a previously issued write.

The failed change retains the original term. The new MeetingTerm must be evaluated before the aggregate method can be invoked, and that evaluation throws. The regression explicitly inspects the dates; it should not be summarized as comprehensive verification of every meeting property or every exceptional path.

Validation only in creation would miss modification and other factory callers. Validation without the mapping fixes would reject valid requests because the handlers would still construct equal start and end values. The two changes therefore address different defects and need complementary tests.

The reflection helper loads the internal handler type from the application assembly and uses its constructor and Handle method. Awaiting the returned task observes asynchronous failures. During review, check that no production visibility was widened, that tests invoke real handlers, and that repository substitutes are described accurately. Future persistence tests should use an isolated database and prove their own transactional behavior rather than inheriting that claim from these unit results.

## Source excerpt

From [modular-monolith-with-ddd/src/Modules/Meetings/Tests/UnitTests/Meetings/MeetingTermCommandHandlerTests.cs](../modular-monolith-with-ddd/src/Modules/Meetings/Tests/UnitTests/Meetings/MeetingTermCommandHandlerTests.cs).

```cs
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
