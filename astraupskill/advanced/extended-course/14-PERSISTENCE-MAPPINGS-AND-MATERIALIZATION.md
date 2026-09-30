# 14. Persistence mappings and materialization without guessing

An aggregate can be correct in memory and still be mapped incorrectly. Read [MeetingEntityTypeConfiguration](../../../modular-monolith-with-ddd/src/Modules/Meetings/Infrastructure/Domain/Meetings/MeetingEntityTypeConfiguration.cs), [MeetingRepository](../../../modular-monolith-with-ddd/src/Modules/Meetings/Infrastructure/Domain/Meetings/MeetingRepository.cs), and [MeetingsContext](../../../modular-monolith-with-ddd/src/Modules/Meetings/Infrastructure/MeetingsContext.cs). This chapter derives a mapping worksheet and a proposed round-trip test plan. No database is created, cleared, migrated, or queried while authoring this course.

The learning goal is to distinguish a domain property, a private backing field, an owned value, a database column, and a read-model alias. Those representations can carry the same business concept while requiring different verification. A test that observes only the original object cannot detect a broken storage mapping.

## Begin with the actual root mapping

The configuration maps Meeting to the Meetings table in the meetings schema and identifies Id as its key. It explicitly maps private fields such as _title to Title, _description to Description, _creatorId to CreatorId, and change and cancellation metadata to their named columns. The aggregate's public surface is therefore not the complete persistence contract.

MeetingsContext applies configurations from its own assembly during model creation. The repository adds through the context's Meetings set and finds by the typed meeting identity. Neither repository method contains SaveChanges; the unit-of-work path from chapter 13 owns that later call. Keep the map and the save boundary separate in a diagram so that a successful AddAsync invocation is not mislabeled as a committed row.

A useful worksheet starts with four columns: domain concept, CLR member or field, mapping expression, and storage column. Add a fifth column for the independent expected value. For title, the worksheet names _title and Title. For term start, it follows the owned _term value and its StartDate property to TermStartDate. This explicit chain exposes swapped or omitted fields.

## Owned values flatten into named columns

The meeting term maps as an owned MeetingTerm through _term, with StartDate and EndDate assigned to TermStartDate and TermEndDate. The RSVP Term maps separately through _rsvpTerm to nullable RSVP columns. Those pairs have different domain policies, even though both use temporal values. Do not merge them into one generic interval assertion that could miss a start/end swap.

Location maps four named properties: name, address, postal code, and city. Event fee maps value and currency. Meeting limits map attendee and guest limits. A sentinel fixture should give each component a distinct value so that a transposed mapping changes the expected projection. Reusing the same text for location name and city makes a swapped mapping invisible.

Nullability matters to meaning. A null attendee limit represents the absence of that total ceiling in the domain predicates, while zero guest limit has its own current semantics. A null fee value participates in the undefined-fee path. A persistence round trip must preserve those distinctions rather than normalizing every missing numeric value to zero in the test expectation.

## Child collections preserve historical occurrences

The attendee collection is mapped as owned children in MeetingAttendees. Its composite key uses AttendeeId, MeetingId, and the decision-date field. The not-attendee collection uses MemberId, MeetingId, and its decision date. The waitlist collection uses MemberId, MeetingId, and SignUpDate. These keys reflect that one member can have multiple historical participation records rather than only one row per member and meeting.

This gives a new reason to keep occurrence identity in chapter 11's snapshots. A dictionary keyed only by member identity can collapse distinct historical records before you compare the round trip. Include the relevant date or a deliberately assigned fixture occurrence label when mapping expected records. If two proposed records share every key component, investigate that as a persistence identity question rather than assuming the database will invent a distinction.

The mapping alone does not establish timestamp precision in the deployed database. A collision analysis must inspect the table definitions and execute the relevant provider behavior before claiming two close instants remain distinct. For ordinary course fixtures, use clearly separated times and avoid making a precision guarantee that was not verified.

## Removal and decision status are separate stored fields

Attendee mapping includes decision-changed status and date, removed status and metadata, guest number, fee-paid flag, owned role, and owned fee. These fields support the distinctions studied in chapters 07 and 10. A removed attendee and a changed-decision attendee are not simply the same stored boolean under different names.

A round-trip worksheet should preserve both flags independently. For example, an accepted removal can set the removed flag while leaving the decision-changed flag false in the current method. If your expected object silently merges them into one active flag, you lose the ability to detect the source's lookup-versus-capacity distinction. A semantic active projection is useful, but retain the underlying fields when the proposed rejection or persistence contract depends on them.

