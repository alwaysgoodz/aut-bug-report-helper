# Prioritised backlog and two-iteration plan

All estimates are team person-hours, not elapsed time. A/B/C/D are unassigned proposed roles. No feature is considered Done until its acceptance criteria, independent review and checks pass. GitHub Issues are the tracked requirements; this file is their readable summary.

| ID | Priority / iteration / hours | Requirement and testable acceptance criteria | Owner / reviewer | Dependencies |
| --- | --- | --- | --- | --- |
| BR-01 | Must / I1 / 4 | Create and persist title, description, steps, expected, actual, environment and severity. Trim title; reject empty/whitespace title and severity outside low/medium/high/critical; retain optional blanks; generate unique ID, UTC timestamp and Open status. Fresh connection returns identical saved content. Invalid submission inserts no row. A1 CLI/service slice precedes browser integration. | C / D | None |
| BR-02 | Must / I1 / 6 | Browser form and list show all seven fields. Valid submit appears once after reload; invalid title shows accessible error without data loss; empty list gives a clear message; no executable HTML from report text. Keyboard-only create/list succeeds in manual acceptance check. | B / C | BR-01 |
| BR-03 | Must / I1 / 4 | Update existing report Open -> In progress -> Resolved; persisted state survives restart. Invalid status or unknown ID yields explicit error without changing rows; QA can reopen Resolved -> Open. | C / B | BR-01, BR-02 |
| BR-04 | Must / I2 / 5 | Score is round(100*n/7), counting six trimmed text fields plus explicit valid severity (no preselected default). Six of seven yields 86; seven yields 100. Blank/whitespace scores zero for that field. Before save show precise missing field names and guidance. Permit incomplete content; invalid title/severity still blocks save. Label the score as completeness, never factual quality. | B / D | BR-02 |
| BR-05 | Should / I2 / 3 | Severity and status filters combine with AND; Clear restores all rows; unmatched combination shows empty state; stored reports are unchanged. | C / B | BR-03 |
| BR-06 | Must / I1 2h + I2 4h / 6 | D maintains test/check instructions and A the evaluation record. Clean checkout passes all acceptance tests; I1 persistence and status checks pass. In I2 conduct a counterbalanced exploratory comparison with four consenting peers on matched seeded defects: record completion time, applicable information present and whether a developer reproduces without clarification. Report raw outcomes and caveats; do not invent results. | D + A / C | All applicable stories |

## Capacity and goals

Assumption to confirm: four members each have five project hours per iteration, giving 20 person-hours per iteration (40 total). Each iteration is five working days scheduled by the team within the Assignment 2 timetable; Assignment 1's setup/trial/report take place in Week 1. These are proposed durations, not Canvas deadlines. I1 has 16 planned hours + 4 contingency; I2 has 12 planned hours + 8 contingency. BR-04 is a Must to preserve the source brief; drop BR-05 before core functions if capacity slips. A1's proven BR-01 work is reused rather than counted as a second implementation.

I1 goal: usable browser create/list/status with persistent data and CI. Days 1-2: agree schema and BR-01/02; days 3-4: integrate BR-03 and review; day 5: run BR-06 checks, demo and retrospective. I2 goal: evaluate missing-information guidance and add filtering if time remains. Days 1-2: feedback reprioritisation and BR-04; days 3-4: BR-05/06 and regression; day 5: demonstration, evaluation and release evidence.

## Definition of Ready / Done

Ready requires agreed acceptance criteria, owner/reviewer, estimate and known dependencies. Done requires criteria demonstrated, acceptance tests and CI green on latest SHA, a substantive non-author review with approval, documentation/evidence updated, and no unresolved critical defects. The A1 trial is a pre-iteration technical experiment; a passing CI run alone does not make BR-01 Done.
