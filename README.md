# Structured Bug Report Helper

AUT Contemporary Methods in Software Engineering, Assignments 1 and 2. A small student-team tool for clearer bug reports. Lecturer approval was confirmed by the repository owner.

## Assignment 1 assessment package (updated 9 November 2026)

Use the [revised A1 report, exact-version setup instructions and evidence index](submission/README.md). The assessed A1 application commit is `03fb9c5e41f80026c0ec66c28a92b09ed6f1251e`; it contains the service/CLI trial, and its 16 acceptance checks and compilation were rechecked successfully. This fixed reference separates A1 evidence from the later browser and A2 changes below. The repository is now public; Issue, PR, CI and fixed-version README access were verified without authentication. PR #7 has a non-author approval with an empty body; substantive review details, member attribution and four actual contribution statements remain unverified. The updated A1 package supersedes older access/review status descriptions in historical drafts.

## Current implementation

The current branch, `feat/interaction-motion`, adds restrained page/feedback motion, smoothly retargeted completeness, clear saving/applying states, current-section focus and status-transition previews. Motion respects initial and live reduced-motion preferences; native forms work without JavaScript. See the [UX-01 checks and evidence](docs/interaction-motion/README.md). It retains the previous Unicode/input fixes, history restoration, filtered navigation, responsive dashboard, grouped form, mobile cards, 25-report pages and BR-01–05 functionality. Incomplete optional information remains savable. Completeness measures information presence, not factual quality. Team names, equal workload allocation, discussion drafts and the peer-study tool are ready in [team preparation](docs/team/work-allocation.zh-CN.md) and [study protocol](docs/peer-study/README.md). No real participant outcomes or completed contributions are inferred. See [navigation/input evidence](docs/navigation-review/README.md), [earlier UI fixes](docs/ui-review/README.md) and [A1/A2 gap audit (Chinese)](docs/assessment-audit.zh-CN.md).

`main`, A1, I1 and the original I2 snapshot remain preserved pending independent teammate review; this is not yet a final reviewed submission.

## Setup and tests

Application and Python tests require Python 3.11 or 3.12 with SQLite (standard library); no runtime third-party packages, credentials, network services or remote fonts. Browser regression checks additionally use Node.js 22 and locked development dependency `@playwright/test` 1.64.1 (`package-lock.json`).

```powershell
git clone https://github.com/alwaysgoodz/aut-bug-report-helper.git
cd aut-bug-report-helper
git switch feat/interaction-motion
python --version
python -m unittest discover -s tests -v
python -m compileall -q bugreport tests tools
```

On Windows, replace `python` with a verified Python executable if an alias opens Microsoft Store. To evaluate an open PR, check out its documented branch/commit before testing. `main` remains the scaffold until a teammate independently reviews the feature.

