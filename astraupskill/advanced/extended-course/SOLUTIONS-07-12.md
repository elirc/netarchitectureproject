# Solutions and grading: chapters 07-12

These answers follow eighteen independent exercises worth 120 points. Combined with chapters 01-06, the delivered course has thirty-six graded exercises worth 240 points. Read the hints first, return to your own worksheet, and use the full answer only after writing a prediction. Award credit for correct boundaries and causal explanations, not merely the same vocabulary as this guide. Source-derived predictions must remain labeled as such when the full aggregate has not been executed.

## Hints before full solutions

For chapter 07, write units beside every number. A member with two guests contributes three places, and the creator host already occupies one. Compare the active predicates directly instead of assuming their names are synonyms.

For chapter 08, put a vertical line at every mutation. The location of a thrown rule relative to those lines determines what unchanged-state evidence still needs inspection. Authorization concerns the actor, while target eligibility concerns another identity.

For chapter 09, give each signup record a separate label even when two records share a member identity. Follow the active filter before sorting. A constructor argument can preserve signup time while another field records promotion time.

For chapter 10, include the clock in the input tuple for repeated commands. The canceled flag is checked after the start guard, and a removal reason uses a specific string predicate rather than a general notion of meaningful text.

For chapter 11, distinguish a read-only view from a frozen value. Follow event ownership through child lists and inspect the direction of IsAssignableFrom before describing helper behavior.

For chapter 12, write the proposed policy independently of its implementation. Give every other candidate field a distinct valid value so that partial mutation becomes visible. A rule exception alone is not the all-fields rejection oracle.

## NA07-A: occupied-place ledger, eight points

The initial host contributes one active place. Ada with two guests adds three, bringing the total to four. Ben with one guest adds two, bringing it to six. A new member with one guest adds two and fits exactly at eight; a new member with two guests would add three and exceed the limit at nine. Both alternative requests satisfy a guest ceiling of three, so total capacity distinguishes them. Each rejected alternative should begin from the same six-place baseline rather than after another accepted alternative.

Collection length after Ada and Ben is three attendee records, while occupied places total six. There are three named member identities; their guests are counted as places without additional member records in this fixture. A null total ceiling does not disable the guest ceiling. A zero guest ceiling disables the selected guest upper-bound predicate but leaves total capacity active when configured.

Award three points for arithmetic including the creator and member place, two for separating records and places, two for correct rule isolation, and one for treating alternative rows as independent fixtures. Do not award full rule-isolation credit when the proposed member was never joined to the group or the RSVP period has already ended.

## NA07-B: predicate disagreement, six points

For a removed attendee whose decision has not changed, IsActive is false because removal excludes it. IsActiveAttendee for its own identity can remain true because that predicate checks identity and the decision-changed flag, not removal. IsActiveHost is false because it requires IsActive in addition to the host role. The role value can still be Host while the active-host predicate is false.

Duplicate attendance detection and target lookup for role or removal operations can change if the predicates are unified. A focused characterization could remove a valid attendee before start, then inspect the three predicates and attempt readdition or repeated removal through the relevant guarded method. Record source prediction separately from an executed result. The policy question is whether a removed participation record should block rejoining, remain addressable for administrative operations, or require a new record with explicit history.

Award two points for the predicate results, two for affected callers, and two for a bounded characterization plus explicit policy question. A response that silently replaces the current predicate with a preferred definition is a proposed repair, not a correct characterization.

## NA07-C: boundary suite, six points

For guest limit three, requests two and three pass the selected upper-bound predicate and four breaks it. For total eight and six occupied places, guest requests zero and one fit while two exceeds capacity. Equality cases detect an accidental inclusive rejection. A full meeting of five places plus a zero-guest member detects forgetting the member's own place. Null total capacity with a larger ordinary occupancy detects an accidental null rejection.

The aggregate fixture must additionally prove that the supplied occupied-place total includes the creator host and guests from active children. Pure predicate tests cannot detect an aggregate passing the wrong active count. A zero guest limit row should explicitly preserve current disabled-check behavior, while negative requests should be characterized separately from a proposed nonnegative-input rule.

