# 02 - Treat command mapping as behavior worth testing

Mapping is often dismissed as plumbing because the code appears to copy values from one object to another. In this module, a single incorrect argument can reject a valid meeting or silently alter its meaning. This chapter treats mapping as an explicit contract and develops tests that distinguish wrong source properties, swapped positions, normalization, and unrelated domain rejection. Read the [create handler](../../../modular-monolith-with-ddd/src/Modules/Meetings/Application/Meetings/CreateMeeting/CreateMeetingCommandHandler.cs), [change handler](../../../modular-monolith-with-ddd/src/Modules/Meetings/Application/Meetings/ChangeMeetingMainAttributes/ChangeMeetingMainAttributesCommandHandler.cs), and [mapping regressions](../../../modular-monolith-with-ddd/src/Modules/Meetings/Tests/UnitTests/Meetings/MeetingTermCommandHandlerTests.cs).

## A mapping table is a test design tool

Start with command property, destination expression, destination meaning, and observation. TermStartDate maps to the first MeetingTerm factory argument and should become StartDate. TermEndDate maps to the second argument and should become EndDate. The location name, address, postal code, and city map into MeetingLocation. Attendee and guest limits map through the group creation path or MeetingLimits on the change path. Optional fee value determines whether MoneyValue is constructed or Undefined is supplied.

The table exposes positions where types alone cannot distinguish mistakes. Two DateTime arguments compile when reversed or duplicated. Several location strings compile when swapped. Two integer-like limits may need different null semantics. A mapping test should therefore choose sentinel values that are valid but visibly different. Identical strings or equal date boundaries erase the signal needed to detect a swapped argument.

For example, use a location named North Room, address 18 Cedar Lane, postal code Z9, and city Harbor. A test that assigns the string test to every field cannot detect a city/address swap. The lesson is not to use bizarre invalid data; it is to choose ordinary values whose identities remain recognizable at the observation point.

## Create and change have different orchestration

Create loads the meeting group and maps each host Guid into MemberId before asking the group to create the meeting. It passes the current member as creator, then calls AddAsync on the meeting repository and returns the aggregate id. A successful test can capture the exact aggregate passed to AddAsync. It should assert that a nonnull aggregate was added and that its term preserves both requested boundaries.

Change loads an existing meeting by MeetingId and invokes ChangeMainAttributes with constructed replacement values and the current modifying member. The handler does not call a separate update method in the inspected body. A test should observe the loaded aggregate's state and relevant interactions rather than inventing a repository UpdateAsync expectation that the code does not contain. Persistence tracking may exist elsewhere, but that requires its own source inspection.

The different return types also matter for a reflection-based test adapter. Create returns Task<Guid>; change returns Task. A generic helper that casts both to the same shape can fail before a business assertion runs. Mapping evidence must include successful invocation and awaiting, not merely successful type discovery.

## Evaluation order determines rejection scope

C# evaluates call arguments before entering the target method. When MeetingTerm construction rejects an equal interval, later arguments and the aggregate method body are not reached through that call. Earlier awaited repository reads have already happened. This explains why invalid command input can cause an exception without a database rollback mechanism or a partially assigned aggregate.

Now consider a different failure location: MeetingLimits.Create during change. The term may already have been constructed successfully, but it is a new value object not yet assigned to the aggregate. If limit validation rejects before method entry, the old aggregate remains untouched through the call. Constructing an unused local object is not the same as mutating persisted domain state.

A third failure can occur inside ChangeMainAttributes after all arguments are successfully built. Its attendee-limit rule checks the requested capacity against current active attendance before assignments. That rejection is at the aggregate boundary rather than the value-object boundary. Tests should distinguish these stages because their setup requirements and diagnostic meaning differ.

## Three mapping mutations, three observations

Mutation one passes start for both MeetingTerm arguments. A valid positive request becomes equal and throws the strict-order rule. A successful mapping test detects the unexpected rejection. Mutation two passes end first and start second. The valid request becomes reversed and also rejects, but a source review identifies a different wiring defect. Mutation three passes start and an end shifted one hour later. The interval remains valid, so a test that only expects no exception will miss it; exact boundary assertions reveal it.

