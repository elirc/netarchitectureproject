# Solutions and assessment: chapters 13-20

The final eight chapters contain twenty-four preparation exercises worth 160 points. Together, the twenty-chapter route contains sixty graded exercises worth 400 points. The two capstone rubrics add 120 separate assessment points; do not count their sixty-point rubrics as extra chapter exercises. Use the hints before the full answers and award credit for precise evidence boundaries as well as correct predictions.

## Hints before full answers

For chapter 13, distinguish scope lifetime from transaction semantics, and read the statements before and after each awaited call. A handler result can exist before the decorator returns it. Follow each cancellation token rather than assuming propagation from a signature.

For chapter 14, write the private field, owned type, storage column, and independent sentinel on one row. Historical child identity includes more than a member GUID. A same-context observation can hide storage and materialization errors.

For chapter 15, compare the SQL view's predicates with the aggregate's active predicate. Count rows, named active members, and occupied places separately. An alias generated with nameof can still point at the wrong source column.

For chapter 16, separate direct action invocation from routing, binding, authorization, and middleware. Creation returns the action's explicit result, not whatever response convention you prefer. Read the environment branch around error middleware.

For chapter 17, setup effects happen even when a test filter selects one method. Follow the fixture's group and member prerequisites, mixed clocks, and message-selection assumptions before diagnosing the target command.

For chapter 18, mark every transition between an in-memory collection, tracked entity, outbox row, recipient attempt, and processed marker. A later marker does not retroactively make an earlier external effect atomic.

For the capstones, choose a declared route and keep its completion claim consistent. A finished design is not an implemented feature. A successful domain experiment is not persistence evidence. Independent oracles and positive controls are essential in both tracks.

## NA13-A: orchestration trace, eight points

Attendee addition takes meeting identity and guests from the command, loads the meeting, derives its group identity from the loaded aggregate, loads that group, and supplies the current context member to AddAttendee. Role demotion similarly loads meeting and group, but supplies the actor from context and the target from the command. Use different actor, target, meeting, and group identities so substitutions are observable.

The inspected handlers do not show a custom missing-meeting result before using the retrieved object. A missing repository result can therefore interrupt the path before the intended domain rule. Do not invent a NotFound return in the handler trace. Award three points for identity origins, three for repository and aggregate order, and two for the missing-object boundary and distinct fixture values.

## NA13-B: failure boundaries, six points

Validation failure prevents that decorator from invoking its decorated handler. A decorated-handler exception prevents the unit-of-work decorator's later commit call. Dispatch failure prevents UnitOfWork from reaching SaveChanges on its normal sequential path. SaveChanges failure occurs after dispatch was invoked. None of these statements alone restores earlier in-memory mutations or proves reversal of external recipient effects.

A possible email or other external call inside an event handler would need its own source and execution evidence before an atomicity claim. Award three points for the four local order predictions, two for distinguishing skipped from restored work, and one for a separately scoped external-effect investigation. Do not infer exact resolved decorator nesting solely from registration order without the relevant composition evidence.

## NA13-C: results and tokens, six points

The result-returning decorator captures the handler result, performs any applicable internal-command marking, awaits CommitAsync, and then returns the result. A newly generated identity in the handler is therefore not yet proof of a saved row. The controller may also ignore that result rather than include it in the response.

The decorator forwards its token to the decorated handler and commit. UnitOfWork forwards it to SaveChanges, while the inspected DispatchEventsAsync call has no token argument. Individual repository calls must be traced separately. Award two points for result ordering, two for durability and response separation, and two for exact token forwarding. A token-bearing signature does not establish universal cancellation or rollback.

## NA14-A: mapping ledger, eight points

The ledger maps _title to Title and _description to Description. Owned _term properties map to TermStartDate and TermEndDate; owned _rsvpTerm properties map to the RSVP columns. Location name, address, postal code, and city have separate columns. Event fee value and currency and meeting attendee/guest limits are separately mapped owned values. Cancellation fields map flag, date, and member identity independently.

