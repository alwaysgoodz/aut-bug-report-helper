# Assignment 1 baseline plan

Verified 9 November 2026. This is the proposed two-iteration plan at the A1 reference, not a claim that students completed later A2 activities. The assessed A1 code reference is `03fb9c5e41f80026c0ec66c28a92b09ed6f1251e`. Lecturer approval is owner-confirmed; the original approval record is not supplied.

A/B/C/D map to the named members on the title page: requirements, interaction, service/storage and testing/CI respectively. Table 2 gives proposed author/reviewer pairs and person-hour estimates; BR-01 is the A1 trial reused in A2. Hours are team effort; owners do not work alone.

| Item / priority | Acceptance criteria | Iteration; hours; author/reviewer |
| --- | --- | --- |
| BR-01 / Must | Persist seven fields, unique ID, UTC timestamp and Open status. Fresh-process read matches. Blank title/invalid severity inserts nothing. | I1; 4; C/D |
| BR-02 / Must | Browser create/list survives reload; details show all fields. Invalid input retains data with accessible errors; keyboard operation works; HTML text is escaped. | I1; 6; B/C |
| BR-03 / Must | Open/In progress/Resolved updates and reopening survive restart. Invalid status or unknown ID causes no mutation. | I1; 4; C/B |
| BR-04 / Must | Score round(100n/7) for six nonblank text fields plus valid severity: 6/7=86; 7/7=100. Identify missing fields; optional blanks remain savable. | I2; 5; B/D |
| BR-05 / Should | Severity/status filters combine with AND; Clear restores all; empty results are explicit; records remain unchanged. | I2; 3; C/B |
| BR-06 / Must | Clean checkout passes applicable checks. Record demonstration feedback, reproduction outcomes and exact revision evidence. | I1 2h; I2 4h; D+A/C |

Proposed capacity is 20 person-hours per two-day iteration: five hours each, subject to confirmation. I1 delivers create/list/status (16 hours plus four contingency); I2 delivers evaluated guidance/filtering (12 plus eight contingency). A1 setup/trial/report occur in Week 1; implementation continues in A2. Each increment ends with demonstration and one recorded retrospective action. Dependencies: BR-01 -> BR-02 -> BR-04; BR-03 precedes BR-05; BR-06 spans both.

Figure 1 shows the A1 reference and intended extensions. Shared service logic prevents CLI/browser validation drift. SQLite transactions and parameterised queries suit local persistence; explicit connection closure supports Windows cleanup. A pure scoring function is independently testable. Completeness measures presence, not correctness.

If remaining Must effort exceeds capacity, A freezes additions and drops BR-05. Concurrent schema edits trigger paired integration led by C. A review waiting one working day triggers D to assign a backup non-author. A misleading high score triggers B to revise guidance; C checks restart persistence. These responses protect core functionality and review time.

Success requires all applicable acceptance checks passing and no critical unresolved defects. I2 plans four consenting peers using matched synthetic tasks with/without guidance in alternating order. Record time, field completeness and independent reproduction without clarification. Report descriptive outcomes and convenience-sample limitations; this evaluation has not run.

## Dependency and completion rules

BR-01 -> BR-02 -> BR-04; BR-03 follows BR-01/02 and precedes BR-05. BR-06 applies to both increments. Ready means agreed acceptance criteria, estimate, owner/reviewer and dependencies. Done means acceptance checks and CI green on the latest SHA, substantive non-author review/approval, updated evidence and no unresolved critical defects. A1 code is technically checked and has an approval event; the substantive human review record remains incomplete.

## Capacity reconciliation (planned person-hours)

The item estimates are total team effort, including analysis, implementation, checks and review. An accountable owner does not perform every item hour. Rows sum to the backlog estimates; each member totals five hours per iteration. Contingency protects integration, feedback and absences; it is not additional available capacity.

| I1 item | A | B | C | D | Total |
| --- | ---: | ---: | ---: | ---: | ---: |
| BR-01 | 0.5 | 0 | 2 | 1.5 | 4 |
| BR-02 | 1 | 3 | 1.5 | 0.5 | 6 |
| BR-03 | 0.5 | 1 | 1.5 | 1 | 4 |
| BR-06 | 1 | 0 | 0 | 1 | 2 |
| Review/contingency | 2 | 1 | 0 | 1 | 4 |
| Total | 5 | 5 | 5 | 5 | 20 |

| I2 item | A | B | C | D | Total |
| --- | ---: | ---: | ---: | ---: | ---: |
| BR-04 | 1 | 2.5 | 0.5 | 1 | 5 |
| BR-05 | 0.5 | 0.5 | 1.5 | 0.5 | 3 |
| BR-06 | 1.5 | 0.5 | 0.5 | 1.5 | 4 |
| Evaluation/review/contingency | 2 | 1.5 | 2.5 | 2 | 8 |
| Total | 5 | 5 | 5 | 5 | 20 |

A = Fengyi Zhan; B = Kaile Shao; C = jianqiao Fang; D = xin Li. The team must confirm availability and actual workload. Planned 25% shares cannot establish completed contributions.

## Tracked requirements

- [BR-01: Issue #1](https://github.com/alwaysgoodz/aut-bug-report-helper/issues/1)
- [BR-02: Issue #2](https://github.com/alwaysgoodz/aut-bug-report-helper/issues/2)
- [BR-03: Issue #3](https://github.com/alwaysgoodz/aut-bug-report-helper/issues/3)
- [BR-04: Issue #4](https://github.com/alwaysgoodz/aut-bug-report-helper/issues/4)
- [BR-05: Issue #5](https://github.com/alwaysgoodz/aut-bug-report-helper/issues/5)
- [BR-06: Issue #6](https://github.com/alwaysgoodz/aut-bug-report-helper/issues/6)

## Design and risk record

The report diagram distinguishes the implemented service/CLI/store from planned browser and scoring adapters. [Figure source](system-overview.svg). Scope, trigger, owner and response are in the assessed report; this plan supplies only supporting allocation detail.
