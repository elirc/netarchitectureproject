# 19. Capstone: a complete domain invariant extension

This capstone turns the proposed title policy from chapter 12 into a complete engineering assignment. The course delivers the specification, evidence plan, review gates, and assessment rubric; it does not implement the feature in the application or overwrite learner work. You may complete the design-only route without a database, or undertake the implementation route later in an owned development workflow. State which route your submission follows.

Use [Meeting](../../../modular-monolith-with-ddd/src/Modules/Meetings/Domain/Meetings/Meeting.cs), [the change handler](../../../modular-monolith-with-ddd/src/Modules/Meetings/Application/Meetings/ChangeMeetingMainAttributes/ChangeMeetingMainAttributesCommandHandler.cs), [the mapping configuration](../../../modular-monolith-with-ddd/src/Modules/Meetings/Infrastructure/Domain/Meetings/MeetingEntityTypeConfiguration.cs), and [the details query](../../../modular-monolith-with-ddd/src/Modules/Meetings/Application/Meetings/GetMeetingDetails/GetMeetingDetailsQueryHandler.cs) as the required source anchors. The assignment crosses these boundaries deliberately rather than stopping at a green value-object test.

## The product request

A meeting title should be normalized by trimming surrounding whitespace, should preserve internal whitespace, and should contain between five and eighty .NET string-length units after trimming. Null or invalid-length input rejects. Creation and main-attribute change should use the same domain policy. Accepted titles should be observable in the read-model projection in normalized form after successful persistence on the implementation route.

On rejected main-attribute change, all affected fields and relevant event collections must remain unchanged. On rejected creation, the handler must not add a new meeting through its repository. This requirement is intentionally stronger than the existing term-only rejection assertion. You must also preserve the existing interval, capacity, RSVP, fee, membership, and role behavior outside the explicitly changed title policy.

The requested feature does not include new UI screens, authentication redesign, dependency upgrades, or broad aggregate refactoring. A good implementation may reveal adjacent issues, but it records them separately instead of expanding scope until the original change becomes impossible to review. The capstone assesses precision and integration, not the number of files edited.

## Deliverable one: a contract and boundary table

Write a compact policy document with exact input and stored-output examples. Include null, empty, whitespace-only, four, five, eighty, and eighty-one units, padded valid input, and internal whitespace. Add a statement about Unicode length interpretation so reviewers do not mistake this exercise for grapheme-aware validation. The table is the oracle against which implementation decisions are judged.

Name the domain ownership boundary. If you choose a title value object, explain how both creation and change receive it and how persistence maps it. If you keep a string field, explain how shared normalization and validation happen before any aggregate mutation. Handler-only validation does not satisfy the requested domain guarantee unless your proposal explicitly changes the assignment and explains the narrower scope.

Also define error-priority expectations for requests with multiple invalid fields. You can guarantee rejection without specifying every competing rule order, but the isolated title tests must make other fields valid. An implementation should not be rejected simply because an unrelated invalid term fails first in a deliberately multiply invalid request unless the written contract requires title-first reporting.

## Deliverable two: an independent rejection snapshot

Construct an original meeting with known title, interval, description, location, limits, RSVP term, fee, and change metadata. Construct a candidate request with an invalid title and different valid values for every other component. Capture independent before values, including all relevant domain event collections and child state that the operation could affect. Retaining mutable references is not sufficient.

After rejection, compare the complete projection and the specific intended rule. The test must detect early description assignment, early change-date assignment, and early event append. Include at least one deliberately introduced signature-compatible mutation in an owned experimental copy to show that your assertions fail for a semantic violation rather than only compile errors.

For creation, capture repository interaction and assert no AddAsync call when the title rejects. A successful creation control should capture the meeting, verify normalized title, and preserve distinct interval boundaries. A rejection-only suite can accidentally accept an implementation that rejects every request; positive controls keep the contract balanced.

## Deliverable three: the mapping and compatibility decision

Explain whether the Title storage column remains the same and how the chosen CLR representation reaches it. Review existing data compatibility: a previously stored short title may not satisfy the new rule. Choose and justify a migration, grandfathering, or validation-on-change strategy rather than allowing constructor placement to decide silently.

The design-only route supplies a concrete round-trip test plan with expected values and an identified owned database fixture. The implementation route executes the approved fixture and records the fresh observation boundary used to avoid merely rereading a tracked object. It also verifies the details query's Title projection. A domain-only test cannot replace this persistence and read-model evidence.

