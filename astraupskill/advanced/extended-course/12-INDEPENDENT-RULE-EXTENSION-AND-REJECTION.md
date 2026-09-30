# 12. Specify an independent rule before implementing it

The course has used current behavior to teach careful observation. This chapter changes mode explicitly: you will design a proposed domain extension. The application does not currently gain this feature by reading the chapter, and the course does not edit learner code. Your deliverable is a reviewable specification, a graduated test plan, and an implementation strategy that preserves every affected field when a command is rejected.

Use [Meeting.ChangeMainAttributes](../../../modular-monolith-with-ddd/src/Modules/Meetings/Domain/Meetings/Meeting.cs), [its command handler](../../../modular-monolith-with-ddd/src/Modules/Meetings/Application/Meetings/ChangeMeetingMainAttributes/ChangeMeetingMainAttributesCommandHandler.cs), and [the existing handler tests](../../../modular-monolith-with-ddd/src/Modules/Meetings/Tests/UnitTests/Meetings/MeetingTermCommandHandlerTests.cs) as anchors. The proposed rule is a normalized meeting title containing between five and eighty characters after trimming surrounding whitespace. The policy is an exercise specification, not an assertion about the shipped domain.

## Write a contract that can disagree with an implementation

Specify null handling, whitespace handling, normalization, length boundaries, and where the normalized value is stored. For this exercise, null rejects; surrounding whitespace is trimmed; a resulting length below five or above eighty rejects; and accepted titles store the trimmed text. Internal whitespace is preserved. The length measure is the ordinary .NET string Length of the trimmed result, so the exercise does not claim a grapheme-aware character count.

That last detail matters. The word character can refer to code units, Unicode scalar values, or user-perceived symbols. A specification that leaves the unit ambiguous creates disagreements that cannot be resolved by adding random tests. You may propose a different internationalization policy in your independent design, but label it as a variation and update its examples consistently.

The contract applies to both meeting creation and main-attribute change in the proposed extension. Decide whether the same value object represents the normalized title in both paths or whether a shared rule and normalization function provide the behavior. Avoid duplicating subtly different trimming and length logic in separate handlers. The acceptance criteria should remain independent of that implementation choice.

## Define rejection as more than an exception

On rejected main-attribute change, all affected meeting fields must remain unchanged, including title, term, description, location, limits, RSVP term, fee, change metadata, relevant child state, and domain event collections. The requirement includes the event graph, not only the aggregate's direct events. Creation rejection must not add the new meeting through the repository boundary in a handler test.

The current interval handler tests protect the old term in their rejection case; that is narrower than the proposed all-fields criterion. Keep both statements accurate. Existing coverage supplies a useful starting pattern, but extending the assertion requires an independent snapshot of the additional fields and events. Do not report the stronger guarantee as already verified merely because a similarly named test exists.

For a rejected title change, use distinct proposed values for every other field. If title, description, location, and fee all equal the original fixture, an incorrect early assignment may remain invisible. Sentinel values make accidental partial mutation observable. Keep those sentinel values valid under their own factories so the title rule remains the intended failure.

## Choose the validation boundary deliberately

A title value object can normalize and validate during construction before the aggregate method receives it. That mirrors the temporal value-object boundary studied earlier. A raw-string aggregate API can instead validate and prepare a normalized string before assigning any field. Both approaches can support unchanged-state rejection if all relevant validation happens before mutation.

Handler-only validation is weaker as a domain invariant because other callers can invoke the aggregate directly. Transport validation can improve request feedback but should not be confused with a domain guarantee. Your proposed design should identify which boundary owns the invariant and which outer layers translate or duplicate feedback for usability.

If introducing a value object, trace persistence mappings, constructors used by materialization, and serialization or DTO conversion before implementing. Those later integration questions are part of the design review, not grounds for guessing the repository's mappings. In this installment, keep them listed as required follow-up evidence until their source is inspected in later chapters.

## Prepare all values before applying changes

A robust change method can be understood as prepare, validate, apply, and record. Preparation computes the normalized title and constructs valid candidate values. Validation checks relationships that depend on current aggregate state, such as capacity against active places. Application assigns the accepted candidates. Recording appends the success event and change metadata at the intended point.

```text
raw command -> prepared candidates -> all applicable rules pass
                                      |
                                      v
                              assign complete new state
                              record change metadata/event
```

This diagram is a proposed implementation discipline. It is not a universal description of every current method: chapter 08 showed demotion validating a resulting host count after child mutation. Reuse the discipline where appropriate without rewriting historical observations to make the repository appear uniformly designed.

Preparation itself can fail, and the failure order should be considered. If a request contains both an invalid interval and invalid title, decide which error is expected at the chosen boundary or document that the contract guarantees rejection without prescribing one rule's priority. Tests for the title invariant should normally make all other fields valid so they do not depend on incidental ordering.

