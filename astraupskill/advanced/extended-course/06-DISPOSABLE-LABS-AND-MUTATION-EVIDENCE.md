# 06 - Use disposable mutations to prove that an assertion can fail

A passing test can be weak because its inputs never distinguish the intended behavior from a plausible defect. A small semantic mutation makes that weakness visible. This chapter introduces a disposable lab that copies selected real domain sources, compiles them with an SDK-only harness, and changes only the copied code or generated adapter. The original source and learner work remain untouched. Read [the lab runner](labs/temporal_lab.py), [MeetingTerm](../../../modular-monolith-with-ddd/src/Modules/Meetings/Domain/Meetings/MeetingTerm.cs), [Term](../../../modular-monolith-with-ddd/src/Modules/Meetings/Domain/Meetings/Term.cs), and [the earlier interval lab](../labs/interval_lab.py).

## The lab's scope is deliberately small

The runner copies the value-object base, rule interface and exception, ignore-member attribute, domain clock, MeetingTerm, its order rule, and RSVP Term into a uniquely created temporary directory. It writes a console project targeting net10.0 with no package references and a NuGet configuration whose package sources are cleared. Restore generates local SDK assets; it does not install the full application's third-party dependencies.

The full project targets net8.0 through shared build properties. The lab therefore proves selected copied source behavior on the installed SDK environment, not compatibility of the complete application target or its packages. It does not instantiate the real internal application handlers, load a repository implementation, issue HTTP requests, or commit database state. The generated mapping adapter has the same factory signature but is not the actual handler.

This narrow scope is useful because the experiment is fast, isolated, and easy to inspect. The source-derived value is real: the compiled MeetingTerm and Term implementations are copied from the checkout rather than rewritten as a fake model. The integration limitation is equally real: an adapter passing start and end correctly does not prove the actual handler does so. That remains the purpose of the handler regression suite.

## Baseline predictions come before execution

Before running the baseline, predict valid interval preservation, equal and reversed rejection, the strict IsAfterStart boundary, inclusive RSVP endpoints, and open-ended RSVP behavior. The harness records named cases and raises a clear failure when an expectation disagrees. A successful output should name the number of real-domain cases; it should not use language such as full system verified.

The meeting cases use fixed UTC values and small differences including one tick. The clock cases set SystemClock to before, equal to, and after the start, then reset it. The RSVP cases exercise a closed interval at both endpoints and outside it, plus open and absent bounds. These inputs distinguish the two temporal contracts discussed in chapter three without inventing a new shared rule.

The mapping case uses an asymmetric positive interval and checks exact boundaries. It is intentionally separate from construction tests. A factory can be correct while an adapter passes the wrong source value. Likewise, an adapter can preserve arguments while the factory accepts an invalid interval. The lab's case groups make those responsibilities visible.

## Signature-compatible mutations produce meaningful failures

The broken-meeting-rule mode changes the copied strict-order expression from less-than-or-equal to less-than. The code still compiles and reversed intervals still reject, but equality is accepted. The equality case should expose that defect. If your suite contained only a reversed interval, this mutation would survive and reveal missing boundary coverage.

The broken-mapping mode changes only the generated adapter to pass start twice. Its public factory call shape remains valid. A positive request becomes an equal interval and fails semantically. This is a useful mapping defect because it reaches the real factory; changing the method name to something nonexistent would merely test the compiler's ability to reject an unknown symbol.

The broken-clock mode changes strict after-start comparison to include equality in the copied MeetingTerm. Valid construction remains unaffected. The exact-start clock case should fail, showing that interval validity and time-relative behavior need separate tests. A suite that only constructs values cannot detect this mutation.

The broken-rsvp-end mode changes the copied RSVP upper-bound comparison from inclusive to exclusive. The closed interval's end boundary should fail while its interior still passes. This mutation demonstrates why importing MeetingTerm's strict inequality into RSVP semantics is not a harmless cleanup. Each domain operation needs the inequality stated by its own contract.

## Commands and expected status

Run from the desktop project's root with Python and the already installed .NET 10 SDK:

```powershell
python astraupskill/advanced/extended-course/labs/temporal_lab.py
python astraupskill/advanced/extended-course/labs/temporal_lab.py --mode broken-meeting-rule
python astraupskill/advanced/extended-course/labs/temporal_lab.py --mode broken-mapping
python astraupskill/advanced/extended-course/labs/temporal_lab.py --mode broken-clock
python astraupskill/advanced/extended-course/labs/temporal_lab.py --mode broken-rsvp-end
```

