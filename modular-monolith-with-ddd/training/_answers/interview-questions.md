# SEALED — answers to `training/interview/QUESTIONS.md`

1. **Boundaries.** NetArchTest assertions run as ordinary tests: `src/Tests/ArchTests/Api/ApiTests.cs` (API folders) and
   `src/Tests/ArchTests/Modules/ModuleTests.cs` (module assemblies). The build fails if Meetings types depend on another module's
   namespace. There are three carve-outs: `INotificationHandler<>`, `*IntegrationEventHandler` and `EventsBusStartup`, because
   subscribers must know the *published* event type. Strong answers mention that the `INotificationHandler<>` carve-out is wider
   than it needs to be.
2. **Command flow.** Controller → `IMeetingsModule.ExecuteCommandAsync` → `CommandsExecutor` opens an Autofac scope → decorators
   (Validation → Logging → UnitOfWork) → handler calls the aggregate (`MeetingGroup.CreateMeeting`) and stages it via the
   repository → the decorator calls `UnitOfWork.CommitAsync`, which dispatches domain events (in-process publish + outbox rows)
   and then `SaveChangesAsync`, in one transaction. The handler never saves.
3. **Trade-off.** Modular monolith: one deploy and one DB to back up, the same design discipline enforced by ArchTests, and
   in-process events that can move to a broker later. The cost is no failure isolation and no independent scaling. Revisit
   when modules need different scaling or release cadence, or when separate teams own them (ADR 0002, `training/navigation/05`).
   Buzzword-only answers fail.
4. **Three hops.** The outbox makes business change + "must tell others" atomic. The inbox makes receipt durable before any
   business effect. The internal command separates "translate the event" from "do the work", so retrying the work doesn't
   reprocess the inbox (`training/navigation/03`, last section).
5. **At-least-once.** The consumer must be idempotent: dedupe on a stable message Id, and/or make the business operation
   idempotent. This repo *intends* to dedupe via the inbox PK, but the Meetings publish handler mints a new Guid per republish
   (`MeetingAttendeeAddedPublishEventNotificationHandler.cs:19`), so duplicates can slip through (FD1).
6. **Scale-out.** `[DisallowConcurrentExecution]` is per scheduler, and the processing `SELECT`s don't claim rows, so both
   instances publish the same messages (FD4). You'd find out with a load test on 2 replicas plus duplicate-count queries on inbox
   business keys. The fix is an atomic claim (`UPDLOCK, READPAST` / `UPDATE ... OUTPUT`) or one worker process.
7. **Event sourcing split.** Benefit: a full audit history of fees and payments, where history matters for money. Cost: two
   persistence models to learn, and projections/snapshots to operate. The `training/_answers/07` answer notes that Payments'
   outbound events go through `IAggregateStore` rather than the Meetings-style handler pattern.
8. **STAR.** Situation: studying a reference architecture. Task: understand its delivery guarantees. Action: traced
   outbox → bus → inbox and noticed the fresh Guid, then checked the inbox table's only constraint. Result: a documented
   duplicate-fee window with a one-line fix and a test plan, stated honestly as unreproduced.
