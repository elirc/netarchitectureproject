# Temporal lab: collecting evidence another learner can audit

This guide accompanies [chapter 06](06-DISPOSABLE-LABS-AND-MUTATION-EVIDENCE.md) and the [runner](labs/temporal_lab.py). It teaches result interpretation rather than adding another domain requirement. Read the failure predictions before opening the solutions. A useful experiment produces an explanation that survives a second person asking what actually executed.

## Start with the smallest honest claim

Suppose the console says that all twenty cases passed. Write the claim as twenty assertions over copied real temporal domain classes and a generated adapter, compiled in an owned temporary SDK project. This statement names both the strong evidence and its limits. The real MeetingTerm constructor and rule executed; the application handler did not. The generated adapter demonstrates the shape of a mapping defect, but it does not establish the current handler's behavior. Handler behavior needs the source trace or the existing handler tests, with their distinct execution record.

Do not describe the result as twenty production scenarios. Several assertions inspect boundaries of the same temporal operation. The number helps detect missing execution and communicates coverage inventory, but it is not a count of independently deployed features. A single assertion can also contain more than one comparison. Keep the runner's case accounting separate from broad claims about confidence.

The application targets .NET 8 through its shared build properties. The disposable project targets the installed .NET 10 SDK and excludes application package references. Therefore, a successful disposable run does not demonstrate that the complete application restores, builds, or runs on its target framework. This difference is deliberate and must remain visible when sharing a screenshot of green output.

## Assemble a baseline receipt

Record the working directory, exact command, selected mode, build result, semantic result, and original-file hash result. A reader should not need to infer whether output came from a previous invocation. Preserve the entire short result rather than cropping away an unexpected warning or error. If a prerequisite is missing, record that limitation instead of translating it into a domain failure.

The baseline command is:

```powershell
python astraupskill/advanced/extended-course/labs/temporal_lab.py
```

Run it from the .netarchitectureproject root. The runner locates the nested source tree relative to its own file, creates its own temporary directory, and clears package sources for the generated project. Its successful completion reports twenty cases and unchanged hashes for eight selected originals. Hash comparison is a preservation check for that selected set during this execution; it is not a repository cleanliness check or evidence about unselected files.

A reviewer can ask you to identify one concrete input and expected result from every group: positive interval construction, invalid ordering, generated mapping, clock boundaries, bounded RSVP membership, and unbounded membership. If you cannot recover those cases from your evidence packet, the summary is too compressed to teach from. Include a pointer to the runner instead of copying its entire implementation into the report.

## Interpret mutations as paired experiments

Every mutation requires a passing baseline on the same relevant source version. Without that comparison, a failing mode could merely reproduce an existing environmental problem. The useful pair is successful compilation and baseline assertions, followed by successful compilation and the predicted semantic assertion failure under one deliberate change.

The relaxed meeting rule permits equal endpoints. Its expected failure is the equal-interval rejection case. A reversed interval alone would continue to fail construction and therefore would not expose this mutation. This is why a boundary table is more valuable than a vague description such as testing invalid dates.

The generated start-twice mapping feeds the start value into the end parameter. It reaches the real strict-order rule and fails during construction. The current case label identifies the mapping assertion being attempted; the rule exception explains why the assertion could not receive a value. This result is different from a shifted-end mutation, which could construct successfully and require exact expected-value comparisons to detect the wrong duration.

The clock mutation changes strict passage of the start boundary into inclusive passage. It must fail at the exact start instant. Before-start and after-start observations can remain identical across both implementations. A test that samples only distant dates would not distinguish the policies, regardless of how many random dates it generates.

The RSVP mutation excludes the end boundary. Its predicted failure occurs at the end instant, while interior membership can remain true. Do not repair the prediction by borrowing MeetingTerm's strict ordering policy: interval validity and membership are different questions handled by different source classes.

## Resolve mismatches without moving the oracle

When output differs from the prediction, first classify the failure stage. Restore or compilation failure means the semantic case did not run. A mutation replacement that no longer matches means the source changed and the experiment needs review. A different rule exception can mean an earlier precondition intercepted the input. A surviving mutation may indicate missing coverage, a mistaken prediction, or a transformation that is behaviorally equivalent for the exercised inputs.

Only after that classification should you consider changing an assertion. Preserve the original prediction and explain the reason for revision. Otherwise, repeatedly editing expectations until the run turns green produces a circular oracle: the implementation and the test agree because the latter copied the former's accident. The independent source contract, exact input, and expected boundary relationship should explain the final assertion.

## Review packet exercise

Prepare a one-page packet containing one baseline and one mutation result. Give a peer the packet without the solutions. Ask them to identify the invoked code boundary, the mutation's exact changed comparison or argument, the intended failing case, and one important behavior still untested. This is an ungraded review activity; the chapter exercises retain the installment's formal point total.

A satisfactory packet makes it possible to distinguish real domain execution from generated-adapter behavior, semantic failure from toolchain failure, selected-source preservation from whole-repository claims, and in-memory results from persistence or transport evidence. If the peer cannot make those distinctions, improve the evidence description before adding more tests. The goal is a result that can be challenged precisely, not a larger collection of unexplained green and red console lines.
