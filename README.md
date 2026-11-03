# Structured Bug Report Helper

AUT Contemporary Methods in Software Engineering, Assignment 1. A small student-team tool for clearer bug reports. Lecturer approval was confirmed by the repository owner; no independent approval document has been supplied.

## Current implementation

The A2 I1 branch implements a local browser application with structured report creation, list/detail pages, persistent state changes and guarded invalid/stale updates (BR-01/02/03). Completeness guidance and filters are selected for I2. `main` and A1's branch remain preserved pending independent review.

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

## Run the browser increment

```powershell
git switch feat/a2-iteration-1
python -m bugreport --db reports.db serve --port 8765
```

Open http://127.0.0.1:8765 in your browser. Stop with Ctrl+C. SQLite data persists in the chosen file; do not delete it to restart. The application binds only to loopback and is scoped to a local single-instance course prototype, with no authentication or remote team database. [I1 record](docs/a2/iteration-1.md) and [prospective process-improvement plan](docs/a2/process-improvement-plan.md) distinguish implemented evidence from the real team activities still required.

## Collaboration and evidence

See [CONTRIBUTING.md](CONTRIBUTING.md), [backlog](docs/backlog.md) and [evidence index](docs/evidence-index.md). Use Issues for requirements, short branches and pull requests with acceptance-test evidence. A non-author teammate must review before merging. Current access is private; the owner must invite the actual teammates and assessor through repository settings.

The actual proposed change is [draft PR #7](https://github.com/alwaysgoodz/aut-bug-report-helper/pull/7). Research, the report draft, diagram and source files are in the [submission review package](submission/README.md). The independently tested implementation snapshot and its CI run are recorded in the evidence index; the final submission release remains pending real team review.

## Reuse and assistance

No existing application codebase has been imported. Python's standard-library SQLite, argparse and unittest are used. The starting brief was supplied by the owner in `content.txt` outside this repository. Research sources and decisions are recorded in project documents. Codex generated the initial scaffold, trial implementation, tests and report materials at the owner's request; this is not evidence of four students' contributions. Confirm the course's permitted use and acknowledge actual assistance in the submission.
