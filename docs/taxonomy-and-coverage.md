# 分类、专业维度与覆盖率

## 一个主目录，多维标签

MECE 在本项目是归档规则，不是声称疾病在生物学上互斥。优先顺序：妊娠特异 → 损伤/中毒 → 肿瘤 → 明确器官系统 → 系统性血液/免疫 → 全身症状 → 先天/遗传/其他。感染、慢性、特殊人群等用标签表示；需要时可扩展标签，不复制同一主题。

| 主目录 ID | 中文 | 当前条目 |
|---|---|---:|
| general | 全身与症状入口 | 5 |
| respiratory | 呼吸系统 | 8 |
| cardiovascular | 心血管 | 6 |
| gastrointestinal | 消化与肝胆胰 | 8 |
| neurologic | 神经系统 | 5 |
| mental_sleep | 精神心理与睡眠 | 3 |
| endocrine_metabolic | 内分泌代谢与营养 | 5 |
| hematologic_immune | 血液与系统性免疫 | 2 |
| musculoskeletal | 肌骨与风湿 | 4 |
| dermatologic | 皮肤毛发与甲 | 5 |
| ophthalmic | 眼科 | 3 |
| ent_oral | 耳鼻喉与口腔 | 5 |
| renal_urinary | 肾脏与泌尿 | 5 |
| reproductive_sexual | 生殖与性健康 | 3 |
| pregnancy_puerperium | 妊娠与产后 | 3 |
| injury_toxicology | 损伤中毒与环境 | 4 |
| neoplastic | 肿瘤 | 2 |
| other_rare_congenital | 先天遗传与其他 | 1 |

## 最终完整覆盖的分母

最终目标采用 **ICD-11 MMS 2026-01 全部13,155个合格独立病症类别**，达到100%才完成；95%是阶段里程碑。完整目录与纳入规则已经冻结，当前逐项核验覆盖8类，剩余13,147类。每类优先顺序见[完整清单](icd-priorities/index.md)。同义词、跨科室归属和193个待办标题不能充当新增覆盖。正文进入分子需满足双语 14 维度内容标准、来源支持与有效类别映射；医学签审覆盖另行计算。纳入排除规则、风险及补充顺序见[覆盖审计与补充计划](coverage-audit-and-roadmap.md)。

页面按[大科与亚科配置](../data/department-groups.json)导航；下面保留的 18 个主目录是唯一归档维度，不等于左侧菜单层级。

## 另行保留的日常需求研究工具

需求覆盖研究需要明确地区、人群、时间和场景下的真实信息需求。由独立人员裁定主题匹配及最低可用信息；高质量覆盖率为已审合格条目所覆盖的加权需求 / 全部合格抽样需求。这与本次 ICD 类别目标不同。

疾病标题计数、ICD 实体计数、搜索 Top-10 命中、全部合成题通过，都不能证明人口需求95%覆盖。当前77篇正文与193个标题待办独立记录；人口需求覆盖率仍未测定。

CSV 输入字段为 `condition_id,weight,group,adjudicated,dataset_kind`。`dataset_kind=representative` 只能由实际采样方法证明，不能靠改字符串获得真实性。所有映射需 adjudicated=true，权重必须正且有限。未知主题留在分母；不允许丢弃难题来抬高分数。

```bash
python -m src.guide coverage tests/fixtures/coverage-synthetic.csv --allow-synthetic
```

示例仅演示计算。程序分别返回草稿主题映射率和医学已审主题映射率，并按 group 给出权重。它不计算未经方法支持的置信区间。真实评估还要固定数据集、公开遗漏与亚组、评估映射质量及采样偏倚。

## 维度细分

14个核心正文维度采用导读加分条说明，具体问题清单见[正文标准](content-depth-standard.md)。另外保留身份、别名、症状、科室、病程标签、地区、证据、审核和翻译状态。定量流行病学、正式诊断准则、定量预后、筛查及地区药品批准的结构化字段预留空值。以后可拆为更细的 claim，不应认为每一自然语言段落就是单一可验证命题。
