# 团队交接与提交前动作

已完成的准备包括：按原始项目方向开展 8 篇学术文献调研；英文报告、APA 7 参考文献与系统图；6 条带验收标准的 GitHub Issues；两轮容量/职责/风险计划；可运行 Python/SQLite 创建与读取切片；本地 16 项测试及远程 Python 3.11/3.12 检查；真实证据索引。报告已生成并逐页检查，但仍为草稿。

## 先理解当前状态

- [私有仓库](https://github.com/alwaysgoodz/aut-bug-report-helper) 已创建。只有已核验的 owner 账号；没有擅自邀请未知成员。
- `main` 是最初脚手架；实际功能和交付材料在 `feat/1-create-report`，由 [PR #7](https://github.com/alwaysgoodz/aut-bug-report-helper/pull/7) 提议合并。
- 实现验证快照为 `0eed2879192c3b6d4feb55484dbb040dd39c6560`，远程结果为 [run 41673631149](https://github.com/alwaysgoodz/aut-bug-report-helper/actions/runs/41673631149)。后续文档提交不改变这一快照。
- PR 暂无独立审查；没有合并，也没有虚构四人协作。当前不能把工作流 30 分部分视作已经满足。
- 当前账户的私有仓库分支保护接口返回 HTTP 403，提示需要 Pro 或改成公开；未更改可见性或购买套餐。审批是已记录的人工规则，不是已启用的强制保护。

## 需要真实团队信息与活动的最后环节

1. 提供四位成员姓名、学号、GitHub 用户名；确认 A/B/C/D 职责和每轮投入时间。标题页与正文贡献陈述目前明确标注待填，不可直接提交。
2. Owner 在 GitHub Settings → Collaborators 邀请实际组员和评阅者，确认他们能打开私有仓库、Issue、PR 和 Actions。不要只测试 owner 自己能否访问。
3. 让非作者的真实成员检出 PR 最新版本，阅读 Issue #1 和验收测试，独立运行至少一项检查，检查实现及资源关闭问题。在 PR 提交具体反馈或有依据的批准，由作者回应；有修改则重新检查最新 SHA。评论模板不能替代真实发现或判断。
4. 每人记录实际工作、决定或结果及链接：需求澄清、实现、审查、测试、调研或反馈整理均可；不要将生成材料归为四位同学各自已完成的活动，不用 commit 总数证明贡献。
5. 独立批准和检查通过后再合并，确定最终 submission commit 或 tag；更新报告、证据索引和贡献陈述。当前文档给出的实现 SHA 可复验，但不是已获独立批准的提交版本。
6. 按 Canvas 确认截止时间和适用规则，复核工具使用声明，由一位成员提交 PDF、仓库链接和证据索引。本次未提交 Canvas，也未推测 deadline。

## 本地复验

```powershell
Set-Location -LiteralPath 'F:\COMP\Contemporary Methods in Software Engineering\bug-report-helper'
git status --short
git log -3 --oneline
& 'D:/anaconda/python.exe' -m unittest discover -s tests -v
& 'D:/anaconda/python.exe' -m compileall -q bugreport tests
```

应用仅需 Python 标准库。A1 实现的是服务/CLI 小切片；浏览器表单、列表、状态更新和第二轮评分/筛选仍为后续 backlog。不要声称已经实现整套两轮产品。

## 修改和重新生成报告

编辑 `docs/report-content.json`，再运行 `D:/anaconda/python.exe docs/build_report.py`。生成器使用本机 Calibri、`reportlab` 与 `PyMuPDF`；它们只用于文档生成，不是应用运行依赖。生成结果为 `output/pdf/assignment-1-report-draft.pdf`、可编辑 Markdown、SVG 系统图、主文字数记录和页面预览。修改后要再次检查每一页，并将更新文件同步到仓库 `submission`。

当前主文按空白分词为 1,263 words；按拆分连字符、斜杠等更保守方式计为 1,318，均低于 1,500。涵盖正文、表格标题/单元格、图中文字、文内引用和贡献陈述。补写真实贡献后必须重新计数，不能把应评分的分析移进附录规避字数。

## 核心设计与判断

原 brief 有 **7 个输入字段**：title、description、steps、expected、actual、environment、severity。ID、status 和 timestamp 是系统元数据，不进入完整度分母。完整度计划公式 `round(100*n/7)`：6 项为 86、7 项为 100。该规则尚未实现，属于第二轮验收。完整度不等于真实性或复现成功率。

报告把迭代增量作为生命周期，配合轻量敏捷实践；保留前期范围、字段契约与验证计划。调研、比较和工作流反思均放在主文；中文调研备忘录用于理解依据和复核来源，不作为额外计分主文提交。
