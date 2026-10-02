# 全量ICD病症编辑优先清单

为全部合格独立ICD类别生成可追溯的知识编写顺序，最终完整覆盖；P0–P3是项目编辑等级，不是WHO排名、临床分诊或执业医师逐病签审。

冻结版本 2026-01：13,155 个合格叶类别全部列出；已完成 98 类，待办 13,057 类，目标100%。

这是规则驱动的编辑排程，不是患者分诊或逐病种医学精确排名。未评估类别默认P2；未知保留null，不能解释为低危。已完成类别仍保留优先级，但待办顺序与工作包为空。

同级待办按章节轮转，章内保持WHO官方顺序；每20个待办类别组成一个工作包。同级顺序仅用于调度。已有候选按精确代码关联当前正文映射、标题库存及首批草稿；标题和草稿不继承正文完整或审核状态。

CSV对可能被Excel解释为公式的文本加单引号；WHO标题的逐字原值保存在JSON。修改内容、映射或规则后运行 `python -m src.guide priorities-icd`；`python -m src.guide priorities-icd --check` 只检查生成物是否过期。

中英文名称取自同版WHO官方表；Markdown仅去除标题层级缩进，JSON保留原值。中文表只补充名称，分类、祖先继承、分母和顺序仍以冻结英文树为准。

[方法与范围](../coverage-audit-and-roadmap.md) · [规则与来源](../../data/icd/priorities.json) · [冻结目录](../../data/icd/README.md) · [CSV全量清单](../../reports/icd-priorities.csv)

## 优先级定义

- **P0 时间敏感与器官保护先补**：优先编写新发或急性情形的关键识别与行动；不由类别名推断患者当前严重性。
- **P1 早诊早治与重点人群先补**：按可干预风险、群体负担、公共卫生或母婴及功能保护需求系统推进；只用有依据的范围。
- **P2 全专科系统补齐／待逐类裁定**：其余所有类别均进入完整队列，未判为低风险；在实际检索发现更高优先依据时更新规则。
- **P3 有依据的稳定管理专题**：仅在有明确个别依据时采用；本版不强制分配。

## 医学考虑维度

- **疾病负担**（burden）：区分家族汇总资料与逐叶数据；未获得可比叶级患病率、死亡率或DALY时不编造数值。
- **证据缺口**（evidence_gap）：仅记录已经确认的证据不足；未逐类检索时为null，不等于没有证据。
- **可避免的死亡或功能损害**（preventable_harm）：早发现、适当治疗、预防或康复可能改变的结局；不得把家族中一个亚型的疗效推广到全部类别。
- **传播与公共卫生**（public_health）：记录传播控制、免疫或暴露预防的选题依据；不将所有感染病等同为可人传人或需隔离。
- **延误敏感性**（time_sensitivity）：是否需要优先解释时间敏感的识别与行动；只记录已核对的范围和条件，不推算统一急救时限。
- **特殊人群与公平可及**（vulnerable_population）：记录母婴、儿童、老人或功能受损者的具体知识需求；年龄和罕见本身不作为降低价值的理由。

## 逐章全量清单

