# Assignment 2 traceability and evidence status

All links are in the private repository. Exact final snapshots and remote runs will be added after they exist. Implementation is AI-assisted preparation; no actual human approval or individual contribution is inferred.

| Requirement | Implementation | Automated acceptance | Iteration / review proposal |
| --- | --- | --- | --- |
| [BR-01 #1](https://github.com/alwaysgoodz/aut-bug-report-helper/issues/1) | `bugreport/service.py`, CLI | `test_creation.py`, C2 | A1 PR #7, review pending |
| [BR-02 #2](https://github.com/alwaysgoodz/aut-bug-report-helper/issues/2) | `web.py`, `views.py`, local CSS/JS | `test_web.py`; C1/C2, keyboard, narrow-screen browser checks | [I1 PR #8](https://github.com/alwaysgoodz/aut-bug-report-helper/pull/8), review pending |
| [BR-03 #3](https://github.com/alwaysgoodz/aut-bug-report-helper/issues/3) | `ReportStore.update_status`, detail form | lifecycle/HTTP tests, C3; stale update rejection | I1 PR #8, review pending |
| [BR-04 #4](https://github.com/alwaysgoodz/aut-bug-report-helper/issues/4) | `rules.py`, progressive form guidance | `test_guidance_filters.py`, BR-04 browser 0/86/100 boundaries | [I2 PR #10](https://github.com/alwaysgoodz/aut-bug-report-helper/pull/10), review pending |
| [BR-05 #5](https://github.com/alwaysgoodz/aut-bug-report-helper/issues/5) | parameterised service list, GET filters | filter/HTTP cases, BR-05 browser AND/empty/clear | I2 PR #10, review pending |
| [BR-06 #6](https://github.com/alwaysgoodz/aut-bug-report-helper/issues/6) | CI, quality measurement, docs | Python/HTTP checks, browser regression, raw performance timings | Technical checks implemented; real four-peer product evaluation pending |
| [PI-01 #9](https://github.com/alwaysgoodz/aut-bug-report-helper/issues/9) | committed browser tests + CI | same C1/C2/C3; controlled missing-focus mutation | [Prospective plan](process-improvement-plan.md), I1 observations preserved |

The measured process change does not replace the genuine team retrospective, peer review, four-person study or individual statements. See the A1 contribution ledger and I1 record for those unresolved requirements.
