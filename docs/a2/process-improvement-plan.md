# Process improvement: browser acceptance in CI

Established after the I1 experiment and before I2 implementation, 4 November 2026 (Asia/Shanghai).

## Evidence and hypothesis

I1's 34 Python/HTTP tests pass despite a controlled disabled error-focus statement; an ad-hoc browser exercise reveals the failed focus criterion. Hypothesis: adding a committed browser regression suite will detect this particular client-side regression and make the shared acceptance scenarios repeatable in CI.

## Common scenarios fixed for comparison

| ID | Inputs and observable pass condition | I1 evidence mode | I2 planned mode |
| --- | --- | --- | --- |
| C1 | Submit whitespace title, blank severity and nonblank reproduction steps; no report inserted, steps retained, linked error summary receives focus | Ad-hoc MCP browser exercise | Committed Playwright assertion |
| C2 | Submit valid seven-field synthetic report; reload detail; same title/content and exactly one saved report | Ad-hoc MCP browser exercise | Committed Playwright assertion |
| C3 | Existing report moves Open -> In progress -> Resolved -> Open and each page reflects saved state | Ad-hoc MCP browser exercise | Committed Playwright assertion |

Measure (a) number of these scenarios present in executable committed browser regression tests and enabled CI; (b) whether the identical controlled missing-focus mutation is caught automatically; (c) actual run durations as descriptive observations, not a causal speed comparison. Record the exact commits, commands, versions, raw logs and restoration of the mutation. No injected faults remain in deliverables.

## Scope and interpretation

A1 proposed product usability measures (completion time, completeness, independent reproduction). Those answer a product-value question, not this development-process question. We retain that protocol for genuine peers, but introduce these process measures explicitly rather than substituting invented user results. A2 permits a justified measure change.

I2 contains additional features/tests, different browser/runner startup and possibly different browser versions. Compare C1/C2/C3 and the single mutation directly; do not compare overall suite time, test totals or commits as developer productivity. One deliberately chosen mutant cannot establish general defect-detection rates, improved teamwork or reduced escaped defects. The intended conclusion is limited to repeatability and the observed missing-focus regression.
