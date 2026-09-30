# 20. Capstone: an evidence packet another engineer can challenge

The final capstone assesses investigation quality across layers without requiring a broad rewrite. Choose one of two tracks: rejected last-host demotion, or outbox publication followed by processed-marker failure. Both have concrete source-order questions already examined in the course. Your task is to produce a precise characterization, a proposed contract, a bounded experiment plan, and a review decision that never claims more than the evidence supports.

The course provides a complete learning route through this chapter, the separate solutions, and the runnable disposable labs. Optional implementation and integration experiments remain learner assignments, not unfinished promises that the application has already changed. Finishing the course means being able to reason and review at these boundaries, not installing every dependency or running destructive fixtures merely to collect more output.

## Track A: rejected host demotion

Use [Meeting.SetAttendeeRole](../../../modular-monolith-with-ddd/src/Modules/Meetings/Domain/Meetings/Meeting.cs), [MeetingAttendee.SetAsAttendee](../../../modular-monolith-with-ddd/src/Modules/Meetings/Domain/Meetings/MeetingAttendee.cs), and [MeetingRolesTests](../../../modular-monolith-with-ddd/src/Modules/Meetings/Tests/UnitTests/Meetings/MeetingRolesTests.cs). State the current source order: early aggregate guards, child transition and event, resulting active-host count, and last-host rule. Distinguish that prediction from any executed characterization you later perform.

The proposed contract is all affected in-memory state and events unchanged when last-host demotion rejects. The successful two-host demotion must remain possible. Actor authorization and target eligibility remain separate concerns. Do not solve the assignment by rejecting every role change or by catching and suppressing the rule exception while leaving the child mutated.

Your experiment plan should include one-host rejection, two-host success, already-attendee rejection, and unauthorized actor rejection. Use distinct identities and a controlled future term. Capture independent child and event snapshots before invocation. If implementing a repair later, show why its future-state validation preserves the intended exception boundaries or explicitly documents a deliberate priority change.

## Track B: outbox marker failure

Use [ProcessOutboxCommandHandler](../../../modular-monolith-with-ddd/src/Modules/Meetings/Infrastructure/Configuration/Processing/Outbox/ProcessOutboxCommandHandler.cs) and [DomainEventsDispatcher](../../../modular-monolith-with-ddd/src/BuildingBlocks/Infrastructure/DomainEventsDispatching/DomainEventsDispatcher.cs). State the current source order for later processing: select unprocessed rows, deserialize notification, publish through mediator, then update ProcessedDate. Do not call that sequence exactly-once delivery without recipient and transaction evidence.

The proposed experiment uses an owned message fixture and a recipient test double that records attempts separately from durable effects. Inject failure after successful recipient work but before successful marker update. Observe the marker and then replay through the chosen boundary. The experiment must never send real email or contact an external production service merely to demonstrate duplicate risk.

The contract you propose may require an idempotent recipient, a stronger processing protocol, or a narrower documented delivery guarantee. Choose one and explain its stable operation identity and failure behavior. Avoid adding a boolean to the handler without considering the failure window between the recipient's effect and the marker. The design must account for the actual order it is trying to improve.

## Build a claim ledger

Every material claim belongs in a ledger with five fields: claim, source anchor, observation method, result, and limitation. For example, the domain method mutates before the final rule is a source-order claim. The same instance has a changed role after rejection is an executed domain-state claim only if the experiment ran. The database committed that role is a persistence claim requiring additional evidence.

For the outbox track, publication was invoked and the recipient completed are separate claims. A log line before an await does not establish completion. A processed marker being null does not establish that no recipient acted. A replay attempt count does not automatically equal duplicate durable effects if the recipient deduplicates. The ledger should preserve these distinctions rather than combine them into one failure statement.

Use concise source links and synthetic identifiers. Record exact commands only when they were actually run, with build and semantic outcomes. Planned commands belong in the experiment plan, not the execution receipt. This makes the packet reviewable even when some integration prerequisites are unavailable.

## Make the oracle independent

For track A, the oracle is the explicit before projection and the specified unchanged-state requirement, plus positive success controls. Do not derive expected host count from the same mutated list after invocation. Do not compare two live views of the same event collection. Do not rely solely on the expected exception type.

For track B, the oracle separates message identity, attempt count, durable-effect count, and marker state. Do not use the processed marker as the only evidence that the recipient ran. Do not let the same mutable log object serve as both before and after state. A recipient test double should have an explicit behavior contract so the experiment does not accidentally assume the guarantee it is meant to test.

