# 文档入口（渐进式阅读）

先看根目录 README 的版本边界。按任务选择一份文档，不需要一次读取全部正文。

| 任务 | 文档 |
|---|---|
| 讨论是否值得做、最强反方和关键变量 | [双向钢人论证与决策](双向钢人论证与决策.md) |
| 理解已经实现的模块及数据流 | [架构](architecture.md) |
| 核验医学结论与引文 | [证据政策](evidence-policy.md) |
| 疾病如何分类、95% 怎么测量 | [分类和覆盖率](taxonomy-and-coverage.md) |
| 添加/更新一条疾病 | [内容贡献](content-contribution.md) |
| 界面翻译与临床地区差异 | [本地化](localization.md) |
| 危险提示和软件局限 | [安全边界](safety-and-limitations.md) |
| 打开网页、上传 GitHub、发布 | [部署](deployment.md) |
| 某来源影响哪些字段 | 运行 `python -m src.guide impact SOURCE_ID` |
| 获取轻量机器入口 | `data/catalog/index.json` → 单个 `data/conditions/ID.json` |

全部来源的检索状态见 [来源登记](references.md)。任何文档中的目标值都不能覆盖 `reports/content-audit.json` 所记载的实际值。
