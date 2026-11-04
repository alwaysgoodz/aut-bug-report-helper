# UI-02 defect fixes and assessment audit

Requirement: [Issue #13](https://github.com/alwaysgoodz/aut-bug-report-helper/issues/13). Parent technical candidate: `a2-review-v0.2`. Original A1/I1/I2 and v0.2 snapshots are preserved. This is AI-assisted preparation, not another claimed four-person iteration or independent approval.

The [Chinese requirement-by-requirement audit](../assessment-audit.zh-CN.md) covers product scope, each A1/A2 marking criterion, submission items, actual repository participation and remaining work. It separates official requirements from the project's own peer-study commitment and optional expansion.

## Defects and design changes

At 901px/1120px the Completeness header exceeded its column content area; checking only document overflow missed this. New regression checks inspect actual text boundaries. Column ratios, padding and sentence-case labels now keep headers readable. Summary icons, spacing and form groups retain the established teal system and local assets; detail links have 44×44px targets.

HTML maxlength uses UTF-16 units while Python uses Unicode code points, silently truncating valid supplementary Unicode. Text controls now defer exact limits to the server, and the live title counter uses code points with an over-limit state. A 161-character title gets an error with retained input; 160 emoji persist with JavaScript enabled or disabled. Stored field limits remain unchanged; grapheme clusters are not the counting unit.

A maximum valid form exceeded the old 64KB transport limit after encoding. The finite 249,088-byte bound derives from declared limits, worst-case UTF-8 percent encoding and overhead. Field limits, CSRF, timeout and other rejection checks remain. The new HTTP scenario saves and verifies every field of a maximal Unicode report.

Form guidance uses short linked labels instead of repeating long explanations. Field-side help remains visible; saved-detail guidance keeps full text. Below 1280px guidance precedes the form and collapses; at short viewport heights the aside does not stick. Nested scroll clipping is removed. Native submission remains available.

## Evidence index

| Evidence | Observation |
| --- | --- |
| [Browser before fix](evidence/browser-before-fix.log), [HTTP before fix](evidence/http-before-fix.log) | Three added browser checks fail on v0.2 as intended; a legal maximum Unicode form returns 413 instead of 303. These are pre-fix failures. |
| [Python/HTTP](evidence/python.log) | 53 functional tests pass; one CI-only bridge skipped locally (54 discovered). |
| [Browser log](evidence/browser.log), [raw JSON](evidence/browser-results.json) | 15 checks pass locally using installed Chrome 155; Unicode JS/native, breakpoint headers, low-height guidance, keyboard, persistence, scoring and filters. |
| [Before form](evidence/form-before.png), [desktop](evidence/desktop.png), [form](evidence/form-desktop.png), [1120px form](evidence/form-tablet.png), [phone](evidence/mobile.png) | Actual browser captures with fictional demo data, not user evaluation. |
| [GitHub participation snapshot](evidence/collaboration-snapshot.json) | Recorded owner only, no pending invites, no reviews on PR #7/#8/#10/#12. |

Python compile, JS syntax and diff checks also pass. Remote CI and fixed source are linked in the follow-up evidence commit once they exist. Browser checks do not establish full accessibility certification. Only Chromium-family browsers have been tested.

## Version and submission boundary

Current branch: `fix/ui-defects-and-assessment-audit`. Follow the root README; checks isolate their databases. Existing PDFs describe v0.1 and are explicitly historical drafts. Use the audit to reconcile the final software/report reference; real identities, contributions, retrospectives, review and assessor access remain pending.

Earlier paginated p95 33.1509ms belongs to 6d9f7dc; p95 77.8756ms belongs to f36dfc7 and a 500-row response. Neither is a new measurement of this fix; differing workloads prevent a speedup-ratio claim. Current quality evidence includes the new input-integrity regression in Windows/Python 3.12 and browser regressions.