## Build a graduated test ladder

Start with pure title-policy examples. Use lengths four, five, eighty, and eighty-one after trimming, plus null, empty, and whitespace-only input. Include a valid padded title to prove normalization and a title with internal spaces to prove they are preserved. Use exact strings generated from known characters when length matters; do not count a long sentence by eye.

Next test direct aggregate change with a valid complete fixture. One accepted case should verify every changed field and exactly the intended new event. One rejected case should compare the complete before projection and specific rule identity. A second rejected case at the opposite length boundary protects both sides of the policy. Include a valid title but insufficient proposed capacity to show that the preexisting aggregate rule remains effective.

Then test each handler mapping. For creation, capture the added meeting and inspect normalized title and distinct interval boundaries. For rejection, assert no AddAsync call. For main-attribute change, return a known meeting from the repository substitute and assert unchanged state after rejection. Use the reflection invocation pattern from chapter 05 correctly, awaiting the returned task so asynchronous exceptions are observed.

Finally, design integration checks for persistence and transport, but do not claim them executed until the relevant environment and source are available. A domain-only success does not establish storage column compatibility or HTTP error shape. Each rung should name the new evidence it contributes rather than repeating the same assertion under a larger test harness.

## Use mutations to test the specification's independence

A useful deliberate mutation trims only on creation but not on change. Another accepts length eighty-one by using the wrong comparison. A third assigns description before validating title, violating unchanged-state rejection while still throwing the right exception. A fourth appends a change event before validation and leaves fields untouched. Each targets a different weakness in an otherwise plausible suite.

Your expected outcomes should detect these changes without copying the implementation's normalization result. For the padded accepted input, write the exact expected stored title. For rejection, compare to a snapshot captured before invocation. For event mutation, compare payload projections and cardinality across the relevant graph. A test that merely catches the rule exception would miss the latter two defects.

Keep mutations signature-compatible and confined to an owned experimental copy or a deliberate learner branch under your own workflow. This course does not apply them to application source. A compiler failure is not a successful semantic mutation test. The experiment must reach the assertion whose contract the mutation violates.

## Plan a compatibility review

Adding a title invariant can affect existing stored data that would not satisfy the new rule. A persistence materializer might encounter historical short titles, and a new constructor check could prevent loading them. Before implementing, decide whether old data is migrated, grandfathered, validated only on new changes, or rejected with an explicit operational plan. Do not accidentally choose a migration policy through constructor placement.

Consider public callers that pass strings, fixtures that use very short placeholder titles, and tests focused on unrelated rules. Those fixtures may need valid titles so their original rule remains isolated. Updating a fixture is justified when it preserves the test's purpose; weakening the new rule merely to keep an invalid placeholder is not. Conversely, mass-changing assertions without reviewing their intent can hide a compatibility regression.

Error messages and rule types also form a practical diagnostic contract. Prefer asserting the rule type and meaningful payload rather than depending on incidental punctuation, unless exact text is part of a documented interface. If an outer layer maps domain exceptions to responses, inspect that mapping separately before claiming the new rule receives a particular HTTP status.

## Assess the proposal with a review rubric

A strong submission states the normalization and length unit, identifies current versus proposed behavior, and supplies boundary examples with independent expected values. It names the domain ownership boundary and explains how creation and change share the invariant. It shows that rejected changes preserve all affected fields and events, and it keeps handler mapping separate from persistence evidence.

A weaker submission may have many tests but no clear oracle. Typical signs include deriving expected title from the same helper under test, catching any exception instead of the intended rule, keeping live before references, or asserting only the title while description and events can change. Another warning sign is claiming the full application supports the extension without inspecting mappings and existing data implications.

Use the chapter's twenty graded points for the written exercises below. The larger independent implementation can become a later capstone after persistence and application boundaries have been studied. That sequencing prevents an attractive domain-only patch from being presented as a complete feature before its integration consequences are understood.

## Independent practice

Exercise NA12-A, policy and boundary table, is worth eight points. Write exact accepted stored values or rejection outcomes for null, whitespace, four, five, eighty, and eighty-one characters, padded valid input, and internal whitespace. State the length unit and provide one alternative policy with its changed examples.

Exercise NA12-B, all-fields rejection, is worth six points. Design a sentinel fixture and independent snapshot for main-attribute change. Explain how your suite catches early description assignment and early event append even when the title rule still throws. Include no-add evidence for creation.

Exercise NA12-C, implementation review, is worth six points. Compare a value-object boundary with aggregate prevalidation, identify one historical-data compatibility risk, and separate the domain, handler, persistence, and transport evidence needed for completion. Review [the separate solutions](SOLUTIONS-07-12.md) only after committing your own reasoning to the worksheet.


[Investigation workbook](INVESTIGATION-WORKBOOK-07-12.md) | [Course route](README.md)
