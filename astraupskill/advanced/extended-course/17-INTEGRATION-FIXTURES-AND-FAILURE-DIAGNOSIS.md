# 17. Integration fixtures and failure diagnosis with owned data

Integration tests expand evidence and also expand effects. Read [the integration TestBase](../../../modular-monolith-with-ddd/src/Modules/Meetings/Tests/IntegrationTests/SeedWork/TestBase.cs), [MeetingCreateTests](../../../modular-monolith-with-ddd/src/Modules/Meetings/Tests/IntegrationTests/Meetings/MeetingCreateTests.cs), [MeetingHelper](../../../modular-monolith-with-ddd/src/Modules/Meetings/Tests/IntegrationTests/Meetings/MeetingHelper.cs), and [OutboxMessagesHelper](../../../modular-monolith-with-ddd/src/Modules/Meetings/Tests/IntegrationTests/SeedWork/OutboxMessagesHelper.cs). This chapter is a source-bound test design and diagnosis guide. The full integration suite is not run by the course.

The repository's fixture performs database cleanup, so its execution requires a dedicated owned test database. That is a concrete property of the inspected setup, not a generic warning about all tests. Keep the course's disposable SDK labs separate from this database-backed fixture; their prerequisites and effects are fundamentally different.

## Read setup before choosing a command

The integration base reads its connection string from a named environment variable and raises an application exception if it is unavailable. Before initializing the module, it opens a SQL connection and calls ClearDatabase. That method issues deletes against a collection of meetings-schema tables, including inbox, internal commands, outbox, attendees, groups, meetings, comments, countries, and members.

A command that merely filters one test still executes its fixture setup. Filtering by test name does not turn the cleanup into a read-only operation. Therefore, a learner should first establish that the configured database is disposable and belongs to this test workflow. Do not print the connection-string value into a report; record only that the required isolated environment was or was not available.

The course does not provision that environment or install missing dependencies. Its validation report instead names the exact project path and marks full integration execution as not run. This is a complete and honest documentation check, not a failed attempt to make every possible suite green regardless of effects.

## Understand module initialization and teardown

Setup creates a logger, an execution-context mock with a new user identity, and initializes MeetingsStartup with the connection, context, logger, email configuration, and an event-bus mock. It then creates MeetingsModule. Teardown stops the module and resets SystemClock. These operations establish a broader environment than a direct aggregate test.

The base also assigns an EmailSender substitute property, but the visible Initialize call does not pass that property as an argument. Do not infer that all email behavior is intercepted by that substitute solely because the property exists. Follow startup registrations and the actual sender path if email isolation becomes the subject of an experiment. A fixture member's name is not proof of its wiring.

Teardown is important for background processing and shared clock state. A test interrupted before normal teardown may require an environment-specific recovery procedure; the course does not provide a broad cleanup command. Keep ownership and effects explicit rather than deleting unrelated state to make the next run start clean.

## Follow the creation helper's prerequisites

MeetingHelper first proposes a group, creates a group from the proposal, queries all groups, chooses the single group, and sets its expiration date into the future. It then creates a meeting with a future interval, location values, finite limits, null RSVP bounds and fee, and a host list containing the execution-context user identity. The calling creation test first creates the member associated with that user.

Those steps satisfy domain prerequisites that a shortcut fixture might miss. A failure in meeting creation may originate in missing membership, group payment or expiration state, or the helper's assumption that exactly one group exists. The helper is not just boilerplate. Its preconditions determine which domain rule a later command can reach.

The use of Single on the queried groups also depends on test isolation. If the database contains extra groups because cleanup did not target the intended environment or concurrent tests interfere, the helper can fail before the meeting command. Diagnosing that as an interval-rule regression would be incorrect. Trace the earliest failing operation and preserve the exception stage in the receipt.

## Existing assertions are useful but narrow

MeetingCreateTests queries details after creation and asserts that the result is nonnull. It queries attendees and asserts a count of one. This adds module and read-model evidence beyond a direct aggregate test, but it does not assert every mapped field, exact interval boundaries, fee semantics, role payload, or HTTP response.

A proposed extension can add distinct sentinel values and compare the details DTO field by field. Another can verify the creator host's identity and role rather than only attendee count. Keep the query's current historical-row semantics in mind when extending attendance lifecycle tests. A count of one in a simple creation fixture does not prove that later queries filter removed or changed-decision records.

