# Structured Bug Report Helper

AUT Contemporary Methods in Software Engineering, Assignment 1. A small student-team tool for clearer bug reports. Lecturer approval was confirmed by the repository owner; no independent approval document has been supplied.

## Current implementation

The feature branch trials a working Python/SQLite creation service and CLI (BR-01). A browser UI, status editing, completeness guidance and filters are planned for the two Assignment 2 iterations. They are not implemented by this A1 trial. `main` retains the initial scaffold pending independent review.

## Setup and tests

Requires Python 3.11 or 3.12 with SQLite (standard library); no third-party packages or credentials.

```powershell
git clone https://github.com/alwaysgoodz/aut-bug-report-helper.git
cd aut-bug-report-helper
python --version
python -m unittest discover -s tests -v
```

On Windows, replace `python` with a verified Python executable if an alias opens Microsoft Store. To evaluate an open PR, check out its documented branch/commit before testing. `main` remains the scaffold until a teammate independently reviews the feature.

## Trial commands (feature branch)

```powershell
git switch feat/1-create-report
python -m bugreport --db reports.db create --title 'Login fails' --severity high --steps 'Open login' --expected 'Dashboard' --actual 'Blank page' --environment 'Firefox / Windows'
python -m bugreport --db reports.db show <id-from-create-output>
```

The second command opens a new process to read persisted data. A blank title or invalid severity returns a nonzero exit and inserts no report. `reports.db` is local and ignored by Git. The example leaves description empty deliberately: completeness guidance is planned for I2; title and valid severity are required now.

## Collaboration and evidence

See [CONTRIBUTING.md](CONTRIBUTING.md), [backlog](docs/backlog.md) and [evidence index](docs/evidence-index.md). Use Issues for requirements, short branches and pull requests with acceptance-test evidence. A non-author teammate must review before merging. Current access is private; the owner must invite the actual teammates and assessor through repository settings.

## Reuse and assistance

No existing application codebase has been imported. Python's standard-library SQLite, argparse and unittest are used. The starting brief was supplied by the owner in `content.txt` outside this repository. Research sources and decisions are recorded in project documents. Codex generated the initial scaffold, trial implementation, tests and report materials at the owner's request; this is not evidence of four students' contributions. Confirm the course's permitted use and acknowledge actual assistance in the submission.
