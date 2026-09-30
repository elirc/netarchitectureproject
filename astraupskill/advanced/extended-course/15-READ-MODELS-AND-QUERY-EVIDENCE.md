# 15. Read models, SQL views, and independent query evidence

The aggregate is not the only representation of a meeting. Read [GetMeetingDetailsQueryHandler](../../../modular-monolith-with-ddd/src/Modules/Meetings/Application/Meetings/GetMeetingDetails/GetMeetingDetailsQueryHandler.cs), [GetMeetingAttendeesQueryHandler](../../../modular-monolith-with-ddd/src/Modules/Meetings/Application/Meetings/GetMeetingAttendees/GetMeetingAttendeesQueryHandler.cs), [the details view](../../../modular-monolith-with-ddd/src/Database/CompanyName.MyMeetings.Database/Structure/meetings/Views/v_MeetingDetails.sql), and [the attendee view](../../../modular-monolith-with-ddd/src/Database/CompanyName.MyMeetings.Database/Structure/meetings/Views/v_MeetingAttendees.sql). These files let you follow a value from storage into a DTO without assuming the query invokes domain predicates.

This chapter's evidence is source review and designed test cases. No SQL query is executed as part of the course's bounded labs. A proposed database test must use the owned integration environment described in chapter 17, because the repository's integration setup clears tables.

## Follow the details projection field by field

The details handler obtains an open connection from ISqlConnectionFactory and calls QuerySingleAsync for MeetingDetailsDto. Its SQL selects explicitly aliased columns from v_MeetingDetails and filters by a parameter named MeetingId. The parameter object supplies query.MeetingId. The query does not load Meeting and then call getters; it projects database values directly.

The view itself selects meeting fields from the Meetings table, including title, term boundaries, description, location components, limits, RSVP bounds, and event fee. The handler aliases each selected column to the corresponding DTO property name using nameof. This helps keep aliases tied to the compiled property name, but it does not prove the selected source column is semantically correct. A start column aliased as an end property can still compile.

Use the sentinel method from chapter 02 at this new boundary. Give term start and end different values, RSVP bounds different values again, and each location component distinct text. Assert the returned DTO against independently specified expected values. A round-trip assertion that compares only nonnull DTO existence would miss many transpositions.

## A single-row query has its own missing-result contract

The handler selects QuerySingleAsync rather than a nullable-result method and shows no custom missing-meeting branch. The controller later returns Ok with the result when the query completes. Do not infer a NotFound response from the fact that the route contains a meeting identity. Missing-row behavior must be traced through the query library and exception middleware, then verified at the intended boundary before documenting an endpoint contract.

A proposed query test should include one existing synthetic identity and one absent identity. Record whether the query returns, throws, or is translated by an outer layer. Keep the query-level result distinct from the HTTP result. A test that mocks the module to return null only proves controller behavior for that mock, not what the real details query does when storage has no row.

Similarly, a duplicate-row scenario concerns the view's cardinality and selected query method, not an aggregate invariant in memory. If a future join can multiply rows, review whether the handler still has the intended single-result contract. Query shape changes can introduce failures even when the underlying Meeting table retains a unique key.

## The attendee projection does not reuse IsActive

The attendee handler selects first name, last name, role code, decision date, guests number, and attendee identity from v_MeetingAttendees, filtered by meeting identity. The view joins MeetingAttendees to Members on attendee identity. In the inspected view there is no predicate filtering DecisionChanged or IsRemoved. The handler adds no such predicate either.

Therefore, the selected query source does not establish that the returned list contains only the aggregate's active attendees. It can project historical rows present in the joined tables. This is a concrete reason not to equate its list Count with GetAllActiveAttendeesWithGuestsNumber. The latter filters active children and sums member-plus-guests places; the query returns one DTO per matching joined row.

The inner join introduces another distinction. A stored attendee row without a matching member row would not appear in this view. That does not mean the attendee was absent from storage or the aggregate's collection. A controlled query fixture should include the relevant member rows, and a data-integrity investigation should distinguish missing join partners from domain deletion.

## Work a projection-versus-domain example

Suppose storage contains a creator host, an active attendee with two guests, and a historical removed attendee with zero guests, each with a matching member row. The selected attendee view projects all three rows because it has no shown active filter. The aggregate's occupied-place calculation excludes the removed record and counts one plus three, totaling four active places.

The projected list has three rows, but neither three nor four can be called the number of current named attendees without qualification. Current named active attendees would be two under the domain predicate in this example. Historical rows, current named people, and occupied places are separate measures. A UI label should identify which measure it presents and a query should implement that chosen contract explicitly.