Award three points for independent boundary rows, two for mutation discrimination, and one for the additional aggregate counting boundary. More rows are not automatically better if every row is intercepted by an earlier eligibility guard or repeats the same comparison region.

## NA08-A: role matrix, eight points

Two-host demotion passes the early guards, changes the target to Attendee, appends its child event, and leaves one active host. Last-host demotion follows the same child transition, then counts zero and raises the host rule. The source therefore predicts a child role and event change before that exception; unchanged-state behavior is not established by the existing exception assertion.

Demoting an already ordinary attendee reaches the child's already-attendee rule and rejects before its role assignment and demotion event. Unauthorized promotion rejects at actor authority before SetAsHost. In both cases, construct a future meeting and otherwise valid target so a different guard does not intercept the intended path. Root event count alone is insufficient because these role events belong to the attendee child.

Award two points each for the four rows, including mutation order and event owner. A response that reports every rejected row as unchanged loses the last-host row. A response claiming the source trace proves a committed database defect also loses boundary credit: persistence was not executed.

## NA08-B: proposed repair, six points

The proposed contract is that a rejected last-host demotion changes no affected field or event collection. Prevalidate the resulting active host count before applying the child transition. Determine whether the target is currently counted as an active host, subtract its contribution for the proposed demotion, and reject if the result violates the intended invariant. Preserve the separate actor, target, and already-attendee checks according to the written error-priority policy.

Checking whether the pre-mutation host count equals zero is insufficient: the risky ordinary fixture has one host before demotion and zero afterward. The algorithm must reason about candidate state. Also account for lookup and active-host predicate differences; a target found by IsActiveAttendee need not be counted by IsActiveHost under every historical state.

Award two points for future-state reasoning, two for preserving distinct checks and identity roles, and two for complete rejection evidence including child events. A rollback design can receive credit if it explicitly restores every affected value and event, but it requires more evidence than merely assigning the old role back.

## NA08-C: evidence critique, six points

An expected exception proves a rejecting path, not the absence of earlier mutation. A root-only event assertion ignores child event collections. A retained attendee reference reads the same mutable object after the call and cannot serve as an earlier state. Replace these with independently captured primitive role and status values plus materialized event projections across the relevant graph.

Use a fixture with one host, then compare before and after even when the expected rule is raised. Keep a two-host success case to ensure the proposed fix does not forbid every demotion. Persistence claims would additionally require the actual application transaction boundary, repository behavior, and storage result; a domain snapshot cannot establish those effects.

Award one point for each of the three weaknesses, two for an independent state-and-event projection, and one for the integration limit. Do not infer that a database rollback restores an already mutated in-memory object unless that object restoration is explicitly implemented and verified at the relevant boundary.

## NA09-A: queue history, eight points

After the four signup/signoff actions, there are three records: Ada at 09:00 signed off, Ben at 09:05 active, and Ada at 09:15 active. The earliest active record is Ben's. Promotion at 09:20 creates Ben's attendee with decision date 09:05, zero guests, and the current event fee. Ben's moved date becomes 09:20, and his queue record becomes inactive. Ada's second record remains active.

Deleting Ada's first record from the worksheet would erase the distinction between first participation and later rejoining. Merging both Ada records by member identity would similarly lose signup ordering and status history. Collection count, active record count, and active identities should therefore be separate columns. The method retains records rather than removing them as part of signoff or promotion.

Award three points for record history, two for active ordering, two for the two different timestamps, and one for guests and current fee. The answer should not claim that a fee was reserved at signup or that promotion itself emits a dedicated moved event in the selected method.

## NA09-B: source versus policy, six points

The selected signup method does not visibly check that the meeting is full. Its membership rule accepts an attendee collection but checks group membership only, so that expression does not establish an existing-attendee exclusion. AddNotAttendee searches for the next active waitlist member after a nullable attendee lookup; promotion is not visibly conditional on that lookup finding a participant and freeing a place.

These conclusions are scoped to inspected domain methods and predicates. They do not prove that every external caller can reach those paths with arbitrary input. A transport or application claim needs the corresponding validators, handlers, and execution evidence. A stronger product policy can be sensible while still being absent from these selected expressions.

