# Ten-minute demonstration + five-minute questions

Proposed slots only. Replace A/B/C/D with actual members after they perform substantive work. Do not present this script as evidence of activities or learning that have not occurred.

## Before the session

Check out the fixed review reference (then the eventual approved submission reference), run the README commands and open the app. Use a separate demo database, seeded only when empty. Keep a terminal with tests ready, the actual successful remote run, raw mutation comparison and performance JSON. Verify assessor access in advance. Have saved screenshots/logs as a contingency, not a substitute for runnable code.

| Time | Proposed speaker | Demonstration and technical explanation |
| --- | --- | --- |
| 0:00–1:00 | A | State the student-team problem; open BR-02/04 and show one testable criterion and its PR/test link. Explain the seven-field boundary and why completeness differs from quality. |
| 1:00–3:20 | B | Open New report. Submit whitespace title with reproduction steps; show retained text and focused linked summary. Fill six fields (86%) then explicit severity (100%), submit and reload. Explain server validation versus progressive JavaScript. |
| 3:20–5:10 | C | Move Open -> In progress -> Resolved -> Open. Explain parameterised persistence and expected-status check. Show the stale-update test and why a conflict is preferable to silently overwriting. Apply both filters, show no matches and Clear. |
| 5:10–7:30 | D | Show actual Python/browser CI results and version. Run C1 or a small relevant test. Compare the I1 escaped mutation to I2's intended focus-assertion failure and original restoration. Avoid waiting for package/browser downloads live. |
| 7:30–9:00 | A + D | Explain the prospective process measures and their limits. Show the 500-record latency setup, raw 50 samples and p95. Distinguish a local technical result from peer product-value evidence and team performance. |
| 9:00–10:00 | All | Each states one actual linked decision/outcome. Explain the approach/tool trade-off and honest limitations. Conclude with what the team would change next. |
| 10:00–15:00 | All | Questions; each member answers about their real technical/process contribution. |

## Commands worth rehearsing

```powershell
python -m unittest discover -s tests -p test_guidance_filters.py -v
npm run test:browser -- --grep C1:
python -m tools.check_browser_mutation
npm run test:browser -- --grep C1:
```

The controlled mutant is expected to fail the focus assertion, and the helper must restore the file. Show the resulting `original_restored` and final passing check. Prefer the saved full evidence during the ten-minute window; mutation diagnosis is not a new team experiment to improvise in front of the assessor.

## Likely questions to prepare for

- Why permit incomplete reports, and what does 100% fail to establish?
- Why does an HTTP test miss a visible focus problem? Why not use only browser tests?
- Why was the process measure changed from the A1 peer study, and what remains unmeasured?
- Does one selected mutation support a general quality claim?
- What changes for distributed users, multiple instances or regulated development?
- Which changes did each real member make, review or evaluate, and where is the evidence?
