# 13. Command orchestration and the actual commit boundary

The first twelve chapters deliberately stopped before claiming persistence. This chapter follows the application path far enough to explain where commit work is requested. Read [MeetingsModule](../../../modular-monolith-with-ddd/src/Modules/Meetings/Infrastructure/MeetingsModule.cs), [CommandsExecutor](../../../modular-monolith-with-ddd/src/Modules/Meetings/Infrastructure/Configuration/Processing/CommandsExecutor.cs), [ProcessingModule](../../../modular-monolith-with-ddd/src/Modules/Meetings/Infrastructure/Configuration/Processing/ProcessingModule.cs), and [UnitOfWork](../../../modular-monolith-with-ddd/src/BuildingBlocks/Infrastructure/UnitOfWork.cs). These are source observations, not a report that a database command was executed during course authoring.

The goal is to replace a vague handler saves everything explanation with a trace that names object lifetime, handler work, decorators, domain event dispatch, and SaveChanges. Keep the trace precise enough that a failure can be assigned to one boundary without assuming that every preceding action is automatically undone.

## Enter through the module contract

MeetingsModule exposes command methods with and without a result. Both delegate to CommandsExecutor. The executor begins a lifetime scope, resolves IMediator, sends the command, awaits completion, and disposes the scope. Query execution also creates a scope and sends through the mediator, but its implementation appears directly in MeetingsModule rather than the command helper.

The scope is an object-lifetime boundary in the visible source. It is not by itself a database transaction declaration. To understand persistence, follow the registered handlers and decorators. ProcessingModule registers unit-of-work and validation decorators for command handler interfaces and logging decorators for mediator request handler interfaces. Their registration is evidence that these concerns are composed into the module; determining an exact resolved wrapper order for a particular command deserves an explicit composition test if that ordering is the subject of your claim.

Do not reconstruct decorator order solely from an attractive diagram or general memory of a dependency-injection library. You can still reason safely about each decorator's local contract: the unit-of-work decorator awaits its decorated handler before committing, and the validation decorator gathers validation errors before invoking its decorated handler. Those statements follow their bodies without requiring an unexecuted global-resolution claim.

## Handler work is orchestration around the aggregate

[AddMeetingAttendeeCommandHandler](../../../modular-monolith-with-ddd/src/Modules/Meetings/Application/Meetings/AddMeetingAttendee/AddMeetingAttendeeCommandHandler.cs) loads the meeting by the request's meeting identity. It obtains the group identity from that loaded meeting, loads the group, and calls AddAttendee with the current member context and requested guests. This is a useful separation of identities: the meeting comes from the command, the related group comes from the aggregate, and the attendee comes from execution context.

The handler does not call an explicit update method after mutating the loaded meeting. That absence is not sufficient to conclude the change is discarded. The concrete repository uses the context's meeting set to find entities, and the unit-of-work path later calls SaveChanges. To establish a successful round trip, however, a persistence test must still load the result through an appropriate fresh context or query; a source trace explains the intended mechanism, not the observed stored result.

The role handler follows the same meeting-to-group lookup pattern. It supplies the setting member from context and the target member from the command. A test with identical actor and target can hide argument substitution. Use distinct identities and verify both the loaded group relationship and the aggregate call's semantic outcome. A repository substitute is useful for orchestration, but it does not exercise concrete tracking or SQL behavior.

## Validation and domain rules reject at different boundaries

ValidationCommandHandlerDecorator receives a list of validators, validates the command with each, flattens nonnull errors, and raises InvalidCommandException when errors exist. Otherwise it awaits the decorated handler. This describes the decorator's behavior; it does not prove a particular command has any registered validators. A list can be empty, and a command still reaches domain rules later.

Domain rules throw BusinessRuleValidationException from the domain's CheckRule path. The two exception families carry different information and are translated differently by the API configuration examined in chapter 16. A test should assert the intended boundary rather than accepting any exception as proof that validation worked. An invalid fixture can fail during repository access or object construction before the rule you intended to test.

For a proposed title rule, decide which domain boundary owns the invariant and whether outer command validation adds earlier feedback. Duplicating feedback does not eliminate the need for direct aggregate protection when that is the stated requirement. It also creates consistency work: trimming, length units, and null policy should not diverge between validators and the domain representation.

## The unit-of-work decorator commits after handler completion

