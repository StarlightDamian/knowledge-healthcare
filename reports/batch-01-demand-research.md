# 首批需求主题：作者研究与证据整理

日期：2026-09-30。作者角色：`/root/demand_content`。这是作者交付记录，不是独立对抗审核或执业医生签审。七篇均保留 `editorial_draft`、章节 `pending_claim_verification`、编辑证据 `pending`、医学签审 `false`。

## 保存范围与结构检查

| 规范主题 | 类型 | 双语章节 | 主张条目 |
|---|---|---:|---:|
| ADHD | 疾病 | 14 | 57 |
| 甲状腺结节 | 疾病主题 | 14 | 56 |
| MASLD | 疾病主题 | 14 | 51 |
| 子宫内膜异位症 | 疾病 | 14 | 55 |
| 围绝经期症状 | 症状入口 | 14 | 52 |
| 玫瑰痤疮 | 疾病主题 | 14 | 52 |
| 脱发 | 症状入口 | 14 | 56 |

现有 ADHD、甲状腺结节及 MASLD 草稿保留；本轮补齐后四篇，并为 MASLD 增加原先缺少的 14 节编辑记录。将前两篇“每条主张复制全节来源”的记录改为逐条定位；来源只支持其 assessment 描述的实际范围。七篇合计 98 节、379 条主张。正文仍以 `section.text` 为唯一文本来源，主张清单逐段对应正文，用于证据核对。

2026-09-30 本地检查通过：七篇条件 schema、全部来源 schema、现有科室/领域 ID、98 个唯一编辑目标、正文与来源哈希、双语段落数量、真实待审状态。此检查验证结构，不证明医学内容已获交叉接受。没有改全局 `data/`，没有提交、推送或部署。

## 实际阅读资料与取舍

完整网址、访问方式、版本、机构和版权范围见 `drafts/batch-01/demand-sources.json`；逐主张章节定位、支持边界和缺口见 `drafts/batch-01/demand-editorial.json`。

