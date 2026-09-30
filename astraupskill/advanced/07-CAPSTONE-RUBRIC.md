# Capstone: ship a rule with a reviewable rejection contract

Your learner capstone is the proposed title rule, developed in a disposable copy and reviewed as though another engineer must maintain it. The change is complete only when the rule has a precise policy, every intended entry point applies it, and rejected changes preserve the aggregate's state. A list of passing tests without a boundary argument is not enough.

Submit five artifacts. First, a short domain decision explains trimmed length, null handling, storage normalization, and why the limits are business requirements for the exercise. Second, a mapping diagram identifies where command data becomes a domain value or aggregate argument. Third, a table of boundary examples includes both acceptance and rejection. Fourth, a full-state rejection projection accounts for every declared Meeting field plus inherited domain events. Fifth, a command/evidence note separates domain lab results, full handler tests, and untested persistence or presentation boundaries.

The reviewer should be able to reproduce an intentional failure: move the new check after an assignment in the learner copy, or replace exact mapping with a different but still positive end. The corresponding test must fail for the expected semantic reason. A failure to compile, a missing restore asset, or a reflection type-name error does not demonstrate that the invariant test would catch the regression. Include those infrastructure failures if encountered, but label them accurately.

| Dimension | Points | Acceptance evidence |
|---|---:|---|
| Domain policy | 15 | Explicit null, trimming, inclusive length boundaries and storage choice |
| Correct boundary placement | 20 | Create/change consistency; validation before mutation; no handler-only bypass |
| Successful mapping | 15 | Asymmetric requested values arrive exactly at the intended aggregate |
| Rejection integrity | 25 | All fields, nested state and events unchanged; no inappropriate repository add |
| Test diagnostics | 15 | Semantic mutation detected; reflection/setup failures distinguished |
| Reproducibility and limits | 10 | Exact commands, owned/disposable artifacts, honest untested boundaries |

An eighty-point score is a useful target, but critical failures override it. Examples are changing the production source to run a demonstration without isolating the change, silently deleting existing domain events, validating only one entry point, using a shallow reference snapshot that changes with the aggregate, or reporting a console adapter result as a full handler/persistence integration pass.

The capstone review should include a counterexample discussion. Ask a partner to propose a field that could change without breaking your assertion. If the field is excluded, justify the exclusion through an independent invariant or extend the projection. Then ask how a future refactor from private fields to another representation would affect the test. An explicit observation helper can localize that coupling, but it must not hide meaningful state merely to reduce maintenance.

For optional further work, specify a persistence-level test and an HTTP-level test rather than implementing them automatically. The former would need an actual repository/unit-of-work boundary and a failure at the appropriate transaction point. The latter would establish an error contract for clients. Neither should be inferred from the current repository substitutes. This distinction helps keep a focused domain change small while still identifying the evidence needed for a broader release claim.

Finish by comparing your first MA-01 classification to the final evidence packet. State exactly which claims became demonstrated and which remain proposals. That last comparison is the practical outcome of the workshop: a stronger rule, a stronger rejection test, and a narrower, more trustworthy explanation of what the tests establish.

[Advanced index](README.md)