Use different start and end values, different location text, a defined fee, and a second nullable case. Null attendee ceiling must remain distinct from zero, and undefined fee must not be silently treated as a zero charge. Award four points for correct field-to-column relationships, two for discriminating sentinels, and two for null semantics. A nonnull aggregate assertion is not a mapping ledger.

## NA14-B: history round trip, six points

Waitlist identity includes member, meeting, and signup date in the configured composite key. Two occurrences of the same member therefore need distinct occurrence values in a valid fixture. Save through the intended path, end the tracking scope, and observe through a fresh context or independent query. An identity-only dictionary can collapse history, while a same-context lookup can return the already tracked object and hide storage defects.

Provider timestamp precision remains a separate question until table definitions and runtime behavior are verified. Use clearly separated fixture times for the ordinary round-trip test. Award two points for key identity, two for the fresh observation boundary, and two for duplicate-preserving comparison and precision limits.

## NA14-C: title compatibility, six points

A proposed title value object requires an explicit mapping to the intended Title storage representation and a review of materialization. Existing short titles may violate the new rule, so choose migration, grandfathering, or validation-on-change deliberately. The read query's Title projection must remain compatible with the chosen storage shape.

Source inspection establishes configured fields and owned types, but not every runtime construction path or historical-row outcome. A controlled materialization test supplies that evidence. Award two points for mapping, two for historical policy, and two for the source-versus-runtime distinction. Do not assume constructor checks either always run or always bypass validation without executing the relevant mapping path.

## NA15-A: details projection, eight points

Map every selected details column to its DTO property, preserving independent start/end and RSVP values, distinct location fields, nullable total limit, and nullable fee value with its currency contract. A source column selected incorrectly but aliased with nameof still compiles; selecting TermStartDate under the TermEndDate alias is a useful conceptual mutation.

A positive nondefault fixture detects omitted or swapped fields better than an all-null or zero-valued object. The existing nonnull integration assertion is weaker than this field-level projection test. Award four points for a complete independent mapping table, two for null alternatives, and two for a mutation that demonstrates why compiler-linked aliases do not prove semantic column selection.

## NA15-B: attendee measures, six points

With creator host, active attendee with two guests, and removed historical attendee, the inspected joined view can project three rows when all member join partners exist. The domain active calculation counts two named active members and four occupied places. The view and handler show no removed or decision-changed filter; the inner join can also omit a stored attendee whose member row is absent.

A proposed current-attendee query must define the active policy explicitly and preserve historical access elsewhere if required. Award two points for the three different measures, two for filter and join evidence, and two for a clearly proposed read contract. Do not describe the current query as active-only based on its endpoint name.

## NA15-C: order and missing rows, six points

Compare unordered results using a duplicate-preserving projection, including an occurrence discriminator for historical records rather than only attendee identity. Sorting in the test normalizes an unordered contract; it does not prove the SQL returns that order. The selected query has no ORDER BY.

For an absent details identity, trace QuerySingleAsync and the outer exception path instead of inventing NotFound. Execute a hosted test before claiming the final HTTP response. The selected Dapper calls do not show forwarding the handler token through a command definition. Award two points for ordering, two for missing-row boundaries, and two for token and HTTP limits.

## NA16-A: request map, eight points

Creation maps body fields into CreateMeetingCommand and returns empty Ok after awaiting execution. Editing takes meeting identity from the route and candidate attributes from the body. Attendee addition passes route meeting identity and guest count; the handler supplies the current member. Role demotion passes target identity from the request, while its handler supplies the actor from context.

The application's creation identity is not automatically returned because the action does not place it in the Ok result. Award four points for the four maps, two for actor/target distinction, and two for the normal response contract. A 201 or Location header would be a proposed API change, not a characterization of this action.

## NA16-B: error evidence, six points

The business-rule problem-details constructor supplies conflict status and exception detail; the invalid-command constructor supplies bad-request status and errors. Startup registers mappings for those exceptions. The visible UseProblemDetails activation is in the development branch, so a constructor assertion or mapping registration does not prove identical serialized output in every environment.

A constructor test checks values, a configuration review checks registration, and a hosted development request checks activation and serialization. This course did not run the hosted request. Award two points for mapping values, two for environment scope, and two for clearly separated tests. Do not report a real HTTP 409 merely because a problem-details object has Status set to 409.