- **ADHD**：重新阅读 NIMH 2024 两份患者资料、APA *Symptoms and Diagnosis*、CDC 2026-07-30 治疗资料、NHS 儿童及成人页面、成人哌甲酯副作用页、FDA 2023 兴奋剂警示；NICE NG87 以官方索引正文核对诊断、饮食、监测和转衔条款。年龄分组、症状组计数、持续时间及多场景条件由 NIMH/APA 对应，不能用当前 CDC 页面补不存在的计数。成人哌甲酯急救资料只支持该药及成人范围，不能称其独立支持所有兴奋剂、所有年龄的全部过量表现。
- **甲状腺结节**：阅读 ATA 结节、FNA、儿童结节、甲状腺激素、低碘及直接妊娠甲亢资料，NHS goitre，NIH ODS 碘资料；NICE NG145 推荐与 rationale、MSK 低碘患者说明通过官方索引正文阅读。ATA 妊娠目录入口不能支持具体核素限制，已补直接 brochure。低碘治疗准备由 ATA 与 MSK 对应；NICE 的复查条件与 ATA 患者资料分开记录。ATA 的骨与心律风险有原文，NICE 本段只直接交叉支持心血管风险，骨风险仍留第二来源缺口。
- **MASLD**：阅读 NIDDK 定义、症状、诊断、治疗、饮食、儿童治疗与肝硬化治疗资料，NHS 肝硬化急救行动，EASL–EASD–EASO 2024 原始 PDF 的定义、风险、非侵入检查、生活干预和营养章节；FDA 2024 resmetirom 公告及现行加速批准表、2025 Wegovy 公告。NIDDK 2021 页仍有“没有获批药物”的过期资料，该句不采用。2024 EASL 不能验证 2025 新批准；多个 FDA 网址仍算同一机构，药物批准关键主张保留独立第二来源缺口。
- **子宫内膜异位症**：阅读 WHO 2025-10-15、NHS 2024-08-27、RCOG 2023-12 患者资料、ESHRE 2022 患者指南 PDF 第 12–16 页、NICHD 治疗资料、Mayo 症状资料，以及 NICE NG73 官方索引正文。急性盆腔痛另查 NHS 2025-11-24 与 Mayo 2026-05-12；NSAID 风险查 ASHP/MedlinePlus。临床工作诊断及可先治疗依据新版 WHO/NICE，未采用 NICHD 2020 “只有手术才能确认”作为开始全部诊疗的前提。RCOG 引用 NICE/ESHRE，来源编写独立不等于底层研究独立。
- **围绝经期症状**：阅读 WHO 2024-10-16、NHS 2026-05-19 系列、OWH 2025–2026 基础/症状/早绝经/治疗资料，以及 NICE NG23 2026-04-15 官方索引正文。HRT 还阅读 NHS 2023 风险及复查页面，版本较旧已保留。OWH 治疗页的低剂量 SSRI 批准表述有疑点，未用于写具体药名；不能把其药名列表当最新批准清单。NHS 旧页局部雌激素“无乳癌风险”的绝对表达未采用，既往乳癌条件以 NICE 最新分层讨论保留不确定性。POI 与自然绝经、生育可能性不能简单画等号。
- **玫瑰痤疮**：阅读 NIAMS 2024 基础与照护、AAD 2024 诊断治疗与护肤/诱因、儿童资料、DermNet 2024 主页面与旧版眼部页面、NHS 2023 患者页面及 2025 多西环素页面。按炎症丘疹、潮红血管、增厚和眼部表现区分治疗。AAD 明确可通过环境和强度调整保持运动，未机械采用 NHS 的广泛避免有氧活动表述。深肤色可能识别不足；不同来源性别比例差异不编成统一统计。皮肤制剂不得直接用于眼睛的具体警示目前只有 AAD，保留缺口。
- **脱发**：阅读 AAD 病因/治疗/护理、NHS 2024、DermNet 2023 总览与头癣、NIAMS 2024 斑秃系列、ASHP 外用米诺地尔资料、NHS 非那雄胺资格/副作用、MHRA 2024-04-29 安全更新。ASHP 米诺地尔页版本为 2017，只用于外用安全和基本用法，不承担最新疗效比较。MHRA 与 NHS 同属英国公立资料但编写职能不同，药物警示可能共享安全通报；不能称为两次独立临床试验。部分复合行动的两份材料只各支持部分句子，仍待逐项独立审读。

ACOG 子宫内膜异位症页面返回访问限制，未以未读内容支持主张。NICE 若直接网页无法读取，则明确使用实际返回的官方索引推荐正文；不将链接打开失败写成全文阅读。来源版本说明保留页面最后审订信息，版权页年份不冒充医学更新日期。

## MECE 归属

- ADHD 不因泛主题提及 inattentive、hyperactive-impulsive 或 combined 就覆盖全部 ICD 子类。
- 甲状腺结节不是甲状腺癌、甲亢或甲状腺炎的同义词；分别说明“结构”和“功能”的问题，不把癌症地图计为具体癌正文。
- MASLD 保留当前规范 ID；旧 NAFLD/NASH 名称只作术语关系，酒精共同病因和 MASH 阶段不能机械合并为同一个人群。
- 子宫内膜异位症不把子宫腺肌病作为别名；共同盆腔痛入口负责分流。
- 围绝经期是生命周期变化中的症状入口，生活方式通用因素不另算疾病覆盖；阴道出血异常、POI 等仍需要自己的分类和评估。
- 玫瑰痤疮按表现解释，但单篇总览不自动完成每个 ICD 叶类。
- 脱发是症状入口，斑秃、遗传性、休止期、真菌感染、牵拉与瘢痕病因分别分流；没有把它们都叫作“营养不足”，也没有统一生发处方。

七篇 `coding` 均保持空数组，交由全目录映射裁定；不据此增加完整叶类覆盖分子。

## 剩余核查与发布边界

