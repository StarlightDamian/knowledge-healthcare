# 生命周期研究导入记录

本记录对应 `data/knowledge/lifecycle.json`，整理日期为 2026-09-29。完整阅读源文档后，将 14 项复合因素和阶段/监测章节拆分为 20 个唯一因素；年龄路径引用因素，保留本阶段独有的照护安排与求医条件。

## 源文档与版本

- 源文件：`C:\Users\Damian\Desktop\research-report\全生命周期中对人类健康影响最大的可测量因素：全球证据综合与分阶段行动框架.md`
- 源文件 SHA-256：`a5df2c5697effdbd05d38d939a42466e8b27126c0ddc51e9098e71e16862a78a`
- 已阅读范围：执行摘要、检索策略与证据标准、MECE 框架与评分方法、全生命周期因素排序、全部生理阶段、第一性原理机制、监测框架及局限。
- 文档内部 `turn…` 引用未作为来源导入。新增知识以实际核对的官方患者教育、指南说明或原始研究摘要为依据；下面记录核对位置。
- 原报告按权重合成的排名、简化 GRADE 式 A/B/C/D 及作者综合分数未导入为官方评分，也未建立个人健康分数或寿命预测。页面仅在 `reading-evidence` 集中解释这些证据尺度的差别。
- 审核状态保留为 `editorial`；本次是有来源的编辑整理，没有生成临床签审记录。

## 原报告到唯一因素的映射

| 原文位置/复合主题 | 唯一因素 ID | 唯一组 | 归属与取舍 |
|---|---|---|---|
| 遗传、家族史、先天与早期发育背景；婴幼儿证据重点 | biological-susceptibility | susceptibility | 家族史与出生记录、检测问题和发育支持；不建立遗传分数。 |
| 饮食质量、母婴营养；孕产期证据重点 | nutrition | nutrition-metabolic | 食物与喂养行为、适龄营养和叶酸；体型测量另归生长。 |
| 血压；成年与老年证据重点 | blood-pressure | nutrition-metabolic | 血管压力、记录与治疗证据；诊疗细节引用 hypertension。 |
| 血糖、胰岛素抵抗；孕产期证据重点 | blood-glucose | nutrition-metabolic | 检查类型、确认与孕期解释；诊疗引用 type-2-diabetes。 |
| LDL-C、ApoB等脂质负担 | blood-lipids | nutrition-metabolic | 解释核心血脂指标及试验证据；未把全部专科检测设为全民常规目标。 |
| 脂肪量、脂肪分布、生长轨迹 | adiposity-growth | nutrition-metabolic | 成人 BMI/腰围与儿童年龄别生长；不把单一体重当完整健康状态。 |
| 烟草与二手烟 | tobacco | behavior | 本人使用与二手烟暴露、依赖和戒烟支持。 |
| 酒精及其他成瘾物质 | alcohol-substances | behavior | 摄入模式、日常功能与戒断行动；依赖者突然停酒的风险保留。 |
| 体力活动、心肺适能、肌力；各阶段活动建议 | physical-activity | behavior | 只拥有活动行为、久坐、活动时长与安排；实测功能归 functional-reserve。 |
| 睡眠时长、质量、节律 | sleep | behavior | 睡眠记录、质量和官方年龄参考时长；诊疗引用 insomnia。 |
| 空气污染、铅及其他有毒暴露中的空气部分 | air-pollution | environment | PM2.5与空气暴露、时段解释和减少暴露；全部年龄阶段和孕产期均引用。 |
| 空气污染、铅及其他有毒暴露中的物质部分 | toxic-exposures | environment | 铅、一氧化碳等按物质区分检查与应对；不与环境颗粒物合成剂量。 |
| 各生理阶段安全、热环境与监测框架的伤害预防内容 | safe-environment | environment | 提取道路、居家、婴儿睡眠与高温安全；跌倒能力测量仍归功能。 |
| 社会经济地位、教育、童年逆境；机制与监测框架 | social-resources | structure | 食物、住房、费用、交通和支持机会；医疗实际使用归 medical-access。 |
| 疫苗与预防医疗可及性中的疫苗部分 | vaccination | preventive-care | 接种记录、免疫记忆与适用程序；各地程序不合并成全球统一表。 |
| 疫苗与预防医疗可及性中的服务部分；孕产照护 | medical-access | preventive-care | 服务利用、结果跟进、转诊与连续照护；经济和社会障碍归资源。 |
| 心理健康、认知刺激与社会联结中的心理部分 | mental-health | psychosocial | 困扰、功能、认知变化及求助；不使用单项量表自动诊断。 |
| 心理健康、认知刺激与社会联结中的关系部分 | social-connection | psychosocial | 区分客观接触和主观孤独，以意愿、支持和关系质量安排联系。 |
| 体力活动、心肺适能、肌力中的实测能力；老年证据重点 | functional-reserve | function | 移动、自理、感觉、跌倒等可观察能力；锻炼行为指向活动因素。 |
| 老年与高龄、监测框架中的用药安全内容 | medication-safety | preventive-care | 集中药物清单、相互作用、症状与复核；不建立重复行为组药物条目。 |

