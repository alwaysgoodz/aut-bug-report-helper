# 深度调研与决策依据

调研日期：2026 年 11 月 4 日（Asia/Shanghai）。对象：AUT Contemporary Methods in Software Engineering Assignment 1；项目依据为工作区 `content.txt`，并非尚未找到的 `context.txt`。用户确认选题已获批准。本文是中文研究与交接材料，不替代 1,500-word 英文主报告。

## 研究问题与检索边界

本次调研回答三个问题：结构化缺陷报告是否有研究依据；四人、低风险、两轮开发适合怎样的方法组合；哪些实践能产生可核验的协作证据。检索使用 “What makes a good bug report”、 “risk agile plan-driven”、 “iterative incremental development”、 “code review participation software quality”、 “continuous integration practices” 和 “distributed agile tailoring”等组合，并对作者、题名、出版信息及结论进行原始来源核验。

优先纳入同行评审期刊、会议论文及作者提供的正式论文版本；排除以供应商宣传或无可核查来源的经验文章作为学术论证主体。覆盖经典概念论文、经验研究、系统综述和 2024 年分布式敏捷综述。本次属于针对作业的定向文献调研，不宣称完成了系统综述。Exa 返回 429 额度限制后改用可用网页检索；部分 DOI 页面反爬时使用作者原文及出版记录交叉核验。Canvas 课程页面未成功读取，因此没有推断课程课件、截止时间或课程特定规则。

## 文献证据及适用范围

### R1：需求依据，而非“填满字段就能解决问题”

Bettenburg 等（2008）的同行评审 FSE 论文汇总 466 份调查回应，揭示开发者需要的信息与报告者提供的信息存在差距。复现步骤等信息的重要性支持结构化提示；其样本来自 Apache、Eclipse、Mozilla 的有经验参与者，不能直接当成 AUT 学生团队的实测数据。项目据此保留原 brief 的七个字段，以降低信息遗漏；不声称已缩短修复时间。

