# 07. Attendees, guests, and capacity as distinct quantities

The next six chapters move from a single interval to interacting aggregate operations. Begin with [Meeting](../../../modular-monolith-with-ddd/src/Modules/Meetings/Domain/Meetings/Meeting.cs), [MeetingAttendee](../../../modular-monolith-with-ddd/src/Modules/Meetings/Domain/Meetings/MeetingAttendee.cs), and [the attendee tests](../../../modular-monolith-with-ddd/src/Modules/Meetings/Tests/UnitTests/Meetings/MeetingAddAttendeeTests.cs). This chapter describes their current source behavior. Proposed stronger validation is always identified separately. Reading a method name is insufficient: several seemingly familiar words have narrower meanings in the implementation.

Your goal is to predict the first rejecting rule and the resulting capacity, not merely whether a call throws. Complete the numeric worksheet before consulting [the separate solutions](SOLUTIONS-07-12.md). The disposable rule lab introduced with this installment executes selected real rule predicates; it does not execute the aggregate, repositories, or HTTP layer.

## Count places, records, and identities separately

A meeting's attendee collection is a history-bearing collection of entities. Its length is not necessarily the number of active people or occupied places. GetAllActiveAttendeesWithGuestsNumber filters entities using IsActive and sums GetAttendeeWithGuestsNumber. The latter returns one plus the stored guest number. The extra one is the named member attending, not another guest. A host is also represented by an attendee entity and contributes a place when active.

Assume a valid future meeting with one creator host and no other attendees. Its active occupied places begin at one. Adding member Ada with two guests creates one additional attendee entity, representing three occupied places. The collection now contains two attendee records and accounts for four active places. Adding member Ben with zero guests would produce three records and five occupied places. Those are different dimensions, and a test should label them rather than calling each number the attendee count.

The existing capacity test uses a limit of five. The initial creator occupies one place; a new member with three guests occupies four more; the next zero-guest member is rejected. This is an excellent small fixture because forgetting the creator, forgetting the member's own place, or counting only entities each produces a different incorrect answer. Preserve that discriminating structure when creating your own example.

## Separate configuration validity from a requested addition

MeetingLimits validates the configuration through its factory. A configured attendee limit cannot be negative. The guest limit cannot be negative. When an attendee limit exists, it must be greater than the guest limit. That final comparison is strict: equal configured limits fail. A null attendee limit passes that particular constraint because there is no configured total ceiling to compare.

Addition uses two different rules after earlier eligibility checks. MeetingGuestsNumberIsAboveLimitRule is broken only when the configured guest limit is greater than zero and less than the requested guests. Consequently, zero currently disables this particular upper-bound check; it does not mean that zero guests are permitted. Treating zero as a prohibition would contradict the expression and existing fixture behavior. This is a source observation, not a recommendation for a public API design.

MeetingAttendeesNumberIsAboveLimitRule is broken when a total limit exists and is less than existing active places plus one plus requested guests. Equal capacity is allowed. Null total capacity disables that rule. A request can pass the guest ceiling and still fail total capacity, because another member has already occupied the remaining places. The two rules answer separate questions and should have separate assertions.

These predicates also expose a useful audit boundary. A negative requested guest number is not rejected by the upper-bound expression alone. The selected AddAttendee method does not visibly introduce a negative-request guard before using that number. Do not leap from this observation to an end-to-end exploit claim: transport validators or other callers require their own inspection. A proposed domain requirement to reject negative requested guests must be specified and tested as a change, rather than silently assumed in explanations of current code.

## Trace the entire rejection sequence

AddAttendee first checks that the meeting has not passed its start. It then checks RSVP membership, group membership, duplicate active-attendee lookup, guest ceiling, and total capacity. Only after those checks does it change an active not-attendee decision and append a new attendee. This order makes rule identity a strong diagnostic signal.

Imagine a stranger requests twenty guests after the meeting starts. The capacity numbers may be invalid, but the observed first rule is the start-time rule. A test that expects the capacity rule from that fixture has not isolated capacity. Move the clock before the start, place the current time inside RSVP, join the member to the group, ensure they are not already an attendee, and keep the guest request within its independent ceiling. Then make only the total capacity insufficient.

The checks form a dependency ladder for test setup:

```text
before start -> inside RSVP -> group member -> not duplicate
             -> guest request accepted -> total places accepted
             -> change old decision -> append new attendee
```

This diagram is a method-order trace, not a database transaction diagram. If a guard throws before the final section, the method has not reached those visible mutations. Nothing in this observation establishes database rollback or concurrent request isolation. Those require a different boundary and evidence set.

## Build a capacity worksheet with explicit units

Use a total limit of eight and guest limit of three. Start with one host. Add Ada with two guests, then Ben with one guest. The totals become four and six places respectively. A new member with one guest fits exactly at eight; another with two would require nine and fail. Both requests satisfy the guest ceiling, which isolates the total-capacity decision.

