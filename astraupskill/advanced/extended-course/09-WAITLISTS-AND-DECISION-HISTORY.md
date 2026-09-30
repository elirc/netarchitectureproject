# 09. Waitlists, decision history, and promotion boundaries

A waitlist sounds like a simple queue until it interacts with changed attendance decisions, historical records, fees, and capacity. Read the waitlist methods in [Meeting](../../../modular-monolith-with-ddd/src/Modules/Meetings/Domain/Meetings/Meeting.cs), [MeetingWaitlistMember](../../../modular-monolith-with-ddd/src/Modules/Meetings/Domain/Meetings/MeetingWaitlistMember.cs), [MeetingNotAttendee](../../../modular-monolith-with-ddd/src/Modules/Meetings/Domain/Meetings/MeetingNotAttendee.cs), and [MeetingWaitlistTests](../../../modular-monolith-with-ddd/src/Modules/Meetings/Tests/UnitTests/Meetings/MeetingWaitlistTests.cs). The chapter characterizes the visible source and separates proposed stronger queue policy from current implementation.

The learning objective is to follow one identity across multiple records without treating a list removal, a status flag, and an attendance decision as interchangeable. Use distinct fixed identities and controlled times in your worksheet. A chronological diagram is useful only when the diagram's transitions correspond to actual statements in the method.

## Signing up creates a history-bearing child

SignUpMemberToWaitlist checks the meeting start boundary, RSVP membership, group membership, and duplicate active waitlist membership. It then appends a newly created MeetingWaitlistMember. The child records SignUpDate using SystemClock.Now, starts as not moved to attendees, and adds MeetingWaitlistMemberAddedDomainEvent. Its active predicate requires that it is neither signed off nor moved to attendees.

The membership rule receives the attendee collection in its constructor, but its IsBroken expression checks group membership only. Do not infer an exclusion of existing attendees from the presence of the unused field. Similarly, the selected signup method does not visibly require the meeting to be full before joining the waitlist. If your desired product policy requires either condition, write that as a proposed requirement with an independent test and inspect other entry points before making an end-to-end claim.

Duplicate detection is based on active waitlist records for the identity, not on every historical record. After a record becomes inactive, a later signup can create another record if all current guards pass. This is different from reactivating the old record. A timeline should retain both records and their different signup dates so that ordering and event history remain understandable.

## Signing off changes status without erasing history

SignOffMemberFromWaitlist checks the start boundary and requires an active waitlist record. It retrieves that record and calls SignOff. The child sets its signed-off flag and sign-off date using SystemClock.Now, then appends MemberSignedOffFromMeetingWaitlistDomainEvent. The record remains in the collection but no longer qualifies as active.

A second signoff normally fails the active-record rule because the first call changed the predicate result. A later signup can produce a new active record, leaving the signed-off record as history. Avoid a test that merely asserts collection count after signing off: unchanged count is expected under this representation. Assert active membership and the appropriate event or date projection instead.

The existing tests check rejecting a nonactive member and verify the member identity in a successful signoff event. A broader lifecycle test could additionally freeze the first record, rejoin at a later time, and verify that only the new record is active. That is a proposed extension to coverage, not a statement that the inspected suite already executes the whole timeline.

## Adding a not-attendee can trigger promotion

AddNotAttendee first checks the start boundary and duplicate active not-attendee status. It appends a new MeetingNotAttendee, finds an attendee for the identity, and changes that attendee's decision if found. It then searches all active waitlist records, orders them by SignUpDate, and selects the first. If one exists, it creates a new attendee for that member and marks the waitlist record as moved.

Notice the trigger's exact shape. Promotion is not visibly conditional on finding an attendee to free a place. It follows adding the not-attendee record even when the nullable attendee lookup finds none. The method also does not call the normal AddAttendee guard sequence for the promoted member. These are important source observations for capacity and duplicate-policy review. They should not be rewritten in prose as a guarantee that a newly freed seat is always required.

The promoted attendee receives the waitlist member's SignUpDate as its decision date, zero guests, the ordinary attendee role, and the meeting's current event fee. The moved timestamp is separately set to SystemClock.Now. Those dates answer different questions: when the member joined the queue and when the record was moved. Conflating them hides the actual constructor arguments.

## Work a three-person timeline

Assume a future meeting and valid group membership. Set the clock to 09:00 and sign up Ada. At 09:05 sign up Ben. At 09:10 sign Ada off. At 09:15 sign Ada up again. The collection now contains three records: Ada's inactive first record, Ben's active record, and Ada's active second record. The next selection by signup time considers only the latter two and selects Ben.

