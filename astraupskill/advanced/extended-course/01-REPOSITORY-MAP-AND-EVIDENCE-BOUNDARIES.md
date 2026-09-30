# 01 - Find the boundary that can prove your architectural claim

This course studies the meeting module in the original modular-monolith checkout. The first task is not to memorize a diagram of layers. It is to connect a concrete requested change to the source that decides it, the state that can change, and the evidence that would reveal a defect. You need basic C# classes, constructors, asynchronous methods, and exceptions. Database and HTTP expertise can come later, after the domain and application boundaries are clear.

The source root is [modular-monolith-with-ddd](../../../modular-monolith-with-ddd/README.md), nested inside the desktop project. The earlier [advanced course](../README.md) provides a compact interval introduction. This extended route adds longer investigations, independent exercises, separated solutions, and disposable failure experiments. Current behavior is described from source; proposed title rules, stronger rejection guarantees, and future integration work remain explicitly proposed.

## Start with a request containing asymmetric values

Imagine a meeting requested for nine in the morning until noon on a fixed UTC date. The start and end are intentionally different, and the duration is not an incidental value computed by two separate clock calls. This request gives the investigation a visible signal: if a handler accidentally passes start twice, the resulting equal interval should be rejected. If it swaps the boundaries, the interval becomes reversed. If it shifts the end, a successful result can still violate the requested mapping.

A broad claim such as meeting creation works hides all those distinctions. Replace it with a narrow claim: the create handler passes the requested start and end into MeetingTerm, and the aggregate added to its repository contains both exact values. That claim identifies an input, a mapping boundary, and an observable. It also makes clear what is not proved: an added object captured by a substitute repository is not evidence of a committed SQL row or an HTTP response.

Use [CreateMeetingCommandHandler](../../../modular-monolith-with-ddd/src/Modules/Meetings/Application/Meetings/CreateMeeting/CreateMeetingCommandHandler.cs), [MeetingTerm](../../../modular-monolith-with-ddd/src/Modules/Meetings/Domain/Meetings/MeetingTerm.cs), and [the handler regressions](../../../modular-monolith-with-ddd/src/Modules/Meetings/Tests/UnitTests/Meetings/MeetingTermCommandHandlerTests.cs) as the initial source triangle. Each contributes a different part of the explanation. The handler maps; the value object validates; the tests arrange a context and observe selected effects.

## The desktop folder is not the solution root

The instructional files live under astraupskill, while application sources live under the nested repository. A command copied from another checkout can therefore target a nonexistent project even when its final filename looks plausible. The actual unit-test project is CompanyName.MyMeetings.Modules.Meetings.Domain.UnitTests.csproj under the meeting module's Tests/UnitTests directory. Keep the full path in the command and verify that the file exists before discussing execution.

The project file itself is minimal, and shared build properties provide important configuration. The inspected src/Directory.Build.props targets net8.0. A separate disposable course lab targets the installed .NET 10 SDK without project packages. Those are different build environments. A successful isolated domain calculation on .NET 10 does not certify that the full net8.0 application and its dependencies build or run in the same environment.

This distinction is practical rather than bureaucratic. If a full test command fails before loading tests because its restored assets or target runtime are unavailable, the failure provides no evidence about the interval invariant. If a disposable lab compiles only selected source files, it can still establish useful behavior for those types. An honest report names both the useful result and the boundary it did not cross.

## Map responsibilities through verbs

The create handler loads a meeting group, translates host identifiers, constructs value objects, asks the group to create a meeting, adds the resulting aggregate to a repository, and returns its id. The change handler loads an existing meeting, constructs replacement values, and invokes ChangeMainAttributes. Neither description requires assuming that every method named repository performs an immediate durable commit. Inspect the implementation or application pipeline before making that stronger claim.

MeetingTerm constructs a valid interval or raises a business-rule exception. MeetingGroup checks group-related prerequisites before creating the meeting. Meeting assigns state, initializes attendees, and collects domain events. The building-block Entity stores events and provides a rule-checking helper. These responsibilities are connected, but each has a different unit of evidence. A domain event in an in-memory collection is not automatically a published integration message.

```text
Requested command values
  -> application mapping and repository reads
  -> value-object construction
  -> group or aggregate business decisions
  -> in-memory state and domain events
  -> repository/persistence pipeline
  -> external response and later consumers
```

