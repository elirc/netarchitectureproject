# Investigation workbook: six cases that challenge a shallow explanation

Use this workbook after the six chapters and before consulting their solution guide. These ungraded investigations extend the eighteen graded exercises with review conversations and concrete evidence records. They do not require changing original application code or learner data. Where a case asks for a mutation, use an owned disposable copy or generated adapter and label it as a proposal until executed.

## Case one: the right exception for the wrong request

A teammate reports that an invalid meeting interval test passes. The fixture creates a group with no valid payment period, and the assertion accepts any Exception. The test uses a positive interval rather than the intended equal interval because a helper calculated end from a different variable. The observed exception therefore says almost nothing about the claimed regression.

Build a diagnostic record with requested input, actual constructed command, fixture prerequisites, invocation stage, exception type, and BrokenRule. The first task is to establish which command values reached the handler. The second is to make the group valid enough to reach the interval decision. The third is to assert the specific rule. Replacing the exception message with a more attractive test name does not repair any of those gaps.

Add a positive asymmetric mapping case using the same valid fixture. If it cannot reach AddAsync, the fixture or invocation adapter remains suspect. Then add the equality case and verify that it rejects with the strict-order rule and no aggregate add. These cases complement each other because one establishes reachability while the other establishes rejection at the intended boundary.

The review question is whether the test would fail if the strict-order rule were removed. Under the original broken fixture and broad assertion, it might continue passing because the unpaid group rejects. A useful regression test needs to be sensitive to the defect it claims to prevent. Record that sensitivity through a disposable mutation or an equally clear counterfactual argument.

## Case two: a snapshot that changes with the object

A proposed all-fields rejection test captures a reference to the aggregate's attendee list and domain-event collection, invokes a broken mutation, and compares the same references afterward. The assertion reports equality even though an attendee role or event sequence changed. The before value was not a historical snapshot; it was another view of mutable state.

Design a value projection that copies the information needed for the invariant. For attendees, include stable member identity, active decision state, role, and guests if those properties are part of the tested behavior. For events, choose type and relevant aggregate identity or another normalized description. Do not compare random generated event ids unless they are central to the claim. Explain which ordering is meaningful and which should be normalized.

Now give the rejected main-attribute request a different title, valid new term, location, fee, and modifier. If the requested values equal the baseline, a premature assignment can occur invisibly. The intended negative rule must be isolated from those otherwise valid replacements. This makes the projection capable of detecting partial mutation rather than merely proving that an exception happened.

The review question is whether the snapshot is independent of the object after capture. A reliable answer identifies every mutable reference that was copied or transformed. Deep cloning an arbitrary aggregate through a serializer is not automatically correct because private state, value objects, and event types may not round-trip as intended. A deliberate test projection can be more transparent than a generic cloning trick.

## Case three: deterministic dates with a shared clock race

Two tests set SystemClock to different fixed instants and run concurrently. Each test individually uses a constant, yet one occasionally observes the other's time. This is not a contradiction: deterministic values do not make a shared static variable isolated. The clock's storage is shared across the process, and teardown in one test can reset it while another is still running.

Draw an interleaving: test A sets time before start, test B sets time after start, test A invokes IsAfterStart, and test B resets the clock. Predict the result A can observe. Then identify which coordination mechanism would prevent that interleaving in the chosen test framework or whether a future injected clock design would remove the shared state. Keep a proposed production refactor separate from a test-isolation change.

Also inspect direct DateTime.Now and DateTime.UtcNow calls in fixture construction. They do not read SystemClock and therefore continue using the real clock. A fixed domain time plus a real-time expiration fixture can unintentionally combine different temporal baselines. Capture one explicit instant and derive fixture values deliberately when designing new tests, while documenting which existing code still uses direct clock access.

The review question is whether the evidence establishes a domain rule or merely a favorable test schedule. A passing run without parallel execution may be sufficient for the bounded disposable lab, whose process owns its clock. It does not prove that every future parallel suite using the same static abstraction is race-free. State the execution model in the report.

## Case four: clamping creates a policy question

A meeting begins at ten. The proposed RSVP starts at eleven and has no end. The current SetRsvpTerm logic supplies the meeting start as the missing end while preserving the requested start. The resulting Term has a start after its end. The Term constructor does not reject that pair in the inspected source, and its inclusive membership conjunction can be false for every date.

