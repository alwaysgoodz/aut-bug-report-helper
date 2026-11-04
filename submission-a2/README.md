# Assignment 2 technical review package

This updated draft covers the supplied names and planned 25% allocations, current v0.4 application behavior/checks and explicitly historical I1/I2/process/performance evidence. [Study tools](../docs/peer-study/README.md) are prepared, with no real participant results. Discussion drafts and individual allocations are not completed human activity. IDs/accounts are intentionally blank.

- [Group evaluation report PDF draft](assignment-2-report-draft.pdf)
- [Editable report](assignment-2-report.md) and [structured source](../docs/a2/report-content.json)
- [Evidence index](../docs/a2/evidence-index.md), [traceability](../docs/a2/traceability.md), [word count](../docs/a2/word-count.json)
- [I1 record](../docs/a2/iteration-1.md), [I2 record](../docs/a2/iteration-2.md), [decisions/changes](../docs/a2/changes.md)
- [Ten-minute demo runbook](../docs/a2/demo-runbook.md), [individual statement template](../docs/a2/individual-statements/template.md)
- [Chinese handoff and marking alignment](../docs/a2/handoff.zh-CN.md)

The report contains 1,921 whitespace words / 2,081 conservative tokens, including tables and citations, under the 2,500-word cap. Supporting appendices and separate individual statements are excluded under the supplied brief. Recount after genuine team material is added.

The fixed `team-study-ready-v0.1` tag packages preparation; historical application tags remain preserved. It preserves runnable software, names and planned allocations; real independent approval, student/account details, actual contributions, team meetings and product evaluation remain pending. Generated preparation does not establish those activities.

The application has no third-party Python runtime dependency. Optional PDF regeneration uses Windows Calibri, `reportlab` and `PyMuPDF`: `python -m tools.build_a2_report`. Inspect every newly rendered page under `tmp/a2-report-render` before delivering a changed PDF.