These examples show why negative and positive tests must complement each other. A test suite that asserts all invalid inputs throw can still allow a valid mapping to change silently. A suite that asserts one valid result exists can still allow equality. A useful matrix includes exact valid mapping, equality rejection, reversal rejection, and the smallest positive duration supported by the DateTime representation.

The disposable lab later mutates a generated adapter while preserving the real factory signature. That produces a semantic failure rather than a compiler error. A broken starter that changes a constructor's parameter count teaches little about mapping because the code never reaches the domain rule. Keep the mutation small enough that the intended boundary is exercised.

## Optional values need explicit policy

The handlers choose MoneyValue.Undefined when the request has no fee value. When a value is present, they pass that value and the requested currency into MoneyValue.Of. This is a branch, not a blind field copy. A test should distinguish absent fee from zero fee if the domain treats those states differently. Do not infer the full monetary validation policy from the handler alone; inspect MoneyValue before asserting allowed currencies or negative values.

RSVP boundaries use the nullable Term type rather than MeetingTerm. The handlers preserve that distinction. The aggregate may later clamp RSVP end relative to the meeting start. A mapping test observing final RSVP state must account for deliberate aggregate normalization rather than accuse the handler of losing a value. The next chapter develops the two temporal contracts separately.

Host membership also belongs to group rules, not simply list conversion. The handler transforms ids, while the group checks whether the creator and supplied hosts satisfy its rule. A valid mapping fixture needs a group and member setup that allows the operation to reach the intended assertion. Empty hosts can trigger the aggregate's default creator-as-host behavior, which is another separate domain decision.

## Write assertions that identify the defect

Use a failure message that names the requested and observed field. Expected end noon but observed one in the afternoon is more diagnostic than aggregate did not match. For rejection, assert the specific business-rule type where appropriate. For repository effects, distinguish reads, add calls, and later persistence. A negative test that checks only no AddAsync may still pass because an unrelated exception occurred during setup.

Capture the aggregate through the substitute's callback before examining private state. This establishes which instance the handler actually added. Do not inspect a separate fixture object that the handler never used. On the change path, configure the repository to return the exact instance whose baseline you captured, then inspect it after invocation or rejection.

Reflection into private fields is a test observation mechanism, not a request to make production fields public. It couples the test to implementation names and should fail clearly when those names change. Later chapters show how to separate observation failures from business failures so a missing field cannot masquerade as a successful negative test.

## Worked mapping worksheet

Create a row for a start at nine and end at twelve, with old meeting term on a different day. For creation, the expected observed start and end are the command values and the repository receives one new aggregate. For change, identity and creation metadata should remain associated with the existing aggregate while its requested main attributes change. For an invalid equal term, no completed replacement term exists and the aggregate method is not entered.

Add a row where only description changes while term remains valid and unchanged. This checks that the handler does not derive dates from unrelated fields or current time. Add a row where the fee value is absent and the currency string is still present; the inspected branch uses Undefined because value presence controls construction. The worksheet should name that branch without claiming an uninspected monetary rule.

Finally, record which observations are direct and which are inferred. The test directly captures AddAsync's argument and reads its term. The conclusion that the requested boundaries survived follows from those observations. The conclusion that SQL contains the same values does not follow until persistence mapping and transaction behavior are tested.

## Independent practice

Exercise NA02-A, sentinel mapping, is worth six points. Design distinct valid sentinels for term, location, limits, and optional fee. Map each command property to its factory argument and observation. Identify two swaps that compile successfully but should fail your assertions.

Exercise NA02-B, mutation matrix, is worth eight points. Compare start-twice, reversed arguments, and shifted-end mutations. State whether construction rejects and which exact assertion detects each defect. Explain why an assertion of no exception alone misses one case.

Exercise NA02-C, orchestration differences, is worth six points. Contrast create and change repository interactions, return types, and aggregate observation points. Include one rejection during value construction and another at the aggregate's capacity rule, identifying what has already happened in each trace.

Continue with [temporal value objects](03-TEMPORAL-VALUE-OBJECTS-AND-BOUNDARIES.md). Check your mappings against [the separated answers](SOLUTIONS-01-06.md) only after writing the expected traces and effects.
