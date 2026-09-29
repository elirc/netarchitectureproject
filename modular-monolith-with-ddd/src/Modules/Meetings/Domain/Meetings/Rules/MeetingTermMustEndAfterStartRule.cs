using CompanyName.MyMeetings.BuildingBlocks.Domain;

namespace CompanyName.MyMeetings.Modules.Meetings.Domain.Meetings.Rules
{
    public class MeetingTermMustEndAfterStartRule : IBusinessRule
    {
        private readonly DateTime _startDate;
        private readonly DateTime _endDate;

        public MeetingTermMustEndAfterStartRule(DateTime startDate, DateTime endDate)
        {
            _startDate = startDate;
            _endDate = endDate;
        }

        public bool IsBroken() => _endDate <= _startDate;

        public string Message => "Meeting end date must be after start date";
    }
}