“第一性原理机制”分配至各因素的机制章节，保留病理过程与环境/行为联系；原文用于解释的累积损伤表达式未改造成计算公式。营养负责吃什么和如何喂养，生长负责测得的体型轨迹；活动负责做了什么，功能负责目前能做到什么。医疗服务实际利用、社会条件和用药复核分别只有一个正文所有者。

## 阶段映射与互斥边界

| 阶段 ID | 年龄/类型 | 原文对应部分与阶段独有内容 |
|---|---|---|
| age-0-4 | 0–4 岁 | 婴幼儿证据重点：出生/早产记录、发育与喂养的照护交接、能力落后或丢失后的评估。 |
| age-5-17 | 5–17 岁 | 儿童与青少年：家庭学校协调、自主表达、功能与心理变化、暴力和自伤危险求助。 |
| age-18-39 | 18–39 岁 | 育龄与中年成人中早期成人部分：迁移/工作变化中的健康记录、异常结果跟进、生育计划连接叠加路径。 |
| age-40-64 | 40–64 岁 | 育龄与中年成人中中年部分：多年趋势、当地风险适宜筛查、照护压力和转诊完成。 |
| age-65-84 | 65–84 岁 | 老年：个人重视的日常能力、跌倒与治疗耐受、近期功能下降和突然意识变化。 |
| age-85-plus | 85 岁及以上 | 高龄：个人意愿、功能与照护支持、获益负担讨论、摄入和活动突然下降后的调整。 |
| pregnancy-postpartum | 生育叠加路径，年龄边界为 null | 孕产期：孕前/产前资料与连续照护、孕期和产后一年严重警示变化。 |

六个年龄段互不重叠，年龄切点用于导航；它们不是生物学风险突然改变的界线。孕产期叠加在实际年龄上，不重复计入年龄分母。阶段介绍明确表述重点，因素目录仍可继续查阅其他适用知识。空气污染关联全部六个年龄段和孕产期，阶段不复制空气因素正文。

## 保留数值的核对与适用范围