| 章 | 中文编辑标签 / WHO官方英文章名 | 全部 | 已完成 | 待办 | P0 | P1 | P2 | P3 |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| [01](chapter-01.md) | 感染与寄生虫病<br>Certain infectious or parasitic diseases | 876 | 18 | 858 | 18 | 176 | 682 | 0 |
| [02](chapter-02.md) | 肿瘤<br>Neoplasms | 1043 | 0 | 1043 | 0 | 669 | 374 | 0 |
| [03](chapter-03.md) | 血液及造血器官<br>Diseases of the blood or blood-forming organs | 220 | 0 | 220 | 0 | 0 | 220 | 0 |
| [04](chapter-04.md) | 免疫系统<br>Diseases of the immune system | 214 | 12 | 202 | 12 | 0 | 202 | 0 |
| [05](chapter-05.md) | 内分泌、营养与代谢<br>Endocrine, nutritional or metabolic diseases | 539 | 2 | 537 | 2 | 98 | 439 | 0 |
| [06](chapter-06.md) | 精神、行为与神经发育<br>Mental, behavioural or neurodevelopmental disorders | 720 | 0 | 720 | 0 | 463 | 257 | 0 |
| [07](chapter-07.md) | 睡眠觉醒<br>Sleep-wake disorders | 73 | 1 | 72 | 0 | 0 | 73 | 0 |
| [08](chapter-08.md) | 神经系统<br>Diseases of the nervous system | 717 | 8 | 709 | 34 | 68 | 615 | 0 |
| [09](chapter-09.md) | 视觉系统<br>Diseases of the visual system | 608 | 5 | 603 | 5 | 85 | 518 | 0 |
| [10](chapter-10.md) | 耳与乳突<br>Diseases of the ear or mastoid process | 136 | 1 | 135 | 1 | 13 | 122 | 0 |
| [11](chapter-11.md) | 循环系统<br>Diseases of the circulatory system | 489 | 17 | 472 | 17 | 44 | 428 | 0 |
| [12](chapter-12.md) | 呼吸系统<br>Diseases of the respiratory system | 288 | 2 | 286 | 2 | 37 | 249 | 0 |
| [13](chapter-13.md) | 消化系统<br>Diseases of the digestive system | 812 | 3 | 809 | 3 | 12 | 797 | 0 |
| [14](chapter-14.md) | 皮肤<br>Diseases of the skin | 657 | 6 | 651 | 6 | 0 | 651 | 0 |
| [15](chapter-15.md) | 肌肉骨骼与结缔组织<br>Diseases of the musculoskeletal system or connective tissue | 361 | 0 | 361 | 0 | 29 | 332 | 0 |
| [16](chapter-16.md) | 泌尿生殖系统<br>Diseases of the genitourinary system | 461 | 1 | 460 | 1 | 12 | 448 | 0 |
| [17](chapter-17.md) | 性健康相关<br>Conditions related to sexual health | 57 | 0 | 57 | 0 | 0 | 57 | 0 |
| [18](chapter-18.md) | 妊娠、分娩及产褥<br>Pregnancy, childbirth or the puerperium | 451 | 12 | 439 | 18 | 433 | 0 | 0 |
| [19](chapter-19.md) | 围产期相关<br>Certain conditions originating in the perinatal period | 536 | 0 | 536 | 4 | 529 | 3 | 0 |
| [20](chapter-20.md) | 发育异常<br>Developmental anomalies | 1129 | 0 | 1129 | 0 | 1129 | 0 | 0 |
| [21](chapter-21.md) | 症状、体征和临床发现<br>Symptoms, signs or clinical findings, not elsewhere classified | 1086 | 7 | 1079 | 7 | 3 | 1076 | 0 |
| [22](chapter-22.md) | 损伤、中毒及外因后果<br>Injury, poisoning or certain other consequences of external causes | 1677 | 3 | 1674 | 3 | 3 | 1671 | 0 |
| [25](chapter-25.md) | 特殊用途中的合格病症<br>Codes for special purposes | 5 | 0 | 5 | 0 | 2 | 3 | 0 |

## 下一工作包：20个待办类别（末包不足20时按实列出）

