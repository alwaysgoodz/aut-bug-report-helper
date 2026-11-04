# Assignment 1 review package

- [English PDF report draft](output/pdf/assignment-1-report-draft.pdf)
- [Editable report](docs/assignment-1-report.md), [content data](docs/report-content.json), [system diagram](docs/system-overview.svg)
- [Research and source appraisal (Chinese)](research/research-memo.zh-CN.md)
- [Team handoff (Chinese)](docs/team-handoff.zh-CN.md)
- [Word count](docs/word-count.json), [evidence index](../docs/evidence-index.md)
- [Original supplied brief](source-brief.txt), originally named `content.txt` in the local workspace

The supplied four names and planned 25% allocations are included; student IDs and GitHub accounts are intentionally blank. Actual contributions, independent review, final assessed reference and access remain unverified. [Equal workload plan](../docs/team/work-allocation.zh-CN.md), [discussion drafts](../docs/team/iteration-1-discussion-draft.zh-CN.md) and [prepared product study](../docs/peer-study/README.md) are not completed human activities. Current count: 1,269 whitespace words / 1,325 conservative tokens, under 1,500.

The application uses only Python's standard library. Optional report regeneration uses `reportlab`, `PyMuPDF` and the Windows Calibri font files: from the repository root, run `python submission/docs/build_report.py`. Inspect every regenerated PDF page before replacing the delivered report. The generator writes PDF output, Markdown, SVG, count metadata and temporary render previews within `submission`; do not commit temporary render previews.
