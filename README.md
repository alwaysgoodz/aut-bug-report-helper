# Structured Bug Report Helper

AUT Contemporary Methods in Software Engineering, Assignment 1. A small student-team tool for clearer bug reports. Lecturer approval was confirmed by the repository owner; no independent approval document has been supplied.

## Current implementation

This repository starts with an Assignment 1 workflow scaffold. The linked feature PR trials a Python/SQLite creation service and CLI. A browser UI, status editing, completeness guidance and filters are planned for the two Assignment 2 iterations. They are not implemented by the scaffold.

## Setup and tests

Requires Python 3.11 or 3.12 with SQLite (standard library); no third-party packages or credentials.

```powershell
git clone https://github.com/alwaysgoodz/aut-bug-report-helper.git
cd aut-bug-report-helper
python --version
python -m unittest discover -s tests -v
```

On Windows, replace `python` with a verified Python executable if an alias opens Microsoft Store. To evaluate an open PR, check out its documented branch/commit before testing. `main` remains the scaffold until a teammate independently reviews the feature.

## Collaboration and evidence

See [CONTRIBUTING.md](CONTRIBUTING.md), [backlog](docs/backlog.md) and [evidence index](docs/evidence-index.md). Use Issues for requirements, short branches and pull requests with acceptance-test evidence. A non-author teammate must review before merging. Current access is private; the owner must invite the actual teammates and assessor through repository settings.

## Reuse and assistance

No existing application codebase has been imported. Python's standard-library SQLite, argparse and unittest are used. The starting brief was supplied by the owner in `content.txt` outside this repository. Research sources and decisions are recorded in project documents. Codex generated the initial scaffold, trial implementation, tests and report materials at the owner's request; this is not evidence of four students' contributions. Confirm the course's permitted use and acknowledge actual assistance in the submission.
