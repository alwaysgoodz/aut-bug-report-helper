# Iteration 1: core browser increment

Date: 4 November 2026 (Asia/Shanghai). This is one AI-assisted implementation increment in the preparation session, not evidence that four students completed a five-day collaborative iteration. Named responsibilities, non-author review and a real team retrospective remain pending.

## Goal and selection

Deliver BR-02 browser creation/listing and BR-03 persisted status transitions on top of BR-01. Acceptance: seven visible fields, no selected severity default, retained form contents and linked errors on rejection, safe rendering, refresh without duplicate insertion, Open -> In progress -> Resolved -> Open, missing/invalid IDs and statuses rejected without mutation. Preserve the A1 service/CLI interface.

Proposed accountable roles remain B (browser), C (service/storage) and D (acceptance/CI), with review partners defined in the backlog. Actual implementation and execution here were generated/performed by Codex through the owner's account; these proposed roles are not individual contribution claims.

## Outcome and evidence

- Service now supports listing, counts and guarded status changes; stale state returns a conflict instead of overwriting another change.
- Local server-rendered UI works without JavaScript for creation and status updates. JavaScript progressively focuses errors and disables duplicate button presses. Static files are local; no runtime third-party package or font fetch is needed.
- All 34 Python/HTTP tests passed: [raw log](evidence/i1-tests.log). Existing 16 A1 tests remain part of this suite.
- Ad-hoc browser exercise C1/C2/C3 passed: invalid input retention/error focus; create/reload; full status cycle/reopen. [Raw observations](evidence/i1-browser.json), [actual screenshot](evidence/i1-reports.png). These were browser automation via MCP, not a human user study or a committed browser regression suite.
- Security boundaries include loopback binding, exact Host validation, Origin checking, CSRF token, escaped HTML, parameterised SQL, request/field limits and CSP. These controls are tested within prototype scope, not a public-hosting assurance claim.

## Technical retrospective and selected improvement

Problem observed: the automated Python/HTTP suite never executes client-side JavaScript, so a passing check cannot establish error-focus behaviour. A controlled mutation disabled the one error-focus statement temporarily. All 34 tests still passed while the browser's active element failed the focus criterion. [Mutation observation](evidence/i1-focus-mutant.json), [mutant test log](evidence/i1-focus-mutant-tests.log). The original statement was restored immediately; the mutation is not an accidental delivered defect.

Selected I2 improvement: commit browser acceptance tests and run them in CI, covering the same C1/C2/C3 and new guidance/filter cases. Repeat the same missing-focus mutation to assess whether the new suite detects it. Retain HTTP/service tests for fast feedback; browser checks complement them.

## Limits and decisions

The A1 four-peer evaluation is still unrun. Actual teammates must inspect the PR and hold their own retrospective. A2's Week 2 work and five-day schedule cannot be reconstructed from this single preparation session. Feature implementation is complete for this increment, but the shared Definition of Done also requires independent approval, which is pending.
