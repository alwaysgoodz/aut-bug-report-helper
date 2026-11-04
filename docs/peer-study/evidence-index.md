# Team / peer-study preparation evidence

This package prepares a real future study. It does not report human participation, meeting attendance or completed individual contributions.

Tracked preparation: [Issue #16](https://github.com/alwaysgoodz/aut-bug-report-helper/issues/16) / [draft PR #17](https://github.com/alwaysgoodz/aut-bug-report-helper/pull/17), continuing BR-06. Tested tool implementation: [36c7e61467ed6b70f7bf3a0dbc767bcd5ae78bae](https://github.com/alwaysgoodz/aut-bug-report-helper/commit/36c7e61467ed6b70f7bf3a0dbc767bcd5ae78bae). Fixed preparation package: `team-study-ready-v0.1`, with later evidence-only updates.

| Item | Evidence and meaning |
| --- | --- |
| Four supplied names / blank IDs | [Central team data](../team.json); names preserve the supplied case. |
| Equal planned allocation | [40 person-hour plan](../team/work-allocation.zh-CN.md): four people × 10h, 25% each; not verified time. |
| I1/I2 discussion content | [I1 draft](../team/iteration-1-discussion-draft.zh-CN.md), [I2 draft](../team/iteration-2-discussion-draft.zh-CN.md); proposed speaking points/actions, no invented attendance or ratification. |
| Individual statement preparation | [Four named drafts](../a2/individual-statements/README.md); intended work with blank actual-results fields. |
| Executable study | [Protocol](README.md), [tool](../../tools/peer_study.py), [facilitator key](facilitator-key.md); original product measures, predeclared counterbalance and paired exclusions. |
| Tool verification | [14 study-tool checks](../../tests/test_peer_study.py), [two test-only browser pilots](../../tests/browser/peer-study.spec.js); simulations in temporary directories, excluded from human evidence. |
| Current full local Python result | [Log](evidence/python.log): 72 functional pass / 73 discovered, one CI-only bridge skipped. |
| Current browser result | [Log](evidence/browser.log), [raw JSON](evidence/browser-results.json): 18 scenarios, of which two are clearly test-only study-tool pilots. |
| Final tool refinement | [14-check log](evidence/study-tool-final.log): complete reviewer notes retained within bounded form requests; no silent note truncation. |
| Remote verification | [Run 41867826618](https://github.com/alwaysgoodz/aut-bug-report-helper/actions/runs/41867826618), [metadata](evidence/implementation-ci.json), [raw log](evidence/implementation-ci.log): Python 3.11/3.12 pass on 36c7e61; Chromium executes 18 with 0 unexpected/skipped/flaky outcomes. |
| Actual empty-cohort readiness | [Status](evidence/preparation-status.json), [software/environment](evidence/preparation-environment.json), [dashboard](evidence/empty-dashboard.png): test_only=false, 0 consented, 0 submitted, 0 reviewed, medians null, human_study_complete=false. No consent was clicked in this real directory. |
| One local connection interruption | [Log](evidence/connection-abort.log): a full rerun reported WinError 10053 before reading an existing HTTP 415 response. A subsequent 60-request rejection probe and full 73-check run passed. Cause unconfirmed; not counted as a successful run or a proved software fix. |
| Updated PDFs and counts | [A1](../../submission/output/pdf/assignment-1-report-draft.pdf), [A1 count](../../submission/docs/word-count.json); [A2](../../submission-a2/assignment-2-report-draft.pdf), [A2 count](../a2/word-count.json). Both rendered and visually inspected. A2 distinguishes v0.4 application evidence from historical I1/I2 conditions. |

The user chose preparation now, participation later; real study results remain absent. Main application source is unchanged from v0.4; tool tests and report preparation do not imply new student-authored application work. Rendered PDFs remain byte-identical to their committed binary blobs.
