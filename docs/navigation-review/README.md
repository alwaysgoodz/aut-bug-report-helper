# UI-03 history, context and input validation follow-up

Requirement: [Issue #15](https://github.com/alwaysgoodz/aut-bug-report-helper/issues/15). Continues [PR #14](https://github.com/alwaysgoodz/aut-bug-report-helper/pull/14); fixed `a2-review-v0.3` remains unchanged. These are AI-assisted technical fixes, not an additional claimed human team iteration.

Tested implementation: [8a0f4bbc3bc28ee1925513b4d599a5e9dad54458](https://github.com/alwaysgoodz/aut-bug-report-helper/commit/8a0f4bbc3bc28ee1925513b4d599a5e9dad54458). Fixed package: `a2-review-v0.4`, a later documentation/evidence commit with the same application source.

## Observed problems and changes

Browser Back restored form text and severity but left completeness at 0%. The regression first failed on v0.3. The form now recomputes score, progress, missing items and the code-point counter on pageshow, with a deferred update for history restoration after event dispatch. No application draft-storage service was added; this synchronises values that the browser restores.

Detail links previously discarded the active severity/status/page context. A validated, structured context now follows list → detail → status update or conflict → Back to reports. Native links/forms support this without JavaScript. Explicit global navigation still opens the full list. A status change can remove a report from its original filter; returning shows the updated filtered data and retains the requested page, subject to existing last-page clamping.

Only allowed severity/status and positive page values are carried. Duplicate/invalid parameters are rejected before mutation. No arbitrary return URL is accepted; an attempted external return parameter does not affect the local redirect.

Null characters could cause an unhandled SQLite title constraint, while optional fields could persist unusable text. They now produce field-specific validation errors before writes; other form values remain available and the HTTP server stays healthy. Existing stored data is not rewritten.

## Evidence index

| Evidence | Result |
| --- | --- |
| [Browser before fix](evidence/browser-before.log) | History-score and detail-context checks fail on v0.3. |
| [HTTP before fix](evidence/http-before.log) | Missing context and unvalidated navigation parameters are detected. |
| [Null-input before fix](evidence/null-before.log) | Title causes SQLite error; five optional-field reports are inserted, violating the new validation criterion. |
| [Initial harness error](evidence/initial-harness-error.log) | First test used a combined subTest/assertRaises context incorrectly; corrected before interpreting null-input evidence. This harness error is not counted as a product finding. |
| [Python/HTTP](evidence/python.log) | 57 functional checks pass; one CI-only bridge skipped locally (58 discovered). |
| [Browser log](evidence/browser.log), [raw JSON](evidence/browser-results.json) | 16 pass with installed Chrome 155; includes real Back traversal, page-2 detail/status return, JS-disabled return, Unicode, keyboard and responsive regressions. |
| [Remote CI 41854085423](https://github.com/alwaysgoodz/aut-bug-report-helper/actions/runs/41854085423), [metadata](evidence/implementation-ci.json), [log](evidence/implementation-ci.log) | Python 3.11/3.12 pass on 8a0f4bb; Chromium 156 executes all 16 browser cases with 0 unexpected, skipped or flaky results. |
| [Environment and source hashes](evidence/environment.json) | Python 3.12.7 / SQLite 3.51.0 / Node 22.22.1 on Windows 11. Both local and canonical Git source hashes are retained because line-ending normalisation can change bytes between platforms. |
| [Restored form screenshot](evidence/restored-form.png) | Actual preview after browser Back with retained fields and 43% score. Fictional, unsaved text. |

Compile, JavaScript syntax and diff checks pass. Source and actual CI results are fixed above. No runtime dependency or visual-system change was introduced. All automated write tests use temporary databases. The form screenshot was recaptured with focus blurred and scroll reset to zero to avoid a full-page capture offset of fixed/sticky elements.

## Submission status

Use the root README for the latest fixed candidate and setup. [A1/A2 completion audit](../assessment-audit.zh-CN.md) remains the submission checklist. Technical regression evidence does not supply real members, independent review, retrospectives, individual contribution statements, assessor access or the scheduled demonstration.
