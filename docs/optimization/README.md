# Current-system refinement evidence

Tracked requirement: [UI-01 / Issue #11](https://github.com/alwaysgoodz/aut-bug-report-helper/issues/11). This is an additional technical refinement after the historical A2 `a2-review-v0.1` candidate, not another claimed team iteration. The original report and results remain unchanged. Codex prepared these changes at the owner's request; real independent teammate review is still required.

## Decisions and observed behavior

The audit found tiny table text, horizontal mobile browsing, unbounded list rendering and different whitespace definitions in Python and JavaScript. The existing local Python/SQLite architecture and teal visual system were retained. There are no new runtime dependencies, remote assets or external data services.

Reports are now rendered 25 per page in stable timestamp/ID order. The service takes the count and page rows in one read transaction, clamps out-of-range pages and uses parameterized filters. Links preserve the active filters; removing a filter resets the page. The unpaged Python API remains available. SQLite indexes support newest-first browsing and combined severity/status filtering; filtering only by status can still scan records, which is acceptable for this small local prototype. Offset pagination is suitable for this scope but cannot promise a fixed cross-request snapshot while reports are concurrently created.

The desktop list becomes readable report cards below 900px, with the same status, severity, date and completeness information. Form sections follow issue, reproduction and context; original field/tab order remains. Missing-information links move focus to the corresponding control, mobile guidance collapses, and status updates receive explicit confirmation. Native form submission and stored guidance remain available without JavaScript. Shared numeric whitespace rules prevent BOM/NEL-only titles and keep browser/server completeness consistent.

## Checks and evidence index

| Evidence | Actual result / purpose |
| --- | --- |
| [Acceptance and measurement plan](plan.md) | Criteria and performance workload fixed before measurement. |
| [Python/HTTP log](evidence/refinement-python.log) | 52 functional checks pass; one CI-only browser bridge skipped locally (53 discovered). Persistence, validation, stale updates, headers, Unicode and pagination included. |
| [Browser log](evidence/refinement-browser.log), [raw JSON](evidence/browser-results.json) | 12 scenarios pass using installed Chrome 155 on Windows. Includes keyboard flow, zero/six/seven-field scoring, pagination, 390/768/1440px layouts and no-JavaScript submission. |
| [Isolated responsive check](evidence/refinement-responsive.log) | List, detail and form checks pass on a fresh database. Test now creates its own sample; an earlier isolated attempt exposed a test-order dependency, which was corrected. |
| [Selected contrast measurements](evidence/contrast.json) | 20 computed text/background pairs exceed 4.5:1; minimum 5.46:1. Selected default states only, not complete accessibility certification. |
| [Desktop list](evidence/desktop.png), [tablet list](evidence/tablet.png), [phone list](evidence/mobile.png) | Actual browser captures using fictional demo data. |
| [Desktop form](evidence/form-desktop.png), [phone form](evidence/form-mobile.png), [desktop detail](evidence/detail-desktop.png), [phone detail](evidence/detail-mobile.png) | Actual visual layout inspection. |

`compileall`, JavaScript syntax and `git diff --check` also pass. The responsive check was expanded after the first full browser run; the archived full browser log/JSON were refreshed after that correction.

## Reproduce

Check out `feat/ui-quality-refinement` and follow the root README. Use `python -m unittest discover -s tests -v`, `npm ci`, `npx playwright install chromium`, then `npm run test:browser`. For the documented local fallback set `BUGREPORT_BROWSER_CHANNEL=chrome` and a verified `BUGREPORT_PYTHON`. Run `python -m tools.measure_quality --output tmp/performance-recheck.json` to retain archived measurements.

Remote CI and the controlled performance measurement are recorded in the follow-up evidence commit, against the committed implementation. Tests establish the listed technical behavior; they do not establish usability-study outcomes or real peer collaboration.
