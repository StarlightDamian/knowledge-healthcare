# 数据入口

轻量目录：`catalog/index.json`。详情：`conditions/{id}.json`。结构：`../schemas/`。独立来源登记：`evidence/sources.json`。论文抽取状态：`evidence/studies.json`。未完成标题：`catalog/backlog.json`，不计已实现内容。

数据有72个医学/症状主题，不包含真实患者病例。所有正文为编辑草稿。`support_status` 表达主张审核状态，不是 URL 可达性；`medical_reviewed_at=null` 不应被编辑日期替代。审稿者登记当前为空。

JSON 内的 URL 仅用于显式引用；网页运行时不自动访问来源。对真实数据收集、任何患者病历和地区临床版本需要另外的权限、契约与审核。
