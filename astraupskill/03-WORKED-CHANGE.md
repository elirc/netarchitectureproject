# Correct creation and modification together

The create handler now constructs MeetingTerm from request.TermStartDate and request.TermEndDate before calling the meeting group's creation method. The repository add occurs only after domain construction succeeds. Its regression captures the aggregate passed to AddAsync and inspects the retained start and end, so a mere successful handler return cannot hide a mapping error.

The change handler receives the same argument correction. It evaluates the new MeetingTerm before invoking ChangeMainAttributes. If interval construction throws, the aggregate mutation method is never entered. The invalid-change regression confirms the original term remains present after the failed command.

The new business rule is intentionally small: the end must be strictly after the start. It uses the existing domain validation pattern instead of adding a parallel exception type or application-only conditional. Existing meeting authorization, group availability, RSVP term, fee, and attendee rules remain responsible for their own decisions.

The tests invoke internal handlers through reflection because the repository's architecture keeps module internals hidden. They do not add InternalsVisibleTo or expose a production handler merely to make testing convenient. Reflection is confined to the test fixture; the invoked Handle method is the real implementation. This preserves the module boundary while still detecting the original application mapping defect at its actual call site.

## Source excerpt

From [modular-monolith-with-ddd/src/Modules/Meetings/Application/Meetings/ChangeMeetingMainAttributes/ChangeMeetingMainAttributesCommandHandler.cs](../modular-monolith-with-ddd/src/Modules/Meetings/Application/Meetings/ChangeMeetingMainAttributes/ChangeMeetingMainAttributesCommandHandler.cs).

```cs
﻿using CompanyName.MyMeetings.Modules.Meetings.Application.Configuration.Commands;
using CompanyName.MyMeetings.Modules.Meetings.Domain.Meetings;
using CompanyName.MyMeetings.Modules.Meetings.Domain.Members;

namespace CompanyName.MyMeetings.Modules.Meetings.Application.Meetings.ChangeMeetingMainAttributes
{
    internal class ChangeMeetingMainAttributesCommandHandler : ICommandHandler<ChangeMeetingMainAttributesCommand>
    {
        private readonly IMemberContext _memberContext;
        private readonly IMeetingRepository _meetingRepository;

        public ChangeMeetingMainAttributesCommandHandler(IMemberContext memberContext, IMeetingRepository meetingRepository)
        {
            _memberContext = memberContext;
            _meetingRepository = meetingRepository;
        }

        public async Task Handle(ChangeMeetingMainAttributesCommand request, CancellationToken cancellationToken)
        {
            var meeting = await _meetingRepository.GetByIdAsync(new MeetingId(request.MeetingId));

            meeting.ChangeMainAttributes(
                request.Title,
                MeetingTerm.CreateNewBetweenDates(request.TermStartDate, request.TermEndDate),
                request.Description,
                MeetingLocation.CreateNew(request.MeetingLocationName, request.MeetingLocationAddress, request.MeetingLocationPostalCode, request.MeetingLocationCity),
                MeetingLimits.Create(request.AttendeesLimit, request.GuestsLimit),
                Term.CreateNewBetweenDates(request.RSVPTermStartDate, request.RSVPTermEndDate),
                request.EventFeeValue.HasValue ? MoneyValue.Of(request.EventFeeValue.Value, request.EventFeeCurrency) : MoneyValue.Undefined,
                _memberContext.MemberId);
        }
    }
}
```

## Course navigation

[README](README.md) / [01-CODEBASE-MAP](01-CODEBASE-MAP.md) / [02-CONCEPTS](02-CONCEPTS.md) / [03-WORKED-CHANGE](03-WORKED-CHANGE.md) / [04-TESTING-AND-DEBUGGING](04-TESTING-AND-DEBUGGING.md) / [05-PRACTICE](05-PRACTICE.md) / [06-SOLUTIONS-AND-REVIEW](06-SOLUTIONS-AND-REVIEW.md) / [07-TRACE-LAB](07-TRACE-LAB.md) / [VERIFICATION](VERIFICATION.md)
