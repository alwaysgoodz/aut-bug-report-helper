# Structured Bug Report Helper

AUT Contemporary Methods in Software Engineering, Assignments 1 and 2. A small student-team tool for clearer bug reports. Lecturer approval was confirmed by the repository owner.

## Current implementation

The A2 I2 branch implements seven-field report creation, persistent list/detail pages, guarded status changes/reopening, live and server-computed completeness guidance, and severity/status AND filters (BR-01–05). Incomplete optional information remains savable. Completeness measures information presence, not factual quality. `main`, A1 and I1 snapshots are preserved pending independent teammate review; this is not yet a final reviewed submission.

## Setup and tests

Application and Python tests require Python 3.11 or 3.12 with SQLite (standard library); no runtime third-party packages, credentials, network services or remote fonts. Browser regression checks additionally use Node.js 22 and locked development dependency `@playwright/test` 1.64.1 (`package-lock.json`).

```powershell
git clone https://github.com/alwaysgoodz/aut-bug-report-helper.git
cd aut-bug-report-helper
git switch feat/a2-iteration-2
python --version
python -m unittest discover -s tests -v
python -m compileall -q bugreport tests tools
```

On Windows, replace `python` with a verified Python executable if an alias opens Microsoft Store. To evaluate an open PR, check out its documented branch/commit before testing. `main` remains the scaffold until a teammate independently reviews the feature.

For the fixed technical review package, use `git checkout a2-review-v0.1`. This candidate is preserved for review and reproducibility; the final assessment submission must follow real team approval. [A2 report, evidence and demonstration materials](submission-a2/README.md) are included.

## CLI commands (same service as the browser)

```powershell
python -m bugreport --db reports.db create --title 'Login fails' --severity high --steps 'Open login' --expected 'Dashboard' --actual 'Blank page' --environment 'Firefox / Windows'
python -m bugreport --db reports.db show <id-from-create-output>
```

Replace `<id-from-create-output>` with the real ID, without angle brackets. The second command reads persisted data from a new process. A blank title or invalid severity returns a nonzero exit and inserts no report. `reports.db` is local and ignored by Git. This example deliberately leaves description empty; the browser explains what is missing.

## Run the browser increment

```powershell
python -m bugreport --db reports.db serve --port 8765
```

Open http://127.0.0.1:8765 in your browser. Stop with Ctrl+C. SQLite data persists in the chosen file; use the same command/file to restart. If the port is occupied, choose another with `--port 8766`. The prototype binds only to loopback, with no authentication or remote team database. Do not expose it through a proxy or public hosting. An expired form after restart should be reloaded before submitting.

To see fictional demonstration data in a separate, empty database:

```powershell
python -m tools.seed_demo --db demo.db
python -m bugreport --db demo.db serve --port 8765
```

Seeding refuses to change a database that already contains reports. Examples describe a fictional Study Planner application, not unresolved defects in this helper.

## Browser regression and quality measurements

```powershell
npm ci
npx playwright install chromium
npm run test:browser
python -m tools.check_browser_mutation
npm run test:browser
python -m tools.measure_quality --output docs/a2/evidence/performance.json
```

For a Windows Python alias problem, set `$env:BUGREPORT_PYTHON='D:/anaconda/python.exe'` before the browser commands (replace with your verified executable). If a browser download fails and Google Chrome is installed, set `$env:BUGREPORT_BROWSER_CHANNEL='chrome'`; record that browser version. Default CI uses Playwright's downloaded Chromium, not this fallback. The app itself never needs a browser download.

The browser runner uses a fresh temporary DB and port 8780, separate from your running app. Seven scenarios cover common C1/C2/C3, scoring, filters, keyboard form use and a narrow screen. HTML reports are in `playwright-report`, machine-readable results in `test-results/browser-results.json`.

The existing Actions workflow runs Python 3.11 and 3.12. Its Python 3.12 job also invokes the seven browser checks through `tests/test_browser_ci.py`; the bridge is skipped in local unittest/3.11 runs. This preserves the shared workflow because the current OAuth token cannot modify workflow files. CI logs print browser version, individual results and `CI_BROWSER_SUMMARY`; snapshots are preserved in the evidence index. Node.js 22 or newer must be present on that Ubuntu runner. A separate browser job would be preferable when workflow-write permission is available.

The mutation experiment deliberately disables one error-focus statement, verifies C1 fails at the focus assertion, and restores the original bytes in `finally`. Its expected mutant failure is evidence, not a failing delivered build. The following full suite verifies restoration. The performance helper measures 50 full-body list requests after five warmups on 500 synthetic reports with a predeclared p95 target; conditions and raw timings are preserved. See [quality plan](docs/a2/quality-plan.md) and [prospective improvement plan](docs/a2/process-improvement-plan.md).

## Collaboration and evidence

See [CONTRIBUTING.md](CONTRIBUTING.md), [backlog](docs/backlog.md) and [evidence index](docs/evidence-index.md). Use Issues for requirements, short branches and pull requests with acceptance-test evidence. A non-author teammate must review before merging. Current access is private; the owner must invite the actual teammates and assessor through repository settings.

The preparation uses stacked review proposals: [A1 PR #7](https://github.com/alwaysgoodz/aut-bug-report-helper/pull/7), [I1 PR #8](https://github.com/alwaysgoodz/aut-bug-report-helper/pull/8), then I2. [A2 traceability](docs/a2/traceability.md) connects requirements, code and checks. [A1 report materials](submission/README.md) remain an archived draft. Named members, real independent reviews, actual team retrospectives, the four-peer product study and assessor access still require the team. Passing CI does not establish those activities.

[I2 PR #10](https://github.com/alwaysgoodz/aut-bug-report-helper/pull/10) and the [A2 evidence index](docs/a2/evidence-index.md) preserve the complete technical review path.

## Reuse and assistance

No existing application codebase has been imported. Python's standard-library SQLite, argparse and unittest are used. The starting brief was supplied by the owner in `content.txt` outside this repository. Research sources and decisions are recorded in project documents. Codex generated the initial scaffold, trial implementation, tests and report materials at the owner's request; this is not evidence of four students' contributions. Confirm the course's permitted use and acknowledge actual assistance in the submission.
