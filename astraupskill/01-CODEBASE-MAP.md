# Find the two mapping boundaries

The Meetings application module receives CreateMeetingCommand and ChangeMeetingMainAttributesCommand. Each command carries TermStartDate and TermEndDate. The create handler loads the meeting group, translates host identifiers, constructs domain values, asks the group to create a meeting, and adds that meeting through IMeetingRepository. The change handler loads an existing meeting and calls ChangeMainAttributes with newly constructed values.

MeetingTerm lives in the domain module. Its public factory delegates to a private constructor. The constructor checks MeetingTermMustEndAfterStartRule before assigning either boundary. The rule compares the supplied dates and provides the business-facing error message through IBusinessRule.

The unit test project now covers both levels. MeetingTermTests checks preservation and rejection directly. MeetingTermCommandHandlerTests constructs real aggregates and invokes the actual application handlers with substituted repositories and member context. The fixture accepts a meeting group proposal and sets a future expiration so unrelated group rules do not obscure the interval behavior under test.

When tracing a defect, first inspect the command values, then the factory arguments, then the aggregate's retained term. A successful domain factory test alone cannot detect a handler passing the wrong parameter. Conversely, a handler example with a valid interval does not establish rejection at the shared factory. These tests deliberately cover both responsibilities rather than assuming one layer proves the other.

## Source excerpt

From [modular-monolith-with-ddd/src/Modules/Meetings/Application/Meetings/CreateMeeting/CreateMeetingCommandHandler.cs](../modular-monolith-with-ddd/src/Modules/Meetings/Application/Meetings/CreateMeeting/CreateMeetingCommandHandler.cs).

```cs
﻿using CompanyName.MyMeetings.Modules.Meetings.Application.Configuration.Commands;
using CompanyName.MyMeetings.Modules.Meetings.Domain.MeetingGroups;
using CompanyName.MyMeetings.Modules.Meetings.Domain.Meetings;
using CompanyName.MyMeetings.Modules.Meetings.Domain.Members;

namespace CompanyName.MyMeetings.Modules.Meetings.Application.Meetings.CreateMeeting
{
    internal class CreateMeetingCommandHandler : ICommandHandler<CreateMeetingCommand, Guid>
    {
        private readonly IMemberContext _memberContext;
        private readonly IMeetingRepository _meetingRepository;
        private readonly IMeetingGroupRepository _meetingGroupRepository;

        internal CreateMeetingCommandHandler(
            IMemberContext memberContext,
            IMeetingRepository meetingRepository,
            IMeetingGroupRepository meetingGroupRepository)
        {
            _memberContext = memberContext;
            _meetingRepository = meetingRepository;
            _meetingGroupRepository = meetingGroupRepository;
        }

        public async Task<Guid> Handle(CreateMeetingCommand request, CancellationToken cancellationToken)
        {
            var meetingGroup = await _meetingGroupRepository.GetByIdAsync(new MeetingGroupId(request.MeetingGroupId));

            var hostsMembersIds = request.HostMemberIds.Select(x => new MemberId(x)).ToList();

            var meeting = meetingGroup.CreateMeeting(
                request.Title,
                MeetingTerm.CreateNewBetweenDates(request.TermStartDate, request.TermEndDate),
                request.Description,
                MeetingLocation.CreateNew(request.MeetingLocationName, request.MeetingLocationAddress, request.MeetingLocationPostalCode, request.MeetingLocationCity),
                request.AttendeesLimit,
                request.GuestsLimit,
                Term.CreateNewBetweenDates(request.RSVPTermStartDate, request.RSVPTermEndDate),
                request.EventFeeValue.HasValue ? MoneyValue.Of(request.EventFeeValue.Value, request.EventFeeCurrency) : MoneyValue.Undefined,
                hostsMembersIds,
                _memberContext.MemberId);

            await _meetingRepository.AddAsync(meeting);

            return meeting.Id.Value;
        }
    }
}
```

## Course navigation

[README](README.md) / [01-CODEBASE-MAP](01-CODEBASE-MAP.md) / [02-CONCEPTS](02-CONCEPTS.md) / [03-WORKED-CHANGE](03-WORKED-CHANGE.md) / [04-TESTING-AND-DEBUGGING](04-TESTING-AND-DEBUGGING.md) / [05-PRACTICE](05-PRACTICE.md) / [06-SOLUTIONS-AND-REVIEW](06-SOLUTIONS-AND-REVIEW.md) / [07-TRACE-LAB](07-TRACE-LAB.md) / [VERIFICATION](VERIFICATION.md)
