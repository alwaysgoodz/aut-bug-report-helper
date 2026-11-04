# Evidence index

Verified 2026-11-04 (Asia/Shanghai). Repository: [alwaysgoodz/aut-bug-report-helper](https://github.com/alwaysgoodz/aut-bug-report-helper), private. Owner must give the actual teammates and assessor access. A 404 to other viewers may mean missing permission.

For the subsequent application and UI changes, see the [current refinement evidence index](optimization/README.md). This table preserves the original A1 workflow evidence.

| Evidence | Link / identifier | Verified meaning and limits |
| --- | --- | --- |
| Prioritised backlog | [BR-01](https://github.com/alwaysgoodz/aut-bug-report-helper/issues/1), [BR-02](https://github.com/alwaysgoodz/aut-bug-report-helper/issues/2), [BR-03](https://github.com/alwaysgoodz/aut-bug-report-helper/issues/3), [BR-04](https://github.com/alwaysgoodz/aut-bug-report-helper/issues/4), [BR-05](https://github.com/alwaysgoodz/aut-bug-report-helper/issues/5), [BR-06](https://github.com/alwaysgoodz/aut-bug-report-helper/issues/6); [readable plan](backlog.md) | Actual Issues with criteria; roles are proposed, not confirmed members. |
| Tracked trial requirement | [Issue #1](https://github.com/alwaysgoodz/aut-bug-report-helper/issues/1) | Exists before feature implementation; BR-01 service/CLI slice. |
| Change proposed for independent review | [Draft PR #7](https://github.com/alwaysgoodz/aut-bug-report-helper/pull/7) | Open, unmerged; independent reviews were empty at verification. This does not yet satisfy the assessed reviewed-change requirement. |
| Exact implementation snapshot | [`0eed2879192c3b6d4feb55484dbb040dd39c6560`](https://github.com/alwaysgoodz/aut-bug-report-helper/commit/0eed2879192c3b6d4feb55484dbb040dd39c6560) | Tested implementation. Later documentation revisions do not change this snapshot. Not a final submission release. |
| Remote implementation checks | [Actions run 41673631149](https://github.com/alwaysgoodz/aut-bug-report-helper/actions/runs/41673631149) | Actual success on that SHA: Ubuntu, Python 3.11 and 3.12; 16 test methods per job plus compile check. |
| Preserved check results | [CI metadata](evidence/ci-implementation.json), [CI log](evidence/ci-implementation.log), [local green](evidence/local-green.txt), [missing-feature baseline](evidence/local-red.txt) | Logs corroborate scope, not user-value improvements or independent review. |
| Trial reflection | [Trial record](trial-record.md) | Actual Windows cleanup failure and correction; later stakeholder evaluation is planned. |
| Individual contributions | [Ledger](contributions.md) | Student identities and genuine member activities pending; AI assistance is disclosed. |
| Repository controls | [Workflow](../.github/workflows/tests.yml), [CONTRIBUTING](../CONTRIBUTING.md) | Main protection API returned HTTP 403 requiring Pro or public visibility. Approval is a manual team rule, not an enabled protected-branch gate. |
| Submission identity | Pending final independently reviewed SHA/tag | Select after team review and evidence completion. The implementation SHA enables review now. |

To reproduce: clone, `git checkout 0eed2879192c3b6d4feb55484dbb040dd39c6560`, then `python -m unittest discover -s tests -v` and `python -m compileall -q bugreport tests`. Initial `main` is the scaffold, not this tested feature.