| 代码 | WHO官方中英名称 | 编辑归口 | 优先级 | 规则 | 覆盖与候选 | 顺序 / 工作包 |
|---|---|---|---|---|---|---|
| [8A66.0](http://id.who.int/icd/release/11/mms/338178896) | 惊厥性癫痫持续状态<br>Convulsive status epilepticus | 神经内科 | P0 | [p0-status-epilepticus](chapter-08.md#rule-p0-status-epilepticus) | missing | 1<br>WP-0001 |
| [JA01.0](http://id.who.int/icd/release/11/mms/1396448570) | 腹腔妊娠<br>Abdominal pregnancy | 产科 | P0 | [p0-ectopic-pregnancy](chapter-18.md#rule-p0-ectopic-pregnancy) | missing | 2<br>WP-0001 |
| [KA60](http://id.who.int/icd/release/11/mms/381388700) | 胎儿或新生儿脓毒症<br>Sepsis of fetus or newborn | 儿科 | P0 | [p0-neonatal-sepsis-asphyxia](chapter-19.md#rule-p0-neonatal-sepsis-asphyxia) | missing | 3<br>WP-0001 |
| [8A66.10](http://id.who.int/icd/release/11/mms/854964357) | 失神癫痫持续状态<br>Absence status epilepticus | 神经内科 | P0 | [p0-status-epilepticus](chapter-08.md#rule-p0-status-epilepticus) | missing | 4<br>WP-0001 |
| [JA01.1](http://id.who.int/icd/release/11/mms/913821868) | 输卵管妊娠<br>Tubal pregnancy | 产科 | P0 | [p0-ectopic-pregnancy](chapter-18.md#rule-p0-ectopic-pregnancy) | missing<br>ectopic-pregnancy: pending | 5<br>WP-0001 |
| [KB21.0](http://id.who.int/icd/release/11/mms/1968732603) | 重度出生窒息<br>Severe birth asphyxia | 儿科 | P0 | [p0-neonatal-sepsis-asphyxia](chapter-19.md#rule-p0-neonatal-sepsis-asphyxia) | missing | 6<br>WP-0001 |
| [8A66.1Y](http://id.who.int/icd/release/11/mms/36262213/other) | 其他特指的非惊厥性癫痫持续状态<br>Other specified non-convulsive status epilepticus | 神经内科 | P0 | [p0-status-epilepticus](chapter-08.md#rule-p0-status-epilepticus) | missing | 7<br>WP-0001 |
| [JA01.2](http://id.who.int/icd/release/11/mms/1121615955) | 卵巢妊娠<br>Ovarian pregnancy | 产科 | P0 | [p0-ectopic-pregnancy](chapter-18.md#rule-p0-ectopic-pregnancy) | missing | 8<br>WP-0001 |
| [KB21.1](http://id.who.int/icd/release/11/mms/1875062819) | 轻度和中度出生窒息<br>Mild and moderate birth asphyxia | 儿科 | P0 | [p0-neonatal-sepsis-asphyxia](chapter-19.md#rule-p0-neonatal-sepsis-asphyxia) | missing | 9<br>WP-0001 |
| [8A66.1Z](http://id.who.int/icd/release/11/mms/36262213/unspecified) | 未特指的非惊厥性癫痫持续状态<br>Non-convulsive status epilepticus, unspecified | 神经内科 | P0 | [p0-status-epilepticus](chapter-08.md#rule-p0-status-epilepticus) | missing | 10<br>WP-0001 |
| [JA01.Y](http://id.who.int/icd/release/11/mms/1563334645/other) | 其他特指的异位妊娠<br>Other specified ectopic pregnancy | 产科 | P0 | [p0-ectopic-pregnancy](chapter-18.md#rule-p0-ectopic-pregnancy) | missing | 11<br>WP-0001 |
| [KB21.Z](http://id.who.int/icd/release/11/mms/848321559/unspecified) | 未特指的出生窒息<br>Birth asphyxia, unspecified | 儿科 | P0 | [p0-neonatal-sepsis-asphyxia](chapter-19.md#rule-p0-neonatal-sepsis-asphyxia) | missing | 12<br>WP-0001 |
| [8A66.Y](http://id.who.int/icd/release/11/mms/906174792/other) | 其他特指的癫痫持续状态<br>Other specified status epilepticus | 神经内科 | P0 | [p0-status-epilepticus](chapter-08.md#rule-p0-status-epilepticus) | missing | 13<br>WP-0001 |
| [JA01.Z](http://id.who.int/icd/release/11/mms/1563334645/unspecified) | 未特指的异位妊娠<br>Ectopic pregnancy, unspecified | 产科 | P0 | [p0-ectopic-pregnancy](chapter-18.md#rule-p0-ectopic-pregnancy) | missing | 14<br>WP-0001 |
| [8A66.Z](http://id.who.int/icd/release/11/mms/906174792/unspecified) | 未特指的癫痫持续状态<br>Status epilepticus, unspecified | 神经内科 | P0 | [p0-status-epilepticus](chapter-08.md#rule-p0-status-epilepticus) | missing | 15<br>WP-0001 |
| [JB40.0](http://id.who.int/icd/release/11/mms/325070079) | 产褥期脓毒症<br>Puerperal sepsis | 产科 | P0 | [p0-puerperal-sepsis](chapter-18.md#rule-p0-puerperal-sepsis) | missing | 16<br>WP-0001 |
| [8B01.0](http://id.who.int/icd/release/11/mms/958976948) | 动脉瘤性蛛网膜下腔出血<br>Aneurysmal subarachnoid haemorrhage | 神经内科 | P0 | [p0-acute-stroke](chapter-08.md#rule-p0-acute-stroke) | missing | 17<br>WP-0001 |
| [8B01.1](http://id.who.int/icd/release/11/mms/247198410) | 非动脉瘤性蛛网膜下腔出血<br>Non-aneurysmal subarachnoid haemorrhage | 神经内科 | P0 | [p0-acute-stroke](chapter-08.md#rule-p0-acute-stroke) | missing | 18<br>WP-0001 |
| [8B01.2](http://id.who.int/icd/release/11/mms/133091217) | 未知动脉瘤或非动脉瘤性蛛网膜下腔出血<br>Subarachnoid haemorrhage not known if aneurysmal or non-aneurysmal | 神经内科 | P0 | [p0-acute-stroke](chapter-08.md#rule-p0-acute-stroke) | missing | 19<br>WP-0001 |
| [8B11.0](http://id.who.int/icd/release/11/mms/1070137396) | 颅外大动脉粥样硬化引起的缺血性脑卒中<br>Cerebral ischaemic stroke due to extracranial large artery atherosclerosis | 神经内科 | P0 | [p0-acute-stroke](chapter-08.md#rule-p0-acute-stroke) | missing | 20<br>WP-0001 |

## 来源与定位

- **WHO官方中文名称** [同版中文电子表格](https://icdcdn.who.int/static/releasefiles/2026-01/SimpleTabulation-ICD-11-MMS-zh.zip)；读取：2026-10-02；快照SHA-256：`8cb750a5c6feaabe9f1d6cf705aa5727b5867990ca48c1c85b20444ff0e370da`；支持范围：同码官方中文名称，不替换英文分类树。
<a id="source-asrs-retinal-tears"></a>

- **asrs-retinal-tears** [American Society of Retina Specialists Retinal Tears](https://www.asrs.org/patients/retinal-diseases/26/retinal-tears)；定位：Symptoms（行35–36）；Diagnostic testing（行62）；Treatment and prognosis（行67–69）；读取：2026-10-02；支持范围：及时识别裂孔可在脱离前干预；部分无症状低风险裂孔可观察。仅用于编辑优先及条件，未建立全文治疗交叉核验。
<a id="source-nci-cns"></a>

- **nci-cns** [NCI Adult Central Nervous System Tumors Treatment (PDQ), Patient Version](https://www.cancer.gov/types/brain/patient/adult-brain-treatment-pdq)；定位：General information（行38–47）；Grades（行69–75）；Astrocytic tumors（行84–85）；Embryonal tumors（行101–105）；Meningeal tumors（行113–118）；读取：2026-10-02；支持范围：区分良恶性及组织类型；支持胶质母细胞瘤、髓母细胞瘤和明确恶性类别的编辑优先。儿童有独立治疗资料，不把成人治疗套给儿童；未将全部中枢肿瘤父级赋级。
<a id="source-nei-retina"></a>

- **nei-retina** [NEI Retinal Detachment](https://www.nei.nih.gov/eye-health-information/eye-conditions-and-diseases/retinal-detachment)；定位：症状及急症说明、类型（行34–49、64–68）；读取：2026-10-02；支持范围：视网膜脱离需及时评估以保护视力；不用于将视网膜囊肿、劈裂的父级兄弟类全判急症。
<a id="source-nhs-aki"></a>

- **nhs-aki** [NHS Acute kidney injury](https://www.nhs.uk/conditions/acute-kidney-injury/)；定位：2026-03-11；定义、Treatment及Complications（行13–15、68–90）；读取：2026-10-02；支持范围：急性肾损伤及早处理价值；严重性不同，不把所有AKI直接判作患者急诊等级。
<a id="source-nhs-anaphylaxis"></a>

- **nhs-anaphylaxis** [NHS Anaphylaxis](https://www.nhs.uk/conditions/anaphylaxis/)；定位：定义、Symptoms、Immediate action（行13–42）；读取：2026-10-02；支持范围：严重过敏反应快速起病且可危及生命；不推广至全部过敏疾病。
<a id="source-nhs-aorta"></a>

- **nhs-aorta** [NHS England South England acute aortic dissection SOP](https://www.england.nhs.uk/wp-content/uploads/sites/6/2024/02/South-England-Supra-regional-SOP-on-the-Acute-Management-of-Aortic-Dissections-v1.0-FINAL-1.pdf)；定位：2024-03；PDF印刷第3页 ED Guidelines for Suspected Acute Aortic Syndrome；读取：2026-10-02；支持范围：急性主动脉夹层识别与专科转诊；ICD夹层类别中既往稳定随访情况不能按标题判断现在需要急救。
<a id="source-nhs-appendicitis"></a>

- **nhs-appendicitis** [NHS Appendicitis](https://www.nhs.uk/conditions/appendicitis/)；定位：定义、症状与Risks of a burst appendix（行13–30、157–167）；读取：2026-10-02；支持范围：急性阑尾炎延误可穿孔及感染，症状有年龄和孕期差异；不覆盖慢性阑尾炎。
<a id="source-nhs-ards"></a>

- **nhs-ards** [NHS Acute respiratory distress syndrome](https://www.nhs.uk/conditions/acute-respiratory-distress-syndrome/)；定位：定义、Immediate action、Treatment（行13–43、50–61）；读取：2026-10-02；支持范围：ARDS危及生命及呼吸支持；页面复核到期不作为新治疗方案依据，仅支持稳定急症识别原则。
<a id="source-nhs-cauda"></a>

- **nhs-cauda** [Royal Free London Cauda equina syndrome](https://www.royalfree.nhs.uk/patients-and-visitors/patient-information-leaflets/cauda-equina-syndrome/submit/43795)；定位：RFL1148 v1，批准2025-01-22；What is CES?与What to do（行16–46）；读取：2026-10-02；支持范围：马尾综合征功能损害及新发相关症状及时就医；不是所有腰痛等同马尾综合征。
<a id="source-nhs-co"></a>

- **nhs-co** [NHS Carbon monoxide poisoning](https://www.nhs.uk/conditions/carbon-monoxide-poisoning/)；定位：What to do；Immediate action；Treatments（行46–77）；读取：2026-10-02；支持范围：CO暴露及时离开危险环境及获得帮助；其ICD归入宽泛NE61，不能由CO子题把该混合类别全部判P0。
<a id="source-nhs-dka"></a>

- **nhs-dka** [NHS Diabetic ketoacidosis](https://www.nhs.uk/conditions/diabetic-ketoacidosis/)；定位：定义、症状及Treatment（行13–32、70–76）；读取：2026-10-02；支持范围：DKA需要及时住院处理；本规则不新增酮体阈值或家庭用药方案。
<a id="source-nhs-ectopic"></a>

- **nhs-ectopic** [NHS Ectopic pregnancy](https://www.nhs.uk/conditions/ectopic-pregnancy/)；定位：When to get medical advice；When to get emergency help；Treatment（行36–63）；读取：2026-10-02；支持范围：异位妊娠及时诊断、破裂急救与稳定病例监测的区别；只用于稳定识别原则，不据过期复核日期页面更新用药方案。
<a id="source-nhs-epiglottitis"></a>

- **nhs-epiglottitis** [NHS Epiglottitis](https://www.nhs.uk/conditions/epiglottitis/)；定位：定义与Immediate action（行13–38）；读取：2026-10-02；支持范围：会厌炎可阻塞气道，应及时处理；不推广至所有喉炎。
<a id="source-nhs-epilepsy"></a>

- **nhs-epilepsy** [NHS Epilepsy](https://www.nhs.uk/conditions/epilepsy/)；定位：How epilepsy affects your life；Risks of epilepsy（行166–178）；读取：2026-10-02；支持范围：癫痫持续状态应及时处理；其他癫痫需治疗和支持但严重程度不同。
<a id="source-nhs-heatstroke"></a>

- **nhs-heatstroke** [NHS Heat exhaustion and heatstroke](https://www.nhs.uk/conditions/heat-exhaustion-heatstroke/)；定位：2026-05-28版；Symptoms of heatstroke（行34–45）；读取：2026-10-02；支持范围：区分热衰竭与需紧急处理的热射病；不将所有热相关疾病P0。
<a id="source-nhs-mi"></a>

- **nhs-mi** [NHS Heart attack](https://www.nhs.uk/conditions/heart-attack/)；定位：定义、Symptoms与Immediate action required（行13–32）；读取：2026-10-02；支持范围：心肌梗死紧急识别；不覆盖稳定冠心病为急症。
<a id="source-nhs-pe"></a>

- **nhs-pe** [NHS Pulmonary embolism](https://www.nhs.uk/conditions/pulmonary-embolism/)；定位：定义、症状、Urgent及Immediate action（行13–38）；读取：2026-10-02；支持范围：急性肺栓塞延误风险与按症状紧急程度处理；不支持慢性PE自动继承。
<a id="source-nhs-sjs"></a>

- **nhs-sjs** [NHS Stevens-Johnson syndrome](https://www.nhs.uk/conditions/stevens-johnson-syndrome/)；定位：2026-03-04；定义、Immediate action与Treatment（行13–17、74–95）；读取：2026-10-02；支持范围：SJS/TEN严重皮肤反应需及时医院处理；不把普通皮疹或所有药物不良反应升级。
<a id="source-nhs-stroke"></a>

- **nhs-stroke** [NHS Symptoms of a stroke](https://www.nhs.uk/conditions/stroke/symptoms/)；定位：Check for signs；Immediate action required（行14–46）；读取：2026-10-02；支持范围：新发卒中症状的时间敏感识别；不把卒中后遗症或无急性症状血管异常继承为P0。
<a id="source-nhs-sudden-hearing"></a>

- **nhs-sudden-hearing** [NHS Hearing loss](https://www.nhs.uk/conditions/hearing-loss/)；定位：2025-05-30；Urgent advice（行55–63）；读取：2026-10-02；支持范围：突发听力下降需及时评估可能可治疗的病因；不宣称所有听力下降必须叫救护车。
<a id="source-nhs-torsion"></a>

- **nhs-torsion** [NHS Testicle pain](https://www.nhs.uk/symptoms/testicle-pain/)；定位：Immediate action；Causes（行16–22、40–44）；读取：2026-10-02；支持范围：睾丸扭转的器官损害及快速处理；未推至附睾或睾丸附件扭转所有子类。
<a id="source-sja-first-aid"></a>

- **sja-first-aid** [St John Ambulance First aid advice](https://www.sja.org.uk/first-aid-advice/)；定位：Advice categories；How to do CPR；Choking；Severe bleeding（网页行124–173）；读取：2026-10-02；支持范围：心搏停止与窒息识别的急救教育；NHS原first-aid链接已重定向至SJA，不计作两个独立来源。
<a id="source-who-cancer"></a>

- **who-cancer** [WHO Cancer](https://www.who.int/news-room/fact-sheets/detail/cancer)；定位：2026-07-03；Early detection；Treatment（行144–174）；读取：2026-10-02；支持范围：恶性肿瘤早诊、分型及及时适当治疗；筛查并非对所有癌症有效，不将此依据用于把良性肿瘤定义成癌症。
<a id="source-who-congenital"></a>

- **who-congenital** [WHO Congenital disorders](https://www.who.int/news-room/fact-sheets/detail/birth-defects)；定位：Screening, treatment and care（行131–154）；读取：2026-10-02；支持范围：先天异常早发现、转诊和支持的家族层理由；只有部分疾病有特异可治疗干预，各国筛查不同。
<a id="source-who-dengue"></a>

- **who-dengue** [WHO Dengue](https://www.who.int/news-room/fact-sheets/detail/dengue-and-severe-dengue)；定位：2025-08-21；Key facts；Symptoms（行87–131）；读取：2026-10-02；支持范围：登革热媒介控制与严重登革热的迅速处理；多数病例轻症，未将全登革热父级定P0。
<a id="source-who-emergency"></a>

- **who-emergency** [WHO Emergency and critical care](https://www.who.int/health-topics/emergency-care)；定位：Overview；Impact（网页行86–95）；读取：2026-10-02；支持范围：急性病和损伤早识别、时间敏感照护的原则；具体P级为项目编辑决策，不是WHO分类排名。
<a id="source-who-ghe"></a>

- **who-ghe** [WHO The top 10 causes of death](https://www.who.int/news-room/fact-sheets/detail/the-top-10-causes-of-death)；定位：2026-10-02版；Leading causes of death globally；收入组差异；Editor’s note（行83–143）；读取：2026-10-02；支持范围：2023年汇总死因资料支持心血管、慢阻肺、下呼吸道感染、糖尿病、痴呆、肾病家族的选题顺序；不支持每个ICD叶类别的死亡负担。
<a id="source-who-hearing"></a>

- **who-hearing** [WHO Deafness and hearing loss](https://www.who.int/news-room/fact-sheets/detail/deafness-and-hearing-loss)；定位：Identification and management；Rehabilitation（行165–185）；读取：2026-10-02；支持范围：听力障碍早识别及沟通康复；不把全部听力障碍判为急性耳科急症。
<a id="source-who-icd-2026"></a>

- **who-icd-2026** [WHO ICD-11 MMS 2026-01 official tabulation](https://icdcdn.who.int/static/releasefiles/2026-01/SimpleTabulation-ICD-11-MMS-en.zip)；定位：本地冻结catalog.json.gz；chapter/class_kind/code/foundation_uri/parent_uri/is_leaf；manifest.json中的官方ZIP哈希；读取：2026-10-02；支持范围：分类结构与精确选择器依据；不提供本站编写优先等级。
<a id="source-who-immunization"></a>

- **who-immunization** [WHO Immunization and vaccine-preventable communicable diseases](https://www.who.int/data/gho/data/themes/immunization)；定位：Immunization coverage estimates；Vaccine-preventable diseases（行110–155）；读取：2026-10-02；支持范围：可疫苗预防病种的公共卫生价值与疾病列表；各地接种方案需要另行核对。
<a id="source-who-infection-programmes"></a>

- **who-infection-programmes** [WHO HIV, tuberculosis, hepatitis and STI guidelines](https://www.who.int/teams/global-hiv-hepatitis-and-stis-programmes/guidelines)；定位：部门目标；Guidelines（行78–88）；读取：2026-10-02；支持范围：上述四个感染领域的预防、诊断、治疗与人群公平可及优先；本次只读总览，不声称已阅读链接内所有指南。
<a id="source-who-malaria"></a>

- **who-malaria** [WHO Malaria](https://www.who.int/news-room/fact-sheets/detail/malaria)；定位：2025-12-04；Overview；Symptoms（行95–125）；读取：2026-10-02；支持范围：疟疾家族可预防可治疗；严重症状需迅速处理，儿童和孕产妇有特定风险；不推算各虫种负担。
<a id="source-who-malnutrition"></a>

- **who-malnutrition** [WHO Malnutrition](https://www.who.int/news-room/fact-sheets/detail/malnutrition)；定位：2024-03-01；Key facts；Overview；Undernutrition（行82–105）；读取：2026-10-02；支持范围：营养不足和肥胖相关的家族负担及儿童发展影响；不将所有微量元素亚型断言为常见。
<a id="source-who-maternal"></a>

- **who-maternal** [WHO Maternal mortality](https://www.who.int/news-room/fact-sheets/detail/maternal-mortality)；定位：2025-04-07；Why do women die?；How can women’s lives be saved?（行100–114）；读取：2026-10-02；支持范围：妊娠、分娩及产后连续照护；出血、感染、子痫特异急症优先；不声称所有产科类别同等严重。
<a id="source-who-meningitis"></a>

- **who-meningitis** [WHO Meningitis](https://www.who.int/news-room/fact-sheets/detail/meningitis)；定位：2026-09-29；Diagnosis；Treatment；Prevention（行133–164）；读取：2026-10-02；支持范围：脑膜炎迅速识别及细菌病因及时治疗；不同病原、传播、年龄及免疫状态的差异。
<a id="source-who-mental"></a>

- **who-mental** [WHO Mental health](https://www.who.int/health-topics/mental-health)；定位：Overview；Impact；WHO Response（行83–103）；读取：2026-10-02；支持范围：精神健康家族功能损害、治疗缺口和有效照护；非每个亚型的定量负担或危险性。
<a id="source-who-msk"></a>

- **who-msk** [WHO Musculoskeletal health](https://www.who.int/news-room/fact-sheets/detail/musculoskeletal-conditions)；定位：2022-07-14；Key facts；Scope（行82–97）；读取：2026-10-02；支持范围：肌肉骨骼家族的功能和参与受限；列明骨关节炎、类风湿、腰痛、骨质疏松等；不外推每个罕见亚型患病率。
<a id="source-who-ncd"></a>

- **who-ncd** [WHO Noncommunicable diseases](https://www.who.int/news-room/fact-sheets/detail/noncommunicable-diseases)；定位：2025-09-25；Key facts；Prevention and control（行83–101、131–136）；读取：2026-10-02；支持范围：心血管、癌症、慢性呼吸疾病、糖尿病的检测、预防和管理价值；家族层证据。
<a id="source-who-newborn"></a>

- **who-newborn** [WHO Newborn mortality](https://www.who.int/news-room/fact-sheets/detail/newborn-mortality)；定位：2024-03-14；Key facts；Causes；Priority strategies（行87–105）；读取：2026-10-02；支持范围：围产期家族保护与及时照护；窒息、感染等具体死亡原因；不把新生儿所有问题一律定为急症。
<a id="source-who-oral"></a>

- **who-oral** [WHO Oral health](https://www.who.int/news-room/fact-sheets/detail/oral-health)；定位：2025-03-17；Key facts；Overview；Dental caries；Periodontal disease（行86–102）；读取：2026-10-02；支持范围：龋病和牙周病的预防、早期治疗及口腔功能；不以口腔总体人数作为单个子类人数。
<a id="source-who-sepsis"></a>

- **who-sepsis** [WHO Sepsis](https://www.who.int/news-room/fact-sheets/detail/sepsis)；定位：2024-05-03；Overview；Signs and symptoms；Treatment（行94–120、155–164）；读取：2026-10-02；支持范围：脓毒症为医学急症；感染相关器官损害与及时处理；含母婴相关风险。
<a id="source-who-suicide"></a>

- **who-suicide** [WHO Suicide](https://www.who.int/news-room/fact-sheets/detail/suicide)；定位：Prevention and control（行98–127）；读取：2026-10-02；支持范围：及时识别、评估、管理和随访自杀相关行为；自杀意念条目用于危机识别知识，不能据此判定每位读者均处于即刻危险。
<a id="source-who-tb"></a>

- **who-tb** [WHO Tuberculosis](https://www.who.int/news-room/fact-sheets/detail/tuberculosis)；定位：2026-03-24；Overview；Prevention（行94–114、128–142）；读取：2026-10-02；支持范围：结核家族早诊及传播预防；明确感染与活动性疾病、部位及传染性不同。
<a id="source-who-vision"></a>

- **who-vision** [WHO Blindness and vision impairment](https://www.who.int/news-room/fact-sheets/detail/blindness-and-visual-impairment)；定位：Overview；Causes（行94–114）；读取：2026-10-02；支持范围：白内障、屈光问题、糖尿病视网膜病、青光眼和老年黄斑变性的功能损害与及时照护；各病治疗和筛查仍分别核对。

WHO原文标题、代码与URI保持不变；编辑归口、优先级、医学考虑及排程属于项目添加。优先级生成不会改变类别覆盖或医学签审。
