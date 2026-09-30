# 04 - Observe aggregate state and domain events as one decision

An aggregate method can change several private fields and append domain events before returning. To assess rejection, you must know which changes occur before the failing rule and what evidence remains afterward. This chapter examines [Meeting](../../../modular-monolith-with-ddd/src/Modules/Meetings/Domain/Meetings/Meeting.cs), [Entity](../../../modular-monolith-with-ddd/src/BuildingBlocks/Domain/Entity.cs), [MeetingLimits](../../../modular-monolith-with-ddd/src/Modules/Meetings/Domain/Meetings/MeetingLimits.cs), and [the capacity-change rule](../../../modular-monolith-with-ddd/src/Modules/Meetings/Domain/Meetings/Rules/AttendeesLimitCannotBeChangedToSmallerThanActiveAttendeesRule.cs). It develops stronger proposed rejection tests without changing the application.

## The aggregate owns related state

Meeting contains its identity and group identity, title, term, description, location, limits, RSVP term, fee, creation metadata, change metadata, cancellation metadata, and attendee-related collections. A main-attribute change is therefore not a single assignment. The method checks the requested attendee limit against current active attendance, then assigns the new main values, normalizes RSVP, records modifier and time, and adds a main-attributes-changed domain event.

The attendee count includes guests through GetAttendeeWithGuestsNumber for active attendees. A limit that looks large enough for the number of member records can still be too small for members plus guests. The capacity rule compares a present requested limit with that total and rejects when it is smaller. A null limit takes a different path because the rule only constrains a value when HasValue is true.

Before testing that aggregate rule, construct valid MeetingLimits. The value object has its own checks for negative limits and the relation between attendee and guest limits. A malformed limit can reject before the aggregate sees it, making a poorly arranged negative test pass for the wrong boundary. A fixture should satisfy value-object rules while violating only the active-attendance condition under investigation.

## Successful change has a precise footprint

A successful ChangeMainAttributes call assigns title, meeting term, description, location, limits, normalized RSVP, and fee. It sets change date to SystemClock.Now and change member to the supplied modifier. It then collects a MeetingMainAttributesChangedDomainEvent for the meeting id. It does not create a new meeting identity or rewrite creation metadata in the inspected method.

A before-and-after worksheet should separate changed fields, preserved fields, and derived fields. The requested RSVP end can be derived through clamping, while title is directly assigned. Identity and group association should remain tied to the original aggregate. Creation metadata describes the original creation, while change metadata describes this mutation. Collapsing all dates into one timestamp field would lose that history distinction.

For a deterministic successful test, set the domain clock to a fixed instant, capture baseline events, invoke the method with visibly different values, and compare the result. Decide whether the expected event assertion means one new event relative to the baseline or exactly one event in the entire aggregate collection. A freshly created meeting already collected a creation event, so ignoring the baseline can make event-count assertions misleading.

## Rejection before assignment is local state protection

The capacity-change rule runs before the assignments in ChangeMainAttributes. If it rejects, those assignments and the change event are not reached. This gives a focused unchanged-state claim for that rejection path. It is not a database rollback and does not automatically establish the same ordering for every other method in the aggregate.

The invalid MeetingTerm command case rejects even earlier, during handler argument evaluation. These two failures can leave the same observed old term while proving different behavior. One proves value construction prevented method entry. The other proves a method-level rule prevented its assignments. A test suite should retain both if both boundaries matter, rather than treating either as a universal atomicity test.

Now inspect another method as a counterexample to careless generalization. SetAttendeeRole changes an attendee's role and then checks that at least one host remains. The source ordering differs from ChangeMainAttributes. This observation means the statement every business-rule rejection leaves every in-memory field unchanged is not established globally by the class. Investigating that path requires its own fixture and assertions. The curriculum does not silently modify it or claim an executed failure result from source inspection alone.

## Domain events are state too

Entity lazily stores a list of IDomainEvent values, exposes a read-only view when present, and allows clearing it. AddDomainEvent appends to that collection. This is an in-memory record of domain occurrences. The helper's name does not demonstrate that a message reached an external broker, a database outbox, or another module. Those later mechanisms require separate source and integration evidence.

