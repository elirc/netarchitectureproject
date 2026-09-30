# 11. Domain events and independent snapshot oracles

Events make successful behavior visible, but they can also hide weak assertions when test helpers are treated as magic. Read [Entity](../../../modular-monolith-with-ddd/src/BuildingBlocks/Domain/Entity.cs), [DomainEventsTestHelper](../../../modular-monolith-with-ddd/src/Modules/Meetings/Tests/UnitTests/SeedWork/DomainEventsTestHelper.cs), and [TestBase](../../../modular-monolith-with-ddd/src/Modules/Meetings/Tests/UnitTests/SeedWork/TestBase.cs). The first defines collection behavior; the second traverses the object graph; the third gives assertion convenience methods. None of those names alone proves external event publication.

This chapter teaches how to build an oracle that does not change underneath the operation being tested. The same technique supports successful role transitions, rejected title changes, and queue promotions. The exercises remain proposals for learner tests; the documentation does not alter application helpers or assert that every possible graph has been executed.

## Identify the event owner

Meeting construction adds MeetingCreatedDomainEvent to the aggregate. It also creates host attendee children, each of which adds MeetingAttendeeAddedDomainEvent to its own collection. Later role changes append events to the relevant attendee child. A root-only inspection can therefore see creation while missing a role change that happened below the aggregate root.

Entity.DomainEvents exposes an IReadOnlyCollection wrapper when the backing list exists and can be null before any event has been added. Read-only means callers cannot mutate through that collection interface; it does not mean the underlying list is frozen in time. ClearDomainEvents clears the backing list, and subsequent AddDomainEvent calls append to it. Retaining the wrapper as a before snapshot is unsafe because later changes can be reflected through the same backing collection.

A correct snapshot materializes the selected values immediately. At minimum, record event type and stable domain payload fields into a new array or list of immutable projections. If event identifiers or occurrence times matter to the contract, include them deliberately after inspecting their actual definitions. Do not use an event object's runtime hash as a portable identity or assume that serialization captures every private field correctly.

## Understand what recursive collection does

GetAllDomainEvents starts with the supplied entity's direct event collection when nonnull. It then reflects fields from the runtime type and its base type. For fields whose declared type is assignable to Entity, it recursively collects the child. For enumerable fields other than strings, it iterates values and recurses when an element is an Entity. This enables the meeting's attendee, not-attendee, and waitlist lists to contribute events.

The helper is tailored to the repository's object shapes; it is not a general graph traversal library. It does not show a visited-object set. A cyclic entity reference or the same child reachable through multiple paths could therefore require additional handling. Direct nullable entity fields also need care because the recursive method expects an entity. Do not claim cycle safety or null tolerance beyond the checks actually present.

Collection traversal order is not a domain chronology guarantee. The helper walks reflected fields and list contents, collecting each entity's events. A flattened list can group events by owner rather than globally by occurrence time. If an assertion depends on order, explain why that order is meaningful for the specific fixture or sort a projection using a deliberately chosen stable domain key. Sorting by time alone may still leave ties.

## Clearing and collecting are not perfect mirrors

Inspect the direct-field type test in ClearAllDomainEvents. Its IsAssignableFrom direction differs from the corresponding collection method. Collection uses typeof(Entity).IsAssignableFrom(field.FieldType), while clearing uses field.FieldType.IsAssignableFrom(typeof(Entity)). Those expressions are not generally equivalent for a field declared as a derived entity type.

The enumerable branch in both helpers still visits Entity elements, which is relevant to Meeting's child lists. The asymmetry is a source-level helper review point, not proof that every current meeting test fails. A precise learner experiment would create a small controlled graph containing both a direct derived-entity field and a list child, then compare collection and clearing. Such a helper characterization would need to respect any dependencies and remain outside application source during this course.

This observation changes how you use fixture cleanup. Instead of assuming ClearAllDomainEvents removed every relevant event, verify the post-clear projection for the actual graph. A test that starts with no selected events can make its delta simpler. A test that intentionally retains fixture events should record a baseline and compare only the operation's expected additions.

## Event count is necessary but not sufficient

Suppose a role test expects one NewMeetingHostSetDomainEvent. An event of the right type with the wrong target identity is still incorrect. Check meeting identity and target identity in addition to cardinality. If the contract concerns time or monetary amounts, inspect the corresponding payload values. An event presence assertion alone can pass when a method mistakenly uses the actor identity in place of the target.

Conversely, a correct payload can appear twice. A SingleOrDefault-based assertion helper can reveal duplicate selected events by throwing rather than returning a single item. A plural helper permits explicit count and per-item checks. Understand which helper you are using before interpreting failure output as a missing event versus a duplicate event.