1. 所有正文需要未参与撰写者的独立原文复核。来源数量只是结构信号；两份材料各支持半句话不能冒充整条关键行动获得两份支持。
2. 编辑记录的 `unresolved_questions` 保留每条缺少第二独立来源及复合条件支持不足的问题，特别是药物急救、FNA 多结节选择、儿童标准、骨风险、儿童/妊娠药物以及术后护理。
3. 目前实读资料主要为 WHO、美国、英国及欧洲/新西兰机构。没有实读确认的中国批准状态、诊断门槛和就医流程，不得推定已经完成国际并列核查；这仍是本批地区证据缺口。
4. 对手册版本陈旧、机构间条件不同及可能共享上游依据的情形保留说明。没有新增处方剂量、个体化用药或自行诊断计算。
5. 全部为自行撰写的中英解释和短定位，不转载指南/PDF 全文、表格或图片。ASHP 通过 MedlinePlus 展示不等于 NIH 公共领域作品；AAD、ATA、NICE、DermNet 等各自保留版权，未再分发第三方全文。

下一步先处理独立审查发现的具体主张缺口，再由发布流程判断哪些文章可计入“交叉核验完整正文”。本作者不能把自己的 `pending` 改为通过，也不能把编辑核验描述成医生签审。


## ADHD 独立审查后的作者修订（2026-09-30）

- 依据 `reports/batch-01-adhd-independent.json` A01–A07 修订；旧正文哈希 `c42b451922c41634845de292d6b9babe85c04d37c012e8e1a4575259e44e19cb`，本次 `f15fbfb04100fe5400b801f0b92937f07a98074e1bdb071fe6874745f620656f`。独立报告未改写，作者不能自行接受修订。
- A01：成人与儿童哌甲酯材料分开；胸痛／抽搐、疑似过量、无症状过量咨询及持续副作用分别定位。FDA 的兴奋剂全类警示与 ASHP 的哌甲酯范围分别记录，没有把成人网页外推至儿童或所有药物。
- A02：保留 NIMH＋APA 实读支持的 DSM 分组计数（16岁及以下6项，17岁及以上5项）、6个月、两个场合和12岁前；发展水平、药物相似表现及治疗前药物史另列。网上测验属于完整评估原则的应用，未声称经过单独验证。
- A03：所有 NIMH 页面归 NIH 同一编写组，所有 NHS 页面归 NHS 同一组。ASHP 是 MedlinePlus 药物材料的实际编写者，归 ASHP，不以托管网站归 NIH。明确 CDC／APA 共同 AAP 与 DSM 上游；美国6岁以下和英国5岁以下路径逐条分开。
- A04–A05：删除无具体支持的餐点便利性比较；饮食记录、排除饮食限定儿童／青少年。固定物品位置和药物安全储存分开；共存睡眠问题、失眠的白天影响、药物包装与用药清单分条，支持来源不互相冒充。保留睡眠、焦虑、抑郁、阅读困难和急性混乱的鉴别信息。
- A06–A07：饮食、监测、复诊、行为支持按 action／risk／benefit 记录；早产保留 APA＋NHS 关联证据，压力及睡眠改为鉴别原因；预防首段限定文章范围，不伪装无预防研究的系统性结论。
- 新增13份实际阅读来源，均为自行中英转述；版权归原机构，ASHP不是NIH公共领域材料。逐项URL见下方及 `demand-sources.json`，精确章节、适用人群、来源版本见 `demand-editorial.json`。NICE官方网页在浏览工具失败后通过官方HTTPS HTML读取了1.1.4–6、1.3.1–6、1.5.7–18、1.6.1–5、1.7.4–5、1.8.1–19和1.10.1–3；没有把失败访问计作阅读。