Award two points per claim when the answer cites the relevant code boundary and preserves the scope distinction. Do not award credit for inferring behavior from an unused field name or from the everyday meaning of waitlist. Names can suggest intent, but the executable predicate determines the current source trace.

## NA09-C: redesign choices, six points

One coherent proposed policy is to promote only after a real capacity release, preserve chronological order with an explicit stable tie-breaker, and reject the whole transition unchanged if the earliest member is ineligible. Another policy could skip ineligible members while recording why; that requires clear status and event rules. There is no single mandatory product answer, but the consequences must be explicit.

For guest-aware parties, specify where requested guests are stored and whether a party must fit entirely. Choosing a later smaller party changes fairness and cannot be treated as a mere optimization. State whether rejection preserves the not-attendee decision as well as queue and attendee state, and identify the events expected only on accepted transitions.

Award two points for eligibility and capacity policy, two for guests and tie handling, and two for unchanged-state and event evidence. A design that calls the current zero-guest promotion path guest-aware without adding a data contract is incomplete. Label every new behavior as proposed rather than rewriting characterization expectations.

## NA10-A: cancellation timeline, eight points

The first before-start cancellation sets the flag, actor, and date and adds one cancellation event. A second before-start call by another actor passes the time guard but skips the already-canceled mutation block. The original actor and date remain, and the cancellation event delta is zero. A later call after start throws the start rule before considering the flag, so it is not an unconditional successful replay.

At exactly start, the strict greater-than comparison does not break the shared rule. The first cancellation at that instant can therefore enter its mutation block, while an already-canceled meeting skips it after passing the guard. Use independent fixtures or clearly specified sequential state to avoid mixing these variants.

Award three points for the first and second state transitions, two for the after-start exception order, two for equality, and one for precise conditional-idempotency language. A passing positive creator test does not establish an organizer-only authorization policy in the selected Cancel method.

## NA10-B: removal policy, six points

The current reason predicate rejects null and empty but accepts whitespace-only text. A proposed trimmed nonblank policy would reject whitespace and must define whether accepted reasons are stored trimmed or merely validated using a trimmed view. Isolate the reason guard with a valid attendee and a future meeting; otherwise an earlier start or eligibility rule can mask it.

Repeated removal should be characterized because the lookup predicate does not include the removed flag and the first removal does not change the attendance decision. The source predicts another accepted child removal with updated metadata and another event when the reason passes. Treat that as a source-derived prediction until a real aggregate test executes it. A proposed no-op or rejection policy is a separate specification.

Award two points for current string behavior, two for isolated fixture design, and two for repeat-policy separation. A statement about child state cannot establish a database update, refund, or external notification. Those effects need their own reviewed path.

## NA10-C: lifecycle matrix, six points

Cancel, RemoveAttendee, SetHostRole, and SignOffMemberFromWaitlist visibly invoke the start rule. ChangeMainAttributes and MarkAttendeeFeeAsPayed do not show that guard in their selected bodies. SetHostRole has explicit actor authority through the role rule; the other listed methods must be described according to their own visible checks rather than borrowing that authorization. Event ownership also differs between root cancellation and child role, removal, or fee events.

The claim that every meeting change is forbidden after cancellation is not established by the flag's existence. Inspect each method for the flag and then inspect the actual request path for outer restrictions. To make an endpoint claim, follow command creation, identity source, validators, handler invocation, and error translation, then execute an appropriate request-level check.

Award three points for the selected-method distinctions, two for rejecting the unsupported universal claim, and one for the additional evidence plan. Unknown and absent should remain different matrix values when a source boundary has not been inspected.

## NA11-A: ownership and payloads, eight points

MeetingCreatedDomainEvent and MeetingCanceledDomainEvent are added directly to Meeting. MeetingAttendeeAddedDomainEvent and NewMeetingHostSetDomainEvent belong to attendee children. MemberSignedOffFromMeetingWaitlistDomainEvent belongs to a waitlist child. A recursive collection can surface them together, but that does not change their owner or prove global chronological ordering.

For each operation, capture a baseline or clear and verify the relevant graph, then assert the selected event delta, cardinality, meeting identity, and target identity. Cancellation additionally checks supplied actor and controlled date. Attendee addition should account for the creator host's fixture event if it was retained. A single matching event with wrong payload is insufficient, just as two correct-looking duplicate events violate an expected single transition.

