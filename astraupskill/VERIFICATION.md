# Interpret the unit test evidence

The accepted command completed with ninety-seven passing unit tests and no failures or skips. The attached [TRX](evidence/regression.trx) gives machine-readable per-test outcomes (`<Counters total="97" executed="97" passed="97" failed="0" …>`), and the [run record](evidence/astra-meetings-tests-r3.json) gives the command, exit code 0 and timing (2026-09-19, 260 s). The console log that the record names (`astra-meetings-tests-r3.log`) was not committed, so the build output cannot be re-inspected. The selected target is the Meetings domain unit test project; its references include application and infrastructure assemblies needed by the existing suite.

The added tests cover exact positive interval preservation, equal and reversed interval rejection, both application handler mappings, prevention of repository addition after invalid creation, and preservation of the existing term after invalid modification. Reflection invokes the actual internal handlers, while repository and member-context substitutes isolate their dependencies.

No SQL integration suite was executed for this improvement. A project reference with IntegrationTests in its name is not evidence that a database integration test ran. No deployment, migration, external service, or browser workflow is included in this acceptance claim. The course separates those boundaries so future work can choose the appropriate environment deliberately.

Earlier attempts exposed source-style violations and were corrected before the accepted run. Long Windows paths also produced assembly-cache warnings in an earlier build attempt. The successful final command is the acceptance evidence; failed attempts remain in the working history. Original snapshots accompany changed source files, and the delivery process verifies their canonical hashes before copying. Reading these guides or passing software tests does not establish human mastery of the architectural concepts.

## How the 97 is made up

Counted from the attributes in `modular-monolith-with-ddd/src/Modules/Meetings/Tests/UnitTests/` and cross-checked against the TRX test names (2026-10-06):

| Source | Count |
|---|---:|
| `[Test]` attributes in the project | 90 |
| …of which carry `[TestCase]` too (three `MeetingCommentTests` methods, `TestCase(null)` + `TestCase("")`), so each runs twice | +3 |
| `[TestCase]`-only methods: `CreateNewBetweenDates_WithoutPositiveDuration_BreaksRule(0/-1)` and `CreateMeeting_InvalidDuration_DoesNotAddAggregate(0/-1)` | +4 |
| **Total cases** | **97** |

The eight new cases are `MeetingTermTests` (3: the preservation test plus the two-case rule test) and `MeetingTermCommandHandlerTests` (5: `CreateMeeting_MapsRequestedEndDateIntoAddedAggregate`, the two `CreateMeeting_InvalidDuration_DoesNotAddAggregate` cases, `ChangeMeeting_MapsRequestedEndDateIntoExistingAggregate`, `ChangeMeeting_InvalidDuration_PreservesExistingTerm`). The other 89 cases already existed.

## Reproduce it

The solution pins .NET 8 (`modular-monolith-with-ddd/global.json`, `src/Directory.Build.props:12`). The recorded run used a private .NET 8 toolchain from the original workstation. On your machine, any .NET 8 SDK works. From `modular-monolith-with-ddd/src`:

```powershell
dotnet test Modules/Meetings/Tests/UnitTests/CompanyName.MyMeetings.Modules.Meetings.Domain.UnitTests.csproj --logger trx
dotnet test Modules/Meetings/Tests/UnitTests/CompanyName.MyMeetings.Modules.Meetings.Domain.UnitTests.csproj --filter "FullyQualifiedName~MeetingTerm"
```

The first command should report 97 passed. The filtered run selects the eight new cases.

## Course navigation

[README](README.md) / [01-CODEBASE-MAP](01-CODEBASE-MAP.md) / [02-CONCEPTS](02-CONCEPTS.md) / [03-WORKED-CHANGE](03-WORKED-CHANGE.md) / [04-TESTING-AND-DEBUGGING](04-TESTING-AND-DEBUGGING.md) / [05-PRACTICE](05-PRACTICE.md) / [06-SOLUTIONS-AND-REVIEW](06-SOLUTIONS-AND-REVIEW.md) / [07-TRACE-LAB](07-TRACE-LAB.md) / [VERIFICATION](VERIFICATION.md)

## Recorded command evidence

The recorded test runs passed **97 tests**. The commands below define the verified scope; counts refer to tests, not commands.

| Check | Recorded command | Exit | Evidence |
|---|---|---:|---|
| `astra-meetings-tests-r3` | `dotnet test Modules/Meetings/Tests/UnitTests/CompanyName.MyMeetings.Modules.Meetings.Domain.UnitTests.csproj --no-restore --nologo --verbosity minimal /m:1 --logger trx` (run from `modular-monolith-with-ddd/src` with a workstation-local .NET 8 `dotnet.exe`; the absolute path is in the record) | 0 | [record](evidence/astra-meetings-tests-r3.json); log not committed |

[Machine-readable results 1](evidence/regression.trx).
