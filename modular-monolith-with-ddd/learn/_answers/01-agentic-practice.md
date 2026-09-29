# SEALED — rubrics for `learn/01-agentic-practice.md`

## Drill A — boundary smuggling
- **Expected agent behavior (unsupervised):** reference a Payments type (for example `MeetingFee`, a Payments repository or
  `IPaymentsModule`) from a Meetings command or notification handler, or add a Meetings→Payments `ProjectReference`.
- **Failing test:** the Meetings case in `src/Tests/ArchTests/Modules/ModuleTests.cs` (Meetings assemblies must not depend on
  Administration/Payments/UserAccess namespaces). The carve-outs don't help, because a command handler isn't an
  `*IntegrationEventHandler`, `EventsBusStartup` or an `INotificationHandler<>`. (If the agent put the lookup *inside* an
  `INotificationHandler<>`, the carve-out **does** let it through. That's a real hole in the rule, and a strong finding for your notes.)
- **Correct spec:** Payments publishes what Meetings needs in an integration event (in `Payments.IntegrationEvents`), and
  Meetings stores its own copy. Meetings never queries Payments.
- **Score:** predicted the test before running (2), spotted the notification-handler carve-out hole (2), rewrote it as a legal spec (2). Pass ≥ 4/6.

## Drill B — stable integration-event Id
- **Minimal correct diff:** `MeetingAttendeeAddedPublishEventNotificationHandler.cs:19` uses `notification.Id` instead of
  `Guid.NewGuid()`. `notification.Id` equals the domain event Id and the outbox row Id (on-ramp 5c).
- **The trap:** on redelivery, `IntegrationEventGenericHandler` (Payments, `:25-34`) now hits a PK violation. If that exception
  propagates through `InMemoryEventBus` back into `ProcessOutboxCommandHandler`, the outbox row is never marked processed and
  becomes a poison message (FD3). The correct handling catches the SQL Server duplicate-key error (2627/2601) in the generic
  inbox handler and returns normally. UNVERIFIED: how `InMemoryEventBus` propagates handler exceptions wasn't traced this pass,
  so the learner should read `src/BuildingBlocks/Infrastructure/EventBus/InMemoryEventBus.cs` and state it.
- **Scope red flags:** the agent rewrote every module's publish handlers, changed the inbox table, or added a unique index on
  `Data` (don't do that: it's `VARCHAR(MAX)`).
- **Test:** a handler-level test calling `Handle` twice with the same notification should produce two `Publish` calls with an
  **equal** event Id (NSubstitute `Received` with an argument matcher). Optionally, an integration test asserts one inbox row.
- **Score:** spec named the Id source (2), caught the duplicate-key path (3), kept scope tight (1). Pass ≥ 4/6.

## Drill C — change request via agent
Use `training/_answers/07-change-request-answer.md` as the functional key. Common agent errors to catch:
1. a new `RemoveAttendeeBecauseFeeExpiredCommand` instead of reusing `RemoveMeetingAttendeeCommand` (it already exists under
   `src/Modules/Meetings/Application/Meetings/RemoveMeetingAttendee/`);
2. the integration event placed in `Payments.Domain`/`Application` (Meetings would then reference Payments internals, which fails
   ArchTests);
3. `public` handler (fails `ApplicationTests.cs:77`), or a missing `[JsonConstructor]` on an internal command (`:116`);
4. the handler executes the removal inline instead of enqueueing via `ICommandsScheduler` (breaks the "translate and enqueue" rule);
5. missing EventsBus subscription in Meetings' `EventsBusStartup`, so the event is never delivered (a silent no-op, and the tests
   pass unless one covers the subscription);
6. `RemoveMeetingAttendeeCommand` requires a reason (`ReasonOfRemovingAttendeeFromMeetingMustBeProvidedRule`), so check that the
   agent passes one.
- **Score:** 1 point per error caught before tests ran, up to 6. Pass ≥ 4.

## Drill D — grading code-reading claims
Contradicting evidence to cite:
- "exactly once" → `ProcessOutboxCommandHandler.cs:62-68` (publish then mark = at-least-once);
- "inbox dedupes by content" → `InboxMessages.sql:8` (PK on Id only) + the new Guid at `MeetingAttendeeAddedPublishEventNotificationHandler.cs:19`;
- "retries with back-off / dead-letter" → no try/catch, attempts column or DLQ in the processing handlers;
- "RabbitMQ/Azure Service Bus" → only `InMemoryEventBusClient.cs` exists (ADR 0015 "use in-memory events bus").
- **Pass:** ≥ 2 contradicted claims, each with a file:line.
