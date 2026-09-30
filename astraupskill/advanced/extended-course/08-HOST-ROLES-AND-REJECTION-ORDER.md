# 08. Host roles and the difference between rejection and unchanged state

A role change is a compact example of an aggregate invariant crossing child state. Read SetHostRole and SetAttendeeRole in [Meeting](../../../modular-monolith-with-ddd/src/Modules/Meetings/Domain/Meetings/Meeting.cs), the corresponding methods in [MeetingAttendee](../../../modular-monolith-with-ddd/src/Modules/Meetings/Domain/Meetings/MeetingAttendee.cs), and [MeetingRolesTests](../../../modular-monolith-with-ddd/src/Modules/Meetings/Tests/UnitTests/Meetings/MeetingRolesTests.cs). The chapter uses source traces and proposed tests. It does not claim an executed aggregate regression or modify the current methods.

The central lesson is that throwing the expected business-rule exception does not, by itself, establish that every field and event remained unchanged. Chapter 04 introduced that distinction for main-attribute changes. Role demotion gives a concrete reason to inspect the complete mutation sequence independently for each operation.

## Separate the actor from the target

The setting member is the person requesting the role change. The target member is the attendee whose role will change. Their identities may be equal, but tests should begin with distinct identities so accidental argument reuse is visible. A group organizer can authorize a change even when the authorization path differs from that of a meeting host. The target must pass its own attendee lookup rule.

OnlyMeetingOrGroupOrganizerCanSetMeetingMemberRolesRule looks for the setting member using IsActiveAttendee, derives host authority using IsActiveHost, and separately asks the group whether the member is an organizer. It rejects only when neither authority holds. Thus group organizer authority and meeting host authority are alternatives, not cumulative requirements. An ordinary group member has neither merely because they belong to the group.

OnlyMeetingAttendeeCanHaveChangedRoleRule checks target lookup using IsActiveAttendee. Its implementation, and the predicate differences from chapter 07, are more precise than the phrase active attendee might suggest. Preserve that exact source boundary in your worksheet. A proposed stricter target policy for removed records would be a separate change and should not be smuggled into expected current behavior.

Use three named identities: organizer Olivia, host Hari, and attendee Ana. Establish Olivia's group role through the existing fixture. Add Hari and Ana as group members and meeting attendees through valid paths. Promote Hari while Olivia has authority. Now a test can request Ana's promotion using Hari as actor, proving the host-authority path without accidentally exercising Olivia's organizer authority instead.

## Promotion checks before the visible child mutation

SetHostRole first checks start time, then actor authority, then target eligibility. It finds the target attendee and calls SetAsHost. The child assigns the host role and appends NewMeetingHostSetDomainEvent. The selected method contains no separate already-host guard in SetAsHost. Consequently, repeated promotion should be characterized from that implementation rather than assumed to be a no-op because the role value already matches.

A good positive test checks target identity in the new host event and verifies the intended state observation. A good rejection test makes the actor ordinary, keeps the meeting before start, and provides a valid target. Otherwise, a missing target or past meeting could intercept the call and leave the authority rule untested. The existing role tests illustrate separate organizer and host success paths; preserve that distinction in independent exercises.

For promotion, the visible guard sequence supports a narrower unchanged-state argument when one of those guards throws: SetAsHost has not yet been called. This still says nothing about an application transaction or other work done before the aggregate method. The claim is scoped to the inspected in-memory operation and its selected state, not generalized to every request that might invoke it.

## Demotion performs an additional check later

SetAttendeeRole begins with the same three aggregate checks. It finds the target and invokes SetAsAttendee. Inside the child, a rule rejects setting attendee role when the current role is already Attendee. If that rule passes, the child assigns Attendee and appends MemberSetAsAttendeeDomainEvent. Control returns to Meeting, which counts active hosts and only then checks MeetingMustHaveAtLeastOneHostRule.

Trace a future meeting whose creator is its sole active host. The creator can be the authorized setting member and the target. The early checks pass. The child changes the role and appends its event. The subsequent host count becomes zero, so the aggregate raises the last-host business-rule exception. The source order indicates mutation before that rejection. The existing last-organizer test asserts the exception rule; it does not demonstrate restoration of child role and event state afterward.

```text
actor and target checks
        |
        v
child role = Attendee
child event appended
        |
        v
count active hosts -> zero -> throw last-host rule
```

This trace is not evidence that a database transaction committed the changed role. An application boundary may discard the object, roll back persistence, or behave differently; that has not been executed here. Nevertheless, an in-memory all-fields-unchanged requirement cannot be inferred from the thrown exception. The distinction is material for callers that catch an exception and continue using the same aggregate instance.

## Build a before-and-after role worksheet

