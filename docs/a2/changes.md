# Significant decisions and changes from A1

| Decision | Reason and effect | Evidence |
| --- | --- | --- |
| Proposed calendar: two two-working-day iterations plus a final preparation day in Week 2 | A2 explicitly requires both iterations in Week 2; A1's tentative five days each would not fit. Capacity remains a proposed 20 person-hours per iteration, subject to actual members. Preparation increments in this session are not that calendar history. | Supplied A2 brief; backlog schedule correction |
| Add process measures alongside the planned product study | Completion time/completeness/reproduction concern product value. PI-01 instead needs repeatable browser scenarios and targeted fault detection. No genuine peer outcomes are available, so the study remains unrun. | Prospective process-improvement plan before I2 |
| Test-only Playwright dependency with lockfile | Python/HTTP tests do not run browser JavaScript; the I1 missing-focus mutant escaped that suite. App runtime stays standard-library-only. Node/Chromium setup increases CI cost and is reported as a trade-off. | I1/I2 experiment logs; package-lock.json; workflow |
| Guard stale updates, restrict local hosting and bound inputs | These acceptance/security safeguards support the existing small local scope; they do not introduce authentication or remote collaboration. | Lifecycle/HTTP checks and quality plan |
| Preserve stacked unmerged review proposals | Actual peers are unknown and cannot independently review via the owner account. Preserve A1 -> I1 -> I2 for substantive review and eventual approved integration. | PRs and contribution ledger |
| Run browser acceptance through the existing Python 3.12 CI entry | GitHub rejected the initial push because the OAuth token lacks workflow-file write scope. The unpushed local commit was revised; the shared workflow stays unchanged. A conditional CI bridge installs locked test dependencies and runs the browser suite once. This couples browser setup to one Python job; a separate job would be clearer if workflow permission is later available. No token or account permission was changed. | `tests/test_browser_ci.py`, remote logs |

No AI diagnosis, automatic fixing, external tracker integration, mobile application, advanced analytics or public deployment was added. Those A1 exclusions remain.
