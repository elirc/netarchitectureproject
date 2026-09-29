# First-change onboarding — what to understand before touching this repo

This is a 1-page checklist, not a tutorial. If you can answer each bullet with a file path, you're
ready for a first PR here.

1. **Which module owns the code you're about to touch, and what are you NOT allowed to reference
   from it?** Find the module's `ArchTests` project (`src/Modules/{Module}/Tests/ArchTests/`) and
   read what it forbids before writing code that would fail it. See `navigation/01-*.md`.
2. **Is this a command or a query?** Commands go through the
   `Validation → Logging → UnitOfWork` decorator stack (`Infrastructure/Configuration/Processing/`
   in your module) and commit as a side effect of the pipeline, not inside your handler. Queries
   (`IQuery<T>`) skip all of that — check `{Module}Module.cs`'s `ExecuteQueryAsync` to see they use
   a bare `mediator.Send`, no unit-of-work wrapper, because they don't write anything.
3. **Does your change need to tell another module something?** If yes, you're adding a domain event
   + an integration event + a handler in the *other* module's `Application` layer — never a direct
   reference. Trace `navigation/03-*.md` first; copy its shape, don't invent a new one.
4. **Where does the transaction boundary actually sit?** Not in your handler. Find the
   `UnitOfWorkCommandHandler(WithResult)?Decorator` for your module and confirm `CommitAsync` is
   called exactly once per command, after your handler returns.
5. **Are you changing an aggregate's public factory/behavior methods?** Check whether the change
   affects an existing invariant enforced by a `Rule` class (e.g.
   `src/Modules/Meetings/Domain/Meetings/Rules/MeetingTermMustEndAfterStartRule.cs`) — rules are
   the idiomatic place for domain validation here, not ad-hoc `if` checks inside the aggregate
   method.
6. **What's the test story?** Each module has `Tests/UnitTests` (domain + handler tests, often using
   `NSubstitute` for repositories) and `Tests/IntegrationTests` (real DB via a test fixture). Match
   the existing test's shape in the same folder before inventing your own pattern.
7. **What database change does this need?** Schema lives in
   `src/Database/CompanyName.MyMeetings.Database/Structure/{module-schema}/`, one `.sql` file per
   table — no EF Core migrations in this repo; the DB project is the source of truth (NUKE/Azure
   Pipelines build it, see `azure-pipelines.yml` and `.nuke/`). Don't add an EF migration expecting
   it to "just work" here.
8. **Don't touch the 6 files already dirty in this working tree** — a preexisting, uncommitted
   `MeetingTerm` start/end-date fix under `src/Modules/Meetings/{Application,Domain}` (see
   `training/README.md`). If your first change happens to touch the same files, coordinate before
   editing — don't silently overwrite it.
