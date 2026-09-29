# Module boundaries — how they're drawn and how they're enforced

## Evidence: the 5 modules

`src/Modules/` — `Administration`, `Meetings`, `Payments`, `Registrations`, `UserAccess`. Each is
its own set of projects (`*.Api`, `*.Application`, `*.Domain`, `*.Infrastructure`, plus
`*.Tests.{UnitTests,IntegrationTests,ArchTests}`), each with its own SQL schema
(`src/Database/CompanyName.MyMeetings.Database/Structure/{administration,meetings,payments,
registrations,users}/`) and its own `Outbox`/`Inbox`/`InternalCommands` tables. This is the
"module-per-bounded-context" shape: one process, one deployable, but internally partitioned as if
each module were a future microservice.

## The two enforcement layers

A module boundary that only lives in a README rots the first time someone is in a hurry. This repo
enforces it with `NetArchTest` assertions that run as ordinary NUnit tests in CI (see
`azure-pipelines.yml`), so a boundary violation fails the build, not a code review.

**1. Solution-level (API layer), `src/Tests/ArchTests/Api/ApiTests.cs`.**
Four tests, one per module, e.g.:
```csharp
[Test]
public void MeetingsApi_DoesNotHaveDependency_ToOtherModules()
{
    List<string> otherModules = [AdministrationNamespace, PaymentsNamespace, UserAccessNamespace];
    var result = Types.InAssembly(ApiAssembly)
        .That().ResideInNamespace("CompanyName.MyMeetings.API.Modules.Meetings")
        .Should().NotHaveDependencyOnAny(otherModules.ToArray())
        .GetResult();
    AssertArchTestResult(result);
}
```
This stops a controller in one module's API folder from directly referencing another module's
types — the thing that would otherwise happen invisibly the first time two controllers need to
share a DTO.

**2. Module-level, `src/Tests/ArchTests/Modules/ModuleTests.cs`.**
Same shape, but scans the module's `Application`/`Domain`/`Infrastructure` assemblies together
(`typeof(IMeetingsModule).Assembly`, `typeof(Meeting).Assembly`, `typeof(MeetingsContext).Assembly`
for Meetings) and asserts no dependency on the other three modules' namespaces — **with three
explicit carve-outs**:
```csharp
.That()
    .DoNotImplementInterface(typeof(INotificationHandler<>))
    .And().DoNotHaveNameEndingWith("IntegrationEventHandler")
    .And().DoNotHaveName("EventsBusStartup")
.Should().NotHaveDependencyOnAny(otherModules.ToArray())
```
Those three exclusions are the whole point: `IntegrationEventHandler` classes and
`EventsBusStartup` are the *only* place a module is allowed to know about another module's
published integration-event types (see `navigation/03-integration-event-flow-*.md`). Everywhere
else — command handlers, domain entities, repositories — cross-module references are a compile-time
architecture-test failure, not just a lint warning.

## What's NOT enforced this way

Each module's *internal* layering (`Application` must not depend on `Infrastructure`, commands must
be immutable, handlers must be non-public, etc.) is enforced too, but by a **third, per-module**
arch-test project: `src/Modules/Meetings/Tests/ArchTests/Application/ApplicationTests.cs` has 8
tests including `Command_Should_Be_Immutable`, `CommandHandler_Should_Have_Name_EndingWith_
CommandHandler`, `Command_And_Query_Handlers_Should_Not_Be_Public`, and
`InternalCommand_Should_Have_Constructor_With_JsonConstructorAttribute` (the internal-command
pipeline round-trips through JSON, so a missing `[JsonConstructor]` is a silent runtime failure,
not a compile error — this test converts it back into one). Each of the 5 modules has its own copy
of this project (`src/Modules/{Module}/Tests/ArchTests/`), so the internal-layering rules are
duplicated 5×, not shared — a maintenance cost worth noting if you're asked "what would you change
here."

## Evidence paths
- `src/Tests/ArchTests/Api/ApiTests.cs`
- `src/Tests/ArchTests/Modules/ModuleTests.cs`
- `src/Tests/ArchTests/SeedWork/TestBase.cs` (namespace constants + assertion helpers)
- `src/Modules/Meetings/Tests/ArchTests/Application/ApplicationTests.cs`
- `src/Database/CompanyName.MyMeetings.Database/Structure/{administration,meetings,payments,registrations,users}/` (schema-per-module at the DB layer too)
