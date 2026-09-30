# Boundary and rejection worksheets

The current rule is `endDate <= startDate` means broken. It does not say meetings must last a whole minute, remain on one day, or normalize time zones. Those would be additional product policies. Keep all values in UTC for the basic table, then separately discuss what a future boundary would need to do about unspecified kinds or user-local time. Do not claim this value object currently converts them.

| Input case | Start/end relation | Current rule | Mapping/repository observation |
|---|---|---|---|
| Ordinary interval | End two hours later | Accept | Both boundaries survive create and change |
| Smallest positive interval | End one tick later | Accept | No invented minimum-duration restriction |
| Equal boundaries | Same value | Reject | Specific business-rule exception |
| Reversed interval | End one tick earlier | Reject | No valid MeetingTerm returned |
| Overnight interval | End next UTC day | Accept if later | No same-day rule exists here |
| Very long interval | End days later | Accept under this rule | Maximum duration would be a separate extension |

Exercise **MA-04**: add expected outcomes for create and change to every row. On create, distinguish "meeting object was returned" from "repository AddAsync was called." On change, identify the original object whose state must be compared. Do not construct a second meeting and compare that instead of the object returned by the mocked repository.

## Expand the all-fields rejection criterion

For the independent aggregate-rule exercise, rejection must preserve the complete observable aggregate state and its event sequence. A term-only assertion is insufficient if an implementation changes the title before discovering a later invalid condition. Before the call, capture a stable projection of identity/group membership, title, term boundaries, description, location values, limits, RSVP values, fee values, creator/create metadata, change metadata, cancellation metadata, and active nested attendee/nonattendee/waitlist state. Capture domain events as an ordered projection including event type and relevant identifiers.

| Field family | Before rejected change | Required after rejection |
|---|---|---|
| Requested mutable values | Original title, description, term, location, limits, fee | Equal values, including values unrelated to the invalid input |
| Audit fields | Original change date/member | No new audit timestamp or actor |
| Identity and creation fields | Existing meeting/group/creator | Unchanged |
| Nested collections | Existing entries and active-state flags | Same membership, order where meaningful, and nested values |
| Domain events | Existing event sequence | No appended, removed, or rewritten event |

Capture values, not merely references. If the before snapshot holds the same mutable list as the aggregate, mutating the aggregate can change both sides and make a false equality assertion pass. Conversely, comparing arbitrary JSON serialization of the private object can omit private fields or include internal caches. Design an explicit projection, or a narrowly scoped reflection snapshot whose inclusion and copying rules are documented.

Exercise **MA-05**: enumerate every private field currently declared in `Meeting` and account for the inherited event collection. Explain how your projection covers each field or why a field is derived and separately checked. Create a rejected change that also proposes a different title, description, location, fee, and audit actor, so an early partial assignment becomes visible. Exercise **MA-06**: choose one field your first design missed and construct the smallest deliberately broken mutation that would escape the old assertion.

[Advanced index](README.md)
