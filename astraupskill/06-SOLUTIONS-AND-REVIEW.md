# Explain the expected outcomes

The valid create request retains nine and eleven in the captured aggregate. An identifier assertion would only prove that some aggregate was created, so an incorrect duration would stay invisible. Now the trap. With the new rule in place, restoring the old start/start mapping does **not** fail on the end-date assertion. `MeetingTerm` throws `BusinessRuleValidationException` inside `Handle`, so the test fails with an unexpected exception before any assertion runs. The end-date assertion is the backstop for a world where someone also deletes the rule, which is exactly the original code (see `snapshots/…MeetingTerm.cs.original.txt`, which has no `CheckRule`). Two layers mean two different failure signatures, and a reviewer should be able to predict both.

Both equal and reversed ends break MeetingTermMustEndAfterStartRule and surface as BusinessRuleValidationException. No repository addition occurs because constructing the value object fails before group creation and AddAsync. This is an ordering guarantee within the tested handler, not evidence that a database rolled back a previously issued write.

The failed change retains the original term. The new MeetingTerm must be evaluated before the aggregate method can be invoked, and that evaluation throws. The regression explicitly inspects the dates; it should not be summarized as comprehensive verification of every meeting property or every exceptional path.

Validation only in creation would miss modification and other factory callers. In production code that means the change handler (`ChangeMeetingMainAttributesCommandHandler.cs:24`), because the two handlers are the only production callers. There is a less visible path too: EF Core loads the owned `_term` (`Infrastructure/Domain/Meetings/MeetingEntityTypeConfiguration.cs:28-32`), and `MeetingTerm` has only the private two-argument constructor. Whether EF binds to that constructor, and therefore whether a zero-duration row written by the old buggy handlers would now *fail to load*, is a runtime question. These unit tests do not answer it. [Extended chapter 14](advanced/extended-course/14-PERSISTENCE-MAPPINGS-AND-MATERIALIZATION.md) shows how to settle it with a historical-data test instead of guessing. Validation without the mapping fixes would reject valid requests because the handlers would still construct equal start and end values. The two changes therefore address different defects and need complementary tests.

The reflection helper loads the internal handler type from the application assembly with `GetType(typeName, throwOnError: true)` and builds it with `Activator.CreateInstance` using `NonPublic` binding flags (the create handler's constructor is `internal`). It then calls `GetMethod("Handle").Invoke(...)` and awaits the returned task. Because both `Handle` methods are `async`, a business-rule exception is stored in the task instead of being thrown from `Invoke`. That is why awaiting matters, and why you see the real `BusinessRuleValidationException` rather than a `TargetInvocationException` wrapper. For Exercise 5: a misspelled type name already fails clearly, because `throwOnError: true` produces a `TypeLoadException` that names the type. A renamed method does not. `GetMethod` returns `null`, and you get a bare `NullReferenceException`. A good fix is `type.GetMethod("Handle") ?? throw new InvalidOperationException($"{typeName} has no public Handle method")`, which stays inside the test project. During review, check that no production visibility was widened, that tests invoke real handlers, and that repository substitutes are described accurately. Future persistence tests should use an isolated database and prove their own transactional behavior rather than inheriting that claim from these unit results.

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
