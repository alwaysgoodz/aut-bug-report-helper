# Thursday Windows demo delivery

Prepared for the owner's **26 November 2026** demonstration. [Issue #20](https://github.com/alwaysgoodz/aut-bug-report-helper/issues/20) / [draft PR #21](https://github.com/alwaysgoodz/aut-bug-report-helper/pull/21) track this delivery follow-up; they were opened during delivery work, not backdated as team decisions. Application source tested: **8bf9edd4d477a5bf96ea243b0f02e2a541ae0cef**. Later packaging/evidence changes retain the exact tested app/runtime hashes, checked by the builder. Independent approval is still pending.

## Use and contents

Extract the entire `BugReportHelper-Windows-x64-v1.0.0-demo.zip` into a writable folder on Windows 10/11 x64 and double-click `StartDemo.cmd`. Keep the terminal open; Ctrl+C stops the server and preserves reports. The browser opens the actual loopback address. If the default port is occupied, an exclusive listener receives a free port instead. Another launch for the same workspace opens the existing instance. Native Markdown download works without JavaScript; copying shows success only after clipboard write succeeds, with a download fallback on rejection.

The first run creates four clearly fictional Study Planner reports. Data lives under the extracted package's `demo-data`; reset requires explicit confirmation, refuses a live workspace and saves a readable SQLite backup before replacing only that demo database. The bundle includes `CheckDemo.cmd`, `ResetDemo.cmd`, a bilingual `DEMO-GUIDE.html` with four suggested 2.5-minute segments, and `Evidence` logs/screenshots. Those segments are suggestions, not completed student contributions or attendance records.

The runtime is the official [CPython 3.13.17 Windows embeddable distribution](https://www.python.org/downloads/release/python-31317/), configured to load only bundled application code. Its downloaded ZIP matches the release's SHA-256; the extracted executable has a valid Python Software Foundation signature. The [embedding documentation](https://docs.python.org/3/using/windows.html#the-embeddable-package) describes this isolated distribution. Original `runtime/LICENSE.txt` is retained. No install, pip, Node.js, internet or administrator action is needed at presentation time; building/testing from source is a separate developer task.

The source companion excludes assessment PDFs/history, real study data and machine databases. Existing uncommitted A1 edits were left untouched and unstaged. Clone the exact manifest commit to rebuild with Git metadata and the full historical documentation; `SOURCE-START.txt` explains the companion's limits.

## Verification

| Check | Evidence and result |
| --- | --- |
| Current Python checks | [Raw log](evidence/python.log): **81 functional pass / 82 discovered**, one local CI-only bridge skip. Includes seven new launcher/data-integrity checks, two export HTTP checks and 14 study-tool checks. |
| Remote source CI | [Run 45413726637](https://github.com/alwaysgoodz/aut-bug-report-helper/actions/runs/45413726637), [metadata](evidence/implementation-ci.json), [log](evidence/implementation-ci.log): Python 3.11/3.12 pass on 8bf9edd; Python 3.12 also runs all 24 Chromium cases. The Windows portable-runtime verification is separately recorded below. |
| Extracted-package browser regression | [Log](evidence/browser.log), [raw JSON](evidence/browser-results.json): **24 pass**, no retries/unexpected/skipped/flaky results. Application scenarios run against the actual embedded CPython 3.13.17 at a Chinese/space path; two study-tool pilots use separate source-based temporary test-only data. Chrome 157.0.8103.80. |
| Portable runtime smoke | [Results](evidence/portable-smoke.json), [verification script](evidence/verify-portable.py): actual runtime with PATH restricted to System32; first seed, real HTTP create/status/export, duplicate launch, refused live reset, restart persistence and a readable five-report backup followed by four seeded reports. SQLite 3.50.4. |
| Actual batch + offline browser rehearsal | [Observation](evidence/offline-rehearsal.json): `StartDemo.cmd` used from outside the package directory; only loopback/file requests allowed. Four fixtures, 86% → 100%, save/status, clipboard success, mobile layout and offline guide work; no attempted external page resources or page errors. |
| Version / identity | [Tested build manifest](evidence/tested-build.json) records source/runtime hashes. The final `BUILD-INFO.json` records the delivery commit and checks equality with those tested hashes before copying evidence. `SHA256SUMS.txt` identifies both delivered ZIPs. |
| Visual QA | [Dashboard](evidence/dashboard.png), [six-field form](evidence/guidance-86.png), [detail/export](evidence/report-detail.png), [phone](evidence/phone.png), [guide](evidence/guide.png) inspected for layout and readability. These are actual settled browser screenshots, not mockups. |
| Static checks | Python compilation, JavaScript/config syntax and Git diff checks pass. |

One test-only study fixture request reported a client-side connection abort while serving a static asset; all 24 assertions passed. The raw log retains that transport message; no unproved network fix is claimed. The initial clipboard check was corrected for Windows CRLF normalisation. A smoke verifier initially kept its own SQLite inspection connection open and reused its previous fixture directory; closing that observer and using a new test directory allowed the actual backup/reset path to be checked without changing application code.

## Reproduce and limits

```powershell
python -m unittest discover -s tests -v
$env:BUGREPORT_PYTHON='D:/anaconda/python.exe' # replace with the local interpreter
$env:BUGREPORT_BROWSER_CHANNEL='chrome' # local installed-browser verification
$env:BUGREPORT_PORTABLE_ROOT='C:/Demo/BugReportHelper-Windows-x64-v1.0.0-demo'
npm run test:browser
python -m tools.build_demo --output dist --evidence-dir docs/demo-delivery/evidence
```

The builder intentionally refuses evidence from a different application/runtime. Verify changed application bytes again before updating `tested-build.json`. A default build without `--evidence-dir` is labelled as a development build without archived verification.

Tests ran on this Windows 11 x64 computer with a relocated isolated runtime, not a second physical presentation machine. External browser page requests were blocked during rehearsal; Windows itself was not disconnected. Rehearse on the actual machine on 25 November, as the guide recommends. Real peers, team discussion confirmation and personal contribution evidence remain separate human work; this package contains no human evaluation results.
