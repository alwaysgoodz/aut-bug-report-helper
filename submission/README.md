# Assignment 1 assessment package

The report addresses the four tasks in the supplied brief. The application reference is the exact A1 commit below, independently approved on GitHub but still a draft PR. Later A2/UI features are outside this trial.

- [English PDF report](output/pdf/assignment-1-report-draft.pdf)
- [Editable report](docs/assignment-1-report.md) and [source data](docs/report-content.json)
- [Evidence index](docs/evidence-index.md), [prioritised plan](docs/a1-plan.md) and [system diagram](docs/system-overview.svg)
- [Verification record](evidence/verification.json) and [acceptance recheck](evidence/a1-acceptance-recheck.log)
- [Assigned individual tasks and deliverables (Chinese)](docs/team-task-allocation.zh-CN.md)
- [Submission gaps and handoff (Chinese)](docs/team-handoff.zh-CN.md)
- [Original assignment brief](source-brief.txt)

## Repository and assessed application reference

Repository: https://github.com/alwaysgoodz/aut-bug-report-helper

Assessed code commit: `03fb9c5e41f80026c0ec66c28a92b09ed6f1251e`.

Requirement [Issue #1](https://github.com/alwaysgoodz/aut-bug-report-helper/issues/1) -> [PR #7](https://github.com/alwaysgoodz/aut-bug-report-helper/pull/7) -> [approval](https://github.com/alwaysgoodz/aut-bug-report-helper/pull/7#pullrequestreview-5796447154) -> [successful CI](https://github.com/alwaysgoodz/aut-bug-report-helper/actions/runs/41675675123). The selected SHA is both reviewed and checked. The approval has no written rationale; member attribution, substantive reviewer findings and reviewer test execution remain unverified. No merge is claimed. Public read access was verified on 9 November 2026; team write access is not established by public visibility.

## Setup and reproduce A1 tests

Requires Python 3.11 or 3.12 with SQLite; application and tests use only the standard library. `main` is the scaffold, so check out the exact A1 SHA.

```powershell
git clone https://github.com/alwaysgoodz/aut-bug-report-helper.git
cd aut-bug-report-helper
git checkout 03fb9c5e41f80026c0ec66c28a92b09ed6f1251e
python --version
python -m unittest discover -s tests -v
python -m compileall -q bugreport tests
python -m bugreport --db reports.db create --title 'Login fails' --severity high --steps 'Open login' --expected 'Dashboard' --actual 'Blank page' --environment 'Firefox / Windows'
python -m bugreport --db reports.db show <actual-ID-from-create>
```

Replace `<actual-ID-from-create>` with the returned ID. On Windows use a verified executable if `python` resolves to a Store alias; the local recheck used `D:/anaconda/python.exe` (Python 3.12.7). The CLI is the A1 feature; a browser is planned for A2. The ignored SQLite database is local. The example intentionally leaves description blank: optional information is permitted. Blank titles/invalid severity fail without inserting a record.

## Regenerate the report and evidence

Return to `docs/a1-assessment-refinement` before using the added report utilities. Report authoring requires `reportlab`, `PyMuPDF` and the existing Windows Calibri fonts; these are not application runtime dependencies. Metadata re-verification requires an authenticated GitHub CLI and internet access. The public-access check deliberately sends no authentication.

```powershell
git switch docs/a1-assessment-refinement
python submission/tools/verify_a1.py
python submission/docs/build_report.py
```

The verifier exports the A1 Git tree to an ignored temporary directory and runs checks there, preserving the active application checkout. PDF regeneration writes the editable report, SVG, complete main-text count and page renders inside `submission`. Inspect every regenerated page. [Word count](docs/word-count.json) includes headings, all main tables, diagram labels, citations and individual contribution statements; cover, references and the supporting evidence appendix are excluded.

## Remaining human inputs

Four names are supplied; IDs/accounts are intentionally blank at the user's request. The individual work is now assigned in the task allocation; genuine execution results still need recording. The planned 25% allocation is not a record of actual contributions. Identify reviewer `fadeout12`, record actual review reasoning/test results, and confirm each member's statement. Topic approval is owner-confirmed without an attached record. Check the Canvas deadline and course materials; neither is present in this workspace. This package has not been submitted to Canvas.

Codex assistance is acknowledged in the main report and appendix. No existing application codebase was imported. Research sources are in APA 7 format; claim-level source appraisal is preserved in the research memo. Passing technical checks does not establish completed human collaboration or a guaranteed grade.
