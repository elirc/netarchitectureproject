# Run real domain source in a disposable failure lab

From the `.netarchitectureproject` root, run:

```powershell
python astraupskill/advanced/labs/interval_lab.py
python astraupskill/advanced/labs/interval_lab.py --mode broken-mapping
python astraupskill/advanced/labs/interval_lab.py --mode broken-rule
```

The baseline should print five passing real-domain interval/mapping cases and return zero. Each broken mode should compile successfully but return nonzero because a semantic assertion fails or the domain exception escapes the expected success path. These failures are the intended lesson. No learner should "fix" them by removing the assertion or weakening the exception expectation.

The [runner](labs/interval_lab.py) copies `MeetingTerm`, its strict-order rule, `SystemClock`, `ValueObject`, and their small domain support types to a uniquely created temporary directory. It generates a console project targeting the installed .NET 10 SDK, uses a NuGet configuration with package sources cleared, and has no `PackageReference`. Restore here generates local SDK assets; it does not install project packages. The original full project targets .NET 8, so this isolated SDK-only exercise does not certify full-project target-framework compatibility. It checks the copied domain behavior on the available runtime.

`broken-mapping` changes only the generated mapping adapter from `(startDate, endDate)` to `(startDate, startDate)`. The adapter still calls the same real factory with the same public signature. A valid three-hour request becomes an equal interval and is rejected. This is preferable to a starter that changes the constructor shape and merely fails to compile: the learner sees the actual class of mapping defect.

`broken-rule` changes only the disposable rule copy from `<=` to `<`. Reversed intervals still reject, so one negative-duration test would pass and provide false reassurance. The equal-boundary row now exposes the missing condition. All original source hashes are checked before and after the run. Temporary artifacts are cleaned by the scoped temporary-directory context; the runner does not invoke Git or touch production databases.

Before running each mode, write the expected first failing case. Exercise **MA-07**: explain why the one-tick positive case belongs beside the equality case. Exercise **MA-08**: propose a third mutation that preserves signatures and is caught by the successful mapping assertion. For example, consider returning a shifted end rather than passing start twice. State whether your mutation belongs in the disposable adapter or the disposable domain source, and never apply it to the original source just to demonstrate a failure.

For full handler evidence, use the existing unit-test project through the repository's documented route. A bounded command from this root is:

```powershell
dotnet test modular-monolith-with-ddd/src/Modules/Meetings/Tests/UnitTests/CompanyName.MyMeetings.Modules.Meetings.Domain.UnitTests.csproj --no-restore --filter "FullyQualifiedName~MeetingTerm" --verbosity minimal
```

This command requires the full project's already restored assets and its target runtime. If those prerequisites are unavailable, report a blocked test rather than installing dependencies or replacing the assertion with the console result. The disposable lab does not invoke the actual internal handlers, repository substitutes, HTTP endpoints, or database transaction adapters. Its source-grounded value is precise but intentionally bounded.

[Advanced index](README.md)
