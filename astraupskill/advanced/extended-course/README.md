# Extended architecture engineering course

The completed twenty-chapter course develops source-grounded investigation and independent engineering practice in the nested modular-monolith-with-ddd project. It includes three separate solution guides, two investigation workbooks, two runnable disposable labs, and two independently assessed capstones. Current implementation, proposed changes, source-derived predictions, and executed evidence are distinguished throughout.

## Complete learning route

Read chapters in order and record predictions before consulting solutions. Each chapter contains three graded exercises worth twenty points: sixty exercises and 400 points in total. The two capstones have separate sixty-point rubrics, for 120 additional assessment points. Workbooks and lab receipt reviews provide ungraded practice.

Chapters 01-06 establish mapping, temporal invariants, reflection, and bounded experiments. Chapters 07-12 examine attendance, roles, queues, lifecycle behavior, event snapshots, and independent rule design. Chapters 13-18 connect orchestration, persistence, queries, HTTP, integration fixtures, and outbox processing. Chapters 19-20 supply complete capstone specifications and review rubrics.

- [01 - Find the boundary that can prove your architectural claim](01-REPOSITORY-MAP-AND-EVIDENCE-BOUNDARIES.md)
- [02 - Treat command mapping as behavior worth testing](02-COMMAND-MAPPING-AS-A-CONTRACT.md)
- [03 - Give each temporal value object its own contract](03-TEMPORAL-VALUE-OBJECTS-AND-BOUNDARIES.md)
- [04 - Observe aggregate state and domain events as one decision](04-AGGREGATE-MUTATION-AND-EVENT-EVIDENCE.md)
- [05 - Keep test infrastructure failures separate from business failures](05-FIXTURES-REFLECTION-AND-ASYNC-FAILURES.md)
- [06 - Use disposable mutations to prove that an assertion can fail](06-DISPOSABLE-LABS-AND-MUTATION-EVIDENCE.md)
- [07. Attendees, guests, and capacity as distinct quantities](07-ATTENDEES-GUESTS-AND-CAPACITY.md)
- [08. Host roles and the difference between rejection and unchanged state](08-HOST-ROLES-AND-REJECTION-ORDER.md)
- [09. Waitlists, decision history, and promotion boundaries](09-WAITLISTS-AND-DECISION-HISTORY.md)
- [10. Cancellation, removal, and time-dependent repeat behavior](10-CANCELLATION-REMOVAL-AND-TIME.md)
- [11. Domain events and independent snapshot oracles](11-DOMAIN-EVENTS-AND-SNAPSHOT-ORACLES.md)
- [12. Specify an independent rule before implementing it](12-INDEPENDENT-RULE-EXTENSION-AND-REJECTION.md)
- [13. Command orchestration and the actual commit boundary](13-COMMAND-ORCHESTRATION-AND-COMMIT-BOUNDARIES.md)
- [14. Persistence mappings and materialization without guessing](14-PERSISTENCE-MAPPINGS-AND-MATERIALIZATION.md)
- [15. Read models, SQL views, and independent query evidence](15-READ-MODELS-AND-QUERY-EVIDENCE.md)
- [16. HTTP contracts, identity sources, and error translation](16-HTTP-CONTRACTS-IDENTITY-AND-ERRORS.md)
- [17. Integration fixtures and failure diagnosis with owned data](17-INTEGRATION-FIXTURES-AND-FAILURE-DIAGNOSIS.md)
- [18. Dispatch, outbox processing, and partial-failure reasoning](18-DISPATCH-OUTBOX-AND-PARTIAL-FAILURES.md)
- [19. Capstone: a complete domain invariant extension](19-CAPSTONE-DOMAIN-INVARIANT-EXTENSION.md)
- [20. Capstone: an evidence packet another engineer can challenge](20-CAPSTONE-EVIDENCE-AND-ENGINEERING-REVIEW.md)

## Separate practice and answers

- [Solutions and grading for 01-06](SOLUTIONS-01-06.md)
- [Solutions and grading for 07-12](SOLUTIONS-07-12.md)
- [Solutions and assessment for 13-20](SOLUTIONS-13-20.md)
- [Investigation workbook 01-06](INVESTIGATION-WORKBOOK-01-06.md)
- [Investigation workbook 07-12](INVESTIGATION-WORKBOOK-07-12.md)
- [Temporal lab evidence guide](LAB-EVIDENCE-01-06.md)
- [Capacity and reason lab guide](LAB-CAPACITY-07-12.md)
- [Executable temporal lab](labs/temporal_lab.py)
- [Executable capacity lab](labs/capacity_lab.py)

## Verified execution boundaries

The temporal lab compiles eight copied real source files and a generated adapter, covering twenty assertions and four deliberate semantic mutations. The capacity lab compiles thirteen copied real source files, covering twenty-nine cases and three deliberate semantic mutations. Both baseline runs passed. All seven broken modes compiled successfully and failed at their predicted semantic cases. Original selected source hashes remained unchanged after every run.

Each lab uses an owned temporary .NET 10 SDK project with cleared package sources and no third-party package references. Neither executes the application's handlers, repositories, HTTP endpoints, or full .NET 8 solution. The actual existing unit-test target is CompanyName.MyMeetings.Modules.Meetings.Domain.UnitTests.csproj; its existence and source were checked, but the full project suite was not run. Integration fixtures clear tables and require a dedicated owned database; they were source-reviewed, not executed.

The course does not change application behavior or implement its proposed title rule or role/outbox capstones. Completing the instructional route means completing the specified reasoning, predictions, exercises, and assessments. Implementing a capstone, running an owned integration environment, and adding hosted HTTP or concurrency experiments are optional further learner work with explicit evidence requirements. No required chapter remains planned-only.

Preserve existing learner work when undertaking those optional projects. Keep executed checks separate from proposed checks, use synthetic data, and describe the strongest claim each observation actually supports.

[Advanced course](../README.md) | [Original course](../../README.md)
