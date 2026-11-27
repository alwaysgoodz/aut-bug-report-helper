# Structured Bug Report Helper

A local application for student software teams to collect reproducible bug reports, complete missing details and track resolution. Built for AUT ENSE701, Contemporary Methods in Software Engineering.

## Assignment 2 assessment release

- [Fixed release a2-submission-v1.0.1](https://github.com/alwaysgoodz/aut-bug-report-helper/releases/tag/a2-submission-v1.0.1) includes the Windows x64 portable demonstration.
- [Assessment package](submission-a2/README.md) links the report text, [evidence index](docs/a2/evidence-index.md), [requirements traceability](docs/a2/traceability.md) and individual evidence worksheet.
- [Demo implementation CI](https://github.com/alwaysgoodz/aut-bug-report-helper/actions/runs/45741766481) ran against b7c88822898d53975ce1f789272fac9646ed6647. The assessed source includes the same application and test files with the verified demonstration guide and evidence.

The Assignment 1 [assessment notes and exact baseline](submission/README.md) describe the BR-01 service and CLI trial at 03fb9c5e41f80026c0ec66c28a92b09ed6f1251e. The A2 evidence index links the two original iteration commits separately from the later demo version.

## Run from source

Requirements are Git and Python 3.11 or 3.12 with the standard SQLite module. The application has no third-party Python packages or remote service dependencies. Browser verification also uses Node.js 22 or newer, npm and the locked development dependency Playwright 1.64.1.

```text
git clone https://github.com/alwaysgoodz/aut-bug-report-helper.git
cd aut-bug-report-helper
git checkout a2-submission-v1.0.1
python --version
python -m bugreport --db reports.db serve --port 8765
```

Open [http://127.0.0.1:8765](http://127.0.0.1:8765). Stop the server with Ctrl+C and use the same database path when restarting to keep reports. If the port is occupied, choose another with `--port 8766`. The server binds to loopback and has no user accounts. Use it locally.

To start with fictional demonstration reports, use a separate empty database:

```text
python -m tools.seed_demo --db demo.db
python -m bugreport --db demo.db serve --port 8765
```

### Try the key workflow

1. Open **New report**. Enter reproduction steps (for example, “Open Settings, then select Notifications”), leave title and severity blank and submit. The form retains the steps and shows linked errors.
2. Enter a title and choose **High**. Save at 43%. Use the detail page's **Add** links or **Edit report** to fill the remaining fields. At 100%, edit remains available. Saves retain the report number and its current status.
3. Move the report from **Open** to **In progress** and **Resolved**. Return to Reports, filter by **High** and **Resolved**, then download the report as Markdown from its detail page. Use the same database to check persistence after restarting.

The list displays 25 reports per page. The seven fields are title, description, reproduction steps, expected behaviour, actual behaviour, environment and severity. Completeness is an equal-weight field-presence score. The prototype has no remote team database, attachments or external tracker integration.

## Verify

```text
python -m unittest discover -s tests -v
python -m compileall -q bugreport tests tools
npm ci
npx playwright install chromium
npm run test:browser
```

The local Python suite discovers 83 checks. It runs 82 functional checks and skips the GitHub-only browser bridge. GitHub Actions runs Python 3.11 and 3.12, with the latter executing the bridge. The browser suite runs 25 tests, including two synthetic study-tool checks. It starts isolated test servers on ports 8780 and 8790 with temporary databases. See `playwright-report/index.html` and `test-results/browser-results.json` after running.

On Windows, if `python` invokes a Store alias, use an installed interpreter's full path and set `$env:BUGREPORT_PYTHON='C:/path/to/python.exe'` before browser tests. If Chromium installation fails and local Chrome is available, use `$env:BUGREPORT_BROWSER_CHANNEL='chrome'` and record the browser version. The hosted checks use Playwright's locked Chromium.

```text
python -m tools.measure_quality --output tmp/performance-recheck.json
python -m tools.check_browser_mutation
npm run test:browser
```

The current performance scenario retrieves 50 full 25-record pages after five warm-up requests from a temporary 500-report SQLite database. The historical I2 full-list measurement belongs to commit `f36dfc7`. The [evidence index](docs/a2/evidence-index.md) describes the scenarios, target, conditions and raw timings. The mutation script temporarily disables error-summary focus, checks for the expected C1 assertion failure and restores the original file before the full suite rerun. Run it in a clean checkout. For the planned human evaluation and its current status, see the [study protocol](docs/peer-study/README.md).

## Windows portable demonstration

Download and fully extract the ZIP from the [assessment release](https://github.com/alwaysgoodz/aut-bug-report-helper/releases/tag/a2-submission-v1.0.1), then double-click `StartDemo.cmd`. The package bundles CPython 3.13.17. It needs no Python or Node installation and opens the local browser without network access during the demo. Verify the ZIP against `SHA256SUMS.txt` in the release.

Open `DEMO-GUIDE.html` for the tested sequence. The app persists into `demo-data/demo-reports.db`. To migrate an earlier demo workspace, stop the launcher and copy the existing database into that relative path before starting the new package. `CheckDemo.cmd` verifies its runtime. `ResetDemo.cmd` requests confirmation and backs up the demo database before resetting it. The checked-in [rehearsal record](docs/a2/evidence/final/VALIDATION.txt) documents the actual package checks.
