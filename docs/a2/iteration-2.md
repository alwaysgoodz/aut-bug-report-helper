# Iteration 2: completeness, filtering and repeatable browser acceptance

Date: 4 November 2026 (Asia/Shanghai). Second AI-assisted implementation increment in the preparation session. No claim of actual four-person, two-day work or completed human retrospective.

## Goal, requirements and responsibilities

Deliver BR-04 and BR-05 and implement PI-01 from I1's observed testing gap. BR-04 requires 0/86/100 scoring boundaries, exact missing fields and nonblocking optional information. BR-05 requires severity/status AND, clear and empty-state behaviour without mutating storage. PI-01 requires the fixed C1/C2/C3 browser scenarios in executable tests/CI and automatic detection of the same disabled-focus mutation.

Proposed roles B (guidance/UI), C (filter/storage) and D (tests/CI), with non-author reviewers, remain subject to real member assignment. Codex performed implementation and technical experiments through the owner account; teammate review is pending.

## Implemented outcomes and observations

- Pure Python completeness rules and progressive JavaScript agree on the seven fields; metadata does not increase the score. Both the new form and saved detail explain the score's limits. No runtime network/font/package dependency was added.
- Combined GET filters, explicit no-match state and Clear are implemented; service and HTTP checks verify filtering cannot mutate reports.
- 43 Python/HTTP test methods pass. Seven committed browser tests pass, including C1/C2/C3, live/saved score consistency, filters, keyboard-only form completion and a 390px layout/stored-markup check. Raw logs and JSON results are in `evidence/`.
- Missing-focus mutation is caught at `toBeFocused`; original bytes restored, then the unmodified full browser suite passes. [Experiment](evidence/i2-focus-mutant.json). I1's automated Python checks did not detect this same targeted fault. This establishes a specific detection and repeatability improvement, not a general quality/defect-reduction rate.
- Experiment-harness corrections: an anchored grep matched no full Playwright test title; changed it to the C1 marker. The HTML reporter cleared a JSON report written inside its own folder; moved machine-readable output to `test-results/browser-results.json`. The initial harness error log is preserved. These tooling corrections are not teammate review findings.
- The local Chromium download was interrupted by the remote CDN after partial transfer; the documented installed-Chrome fallback was used for local checks. Version is printed in logs. CI uses the locked Playwright Chromium installation, so its results are recorded separately.
- GitHub denied workflow edits under the current OAuth scope. The unpushed local commit was revised to retain the shared workflow and add a conditional `test_browser_ci.py` bridge in its existing Python 3.12 job. Local unittest runs therefore show 43 functional checks plus one skipped CI-only entry. The remote 3.12 job must execute that entry and the seven browser checks successfully; a skipped local bridge is not evidence of remote browser success.

## Retrospective and next action

Keep service/HTTP checks for fast feedback and browser checks for behaviour that those layers cannot observe. Keep JSON/HTML output in separate directories and fail the mutation helper unless the intended assertion, not an unrelated runner error, fails. Next add a small diverse mutant set if the team needs broader test-effectiveness evidence; do not inflate conclusions from this single chosen example. A real team must discuss the trade-off between added CI browser setup and the detected regression.

Performance and security conditions are fixed in [quality plan](quality-plan.md); exact measured results, implementation SHA and remote run links are added to the evidence index once produced. The four-peer product study and real contribution statements remain incomplete.
