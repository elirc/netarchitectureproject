# 16. HTTP contracts, identity sources, and error translation

A controller method is an important boundary, but invoking it directly is not the same as sending an HTTP request. Read [MeetingsController](../../../modular-monolith-with-ddd/src/API/CompanyName.MyMeetings.API/Modules/Meetings/Meetings/MeetingsController.cs), [MemberContext](../../../modular-monolith-with-ddd/src/Modules/Meetings/Application/Members/MemberContext.cs), [ExecutionContextAccessor](../../../modular-monolith-with-ddd/src/API/CompanyName.MyMeetings.API/Configuration/ExecutionContext/ExecutionContextAccessor.cs), and [Startup](../../../modular-monolith-with-ddd/src/API/CompanyName.MyMeetings.API/Startup.cs). The chapter describes visible source contracts and proposes layered tests. It does not start a server or send authenticated requests.

Your objective is to trace route values, body values, current-user identity, module calls, return values, and exception translation without merging them into a generic endpoint works claim. The distinctions are especially important for a course that already has strong domain examples but has not executed the full web application.

## Map routes to actions before reading payloads

The controller has the base route api/meetings/meetings. Its actions include a list GET, a details GET by meeting identity, creation POST, main-attribute PUT, attendee GET and POST, and separate role, waitlist, and cancellation routes. Each action carries a named permission attribute and declares a successful response type or status.

CreateNewMeeting constructs a CreateMeetingCommand from the body request's fields, awaits module execution, and returns Ok without a response object. The application command can produce a meeting identity, but this controller does not return that identity in its success body. Do not document a 201 response, Location header, or newly created DTO simply because those would be familiar REST choices. They are possible proposed changes, not this action's visible return contract.

EditMeeting takes the meeting identity from the route and the remaining candidate fields from the body. Its command argument order includes distinct start and end dates, location components, limits, RSVP bounds, and fee. This is another mapping boundary where sentinels can detect transposed values. A correct handler cannot repair a controller that already copied the wrong field into the command.

## Current-user identity is not always a request field

AddMeetingAttendee constructs a command from the route meeting identity and body guest count. The corresponding handler uses IMemberContext.MemberId for the attendee identity. MemberContext wraps IExecutionContextAccessor.UserId in a MemberId. The execution context reads the sub claim from the current HTTP user and parses it as a Guid, raising an application exception when the expected user context is unavailable.

This chain distinguishes adding the authenticated member from adding an arbitrary member identity supplied in the body. A controller test can verify the command fields, but a handler test verifies use of member context. A request-level test is needed to establish how the authenticated principal is populated and how missing or malformed identity is handled by the configured pipeline.

Role changes contain both an actor and target. The target attendee identity comes from the request and enters the command, while the handler supplies the setting actor from member context. Use different synthetic identities in tests. If they are equal, a mistake substituting target for actor can remain invisible even though the domain authorization rule is otherwise correct.

## Permission metadata is part of a larger pipeline

HasPermissionAttribute derives from AuthorizeAttribute with the named permission policy and stores the requested permission name. Startup registers that policy with a permission requirement and a Bearer authentication scheme, and registers an authorization handler. These source facts establish intended composition, not a successful permission enforcement test.

The visible pipeline invokes identity-service setup and authorization, while a standalone UseAuthentication line is commented. Do not infer from that one comment that authentication is globally absent: identity-service extension behavior and the configured scheme require their own inspection. Equally, do not claim complete authorization merely because attributes are present. A hosted test should distinguish unauthenticated, authenticated without permission, and authorized requests using an owned test configuration.

A direct C# call to a controller action bypasses routing, binding, authorization middleware, and exception middleware. It can still be a valuable mapping test. Its report should say controller action invocation, not HTTP acceptance. Naming the boundary accurately prevents an apparently green test from becoming misleading security or transport evidence.

## Return declarations and actual returns serve different roles

ProducesResponseType documents expected response metadata. The action's executed return statement supplies the actual IActionResult on its normal path. Domain exceptions interrupt that path and are handled outside the action if suitable middleware is active. A declared 200 response is not proof that every invalid request returns 200, nor is it a complete list of every runtime error response.

For creation and mutation actions, the inspected normal path returns empty Ok results after awaiting commands. Query actions return Ok with DTOs or lists obtained from the module. A module substitute returning a known DTO can verify the action wraps that object, but it cannot prove the query's SQL aliases, missing-row behavior, or persistence state.

