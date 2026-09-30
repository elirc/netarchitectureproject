# Hints, solutions, and assessment notes for chapters 01-06

The first installment contains eighteen graded exercises worth one hundred twenty points. Read the hints first only if you cannot identify the next source boundary. Save a prediction before reading each full answer. Credit depends on correctly locating the decision and honestly describing evidence, not merely repeating a final Boolean or exception name.

## Hints before solutions

For chapter one, distinguish a repository read from AddAsync and from a later database commit. Follow argument evaluation before assuming the aggregate method began. For chapter two, make every same-typed input visibly different and identify branches for optional values. For chapter three, write separate inequalities for meeting construction, after-start observation, and RSVP membership.

For chapter four, capture events and metadata in addition to the term. Inspect whether a rule runs before or after mutation rather than assuming a class-wide policy. For chapter five, label each reflection stage and await the returned task. For chapter six, identify the first semantic case that distinguishes a mutation from the baseline. A nonzero exit alone is not enough evidence.

## NA01-A: the responsibility map

The command contains requested start and end values. The handler passes them into MeetingTerm.CreateNewBetweenDates after loading the group. The factory rejects invalid order or returns a value preserving both boundaries. The group checks its own prerequisites and creates the meeting. The aggregate stores the term and collects creation effects. The handler then passes that aggregate to AddAsync, where the substitute can capture it.

This trace supports the mapping claim when the captured aggregate has the exact requested values. It does not show a SQL commit, an HTTP status, or external message publication. Award one point for each correctly traced responsibility and observable, up to six. A diagram that replaces the last three boundaries with saved successfully is too vague because it collapses distinct effects.

## NA01-B: the disposable lab's evidence

A supported statement is that selected real domain sources, copied into an SDK-only net10.0 project, satisfy the exercised interval and temporal cases. The generated adapter can show how a particular mapping defect is detected, but it is not the actual application handler. The next mapping layer is the existing handler regression using real handler reflection and substitutes. A request-level layer is then needed to establish transport input and response behavior.

The full repository's shared target is net8.0. A successful net10.0 copied-source lab does not establish that target's complete dependency compatibility. Award two points for the corrected claim, two for the additional evidence layers, and two for the environment distinction. Do not describe unavailable full-project prerequisites as a business-rule failure.

## NA01-C: rejected change timing

The handler retrieves the existing meeting first. It begins evaluating ChangeMainAttributes arguments, and MeetingTerm construction rejects the equal boundaries. The aggregate method is not entered through that call, so its assignments and change event are not reached. The repository read is expected and must not be forbidden by the test.

A stronger proposed snapshot includes all main fields, identity, creation and change metadata, cancellation state, relevant collections, and events. The existing regression directly checks the old term boundaries, not that complete projection. Award two points each for the read, argument exception, method-entry distinction, and stronger-but-not-yet-existing assertion scope.

## NA02-A: sentinel mapping

A suitable table uses different UTC start and end values and distinct location strings. It maps the start to the first MeetingTerm argument, end to the second, and each location component to its corresponding factory parameter. Limits and optional fee are recorded with their meaning rather than only their primitive type. The observation should be tied to the aggregate the handler actually uses.

Date reversal and address/city swaps can compile because the argument types match. Distinct valid sentinels expose them. Award two points for temporal sentinels, two for other same-typed values, and two for source-to-observation mapping with plausible swaps. Identical placeholder strings weaken the design even if the current implementation happens to pass.

## NA02-B: three defects require different assertions

Passing start twice creates equality and should reject the originally valid request. Reversing start and end creates a reversed interval and should also reject. Shifting end one hour later leaves a valid interval but violates exact mapping, so no-exception alone misses it. Assert the requested StartDate and EndDate on the observed aggregate for successful mappings.

A negative test should identify the strict-order rule rather than accept any exception. Award two points for each mutation prediction and two for explaining why positive preservation assertions complement rejection tests. A syntax-breaking mutation does not receive semantic-mutation credit because it never reaches the intended domain boundary.

## NA02-C: create versus change

