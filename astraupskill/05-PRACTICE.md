# Predict the boundary and the side effects

Every exercise below is a prediction you write down first and then confirm. Run the commands from `modular-monolith-with-ddd/src` in a disposable branch or copy, and restore every edit with `git checkout -- .` when you finish. `Modules/Meetings/Tests/UnitTests/CompanyName.MyMeetings.Modules.Meetings.Domain.UnitTests.csproj` is abbreviated as `<UnitTests.csproj>`.

## Exercise 1 - Trace a valid create

**Goal.** Supply a command whose start is October 1 at 09:00 and whose end is 11:00. Trace the two values through `CreateMeetingCommandHandler.Handle` (line 32) and `MeetingTerm.CreateNewBetweenDates` (`Domain/Meetings/MeetingTerm.cs:13-23`). Explain why checking only the returned meeting identifier would be insufficient. Then predict exactly *how* `CreateMeeting_MapsRequestedEndDateIntoAddedAggregate` fails if the handler goes back to the old `(TermStartDate, TermStartDate)` mapping. Is it an assertion failure or an exception?

**Check.** Make that one-argument edit in `Application/Meetings/CreateMeeting/CreateMeetingCommandHandler.cs:32`, run `dotnet test <UnitTests.csproj> --filter "FullyQualifiedName~MeetingTermCommandHandlerTests"`, and read the failure message. Then restore the line.

## Exercise 2 - Equal and reversed ends

**Goal.** Change the end to 09:00, then to 08:59. For each request, predict the exception type, the broken rule, the number of `AddAsync` calls and the line where execution stops. Keep the handler's repository call separate from any assumption about a database transaction.

**Check.** These are exactly the two cases of `CreateMeeting_InvalidDuration_DoesNotAddAggregate` (offsets `0` and `-1`) and of `CreateNewBetweenDates_WithoutPositiveDuration_BreaksRule`. Run `--filter "FullyQualifiedName~InvalidDuration|FullyQualifiedName~WithoutPositiveDuration"` and expect 4 passing cases.

## Exercise 3 - A rejected change leaves the aggregate alone

**Goal.** Create a valid meeting, then try to change it to a zero-duration interval. Predict the aggregate's stored term after the exception. Explain how evaluating the arguments before `ChangeMainAttributes` is entered makes this guarantee possible. Which additional assertions would you need before claiming that *every other* attribute is unchanged too?

**Check.** `ChangeMeeting_InvalidDuration_PreservesExistingTerm` asserts only the two dates. Add assertions for one more field (the title is a private field read the same way `GetTerm` reads `_term`) and run the handler-test filter.

## Exercise 4 - Validation in the wrong layer

**Goal.** Suppose validation moved from the value object into the create handler only. List the entry points that would lose protection. Production code has exactly two callers of `MeetingTerm.CreateNewBetweenDates` (the two handlers). The existing test fixtures that build meetings are callers too. Next, suppose shared validation stays but the mapping corrections are removed. Explain why valid requests would now fail even though the invariant is correct.

**Check.** Confirm the caller list yourself with a scoped search: `git grep -n "MeetingTerm.CreateNewBetweenDates" -- "modular-monolith-with-ddd/src/Modules/Meetings"`. For the second half, revert both handler lines and run the handler-test filter. Expect 2 failures: the two mapping tests. The three invalid-duration cases still pass, because they were designed to throw anyway.

## Exercise 5 - Review the reflection helper

**Goal.** In `MeetingTermCommandHandlerTests.cs`, find how `InvokeHandler` locates the internal type, supplies constructor dependencies, invokes `Handle` and awaits the result. Propose a clear failure message for a future handler rename or signature change, without changing production accessibility.

**Check.** Change one character of a handler type-name string and run the filter. Note which exception you get and whether it names the type. Then rename `"Handle"` to `"Handl"` in one `GetMethod` call and compare. Restore both. Compare your conclusions with [06](06-SOLUTIONS-AND-REVIEW.md).

## Source excerpt

From [modular-monolith-with-ddd/src/Modules/Meetings/Tests/UnitTests/Meetings/MeetingTermCommandHandlerTests.cs](../modular-monolith-with-ddd/src/Modules/Meetings/Tests/UnitTests/Meetings/MeetingTermCommandHandlerTests.cs).

```cs
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

        [Test]
        public async Task ChangeMeeting_MapsRequestedEndDateIntoExistingAggregate()
        {
            var fixture = CreateFixture();
            var original = fixture.Group.CreateMeeting(
                "Original",
                MeetingTerm.CreateNewBetweenDates(DateTime.UtcNow.AddDays(1), DateTime.UtcNow.AddDays(1).AddHours(1)),
                "Description",
                MeetingLocation.CreateNew("Room", "Street", "00-001", "City"),
                null,
                0,
                Term.NoTerm,
                MoneyValue.Undefined,
                [],
                fixture.MemberId);
            fixture.MeetingRepository.GetByIdAsync(Arg.Any<MeetingId>()).Returns(Task.FromResult(original));
            var start = DateTime.UtcNow.AddDays(3);
            var end = start.AddHours(4);

            await InvokeHandler<ChangeMeetingMainAttributesCommand>(
                "CompanyName.MyMeetings.Modules.Meetings.Application.Meetings.ChangeMeetingMainAttributes.ChangeMeetingMainAttributesCommandHandler",
                [fixture.MemberContext, fixture.MeetingRepository],
                ChangeCommand(original.Id.Value, start, end));

            GetTerm(original).StartDate.Should().Be(start);
            GetTerm(original).EndDate.Should().Be(end);
        }

        [Test]
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
```

## Course navigation

[README](README.md) / [01-CODEBASE-MAP](01-CODEBASE-MAP.md) / [02-CONCEPTS](02-CONCEPTS.md) / [03-WORKED-CHANGE](03-WORKED-CHANGE.md) / [04-TESTING-AND-DEBUGGING](04-TESTING-AND-DEBUGGING.md) / [05-PRACTICE](05-PRACTICE.md) / [06-SOLUTIONS-AND-REVIEW](06-SOLUTIONS-AND-REVIEW.md) / [07-TRACE-LAB](07-TRACE-LAB.md) / [VERIFICATION](VERIFICATION.md)
