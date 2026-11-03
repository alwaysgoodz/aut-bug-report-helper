# Assignment 1 review package

- [English PDF report draft](output/pdf/assignment-1-report-draft.pdf)
- [Editable report](docs/assignment-1-report.md), [content data](docs/report-content.json), [system diagram](docs/system-overview.svg)
- [Research and source appraisal (Chinese)](research/research-memo.zh-CN.md)
- [Team handoff (Chinese)](docs/team-handoff.zh-CN.md)
- [Word count](docs/word-count.json), [evidence index](../docs/evidence-index.md)
- [Original supplied brief](source-brief.txt), originally named `content.txt` in the local workspace

The report is a draft because actual student identities/contributions, non-author review, final reviewed submission identity and assessor access remain pending. Generated materials must not be presented as evidence that four members already performed those activities.

The application uses only Python's standard library. Optional report regeneration uses `reportlab`, `PyMuPDF` and the Windows Calibri font files: from the repository root, run `python submission/docs/build_report.py`. Inspect every regenerated PDF page before replacing the delivered report. The generator writes PDF output, Markdown, SVG, count metadata and temporary render previews within `submission`; do not commit temporary render previews.
