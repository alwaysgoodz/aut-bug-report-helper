# Design and risk record

## Proposed architecture

One local Python application serves browser forms and invokes a separate validation/report service backed by SQLite. Keep the scoring function pure and tested separately. The A1 CLI uses the same service boundary; the web adapter is planned for I1. No public deployment, authentication or cross-device concurrent editing is in scope. The shared repository supports software development collaboration; it is not the product database. If authenticated remote access becomes necessary, raise a scope change before choosing a hosted database.

SQLite reduces setup and deployment effort for a single-instance student prototype; parameterised queries prevent report text being interpreted as SQL. Store UTC timestamps and explicit enumerations. Incomplete descriptions remain permitted so I2 can guide users; only title and valid severity gate persistence. No schema changes without an Issue and migration discussion. Escape all report content in future HTML; bind development hosting to localhost and use synthetic defects rather than passwords/personal records.

## Risk register

| Risk | Likelihood / impact | Trigger | Owner | Response and fallback |
| --- | --- | --- | --- | --- |
| Scope exceeds two short iterations | High / High | Remaining Must estimate exceeds remaining capacity at daily check | A | Freeze Must scope; drop BR-05; retain test/review time. Lecturer approves any substantive scope change. |
| Merge/schema conflict | Medium / High | Two active branches edit storage/schema | C | Shared contract, max two active implementation items, short branches and daily integration; stop parallel schema edits and resolve in a paired session. |
| Meaningless high score | High / Medium | Filled text cannot reproduce seeded defect | B | Label completeness; show field-specific examples; evaluate reproduction independently; do not claim reduced resolution time. |
| Review bottleneck or absent member | Medium / High | PR awaits review for one working day | D | Assign backup non-author, pair handover; defer merge if no independent reviewer. Never count generated review as teammate evidence. |
| Data loss or disclosure | Low / High | Restart check fails or sensitive example appears | C | Transaction tests, ignored local DB, synthetic cases and local binding; backup before schema change. |
| Assessor cannot access private evidence | Medium / High | Invite not accepted or clean checkout fails | A | Verify actual assessor account access and exact submission SHA before submission; archive logs and patch as supplementary evidence. |

## Evaluation protocol (planned)

Four consenting peers each submit comparable seeded defects through an unstructured template and the guided form; alternate order, vary task equivalents and keep no identifying personal data. A developer unaware of the collection method records independent reproduction and clarification requests. Record raw time and completeness separately; show descriptive results without significance claims or causal conclusions from this tiny convenience sample. Do not treat this unrun protocol as results.