## NA16-C: identity and authorization, six points

Use an authorized actor A and distinct target B, then verify context supplies A and the command supplies B to the role operation. Plan hosted outcomes for unauthenticated, authenticated without permission, and authorized principals using synthetic fixture identities. Direct action invocation bypasses those middleware boundaries.

The commented standalone authentication call is not enough to conclude authentication is absent because identity-service extension behavior and scheme configuration also matter. Permission attributes alone likewise do not prove enforcement. Award two points for the actor/target fixture, two for the three-outcome hosted plan, and two for avoiding both unsupported broad conclusions.

## NA17-A: fixture ownership, eight points

A test filter does not skip SetUp. The integration base reads its configured connection and calls ClearDatabase before module initialization, deleting a collection of meetings-schema tables. Therefore, execution requires a dedicated owned database whose cleanup is intended. Record environment availability and the project/test target without printing the connection value.

The disposable labs instead copy selected source into unique temporary directories, compile SDK-only projects, and compare original hashes. They do not invoke this database fixture. Award three points for setup effects, two for ownership, two for a credential-free receipt, and one for the lab contrast. An unavailable integration environment should remain an explicit unexecuted boundary.

## NA17-B: creation evidence, six points

The calling test creates the member; the helper proposes and creates a group, queries the single group, sets future expiration, and creates the meeting with the context user as host. The Single assumption depends on isolated data. Meeting start/end use direct UtcNow calls while expiration uses SystemClock.

Strengthen assertions with exact sentinel details, interval boundaries, host identity, and role, rather than only nonnull details and count one. Award two points for prerequisites, two for independent projection assertions, and two for isolation and mixed-clock observations. Do not infer every fixture timestamp is frozen merely because teardown resets SystemClock.

## NA17-C: asynchronous diagnosis, six points

Select the intended outbox notification by type and stable domain or message identity, verify cardinality, and inspect its payload. Use a bounded condition probe rather than an unexplained fixed sleep. Record relevant observed states on timeout so missing trigger and delayed completion can be distinguished.

Classify missing environment configuration as prerequisite failure, schema mismatch as database/setup failure, and wrong DTO field after successful command as mapping/query evidence failure. Award two points for identity-specific observation, two for bounded polling, and two for causal diagnosis. Increasing a timeout does not repair a wrong message-selection assumption.

## NA18-A: event-to-outbox trace, eight points

The runtime accessor collects events from tracked Entity entries. The dispatcher optionally resolves notifications, clears entity collections, publishes domain events in process, serializes resolved notifications, and adds outbox objects. UnitOfWork calls SaveChanges after dispatch returns. The reflection-based test helper traverses a different boundary and cannot prove runtime tracking.

An event without a resolved notification does not create an outbox message through the inspected notification path. Award four points for order, two for runtime-versus-test collection, and two for optional notification mapping. Do not equate in-process mediator publication with external broker delivery.

## NA18-B: partial failures, six points

Deserialization failure prevents notification publication. Recipient failure prevents the later processed-date update on the normal path. Successful publication followed by marker-update failure can leave a row eligible for later selection even though recipient work may already have occurred. Exactly-once effects would require recipient, deduplication, concurrency, and transaction evidence beyond this order alone.

These are source-derived failure windows until executed in an owned fixture. Award three points for stage predictions, two for separating attempt, effect, and marker, and one for the stronger guarantee's missing evidence. A null marker is not proof that the recipient did nothing.

## NA18-C: retries and cancellation, six points

Retrying the same context can encounter cleared event collections, while a fresh command scope recreates a different lifetime and may regenerate domain work. Treat them as distinct experiments. The processor passes its token to mediator publication; the selected SQL calls do not show the same explicit token forwarding.

Use a recipient test double with stable message identity and separate attempt/effect counters. Inject failure at a named stage without contacting real services. Award two points for lifetime distinction, two for token trace, and two for the isolated recipient experiment. Cancellation alone is not an automatic rollback guarantee.