Separate three statements. The source permits this construction path. The membership predicate has a predictable result for the resulting bounds. The business should or should not permit such an RSVP configuration is a policy decision requiring a specification. Do not turn the third statement into an undocumented source edit merely because the first two look unusual.

Propose two alternative policies and compare their consequences. One rejects an RSVP start later than the meeting start before any aggregate mutation. Another normalizes both bounds under a clearly stated rule. Rejection preserves the original request as evidence but requires actionable feedback. Normalization may be convenient but must not silently transform the learner's intended registration window in a surprising way.

For either proposal, design boundary cases at the meeting start, one tick before, and one tick after, with missing and present end values. Include an all-fields-unchanged rejection assertion if the policy rejects. Keep MeetingTerm's positive-duration invariant separate; it protects the meeting itself and does not automatically decide RSVP policy.

## Case five: a compile-compatible mapping defect

A generated adapter adds an hour to the requested end before calling MeetingTerm. Every type is correct, the interval remains positive, and the factory returns normally. A test that checks only construction success passes. A test that compares end to the adapter's own modified local variable also passes, because its expected value was contaminated by the same defect.

Use the original command's immutable requested end as the expected value and observe the resulting value object or captured aggregate. The assertion should fail with both values visible. This experiment distinguishes mapping preservation from domain validity. An interval can satisfy all local value-object rules while representing the wrong request.

Now consider a location swap among four strings. The domain may accept all strings, so a factory-level validity test will not reveal the mapping error. Distinct valid sentinels and component-level observations are needed. The same reasoning applies to actor identities when Guid wrappers share similar construction patterns: type-safe wrappers reduce some mistakes, but mapping the wrong source Guid into the correct wrapper can still compile.

The review question is where the oracle comes from. It should be the declared command contract and independent input values, not a second execution of the same mapper. Generated tests can be useful, but automatic expected-output generation from the implementation under test cannot establish that the implementation preserves the intended request.

## Case six: an event exists, but nothing was published externally

A unit test finds MeetingMainAttributesChangedDomainEvent in the aggregate's collection and a report says the notification reached other modules. The observation is real, but the conclusion crosses untested boundaries. Entity.AddDomainEvent appends in memory. Delivery may require later dispatch, persistence, transaction completion, an outbox, or another mechanism that must be inspected separately in the actual application.

Rewrite the report as three claims: the aggregate collected the event with the correct meeting id; the application pipeline handled or persisted that event according to its implementation; the external consumer observed the intended effect. Name an appropriate test boundary for each. A unit assertion supports the first. The remaining claims need their own source and integration evidence rather than a stronger adjective attached to the same test.

Also consider rejection. If a broken aggregate appends an event before a later rule throws, the event collection may contain a change that should not be treated as accepted. A complete rejection projection includes events because they are part of the aggregate's observable state. A persistence rollback might prevent later publication while still leaving the in-memory object altered; those are distinct observations.

The review question is whether the event's payload and timing match the state transition being claimed. Counting one event of the right type is weaker than checking its aggregate identity and relating it to a successful mutation. A source-bound test should state exactly which payload properties it inspects and which later delivery guarantees remain unverified.

## Evidence card template

Write the claim in one sentence with a concrete input and observable. Name the original source files and the test or disposable adapter used. State fixture preconditions, especially group validity, clock ownership, and baseline events. Record the exact working directory and command. Separate compilation, execution, assertion result, and cleanup. Finally, state the strongest unsupported conclusion a reader might be tempted to infer, and explicitly exclude it.

For a baseline lab run, the supported claim is that the selected copied temporal types passed the named cases in the SDK-only environment. For a broken mode, the supported claim is that a particular semantic assertion detected the deliberate mutation after compilation succeeded. For an unavailable full-project run, the honest result is that the broader boundary remains unexecuted. These records let another engineer reproduce the reasoning without confusing plans, source inspection, and observed behavior.

## Peer-review protocol

Exchange one workbook case with another learner. The reviewer changes exactly one premise and asks for a new prediction before allowing another tool run. Examples include a different actor id, a preexisting event, a one-tick interval, an expired group, or a later clock value. The author must identify the boundary affected and the assertion that should change.

Then review one conclusion for overreach. Look for statements equating repository add with commit, collected event with delivery, fixed values with isolated time, or a successful factory with correct mapping. Rewrite the claim at the strongest level its evidence actually supports. This is a practical architectural skill: precise evidence makes both defect diagnosis and future design discussion faster.
