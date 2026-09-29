# Command flow, file by file: POST a meeting

Trigger: `POST api/meetings/meetings` — create a meeting inside a meeting group.

## 1. HTTP entry — the controller does nothing but map and delegate

`src/API/CompanyName.MyMeetings.API/Modules/Meetings/Meetings/MeetingsController.cs:55-70`
```csharp
[HttpPost("")]
public async Task<IActionResult> CreateNewMeeting([FromBody] CreateMeetingRequest request)
{
    await _meetingsModule.ExecuteCommandAsync(new CreateMeetingCommand(
        request.MeetingGroupId, request.Title, request.TermStartDate, request.TermEndDate,
        request.Description, request.MeetingLocationName, /* ... */));
```
The controller depends only on `IMeetingsModule` (`Application.Contracts`) — the module's public
seam. It never touches `MeetingsContext` or any domain type directly.

## 2. Module facade — crosses into the module's own DI scope

`src/Modules/Meetings/Infrastructure/MeetingsModule.cs`
```csharp
public async Task ExecuteCommandAsync(ICommand command) => await CommandsExecutor.Execute(command);
```
`src/Modules/Meetings/Infrastructure/Configuration/Processing/CommandsExecutor.cs`
```csharp
internal static async Task Execute(ICommand command)
{
    using var scope = MeetingsCompositionRoot.BeginLifetimeScope();
    var mediator = scope.Resolve<IMediator>();
    await mediator.Send(command);
}
```
Every command execution opens its own Autofac lifetime scope (`MeetingsCompositionRoot`) — this is
where a unit-of-work / `DbContext` per request gets created, independent of ASP.NET's own DI scope.

## 3. MediatR pipeline — three stacked decorators, innermost-out

`ICommandHandler<CreateMeetingCommand>` for a command *without* a result (this one is
`ICommandHandler<CreateMeetingCommand, Guid>` — the with-result variant) is wrapped, at Autofac
registration time, as:
`ValidationCommandHandlerWithResultDecorator` → `LoggingCommandHandlerWithResultDecorator` →
`UnitOfWorkCommandHandlerWithResultDecorator` → `CreateMeetingCommandHandler` (actual handler is
innermost; decorators wrap outward, so Validation runs first).

- `ValidationCommandHandlerWithResultDecorator.cs` — runs all `IValidator<CreateMeetingCommand>`
  (FluentValidation) and throws `InvalidCommandException` before the real handler ever runs.
- `UnitOfWorkCommandHandlerWithResultDecorator.cs` — runs the decorated handler **first**, then
  calls `_unitOfWork.CommitAsync()`. This means `CreateMeetingCommandHandler` itself never calls
  `SaveChanges` — the transaction boundary is a cross-cutting decorator, not something each handler
  remembers to do. (It also has special handling for `InternalCommandBase<TResult>` — see
  `navigation/04-outbox-inbox-processing.md`.)

## 4. The actual handler — pure orchestration, no I/O beyond two repo calls

`src/Modules/Meetings/Application/Meetings/CreateMeeting/CreateMeetingCommandHandler.cs:39-60`
```csharp
public async Task<Guid> Handle(CreateMeetingCommand request, CancellationToken cancellationToken)
{
    var meetingGroup = await _meetingGroupRepository.GetByIdAsync(new MeetingGroupId(request.MeetingGroupId));
    var hostsMembersIds = request.HostMemberIds.Select(x => new MemberId(x)).ToList();

    var meeting = meetingGroup.CreateMeeting(
        request.Title,
        MeetingTerm.CreateNewBetweenDates(request.TermStartDate, request.TermEndDate),
        request.Description, MeetingLocation.CreateNew(/* ... */),
        request.AttendeesLimit, request.GuestsLimit,
        Term.CreateNewBetweenDates(request.RSVPTermStartDate, request.RSVPTermEndDate),
        request.EventFeeValue.HasValue ? MoneyValue.Of(...) : MoneyValue.Undefined,
        hostsMembersIds, _memberContext.MemberId);

    await _meetingRepository.AddAsync(meeting);
    return meeting.Id.Value;
}
```
Note: the *aggregate root that creates the meeting is `MeetingGroup`*, not `Meeting` directly —
`meetingGroup.CreateMeeting(...)` is a factory method on the group, consistent with "a meeting
cannot exist without its group" as an invariant. `MeetingTerm.CreateNewBetweenDates` is where the
6-file dirty working-tree change (start/end date mapping) lives — not touched by this pack; see
`training/README.md`.

## 5. Repository — thin EF Core wrapper, no `SaveChanges`

`src/Modules/Meetings/Infrastructure/Domain/Meetings/MeetingRepository.cs`
```csharp
public async Task AddAsync(Meeting meeting) => await _meetingsContext.Meetings.AddAsync(meeting);
```
Just stages the entity with EF Core's change tracker. The actual `INSERT` happens later, when step
3's `UnitOfWorkCommandHandlerWithResultDecorator` commits — confirming the transaction boundary is
"one command = one unit of work," not "one repository call = one write."

## 6. What happens after the commit (teed off, not blocking the HTTP response)

`Meeting.CreateMeeting`-family aggregate operations raise domain events (e.g.
`MeetingAttendeeAddedDomainEvent`, not relevant to *creation* but the same mechanism). After the
decorator commits, nothing in this specific flow raises an outbox message — `CreateMeeting` itself
has no domain event in this codebase (verify: `grep -rl DomainEvent src/Modules/Meetings/Domain/Meetings` finds
events for attendee-add/remove/role-change, not creation). Contrast this with the attendee-add flow
traced in `navigation/03-integration-event-flow-meeting-attendee-added.md`, which *does* fan out
across modules via the outbox.

## Reading order for this trace
1. `MeetingsController.cs` (HTTP → command)
2. `MeetingsModule.cs` + `CommandsExecutor.cs` (module boundary crossing, DI scope)
3. `ValidationCommandHandlerWithResultDecorator.cs`, `UnitOfWorkCommandHandlerWithResultDecorator.cs` (pipeline)
4. `CreateMeetingCommandHandler.cs` (business logic — delegates to the aggregate)
5. `MeetingGroup.cs` → `Meeting.cs` → `MeetingTerm.cs` (domain invariants)
6. `MeetingRepository.cs` (persistence — stage only, no commit)