A proposed current-attendee endpoint might add filters matching a specified active policy. Before implementing, reconcile the domain's differing active predicates and define whether removed and changed-decision history remains accessible elsewhere. Simply adding a WHERE clause can alter reporting and audit behavior. Treat it as a product-visible query change, not a harmless cleanup inferred from the endpoint name.

## Ordering is not guaranteed by a convenient fixture

The attendee handler's selected SQL contains no ORDER BY. A test that observes creator first and later attendee second in one database run should not promote that observation into a stable ordering contract. If consumers need role priority, name order, or decision chronology, define it and implement an explicit ordering expression with a tie policy.

For unordered results, compare a multiset or a stable test projection keyed by the intended record identity. Be careful with historical duplicates: attendee identity alone can collapse multiple rows. Include decision date or another explicit occurrence discriminator when appropriate, and preserve duplicate cardinality. A set comparison that drops duplicates can let a duplicated query row pass unnoticed.

If you choose to sort expected and actual rows in a test, explain that the sort normalizes an unordered contract rather than asserting the query produces that order. The distinction keeps a future reader from mistaking test convenience for application behavior.

## Parameter binding and projection are separate checks

The meeting identity is supplied through a parameter object rather than concatenated into the selected SQL expression. Source review can establish that shape. A mapping test can capture the intended identity at the query boundary, while a database test can show that only the matching fixture rows return. Do not use production identifiers or connection details in teaching output when synthetic values suffice.

DTO properties also have types and nullability that matter. MeetingDetailsDto represents attendee limit as nullable integer, RSVP dates as nullable DateTime, and event fee value as nullable decimal. Guests limit is nonnullable integer. A missing selected column might leave a default value that looks plausible, so positive nondefault sentinels are essential. A DTO with all zeros and nulls can pass a weak test even when little was mapped.

The query methods accept cancellation tokens, but the inspected Dapper calls do not show a token-bearing command definition. Do not claim that the handler token is forwarded to the SQL operation merely because it is present in the method signature. As in chapter 13, cancellation behavior needs its own exact trace and execution evidence if it becomes a requirement.

## Query helpers are another contract to inspect

[MeetingsQueryHelper](../../../modular-monolith-with-ddd/src/Modules/Meetings/Application/Meetings/MeetingsQueryHelper.cs) reads a smaller MeetingDto from v_Meetings using a primitive Id derived from MeetingId.Value. It selects title, description, address, city, postal code, and term dates. It does not automatically share every column or behavior of the details query.

A caller using that helper cannot assume it has the full details DTO. If a future email or integration notification needs location name or fee, inspect whether the helper provides it and whether adding it changes a shared contract. Reusing a helper is useful only when its projection actually matches the caller's needs. Otherwise a missing field may be papered over with an incorrect default.

Do not infer that all views refresh asynchronously because the repository uses read models. The inspected definitions here are SQL views over tables. Any claim about asynchronous projection lag would require a different source path and evidence. Architectural labels such as CQRS do not by themselves tell you the consistency mechanism of a particular query.

## Design a discriminating query suite

A small suite can verify a details row with distinct values, nullable alternatives, an absent identity, attendee history filtering as currently implemented, join behavior, and unordered duplicate-preserving comparison. Each case should name its contract. A proposed changed filter belongs in a specification test separate from current characterization.

Avoid running the entire application to answer a pure alias question when source inspection and a focused query fixture suffice. Conversely, a source review cannot demonstrate that deployed database objects match the checked-in view definitions. A useful integration receipt identifies the schema version or fixture setup and the query path executed, without exposing credentials.

When a query disagrees with the aggregate, first ask whether they intentionally answer different questions. If not, identify the earliest differing filter, join, count, or mapping. Changing the aggregate to make a historical reporting query look current can solve the wrong problem. The right repair follows the explicitly chosen read contract.

## Independent practice

Exercise NA15-A, projection ledger, is worth eight points. Map details columns to DTO properties with distinct sentinels and include a null-limit and undefined-fee case. Explain one alias error that nameof alone would not prevent.

Exercise NA15-B, attendee measures, is worth six points. Compute projected rows, current named active attendees, and occupied places for the three-record example. Explain the inner join and missing active filter, then propose a clearly labeled current-attendee query contract.

Exercise NA15-C, ordering and missing rows, is worth six points. Design an unordered duplicate-preserving assertion and an absent-identity investigation. Separate query behavior from HTTP translation and avoid claiming cancellation propagation not present in the selected call. Use [the final solutions](SOLUTIONS-13-20.md) for review.


[Complete course route](README.md) | [Separate solutions and assessment](SOLUTIONS-13-20.md)