Create loads a group, constructs values, asks the group for a new meeting, calls AddAsync, and returns a Guid through Task<Guid>. Change loads an existing meeting, constructs replacements, invokes its method, and returns Task. The inspected change handler has no explicit repository update call. Observing a captured added instance and observing the known loaded instance are therefore different test setups.

A value-object rejection occurs before aggregate entry. A capacity rejection occurs inside ChangeMainAttributes after valid arguments exist but before its assignments. Award two points for orchestration, two for return and observation shape, and two for the rejection-stage distinction. Do not infer database commit behavior from either substitute interaction alone.

## NA03-A: strict interval boundaries

One tick before and equality both raise BusinessRuleValidationException carrying MeetingTermMustEndAfterStartRule. One tick after and two hours after succeed and preserve exact boundaries. Equality distinguishes the current less-than-or-equal rejection from a defective less-than-only rule. The smallest positive case rejects an accidental stronger minimum-duration policy.

Award one point for each outcome, two for exact preservation and specific BrokenRule, and two for mutation discrimination. Expected values must come from the supplied inputs and stated rule. Reading the constructed object's end to calculate the expected end removes the independence of the assertion.

## NA03-B: separate temporal contracts

MeetingTerm requires nonnullable boundaries with end strictly after start. Term accepts nullable boundaries and tests membership inclusively when bounds exist. The inspected Term constructor does not reject equality or reversal. For a meeting starting at ten, RSVP eight-to-nine stays unchanged, eight-to-eleven becomes eight-to-ten, eight-to-open becomes eight-to-ten, and NoTerm becomes open-start-to-ten after aggregate normalization.

A proposed rule preventing RSVP start after meeting start is an extension, not current behavior. Award two points for contract differences, two for clamping predictions, and two for keeping the proposal separate. Applying the meeting's strict inequality to RSVP without a specification would change behavior beyond the focused interval repair.

## NA03-C: clock and equality

Set SystemClock to one tick before, exactly at, and one tick after the same MeetingTerm start. IsAfterStart is false, false, and true. Reset the static clock in guaranteed cleanup. Direct property assertions establish boundary preservation, while value equality depends on the ValueObject reflection contract and runtime type. Neither establishes timezone conversion or ambiguous-local-time handling.

Award two points for the clock table and cleanup, two for equality scope, and two for a correctly excluded timezone claim. A test using SystemClock.Set does not control direct DateTime.UtcNow expressions elsewhere in its fixture. Recognizing that limitation is stronger than assuming a clock abstraction overrides the entire process.

## NA04-A: successful mutation footprint

Main title, term, description, location, limits, RSVP, and fee change according to arguments and normalization. Change date and modifier are updated. Meeting identity, group identity, and creation metadata remain associated with the original meeting. A new main-attributes-changed event is added. The initial constructor already added a creation event and at least a creator-host when no explicit hosts were supplied.

Award two points for changed values and derived RSVP, two for preserved identity and creation history, and two for event and attendee baseline. Exactly one event in the whole collection is not necessarily the correct assertion; one new expected event relative to a known baseline is the clearer claim.

## NA04-B: complete rejection snapshot

Create a valid limit value that is lower than the aggregate's active attendees plus guests while still satisfying MeetingLimits' own rules. Capture scalar fields, nested value components, metadata, identities, relevant attendee states, and a copied event projection. Invoke ChangeMainAttributes with otherwise valid distinct replacements and expect the capacity rule before assignments.

A live reference to a mutable list can change both the before and after observations, hiding mutation. Copy values and normalize ordering according to the contract. Award three points for isolating the intended rule, three for a complete independent snapshot, and two for collection handling. Do not claim this test proves every other aggregate method rejects before mutation; inspect each path separately.

## NA04-C: proposed title policy

The learner must decide null handling and whether trimming changes stored text or only validation. Place the proposed five-through-eighty-character rule before mutable assignments and cover creation and change consistently. A broken late-check version assigns title and term before rejecting. The complete unchanged projection should fail even though the correct business exception is thrown.

