# Reflection diagnostics and an independent rule extension

The handler regressions use reflection because the application handler types are internal. The create constructor is internal; the change constructor is public inside an internal type. The existing helper obtains the application assembly from `typeof(CreateMeetingCommand).Assembly`, resolves the fully qualified handler name, creates it with public/nonpublic instance flags, calls `Handle`, and awaits the returned task. Keep those mechanics separate from the business assertion you want to prove.

A missing type usually means an assembly/name problem, not a broken interval. A missing constructor can mean the substitute argument order no longer matches the actual signature. The create helper expects member context, meeting repository, then group repository. The change helper expects member context and meeting repository. A task cast must match the handler contract: create returns `Task<Guid>` while change returns `Task`. Failure to await a returned task can let a test finish before the domain exception is observed.

`MethodInfo.Invoke` can wrap a synchronously thrown exception in `TargetInvocationException`; an exception from the returned asynchronous task is observed on awaiting that task. Diagnose the stage rather than asserting every reflection failure is a business rejection. Private-field inspection of `_term` is similarly coupled to the implementation name. If a refactor renames the field, update the test's observation mechanism explicitly instead of changing production visibility purely to satisfy reflection.

Exercise **MA-09**: prepare a diagnostic table for wrong assembly, wrong full type name, swapped constructor dependencies, missing `Handle`, wrong task type, and an unawaited task. For each, state which setup line fails and whether the domain rule ran. This prevents infrastructure errors from being mistaken for successful negative business tests.

## MA-10: Independent proposed title rule

Design a new business rule: after trimming, a meeting title must contain between five and eighty characters inclusive. This is a training proposal, not current production behavior. Decide whether whitespace is only used for validation or whether the stored title is normalized; specify that decision before implementing. Add an `IBusinessRule` implementation and place validation at the aggregate boundary before mutable-field assignments. Ensure creation and change cannot disagree about the rule, and avoid introducing a second hidden definition in a command handler.

Use title lengths four, five, eighty, and eighty-one after trimming. Include whitespace-only input, a valid title surrounded by spaces, and a rejected change that also requests different term, description, location, limits, fee, and modifier. Decide how null input is treated explicitly instead of letting an incidental null-reference exception become your domain contract.

Acceptance requires all fields and domain events to remain unchanged on rejection, using the projection from the preceding chapter. On acceptance, require the intended title policy, exactly the expected change event, and correct preservation of unrelated identity/creation state. Exercise **MA-11**: place the title check intentionally after `_title` and `_term` assignments in a disposable learner copy. Show that your all-fields rejection assertion catches the partial mutation even though the older term-only invalid-interval case might still pass.

Exercise **MA-12**: justify why this rule belongs to the aggregate rather than only a form validator. Then identify one separate concern, such as UI character feedback or HTTP error formatting, that still requires an application-boundary test even after the domain rule is correct.

[Advanced index](README.md)