An absent meeting is a useful example. The details handler uses a single-result query and the action contains no explicit NotFound branch. To document the final HTTP behavior, follow the actual exception and middleware configuration and execute a hosted request in the relevant environment. Do not fabricate a 404 contract from common conventions.

## Error translation has an environment boundary

[BusinessRuleValidationExceptionProblemDetails](../../../modular-monolith-with-ddd/src/API/CompanyName.MyMeetings.API/Configuration/Validation/BusinessRuleValidationExceptionProblemDetails.cs) sets a conflict status, a business-rule title, the exception message as detail, and a type URI. [InvalidCommandProblemDetails](../../../modular-monolith-with-ddd/src/API/CompanyName.MyMeetings.API/Configuration/Validation/InvalidCommandProblemDetails.cs) sets a bad-request status and exposes the validation error list. Startup registers mappings for both exception types.

However, the visible UseProblemDetails call is inside the development-environment branch. The nondevelopment branch shown invokes HSTS instead. Therefore, the source supports a configured development error-mapping path, not an unconditional claim that the same serialized response appears in every environment. A production behavior statement requires reviewing the complete hosting configuration and executing that environment's path.

A focused test can instantiate each problem-details class and inspect its values without starting a server. That verifies the mapping object, not middleware activation or response serialization. A hosted development test adds those boundaries. Keep the two receipts separate so a constructor test is not presented as proof of an actual HTTP 409 response.

## Binding details deserve exact reading

Some action parameters explicitly use FromRoute or FromBody, while others rely on framework binding conventions under ApiController. Do not invent explicit annotations in a diagram that are absent from the method. A controller mapping worksheet should copy the actual parameter sources and identify convention-dependent behavior for request-level verification.

For example, removal accepts route identities and a request object containing the reason. Role endpoints accept a target attendee request. Their source signatures matter when building an HTTP test payload. A direct action invocation can supply those objects regardless of how a real request would bind, so it cannot detect a binding mismatch on its own.

Use synthetic payloads with distinguishable values. Include an invalid interval only when testing the domain-error path; otherwise keep all values valid to isolate binding or mapping. A malformed GUID route and a valid GUID for a nonexistent meeting are different cases, potentially failing at different stages. Do not collapse both into invalid meeting identifier without specifying the boundary.

## Design a layered transport suite

Start with pure action tests using a module substitute to capture command and query objects. Verify route/body mapping, target identity, and the normal IActionResult. Next test context identity in the handler with a controlled IMemberContext. Then design hosted tests for route selection, JSON binding, permission outcomes, and the development error translation path.

For a proposed title rule, include a body whose title is invalid while all other values are valid. The expected domain rule, command-validation error, or binding error depends on where the rule is implemented. State that decision in the specification. A test that accepts either 400 or 409 without explaining the policy can hide a change in ownership boundary.

A final persistence-backed request test can create or change a meeting and query the independent read model. That is a larger fixture with more prerequisites and effects. It should not be run merely to validate a Markdown command or a local source explanation. The course's current verification stops at bounded disposable domain and rule labs plus source and link checks.

## Keep evidence safe and useful

Record method, route template, synthetic request shape, expected status, and observation boundary. Do not include live bearer tokens, connection strings, or real member data in a learning receipt. An authorization test can describe its fixture role and permission set without disclosing credentials. Source paths and synthetic identities are enough to make the design reviewable.

When debugging, ask whether the action was selected, whether binding succeeded, whether authorization allowed entry, whether the module completed, and whether middleware translated an exception. Each answer narrows the next experiment. A generic request failed message skips the useful structure already present in the source.

A strong endpoint explanation can be candid about unexecuted layers while still being actionable. It tells the learner which exact test would add the missing evidence and which claim should remain provisional until then. That is more reliable than copying a familiar API convention onto a repository that uses a different normal response or environment branch.

## Independent practice

Exercise NA16-A, request map, is worth eight points. Trace creation, editing, attendee addition, and role demotion from route/body/context values to command arguments and normal results. Explain why creation's returned application identity is not automatically in the HTTP response.

Exercise NA16-B, error evidence, is worth six points. Separate problem-details constructor values, registered mappings, development middleware activation, and observed HTTP output. Design one test at each useful boundary and state which have not been executed in this course.

Exercise NA16-C, identity and authorization, is worth six points. Build an actor/target fixture and a three-outcome permission test plan. Explain why direct controller invocation and a commented middleware line each provide insufficient evidence for a broad authorization conclusion. Review [the final solutions](SOLUTIONS-13-20.md) after recording your predictions.


[Complete course route](README.md) | [Separate solutions and assessment](SOLUTIONS-13-20.md)
