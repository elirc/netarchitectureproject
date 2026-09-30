# Capacity and reason lab: real predicates, limited claims

This lab supports [chapter 07](07-ATTENDEES-GUESTS-AND-CAPACITY.md) and [chapter 10](10-CANCELLATION-REMOVAL-AND-TIME.md). The [Python runner](labs/capacity_lab.py) copies thirteen actual source files into an owned temporary directory and compiles them with an explicit generated program. It uses the installed .NET 10 SDK without third-party package references and clears package sources for the temporary project. It imports command and mutation helpers from the adjacent temporal lab; keep both scripts in their delivered directory.

## Predict the baseline before running

The twenty-nine baseline cases comprise four accepted limit configurations, three rejected configurations, five guest-ceiling predicates, six total-capacity predicates, four changed-limit predicates, three host-count predicates, and four removal-reason predicates. The rejected configurations assert the specific business-rule type, while direct predicate rows assert the expected broken flag. Both kinds of evidence execute real copied rule code, but they establish different boundaries.

Configuration cases verify that accepted values are preserved and that negative limits or equal configured total and guest limits reject through the expected factory rule. The guest rows distinguish below, equal, and above a positive ceiling; they also characterize zero disabling that upper-bound check and a negative requested value not being rejected by that predicate. These last two rows preserve current behavior rather than endorsing it as a preferred public policy.

Total-capacity rows include exact fit, overflow by one place, null ceiling, the named member's own place, and the creator-plus-party example. The generated harness supplies occupied-place counts directly. It does not call Meeting.GetAllActiveAttendeesWithGuestsNumber. Therefore, passing these rows cannot prove that the aggregate computes or supplies the right total. The chapter's independent aggregate fixture remains necessary for that claim.

Changed-limit rows compare a proposed ceiling below, equal to, and above current occupancy, plus null. Host rows characterize zero, one, and two hosts. Reason rows distinguish null, empty, whitespace-only, and ordinary text. The lab deliberately keeps arithmetic small; it is not an exhaustive range or overflow analysis.

## Commands and expected outcomes

From the .netarchitectureproject root, run the baseline:

```powershell
python -B astraupskill/advanced/extended-course/labs/capacity_lab.py
```

The -B option prevents Python bytecode cache creation for the imported helper. The expected successful result includes a completed build, twenty-nine real rule cases, semantic exit zero, and unchanged hashes for thirteen originals. The application itself targets .NET 8; this generated SDK project is a different, bounded execution environment. Do not report it as a full application build.

Run one mutation at a time when learning:

```powershell
python -B astraupskill/advanced/extended-course/labs/capacity_lab.py --mode broken-capacity-equality
python -B astraupskill/advanced/extended-course/labs/capacity_lab.py --mode broken-guest-zero
python -B astraupskill/advanced/extended-course/labs/capacity_lab.py --mode broken-reason-whitespace
```

The capacity mutation changes the comparison so an exact fit rejects; the expected failure label is capacity equal. The guest mutation makes zero participate in the upper-bound comparison; the expected failure label is zero disables guest ceiling. The reason mutation replaces the empty-string predicate with the whitespace predicate; the expected failure label is whitespace reason characterization. Each mode should compile and then exit one at its intended semantic assertion.

The word broken here means incompatible with the baseline characterization. A product team could intentionally adopt whitespace rejection as a stronger policy. In that case, the specification, implementation, and expected characterization would change together through a reviewed task. A red characterization test identifies a behavior change; it does not settle whether the new policy is desirable.

## Interpret failures by stage

A missing SDK, failed restore, or compiler error is an environmental or experiment problem, not a killed semantic mutation. The runner labels those failures and does not claim a successful behavior check. Mutation replacement requires exactly one matching expression; if source has changed, the script stops rather than silently mutating a different location. Review the current predicate before updating the mutation.

Every run hashes its selected source set before and after. Equality proves preservation of those thirteen originals during that invocation. It does not prove that every application file was unchanged or that preexisting learner edits were absent. The runner never invokes Git, touches a database, or builds the full application. Its temporary directory is uniquely owned and checked before normal cleanup.

If you add another row, first write its contract and expected result independently. Do not generate the expected boolean by copying the exact expression from the rule; that would make the harness agree with the same mistake. A table should distinguish a meaningful comparison boundary or input category. Repeating dozens of ordinary passing values adds less learning value than a single exact-fit row with a clear explanation.

## Review activity

Choose one passing predicate row and explain a bug in Meeting that could still exist despite that row passing. For example, a correct total-capacity predicate can receive an incorrect occupied-place count. Then choose one aggregate worksheet and explain an earlier guard that could prevent its intended rule from being exercised. These two answers connect unit-level arithmetic to fixture-level reachability without collapsing their evidence boundaries.

Finally, prepare a short receipt containing command, build success, semantic result, selected failure label when applicable, and original-hash result. Keep proposed title-policy tests separate: this lab does not implement or validate the new title rule from chapter 12. That independent extension remains a specified learner exercise.