| 数值/表达 | 采用的来源和定位 | 正文保留的条件 |
|---|---|---|
| 成人总盐 <5 克/天 | lifecycle-diet：Sodium and potassium | 成人；包括加工食物与调味料，不把成人限盐量套给婴幼儿。 |
| 前 6 个月纯母乳；约 6 个月辅食；继续至 2 岁或以后 | lifecycle-feeding：Key facts / Complementary feeding | WHO 喂养建议；喂养困难需要实际支持以确保摄入。 |
| 400 微克/天叶酸 | lifecycle-folate：Recommended intake | CDC 对可怀孕人群的预防建议；既往受影响妊娠和特殊用药另由产科确认。 |
| 48 项试验、344716 人、收缩压每低 5 mmHg、主要心血管事件相对风险约低 10% | lifecycle-bp-trials：2021 Abstract Methods / Findings / Interpretation | 随机治疗的群体相对效果，不是个人绝对减少 10 个百分点，不直接给个人降压目标。 |
| HbA1c 约反映 3 个月；孕期 24–28 周检测 | lifecycle-glucose：A1C test / Who should be tested | 贫血、血红蛋白变异和妊娠影响解释；孕期流程与非孕诊断/治疗目标区分。 |
| 27 项试验；LDL 每低 1 mmol/L，主要血管事件相对风险约低 21% | lifecycle-ldl-trials：2012 Abstract Findings | 采用 CTT 2012 的 RR 0.79；没有混用 CTT 2010 的 22% 与另一试验数。群体相对效果不是个人保证。 |
| BMI＝体重（kg）/身高（m）的平方，kg/m² | lifecycle-growth：Diagnosis | 成人粗略测量；肌肉、脂肪分布及儿童年龄别生长另看，没有建立计算器。 |
| 成人每周中等强度 150–300 分钟或高强度 75–150 分钟、肌力至少 2 天 | lifecycle-activity：Adults aged 18–64 years | 活动起点结合现有能力；慢病与症状影响安排，不由分钟数预测寿命。 |
| 65+ 多组成平衡与力量活动每周至少 3 天 | lifecycle-activity：Adults aged 65 years and above | 用于功能与跌倒预防的活动安排，实测功能另归功能因素。 |
| 5–17 岁平均每天 60 分钟；肌骨强化至少每周 3 天 | lifecycle-activity：Children and adolescents aged 5–17 years | 年龄明确，不套用成人分钟建议。 |
| 未活动婴儿清醒俯卧累计至少 30 分钟；1–4 岁活动至少 180 分钟，其中 3–4 岁至少 60 分钟较有活力 | lifecycle-activity：Children under 5 years of age | 俯卧是清醒时活动，睡眠仍仰卧；1–2 岁与 3–4 岁的活动组成区分。 |
| 无禁忌的孕产期至少每周 150 分钟中等强度活动 | lifecycle-activity：Pregnant and postpartum women | 明确无禁忌，不将孕产期建议替代个别产科评估。 |
| 睡眠：0–3 月 14–17 小时、4–12 月 12–16、1–2 岁 11–14、3–5 岁 10–13、6–12 岁 9–12、13–17 岁 8–10、18–60 岁至少 7、61–64 岁 7–9、65+ 7–8 | lifecycle-sleep：Getting enough sleep 表格 | 婴幼儿含午睡；保留 CDC 自己的年龄带，未强行改为导航年龄段。源报告的青少年 13–18 改为核对页的 13–17。 |
| PM2.5 年均 5 μg/m³；颗粒物直径尺度 2.5 μm | lifecycle-air-guideline：Recommended 2021 AQG levels / Pollutants；lifecycle-air-table：推荐值表 | 年均值不能当小时警报线或个人安全证明；环境指标不是体内剂量。 |
| 儿童血铅参考值 3.5 μg/dL | lifecycle-lead：What is a reference value? | 来自美国 1–5 岁儿童人群分布，用于识别较高暴露和安排跟进；不是安全阈值。 |
| 至少 8 次产前接触、首次孕 12 周内 | lifecycle-antenatal：2016 antenatal model | WHO 产前照护建议；接触需包含评估、检验结果及后续安排，不只计次数。 |
| 孕期及产后一年严重警示变化 | lifecycle-maternal-warning：Signs and symptoms | 即刻求医并说明妊娠/分娩时间；无全球统一急救号码假设。 |

## 未沿用的数值和推断

- 源报告的加权总分、全球排序与 A/B/C/D 标签是作者组织方法；没有注册系统综述和独立偏倚复核记录，因此未当作正式 GRADE 或官方风险次序。
- 不复现吸烟寿命损失/某年龄戒烟收益、PREDIMED 降幅、BMI 分层死亡比、美国 Medicare 空污关联、全球疫苗挽救人数、社会经济/童年逆境相对风险、饮酒及长睡眠死亡比、孤独风险比例、可归因痴呆比例等大量异质结果。这些研究的地域、人群、结局和估计方式不同，也不是完成具体行动说明所需的数字。
- WHO 婴幼儿喂养页在 2026 年更新，当前可预防死亡负担的表述与源报告沿用的“超过 82 万”不同。保留实际核对的喂养建议，没有把旧估算当作当前统一数值。
- 妊娠阿司匹林试验、SPRINT-MIND、运动防跌倒汇总效果及听力干预亚组结果没有按报告中的精确效应值复制。页面保留相应的活动、评估和照护知识；具体药物选择或选择性亚组效应需相应临床条件。
- ApoB/Lp(a)、最大摄氧量、握力常模和 ACE 分数未变成面向所有人的检查清单或统一阈值。核心测量和何时找医生评估优先；疾病诊断和治疗继续链接现有病症。
- 没有用多个相对风险相乘，也没有将环境参考值、年龄、生活行为和检验数值合成个人评分。

## 来源核对清单

下面的定位对应实际读取的官方正文、官方检索返回的正文片段或原始研究摘要。研究摘要核对不代表重新取得个体原始数据；部分网页直接打开不可用时，仅采用官方检索结果中实际可见的内容，不把候选链接登记为已阅读全文。逐节 source_ids 保留在 JSON，源条目的 scope 给出支持范围。