For the earlier complete preparation package use `git checkout team-study-ready-v0.1`; UX-01 is a subsequent interface change. Software candidate `a2-review-v0.4` and earlier snapshots are preserved. Updated A1/A2 report drafts include the supplied names, intentionally blank IDs/accounts, planned 25% shares and explicit uncompleted human activities. A2 distinguishes its v0.4 application checks from historical I1/I2 and latency conditions. Final assessment submission requires real team approval.

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
python -m tools.measure_quality --output tmp/performance-recheck.json
```

For a Windows Python alias problem, set `$env:BUGREPORT_PYTHON='D:/anaconda/python.exe'` before the browser commands (replace with your verified executable). If a browser download fails and Google Chrome is installed, set `$env:BUGREPORT_BROWSER_CHANNEL='chrome'`; record that browser version. Default CI uses Playwright's downloaded Chromium, not this fallback. The app itself never needs a browser download.

The browser runner uses temporary databases on ports 8780 (application) and 8790 (test-only study tool), separate from your previews. Twenty-two scenarios comprise 16 earlier application regressions, four UX-01 scenarios and two explicitly simulated study-pilot checks. Python discovery finds 73 tests: 72 functional checks (58 application/transport, 14 study-tool) pass locally and one CI-only bridge is skipped. HTML results are in `playwright-report`, raw JSON in `test-results/browser-results.json`. Simulated consent/reports are never copied into the real study directory.

The existing Actions workflow runs Python 3.11 and 3.12. Its Python 3.12 job also invokes the 22 browser checks through `tests/test_browser_ci.py`; the bridge is skipped in local unittest/3.11 runs. This preserves the shared workflow because the current OAuth token cannot modify workflow files. CI logs print browser version, individual results and `CI_BROWSER_SUMMARY`; snapshots are preserved in the evidence index. Node.js 22 or newer must be present on that Ubuntu runner. A separate browser job would be preferable when workflow-write permission is available.

The historical mutation experiment deliberately disables one error-focus statement, verifies C1 fails at the focus assertion, and restores the original bytes in `finally`. Its expected mutant failure is evidence, not a failing delivered build. The current performance helper measures 50 full-body requests rotating over 20 pages after five warmups on 500 synthetic reports, audits every ID and records source hashes. Each response contains 25 reports, so its latency is not directly comparable with the historical 500-row response. See the [refinement measurement plan](docs/optimization/plan.md), original [quality plan](docs/a2/quality-plan.md) and [process improvement plan](docs/a2/process-improvement-plan.md). Write rechecks to `tmp` to preserve archived evidence.

## Collaboration and evidence

See [CONTRIBUTING.md](CONTRIBUTING.md), [backlog](docs/backlog.md) and [evidence index](docs/evidence-index.md). Use Issues for requirements, short branches and pull requests with acceptance-test evidence. A non-author teammate must review before merging. Public read access was verified on 9 November 2026; actual teammates still need appropriate write access. The assessor can inspect the public evidence without an invitation while visibility remains public.

The preparation uses stacked review proposals: [A1 PR #7](https://github.com/alwaysgoodz/aut-bug-report-helper/pull/7), [I1 PR #8](https://github.com/alwaysgoodz/aut-bug-report-helper/pull/8), then I2. [A2 traceability](docs/a2/traceability.md) connects requirements, code and checks. [A1 report materials](submission/README.md) remain an archived draft. Named members, real independent reviews, actual team retrospectives, the four-peer product study and assessor access still require the team. Passing CI does not establish those activities.

[I2 PR #10](https://github.com/alwaysgoodz/aut-bug-report-helper/pull/10) and the [A2 evidence index](docs/a2/evidence-index.md) preserve the complete technical review path.

## Reuse and assistance

No existing application codebase has been imported. Python's standard-library SQLite, argparse and unittest are used. The starting brief was supplied by the owner in `content.txt` outside this repository. Research sources and decisions are recorded in project documents. Codex generated the initial scaffold, trial implementation, tests and report materials at the owner's request; this is not evidence of four students' contributions. Confirm the course's permitted use and acknowledge actual assistance in the submission.

## Team and peer-study preparation

[Fengyi Zhan, Kaile Shao, jianqiao Fang and xin Li: planned 25% each](docs/team/work-allocation.zh-CN.md). [I1 discussion draft](docs/team/iteration-1-discussion-draft.zh-CN.md), [I2 discussion draft](docs/team/iteration-2-discussion-draft.zh-CN.md) and [named individual drafts](docs/a2/individual-statements/README.md) require actual member confirmation/evidence. IDs/accounts are blank by request.

Run `python -m tools.peer_study serve --data-dir study-data --port 8766`, then open http://127.0.0.1:8766. Follow the [protocol](docs/peer-study/README.md); the real dataset starts empty. Use a separate `--test-only` directory for practice. Anonymous reports, timing and independent semantic/reproduction coding are collected only through actual participation. Export with `python -m tools.peer_study export --data-dir study-data --output study-export`. Local participant directories are ignored by Git.