原文：[作者提供的 FSE 论文](https://thomas-zimmermann.com/publications/files/bettenburg-fse-2008.pdf)，重点阅读摘要、调查设计、结果与有效性讨论。正式引文 DOI：[10.1145/1453101.1453146](https://doi.org/10.1145/1453101.1453146)。不要把较早技术报告当成另一个独立研究重复计证。

### R2：用较新、混合方法研究交叉验证

Soltani、Hermans 和 Bäck（2020）结合 35 位开发者访谈、305 人调查以及 250 个 GitHub 项目的挖掘，支持复现信息的价值。研究也讨论关闭时间等指标可能受其他因素影响。对本项目的推论是：分别测量“字段完整度”和“开发者能否独立复现”，不把非空字段比例解释为正确性或因果性的效率提升。堆栈信息有研究价值，但考虑 brief 和工期，暂通过 description 自由文本承载，不新增日志采集或附件子系统。

原始出版全文：[The significance of bug report elements](https://link.springer.com/article/10.1007/s10664-020-09882-z)，重点阅读 §2、§4、§5 和结论。

### R3：迭代增量是生命周期安排

Larman 和 Basili（2003）梳理迭代增量开发的历史，展示其既可与前期计划结合，也可由反馈驱动。它帮助纠正源材料中把 plan-driven、iterative-incremental、Agile 当成三个互斥层级的问题。本文将“两个可交付增量”作为生命周期，再选择需求管理、审查和反馈实践。该文是历史分析，不是证明某种方法更快的对照实验。

原文：[作者所在大学保存的论文](https://www.cs.umd.edu/~basili/publications/journals/J90.pdf)。DOI：[10.1109/MC.2003.1204375](https://doi.org/10.1109/MC.2003.1204375)。

### R4：方法选择要匹配风险

Boehm 和 Turner（2003）提出按项目风险平衡敏捷与计划驱动做法，讨论规模、关键性、变化程度、人员和文化等因素。四人、可逆、低后果原型的优势在于迅速验证未知的提示设计；团队仍需前期字段定义、验收标准和设计边界。监管场景则应增加风险论证、追溯和批准记录。该框架用于组织判断，不作为本团队已获收益的统计证据。

已读取论文原文：[Using risk to balance agile and plan-driven methods](https://www.fritz.tips/wp-content/uploads/2016/09/BeohmAndTurner_UsingRiskToBalanceAgileAndPlan-DrivenMethods.pdf)；[IEEE DOI](https://doi.org/10.1109/MC.2003.1204376)。

### R5：不能把“敏捷更好”当作结论

Dybå 和 Dingsøyr（2008）的系统综述纳入 36 项经验研究，同时指出证据质量、研究设计和情境迁移的局限。其检索覆盖到 2005 年，而且主要研究 XP，因此不能代替当代工具的直接评价。报告用它约束论证力度：根据本项目反馈需求和成本选择实践，而不承诺 Agile 普遍更快、质量更高。

原文：[期刊论文 PDF](https://cs.ecu.edu/gudivada/research/papers/agile-software-development-systematic-review.pdf)；作者机构出版记录：[SINTEF](https://www.sintef.no/en/publications/publication/1040587/)。重点阅读 §4.3、§5.3 和 §6。

### R6：审查的价值在参与内容

McIntosh 等（2014）对 Qt、VTK、ITK 的研究发现审查覆盖及参与程度与发布后缺陷有关。这是观察性证据，不能直接推出四人课程项目的因果效果。对应做法是要求非作者组员对实现或测试提出具体意见，并记录作者回应及最终审批。单纯创建 PR、机器人检查或同账号自审均不能替代这种证据。

作者原文：[MSR 2014 PDF](https://posl.ait.kyushu-u.ac.jp/~kamei/publications/McIntosh_MSR2014.pdf)；[机构出版记录](https://publications.polymtl.ca/11897/)。正式 DOI：[10.1145/2597073.2597076](https://doi.org/10.1145/2597073.2597076)。

### R7：CI 是反馈实践，不是一个绿勾

Elazhary 等（2022）的正式期刊论文基于三家中小型公司的访谈与活动记录，发现 CI 的实施因情境而异，也会形成反馈瓶颈。本项目据此采用小型、无第三方运行依赖的测试管道，要求检查结果绑定提交 SHA，并保留人工复现评价。不能把安装 GitHub Actions 直接视作完整持续集成或有效协作的证明。

[作者预印本全文](https://arxiv.org/pdf/2103.04251)；[IEEE 正式出版记录](https://ieeexplore.ieee.org/document/9374092/)。APA 引文采用最终卷期年份 2022、48(7)、2570–2583，DOI 为 **10.1109/TSE.2021.3064953**，不是检索时未获验证的其他相似编号。

### R8：分布式情境需要调整协作方式

Camara、Marinho 和 Moura（2024）的系统综述归纳了分布式大型团队对敏捷实践的调整。本文仅借鉴异步记录、沟通渠道和显式交接的思路；不据此为四人团队引入 SAFe 等大型框架。时间区隔越大，越需要在 Issue 中记录验收、决定和交接内容，而不能依赖口头讨论。

[期刊论文全文](https://www.clei.org/cleiej/index.php/cleiej/article/download/607/470/3228)，重点阅读 §3 和 §4.6.6。DOI：[10.19153/cleiej.27.1.8](https://doi.org/10.19153/cleiej.27.1.8)。期刊落地页列两位作者，PDF 正文明确列三位；交付引用按实际读取的论文首页三位作者记录。

## 本项目的综合判断

选择两个固定长度迭代，加上轻量敏捷协作实践：优先级 backlog、可测试验收、短分支、独立审查、自动检查、演示与回顾。理由是第一轮能验证基础报告流程，第二轮能根据反馈改进完整度提示；同时用明确的范围和 Done 规则约束返工。纯前期冻结全部需求会使提示设计过早定型；只有增量交付而没有反馈与质量活动，也不能自动解决协作问题。

把三种工程问题与技术逐一连接：需求变化由反馈和优先级控制；集成冲突由模块边界、短分支和 CI 管理；质量与证据真实性由验收、独立审查和精确 SHA 管理。计划中的角色不等于实际贡献，测试通过也不等于用户价值已经得到验证。

## 评分对齐与当前缺口

| 标准 | 主报告必须呈现 | 实际材料 | 尚需团队完成 |
| --- | --- | --- | --- |
| 问题与范围 15 | 五类利益相关者、价值、边界、约束、三项工程问题 | 保留原 brief 的学生团队定位，限定本地单实例原型 | 标题页成员身份；批准依据可补附件 |
| 方法比较 30 | 对同一情境比较收益、代价、条件，研究支持及局限，异地/监管情境调整 | 8 篇学术来源、比较表和选择依据 | 结合实际课堂术语复核；未读取课件不得冒称已引用 |
| 工作流 30 | 真实需求、实现、审查、测试链及经验反思 | Issues #1–6、PR #7、实现 SHA、真实本地与 CI 日志 | 非作者组员实际审查、作者回应及最终批准；评阅者权限 |
| 计划风险 15 | 优先级、可测试 AC、人员责任、两轮目标、容量、指标、风险应对 | backlog、职责、风险触发器、评价方案 | 确认 A/B/C/D 对应人员与可投入时间 |
| 表达引用 10 | 1,500 words、APA 7、图表清晰、证据可追溯 | 英文 PDF、可编辑源文件、字数报告、证据索引 | 用真实贡献替换待填项并重新计数；确认 Canvas 截止时间 |

## 官方学校资料的使用界限

已查阅 [AUT AI in learning and teaching](https://www.aut.ac.nz/about/ai-at-aut/ai-in-learning-and-teaching)，其提供学生相关 Canvas 模块入口；这不能证明本门作业允许何种 AI 使用。因此保留工具使用记录和声明草稿，最终以课程规定为准。本次没有自动提交 Canvas，也没有用其他大学的政策替代 AUT 或课程规则。