Do not run the existing integration fixture against an unowned database. Its setup deletes tables, as chapter 17 documents. If the environment is unavailable, report that integration evidence remains unexecuted and submit the design-only route honestly. A clearly limited design can be assessed without pretending it is a deployed feature.

## Deliverable four: a reviewable change narrative

Lead with the concrete behavior: valid padded titles become normalized; invalid titles reject without partial meeting changes. Explain where the invariant lives and why the implementation preserves rejection state. Then describe mapping consequences, compatibility choices, and test evidence. Avoid narrating every abandoned attempt unless it explains a tradeoff a reviewer must evaluate.

List executed checks separately from designed checks. A mutation that fails compilation does not prove a semantic assertion. A mocked controller action does not prove an HTTP error response. A source mapping review does not prove historical rows materialize. The narrative should let a reviewer identify the strongest supported claim without reconstructing the entire course.

Include exact relative paths for changed learner files in your own submission, but do not include secrets, real user data, or machine-specific connection values. Use synthetic identifiers and titles. The course itself leaves application source untouched; any later implementation work belongs to the learner's explicitly chosen workspace and history workflow.

## Acceptance scenarios

Scenario one accepts a five-unit trimmed title with surrounding spaces and stores the normalized five-unit value. Scenario two rejects a four-unit title while every other proposed attribute differs validly from the original; all affected values and events remain unchanged. Scenario three rejects eighty-one units on creation without repository addition. Scenario four accepts eighty units and preserves exact start and end mapping.

Scenario five supplies a valid title but a proposed attendee ceiling below active occupied places. The preexisting capacity rule still rejects without partial main-attribute mutation. Scenario six exercises the undefined-fee and nullable-limit forms to ensure title work did not accidentally normalize unrelated values. These controls prevent a local feature from weakening neighboring invariants.

Scenario seven covers a historical stored title according to the chosen compatibility policy. Its expected outcome must be written before execution. Scenario eight checks the read projection after an accepted implementation-route change through a fresh scope. If you cannot execute those scenarios, retain their concrete test designs and mark the evidence gap rather than deleting them from the completion narrative.

## Mutation review

Use at least three conceptual mutations in the design and one executed semantic mutation if taking the implementation route. Candidate mutations include accepting eighty-one units, trimming only on creation, assigning description before validation, and appending the change event before validation. Each should map to a specific failing assertion in your plan.

A high-quality suite detects the mutation for the intended reason. If an invalid fixture fails a membership guard before reaching title handling, it does not test the title mutation. If reflection invocation fails to construct the handler, it does not test rejection. Preserve build and invocation evidence so a red result can be interpreted precisely.

Do not make the expected result depend on the implementation helper under test. Fixed strings and independently captured before projections are the oracle. Mutation exercises are useful because they expose tests that merely mirror production code or assert only the most obvious output while missing partial effects.

## Sixty-point capstone rubric

Award twelve points for a precise independent contract, including normalization, length unit, boundaries, and current-versus-proposed separation. Award twelve for domain placement and complete unchanged-state rejection evidence. Award ten for creation and change mapping tests with distinct sentinels and positive controls. Award ten for persistence mapping and historical compatibility design or execution appropriate to the declared route.

Award eight points for discriminating mutation analysis and failure-stage interpretation. Award eight for a concise, truthful review packet with exact evidence boundaries and limitations. A design-only submission can earn full design credit when it clearly states that no feature was implemented; implementation completion requires the additional executed evidence claimed by that route. Do not award execution credit for a proposed command or a screenshot from an unrelated run.

A submission cannot claim implementation completion if the rejection snapshot omits affected events, the title policy differs between creation and change without explanation, or the reported integration run used an unknown database. These are material gaps in the assigned contract. They are not cured by a larger word count or more unrelated passing tests.

## Independent preparation exercises

Exercise NA19-A, acceptance packet, is worth eight points. Write the eight scenarios with exact inputs, expected outputs, and evidence boundaries. Identify which are executable with domain or handler substitutes and which need an owned persistence fixture.

Exercise NA19-B, mutation-to-assertion map, is worth six points. Match four proposed mutations to independent assertions and explain one earlier guard that could invalidate each intended experiment. Keep compiler and invocation failures separate from semantic failures.

Exercise NA19-C, review decision, is worth six points. Assess a submission with passing title unit tests but no event snapshot or mapping review. State what can be accepted now and what remains before implementation completion. These preparation exercises contribute the chapter's twenty points; the sixty-point capstone rubric is a separate assessment. See [the final solutions](SOLUTIONS-13-20.md) after writing your review.


[Complete course route](README.md) | [Separate solutions and assessment](SOLUTIONS-13-20.md)