- [Methylphenidate — AHFS Patient Medication Information](https://medlineplus.gov/druginfo/meds/a682188.html)：Important Warning, precautions, side effects, child growth, storage and emergency/overdose. ASHP authorship distinct from NIH hosting.
- [Side effects of methylphenidate for children](https://www.nhs.uk/medicines/methylphenidate-children/side-effects-of-methylphenidate-for-children/)：Common/serious and immediate-action effects and child growth; children taking methylphenidate only.
- [How and when to take methylphenidate for children](https://www.nhs.uk/medicines/methylphenidate-children/how-and-when-to-take-methylphenidate-for-children/)：Formulation food instructions, continuation/review, overdose, medicine packets and safe storage; no doses reproduced.
- [How and when to take methylphenidate for adults](https://www.nhs.uk/medicines/methylphenidate-adults/how-and-when-to-take-methylphenidate-for-adults/)：Formulation instructions, review/stopping, overdose even without symptoms, serious signs, packets; adult scope.
- [Common questions about methylphenidate for children](https://www.nhs.uk/medicines/methylphenidate-children/common-questions-about-methylphenidate-for-children/)：Treatment-programme role, brand differences, limited omega evidence; did not adopt categorical no-harm wording.
- [Frequently Asked Questions About Suicide](https://www.nimh.nih.gov/health/publications/suicide-faq)：2023 publication23-MH-6389: warning signs, crisis/immediate-danger response and not leaving a person stating suicidal intent alone.
- [Help for suicidal thoughts](https://www.nhs.uk/mental-health/feelings-symptoms-behaviours/behaviours/help-for-suicidal-thoughts/)：Trusted support; imminent/serious harm emergency and being around others; UK numbers not generalized globally.
- [Insomnia](https://www.nhs.uk/conditions/insomnia/)：Symptoms: daytime fatigue and concentration difficulty; differential explanation only.
- [Generalised anxiety disorder](https://www.nhs.uk/mental-health/conditions/generalised-anxiety-disorder-gad/)：Symptoms: uncontrollable worry and concentration difficulties; explicitly adults18+.
- [Depression in adults — Symptoms](https://www.nhs.uk/mental-health/conditions/depression-in-adults/symptoms/)：Low mood and lost interest; review-due July2026 passed, retained dated description pending current review.
- [Dyslexia in children](https://www.nhs.uk/conditions/dyslexia-in-children/)：Signs and assessment; reading/writing/spelling difficulties differ from generic ADHD label.
- [Sudden confusion (delirium)](https://www.nhs.uk/symptoms/confusion/)：Recognition, immediate emergency action, medicines and causes; not all forgetfulness is an emergency.
- [Delirium — Symptoms and causes](https://www.mayoclinic.org/diseases-conditions/delirium/symptoms-causes/syc-20371386)：Overview, Poor thinking skills, When to see a doctor; rapid clinical evaluation, not literal second endorsement of NHS emergency route.

本次14节、98条绑定中英正文的主张；新增来源13份。每项支持只列实际相关定位，章节来源由这些主张汇总。NHS成人抑郁页面显示的2026-07-05复核日期已过，保留其日期及描述范围，需更新复核。

剩余缺口包括：哌甲酯无过量胸痛／抽搐的完全同等急诊路径、无症状过量限定语、包装与用药清单、饮食排除和少数食物长期证据、品牌与进食、睡眠日记、服务过渡、若干具体生活调整，以及全兴奋剂类警示的第二独立编写支持。仅一个编写来源的行动／风险／获益主张：red_flags-6, red_flags-7, care-4, treatment-5, diet-3, diet-5, daily_care-3, daily_care-5, daily_care-6, prognosis_followup-4, complications-3, complications-4。具体限制已写入各节 `unresolved_questions`，不能仅凭有两个网址宣称交叉核验完成。

保存前通过condition/source JSON Schema、14节结构、双语逐主张正文绑定、来源元数据哈希及其他六篇证据记录不变检查。全部章节继续 `pending`，`adversarial_review.pending`，`medical_reviewed=false`；正文仍 `editorial_draft`，不进入覆盖分子。本轮未修改生产数据、测试、独立报告或Git索引。


## MASLD 独立审查后的作者修订（2026-09-30）

- 对应 M01–M08：旧正文 `7792e270a8b96ba750bdfeb88d1e010ab18d153c2c76ca30a4183f464ee48b1c`，新正文 `dff08711ecfcb62c0f0e03e8784165bddb09a9addc2d1933604472fa265ec1a4`。保持独立报告原样，不自行接受。
- M01：体重／腰围代谢评估与 FIB-4 分开；中英均明确输入为年龄、AST、ALT、血小板，EASL印刷p10及AASLD官方教学页第2节相互核对。未增加评分计算器或自行诊断阈值。
- M02／M08：resmetirom与Wegovy分条说明人群、作用和边界。补GI不适、肝胆风险、他汀相互作用、Wegovy甲状腺髓样癌／MEN2条件、腹痛就医和孕期讨论。美国成人非肝硬化MASH F2–F3条件写明；补EMA确认的欧盟resmetirom有条件批准（2025-08-18）。中国、英国及其他地区批准未核验，不能宣称相同。
- 药物版本：当前FDA批准表、2026年7月resmetirom美国标签及EMA于2026-05-27更新的产品资料已读；Wegovy使用FDA公告链接的2025年8月MASH标签，并不声称它是2026年最新完整说明书。该版MASH孕期条件为获益／胎儿风险权衡，不能把普通减重停药规则无条件外推。
- M03：一般人群呕血／柏油便及休克行动由Mayo＋NIDDK急性GI出血资料支持；肝硬化意识变化、黄疸／肿胀／气短行动保留其“已确诊肝硬化”条件，仍有单来源问题。
- M04／M05：中英统一较大且持续减重条件；饮食中的advanced fibrosis统一为“进展期纤维化”。运动无显著减重仍有益改绑EASLpp21–22。检查局限、活检、代谢治疗、移植与减重手术分开；肝酶正常的精确定位为EASLp5，不再指向评分公式。
- M06／M07：新增精确来源定位，饮食／记录／监测等行动按action登记。正常体重与营养不良分开；记录行为不再声称比体重数字更有效。随访和部分原有复合主张保留明确证据缺口，未为了凑双源机械删掉医学知识。
- 独立性：NIH所有页面算一组；FDA公告、批准表及美国监管标签保守归一组；EASL/EASD/EASO为一份联合指南。ASHP药物资料的实际作者不是托管者NIH。EMA/FDA标签和评估共享厂商材料及关键研究，不能当成独立试验重复验证。

本轮新增实际阅读来源10份：

- [Spare Me the Jab: Noninvasive Assessment of Patients with MASLD](https://www.aasld.org/liver-fellow-network/core-series/clinical-pearls/spare-me-jab-noninvasive-assessment-patients-masld)：Clinical Pearls; primary/secondary risk assessment, exact FIB-4 inputs, age limitations and biopsy indications; read on2026-09-30. Linked PMC guidance was blocked and publisher fetch failed; neither failure is counted as full reading.
- [Resmetirom — AHFS Patient Medication Information](https://medlineplus.gov/druginfo/meds/a624021.html)：Why prescribed, precautions, common/serious side effects, pregnancy and follow-up; no dosing schedule reproduced. ASHP authorship, not NIH authorship.
- [Semaglutide injection — AHFS Patient Medication Information](https://medlineplus.gov/druginfo/meds/a618008.html)：Important Warning, uses including noncirrhotic MASH, mechanism, precautions, adverse effects and pregnancy. General monograph does not independently state every brand-specific F2-F3 or MTC criterion.
- [Wegovy prescribing information — MASH indication revision](https://www.accessdata.fda.gov/drugsatfda_docs/label/2025/215256s024lbl.pdf)：August2025 MASH label linked from FDA approval page; sections1,4,5.1-5.4,8.1 and patient counselling read. Versioned label, not claimed latest full-label revision in2026.
- [Rezdiffra — European public assessment overview](https://www.ema.europa.eu/en/medicines/human/EPAR/rezdiffra)：Overview, mechanism, benefits/risks, conditional approval and therapeutic indication; EU authorisation18August2025; same pivotal resmetirom programme as FDA.
- [Rezdiffra product information](https://www.ema.europa.eu/en/documents/product-information/rezdiffra-epar-product-information_en.pdf)：SmPC and package leaflet: indication, warnings, interactions, pregnancy and adverse effects; primarily leaflet sections1-4 printedpp31-34. Shared sponsor labelling is disclosed, not independent trial replication.
- [Rezdiffra US prescribing information — July2026](https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=e67ea09f-a840-439c-86c8-f98585f978b2)：RevisedJuly2026; sections1,5.1-5.3,7 and patient information read. Conservatively grouped with FDA regulatory material; DailyMed hosting does not make it a second NIH-authored source.
- [Gastrointestinal bleeding — Symptoms and causes](https://www.mayoclinic.org/diseases-conditions/gastrointestinal-bleeding/symptoms-causes/syc-20372729)：Symptoms of shock and When to see a doctor; vomiting blood/black tarry stool immediate care, shock emergency; not restricted to established cirrhosis.
- [Symptoms and Causes of Gastrointestinal Bleeding](https://www.niddk.nih.gov/health-information/digestive-diseases/gastrointestinal-bleeding/symptoms-causes)：Last reviewedJuly2024: acute bleeding and shock symptoms/actions read; same NIH group as cirrhosis pages.
- [Symptoms and Causes of Diabetes](https://www.niddk.nih.gov/health-information/diabetes/overview/symptoms-causes)：Last reviewedOctober2024: What causes type2 diabetes, insulin resistance definition; same NIH authorship as MASLD pages.

共14节、80条中英主张。单来源行动／阈值／风险／获益仍有：causes_risks-3, causes_risks-5, red_flags-2, red_flags-3, care-1, diagnosis-4, diagnosis-6, differentials-2, treatment-2, treatment-4, treatment-6, medications-6, diet-2, diet-4, diet-7, daily_care-0, special_populations-2, special_populations-4, prognosis_followup-2。另外，完整的Wegovy禁忌和F2–F3批准条件、药物孕期MASH特例、他汀相互作用的共享标签来源、部分饮食／儿科／随访条件仍需独立逐条确认，详见每节 `unresolved_questions`。普通网页有两个链接不等于这些全部通过。

保存前检查：condition/source Schema、逐主张双语正文绑定、章节与来源哈希、14条pending记录、零合格覆盖章节均通过；其他六篇（包括最新ADHD）正文和证据记录、既有来源元数据及独立报告均保持不变。原始EASL PDF截图调用未返回可见图像，因此公式和推荐按可读取PDF文字核对；AASLD正式论文PMC访问受验证码限制、出版商链接失败，未把这两次访问算作全文阅读，改读AASLD官方专业教学正文。仅写4个授权文件，未提交、上线或改生产数据。

磁盘回读复核：14节80条主张、22份关联来源，JSON Schema及正文／来源哈希绑定通过，editorial-audit issues为0、qualified_sections为0。新增分类修正：危险信号导读、持续腹痛就医、地区产品核对、饮食随访记为action；加速批准长期结局未确定记为risk。diet-7因此纳入单来源行动缺口。再次核对ASHP resmetirom及2026年7月美国标签的严重不适就医、医生按疑似肝毒性决定停药段落，正文保持。限定4文件的 `git -c core.whitespace=cr-at-eol diff --check` 通过；共享文件diff还包含之前ADHD修订，不应把全部diff量算作本次MASLD。


## MASLD 定向复核绑定修复（2026-09-30）

- 按 `reports/batch-01-masld-recheck.json` MR03，仅恢复此前实际阅读的定位：`differentials-1` → NIDDK Other causes；`complications-0` → NIDDK Complications 与 EASL 印刷pp4–7自然史／心脏代谢风险。同步章节汇总支持，正文80条内容不变。
- 按MR02，resmetirom美国／欧盟产品标签的实际编写方均为Madrigal，`independence_group`统一为`MADRIGAL-PHARMACEUTICALS`，并同步来源元数据哈希和支持记录。FDA自己编写的公告／批准表及EMA自己编写的overview保持其机关来源组；底层共享厂商与MAESTRO研究明确记录，不能按域名把同一标签算两个编写来源。
- Wegovy MASH孕期例外仍保留已记录的单FDA缺口；不改为通用停药条件，不补造双源。其他风险、行动和阈值缺口保持。
- 无需重复检索未变医学内容。只修改两份共享来源／证据JSON和本日志；MASLD正文文件未改，其他6篇／其证据、两份独立报告均逐哈希保护。当前正文canonical哈希仍为 `dff08711ecfcb62c0f0e03e8784165bddb09a9addc2d1933604472fa265ec1a4`。
- 保存前Schema、章节／来源哈希绑定、editorial-audit通过：14条pending、80条主张、0合格章节、医学签审false。此为作者证据绑定修复，尚未独立接受；未提交、推送或上线。
