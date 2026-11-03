# Assignment 2 evidence index

Repository is private. Evidence records AI-assisted technical preparation; real member approvals and collaboration are not inferred. The fixed technical review reference is `a2-review-v0.1` once published; it is not the final approved assessment submission.

| Evidence | Fixed or activity link | What it establishes |
| --- | --- | --- |
| Requirements | [Issues #1–6](https://github.com/alwaysgoodz/aut-bug-report-helper/issues), [traceability](traceability.md), [backlog](../backlog.md) | Original priorities/criteria and implementation/test mapping. |
| A1 proposal | [PR #7](https://github.com/alwaysgoodz/aut-bug-report-helper/pull/7) | Preserved baseline; independent approval pending. |
| I1 proposal and snapshot | [PR #8](https://github.com/alwaysgoodz/aut-bug-report-helper/pull/8), [cee24aaa908991a9ff38967bfc2a46f973493934](https://github.com/alwaysgoodz/aut-bug-report-helper/commit/cee24aaa908991a9ff38967bfc2a46f973493934) | Browser core/status increment; unmerged and unreviewed by real peers. |
| I2 proposal and implementation | [PR #10](https://github.com/alwaysgoodz/aut-bug-report-helper/pull/10), [f36dfc792c4467c0726598cce401629f7a9e7fe5](https://github.com/alwaysgoodz/aut-bug-report-helper/commit/f36dfc792c4467c0726598cce401629f7a9e7fe5) | Completeness/filtering and browser-gate implementation used for measurement. |
| I1 remote checks | [Run 41677785458](https://github.com/alwaysgoodz/aut-bug-report-helper/actions/runs/41677785458), [snapshot](evidence/i1-ci.json), [log](evidence/i1-ci.log) | Python 3.11/3.12 acceptance/compile success on I1 SHA. |
| I2 remote checks | [Run 41680263474](https://github.com/alwaysgoodz/aut-bug-report-helper/actions/runs/41680263474), [snapshot](evidence/i2-ci.json), [log](evidence/i2-ci.log) | Both Python jobs pass. 3.12 actually executes seven Chromium browser cases: expected=7, unexpected=0, skipped=0, flaky=0. |
| Local checks | [Python](evidence/i2-python.log), [browser raw JSON](evidence/i2-browser-report.json), [browser log](evidence/i2-browser.log) | 43 functional tests plus one locally skipped CI-only bridge; seven local Chrome browser cases pass. |
| I1 browser exercise | [C1/C2/C3 observations](evidence/i1-browser.json), [I1 screenshot](evidence/i1-reports.png) | Ad-hoc MCP exercise, not a saved regression suite or human evaluation. |
| I1 fault evidence | [observation](evidence/i1-focus-mutant.json), [34-check log](evidence/i1-focus-mutant-tests.log) | Disabled focus escapes automated Python checks; browser focus criterion fails. Original restored. |
| Improvement requirement and prospective plan | [PI-01 #9](https://github.com/alwaysgoodz/aut-bug-report-helper/issues/9), [plan](process-improvement-plan.md) | Common scenarios/measures fixed before I2. |
| I2 controlled experiment | [result](evidence/i2-focus-mutant.json), [intended failure log](evidence/i2-focus-mutant.log), [raw browser JSON](evidence/i2-focus-mutant-browser.json) | Same focus regression caught by intended assertion; original bytes restored. One targeted mutation, not general effectiveness. |
| Quality measurement | [prospective quality plan](quality-plan.md), [raw performance JSON](evidence/performance.json), `python -m tools.measure_quality` | Clean I2 SHA, 500 reports, 50 samples after 5 warmups, recorded environment/hashes; p95 77.8756 ms against predeclared <250 ms target. |
| Iteration records / technical retrospectives | [I1](iteration-1.md), [I2](iteration-2.md), [changes](changes.md) | Actual implementation decisions and observations, with pending human discussions clearly identified. |
| Product screenshots | [list/filter view](evidence/i2-reports.png), [live guidance form](evidence/i2-form.png) | Actual browser captures with fictional seeded data; inspect at original resolution. |
| Demonstration / individuals | [demo runbook](demo-runbook.md), [statement templates](individual-statements/README.md), [A1 ledger](../contributions.md) | Preparation materials; identities, actual activities and real presentation still pending. |

## Reproduce the measured implementation

Clone and check out `f36dfc792c4467c0726598cce401629f7a9e7fe5` for the exact implementation measurement, or the later fixed `a2-review-v0.1` tag for code plus report materials. Follow the README. Local browser checks may explicitly use installed Chrome if CDN installation fails; record the version. The CI uses its downloaded Chromium and preserves its output in the linked run/log.

Do not treat the intentionally failing mutant log as a failing delivered build. Verify `caught_by_focus_assertion=true`, `original_restored=true`, then the full-suite success evidence. The original failed harness filter is preserved separately and is not counted as a caught mutant.

## Remaining assessed evidence

Real non-author review and author response; actual iteration teamwork/retrospectives; four member identities and genuine linked contribution statements; planned product study or explicit justified omission; assessor access; team-approved final submission SHA/tag. The present review candidate and technical logs cannot establish these.
