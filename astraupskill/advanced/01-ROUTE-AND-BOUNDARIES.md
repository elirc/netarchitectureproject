# Route: prove an invariant at the boundary that owns it

This advanced pack follows one small interval defect through a modular application: an end date was lost when application handlers mapped a request into a meeting term. The repair is simple to read and easy to misunderstand. Correct mapping, valid value-object construction, unchanged aggregate state on rejection, and durable database rollback are four distinct claims. Your task is to explain which current tests support each claim, then design an independent extension without weakening those boundaries.

You should know C# constructors, asynchronous methods, interfaces, exception assertions, and basic value-object versus aggregate terminology. Begin by explaining why two `DateTime` parameters in the correct order can still compile when the caller passes the start twice. The type system prevents certain errors, but it does not infer that two values with the same type represent different business meanings. That gap makes a source-to-observable-state test valuable.

## Learning route and deliverables

| Session | Inspect | Produce |
|---|---|---|
| 1, 30 minutes | Command handlers and MeetingTerm | Diagram showing request fields, factory arguments, aggregate entry point |
| 2, 40 minutes | Rule and handler regression tests | Boundary table with concrete dates and expected repository observations |
| 3, 45 minutes | Disposable real-source lab | Baseline output and two intentionally failing semantic variants |
| 4, 45 minutes | Reflection helper and aggregate fields | Diagnostic checklist and an all-fields rejection snapshot design |
| 5, 60-90 minutes | Independent rule specification | Test-first proposal, separate solution review, capstone evidence packet |

Read the [create handler](../../modular-monolith-with-ddd/src/Modules/Meetings/Application/Meetings/CreateMeeting/CreateMeetingCommandHandler.cs), [change handler](../../modular-monolith-with-ddd/src/Modules/Meetings/Application/Meetings/ChangeMeetingMainAttributes/ChangeMeetingMainAttributesCommandHandler.cs), [MeetingTerm](../../modular-monolith-with-ddd/src/Modules/Meetings/Domain/Meetings/MeetingTerm.cs), and [current handler tests](../../modular-monolith-with-ddd/src/Modules/Meetings/Tests/UnitTests/Meetings/MeetingTermCommandHandlerTests.cs). Do not replace them with a similarly named example from a copied collection.

The current `MeetingTerm` constructor calls `CheckRule` before assigning start and end. The rule rejects equality as well as reversal. Both handlers pass `request.TermEndDate` as the second factory argument. The existing invalid-change regression checks that the original term survives an invalid interval. It does not compare every private aggregate field, every nested collection, or the domain-event sequence. The advanced all-fields criterion is a deliberate expansion of the proof, not a description of an assertion that already exists.

Exercise **MA-01**: classify these statements as currently demonstrated, inferred from source, or not demonstrated: the requested end reaches the added aggregate; an invalid create never calls `AddAsync`; a rejected change preserves every field; an HTTP client receives a particular status; a committed database transaction cannot contain an invalid meeting term. For each statement, name the next smallest test or inspection that would increase confidence.

The included lab compiles copies of the actual value-object and rule source with an already installed .NET SDK in a disposable directory. It is stronger than a hand-written reimplementation for the domain rule, but weaker than executing the full handler/project test assembly. Its mapping adapter deliberately isolates the two-argument error and retains the factory signature. No original application source is mutated by the lab, and no production feature is introduced by these chapters.

[Advanced index](README.md)