A rejected mutation that appends an event before failing can leave misleading evidence even if the primary field is restored manually. Conversely, changing state without the expected event can break downstream behavior even when immediate assertions pass. A complete proposed rejection projection should include the event sequence or a normalized event description, not only the aggregate's scalar fields.

Domain event objects can include generated ids and occurrence times through their own base types. If your test compares event instances, decide which properties are relevant and control time where possible. An event-type count proves less than checking the meeting id carried by that event. An event with the right type but the wrong aggregate id is not a correct outcome.

## Build a complete rejection projection

For a proposed main-attribute rejection test, capture title, term start and end, description, all location components, attendee and guest limits, RSVP boundaries, fee representation, modifier and change date, meeting and group identities, creation metadata, cancellation state, relevant attendee data, and domain events. The goal is not to expose all fields publicly; use an intentional test observation helper or supported behavior that reveals the required projection.

A snapshot should copy values rather than retain references to mutable collections. If before and after both point to the same list, a mutation can change both observations and make equality appear to hold. Normalize ordering where order is not part of the domain contract. Preserve ordering where it carries meaning, such as a sequence of newly collected events, and explain that choice.

Use a rejected command that requests several visibly different values. If the requested title and location equal the originals, a partial assignment can occur without changing the snapshot, weakening the experiment. Combine a genuinely invalid rule condition with otherwise valid but distinct replacement values. That setup exposes whether mutation happened before rejection.

## A proposed title rule as an independent extension

The independent extension requires trimmed title length between five and eighty characters inclusive. This is not current production behavior in the inspected ChangeMainAttributes method. Specify null handling and whether the stored title is trimmed or only validated. Then implement the rule in an isolated learner copy at the aggregate boundary before mutable assignments, covering both creation and change according to the chosen contract.

The boundary set includes four, five, eighty, and eighty-one characters after trimming, whitespace-only input, and a valid title surrounded by spaces. A rejected change should request a different valid term, description, location, limits, fee, and modifier so the complete projection can reveal partial mutation. On success, assert the chosen normalization policy and one expected new change event without replacing identity or creation metadata.

A deliberately broken version places the title check after assigning title and term. The test should fail because rejection leaves changed state, even though the correct exception is thrown. This is a stronger teaching example than removing the exception assertion: it demonstrates that correct rejection type and unchanged state are independent obligations.

## Creation has its own event and attendee effects

The constructor creates a meeting id, assigns main state, normalizes RSVP, records creator and creation time, initializes collections, and adds a creation event. If explicit hosts exist, it adds them as hosts; otherwise it adds the creator as host. A fixture assuming an empty attendee collection immediately after creation would therefore be wrong under the current code.

This matters when testing capacity changes. The creator-as-host can already contribute to active attendance. Additional attendees and guests must be counted relative to that baseline. A test that expects the first added attendee to be the only active person may accidentally choose a capacity that violates a different condition than intended. Write the initial aggregate state explicitly before arranging the rejection.

## Independent practice

Exercise NA04-A, mutation footprint, is worth six points. Classify main attributes, derived RSVP, creation metadata, modification metadata, identity, and events as changed or preserved in a successful main-attribute update. Include the initial creator-as-host effect in your baseline.

Exercise NA04-B, complete rejection, is worth eight points. Design a capacity rejection fixture with valid MeetingLimits and enough active attendees plus guests. Capture a complete value projection and event baseline, then explain why references to live mutable collections would weaken the comparison.

Exercise NA04-C, independent title rule, is worth six points. Specify the proposed title policy and a before-assignment implementation point. Describe the deliberate late-check mutation and the assertion that detects partial state despite the correct business exception. Keep this proposal separate from current source behavior.

Continue with [fixtures and reflection diagnostics](05-FIXTURES-REFLECTION-AND-ASYNC-FAILURES.md). Use [the solution guide](SOLUTIONS-01-06.md) after distinguishing local mutation ordering, database persistence, and external event publication in your own words.