The attendee-addition test illustrates fixture contamination productively: it expects two attendee-added events because the creator host was created automatically and the later member adds another. A different test might clear fixture events and expect one. Neither count is universally correct. The setup and collection boundary determine the intended baseline.

## Snapshot the whole rejection contract

An all-fields-unchanged requirement needs more than an event assertion. For a main-attribute rejection, project title, term boundaries, description, location components, limits, RSVP bounds, fee value and currency, change member, and change date. Include relevant child state and event projections when the operation can reach children. Keep meeting identity and creation metadata in the baseline as stability checks when meaningful.

Avoid comparing only references for mutable child entities. Two variables pointing to the same attendee do not preserve an earlier role. Also avoid rebuilding expected values from the post-operation object, which turns the actual result into its own oracle. Write fixed expected values from setup or capture independent primitives before invocation.

A practical projection can be a record-like value with nested arrays of child summaries sorted by stable identity and record occurrence. Historical records may share member identities, so identity alone might not distinguish them. Use an explicit occurrence label in the test fixture or include a stable combination of recorded fields. The projection's job is to preserve the distinctions relevant to the contract, not to expose every implementation detail indiscriminately.

## Choose between semantic and structural snapshots

A semantic snapshot captures domain-observable meaning: role, active participation, occupied places, and event payloads. A structural snapshot may include exact private fields and collection ordering. The stronger the proposed rejection guarantee, the more carefully you must decide which internal changes count as violations. For the course's all-fields-unchanged rejection criterion, include all fields affected by the proposed operation and all relevant event collections, not just a convenient subset.

Do not serialize the entire aggregate graph without inspecting cycles, private-field coverage, and ignored members. A generic serializer may omit the private state that matters most, or include unstable values that make comparisons noisy. A small explicit projection is easier to review and gives failures names that correspond to the domain.

If reflection is necessary to inspect private fields in a learner test, use one well-scoped helper with explicit expected field names and clear missing-field errors. A renamed field should make the test's inspection dependency visible. Silently returning null on a lookup failure can make unchanged null equal unchanged null, allowing the test to pass while observing nothing.

## Separate events from delivery evidence

The term published in a unit-test helper name does not change the executed boundary. The helper collects in-memory IDomainEvent objects. It does not demonstrate an outbox row, a message broker send, subscriber execution, or transaction commit. A report should say recorded or collected domain event when that is the evidence actually available.

A later integration investigation can trace how domain events are dispatched or persisted, but it must inspect those components and execute an appropriate boundary. Do not infer them from a successful child event assertion. Similarly, absence of a direct event on the aggregate does not imply no event anywhere in the graph, and absence from a transport log does not prove no domain event was created.

This layered vocabulary makes failures easier to assign. Missing child event is a domain transition issue. Missing outbox record after a committed operation is a persistence or dispatch investigation. Missing consumer effect after message delivery belongs to another boundary. Collapsing them all into event failed obscures the next useful experiment.

## Debug an apparently impossible passing test

Imagine a last-host rejection test stores beforeEvents = attendee.DomainEvents, invokes demotion, catches the expected exception, and compares beforeEvents with attendee.DomainEvents. Both variables can refer to views of the same mutated backing list. Equality of those observations does not establish an unchanged event set. Materialize before into an independent projection and repeat the reasoning.

Now imagine the test stores beforeRole by retaining the attendee object and reads its role only during the final assertion. It has the same problem. The time of observation matters as much as the selected property. A before snapshot must be captured before the operation, not reconstructed from a before-named reference afterward.

Finally, imagine the event helper is called only on MeetingGroup while the changed object is a separately referenced Meeting. Clearing or collecting one graph does not automatically reach another merely because the domain concepts are related. Follow actual object references. A domain association represented by an identifier is not a recursive object link.

## Independent practice

Exercise NA11-A, event ownership map, is worth eight points. Map creation, attendee addition, host promotion, cancellation, and waitlist signoff to their direct event owners. Design payload and cardinality assertions that isolate one operation from fixture history.

Exercise NA11-B, snapshot repair, is worth six points. Replace a retained read-only event view and mutable attendee reference with independent projections. Explain how your projection handles multiple historical records for one member and fails loudly on a missing reflected field.

Exercise NA11-C, helper audit, is worth six points. Explain the assignability-direction difference, describe a bounded graph that distinguishes collection from clearing, and identify two claims about event delivery that the helper cannot establish. Use [the solutions](SOLUTIONS-07-12.md) to review your reasoning after completing the design.


[Investigation workbook](INVESTIGATION-WORKBOOK-07-12.md) | [Course route](README.md)