Award three points for ownership, three for payload and count, and two for fixture isolation. The word published in a helper name does not add outbox or broker evidence to the unit test.

## NA11-B: independent snapshots, six points

Materialize a new array of immutable event projections before invocation, and copy the selected attendee state into independent primitive or value-object summaries. Do not keep the read-only wrapper or the mutable entity as the before value. Historical records sharing a member identity need an additional stable occurrence distinction so one record cannot replace another unnoticed in the comparison.

A reflection helper should throw a clear error if a required field is missing. Returning null silently can create a false equality between two absent observations. Choose fields based on the proposed rejection contract and include all relevant child event collections. Avoid generic serialization that may omit private fields or encounter cycles without a reviewed policy.

Award two points for immediate materialization, two for historical-record identity, and two for explicit inspection failure and relevant scope. Snapshot completeness should be justified from affected state, not from the convenience of whatever properties happen to be public.

## NA11-C: helper audit, six points

Collection asks whether Entity is assignable from the declared field type, which recognizes a derived-entity field. Clearing reverses that direction for direct fields, so the two checks are not generally equivalent. A controlled graph with a direct field declared as a derived entity and another child inside a list distinguishes the paths. The list branch explicitly tests runtime elements as Entity in both helpers.

The helper also lacks a shown visited set, so a cyclic or multiply referenced graph needs additional review. Its in-memory collection cannot establish outbox persistence or external subscriber execution. Nor does a root-only collection establish absence of child events. These are different evidence boundaries rather than defects that every current fixture necessarily triggers.

Award two points for the direction, two for a discriminating graph, and two for delivery limits. Avoid claiming that every current meeting test fails because of the direct-field asymmetry; the actual meeting children examined here are stored in lists.

## NA12-A: proposed title policy, eight points

Null, whitespace-only, four-character, and eighty-one-character trimmed results reject. Five and eighty characters accept. Padded valid text accepts and stores exactly its trimmed form; internal spaces remain. The specified unit is .NET string Length after trimming, not a count of user-perceived Unicode symbols. Construct exact repeated-character boundary strings rather than estimating a sentence's length.

An alternative policy might use a different text-length unit or preserve outer whitespace while validating a normalized view, but it must change the examples and stored-value contract explicitly. Such a variation is a proposal, not current repository behavior. A shared creation/change invariant should produce consistent accepted values across both paths.

Award three points for boundaries, two for normalization, one for the length unit, and two for a coherent alternative. Do not derive expected output by calling the same helper being tested; the written examples must remain an independent oracle.

## NA12-B: all-fields rejection, six points

Construct an original meeting with distinct known values and a candidate request whose non-title fields are all different but independently valid. Capture title, term, description, location, limits, RSVP, fee, change metadata, relevant children, and event projections before invocation. On invalid title, compare the complete projection and assert the intended rule. This detects an early description assignment and an early event append even when the rule exception remains correct.

For creation, the handler test should assert that AddAsync was not called after rejection. For change, the repository substitute returns the known aggregate whose before snapshot is compared. Await the reflected task so asynchronous failure is actually observed. A retained reference or term-only assertion cannot satisfy the expanded contract.

Award two points for distinct valid sentinels, two for state plus events, and two for handler boundary evidence. Database rollback remains a separate integration concern.

## NA12-C: implementation and compatibility, six points

A value object can normalize and validate before aggregate invocation; aggregate prevalidation can also prepare the normalized string before assignment. Handler-only checks leave other aggregate callers outside the invariant. Both domain strategies require review of creation, change, materialization, and mapping consequences. Historical stored titles may violate the new policy, so constructor placement must not accidentally choose an unplanned migration strategy.

Domain tests establish normalization and unchanged-state rejection. Handler tests establish argument mapping and repository interaction. Persistence tests establish loading and storing the new representation or policy. Transport tests establish request validation, identity, and error shape. Passing one layer does not replace the others. Existing fixtures with short placeholder titles should be updated only after confirming their original test purpose.

Award two points for boundary comparison, two for historical compatibility, and two for the evidence ladder. Completion requires an honest account of which layers were executed and which remain proposed, not merely a large passing test count.
