# Reproducible quality scenarios

Defined before performance measurement. Scope is the loopback-only student prototype; no public-network, concurrent-user or production-security claim is made.

## Security and integrity acceptance

Run `python -m unittest discover -s tests -v`. `test_web.py` exercises escaped stored HTML and CSP, missing/wrong/non-ASCII CSRF, foreign Origin, untrusted Host, content/body limits, duplicate fields, invalid query filters, unknown IDs and stale status updates. Observe response codes and unchanged saved data. The browser suite verifies that injected report markup is displayed as text, not an image element. These are selected regression checks, not a penetration test or proof of absence of vulnerabilities.

## Performance scenario and fixed target

Stimulus: one local browser-equivalent client retrieves the full report list from a new SQLite database containing 500 synthetic reports; include connection, server rendering and reading the response body. No concurrent requests. Use five warm-up GETs then 50 measured GETs. Each response must be HTTP 200; nearest-rank p95 must be below 250 ms on the recorded local environment. Preserve all measured durations, response bytes, SQLite size, Python/SQLite/OS/CPU information and exact Git/source fingerprints. Record dataset setup time separately; do not count it as request latency.

Procedure: `python -m tools.measure_quality --output docs/a2/evidence/performance.json`. The helper creates and removes its own temporary database, starts an ephemeral loopback server and shuts it down. It never uses or deletes the user's reports.db. Report cold-start, concurrent users, larger datasets, hardware differences and network deployment as limitations. Do not tune the threshold after seeing results or compare this measurement to browser automation startup time.

## Process-quality experiment

See [prospective PI-01 plan](process-improvement-plan.md). `python -m tools.check_browser_mutation` deliberately disables one focus statement, runs only C1, verifies the expected focus assertion fails and restores the original bytes in a finally block. Run the unmodified full browser suite afterwards. A failing controlled-mutant check is expected evidence; delivered-code checks must all pass.
