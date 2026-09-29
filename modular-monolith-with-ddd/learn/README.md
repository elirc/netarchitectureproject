# Study guide: modular-monolith-with-ddd (READ tier)

This folder is for a junior engineer who wants to learn *how to study* this repo, and how to direct a coding agent inside it
without being fooled. It sits next to `training/` and does not replace it. `training/navigation/` is the material; this guide
tells you the order, the time to spend, what to do by hand, and what to hand to an agent.

READ tier means there is **no ticket ladder and there are no incident branches here**. You learn by reading real code, tracing
flows, and doing **reading fire drills** (`learn/02-fire-drills.md`): a production symptom is given and you find the cause in
the code without running anything.

## What this app is and why it's in the portfolio
- Kamil Grzybek's reference "MyMeetings" app (meeting groups, meetings, fees): one .NET process split into 5 modules under
  `src/Modules/` (Administration, Meetings, Payments, Registrations, UserAccess), each with its own SQL schema in
  `src/Database/CompanyName.MyMeetings.Database/Structure/`.
- It is in the portfolio because it is the cleanest example you have of **enforced module boundaries**
  (`src/Tests/ArchTests/`) and of **outbox → inbox → internal-command** messaging between modules.
- It is also where you learn that a famous reference repo still has real gaps. `training/navigation/04-outbox-inbox-processing.md`
  documents one (a republish mints a new Guid). The committed `main` also stores a meeting's end date as its start date
  (on-ramp exercise 3).

## Known state of main (read before you plan anything)
- **Build: UNVERIFIED on this machine.** `src/global.json` pins SDK `8.0.0` with `rollForward: latestFeature`. Only SDK 10 is
  installed here, which is the same blocker B01 hit on netauth (`batch1report/projects/netauth.md`). To build, install SDK 8
  or use a temporary `global.json` override in a scratch worktree. Never commit that override.
- The database is **SQL Server**. The schema is a SQL database project (one `.sql` file per table) and there are **no EF
  migrations**. Integration tests need a SQL Server container (see the README section "3.13 Integration Tests").