Waitlist mapping similarly distinguishes signed-off and moved-to-attendees flags with separate dates. A queue record can become inactive through either path. The domain's active predicate combines them, while storage preserves why it became inactive. A reporting feature may need that reason, so do not discard it during a generic active-record conversion without a requirement.

## Use a fresh observation boundary for round trips

A proposed persistence test should arrange a valid meeting with distinct values, save it through the intended unit of work, end the relevant tracking scope, and observe it through a fresh context or independently executed read query. Reading the same tracked instance back can return the in-memory object and miss a storage or materialization defect. The exact fixture implementation must respect the repository's existing integration setup.

Compare both positive and null cases. One meeting can carry a defined fee, explicit RSVP bounds, and a finite total limit. Another can exercise the undefined or unbounded forms. Do not combine every unusual condition into one fixture if an earlier domain guard would reject it before persistence. Build valid objects through domain factories and make each mapping assertion independently understandable.

For child collections, create more than one historical occurrence through valid transitions where possible. Verify the intended count and values after a new observation boundary. If a proposed scenario cannot be reached through current public domain behavior, label any reflection-built state as a specialized materialization fixture rather than a normal business workflow.

## Constructors and invariants require compatibility review

Meeting has a private parameterless constructor that initializes child lists, while value objects have their own constructors and factories. A source mapping review tells you which fields and owned types are configured, but it does not prove precisely which construction path a particular ORM version will use for every type. A materialization test supplies that missing runtime evidence.

This is especially relevant to the proposed normalized title extension. Replacing a string field with a value object changes more than command validation. The mapping must represent the new type, existing data may violate the new rule, and read queries still expect a Title column. A design can preserve that column while changing the CLR representation, but it requires an explicit mapping decision and round-trip validation.

Do not assume that adding a constructor guard automatically validates all stored rows or that materialization always bypasses every invariant. Both are broad claims that depend on the actual mapping and runtime path. Instead, create a controlled historical-data compatibility case and record whether loading succeeds, rejects, or requires migration under the proposed design.

## Separate domain identity from primitive storage

MeetingId, MemberId, and MeetingGroupId are typed domain identities. Their use reduces accidental interchange in application code, but storage and query DTOs often expose primitive Guid values. A mapping test should distinguish the type-level contract from the primitive value being preserved. Two typed identifiers can contain different sentinel GUIDs even if their underlying storage type is the same.

Do not use one GUID for meeting, group, creator, and target in a fixture intended to verify mapping. That removes the very distinction typed identities are meant to protect. Use readable fixed labels in the worksheet and deterministic distinct values in a future runnable test. Avoid copying real member identifiers into a teaching artifact when synthetic fixtures suffice.

A query returning a Guid does not recreate the aggregate's behavior or prove its invariants. It is a projection. Chapter 15 follows those read-model paths and shows why an attendee list can have different filtering semantics from the aggregate's occupied-place calculation.

## Diagnose a mapping failure before changing the domain

If the stored term end equals its start, first compare the command values, handler mapping, in-memory term, configured columns, stored row, and query aliases in order. The earliest boundary where the value changes identifies the next useful test. Changing the domain constructor when the in-memory term was already correct would address the wrong layer.

If a child record disappears, inspect key identity, relationship mapping, save completion, and query filtering before assuming the domain failed to append it. If a read DTO has default values, inspect selected columns and aliases as well as storage. A missing projection field is not necessarily a missing stored field.

A good failure report includes the synthetic fixture, expected value, actual value, observation boundary, and source mapping pointer. It does not need a full database dump or sensitive connection details. The goal is to make the mismatch reproducible with the smallest owned dataset that distinguishes the suspected mapping.

## Independent practice

Exercise NA14-A, mapping ledger, is worth eight points. Map title, meeting term, RSVP term, location, fee, limits, and cancellation metadata to their explicit fields and columns. Assign distinct sentinels and include null cases that must remain distinguishable from zero or empty values.

Exercise NA14-B, history round trip, is worth six points. Design a fresh-scope test for two waitlist occurrences of one member and explain the composite key. State why an identity-only dictionary and a same-context reload can each conceal a defect. Keep provider precision as a separate unverified question.

Exercise NA14-C, title compatibility, is worth six points. Describe the mapping and historical-data decisions required by the proposed title value object. Identify what source inspection establishes and what materialization execution must still prove. Review [the final solutions](SOLUTIONS-13-20.md) after writing the test plan.


[Complete course route](README.md) | [Separate solutions and assessment](SOLUTIONS-13-20.md)
