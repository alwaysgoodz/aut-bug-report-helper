# Assignment 2 technical review package

- [Group evaluation report PDF draft](assignment-2-report-draft.pdf)
- [Editable report](assignment-2-report.md) and [structured source](../docs/a2/report-content.json)
- [Evidence index](../docs/a2/evidence-index.md), [traceability](../docs/a2/traceability.md), [word count](../docs/a2/word-count.json)
- [I1 record](../docs/a2/iteration-1.md), [I2 record](../docs/a2/iteration-2.md), [decisions/changes](../docs/a2/changes.md)
- [Ten-minute demo runbook](../docs/a2/demo-runbook.md), [individual statement template](../docs/a2/individual-statements/template.md)
- [Chinese handoff and marking alignment](../docs/a2/handoff.zh-CN.md)

The report contains 1,889 whitespace words / 2,050 conservative tokens, including tables and citations, under the 2,500-word cap. Supporting appendices and separate individual statements are excluded under the supplied brief. Recount after genuine team material is added.

The fixed `a2-review-v0.1` tag is a technical preparation candidate. It preserves runnable software and evidence; real independent approval, member identities/contributions, team retrospectives and product evaluation remain pending. Do not submit generated preparation as evidence that four students already completed those activities.

The application has no third-party Python runtime dependency. Optional PDF regeneration uses Windows Calibri, `reportlab` and `PyMuPDF`: `python -m tools.build_a2_report`. Inspect every newly rendered page under `tmp/a2-report-render` before delivering a changed PDF.
