# 逐节、逐主张的编辑核验记录

这里存储人工或 AI 辅助编辑实际完成的资料核对。原始正文和来源仍由各自 JSON 文件维护，记录用哈希绑定。填写记录本身不能证明医学主张正确；独立审核角色需要重新阅读来源。本站编辑审核和执业医生签审为不同状态。

每个目标章节只保留一份当前记录。`make_editorial_record(data, target, id)` 仅生成 `pending` 空白记录，不自动声称已核验。条件正文的 target 为 `{kind: "condition", id, section}`；地图条目还需 `module_id`。模块导读、地图摘要和生命周期年龄范围也纳入哈希及变更门禁。

`cross_checked` 完整章节需要以下字段：

- `content_sha256`：`section_content_hash` 生成；包含正文、章节引用及目标。
- `scope: "full_section"`、`checked_at`、实际 `checker`、`medical_reviewed: false`。
- `supports`：每个实际阅读的来源具有 `source_id`、`source_metadata_sha256`、精确 `locator`、`source_version`、`accessed_at`、`population`、`region`、`independence_group`、`upstream_evidence`、`relation: "supports"`、说明具体支持范围的 `assessment`。版本未标明时明确写未标明，不能捏造更新时间。
- `independence`：`status: "independent_editorial_sources"`，具体编写独立性的 `rationale`，`underlying_evidence: "not_assessed" | "overlap" | "independent"`。转载、镜像和共享指南不因网址不同变成独立证据。
- `dispute`：`status: "none" | "regional_difference"` 及 `resolution`；未解决冲突不能通过。
- `claim_inventory: "all_medical_claims_in_section"` 和 `claims`：每项的 `id`、`kind`（explanation/action/threshold/benefit/risk）、`text`（两种语言的正文原句片段）、`supports`（source_id、精确 locator、assessment）。行动、阈值、疗效和风险至少有两份独立编写的支持；一般解释须有实际支持。章节整体至少覆盖两个独立来源。不能把多个主张捆成一个“全节均支持”而跳过逐项判断。
- `adversarial_review`：`status: "accepted"`、真实且不同的 `author` 与 `reviewer`、`checked_at`、重新打开的全部 `original_sources_reopened`、`findings` 及 `resolution`；每条发现记录 `status: "resolved"` 与解决方式。无发现时 findings 为 []，仍须写审核结论。AI 角色不得冒充临床人员。

旧 `claim-spot-checks.json` 只核对少量指定句子，没有当前全节正文绑定，不会自动升级为全章节合格。仅有标题、14 栏非空、篇幅增加、两条来源链接或数据库迁移，也不会升级状态。

`editorial_audit` 返回 `qualified_condition_ids` 和各目标缺口；`require_editorial_changes` 比较当前内容与已发布基线，正文、来源引用或来源元数据改变后要求重新核验。首次迁移可以显式保留旧版状态；此后新内容不能以旧签审或旧哈希放行。原临床签审门禁保持独立。
