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