In either track, introduce one conceptual mutation that should survive a weak test and fail your stronger oracle. Track A can append an event before rejection while leaving the final role unchanged. Track B can record an attempt before failing and reveal a report that wrongly equates attempts with effects. Explain exactly which assertion distinguishes the cases.

## Diagnose failures in causal order

First confirm the fixture reaches the intended method. Next confirm prerequisites and earlier guards. Then identify the first mutation or external attempt, the injected failure point, and the observation boundary. A setup failure is not evidence about the target behavior. A compile failure is not a semantic mutation result. A timeout with no diagnostic observations is not enough to identify a concurrency bug.

If an experiment differs from prediction, preserve both the original prediction and the actual result. Revise the model only after locating the differing source path or fixture condition. Changing expectations until the suite passes without explanation destroys the independence of the exercise. A useful investigation can conclude that the initial hypothesis was wrong and still earn strong credit for precise evidence.

Keep scope narrow. A role-order investigation need not redesign all membership predicates. An outbox marker experiment need not replace the messaging architecture. Record adjacent findings with source pointers and proposed follow-up tests, but do not claim they were repaired or verified as part of the chosen capstone.

## Produce a reviewer decision

The final packet should let a reviewer choose among accepting the characterization, accepting the proposed design with unexecuted integration work noted, or accepting an implemented change with sufficient evidence. These are different decisions. A design can be useful and complete as a design while remaining unimplemented. An implementation cannot borrow completion credit from a detailed plan for tests that never ran.

Lead the review narrative with the observed or proposed behavior and its consequence. Then give the strongest evidence, the remaining limits, and the next concrete experiment if needed. Avoid recounting every tool invocation. A reviewer needs the causal argument and reproducible artifacts, not a transcript of exploratory commands.

State whether application code changed, which tests ran, which source files were preserved, and which environment boundaries were not entered. The course's own authoring report follows that pattern: documentation and disposable labs were added, application source was preserved, bounded real-source cases ran, and full database and HTTP suites were not claimed.

## Sixty-point capstone rubric

Award twelve points for a precise chosen contract and accurate current-source trace. Award twelve for independent state or effect oracles that distinguish rejection, attempts, and completed effects. Award ten for fixture isolation and failure injection at the intended stage. Award ten for positive controls, mutation discrimination, and repeat-behavior reasoning.

Award eight points for source, domain, persistence, and transport evidence boundaries. Award eight for a concise reviewer packet with exact results and honest limitations. A design-only submission should be graded on the quality and completeness of its specified experiment while clearly receiving no claim of executed behavior. An implementation-route submission must include its actual results and cannot substitute planned checks for missing verification.

Material errors include treating a thrown exception as automatic state restoration, treating an in-memory event as delivered externally, treating a marker as proof of exactly-once effects, or running an unowned destructive fixture. Correct those errors before considering the capstone complete. They undermine the evidence model rather than merely reducing presentation quality.

## Course completion assessment

You should now be able to follow a value from request to command, factory, aggregate, mapping, query, and response without assuming every layer executes the same policy. You should be able to distinguish active predicates, historical records, occupied places, and read-model rows. You should recognize that event ownership and event delivery are separate questions, and that rejection requires explicit before/after evidence when unchanged state matters.

Use the two disposable labs as calibration exercises. Predict their boundary cases before running; interpret expected mutation failures by stage; and preserve the selected source-hash receipts. Their success does not certify the full application, but it gives real execution evidence for the specific temporal and capacity rules they compile. The rest of the course teaches how to extend that evidence deliberately.

Optional future work includes implementing either capstone, running an owned integration environment, adding a hosted API fixture, and investigating concurrency under controlled processors. These are clearly optional extensions beyond the completed instructional route. No required chapter remains planned-only, and no optional exercise is represented as a shipped feature.

## Independent preparation exercises

Exercise NA20-A, claim ledger, is worth eight points. Choose a track and write five claims at distinct evidence boundaries, including one tempting overclaim and its corrected wording. Attach source anchors and specify the observation needed for each claim.

Exercise NA20-B, independent oracle, is worth six points. Design the before/after or attempt/effect projection and a mutation that defeats a weaker test. Include a positive control and explain why a setup or compiler failure would not satisfy the experiment.

Exercise NA20-C, reviewer decision, is worth six points. Write a short acceptance decision for a design-only packet and for an implementation packet with missing persistence evidence. State exactly what is complete in each and what remains unverified. These twenty preparation points are separate from the sixty-point capstone rubric. Use [the final solutions](SOLUTIONS-13-20.md) after completing your own assessment.


[Complete course route](README.md) | [Separate solutions and assessment](SOLUTIONS-13-20.md)
