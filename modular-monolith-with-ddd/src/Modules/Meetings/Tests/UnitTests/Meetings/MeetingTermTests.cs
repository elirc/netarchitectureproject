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