At 09:20, add a not-attendee through a fixture that satisfies its guards. Ben's new attendee receives 09:05 as decision date and zero guests. Ben's waitlist record is marked moved at 09:20 and becomes inactive. Ada's second record remains active. The collection does not shrink merely because Ben moved. Record both identity and record occurrence in the worksheet so that Ada's two entries are not accidentally merged.

Now change the meeting fee between 09:05 and 09:20 in a valid hypothetical setup. The promotion code supplies the current meeting fee when constructing the attendee, not a fee snapshot stored on the waitlist member. Whether price should instead be reserved at signup is a proposed business-policy question. The selected child has no shown fee field that would support claiming such reservation.

## Ordering ties need an explicit policy

The method orders by SignUpDate and chooses the first active record. With distinct timestamps, the intended selection is clear. With equal timestamps, the expression contains no explicit secondary business key. The current in-memory list and ordering behavior may produce a repeatable result for a particular fixture, but do not describe that as a documented cross-storage fairness rule without further evidence.

A proposed deterministic policy could add a stable sequence number or another explicit tie-breaker. Before choosing one, define whether fairness means arrival at the API, acceptance by the aggregate, or committed database order. Those clocks and concurrency boundaries can differ. A source-only queue exercise should stay with distinct controlled timestamps unless tie behavior is its stated subject.

Your independent tests should include one signed-off earlier record, one moved earlier record, and two active records with distinct times. That proves the filter and the ordering independently. A test containing only active records cannot detect a missing active filter; a test with only one active record cannot distinguish ascending from descending ordering.

## Decision changes retain multiple views of participation

MeetingNotAttendee.IsActiveNotAttendee checks identity and that the decision-changed flag is false. Its ChangeDecision sets the flag, records SystemClock.Now, and appends a changed-decision event. Normal AddAttendee can call that method before appending the new attendee. ChangeNotAttendeeDecision can also deactivate an active not-attendee record without itself adding an attendee.

Therefore, not active not-attendee does not imply currently attending. It only describes that record's decision status. Similarly, a moved waitlist record is no longer active on the queue, but understanding current attendance still requires the attendee history. A UI query that treats absence from one collection as membership in another would need explicit justification.

There is also a clock boundary in the source: MeetingNotAttendee construction uses DateTime.UtcNow for its decision date, while its change date uses SystemClock.Now. Setting the test clock controls the latter and the waitlist times, but not that constructor's direct wall-clock read. A deterministic all-date assertion must account for this distinction. Do not assume every temporal field honors the shared clock simply because the aggregate often uses it.

## Design a stronger promotion policy as an exercise

A proposed policy might require a real capacity release, recheck the promoted member's eligibility, and prevent simultaneous active attendance and waitlist status. Such a policy affects more than one line. Define what happens when the earliest waitlist member is no longer eligible: reject the entire operation, skip and retain them, skip and deactivate them, or stop promotion. Each answer has different fairness and audit consequences.

Define guest handling separately. The current waitlist record does not store a requested guest count; promotion supplies zero. A new guest-aware queue would need a data model, capacity accounting, and a rule for a request larger than the available places. Choosing the next smaller party instead of the oldest changes the fairness policy. Do not add that behavior merely by reusing a capacity helper.

Finally define event evidence for the transition. The current promotion creates an attendee-added event through the child constructor and marks the waitlist record moved without a dedicated event in that method. A proposed moved event could help consumers distinguish paths, but it would be a new contract. First document what can already be inferred from current event payloads and what cannot.

## Independent practice

Exercise NA09-A, history timeline, is worth eight points. Complete the Ada and Ben timeline with record count, active queue identities, selected member, attendee decision date, and moved date. Explain why deleting Ada's first record from your worksheet would hide useful history.

Exercise NA09-B, source versus policy, is worth six points. Evaluate three claims: signup requires a full meeting, an attendee cannot join the queue, and adding a not-attendee promotes only after freeing capacity. For each, identify the inspected method or predicate and state the source-supported conclusion without making an unverified transport claim.

Exercise NA09-C, queue redesign, is worth six points. Specify a stronger promotion policy for an ineligible earliest member and a party with guests. Include tie handling, all-fields-unchanged rejection, and event expectations. Keep the proposed contract separate from characterization tests. Compare your design with [the solution discussion](SOLUTIONS-07-12.md), which offers reasoning rather than a single mandatory product policy.


[Investigation workbook](INVESTIGATION-WORKBOOK-07-12.md) | [Course route](README.md)
