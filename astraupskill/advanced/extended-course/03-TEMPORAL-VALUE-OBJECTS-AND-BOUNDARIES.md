# 03 - Give each temporal value object its own contract

MeetingTerm and Term both contain dates, but they do not express the same domain rule. The meeting requires a strictly positive interval. The RSVP term permits nullable boundaries and inclusive membership. Confusing those contracts can turn a focused repair into an unrelated behavior change. Read [MeetingTerm](../../../modular-monolith-with-ddd/src/Modules/Meetings/Domain/Meetings/MeetingTerm.cs), [its order rule](../../../modular-monolith-with-ddd/src/Modules/Meetings/Domain/Meetings/Rules/MeetingTermMustEndAfterStartRule.cs), [Term](../../../modular-monolith-with-ddd/src/Modules/Meetings/Domain/Meetings/Term.cs), [ValueObject](../../../modular-monolith-with-ddd/src/BuildingBlocks/Domain/ValueObject.cs), and [SystemClock](../../../modular-monolith-with-ddd/src/Modules/Meetings/Domain/SharedKernel/SystemClock.cs).

## Construction establishes the interval invariant

MeetingTerm exposes get-only StartDate and EndDate properties. Its public factory calls a private constructor, which checks MeetingTermMustEndAfterStartRule before assigning either property. The rule is broken when end is less than or equal to start. Equality therefore rejects just as reversal does. A successfully returned MeetingTerm from this factory preserves the exact supplied boundaries and represents positive duration.

That claim is deliberately about this construction path. Reflection, serialization mechanisms, or future persistence materialization can introduce other object-creation paths with their own contracts. Do not describe a private constructor as a universal proof that arbitrary external data can never produce invalid state. For the application handlers inspected here, the factory is the relevant boundary and its behavior is directly testable.

The rule returns a Boolean from IsBroken and supplies a message. CheckRule raises BusinessRuleValidationException containing the broken rule. That exception identity is useful evidence: it distinguishes an intended domain rejection from an incidental null reference, reflection failure, or repository problem. A test expecting any exception discards that distinction and can pass for a reason unrelated to the interval.

## The nearest boundaries reveal the inequality

Use a fixed start and ends one tick before, equal to, and one tick after it. The first two reject; the last succeeds. A tick is the DateTime representation's small unit, so the one-tick positive case distinguishes strict positivity from an invented minimum duration such as one minute. The current rule does not require a meeting to last at least a particular business-friendly number of minutes.

Add an ordinary two-hour interval and assert both properties. Boundary cases establish the inequality; the ordinary case makes mapping errors easier to read. A reversed interval several days apart is useful but cannot distinguish less-than from less-than-or-equal. That is why the disposable broken-rule mutation can still reject reversal while incorrectly accepting equality.

| End relative to start | Current factory outcome | What the row distinguishes |
| --- | --- | --- |
| One tick earlier | Business-rule rejection | Reversal is forbidden |
| Equal | Business-rule rejection | Zero duration is forbidden |
| One tick later | Exact values preserved | No larger minimum is imposed |
| Two hours later | Exact values preserved | Ordinary positive mapping |

The tests should not calculate expected end by reading the constructed object. The input is the oracle for preservation. If the factory shifts the end and the test derives its expectation from that shifted output, both sides can agree while the contract is violated. Keep expected values independent and visible.

## Comparison does not define a timezone conversion policy

The inspected code compares DateTime values directly and does not normalize them to a named timezone. The worked examples use UTC values to avoid ambiguous assumptions. Do not infer that the factory converts local times, handles daylight-saving gaps, or resolves repeated wall-clock times. Those would require an explicit boundary for converting user input into the domain's chosen representation.

A proposed scheduling API should state whether it accepts instants, local wall times with a timezone, or already normalized UTC values. Two displayed times can look ordered while their underlying instants require conversion. Conversely, a daylight-saving day can have a duration different from a naive wall-clock subtraction. Those questions are important, but they are not answered by this small strict-order rule alone.

For this installment's tests, hold DateTimeKind and the date construction method consistent. The goal is to isolate the existing inequality and mapping. A later independent timezone exercise can introduce a conversion layer with its own invalid and ambiguous input cases. Adding such conversion silently inside MeetingTerm would change its responsibility and could alter callers that already supply normalized values.

## Time-relative behavior is another method