Record each child's stable member identity, role, active predicates, and relevant event count before invoking the method. Record aggregate event count separately because the demotion event belongs to the child. Freeze any collection snapshot into independent values; retaining a reference to the child and reading it after the operation is not a before snapshot.

For a two-host fixture, demote Hari while Olivia remains an active host. The intended current path succeeds and leaves one active host. The worksheet should show Hari as attendee, Olivia as host, and a new child event for Hari. For a one-host fixture, predict the exception and inspect post-call state in a proposed characterization. Do not write unchanged as an assumption merely because the operation is labeled unsuccessful.

A third row targets an ordinary attendee. The child's already-attendee rule rejects before assigning or appending its demotion event. This row differs from the last-host failure even though both calls reject. The first fails inside the child before mutation; the second fails after a successful child transition. A test suite that only counts thrown exceptions loses this important difference.

## Distinguish characterization from a proposed repair

A characterization test captures the observed current behavior, including surprising mutation order. A specification test describes an intended future contract, such as all state and event collections remaining unchanged on a rejected last-host demotion. Keep their names and expected outcomes explicit. A failing new specification can be a useful starting point, but it is not evidence that the repository already offers that guarantee.

One proposed repair strategy is to compute whether the target is an active host and whether its removal would leave another active host before mutating it. This requires care when the target is already an attendee or when lookup and active-host predicates disagree. Preserve the already-attendee rule and its identity where intended. Do not simply move a count check above mutation and compare it with zero: a pre-mutation count of one is precisely the risky case.

Another strategy is to prepare a proposed transition, validate it, then apply the change and append events. That can make future-state reasoning clearer, but it introduces design work beyond this lesson. A manual rollback approach must restore role and event state exactly, including any other child effects; it is easy to overlook an event. The independent exercise asks you to evaluate these approaches rather than edit the application during reading.

## Specify the invariant in future-state terms

The requirement at least one active host is about the resulting active host set. Define that set using the actual IsActiveHost predicate when characterizing current code. For a proposed repair, explicitly decide whether the active definition itself changes. Then derive the candidate result by removing the target from the host set only if the target is currently counted and the requested operation demotes it.

For example, two active hosts yield one after a valid demotion; one yields zero; a target who is not an active host may leave the count unchanged, but another rule can still reject the requested role operation. This decomposition avoids mixing authorization, target eligibility, transition legality, and resulting aggregate invariants into a single unexplained conditional.

Your tests should include self-demotion by an authorized host, demotion by a different organizer, and an unauthorized actor. These cases exercise different identities even when they reach the same final rule. Also consider the clock boundary: the shared start predicate is strict, so exactly-at-start behavior follows that comparison rather than an everyday interpretation of already started. Chapter 10 develops that lifecycle boundary in more detail.

## Review event assertions as part of role correctness

An emitted domain event is an in-memory record of a transition in this source. If a rejected operation leaves MemberSetAsAttendeeDomainEvent in a child collection, asserting only the aggregate's direct DomainEvents collection can miss it. The recursive test helper exists to inspect child collections; chapter 11 examines its limits. For a proposed unchanged-state contract, compare a stable projection of all relevant events before and after.

Be cautious about event names. MemberSetAsAttendeeDomainEvent exposes a property named HostId in the existing tests even though the target is becoming an attendee. A reviewer should trace the constructor arguments and asserted property rather than renaming the semantic role in memory. Naming consistency can be a future cleanup, but a current test must bind to the actual contract.

Repeated SetAsHost calls append events according to the inspected child method. Whether that should be idempotent is a product decision. A proposed idempotency change must define whether the caller receives success, whether a new event is suppressed, and whether audit timestamps should change. Those decisions cannot be inferred solely from assigning the same enum-like value twice.

## Independent practice

Exercise NA08-A, role transition matrix, is worth eight points. Predict early guard, child guard, role result, host count, and child event delta for two-host demotion, last-host demotion, already-attendee demotion, and unauthorized promotion. Clearly distinguish source-derived predictions from executed results.

Exercise NA08-B, repair design, is worth six points. Specify an all-fields-unchanged last-host rejection and propose a prevalidation algorithm. Include a case that would defeat the naive strategy of checking pre-mutation count equals zero. Preserve authorization and already-attendee behavior unless your written policy deliberately changes them.

Exercise NA08-C, evidence critique, is worth six points. Explain why the existing exception assertion, a root-only event check, and a retained mutable child reference are each insufficient for the stronger rejection contract. Design independent snapshots and state which integration evidence would still be needed before making a persistence claim. Consult [the solutions](SOLUTIONS-07-12.md) after completing the worksheet.


[Investigation workbook](INVESTIGATION-WORKBOOK-07-12.md) | [Course route](README.md)
