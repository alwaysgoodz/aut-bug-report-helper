# Team / peer-study preparation evidence

This package prepares a real future study. It does not report human participation, meeting attendance or completed individual contributions.

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
| One local connection interruption | [Log](evidence/connection-abort.log): a full rerun reported WinError 10053 before reading an existing HTTP 415 response. A subsequent 60-request rejection probe and full 73-check run passed. Cause unconfirmed; not counted as a successful run or a proved software fix. |
| Updated PDFs and counts | [A1](../../submission/output/pdf/assignment-1-report-draft.pdf), [A1 count](../../submission/docs/word-count.json); [A2](../../submission-a2/assignment-2-report-draft.pdf), [A2 count](../a2/word-count.json). Both rendered and visually inspected. A2 distinguishes v0.4 application evidence from historical I1/I2 conditions. |

The implementation commit, actual remote CI and empty real-cohort readiness snapshot are added after verification. The user chose preparation now, participation later; real study results remain absent.
