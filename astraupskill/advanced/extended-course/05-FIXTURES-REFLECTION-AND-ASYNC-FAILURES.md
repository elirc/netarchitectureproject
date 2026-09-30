# 05 - Keep test infrastructure failures separate from business failures

The interval handler regressions use reflection because the handler types are internal. That arrangement can exercise real mapping, but it introduces failure stages that must not be confused with domain rejection. This chapter examines [MeetingTermCommandHandlerTests](../../../modular-monolith-with-ddd/src/Modules/Meetings/Tests/UnitTests/Meetings/MeetingTermCommandHandlerTests.cs), [MeetingTestsBase](../../../modular-monolith-with-ddd/src/Modules/Meetings/Tests/UnitTests/Meetings/MeetingTestsBase.cs), and [TestBase](../../../modular-monolith-with-ddd/src/Modules/Meetings/Tests/UnitTests/SeedWork/TestBase.cs). The goal is a fixture and invocation path whose failures are diagnostic.

## A valid fixture isolates the intended rule

The handler fixture creates a new member id, proposes a group, accepts the proposal, creates the group, and supplies a future expiration date. It substitutes group and meeting repositories and a member context. The group repository returns the constructed group; the context returns the chosen member. These steps make creation viable before the term mapping is tested.

If the group is unpaid or expired, a valid interval can still be rejected by another rule. If host membership is inconsistent, the same problem occurs. A negative interval test that asserts any exception might pass because of those unrelated preconditions. A successful mapping test helps detect fixture invalidity because it requires the entire arranged path to reach the aggregate observation.

The fixture should use distinct identities for roles whose distinction matters. When every Guid is the same, an accidental swap between group id, meeting id, creator id, and modifier id can become invisible. At the same time, do not create arbitrary unrelated ids where the domain requires membership. A good fixture is intentionally valid, not simply populated with random values.

## Reflection has a staged contract

The helper obtains the application assembly through typeof(CreateMeetingCommand).Assembly and resolves a fully qualified handler name. It then constructs the handler with instance, public, and nonpublic binding flags, using the supplied constructor arguments. It locates Handle, invokes it with the command and CancellationToken.None, casts the result to the expected task type, and awaits it.

Each stage has its own failure meaning. A missing type indicates assembly or name resolution trouble. Constructor binding can fail because the dependency types, order, or visibility do not match. A missing method indicates an invocation contract mismatch. A task cast can fail because the helper assumes the wrong return shape. None of those facts establishes that the interval rule ran.

The create constructor receives member context, meeting repository, and group repository in that order. The change constructor receives member context and meeting repository. The handler types are internal, but constructor visibility differs in the source. Including both public and nonpublic instance flags is therefore relevant to the helper's ability to create both types. Do not simplify the flags without checking the actual declarations.

## Async exceptions need an awaited observation

Create Handle returns Task<Guid>; change Handle returns Task. An async method can return a task that later faults. A helper that invokes Handle but never awaits the returned task can finish the test before the business exception is observed. The test might pass its immediate assertions while the operation has not reached the expected point or its failure remains unobserved.

MethodInfo.Invoke can wrap an exception thrown synchronously during invocation in TargetInvocationException. A failure represented by the returned task is observed when awaiting that task. Diagnose the stage rather than flattening every exception into a business rejection. The existing helper performs the correct task cast for its generic overload and awaits the result; proposed changes should preserve that behavior.

A useful diagnostic trace labels resolve type, bind constructor, invoke method, receive task, await task, and assert domain result. Record the last completed stage when a test fails. That makes a wrong type name visibly different from a correct handler rejecting an equal interval. It also helps avoid an overbroad catch that converts infrastructure mistakes into the expected exception category.

## Observe the instance the handler actually used

On creation, the test configures AddAsync with a callback that captures the Meeting argument. It then checks that the captured aggregate exists and reads its term. This proves the observed object is the one submitted by the handler. Inspecting a separately constructed fixture meeting would not establish the create mapping, even if that fixture object had the expected dates.

On change, the repository substitute returns a known meeting instance. Capture its baseline before invoking the handler and inspect the same instance afterward. A substitute that returns a new object for each call can make before-and-after comparisons meaningless if the test does not retain the actual returned object. Identity of the observation target is part of the fixture contract.