The no-result decorator awaits the decorated Handle call. For an InternalCommandBase command, it then looks up the corresponding internal-command record and marks its ProcessedDate when found. Finally it calls CommitAsync. The result-returning decorator follows the same shape, captures the handler's result, marks an internal command when applicable, commits, and returns the result afterward.

If the decorated handler throws before returning, normal sequential control does not reach the later commit call in that decorator. That is a useful local guarantee. It does not prove that the handler performed no external side effect before throwing, nor does it restore mutations in an object held by another reference. A complete failure analysis must inventory effects according to their actual owner and lifetime.

The result-returning order also matters. A handler can calculate a new meeting identity before commit, but the decorator returns it only after its commit call completes. A controller that ignores the returned identity still waits for command completion. Do not confuse an identity created in memory with a durable row or a response body containing that identity.

## UnitOfWork dispatches before saving

UnitOfWork.CommitAsync first awaits domain event dispatch and then calls the context's SaveChangesAsync with the supplied cancellation token. This is more specific than saying events happen after commit. The dispatcher may publish in-process domain events and add outbox messages before SaveChanges runs. Chapter 18 follows that path in detail.

The method does not show an explicit begin-transaction statement around every possible external operation. Avoid promising atomicity across email, broker delivery, or arbitrary handlers based on the class name. The context's eventual save and the outbox mechanism have particular responsibilities, but external effects require their own implementation and failure analysis.

A failure before SaveChanges can leave in-memory event collections already cleared or other in-process work attempted, depending on the dispatch path. A failure during SaveChanges can occur after dispatch was invoked. These are source-order observations that motivate tests; they do not establish exactly what a particular database provider committed under an unexecuted failure. Name the failure injection point in every proposed experiment.

## Trace cancellation tokens honestly

The unit-of-work decorator passes its token to the decorated handler and to CommitAsync. UnitOfWork passes the token to SaveChangesAsync, while DispatchEventsAsync in the inspected interface call is invoked without that token argument. Individual handlers may accept a token without passing it to every repository method, especially when those repository interfaces do not expose one.

Therefore, a method signature containing CancellationToken is not evidence that every nested operation is cancelable through that token. A proposed cancellation test should identify where cancellation is observed and what effects may have preceded it. Do not infer rollback from OperationCanceledException alone. The same state-and-event snapshot discipline used for business-rule rejection applies, with an additional integration boundary for persistence.

This does not mean every missing token forwarding is automatically a defect to repair during the course. It is a traceable behavior and a design question. Prioritize changes according to the intended command contract and measured operational need, preserving the task's scope.

## Build a command evidence ledger

For each command, record entry method, scope creation, handler type, identity sources, repository reads, aggregate call, potential direct external calls, decorator commit point, and returned result. Mark each line as source-reviewed, substitute-tested, database-tested, or request-tested. This makes evidence accumulation visible without claiming one test traversed every layer.

For attendee addition, a minimal ledger begins with the request meeting identity and guests, adds context member identity, follows the loaded meeting's group identity, and ends at AddAttendee. A larger module test can add decorator and persistence evidence. An HTTP test adds binding and permission behavior. The ledger prevents those different tests from being summarized inaccurately as the same kind of integration test.

Use this ledger when debugging an apparent no-update issue. First establish whether the handler was reached, whether the aggregate changed, whether the decorator reached CommitAsync, whether dispatch completed, whether SaveChanges completed, and whether the read query projects the intended row. Jumping straight from a stale UI to repository failure skips several plausible boundaries.

## Independent practice

Exercise NA13-A, orchestration trace, is worth eight points. Map attendee addition and role demotion from command identity through context identity, meeting repository, group repository, and aggregate call. Give actor and target distinct identities and identify the earliest possible missing-object failure without inventing a custom not-found result.

Exercise NA13-B, failure boundaries, is worth six points. Predict which later calls are skipped when validation, the decorated handler, domain dispatch, or SaveChanges throws. Distinguish skipped work from restored state and name one external effect that would need separate evidence before an atomicity claim.

Exercise NA13-C, result and cancellation contract, is worth six points. Explain why a handler-created identity is not yet a durable result, where the result-returning decorator commits, and which token propagation claims the inspected source supports. Compare your answers with [the final solution guide](SOLUTIONS-13-20.md).


[Complete course route](README.md) | [Separate solutions and assessment](SOLUTIONS-13-20.md)
