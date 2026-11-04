# Prioritised backlog and two-iteration plan

All estimates are team person-hours, not elapsed time. A/B/C/D map to Fengyi Zhan / Kaile Shao / jianqiao Fang / xin Li; see [25%-each planned allocation](team/work-allocation.zh-CN.md). Actual activities remain to be verified. No feature is Done until criteria, independent review and checks pass. GitHub Issues are the tracked requirements; this file is their readable summary.

**Current schedule:** A2 places both iterations in Week 2: two working days per iteration, followed by a final evaluation/demo preparation day. Proposed capacity is 20 person-hours per iteration, subject to member availability confirmation. The original five-day A1 assumption remains in Git history; actual AI-assisted preparation is not a completed human team schedule.

| ID | Priority / iteration / hours | Requirement and testable acceptance criteria | Owner / reviewer | Dependencies |
| --- | --- | --- | --- | --- |
| BR-01 | Must / I1 / 4 | Create and persist title, description, steps, expected, actual, environment and severity. Trim title; reject empty/whitespace title and severity outside low/medium/high/critical; retain optional blanks; generate unique ID, UTC timestamp and Open status. Fresh connection returns identical saved content. Invalid submission inserts no row. A1 CLI/service slice precedes browser integration. | C / D | None |
| BR-02 | Must / I1 / 6 | Creation form exposes all seven fields; the summary list links to details showing all seven (title/severity in the heading, five body fields below). Valid submit appears once after reload; invalid title shows accessible error without data loss; empty list gives a clear message; no executable HTML from report text. Keyboard-only create/list succeeds in acceptance checks. This UI-02 clarification preserves Issue #2's "Show all seven fields" criterion without placing long report bodies in list columns. | B / C | BR-01 |
| BR-03 | Must / I1 / 4 | Update existing report Open -> In progress -> Resolved; persisted state survives restart. Invalid status or unknown ID yields explicit error without changing rows; QA can reopen Resolved -> Open. | C / B | BR-01, BR-02 |
| BR-04 | Must / I2 / 5 | Score is round(100*n/7), counting six trimmed text fields plus explicit valid severity (no preselected default). Six of seven yields 86; seven yields 100. Blank/whitespace scores zero for that field. Before save show precise missing field names and guidance. Permit incomplete content; invalid title/severity still blocks save. Label the score as completeness, never factual quality. | B / D | BR-02 |
| BR-05 | Should / I2 / 3 | Severity and status filters combine with AND; Clear restores all rows; unmatched combination shows empty state; stored reports are unchanged. | C / B | BR-03 |
| BR-06 | Must / I1 2h + I2 4h / 6 | D maintains test/check instructions and A the evaluation record. Clean checkout passes all acceptance tests; I1 persistence and status checks pass. In I2 conduct a counterbalanced exploratory comparison with four consenting peers on matched seeded defects: record completion time, applicable information present and whether a developer reproduces without clarification. Report raw outcomes and caveats; do not invent results. | D + A / C | All applicable stories |

## Capacity and goals

Assumption to confirm: each named member has five project hours per iteration, giving 20 person-hours per iteration (40 total), distributed equally in the detailed allocation. Each iteration is two working days in Week 2; A1 setup/trial/report take place in Week 1. These are planned durations, not Canvas dates or completed work. I1 has 16 planned core hours + 4 review/contingency; I2 has 12 planned core hours + 8 evaluation/review/contingency. Drop BR-05 before core work if capacity slips. A1's proven BR-01 work is reused.

I1 goal: usable browser create/list/status with persistence and CI. Week 2 day 1: agree contracts and BR-01/02; day 2: BR-03 integration, review, checks and retrospective. I2 goal: evaluate guidance and add filtering if time permits. Day 3: reprioritise and BR-04/PI-01; day 4: BR-05/06, regression, evaluation and retrospective. Day 5: final report, demonstration and release preparation. The team must choose actual dates and record real activity.

## Definition of Ready / Done

Ready requires agreed acceptance criteria, owner/reviewer, estimate and known dependencies. Done requires criteria demonstrated, acceptance tests and CI green on latest SHA, a substantive non-author review with approval, documentation/evidence updated, and no unresolved critical defects. The A1 trial is a pre-iteration technical experiment; a passing CI run alone does not make BR-01 Done.