Now change the total limit to null while leaving the guest limit at three. A request for four guests still fails the guest rule even though total capacity is unlimited. Change the guest limit to zero while keeping the total limit at eight. The requested guest ceiling no longer rejects four by itself, but total capacity can still reject the addition. Unlimited in one dimension does not imply unlimited in the other.

For every row, record configuration validity, occupied places before, requested guests, requested places, first applicable rule, and occupied places after. On rejection, after should equal before for this particular method's visible guarded mutation section. Add an independent event snapshot when testing the real aggregate so that a rejection cannot conceal an unwanted child event. A numeric capacity assertion alone would miss such an effect.

## Active predicates are not interchangeable

MeetingAttendee.IsActive returns true only when there is no decision-change date and the entity is not removed. IsActiveAttendee instead checks matching member identity and that the decision-changed flag is false. It does not include the removal flag. IsActiveHost combines IsActive with the host role. These methods share an English word but implement different conditions.

This distinction matters when reasoning about a removed attendee. Capacity excludes a removed record through IsActive. A lookup using IsActiveAttendee can still find that record if its decision has not changed. The duplicate rule and several role/removal lookups use that latter predicate. Describe this as a source-level consistency question and design a focused characterization before deciding on a repair. Do not substitute your preferred meaning of active into a trace.

A proposed refactor to unify the predicates has a larger effect than shortening duplicated code. It can alter rejoining behavior, duplicate detection, role eligibility, and removal semantics. A review should enumerate those callers, define the desired lifecycle, and distinguish historical records from current participation. Changing a helper in isolation risks converting a local cleanup into an unreviewed domain policy change.

## Fees add another unit to the worksheet

MeetingAttendee construction multiplies a defined event fee by one plus guests. With a per-place fee of twelve and two guests, the attendee's stored fee represents three places and therefore thirty-six in the same currency. The attendee-added event receives the computed fee value and currency. This statement follows the constructor's multiplication; it does not assert payment collection, settlement, or refund behavior.

Hosts created by the meeting constructor use zero guests and MoneyValue.Undefined. A normal addition uses the meeting's event fee. A promoted waitlist member is also created with zero guests and the current meeting fee, which chapter 09 examines. These paths share a child constructor while supplying different arguments. An event payload assertion should therefore identify the path being tested instead of assuming all attendees have identical fee origins.

Keep arithmetic fixtures within ordinary small integer and decimal values unless overflow or numeric-range policy is the explicit exercise. A bounded rule lab is not a general proof about all integer inputs. Negative guests, extreme sums, and currency constraints each deserve a separately stated contract and relevant source review. A precise limited test is more useful than an unexplained claim of complete validation.

## Design an independent boundary suite

Choose values that distinguish every comparison. For guest ceiling three, use requests two, three, and four. For total capacity eight with six occupied places, use zero, one, and two guests. For null total capacity, use a value above a formerly configured limit while keeping other conditions valid. For zero guest ceiling, characterize the current disabled-check behavior explicitly.

Then add one fixture-level test with the creator host included. Predicate tests can verify an arithmetic expression while an aggregate incorrectly calculates the supplied occupied-place count. Conversely, an aggregate fixture can hide arithmetic boundaries behind earlier guard failures. These two evidence layers complement one another; neither makes the other redundant.

When the suite fails, report both the expected rule and the actual rule. Preserve the before-state worksheet. If the actual rule is group membership, fix the fixture's membership, not the capacity expectation. If capacity unexpectedly accepts a row, check the exact total, null configuration, and requested-place calculation before changing production code. Investigation should preserve a clear causal chain from input to rule.

## Independent practice

Exercise NA07-A, the occupied-place ledger, is worth eight points. Construct the eight-place worksheet above, including both accepted additions and rejected alternatives. Explain the difference between collection length, member identities, and occupied places. Include the creator host and report each first rejecting rule.

Exercise NA07-B, predicate disagreement, is worth six points. Trace a removed attendee through IsActive, IsActiveAttendee, and IsActiveHost. Name two callers whose behavior could change if the predicates were unified. State one characterization test and one policy question without claiming that the proposed answer is already implemented.

Exercise NA07-C, independent suite design, is worth six points. Specify a minimal guest and capacity boundary matrix that detects strict-versus-inclusive comparison changes, a missing member place, and an accidental null-limit rejection. Identify which case requires an aggregate fixture beyond the standalone predicates. Read the solutions only after recording exact expected numbers.


[Run the bounded capacity and reason lab](LAB-CAPACITY-07-12.md) after writing predictions. [Investigation workbook](INVESTIGATION-WORKBOOK-07-12.md) | [Course route](README.md)
