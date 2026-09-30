# 10. Cancellation, removal, and time-dependent repeat behavior

Lifecycle commands are often described as idempotent or forbidden after start. Those phrases conceal important qualifications. Inspect Cancel, RemoveAttendee, and MarkAttendeeFeeAsPayed in [Meeting](../../../modular-monolith-with-ddd/src/Modules/Meetings/Domain/Meetings/Meeting.cs), the removal and fee methods in [MeetingAttendee](../../../modular-monolith-with-ddd/src/Modules/Meetings/Domain/Meetings/MeetingAttendee.cs), and [MeetingTests](../../../modular-monolith-with-ddd/src/Modules/Meetings/Tests/UnitTests/Meetings/MeetingTests.cs). This chapter develops an operation-by-operation contract rather than assuming every method follows one lifecycle policy.

The task is to distinguish the state a command changes, the guards it evaluates, the events it records, and the behavior of a repeated call at a different time. All examples below are source-derived predictions unless an explicitly identified lab or existing test execution provides additional evidence. The application is not changed by the course.

## The start boundary is a comparison, not a slogan

MeetingCannotBeChangedAfterStartRule delegates to MeetingTerm.IsAfterStart, which compares SystemClock.Now strictly greater than StartDate. At a time one tick before start, the rule is not broken. At exactly start, it is still not broken. One tick after, it is broken. The temporal lab from chapter 06 executes this distinction over real copied source.

Use a fixed UTC start at 10:00 and a later end. Do not repeatedly call the wall clock while constructing a boundary fixture. Construct the term once, then set SystemClock to the three exact instants for separate fresh fixtures or carefully isolated calls. Otherwise a test intended for equality may drift into the after-start case between setup and invocation.

The phrase cannot be changed after start describes a shared rule used by selected methods. It does not establish that every public method invokes it. ChangeMainAttributes and MarkAttendeeFeeAsPayed do not show the same start guard in their selected bodies. A course explanation should name the methods inspected rather than generalize the rule into an aggregate-wide interceptor that does not appear in the source.

## First cancellation records three values and an event

Cancel checks the start rule before examining the canceled flag. If the meeting is not already canceled, it sets the flag, captures SystemClock.Now as cancellation date, stores the supplied member identity, and adds MeetingCanceledDomainEvent containing the meeting, member, and date. The selected method does not visibly validate organizer authority. Any authorization in application or transport layers would need its own inspection.

The existing positive cancellation test sets SystemClock to a captured date, calls Cancel with the creator identity, and asserts the event's meeting identity, cancel member identity, and cancel date. This is a focused payload check. It does not prove that only creators may cancel, because the fixture supplies a creator without testing a rejecting alternative. Positive examples establish acceptance for their input, not exclusivity of that input class.

A proposed direct state snapshot can also inspect the canceled flag and stored cancellation metadata. If using reflection in a learning test, keep that inspection isolated and make missing fields fail clearly. Do not add public getters merely to make a one-off worksheet easier; that would change the domain API for a test convenience rather than a product need.

## Repetition depends on when it occurs

Call Cancel twice before start. The first call sets state and adds an event. The second passes the start guard, sees the flag already true, and skips the mutation block. It leaves the original cancel date and member unchanged and adds no second cancellation event. If the second call supplies a different member, that identity is not substituted into the existing cancellation metadata by the visible code.

Now advance the clock beyond start and call Cancel again on the already canceled meeting. The start guard executes before the canceled check and throws. Thus the method is not an unconditional successful no-op for every repeated cancellation. Its repeat behavior is conditional on the time guard. This distinction matters for retry contracts, even though no transport retry behavior has been executed in this chapter.

```text
Cancel(actor)
  evaluate start rule
  if broken: throw
  if already canceled: return with no new cancellation event
  otherwise: flag + date + actor + event
```

A test named cancellation is idempotent should state the time assumptions or use a more precise name. The source supports stable state and event count for repeated calls that pass the initial guard. It does not support claiming all possible replays produce the same successful result regardless of clock changes.

## Cancellation does not imply every other method checks the flag

The selected AddAttendee, role, waitlist, and removal methods visibly check their own guards; they do not automatically inherit the Cancel method's flag branch. Do not draw a lifecycle diagram with a canceled terminal state that forbids every operation unless the implementation or a proposed policy actually enforces it. A field representing cancellation is not itself a universal dispatch guard.

A useful source audit lists each operation and asks whether it reads the canceled flag, reads the term, checks authority, and mutates children. This matrix is evidence about selected method bodies. It remains separate from the request path, where validators, handlers, or authorization may constrain entry. The matrix can reveal a domain consistency question without pretending to have proven a production incident.

If you propose cancellation as a terminal state, define exceptions deliberately. Fee settlement might remain allowed after cancellation; comments might be restricted; administrative corrections might require a different command. A blanket rule can be simpler but may conflict with legitimate post-event work. State the desired policy before choosing where to place a guard.