Chapters 01-06 focus on the middle of this chain. Chapters 13-18 study persistence and transport with their actual implementations. Before reaching those chapters, do not fill uninspected boxes with assumptions from a generic architecture article. The repository's concrete code is the authority for what happens here.

## Build an evidence ladder without confusing levels

A pure rule test can establish that equal or reversed boundaries break a particular rule. A value-object test can establish that construction enforces it and preserves valid values. A handler test can establish argument mapping and selected repository interactions. An aggregate test can establish mutation ordering and domain-event behavior. An integration test can establish persistence or messaging behavior in its configured environment. A request-level test can establish routing and response interpretation.

These are complementary evidence types, not interchangeable badges of completeness. A handler test can miss a database mapping defect because its repository is substituted. A database test can miss a UI that sends the wrong property because it constructs commands directly. A broad end-to-end test may observe failure without identifying which boundary caused it. Select evidence according to the claim you need to resolve.

For every experiment, write a card containing the source claim, input, setup assumptions, command, expected observation, actual observation, and limitation. A skipped test is recorded as skipped. A compilation error is recorded as failure to execute the behavioral assertion. An intentionally broken disposable mutation is useful only if it fails for the intended semantic reason. A syntax error does not prove that the invariant test can detect the target defect.

## A worked investigation: invalid change

Suppose a change command requests a new title, location, fee, and an equal start/end interval. The change handler first retrieves the existing meeting. It then evaluates arguments for ChangeMainAttributes, including MeetingTerm construction. The interval factory rejects before the aggregate method is entered. The repository read already happened; the mutable aggregate assignments did not happen through this call. That is an argument-evaluation boundary, not a database transaction rollback.

A test expecting no repository interaction would be wrong because the read is part of the actual sequence. A test expecting no repository write might be reasonable only after identifying which write operations the handler or pipeline performs. The existing regression checks that the old term remains. A stronger proposed projection can compare title, term, description, location, limits, RSVP term, fee, modification metadata, identity, and collected events.

The strengthened projection should not be advertised as already established by the current term-only assertion. It is a deliberate extension of evidence. This habit matters throughout the course: distinguish what the source suggests, what a test actually asserts, and what a proposed stronger contract would require.

## Keep fixture preconditions visible

A meeting group must satisfy other rules before a valid meeting can be created. The handler fixture proposes a group, accepts it, creates the group, and gives it a future expiration date. It supplies a member context and repository substitutes. This is not incidental test noise. Those choices make the interval mapping the relevant decision rather than allowing an unrelated group-payment or host-membership rule to reject first.

When a negative test expects merely some exception, an invalid fixture can make it pass for the wrong reason. Prefer asserting BusinessRuleValidationException and its specific BrokenRule when that is the boundary under test. For a successful mapping test, assert both start and end using distinct values. A result id alone says little about whether the requested term survived the mapping.

Keep time deterministic where the test's purpose permits it. SystemClock can supply a custom domain time, but not every fixture uses it for every DateTime expression. Inspect real-clock calls as well as the domain abstraction. A fixed future date can eventually become past in a long-lived suite, while relative dates can obscure exact boundaries. Choose the approach that isolates the rule and document its assumptions.

## Independent practice

Exercise NA01-A, responsibility map, is worth six points. Trace the nine-to-noon create request through command, handler, value object, group, aggregate, and repository observation. Name the exact value or effect at each boundary and identify which later persistence and HTTP claims remain unproved.

Exercise NA01-B, evidence critique, is worth six points. Review the statement that a passing disposable interval lab proves the create endpoint works. Replace it with a supported claim and specify the next two evidence layers needed for mapping and transport. Include the net8.0 versus isolated net10.0 distinction.

Exercise NA01-C, rejected change, is worth eight points. Draw the equal-interval change trace and mark the repository read, value-object exception, and aggregate method entry. Propose a complete unchanged-state projection and distinguish that stronger proposal from the existing term-only regression assertion.

Continue with [command mapping](02-COMMAND-MAPPING-AS-A-CONTRACT.md). Hints and full answers are separated in [the first installment guide](SOLUTIONS-01-06.md). The chapter is complete when another reader can follow your claim to an observable without guessing which layer your evidence exercised.