Private-field reflection into _term is a narrow observation mechanism. If that field is renamed or moved, the test should fail as an observation setup problem. Do not change production visibility merely to preserve a brittle helper without considering alternatives. A focused helper with a clear missing-field message can be more useful than scattered unchecked reflection calls throughout tests.

## Distinguish interaction assertions from state assertions

DidNotReceive().AddAsync establishes that the substitute did not observe that add call. It does not prove that no read occurred, no other side effect happened, or no outer transaction committed unrelated work. Direct term assertions establish selected in-memory values. Event assertions establish collected domain events. Each assertion has a scope that should appear in the test name or accompanying explanation.

For a rejected change, the existing regression preserves the old start and end. It does not compare every private field or event. A stronger proposed test should capture a broader projection rather than claim the original test already provides that evidence. Conversely, do not dismiss the original regression as useless: it directly protects the term-preservation behavior that motivated it.

When using a substitute, assert only interactions that form part of the contract under study. Requiring an exact number of harmless reads can make a test brittle under a legitimate optimization unless read count itself matters. Requiring no AddAsync for a rejected create is directly relevant because adding an invalid aggregate would violate the decision. Explain why each interaction assertion belongs.

## Shared clocks and cleanup belong to fixture design

The domain SystemClock has static mutable custom time, and TestBase resets it during teardown. A test that changes it must reliably execute cleanup even after assertion failure. A standalone disposable runner should use a finally block. If tests run concurrently and share this clock, one test's fixed time can affect another; determinism requires isolation or coordination in addition to a fixed value.

The existing handler fixture uses DateTime.UtcNow for several future values, while another shared meeting fixture uses DateTime.Now for expiration and UTC expressions for terms. These are source observations to consider when designing new deterministic tests. Do not claim that calling SystemClock.Set automatically overrides every direct DateTime call in the fixture. An abstraction controls only the code that reads it.

A proposed fixture can capture one baseline instant and derive all relative dates from it, while separately setting the domain clock. This reduces accidental drift and makes assertions readable. Keep the scope explicit: changing test date construction is a test refactor, whereas changing production clock semantics is a behavior change requiring separate justification.

## A worked diagnostic table

Suppose the fully qualified create handler name is misspelled. The type-resolution stage fails, and no constructor or domain rule runs. Suppose the repositories are swapped in the constructor array. Binding fails or cannot find a matching signature, again before Handle. Suppose the helper casts the create result to an incompatible task type. Invocation may have started, but the observation adapter fails before it can reliably await the intended result.

Now suppose all reflection stages succeed and awaiting the task yields BusinessRuleValidationException with MeetingTermMustEndAfterStartRule. That is the intended equal-interval rejection. A diagnostic report can now attribute the failure to the domain boundary. The difference is not merely exception text; it is the chain of successfully established stages and the exact BrokenRule object.

For a valid request with a shifted end, every infrastructure stage and rule check can succeed. Only the exact end assertion fails. That example shows why infrastructure success, domain acceptance, and mapping correctness are three separate conclusions. A well-designed test suite includes evidence for all three instead of treating one successful invocation as complete coverage.

## Independent practice

Exercise NA05-A, invocation matrix, is worth eight points. Make rows for wrong assembly, wrong type name, swapped constructor dependencies, missing Handle, wrong task shape, and unawaited task. Identify the failing or unreliable stage and whether the domain rule is known to have run.

Exercise NA05-B, fixture validity, is worth six points. Explain the accepted proposal, group expiration, member context, and repository setup required by the mapping test. Propose a fixture defect that could make an overbroad negative test pass for the wrong reason, and add a positive case that exposes it.

Exercise NA05-C, observation contract, is worth six points. Compare captured AddAsync argument, returned repository instance, private-field reflection, and collected events as observation mechanisms. State one limitation of each and design a clearer missing-field diagnostic without changing production visibility.

Continue with [disposable semantic failure labs](06-DISPOSABLE-LABS-AND-MUTATION-EVIDENCE.md). The [solution guide](SOLUTIONS-01-06.md) separates reflection mechanics from the business outcome so the tests remain informative when code structure changes.