MeetingTerm.IsAfterStart compares SystemClock.Now strictly greater than StartDate. Exactly at the start boundary it returns false under that expression; one tick after returns true. That is separate from whether the interval itself is valid. A positive meeting can be in the future, at its start, in progress, or ended while retaining the same immutable term values.

SystemClock returns a custom date when set and otherwise DateTime.UtcNow. Tests can set it to isolate time-relative rules. They must reset it afterward, because its custom value is static shared state. The base test class includes a teardown reset. A test outside that inheritance path needs its own cleanup. Parallel tests that change the same static clock require deliberate coordination; setting a fixed value does not automatically make shared global state concurrency-safe.

A good clock experiment checks one tick before start, exactly start, and one tick after, using the same MeetingTerm. It records that these are observations of a time-relative predicate, not new constructions. Recreating the term for each row can be valid, but it should not obscure which variable changes and which remains constant.

## RSVP Term expresses open and inclusive boundaries

Term contains nullable StartDate and EndDate and offers NoTerm with both null. Its constructor simply assigns the boundaries; the inspected implementation does not apply MeetingTerm's strict-order rule. IsInTerm treats a missing start as no lower bound and a missing end as no upper bound. Present bounds are inclusive: start less than or equal to the tested date and end greater than or equal to it.

An equal bounded RSVP term can therefore include that exact instant. A reversed bounded term may include no dates under the conjunction, but construction itself does not reject it in the inspected code. This is current behavior to describe accurately, not a recommendation to copy it into every domain. A proposed RSVP validation rule needs its own specification and compatibility review.

The aggregate's SetRsvpTerm also modifies the effective RSVP end. When the requested end is absent or later than the meeting start, it constructs an RSVP term ending at the meeting start while preserving the requested start. Otherwise it retains the supplied term. That normalization links two temporal objects without making their individual contracts identical.

## Work the clamping cases

Take a meeting beginning at ten. An RSVP term from eight to nine remains unchanged. An RSVP term from eight to eleven is clamped to end at ten. An open-ended RSVP term starting at eight also ends at ten after aggregate normalization. A NoTerm request has its absent end replaced by the meeting start while retaining an absent start. These predictions follow the private helper's branches.

Now propose an RSVP start after the meeting start with an absent end. The helper can produce a reversed bounded term because it preserves that requested start and clamps the end. The current Term constructor does not reject it. This is a valuable source-bound review question, not a license to silently repair the original application during curriculum authoring. A learner can propose a rule and tests that define the desired policy.

The distinction also affects mapping tests. Observing an RSVP end different from the command does not necessarily reveal a mapping defect; the aggregate may intentionally clamp it. Observing a MeetingTerm end different from the command has no equivalent normalization in the inspected factory. Each expected value must be justified by the responsible boundary.

## Equality is value semantics with implementation details

ValueObject compares objects only when their runtime types match, then compares selected public properties and fields through reflection, excluding members marked with IgnoreMemberAttribute. Its hash code follows the selected members. This supports comparing separately constructed values with equivalent data, but it is not a universal deep comparison of arbitrary object graphs. The reflected members and their own equality semantics determine the result.

A regression that changes a value object's fields or annotations can change equality behavior without changing its public factory signature. When testing an interval, direct StartDate and EndDate assertions provide a clear mapping claim; an equality assertion can add evidence about value semantics but should not hide which component differs. Avoid persisting hash codes as portable identities, since they are implementation-level values rather than stable domain keys.

## Independent practice

Exercise NA03-A, boundary matrix, is worth eight points. Predict construction for one tick before, equal, one tick after, and two hours after a fixed UTC start. Identify which mutation each boundary catches and assert the specific broken rule for rejected rows.

Exercise NA03-B, two temporal contracts, is worth six points. Compare MeetingTerm with RSVP Term for equal, open-ended, and reversed boundaries. Work the four clamping examples and label a proposed RSVP consistency rule separately from current behavior.

Exercise NA03-C, clock and equality, is worth six points. Specify a deterministic IsAfterStart experiment with cleanup, then explain why direct property assertions and value equality answer related but different questions. Identify one unsupported timezone claim that must remain outside the current rule's evidence.

Continue with [aggregate mutation and domain events](04-AGGREGATE-MUTATION-AND-EVENT-EVIDENCE.md). The [solution guide](SOLUTIONS-01-06.md) keeps the interval, clock, and RSVP interpretations distinct so that a correct result at one boundary does not justify an incorrect claim at another.
