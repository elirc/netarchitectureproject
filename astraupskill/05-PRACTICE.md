# Predict the boundary and the side effects

Exercise one: supply a command whose start is October first at nine and whose end is eleven. Trace the two values through the create handler and MeetingTerm factory. Identify the assertion that would fail if a developer accidentally restored the old start/start mapping. Explain why checking only the returned meeting identifier would be insufficient.

Exercise two: change the end to nine, then to eight fifty-nine. Predict the exception type, broken rule, and number of repository additions for each request. Locate the point at which execution stops. Keep your explanation about the handler's repository call separate from any assumption about a database transaction.

Exercise three: create a valid meeting, then attempt to change it to a zero-duration interval. Predict the aggregate's stored term after the exception. Explain how argument evaluation before ChangeMainAttributes makes this possible. What additional assertions would be needed before claiming every other attribute also remains unchanged?

Exercise four: move validation from the value object into only the create handler. List the entry points that would no longer receive that protection. Then restore shared validation and remove the handler mapping corrections. Explain why valid requests would fail despite the invariant being correct.

Exercise five: review the reflection helper. Find how it locates the application type, supplies constructor dependencies, invokes Handle, and awaits the result. Propose a clear failure message for a future handler rename without changing production accessibility.

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