The baseline should exit zero. Each broken mode should compile and then exit nonzero at the intended semantic case. Record the named failure and original-source hash check. A restore failure, missing SDK, or syntax error is not a successful mutation experiment. It means the behavioral case was not reached and must be reported as such.

Do not run all modes repeatedly merely to accumulate passing output. One reviewed baseline and each distinct intended failure are sufficient unless source or harness changes introduce a new uncertainty. If a mutation no longer finds its exact source expression, the runner stops rather than guessing a replacement. That protects the meaning of the experiment when the source evolves.

## A failure matrix is stronger than an exit-code list

Create a matrix with mutation, compilation, first semantic distinction, expected observation, and excluded claims. The strict-order mutation should be detected by equality, not by arbitrary exception text. The mapping mutation should reach the valid-mapping case and reveal the duplicate argument. The clock mutation should fail exactly at start. The RSVP mutation should fail at its inclusive end. This matrix explains why each case exists.

An unexpected failure earlier in the run invalidates the intended result. For example, if a copied source type gains a new dependency and compilation fails, none of the later domain assertions ran. The correct response is to update the lab's dependency inventory after source review, not to count the nonzero exit as evidence that every mutation was killed. Evidence is about the path taken, not merely a process status.

A mutation surviving the suite is also useful. It may reveal a missing case, an equivalent transformation, or an incorrectly stated contract. Analyze which of those applies before adding assertions. A random test added only because it makes the mutation fail can encode an unintended requirement. The contract and its independent expected values remain the oracle.

## Preserve originals and make cleanup reviewable

The runner records hashes of every copied source file before the experiment and compares them afterward. All generated project files and mutations live in its owned temporary directory. The directory identity and prefix are checked before relying on cleanup. The script does not invoke Git, edit application projects, or connect to databases.

Hash equality establishes that the selected original files did not change during the run; it does not certify every file in the repository or all preexisting learner changes. The report should name the selected source set. Similarly, temporary cleanup removes this experiment's generated artifacts, not unrelated build outputs or caches in the application. Ownership makes the operation concrete and reviewable.

If the process is interrupted externally, normal cleanup behavior can depend on how it was interrupted. A later manual investigation should identify the unique lab directory rather than deleting broad temporary trees. The intended workflow is bounded creation and removal, not a general cleanup utility. This distinction keeps a learning experiment from becoming an unrelated filesystem operation.

## Full-project evidence remains separate

The existing domain unit-test target is the actual CompanyName.MyMeetings.Modules.Meetings.Domain.UnitTests.csproj file under the nested meeting module. A focused no-restore command can select MeetingTerm-related tests when its existing dependencies and target runtime are available. Verify the path and prerequisites before executing. The course does not install missing packages to make a documentation check appear complete.

A handler suite run adds evidence about reflection invocation, repository substitutes, and real mapping. An integration suite would add another boundary for persistence and application configuration. A request-level run would add transport behavior. The disposable lab is a useful first layer, not a replacement certificate for these later layers.

## Independent practice

Exercise NA06-A, mutation predictions, is worth eight points. Fill the four-mode failure matrix before running. Identify the exact boundary case for each mutation and explain why reversed-only interval coverage would miss the relaxed equality rule.

Exercise NA06-B, evidence triage, is worth six points. Classify baseline success, intended semantic failure, compilation failure, missing SDK, and a mutation that no longer matches source. State which results support a behavior claim and which require updating the experiment before interpretation.

Exercise NA06-C, new independent mutation, is worth six points. Propose a signature-compatible shifted-end mapping mutation and an assertion that detects it without relying on rejection. Explain why this adds evidence beyond the start-twice mutation and keep all changes in the generated adapter.

Use [the solution guide](SOLUTIONS-01-06.md) after recording predictions. The first installment is complete when you can explain what each successful or failing run proves, what remains untested, and why the original source is preserved.


Before handing results to another learner, include the invocation directory and the selected mode. A successful run from the repository root says nothing about a differently resolved source path in an copied script. The runner anchors its own source lookup to its file location; that design makes the original course path part of the experiment. Consult the [run evidence guide](LAB-EVIDENCE-01-06.md) when preparing a review packet.
