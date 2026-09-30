# Investigation workbook: interacting aggregate operations

These ungraded investigations extend the eighteen graded exercises in chapters 07-12. They require written predictions and source pointers, not application edits. Use a fresh worksheet for each case and keep current behavior, desired policy, and executed evidence in separate columns. The [solutions](SOLUTIONS-07-12.md) explain the component rules, but the cases below ask you to combine them without assuming a universal aggregate contract.

## Case A: the capacity dashboard disagrees

A learner counts three attendee records and concludes that a meeting with a limit of five has two free places. The fixture contains the creator host, Ada with two guests, and Ben with zero guests. Before investigating UI code, compute occupied places using the aggregate's active filter and child contribution. There are five places, so the next zero-guest member would require six. The record count was a different unit, not an arithmetic error in subtraction.

Now mark Ada removed in the hypothetical state and compare the capacity predicate with member lookup. Capacity excludes her removed record, but IsActiveAttendee can still match her unchanged-decision identity. This can produce different answers to has occupied places and can be found by attendee lookup. Document the predicate expressions before calling the whole state inconsistent. A proposed domain policy might unify them, but doing so affects duplicate detection and role or removal targets.

Your deliverable is a two-row before/after ledger with records, active records, occupied places, and Ada's lookup result. Add one test boundary that the disposable capacity lab covers and one that requires the real aggregate fixture. Explain why a screenshot of the dashboard cannot, by itself, identify which domain count the UI actually used.

## Case B: the rejected demotion appears successful later

An operation reports the last-host rule, yet a later in-memory inspection sees the target as an attendee. Reconstruct the current SetAttendeeRole sequence. The child changes role and adds an event before the aggregate checks the resulting host count. That source order makes the observation plausible without requiring a second command or a background worker.

Prepare two competing claims: the object changed before rejection, and the database committed the changed role. The first can be investigated with independent domain snapshots around one invocation. The second needs the application transaction and persistence path. Do not use evidence for the first as proof of the second. Also do not assume that a database rollback rewinds an object already held by the caller.

Write a proposed regression specification requiring unchanged child role and events. Explain why checking only the thrown rule would retain the original weakness. Include a two-host success control so a fix that rejects every demotion cannot pass the suite. Your review packet should identify which parts are source predictions and which would require an actual characterization run.

## Case C: a queue promotion has an unexpectedly old date

Ben joined a waitlist at 09:05 and was promoted at 09:20. An attendee-added event uses 09:05 as its decision date. Trace the arguments supplied to MeetingAttendee.CreateNew during promotion. The old date is explicitly the waitlist SignUpDate, while the moved timestamp is recorded separately using the current clock. The observation follows the selected implementation rather than proving a stale clock.

Compare this with a normal AddAttendee call, which supplies SystemClock.Now as the decision date. The same child constructor receives different date sources depending on the parent path. A test that asserts every attendee decision date equals the command invocation time would encode a broader policy than the source provides.

Your deliverable is an argument-origin map for normal addition and promotion: member identity, date, role, guests, and fee. Then propose whether a product-facing report should display queue signup, promotion, or attendance-decision time. Label that display choice as a product decision until the read model and UI are inspected. Do not silently rename the stored event field to make your preferred interpretation fit.

## Case D: cleanup leaves an event behind

A test calls ClearAllDomainEvents and later finds a child event that was supposed to be fixture noise. First verify that the helper was called on the same reachable object graph as the operation. Clearing a MeetingGroup does not automatically clear a separately referenced Meeting whose association is only represented by an identifier.

Next inspect the shape of the child reference. List elements are handled by a runtime Entity test, while direct entity fields use an assignability expression that differs between collecting and clearing. A controlled helper characterization can distinguish these paths. Do not immediately rewrite production event handling because a test cleanup helper behaved unexpectedly.

Finally check whether the before variable was a live read-only view of the backing event list. Clearing or appending changes what that view exposes. An independently materialized projection makes the timing of observation explicit. The deliverable is a three-step diagnostic plan that narrows graph identity, traversal shape, and snapshot independence before considering external dispatch infrastructure.

## Case E: a retry passes yesterday and fails today

A canceled meeting receives the same cancellation request again. Before start, the method passes its initial guard and skips the already-canceled mutation block. After start, it raises the time rule before reaching that block. The input is not identical when time is part of the domain state, even if the serialized command arguments are unchanged.

Design a table with original cancellation time, replay time, stored actor, stored date, event delta, and exception result. Include a different actor on replay to demonstrate that the skipped mutation does not overwrite cancellation metadata. Then state a proposed transport retry contract and identify where it would need to be implemented or translated. Do not assume a domain exception automatically maps to a particular HTTP status.

The lesson is not that retries should always succeed or always fail. It is that a useful repeatability claim names the boundary and relevant state. Your receipt should say conditional no-op before start when that is the actual evidence, rather than using an unqualified idempotent label.

## Peer review protocol

Exchange one case with another learner. The reviewer should identify an independent expected value, the earliest guard that could intercept the scenario, the first visible mutation, the event owner, and the strongest claim the evidence supports. The author should then revise any claim that crosses an unexecuted boundary.

A strong review can preserve a surprising current behavior while recommending a separate policy change. It does not need to defend every source choice or repair everything encountered. The immediate goal is a precise, reproducible investigation that lets a later implementation task change one contract deliberately and assess its consequences.
