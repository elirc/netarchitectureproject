# Why? Modular monolith vs. microservices, grounded in this codebase

Format per the apprenticeship brief: Problem → naive approach → where it fails → options A/B/C →
trade-offs → choice → failure modes → how it's tested → how it's monitored → when to revisit.

## Decision 1: one deployable process, five internally-isolated modules

**Problem.** Five business capabilities (Administration/group-proposals, Meetings, Payments,
Registrations, UserAccess) need to evolve somewhat independently and never leak internal types into
each other, but this is a from-scratch reference app, not an org with five separately-owned teams.

**Naive approach.** One big `Controllers`/`Services`/`Models` folder set, everything referencing
everything (this is what most of the archive's "Net-fleet" custom apps actually do — see
`portfolio-audit/projects/batch-01.md`, they're flat `Api/Application/Domain/Infrastructure`
without module partitioning).

**Where it fails.** At small scale it doesn't "fail" — it just accumulates implicit coupling
(a `PaymentsService` calling `MeetingRepository` directly) that nobody notices until someone tries
to change `Meeting` and breaks `Payments` at runtime, discovered late, possibly in production.

**Options.**
- **A — full microservices.** Each module its own deployable, own DB server, network calls between
  them (gRPC/REST), a real message broker (RabbitMQ/Kafka) for events.
- **B — modular monolith with enforced boundaries** (this repo's choice): one process, one DB
  server (but per-module schema), in-process pub/sub standing in for a broker, `ArchTests` enforcing
  the same "you may not import my internals" rule a network boundary would enforce for free.
- **C — flat monolith, no enforced modules** (the naive approach above).

**Trade-offs.**
- A gets you independent deploys, independent scaling, and failure isolation (Payments down doesn't
  take Meetings down) — at the cost of distributed-transaction complexity, network latency, service
  discovery, and a much bigger ops surface (5 deployables × environments, 5 sets of health checks,
  cross-service debugging).
- B gets you almost all of the *design discipline* of A (forced module boundaries, an outbox/inbox
  pattern that would translate directly to a real broker) with none of the *operational* cost — one
  process to deploy, one DB to back up, no network partition between "services" because there isn't
  a network between them. The cost: you don't get real failure isolation (an unhandled exception in
  a Payments handler still runs inside the same process as Meetings; a slow `ProcessOutboxJob` for
  one module still consumes the one process's Quartz thread pool) or independent scaling.
- C is strictly worse than B for the same deploy cost, since it gives up the design discipline for
  free — B costs a bit of ceremony (the module folder structure, the ArchTests, the outbox
  boilerplate per module) but the "you must ask before you can microservice this" property is worth
  more than the ceremony once the codebase is more than a few thousand lines.

**Choice.** B — this repo's whole reason to exist is demonstrating that a monolith doesn't have to
mean "flat and coupled"; the module boundary discipline is meant to make a later split to A
mechanical rather than a rewrite (a module's `Api`/`Application`/`Domain`/`Infrastructure` are
already separate assemblies with a known dependency graph — extracting one to its own service is
"stand up a process boundary around code that already didn't leak," not "figure out where the
seams are for the first time").

**Failure modes of the choice.** A bug or long-running loop in one module's request thread can still
starve the whole process (no per-module process isolation); a schema migration that locks a table
in one module's schema can block a request in the same connection pool serving another module even
though the modules "don't know about each other" logically; and (per `04-outbox-inbox-processing.md`)
the in-process `InMemoryEventBusClient` used here means the "swap in a real broker later" story is
untested — this clone never exercises a broker being down, slow, or partitioned.

**How it's tested.** `src/Tests/ArchTests` (solution-level, `navigation/01-*.md`) plus each
module's own `Tests/ArchTests` (internal layering) — architecture is a **build-time test**, not a
design-review checklist. This is itself a "why" worth remembering for interviews: architecture
tests catch the *class of* violation a code reviewer might miss on a big PR.

**How it's monitored.** Not really, in this reference app — there's Serilog logging
(`OutboxMessageContextEnricher` tags outbox-processing log lines with the message id) but no metrics
on outbox/inbox queue depth or processing lag that would tell you in production "Payments' inbox is
backing up." That's a real gap to name if asked "what would you add before shipping this."

**When to revisit.** When a module needs independent scaling (Payments doing heavy report
generation shouldn't need to scale Meetings' web tier too), independent deploy cadence (a
compliance-driven Payments release schedule vs. a fast-moving Meetings team), or a genuinely
separate failure domain (Payments talking to an external processor should not be able to take down
meeting creation) — at that point, extract that one module first, keep the rest as the monolith,
and replace `InMemoryEventBusClient` with a real broker for just that boundary. This repo's own
`IEventsBus` abstraction is already built for exactly that swap.

## Decision 2: outbox + inbox + internal-command queue instead of a synchronous call or a raw pub/sub

**Problem.** Meetings needs to tell Payments "an attendee with a fee was added" without a
distributed transaction across two schemas, and without losing the message if either side is
momentarily down or slow.

**Naive approach.** Meetings' handler directly calls a `PaymentsService.CreateFeeAsync(...)`
in-process, or publishes straight to an in-memory event with no persistence.

**Where it fails.** Direct call: couples Meetings' request latency and availability to Payments'
(and violates the module boundary outright). Fire-and-forget in-memory publish with no outbox: if
the process crashes after committing the meeting-state change but before the publish call runs, the
event is lost forever — Payments never finds out, no fee ever gets created, and there's no record
that anything is missing.

**Options.** A — synchronous cross-module call (rejected, breaks isolation + boundary). B — outbox
+ polling job + inbox (this repo's choice, traced in `navigation/03-*.md` and `04-*.md`). C —
publish directly to the bus with no outbox, accept at-most-once and occasional silent loss.

**Trade-offs.** B guarantees the message survives a crash (it's in the DB, in the same transaction
as the state change) at the cost of latency (a poll interval, not instant delivery) and the
duplicate-delivery risk documented in `04-outbox-inbox-processing.md`. C is simpler and lower-latency
but can silently drop a fee-creation event with no way to even notice it happened.

**Choice.** B, for the same reason most production systems choose it: silent data loss (a member
never gets billed, and nobody knows) is worse than an occasional duplicate that's at least
detectable and fixable, and is worse than a few seconds of latency.

**Failure modes / testing / monitoring / when to revisit:** covered in full in
`04-outbox-inbox-processing.md` — including the specific duplicate-`MeetingFee` gap this codebase
actually has.
