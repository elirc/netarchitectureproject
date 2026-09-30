# 18. Dispatch, outbox processing, and partial-failure reasoning

An outbox is useful only when its actual boundaries are understood. Read [DomainEventsAccessor](../../../modular-monolith-with-ddd/src/BuildingBlocks/Infrastructure/DomainEventsDispatching/DomainEventsAccessor.cs), [DomainEventsDispatcher](../../../modular-monolith-with-ddd/src/BuildingBlocks/Infrastructure/DomainEventsDispatching/DomainEventsDispatcher.cs), [OutboxAccessor](../../../modular-monolith-with-ddd/src/Modules/Meetings/Infrastructure/Outbox/OutboxAccessor.cs), and [ProcessOutboxCommandHandler](../../../modular-monolith-with-ddd/src/Modules/Meetings/Infrastructure/Configuration/Processing/Outbox/ProcessOutboxCommandHandler.cs). This chapter follows their visible order and designs failure experiments. It does not claim that a broker, email service, or database was exercised during course authoring.

The goal is to replace exactly once happens here with a concrete sequence of reads, in-memory publication, message creation, save, later publication, and processed marking. Each boundary has different evidence and different potential repeat behavior. A class name cannot supply guarantees that its statements do not establish.

## Runtime event collection differs from the unit-test helper

DomainEventsAccessor obtains Entity entries from the context's ChangeTracker, filters those with nonempty event collections, and flattens their events into a list. Clearing similarly visits tracked entities and clears their direct collections. This is different from the reflection-based object-graph traversal used in the domain unit tests.

Consequently, an event visible to the recursive test helper is not automatically evidence that the runtime accessor sees it. The relevant entity must be represented in the context's tracked entries for this accessor path. Owned child mappings and tracking behavior connect those layers, but a persistence-backed test is needed to establish the executed graph. A domain-only child event assertion remains valuable without claiming more.

The runtime accessor materializes the selected event list before clearing. That makes the dispatcher's local list available after the entity collections are cleared. Do not confuse that local copy with a durable queue. A process failure can still lose in-memory work that has not reached the relevant persistence boundary.

## Notification resolution is optional per domain event

For every collected event, DomainEventsDispatcher constructs the corresponding generic notification interface type and asks the lifetime scope to resolve an optional notification using the domain event and its identity. When a notification is found, it is added to a notification list. When none is found, that event does not contribute a notification through this path.

The dispatcher then clears collected domain events from their tracked entities and publishes each domain event through IMediator. After those publications, it serializes the resolved notifications and adds OutboxMessage objects. Thus every collected domain event is considered for in-process publication, while an outbox notification depends on an optional registered mapping. Do not claim one outbox row per domain event without checking notification registration.

The notification type name is obtained through a mapper, and serialization uses a configured contract resolver. Those are additional compatibility boundaries. A renamed CLR type or changed payload shape can affect stored messages and later deserialization. The course does not redesign that format; it asks you to identify the contract before proposing a change.

## Clearing occurs before publication and save

The visible order is collect, resolve notifications, clear entity collections, publish domain events, create outbox messages. UnitOfWork then calls SaveChanges after dispatch returns. If in-process publication throws, later notification creation and SaveChanges may not be reached on that path. The original entity event collections have already been cleared by the dispatcher.

This sequence means a simplistic retry on the same in-memory object requires careful analysis. The object may no longer hold the original events even though save did not complete. A fresh command execution with a new scope can behave differently from calling CommitAsync again on the same context. Do not describe both as the same retry without tracing state and lifetime.

These are source-order observations, not an executed proof of message loss or committed inconsistency. A meaningful experiment would inject failure at a named point, inspect the owned context and database state, and distinguish attempted effects from durable effects. The proposed capstone in chapter 20 uses this evidence discipline.

## Outbox addition participates in the context

OutboxAccessor.Add adds a message to the MeetingsContext OutboxMessages set. Its Save method returns a completed task and comments that saving is handled through EF change tracking during SaveChanges. This supports a concrete explanation of the intended storage path: adding a message object is not itself a separate committed database write in this accessor.

A persistence test can verify that a successful command stores its intended state and corresponding outbox row under the actual unit-of-work path. A failure test can investigate what remains after a controlled save failure. The result must be described according to the provider and transaction boundary actually executed; the source alone does not establish every cross-resource atomicity claim.