| 来源 ID | 直接来源 | 实际核对位置与范围 |
|---|---|---|
| lifecycle-family | [CDC: About Family Health History](https://www.cdc.gov/family-health-history/about/index.html) | Overview; Collect your family health history; Why family health history is important。家族史包括共享基因、行为和环境；记录亲属关系、诊断和发病年龄。 |
| lifecycle-preterm | [WHO: Preterm birth](https://www.who.int/news-room/fact-sheets/detail/preterm-birth) | Overview; Why does preterm birth happen?; Solutions。早产与儿童发育和照护需求，全球公共卫生背景。 |
| lifecycle-diet | [WHO: Healthy diet](https://www.who.int/news-room/fact-sheets/detail/healthy-diet) | Carbohydrates; Sugars; Fats; Sodium and potassium。食物结构、成人每日盐少于5克、食物与营养需求；不是患者专属处方。 |
| lifecycle-feeding | [WHO: Infant and young child feeding](https://www.who.int/news-room/fact-sheets/detail/infant-and-young-child-feeding) | Key facts; Complementary feeding。前6个月纯母乳、6个月起辅食、继续至2岁或以后；页面2026年8月更新，未沿用旧死亡负担估算。 |
| lifecycle-folate | [CDC: Folic Acid — Sources and Recommended Intake](https://www.cdc.gov/folic-acid/about/intake-and-sources.html) | Recommended intake。可怀孕人群每日400微克叶酸、强化食品及补充剂。美国公共卫生建议，不推导高风险剂量。 |
| lifecycle-bp | [WHO: Hypertension](https://www.who.int/news-room/fact-sheets/detail/hypertension) | Overview; Symptoms; Treatment; Complications。收缩/舒张压、无症状损伤、按合并病调整目标。 |
| lifecycle-bp-trials | [BPLTTC 2021: Blood pressure lowering — individual participant data meta-analysis](https://pubmed.ncbi.nlm.nih.gov/33933205/) | Abstract Methods/Findings/Interpretation。48项随机试验、344716人；收缩压下降5 mmHg对应主要心血管事件相对风险约下降10%；群体治疗证据。 |
| lifecycle-glucose | [NIDDK: Diabetes Tests & Diagnosis](https://www.niddk.nih.gov/health-information/diabetes/overview/tests-diagnosis) | Who should be tested; A1C test; Test results for diagnosis。HbA1c约3个月、贫血/妊娠影响；非孕诊断通常需要确认；孕期24–28周检测。 |
| lifecycle-cholesterol | [NHLBI: Blood Cholesterol](https://www.nhlbi.nih.gov/health/blood-cholesterol) | What is Blood Cholesterol?。脂蛋白运送胆固醇、LDL与斑块、血液检查及生活方式/药物。 |
| lifecycle-ldl-trials | [CTT 2012: Lowering LDL with statins in people at low vascular risk](https://pubmed.ncbi.nlm.nih.gov/22607822/) | Abstract Findings。27项随机试验个体数据；每降低1 mmol/L LDL主要血管事件RR 0.79（95%CI 0.77–0.81），相对效果非个人绝对收益。 |
| lifecycle-growth | [WHO: Obesity and overweight](https://www.who.int/news-room/fact-sheets/detail/obesity-and-overweight) | Diagnosis; Causes; Prevention and management。成人BMI、儿童年龄别生长判断、肥胖多因素原因和支持性管理。 |
| lifecycle-tobacco | [WHO: Tobacco and nicotine](https://www.who.int/news-room/fact-sheets/detail/tobacco) | Overview; Second-hand smoke kills; Tobacco users need help to quit; Newer tobacco and nicotine products。烟草、二手烟、依赖和戒烟服务。 |
| lifecycle-alcohol | [WHO: Alcohol](https://www.who.int/news-room/fact-sheets/detail/alcohol) | Health risks; Factors affecting alcohol consumption and alcohol-related harm。饮酒量、模式、致癌、受伤及孕期风险。 |
| lifecycle-withdrawal | [NHS: Alcohol-use disorder](https://www.nhs.uk/conditions/alcohol-use-disorder/) | Symptoms; Withdrawal symptoms; Treatment。依赖者突然停酒的危险、抽搐等严重戒断的急救。英国服务名称不作为全球号码。 |
| lifecycle-activity | [WHO Europe: Physical activity](https://www.who.int/europe/news-room/fact-sheets/item/physical-activity) | Physical activity recommendations：<1、1–2、3–4、5–17、18–64、65+、pregnant/postpartum。活动时长、肌力和平衡建议；具禁忌者另行评估。 |
| lifecycle-sleep | [CDC: About Sleep](https://www.cdc.gov/sleep/about/) | Getting enough sleep; Sleep quality; Keeping a sleep diary。各年龄参考时长、质量和白天功能。CDC表中青少年范围为13–17岁。 |
| lifecycle-air | [WHO: Ambient outdoor air pollution](https://www.who.int/news-room/fact-sheets/detail/ambient-(outdoor)-air-quality-and-health) | Health effects; Policies reducing air pollution。心肺负担与上游污染控制，空气质量不是个人疾病检验。 |
| lifecycle-air-guideline | [WHO: Global Air Quality Guidelines](https://www.who.int/news-room/questions-and-answers/item/who-global-air-quality-guidelines) | Recommended 2021 AQG levels; Pollutants in daily life; Guidelines development。PM2.5年均5 μg/m³为政策健康指导值。 |
| lifecycle-lead | [CDC: Updates Blood Lead Reference Value](https://www.cdc.gov/lead-prevention/php/news-features/updates-blood-lead-reference-value.html) | What is a reference value?; Lead sources; Follow-up actions。儿童3.5 μg/dL参考值、并非安全阈值；来自美国1–5岁人群分布。 |
| lifecycle-co | [CDC: Carbon Monoxide Poisoning Basics](https://www.cdc.gov/carbon-monoxide/about/index.html) | Overview; Symptoms; Prevention。无色无味、一氧化碳报警器和发电机不得室内使用。 |
| lifecycle-heat | [WHO: Heat and health](https://www.who.int/news-room/fact-sheets/detail/climate-change-heat-and-health) | How does heat impact health?; What actions should the public take?; Protect infants and children。散热、降温环境和易受影响人群；未复制统一喝水量。 |
| lifecycle-road | [WHO: Road traffic injuries](https://www.who.int/news-room/fact-sheets/detail/road-traffic-injuries) | Risk factors; Seat-belts, child restraints and helmets; Safe system。道路安全、速度、酒驾和保护设备。 |
| lifecycle-safe-sleep | [NICHD: Safe Sleep Environment](https://safetosleep.nichd.nih.gov/safe-sleep/environment) | Safe sleep area; Firm, flat and level sleep surface。婴儿仰卧、独立硬平床面、清除松软物品。 |
| lifecycle-social | [WHO: Social determinants of health](https://www.who.int/news-room/fact-sheets/detail/social-determinants-of-health) | Overview; Health inequities; Health equity benefits all。教育、收入、居住和食物可及性及制度行动。 |
| lifecycle-vaccines | [WHO: Vaccines and immunization — What is vaccination?](https://www.who.int/news-room/questions-and-answers/item/vaccines-and-immunization-what-is-vaccination) | How does a vaccine work?; When should I get vaccinated?; Safety。免疫记忆、程序、不同疫苗适用性。 |
| lifecycle-access | [WHO: Universal health coverage](https://www.who.int/news-room/fact-sheets/detail/universal-health-coverage-(uhc)) | Overview。服务应覆盖预防、治疗、康复、缓和医疗和全生命周期；质量与及时使用。 |
| lifecycle-antenatal | [WHO: Right care at the right time during pregnancy](https://www.who.int/news/item/07-11-2016-pregnant-women-must-be-able-to-access-the-right-care-at-the-right-time-says-who) | 2016 antenatal model。至少8次接触、首次在孕12周内；接触需有实际评估，不是仅计次数。 |
| lifecycle-mental | [WHO: Mental health](https://www.who.int/en/news-room/fact-sheets/detail/mental-health-strengthening-our-response) | Determinants; Promotion and prevention; Care and treatment。功能、困扰、社会和生物因素以及服务。 |
| lifecycle-connection | [WHO: Social connection](https://www.who.int/news-room/questions-and-answers/item/social-connection) | What is social connection/isolation/loneliness?; Solutions。客观接触、主观孤独、支持质量和社区机会。 |
| lifecycle-function | [WHO: Integrated care for older people](https://www.who.int/publications/i/item/9789241550109) | Overview。以可测身体和心理能力下降为目标的社区照护；分领域评估。 |
| lifecycle-falls | [CDC: Preventing Falls and Hip Fractures](https://www.cdc.gov/falls/prevention/index.html) | Talk to your doctor; Strength and balance; Eyes checked; Home safer。功能评估、视力与环境危险及用药复核。 |
| lifecycle-medicines | [NIA: Taking Medicines Safely as You Age](https://www.nia.nih.gov/health/medicines-and-medication-management/taking-medicines-safely-you-age) | Starting a new medicine; Medicine lists; Interactions。处方、非处方、补充剂统一清单和症状记录。 |
| lifecycle-development | [CDC: Concerned About Your Child’s Development?](https://www.cdc.gov/concerned) | Act early; Why act early?。观察玩耍、学习、说话、行为和移动；尽早联系评估和早期支持。 |
| lifecycle-maternal-warning | [CDC: Urgent Maternal Warning Signs and Symptoms](https://www.cdc.gov/hearher/maternal-warning-signs/index.html) | Signs and symptoms。孕期及产后一年严重头痛视力变化、呼吸胸痛、出血、胎动变化和伤害念头即刻就医。 |
| lifecycle-confusion | [NHS: Sudden confusion](https://www.nhs.uk/symptoms/confusion/) | Immediate action; What to do。突然意识混乱需急救评估，不能归为正常老化。 |
| lifecycle-air-table | [WHO Compendium: Air pollution — recommended AQG levels](https://cdn.who.int/media/docs/default-source/environmental-health-impact/who_compendium_air_pollution_01042022_eo_final.pdf) | Recommended AQG levels and interim targets table：PM2.5 annual 5 μg/m³。用于核对数值与平均时段，不将年度均值用作小时阈值。 |
| lifecycle-stroke-warning | [CDC: Signs and Symptoms of Stroke](https://www.cdc.gov/stroke/signs-symptoms/index.html) | Signs and symptoms; When to seek emergency help。突然单侧无力、语言异常等需立即急救。 |
| lifecycle-crisis | [NIMH: Frequently Asked Questions About Suicide](https://www.nimh.nih.gov/health/publications/suicide-faq) | Warning signs; Help in crisis。即时生命危险需当地急救，不推广美国号码为全球号码。 |
| lifecycle-co-action | [CDC/NIOSH: Carbon Monoxide Hazards at Work](https://www.cdc.gov/niosh/carbon-monoxide/about/index.html) | Prevention; Symptoms/action。出现症状离开至新鲜空气并立即求医，适用燃烧设备相关暴露。 |

获取方式补充：BPLTTC 和 CTT 核对的是 PubMed 中原始论文摘要；WHO 空气推荐值核对 Q&A 及官方 PDF 可检索表格。WHO 社会联结与 ICOPE 概述、NIA 用药安全、CDC 发育/叶酸/一氧化碳部分、NICHD 安全睡眠、NHS 戒断、WHO 产前接触/UHC 等条目使用官方检索返回的可见正文。WHO 社会联结直接打开返回错误，NIA 直接打开仅返回很短内容，因此未声称取得这两页完整正文。其余条目按 scope 核对；数值只采用可见原文支持的范围。

危险行动定位另核对了 CDC 卒中症状、NIMH 自杀危机说明及 CDC/NIOSH 一氧化碳行动，分别用于突然神经变化、即时自伤危险、离开暴露至新鲜空气并求医。急救动作不依赖活动或风险指标达到某分数。

## 本次验证

- JSON 可用 UTF-8 读取：20 个指定因素、8 组、6 个互斥年龄阶段、1 个孕产期叠加、95 个中英章节、39 条来源。
- 每因素只归属一个组；各因素的 source_ids 与其章节来源并集一致。所有章节都有有效来源 ID、中文/英文标题和分段列表。
- 所有 condition_ids 均存在于现有 conditions；所有 factor_ids 均引用本模块唯一因素；没有自身引用或阶段重复引用。
- 阶段因素并集覆盖全部 20 个因素；空气污染已关联全部 7 条阶段路径。
- 章节 ID 全局唯一；未检出整节中文逐字复制、正文 HTML、内部 turn 引用或平台引用标记。
- 中英数值与适用对象已对应检查；血压/血脂及睡眠的数字出现顺序因语序不同，不作为缺失或多余数值。BMI 公式单位已明确。
- 本文件记录数据级检查；界面、构建与全站回归由主任务集成执行。本子任务未提交、推送或部署。
