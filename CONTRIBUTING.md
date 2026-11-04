# Team workflow

1. Agree an Issue with value, acceptance criteria, owner, reviewer, iteration and estimate. Never infer completion from commit counts.
2. Move its backlog status to Ready, then In progress. Limit the team to two implementation items and one review item at once.
3. Branch `feat/<issue>-<short-name>`; keep branches under one working day where feasible. Synchronise before editing shared schema files.
4. Write acceptance-focused tests; implement; run `python -m unittest discover -s tests -v` and `python -m compileall -q bugreport tests`.
5. Open a PR referencing the Issue, test results and known limitations. One teammate other than the author inspects correctness, edge cases, persistence, scope and privacy; records substantive comments; and reruns a test. The author responds with changes or reasoning.
6. Merge only after checks pass and that reviewer approves the latest revision. If branch protection is unavailable on the account's plan, record that limitation and enforce the same rule manually; do not claim a technical gate is active.
7. Update evidence links, decision log and contribution ledger. At each iteration end, demonstrate the increment, record feedback and choose one process improvement.

Member names are recorded in [team.json](docs/team.json); student IDs and GitHub accounts are blank at the owner's request. A/B/C/D map to Fengyi Zhan, Kaile Shao, jianqiao Fang and xin Li. [Equal workload allocation](docs/team/work-allocation.zh-CN.md) proposes 25% each; actual contributions still require linked activities. Rotate author and reviewer across work items.

| Role | Accountable area | Review partner |
| --- | --- | --- |
| A | Backlog, stakeholder feedback, requirements | D |
| B | Browser forms and accessibility | C |
| C | Python service, SQLite, schema | B |
| D | Acceptance tests, CI, release evidence | A |