Do not inflate the meaning of an existing green test. A receipt should state the assertions it actually makes. If the suite was not run in the current environment, say the source contains those assertions rather than claiming they passed. The course's reports distinguish source review from execution for exactly this reason.

## Time control is partial unless every clock is traced

The helper uses SystemClock for group expiration but direct DateTime.UtcNow reads for meeting start and end. Other domain code, such as not-attendee construction, also reads the wall clock directly. Setting SystemClock therefore does not freeze every timestamp involved in an integration fixture.

A proposed deterministic rewrite should identify each time source before changing it. A test can avoid exact equality for intentionally uncontrolled timestamps while still asserting sensible ordering, but it should not use broad tolerances to hide an unrelated mapping error. For boundary tests, prefer a controlled domain fixture or a deliberately designed test clock path rather than a full integration helper with mixed clocks.

Parallel execution adds another concern because SystemClock is static. Resetting after each test limits leakage during normal teardown but does not make simultaneous clock mutations independent. Inspect suite-level parallelization before adding tests that manipulate the shared clock. A test can be deterministic alone and still race when run with another fixture.

## Outbox observation needs identity, type, and timing

GetLastOutboxMessage reads outbox rows ordered by OccurredOn and deserializes the last row into a requested notification type. This convenience assumes the last relevant row is the one you want. Multiple messages, equal occurrence times, or background processing can make that assumption fragile for a more complex scenario.

A stronger proposed assertion selects the message by expected type and correlation or domain identity, checks cardinality, and inspects its payload. Do not assume a successful cast from the last row proves the operation's intended notification when other messages may be present. The helper's deserialization uses stored type information and can return a result incompatible with the requested generic type.

Outbox existence is still not external delivery. A row can be present and unprocessed; a processed marker can be written after notification publication. Chapter 18 describes the selected processing order. Your integration assertion should say which state it observes and avoid treating every outbox-related check as a broker-delivery test.

## Poll conditions rather than sleeping blindly

The base exposes AssertEventually through a Poller and probe abstraction. This indicates a testing pattern for effects that may become visible after asynchronous processing. A useful probe checks a domain-relevant condition and produces diagnostic information when its timeout expires. A fixed sleep merely delays and then guesses whether enough time passed.

When designing a new eventual assertion, specify the maximum wait, the exact condition, and the evidence retained on failure. Do not continuously mutate state while polling a read condition. Also distinguish absent forever from not yet visible by recording the observed states or relevant message identifiers within the owned fixture.

This chapter does not execute the poller or claim a particular scheduler latency. The source suggests a mechanism for bounded observation; the actual timing behavior depends on the initialized environment. A test that succeeds only after increasing an arbitrary timeout may still have an incorrect condition or missing trigger.

## Build a failure-stage checklist from the trace

Classify failures into prerequisite discovery, database connection, cleanup, module initialization, fixture command, target command, commit or dispatch, query projection, and final assertion. Each stage implies a different next action. A missing environment variable is not a failed domain invariant. A SQL schema mismatch is not a controller binding issue. A wrong DTO field after a successful command requires mapping and query investigation.

Record the first meaningful exception without exposing sensitive configuration. Include the synthetic scenario and exact test target. If a prerequisite is unavailable, stop that execution path and continue useful source or disposable-lab work. Do not install or reconfigure the application merely to turn an unavailable integration environment into an apparent course success.

For a failed target command, compare its earlier prerequisite guards before changing the expected rule. For a failed final count, inspect fixture history and query filtering. For an outbox mismatch, inspect type and identity selection before increasing a wait. This diagnosis order follows the actual dependency chain and avoids broad speculative repairs.

## Independent practice

Exercise NA17-A, fixture ownership, is worth eight points. Explain why a filtered integration test can still delete data, identify the owned-environment prerequisite, and write a receipt that records availability without revealing connection values. Contrast its effects with the disposable capacity lab.

Exercise NA17-B, creation evidence, is worth six points. Trace the helper's group and member prerequisites and design stronger sentinel assertions than nonnull details plus attendee count. Identify one assumption that depends on database isolation and one timestamp not controlled by SystemClock.

Exercise NA17-C, asynchronous diagnosis, is worth six points. Replace a last-message assumption and fixed sleep with an identity-specific, bounded observation plan. Classify three failures at different stages and name the next useful evidence for each. Review [the final solutions](SOLUTIONS-13-20.md) after completing the plan.


[Complete course route](README.md) | [Separate solutions and assessment](SOLUTIONS-13-20.md)