External calls made by an in-process event handler require separate inspection. The presence of an outbox does not automatically route every side effect through it. A review should list which handlers merely update tracked state, which schedule internal commands, and which can reach external services. That inventory is more useful than declaring the entire module transactional by architecture label.

## Later processing publishes before marking processed

ProcessOutboxCommandHandler queries rows whose ProcessedDate is null, ordered by OccurredOn. It resolves each stored notification type, deserializes the payload, publishes the notification through IMediator with the handler's cancellation token, and only then executes an update setting ProcessedDate by message identity. The update uses the current wall-clock time.

The order creates a clear partial-failure window for study: publication may complete before the processed-date update completes. If the marker remains null, a later query can select the row again. This source order does not establish that every consumer receives duplicates, but it does mean the inspected method alone is insufficient evidence for an unconditional exactly-once delivery guarantee.

A consumer or notification handler may implement deduplication, or a broader transaction arrangement may affect local work. Those components must be inspected and tested separately. Do not assume either perfect deduplication or unavoidable duplicate external effects without following the actual recipient path.

## Ordering has limits here too

Rows are ordered by OccurredOn, but the selected query shows no explicit secondary key. Equal timestamps require a separate ordering policy if consumers depend on a deterministic sequence. Also, ordering a batch read does not by itself establish that multiple concurrent processors cannot overlap. The selected method does not show a claim or lease step before publication.

A concurrency experiment would need an owned database, controlled processors, observable message identities, and an explicit expected contract. It should not be improvised against a running shared environment. In this course, the concurrency question remains a design and evidence exercise. The point is to identify what the source does and which stronger guarantee would require another mechanism or test.

For ordinary single-processor tests, use distinct occurrence times and verify each message's identity and processed marker. That isolates the basic ordering and marking path before introducing concurrency. A test suite becomes easier to diagnose when it separates deterministic local behavior from contested scheduling scenarios.

## Cancellation is not a universal rollback switch

The processor forwards the token to mediator publication. The selected Dapper query and processed-date update calls do not show token-bearing command definitions. Cancellation can therefore be observed at some stages without proving that every SQL operation is canceled through the same token. A canceled task does not automatically mean no notification handler ran.

Design a cancellation timeline with at least three points: before publication, during recipient work, and after publication before marking. For each point, list attempted recipient effects, stored marker state, and whether replay is possible. Do not assume that cancellation of the caller undoes a completed external action. An idempotent recipient contract, when required, must be explicit about its stable operation identity and duplicate response behavior.

The course does not introduce a new cancellation implementation. This is an analysis exercise that prepares the learner to review a future change responsibly. It uses actual forwarding statements rather than generic advice that all asynchronous work supports cancellation because a token appears in a signature.

## Design a failure matrix with stable identities

Use a synthetic message identity M1 and a recipient fixture that records attempts separately from committed effects. Define expected observations for deserialization failure, recipient rejection, recipient success followed by marker-update failure, and complete success. Keep the stored notification payload independent from the recipient's observation log so one artifact cannot overwrite the evidence for another stage.

On complete success, the inspected path publishes before setting the marker. On deserialization failure, publication is not reached. On recipient failure, the later update is not reached through normal sequential control. On marker failure after successful publication, the recipient may already have acted while the row remains eligible for later selection. These predictions become stronger only when executed in an owned fixture with explicit failure injection.

A good receipt reports attempt count, effect count, marker value, and replay result separately. A single processed boolean or a single exception cannot summarize the whole experiment. This is the same evidence principle used for aggregate rejection, extended across persistence and asynchronous work.

## Independent practice

Exercise NA18-A, event-to-outbox trace, is worth eight points. Draw the runtime accessor, optional notification resolution, clearing, in-process publication, message addition, and SaveChanges sequence. Explain why recursive unit-test event collection does not prove runtime tracking or one notification per event.

Exercise NA18-B, partial-failure matrix, is worth six points. Predict observations for failure before publication, during recipient work, and during processed marking. Separate source-derived possibilities from executed guarantees and identify what would be needed to support an exactly-once claim.

Exercise NA18-C, retry and cancellation design, is worth six points. Compare retrying the same context with a fresh command scope, identify token forwarding actually present, and propose an identity-specific recipient test without contacting external services. Review [the final solutions](SOLUTIONS-13-20.md) after completing the matrix.


[Complete course route](README.md) | [Separate solutions and assessment](SOLUTIONS-13-20.md)