- The working tree has **6 uncommitted user files** (a `MeetingTerm` end-date fix plus new tests, the same fix as
  `Desktop\.netarchitectureproject\astraupskill\`). Do not edit, stage or stash them. When an exercise says "read HEAD", use
  `git show HEAD:<path>`.
- Payments is **event-sourced** (README section "3.15 Event Sourcing"). The other modules use EF Core state storage.

## Prerequisites
You need these before the study route will make sense. Do each one in about 30 minutes, then come back.
1. **C# classes, interfaces, `async`/`await`, and generics** well enough to read
   `src/BuildingBlocks/Domain/Entity.cs` (36 lines) and explain every line. If you can't yet, do `.netramp`'s `learn/00-onramp.md` first.
2. **What a transaction is and what "dual write" means.** Read [01 Transactional outbox](../../../opusorganize/apprenticeship/curriculum/01-transactional-outbox.md).
3. **At-least-once delivery and idempotency.** Read [02 Idempotency](../../../opusorganize/apprenticeship/curriculum/02-idempotency.md).
4. **Why a second process makes check-then-act unsafe.** Read [03 Concurrency races](../../../opusorganize/apprenticeship/curriculum/03-concurrency-races.md), sections 1–2.
5. **Pinning current behavior before you change it.** Read [04 Characterization tests](../../../opusorganize/apprenticeship/curriculum/04-characterization-tests.md).
6. **Checking code you didn't write.** Read [05 Verify before trust](../../../opusorganize/apprenticeship/curriculum/05-verify-before-trust.md). You will use it in every session.

Optional background: [16 Sagas vs 2PC vs outbox](../../../opusorganize/apprenticeship/curriculum/16-sagas-vs-2pc-vs-outbox.md)
(this repo and eShop are its worked examples) and the repo's own ADRs in `docs/architecture-decision-log/` (0002, 0014, 0015 and 0017 matter most).

## Study route
There are 9 sessions and about 9.5 hours in total. Do them in order. Keep a notes file **outside the repo**.
Each exit criterion should be checked by you, not by an agent.

### Session 1 — Orientation and a map on paper (60 min)
- **Files/branches:** `README.md` sections 1–3.3; `docs/architecture-decision-log/0002-*.md`, `0004-*.md`, `0014-*.md`,
  `0015-*.md`; `src/CompanyName.MyMeetings.sln`; `src/global.json`; `training/README.md`.
- **Do by hand:** draw the 5 modules as boxes. For each module, list its 4 main projects (Api is under `src/API/`, while
  Application, Domain, Infrastructure and IntegrationEvents are under `src/Modules/<Module>/`) and its SQL schema folder.
  Write one sentence explaining why the author chose a modular monolith (ADR 0002).
- **Delegate, then verify:** ask an agent to "list every project in the .sln grouped by module". Then open two `.csproj`
  files yourself and check that at least one `ProjectReference` it claims is real. Record any claim it got wrong.
- **Exit criterion:** without notes, you can name all 5 modules, say which one is event-sourced, and say why this repo does
  not build here as-is (global.json pins SDK 8).

### Session 2 — On-ramp, part 1: read the domain (75 min)
- **Files/branches:** `learn/00-onramp.md` exercises 1–4; `src/Modules/Meetings/Domain/Meetings/Meeting.cs`,
  `MeetingAttendee.cs`, `MoneyValue.cs`, `src/BuildingBlocks/Domain/ValueObject.cs`.
- **Do by hand:** all four exercises. They are predict-the-output and read-HEAD questions, so an agent would just give you the answer.
- **Delegate, then verify:** nothing. This session is fundamentals.
- **Exit criterion:** your answers match `learn/_answers/00-onramp.md` for 1–4. You can explain the `+ 1` in
  `MeetingAttendeesNumberIsAboveLimitRule.cs:24` and why `MeetingTestsBase.cs:60-61` means no unit test would catch exercise 3's bug.

### Session 3 — One command, file by file (60 min)
- **Files/branches:** `training/navigation/02-command-flow-create-meeting.md`; `learn/00-onramp.md` exercises 5–6;
  `src/Modules/Meetings/Infrastructure/Configuration/Processing/UnitOfWorkCommandHandlerWithResultDecorator.cs`;
  `src/BuildingBlocks/Infrastructure/UnitOfWork.cs`.
- **Do by hand:** follow `POST api/meetings/meetings` from `MeetingsController` to `SaveChangesAsync` with the files open.
  Then do exercises 5–6.
- **Delegate, then verify:** ask an agent "where is SaveChanges called for CreateMeetingCommand, and what runs just before it?"
  Check its answer against `UnitOfWork.cs:23-25`. If it says the handler saves, that's a hallucination you just caught.
- **Exit criterion:** you can state the order *handler → dispatch domain events (publish in-process, then add outbox rows) → SaveChanges*
  and explain what happens to the meeting if an in-process notification handler throws.

### Session 4 — Boundaries that fail the build (60 min)
- **Files/branches:** `training/navigation/01-module-boundaries.md`; `src/Tests/ArchTests/Modules/ModuleTests.cs`;
  `src/Modules/Meetings/Tests/ArchTests/Application/ApplicationTests.cs` (10 tests; B01's doc says 8, so count them yourself).
- **Do by hand:** for each of the 3 carve-outs in `ModuleTests.cs`, write down one real class it exists for. Find
  `EventsBusStartup.cs` in Payments and say which Meetings type it is allowed to reference.
- **Delegate, then verify:** `learn/01-agentic-practice.md` Drill A (the agent tries to smuggle a cross-module reference, and
  you predict which ArchTest fails).
- **Exit criterion:** you can explain why `InternalCommand_Should_Have_Constructor_With_JsonConstructorAttribute` (line 116)
  turns a runtime failure into a test failure.

### Session 5 — One event across two modules (60 min)
- **Files/branches:** `training/navigation/03-integration-event-flow-meeting-attendee-added.md`; the 10-file trace at its end.
- **Do by hand:** walk all 10 files. At each hop, write which table the data lands in (`meetings.OutboxMessages`,
  `payments.InboxMessages`, `payments.InternalCommands`) and which Quartz job moves it on.
- **Delegate, then verify:** nothing new. Re-read your own notes instead.
- **Exit criterion:** you can draw the three hops and give the one failure each hop makes survivable, without looking.

### Session 6 — Reading fire drills (90 min) — do this BEFORE Session 7
- **Files/branches:** `learn/02-fire-drills.md` (FD1–FD5). Do **not** open `training/navigation/04-*.md` yet, because it spoils FD1 and FD4.
- **Do by hand:** all of it. For each drill, write the suspect file:line, the mechanism, the one query or log line that would
  confirm it in production, and a fix outline. No agent, no running code.
- **Delegate, then verify:** after you've written your answers, ask an agent the same FD3 question and grade it against
  `learn/_answers/02-fire-drills.md`. Did it invent a retry mechanism that doesn't exist?
- **Exit criterion:** at least 3 of 5 root causes match the sealed answers, and for each miss you've written down the pattern behind it.

### Session 7 — Outbox/inbox mechanics and the Guid gap (60 min)
- **Files/branches:** `training/navigation/04-outbox-inbox-processing.md`;
  `src/Modules/Meetings/Infrastructure/Configuration/Processing/Outbox/ProcessOutboxCommandHandler.cs:55-69`;
  `src/Modules/Meetings/Application/Meetings/SendMeetingAttendeeAddedEmail/MeetingAttendeeAddedPublishEventNotificationHandler.cs:18-19`.
- **Do by hand:** compare doc 04 with your FD1/FD4 answers. Write a 5-line spec for making the integration-event Id stable.
- **Delegate, then verify:** `learn/01-agentic-practice.md` Drill B (the agent implements your spec in a scratch worktree, and
  you review it adversarially).
- **Exit criterion:** you can explain why the inbox PRIMARY KEY does not deduplicate a republished event today, and which
  single line your spec changes.

### Session 8 — Trade-offs and the change request (75 min)
- **Files/branches:** `training/navigation/05-why-modular-monolith-vs-microservices.md`, `06-first-change-onboarding.md`,
  `07-change-request.md` (then the sealed `training/_answers/07-change-request-answer.md`).
  Note: `07` cites `MeetingTermCommandHandlerTests.cs` as a style model. That file is one of the user's *untracked* WIP files,
  so use `MeetingAddAttendeeTests.cs` as the committed model instead.
- **Do by hand:** write the 6 answers for the change request as a spec. This is the most important writing you'll do in this repo.
- **Delegate, then verify:** `learn/01-agentic-practice.md` Drill C (the agent implements your spec, and you check it against
  the verification checklist).
- **Exit criterion:** your written plan names the reused command (`RemoveMeetingAttendeeCommand`) and the project that gets
  the new event type *before* you open the sealed answer.

### Session 9 — Interview kit (45 min)
- **Files/branches:** `training/interview/QUESTIONS.md` (added in B08) and the sealed `training/_answers/interview-questions.md`.
- **Do by hand:** answer the 8 questions out loud, 2 minutes each, then write one STAR story from Session 6 or 7
  ("I found a duplicate-delivery gap in a reference architecture by reading code").
- **Delegate, then verify:** have an agent play a sceptical interviewer on Q3 and Q6. Grade yourself, not it.
- **Exit criterion:** you can answer "modular monolith or microservices?" with a trade-off tied to a real file, not a slogan.

## Do vs. delegate: the rule for this repo
| Always by hand | Delegate, then verify |
|---|---|
| Reading and tracing (Sessions 2, 3, 5), fire-drill diagnosis (Session 6), specs (Sessions 7, 8), grading an agent's answer | Listing projects/references, scaffolding a test in the existing NUnit style, implementing a spec in a **scratch worktree off HEAD** |

Before you trust any agent output here, run it through `learn/01-agentic-practice.md` → "Verification checklist".

## How you know you're done here
- You finished all 9 exit criteria and graded yourself against every sealed answer.
- You can trace any command or integration event in any module on your own. Test it by picking `NewUserRegisteredIntegrationEvent`
  (one publisher, three subscribers) and tracing it in 30 minutes.
- You can explain the Guid gap, the poison-message gap (FD3) and the HEAD end-date bug to someone else, with file:line references.

## Next repo
**eShop** (`Desktop\netopen1\eShop`, `learn/README.md`). It uses the same outbox idea, but across real services, a real broker
(RabbitMQ) and separate databases, so the failure windows you found here get a network in the middle.
After eShop, go on to **gitvg/atlas** (B02), where you run the code instead of only reading it.
