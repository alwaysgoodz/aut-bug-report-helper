# UX-01: interaction feedback and accessible motion

The owner requested further usability optimisation and dynamic effects. [Issue #18](https://github.com/alwaysgoodz/aut-bug-report-helper/issues/18) records the acceptance criteria for this follow-up. It was opened during implementation, not presented as an earlier team decision. The change is stacked on the named-team preparation branch and awaits independent review.

## What changed and why

The audit found that pending native submissions only dimmed a button, progress jumped between values and selected status transitions had no preview. The existing teal palette, responsive layout, semantic form fields and dependency-free Python/vanilla-JavaScript stack are retained.

Page headings and main content enter with small transform/opacity transitions. Interactive arrows and buttons provide brief hover/pressed feedback. A form section receives an accent while one of its controls is focused. The seven-field score and native progress value update immediately; a separate, aria-hidden visual fill smoothly retargets with each presence change. Score feedback occurs only when the percentage changes, not on every keystroke. No animation delays input, saving or navigation.

Create/status/filter submissions show explicit pending labels and a loading indicator. Submit buttons are disabled and their minimum width retained during the native request. The browser's `pageshow` event restores their nodes, labels, width and availability; status controls still disable an unchanged selection. Status help previews the selected transition and reminds the user to save. Existing success notices remain server-confirmed, never optimistic results.

Reduced-motion preferences disable CSS animations/transitions and cancel JavaScript feedback, including when changed during use. Static pending labels and progress remain available. Native progress, details, links and forms continue to work without JavaScript. No new runtime or development dependency was introduced.

## Verification and evidence

| Acceptance area | Evidence / result |
| --- | --- |
| Rapid field edits | [New browser scenarios](../../tests/browser/interaction-motion.spec.js): exact 43%/29% semantic values, visible missing fields and final visual scale agree after interrupted edits. |
| Pending create / filters | Real native submissions are intercepted and held before the response. A read-only submit-event observer captures labels, disabled/busy state and button width; the request is then released. History return restores a usable action and form values. |
| Status preview | Selecting In progress from Open shows the pending transition; returning to Open disables Update. Existing full status-cycle checks still pass. |
| Reduced motion | Phone viewport, initial reduced preference and live switch: zero running animations, accurate progress, working keyboard disclosure and no horizontal overflow. |
| Full browser regression | [Log](evidence/browser.log), [raw JSON](evidence/browser-results.json): **22 pass**, 0 unexpected/skipped/flaky outcomes, no retry. Includes 16 earlier app scenarios, four UX-01 scenarios and two explicitly test-only study pilots. |
| Python checks | [Log](evidence/python.log): **72 functional pass / 73 discovered**; local CI-only browser bridge skipped once. Includes 14 study-tool checks. |
| Visual inspection | [Before](evidence/before.png), [desktop](evidence/desktop.png), [phone](evidence/phone.png): actual local browser screenshots. Desktop 1440×1000, phone 390×844; fields and score remain readable. Screenshots show settled states, not proof of animation timing. |
| Static checks | `node --check bugreport/static/app.js`, `python -m compileall -q bugreport tests tools`, `git diff --check`. |

Initial test-harness attempts read an in-progress focus colour too soon or tried to query a document while native navigation was pending. The final tests wait for the final colour and capture pending feedback synchronously at the real submit event, then release a held network response. Those attempts are not product failures counted as passes. Exploratory logs remain under ignored `tmp`; the table links the complete final regression.

## Version and assessment limits

The earlier `team-study-ready-v0.1` tag preserves its original guided condition and the existing A1/A2 PDFs retain their stated v0.4 scope. This UI change affects the guided condition; do not combine outcomes collected on different sources. The real local cohort had no participants or trials and its server was paused before editing source. Restart the empty cohort on the committed UX version and retain its source fingerprint before recruitment. A non-empty dataset must retain its original source or use a separate cohort.

This remains preparation and technical verification, not human product-evaluation results, student contributions or a completed independent review. No improvements in task completion time or user satisfaction are claimed. Movement was checked in local Chrome and the CI Chromium target; other browser engines have not been verified.