Award two points for a precise policy, two for placement and boundary cases, and two for the detecting assertion. This proposal must not be described as an existing shipped rule. A UI character counter can complement it, but cannot replace aggregate enforcement if multiple application paths can perform the mutation.

## NA05-A: invocation stages

Wrong assembly or type name fails resolution before construction. Swapped dependency objects can prevent constructor binding. Missing Handle fails method lookup or invocation setup. An incompatible task cast breaks the adapter's observation. An unawaited task makes completion and exception observation unreliable. In the latter two cases, invocation may have begun, so do not assert categorically that no domain code ran.

Award one point for each of the six diagnoses and two for correctly distinguishing known-not-run from unknown or unobserved execution. The intended business failure is established only after invocation succeeds and awaiting yields the specific rule exception. A broad reflection exception catch should not manufacture that conclusion.

## NA05-B: valid context

The accepted proposal and future expiration allow group creation prerequisites to pass. Member context supplies the actor, and repositories return the intended group or meeting instances. A fixture with an expired group could make an overbroad invalid-interval test throw for an unrelated reason. A positive asymmetric interval case that reaches AddAsync exposes that invalid arrangement.

Award two points for preconditions, two for the false-positive fixture example, and two for the complementary success case. Random ids alone are not proof of a valid relationship: member and group rules determine whether those identities belong together.

## NA05-C: observation mechanisms

The AddAsync callback captures the actual newly added aggregate but does not prove persistence. A configured repository return gives a known change target but remains a substitute. Private-field reflection exposes selected state while depending on implementation names. Domain-event inspection observes collected events, not external publication. A clear helper can fail immediately with the missing field name and declaring type before making business assertions.

Award one point for each mechanism's scope and two for an explicit diagnostic that preserves production encapsulation. Changing a private field to public solely to satisfy a test is not automatically the best design; evaluate an intentional test projection or supported behavior first.

## NA06-A: mutation matrix

The relaxed meeting rule is detected by equal boundaries being accepted. The start-twice adapter is detected when a valid mapped request becomes equal and rejects. The clock mutation is detected exactly at the meeting start, where current behavior is not after-start. The RSVP mutation is detected exactly at its end boundary, which current behavior includes. All four should compile before their intended semantic failure.

Award two points for each mode with the correct discriminating case. Reversed-only interval coverage cannot distinguish less-than from less-than-or-equal because reversal breaks both expressions. A mutation test must reach the relevant assertion rather than merely return a nonzero process code somewhere earlier.

## NA06-B: triage the process result

Baseline success supports only the exercised copied-source cases. Intended semantic failure supports the assertion's ability to detect that mutation. Compilation failure, missing SDK, or unmatched source expression means the behavioral experiment was not completed. These conditions should trigger investigation of environment or harness compatibility, not a claim that the domain contract passed or failed.

Award two points for valid behavioral evidence, two for blocked execution categories, and two for explaining why process status alone is insufficient. Preserve the observed stage and message so a later run can be compared without confusing a setup repair with a domain behavior change.

## NA06-C: shifted-end mutation

Change the generated adapter to pass a valid but later end, such as the requested end plus one hour. Construction succeeds because the interval remains positive. An exact EndDate assertion against the original request detects the mapping defect. This adds evidence that a test expecting only rejection or only successful construction cannot provide.

Award two points for a signature-compatible mutation, two for the independent expected boundary, and two for keeping it in the generated adapter. The original handler and domain source should remain untouched. If the learner instead changes the expected value to match the shifted output, the exercise no longer proves preservation of the requested contract.

## Review discussion

Ask a partner to change one premise: the interval is one tick long, RSVP has no end, the group is expired, the handler type name changes, or the aggregate already has events. Explain which conclusion changes and which evidence remains valid. This transfer exercise exposes whether you understand the boundary or only memorized the worked example.

Keep a record of failed predictions. Name the missed condition and write a new case that distinguishes it. For example, confusing a repository read with a write suggests a trace exercise; confusing task invocation with awaiting suggests an async adapter experiment; confusing a collected event with a published message suggests a later integration-boundary investigation. Chapters 07-20 build on those distinctions; one passing interval lab is not complete architectural proof.
