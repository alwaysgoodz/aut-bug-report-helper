# Current-system refinement evidence

Historical v0.2 record. Later UI-02 fixes and the current requirement audit are in [UI-02 evidence](../ui-review/README.md) and [completion/gap audit](../assessment-audit.zh-CN.md). The measurements below stay bound to their original implementation.

Tracked requirement: [UI-01 / Issue #11](https://github.com/alwaysgoodz/aut-bug-report-helper/issues/11); [draft PR #12](https://github.com/alwaysgoodz/aut-bug-report-helper/pull/12). This is an additional technical refinement after the historical A2 `a2-review-v0.1` candidate, not another claimed team iteration. The original report and results remain unchanged. Codex prepared these changes at the owner's request; real independent teammate review is still required.

## Decisions and observed behavior

The audit found tiny table text, horizontal mobile browsing, unbounded list rendering and different whitespace definitions in Python and JavaScript. The existing local Python/SQLite architecture and teal visual system were retained. There are no new runtime dependencies, remote assets or external data services.

Reports are now rendered 25 per page in stable timestamp/ID order. The service takes the count and page rows in one read transaction, clamps out-of-range pages and uses parameterized filters. Links preserve the active filters; removing a filter resets the page. The unpaged Python API remains available. SQLite indexes support newest-first browsing and combined severity/status filtering; filtering only by status can still scan records, which is acceptable for this small local prototype. Offset pagination is suitable for this scope but cannot promise a fixed cross-request snapshot while reports are concurrently created.

The desktop list becomes readable report cards below 900px, with the same status, severity, date and completeness information. Form sections follow issue, reproduction and context; original field/tab order remains. Missing-information links move focus to the corresponding control, mobile guidance collapses, and status updates receive explicit confirmation. Native form submission and stored guidance remain available without JavaScript. Shared numeric whitespace rules prevent BOM/NEL-only titles and keep browser/server completeness consistent.

## Checks and evidence index

| Evidence | Actual result / purpose |
| --- | --- |
| [Acceptance and measurement plan](plan.md) | Criteria and performance workload fixed before measurement. |
| [Implementation commit 6d9f7dc](https://github.com/alwaysgoodz/aut-bug-report-helper/commit/6d9f7dc172f637828e5f5c5060e058f8befbd7ec) | Committed application and checks used for measurement. |
| [Remote run 41758374584](https://github.com/alwaysgoodz/aut-bug-report-helper/actions/runs/41758374584), [snapshot](evidence/implementation-ci.json), [raw log](evidence/implementation-ci.log) | Both Python 3.11/3.12 jobs pass on 6d9f7dc. Chromium 156: expected=12, unexpected=0, skipped=0, flaky=0. |
| [Python/HTTP log](evidence/refinement-python.log) | 52 functional checks pass; one CI-only browser bridge skipped locally (53 discovered). Persistence, validation, stale updates, headers, Unicode and pagination included. |
| [Browser log](evidence/refinement-browser.log), [raw JSON](evidence/browser-results.json) | 12 scenarios pass using installed Chrome 155 on Windows. Includes keyboard flow, zero/six/seven-field scoring, pagination, 390/768/1440px layouts and no-JavaScript submission. |
| [Isolated responsive check](evidence/refinement-responsive.log) | List, detail and form checks pass on a fresh database. Test now creates its own sample; an earlier isolated attempt exposed a test-order dependency, which was corrected. |
| [Selected contrast measurements](evidence/contrast.json) | 20 computed text/background pairs exceed 4.5:1; minimum 5.46:1. Selected default states only, not complete accessibility certification. |
| [Desktop list](evidence/desktop.png), [tablet list](evidence/tablet.png), [phone list](evidence/mobile.png) | Actual browser captures using fictional demo data. |
| [Desktop form](evidence/form-desktop.png), [tablet form](evidence/form-tablet.png), [phone form](evidence/form-mobile.png) | Actual visual layout inspection. |
| [Desktop detail](evidence/detail-desktop.png), [tablet detail](evidence/detail-tablet.png), [phone detail](evidence/detail-mobile.png) | Actual visual layout inspection. |
| [Raw performance data](evidence/performance.json), [console output](evidence/performance.log) | Clean implementation commit, recorded source hashes/environment, every paginated ID audited and raw request observations preserved. |

`compileall`, JavaScript syntax and `git diff --check` also pass. The responsive check was expanded after the first full browser run; the archived full browser log/JSON were refreshed after that correction.

## Controlled performance result

On Windows 11, Python 3.12.7 and SQLite 3.51.0, with 500 synthetic reports and one client, five warmups preceded 50 full-body requests rotating across 20 pages. All 500 expected IDs appeared exactly once in the page audit. Each measured response contained 25 rows and 38,156–38,182 bytes. Median latency was 21.9976 ms, p95 33.1509 ms, and maximum 33.2962 ms; the predeclared p95 <250 ms target was met.

The measured source is `6d9f7dc172f637828e5f5c5060e058f8befbd7ec`, with an empty working-tree status before measurement. The later evidence/package commit changes documentation and archived evidence only. This is a warm-cache, local single-client experiment. It does not establish concurrent-load or network performance. The historical 77.8756 ms p95 returned 500 rows in one response, so a direct speedup ratio would be misleading.

## Reproduce

Check out technical candidate `a2-review-v0.2` (or branch `feat/ui-quality-refinement`) and follow the root README. Use `python -m unittest discover -s tests -v`, `npm ci`, `npx playwright install chromium`, then `npm run test:browser`. For the documented local fallback set `BUGREPORT_BROWSER_CHANNEL=chrome` and a verified `BUGREPORT_PYTHON`. Run `python -m tools.measure_quality --output tmp/performance-recheck.json` to retain archived measurements. Use the full implementation SHA above for the exact measured commit.

Tests establish the listed technical behavior; they do not establish usability-study outcomes or real peer collaboration. PR #12 is a review proposal, not an approval. The v0.2 technical candidate supplements the historical v0.1 report; the team must reconcile report claims and add genuine review/evaluation evidence before final assessment submission.
