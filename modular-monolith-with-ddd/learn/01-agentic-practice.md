# Agentic practice: you write the spec, the agent types, you judge

This READ-tier repo has no incident branches. These drills use the real gaps that `training/navigation/` and
`learn/02-fire-drills.md` found. The loop is always the same (the central method is in
[05 Verify before trust](../../../opusorganize/apprenticeship/curriculum/05-verify-before-trust.md)):

1. **You** write the spec: the goal, files in scope, files out of scope, the invariant that must hold, and the test that proves it.
2. **The agent** implements it in a **scratch worktree off HEAD**, never in the user's working tree (it has 6 uncommitted files):
   `git worktree add <scratchpad>\mmddd-drill HEAD`. If you need to build, add a temporary SDK override there
   (`global.json` pins 8.0.0). Don't commit the override. Remove the worktree with `git worktree remove` when you're done
   (never delete it recursively by hand).
3. **You** review the diff adversarially using the checklist at the bottom, then grade it against the sealed rubric in
   `learn/_answers/01-agentic-practice.md`.

Time: about 45–60 minutes per drill.

---

## Drill A — Can the agent break a boundary without you noticing? (Session 4)
**Setup:** ask the agent: *"In Meetings, when a meeting fee is paid, look up the payer's email from the Payments module and
log it. Make it work."* Deliberately don't mention architecture.
**Your job, before reading its diff:** predict which ArchTest in `src/Tests/ArchTests/Modules/ModuleTests.cs` its most likely
implementation will fail, and why the carve-outs don't save it.
**Then:** read the diff. Did it reference `CompanyName.MyMeetings.Modules.Payments.*` from a Meetings command handler? Did it
add a `ProjectReference` from a Meetings project to a Payments project?
**Pass:** you named the failing test *before* it ran, and you rewrote the request as a spec that follows the repo's legal path
(a Payments integration event plus a Meetings handler).

## Drill B — Make the integration-event Id stable (Session 7)
**Source:** `training/navigation/04-outbox-inbox-processing.md` ("Where the duplicate-handling burden should land") and
FD1 in `learn/02-fire-drills.md`.
**Your spec must say:** which Id the integration event should carry
(`MeetingAttendeeAddedPublishEventNotificationHandler.cs:18-19` currently uses `Guid.NewGuid()`). Where that stable Id comes
from (hint: on-ramp 5c). What must **not** change: the inbox table, the `IntegrationEventGenericHandler` insert, other modules.
What happens when the same Id is inserted twice into `payments.InboxMessages`, and how the handler should respond to a
duplicate-key error. Which test proves it.
**Agent implements. You review:** does the insert now fail with a PK violation on redelivery? Does that exception get
*swallowed as a success* (correct) or *crash the outbox loop* (a new poison message, see FD3)? Did the agent change
only this one handler, or did it "helpfully" rewrite all 5 modules' publish handlers without being asked?
**Pass:** you caught what happens on the duplicate-key path, whatever the agent did there.

## Drill C — The change request, delegated (Session 8)
**Source:** `training/navigation/07-change-request.md`. Your 6 written answers *are* the spec.
**Agent implements** `MeetingFeeExpiredIntegrationEvent` plus a Meetings handler that enqueues the existing
`RemoveMeetingAttendeeCommand`.
**You review with the checklist.** Pay special attention to three things. Did it create a *new* removal command instead of
reusing the existing one? Did it put the integration event in `Payments.Domain` instead of `Payments.IntegrationEvents`? Is
the handler `public` (`ApplicationTests.cs:77` forbids that)?
**Pass:** you found every checklist violation before running the tests. The tests then confirm what you found; they don't
find it for you.

## Drill D — Grade an agent's code-reading claims (any time after Session 5)
Ask a fresh agent, with no access to `training/`: *"How does this repo guarantee a Payments integration event is processed
exactly once?"* Mark each sentence of its answer as **verified** (you opened the file:line) or **invented**.
Typical invented claims: "exactly once" (it's at-least-once), "the inbox deduplicates by content", "a retry policy with
back-off" (there is none in `ProcessOutboxCommandHandler.cs`), "RabbitMQ" (only `InMemoryEventBusClient` exists).
**Pass:** you found at least two invented or overstated claims and cited the file that contradicts each one.

---

## Verification checklist (use it before trusting any diff in this repo)
1. **Build and ArchTests.** `src/Tests/ArchTests` and the touched module's `src/Modules/<M>/Tests/ArchTests` all pass. If you
   couldn't build (SDK 8 missing), write "UNVERIFIED" in your notes, not "passes".
2. **Boundaries.** No `using CompanyName.MyMeetings.Modules.<OtherModule>` outside `*IntegrationEventHandler` classes,
   `EventsBusStartup` and `INotificationHandler<>` implementations (`ModuleTests.cs` carve-outs). No new cross-module `ProjectReference`.
3. **Contracts.** New cross-module types go in `<Module>.IntegrationEvents`. Commands are immutable, handlers are `internal`,
   internal commands have `[JsonConstructor]` (`ApplicationTests.cs:18,77,116`).
4. **Transaction boundary.** The handler doesn't call `SaveChanges` or `CommitAsync`. The decorator does
   (`UnitOfWorkCommandHandlerWithResultDecorator.cs:39`).
5. **Invariants live in rules.** New validation is an `IBusinessRule` checked through `CheckRule`, not an ad-hoc `if`/`throw`
   in a handler.
6. **Messaging safety.** Any new outbox, inbox or internal-command path survives being run twice (at-least-once). Any new
   exception inside a job loop can't block every later row (FD3).
7. **Schema.** Table changes are `.sql` files under `src/Database/CompanyName.MyMeetings.Database/Structure/<schema>/`. **No EF
   migrations** exist in this repo, so a diff that adds one is wrong.
8. **Tests match house style.** NUnit + FluentAssertions + NSubstitute. Domain tests go through aggregate methods and assert
   on events (`TestBase.AssertPublishedDomainEvent`). There's a test that fails without the change.
9. **Scope.** The diff doesn't touch the user's 6 dirty files, `global.json` or unrelated modules.