## Removal has a child-level reason check

RemoveAttendee checks the start boundary, then requires a lookup matching OnlyActiveAttendeeCanBeRemovedFromMeetingRule. It retrieves the attendee and calls Remove with the removing identity and reason. The child checks ReasonOfRemovingAttendeeFromMeetingMustBeProvidedRule before setting its removal fields or appending MeetingAttendeeRemovedDomainEvent.

That reason rule uses string.IsNullOrEmpty. Null and the empty string reject; a whitespace-only string is not rejected by that expression. Trimming and rejecting blank text would be a proposed stronger policy. An assertion that whitespace must fail is therefore a specification for a change, not a characterization of this particular predicate.

On accepted removal, the child sets its removed flag, removal date using SystemClock.Now, reason, and removing member identity, then records an event with attendee identity, meeting identity, and reason. Capacity later uses IsActive and therefore excludes the removed child. The lookup predicate discussed in chapter 07 has a different removal condition, so repeat removal needs its own characterization rather than an assumed already-removed rejection.

## Reason about repeat removal through exact predicates

OnlyActiveAttendeeCanBeRemovedFromMeetingRule uses IsActiveAttendee, which checks identity and unchanged decision rather than the removed flag. A first removal does not set the decision-changed flag in the selected child method. Consequently, the source suggests that a repeated removal before start can find the same record, overwrite removal metadata, and append another removed event when the reason passes. This is a source-derived prediction for a proposed characterization, not a newly executed aggregate result.

If the desired policy is one removal event per participation record, define how repeated calls should behave: reject, return success without change, or update an administrative correction with a different event. These choices affect audit interpretation. Reusing a removal event for both initial removal and correction can obscure whether consumers should decrement a count twice.

A meaningful unchanged-state rejection test uses a valid attendee and an invalid reason, takes independent snapshots, invokes once, and checks the specific reason rule. A missing attendee with a null reason tests the earlier eligibility guard instead. The existing tests separate those concerns by constructing membership and attendance for the reason case.

## Fee marking is another contract, not a lifecycle template

MarkAttendeeFeeAsPayed retrieves an attendee and invokes MarkFeeAsPayed. The child sets a paid flag and appends MeetingAttendeeFeePaidDomainEvent. The selected method does not include the shared start guard or an explicit duplicate-paid guard. It also does not visibly add a custom missing-attendee rule before invoking the retrieved result.

Do not convert those observations into assumptions about payment processing. The method records domain state; it is not evidence of a gateway charge, refund, receipt, or financial settlement. A repeated paid event may or may not be acceptable to downstream handlers, which must be inspected separately. A proposed idempotency requirement should specify both state and event behavior and identify the caller's replay boundary.

This operation is a useful reminder that a naming pattern does not provide uniform semantics. Cancel has a flag-protected mutation block, Remove does not use the same repeat pattern, and fee marking follows another path. Review each method's guards and effects rather than importing one method's contract into its neighbors.

## Create a lifecycle evidence matrix

Use rows for Cancel, RemoveAttendee, SetHostRole, SignOffMemberFromWaitlist, ChangeMainAttributes, and MarkAttendeeFeeAsPayed. Use columns for start guard, actor-authority check in the selected method, target lookup, duplicate-state behavior, direct aggregate events, and child events. Fill a cell with a source pointer or explicitly not inspected. Do not use a blank cell to mean both absent and unknown.

For repeat behavior, include time as an input. The same object and same command arguments can follow a different path after the clock advances. For event assertions, compare deltas from a baseline rather than total counts contaminated by fixture creation. For state assertions, distinguish values that should remain stable from values intentionally overwritten by the current method.

This matrix supports an engineering conversation about consistency without prescribing uniformity. Some operations should legitimately be repeatable while others reject. The quality criterion is whether each behavior is intentional, testable, and described at the correct boundary. A precise exception to a policy is better than an attractive diagram contradicted by source.

## Independent practice

Exercise NA10-A, cancellation timeline, is worth eight points. Predict flag, stored actor, stored date, event delta, and exception behavior for first cancellation before start, a second cancellation by another member before start, and a third after start. Include the exact-start variant and explain the comparison that controls it.

Exercise NA10-B, removal specification, is worth six points. Separate current null, empty, and whitespace reason behavior from a proposed trimmed nonblank policy. Design a test isolating the reason guard and a characterization for repeated removal. Avoid claiming database persistence from child state alone.

Exercise NA10-C, lifecycle matrix, is worth six points. Fill the selected-method matrix and critique the statement that every meeting change is forbidden after cancellation. Name the additional source and execution evidence needed to turn a domain observation into an endpoint claim. Compare your conclusions with [the solutions](SOLUTIONS-07-12.md).


[Run the bounded capacity and reason lab](LAB-CAPACITY-07-12.md) after writing predictions. [Investigation workbook](INVESTIGATION-WORKBOOK-07-12.md) | [Course route](README.md)
