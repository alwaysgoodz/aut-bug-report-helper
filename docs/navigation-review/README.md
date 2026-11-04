# UI-03 history, context and input validation follow-up

Requirement: [Issue #15](https://github.com/alwaysgoodz/aut-bug-report-helper/issues/15). Continues [PR #14](https://github.com/alwaysgoodz/aut-bug-report-helper/pull/14); fixed `a2-review-v0.3` remains unchanged. These are AI-assisted technical fixes, not an additional claimed human team iteration.

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
| [Restored form screenshot](evidence/restored-form.png) | Actual preview after browser Back with retained fields and 43% score. Fictional, unsaved text. |

Compile, JavaScript syntax and diff checks pass. The committed implementation, environment and actual remote results are recorded in the follow-up evidence commit once available. No runtime dependency or visual-system change was introduced. All automated write tests use temporary databases.

## Submission status

Use the root README for the latest fixed candidate and setup. [A1/A2 completion audit](../assessment-audit.zh-CN.md) remains the submission checklist. Technical regression evidence does not supply real members, independent review, retrospectives, individual contribution statements, assessor access or the scheduled demonstration.