## NA19-A: acceptance packet, eight points

The packet accepts a padded five-unit title in normalized form; rejects four units unchanged; rejects eighty-one units on creation without addition; accepts eighty units with correct interval mapping; preserves the old capacity rejection with a valid title; preserves nullable-limit and undefined-fee semantics; handles a historical title according to the chosen compatibility policy; and verifies the read projection after a successful persisted change.

Domain and substitute-handler tests can cover the first rejection and mapping boundaries. Historical materialization and fresh read projection require an owned persistence fixture on the implementation route. Award four points for exact scenarios, two for independent expected values, and two for correct evidence allocation. A design-only packet must not label the latter scenarios executed.

## NA19-B: mutation map, six points

Accepting eighty-one units should fail the upper-bound rule assertion. Trimming only on creation should fail a padded change's exact stored-title assertion. Early description assignment should fail the independent rejection-state projection. Early event append should fail the event projection even if all fields remain unchanged.

Earlier invalid interval, invalid limits, or fixture prerequisite failures can prevent the intended title path from being reached; use otherwise valid candidates and a valid aggregate. Compiler or reflection-construction failures do not count as semantic mutation detection. Award three points for mutation-to-assertion matches, two for reachability, and one for failure-stage interpretation.

## NA19-C: review decision, six points

Passing title unit tests can support the pure normalization and boundary policy they execute. Without event snapshots, they do not establish complete unchanged-state rejection. Without mapping review, they do not establish persistence compatibility. Accept the demonstrated component evidence while requiring those missing pieces before implementation completion.

A useful review requests concrete additions: sentinel rejection projection including events, creation no-add assertion, mapping and historical-data decision, and the appropriate fresh-scope evidence for the declared route. Award two points for accepting only supported claims, two for specific missing work, and two for separating design completion from implemented-feature completion.

## NA20-A: claim ledger, eight points

For track A, distinguish source mutation order, executed child role after rejection, event delta, persisted state, and HTTP response. Correct the overclaim exception means rollback to the narrower statement that the expected rule was raised; unchanged state still needs observation. For track B, distinguish selected row, publication attempt, recipient completion, processed marker, and replay effect.

Each ledger row needs a source anchor and observation method appropriate to its claim. Award three points for distinct boundaries, two for a corrected overclaim, and three for concrete evidence methods. A collection of identical source pointers without explaining what each test observes is not a complete ledger.

## NA20-B: oracle and controls, six points

Track A needs independent child-state and event projections plus a two-host success control. An early event append with restored role defeats a role-only test and should fail the stronger oracle. Track B needs separate attempt, durable-effect, and marker observations plus complete-success and pre-publication-failure controls. An attempt log alone must not count as a durable effect.

Setup and compile failures do not reach the intended behavior, so they cannot satisfy either experiment. Award two points for the independent projection, two for a discriminating mutation, and two for positive controls and stage interpretation. The oracle must be specified before observing the result.

## NA20-C: reviewer decision, six points

A complete design-only packet can be accepted as a source-grounded contract and experiment plan while explicitly remaining unimplemented and unexecuted at its integration boundaries. An implementation packet lacking required persistence evidence can be accepted for demonstrated domain behavior but not represented as a complete end-to-end feature.

State the next concrete check and why it matters: fresh-scope storage observation, identity-specific outbox replay, or hosted error translation depending on the chosen track. Award two points for each scoped completion decision and two for a precise remaining evidence request. Do not reject useful design work merely because it is not implementation, and do not award implementation completion because the design is detailed.

## Final assessment guidance

A strong learner submission can explain a surprising current behavior without defending it as ideal or silently repairing it in the description. It can propose a stronger rule while preserving the old characterization and identifying compatibility effects. It can also say not executed with enough detail that another engineer knows exactly how to obtain the missing evidence.

Review the course as a connected chain: command mapping supplies values, factories establish local validity, aggregate methods coordinate state, mappings preserve representation, queries choose projections, controllers expose contracts, and dispatch processing introduces further failure boundaries. No single green test covers that chain automatically. The completed route equips you to build the chain deliberately, one independently observed boundary at a time.
