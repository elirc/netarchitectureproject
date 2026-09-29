# On-ramp: 8 warm-ups before `training/navigation/`

Every exercise uses real files in this repo. You don't need to build or run anything, just read. Answers are sealed in
`learn/_answers/00-onramp.md`. Write your answer down before you look.
Line numbers refer to committed `HEAD` (`a7d111a`). Where the working tree differs (the user's uncommitted `MeetingTerm` fix),
the exercise tells you to use `git show HEAD:<path>`.

---

## 1. Predict a business rule (10 min)
Open `src/Modules/Meetings/Domain/Meetings/Rules/MeetingAttendeesNumberIsAboveLimitRule.cs:23-24`.
`Meeting.AddAttendee` calls it at `Meeting.cs:168` with
`(_meetingLimits.AttendeesLimit, GetAllActiveAttendeesWithGuestsNumber(), guestsNumber)`.

Say whether `IsBroken()` returns true or false for each case:
| case | attendeesLimit | active attendees incl. guests | guestsNumber (new member) |
|---|---|---|---|
| a | `null` | 40 | 3 |
| b | 10 | 8 | 1 |
| c | 10 | 8 | 2 |
| d | 5 | 4 | 0 |

Then explain what the `+ 1` stands for, and why the test at
`src/Modules/Meetings/Tests/UnitTests/Meetings/MeetingAddAttendeeTests.cs:100-121` says "creator ... automatically" in its
comment. (Hint: `Meeting.cs:124`.)

## 2. Money and value equality (10 min)
Read `MeetingAttendee.cs:71-78`, `MoneyValue.cs:7` and `:24-27`, and `src/BuildingBlocks/Domain/ValueObject.cs:11-45`.
- a) An attendee joins a meeting whose fee is `MoneyValue.Of(10, "EUR")` with `guestsNumber = 2`. What is `_fee`?
- b) `MoneyValue.Undefined` returns a **new** object on every call (`=>`, not `=`). Why does
  `eventFee != MoneyValue.Undefined` still behave correctly?
- c) Suppose `ValueObject` did **not** override `==`/`!=` (so they compared references). What would `_fee` be for a free
  meeting? Would any user notice? What does that tell you about bugs that "cancel out"?

## 3. Read HEAD, not the working tree (10 min)
Run `git show HEAD:src/Modules/Meetings/Application/Meetings/CreateMeeting/CreateMeetingCommandHandler.cs` and read the
`MeetingTerm.CreateNewBetweenDates(...)` call (around line 24 of HEAD's version).
- a) A user creates a meeting from 18:00 to 20:00. What `StartDate` and `EndDate` get stored?
- b) Does any rule in HEAD reject this? (List `src/Modules/Meetings/Domain/Meetings/Rules/` and remember that
  `MeetingTermMustEndAfterStartRule.cs` is *untracked*, so `git status` shows `??`.)
- c) Look at `src/Modules/Meetings/Tests/UnitTests/Meetings/MeetingTestsBase.cs:60-61`. Why would the whole committed unit
  test suite stay green with this bug?
- d) The same mistake exists in one more HEAD handler. Name it.

## 4. Where does a rule get checked, and what is thrown (5 min)
`src/BuildingBlocks/Domain/Entity.cs:28-34` defines `CheckRule`. Name the exception type, and the test helper that asserts it
(`src/Modules/Meetings/Tests/UnitTests/SeedWork/TestBase.cs:43-52`). If you wrote a new rule class, which interface must it
implement, and which two members?

## 5. Trace the commit (10 min)
Starting at `src/Modules/Meetings/Infrastructure/Configuration/Processing/UnitOfWorkCommandHandlerWithResultDecorator.cs:25-42`,
follow `CommitAsync` into `src/BuildingBlocks/Infrastructure/UnitOfWork.cs:19-26`, then into
`src/BuildingBlocks/Infrastructure/DomainEventsDispatching/DomainEventsDispatcher.cs:38-82`.
- a) Put these steps in order: `SaveChangesAsync`; `_mediator.Publish(domainEvent)`; `_outbox.Add(...)`; the handler's `Handle`.
- b) An in-process notification handler throws inside `_mediator.Publish` (`DomainEventsDispatcher.cs:63`). Is the new
  meeting row saved? Is an outbox row saved?
- c) Which Id is used as the outbox row's primary key (`DomainEventsDispatcher.cs:74-78`)? Keep this answer, because it matters in drill FD1.

## 6. Explain a schema (10 min)
Open `src/Database/CompanyName.MyMeetings.Database/Structure/payments/Tables/InboxMessages.sql`.
- a) What does a row with `ProcessedDate IS NULL` mean?
- b) Write the T-SQL to count pending inbox messages per `Type`, oldest first.
- c) Which constraint deduplicates rows? What exactly does it deduplicate on?
- d) This is SQL Server, not Postgres. What would you add to a `SELECT` so that two workers can't claim the same row? (Name
  the table hints. You don't have to write the full statement.)

## 7. Static state in tests (5 min)
`src/Modules/Meetings/Domain/SharedKernel/SystemClock.cs` is a static class with `Set`/`Reset`.
`TestBase.cs:65-69` calls `SystemClock.Reset()` in `[TearDown]`. What kind of flaky failure would appear if one test called
`SystemClock.Set(...)` and TearDown didn't exist? Why would it depend on the order the tests run in?

## 8. Write one characterization test (20 min)
`Meeting.AddNotAttendee` (`Meeting.cs:182-209`) has a behavior that **no committed test covers**: when an attendee drops out,
the *earliest active* waitlist member is promoted to attendee with `0` guests (`:194-207`). Check the coverage gap yourself:
`src/Modules/Meetings/Tests/UnitTests/Meetings/MeetingAddNotAttendeeTests.cs` never mentions the waitlist.

Write an NUnit test in the style of `MeetingWaitlistTests.cs:82-96` that pins this behavior:
- Arrange: member B joins the group and attends. Member A joins the group and signs up to the waitlist
  (`SignUpMemberToWaitlist`, `Meeting.cs:222`).
- Act: B calls `AddNotAttendee`.
- Assert: a `MeetingAttendeeAddedDomainEvent` was published for A with `GuestsNumber == 0`.

You're pinning **current** behavior, not judging it ([04](../../../opusorganize/apprenticeship/curriculum/04-characterization-tests.md)).
Write the test on paper or in a scratch worktree. **Do not add it to the user's working tree.**
