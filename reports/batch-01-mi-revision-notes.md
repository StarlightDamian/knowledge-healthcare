# 心肌梗死草稿定向修订交接

日期：2026-09-30。修订作者：`/root/demand_content`；原作者：`/root/emergency_content`。

## 状态与边界

本轮修正既有 MI01–MI08 中的真实措辞/范围问题及对应来源绑定。正文为 14 节、55 个导读或列表段落；证据按不同医疗行动与来源范围拆为 90 个中英对应主张。全部 14 条编辑记录仍为 `pending`，独立复核为 `pending`，医学签审为 false；新增覆盖和发布增量均为 0。这是修订作者的资料阅读与自检，不是独立审核结论。

仅修改 MI 正文、共有 sources/editorial 中的 MI 对象及本日志。其余主题对象与当前 HEAD 深比较一致；未写生产 data、未 Git 提交/推送或部署。线上 74 篇不受影响。未增加剂量、统一疗程、居家排除胸痛规则或整套护理模板。

## 输入版本

- 原 MI canonical：`4a35256c21090af048581dd5877347da99039fe7b6031c663af79672304c4d09`。
- 原 MI 文件 SHA-256：`39c9a50662f5e0e778dd64afdc38c2759c08a0bcc8f7ee478fdd3a3a22db072a`。
- 原独立报告：`reports/batch-01-mi-independent.json`，文件 SHA-256 `e9e778e524c749090f84b889b4b8afdcd9c3dfc2076263c54d4d3d5d2fb11029`。
- 审阅要求挑战：`reports/batch-01-mi-review-challenge.json`，文件 SHA-256 `b8093845053e476df6f0e96846bc9c96875ec20b69def6668b5aff5253bbe5e1`；采纳其范围纠正，不把前瞻提醒写成原稿错误。

## 实际修订

| 原发现 | 本轮处理 |
|---|---|
| MI01 | 分开氯吡格雷使用者黑色柏油样便的立即医疗联系、吐血/咖啡渣样呕吐的立即急诊，以及外部伤口严重/持续止不住出血的急诊行动。111 明确为英国 NHS 路径；没有将所有黑便等同叫救护车。 |
| MI02 | 早期结果、是否复测及检测/时间/风险条件分开；肌钙蛋白提示损伤而非单独确诊病因。保留正确的 NSTEMI 可有严重堵塞，不改成只会部分堵塞。 |
| MI03 | 简要解释稳定/不稳定心绞痛、主动脉夹层和肺栓塞；按危险信号急诊区分，未重复建立胸痛诊断指南。 |
| MI04 | 溶栓限定合格 STEMI、发病时间、PCI 可及性与医生对重大出血风险的判断；说明 NSTEMI 按风险选择抗栓和造影，不列禁忌算法/剂量/统一时限。 |
| MI05 | 增补抗血小板/他汀/ACE/β阻滞剂的角色及相关风险；拆清每个来源真正支持的分句，药物特异或肾病适用范围不外推。双药疗程不写统一期限。 |
| MI06 | 胎儿相关检查/药物条件仅限孕期，产后并列风险不带入胎儿条件；糖尿病/CKD 饮食依病情、药物及化验调整，不给统一禁食表。 |
| MI07 | 康复活动、危险行动、心功能结果及复诊用途分开。药单、日期、症状记录是低风险编辑整理建议，未当作新增医疗双源门槛。 |
| MI08 | 阿司匹林准确归属于 Mayo 与 NHS 各自说明，不夸成国家绝对冲突；没有新增无条件氧疗、统一 DAPT 疗程或 NSTEMI 仅部分堵塞等原稿不存在的错误。 |
| 原报告其他缺口 | CPR 的无反应且无正常呼吸触发条件补读 AHA BLS 与 St John；心源性休克机制补读 NHLBI 专门材料，不把原恢复页只列病名算机制支持。 |

中英各节信息对应，关键行动保持相同紧急程度；新记录中的每一摘录均可在该语言唯一正文中定位，顺序拼接覆盖全文。

## 阅读与来源独立性

本轮新增 30 个已实际读取相关原段的来源记录（26 页直接打开，4 个只取得官方发布页面的索引文本）。不把索引范围写成完整指南阅读。NICE 直连 403、ESC 原页/更正直连受限均据实保留；未继续无范围扩张地追索全文。

- NIH 旗下 NHLBI、NIDDK、NLM 自编材料算同一机构组。NLM 托管的 ASHP 药物信息和 ADAM 患者教育明确按实际作者记录，不写成 NIH 原作。
- NICE 各页及视觉摘要是同一编写来源。美国联合 ACS 指南及其 AHA 摘要为同一来源；AHA 患者页与指南可能共享上游依据，双药疗程不据两个网址判独立双源。
- NHS 与 CUH 信息保守归为同一 NHS 组；CUH ACE 页适用于肾病患者，NHS bisoprolol 是具体药物。所有这些限制保留在主张级 assessment。
- Mayo、AHA 等资料可能共引指南、教科书或研究。独立机构编写不等于独立临床试验重复；既有研究依赖不得重复计算。
- 权利仍归来源方；保存自行撰写的双语事实归纳、链接与定位，未保存或转载受限文章全文、表格及图片。ASHP/ADAM 与学会材料不视为公有领域；索引访问不能替代转载许可。

### 新增来源及实际读取范围

- `mi-ashp-clopidogrel` — [ASHP — Clopidogrel (MedlinePlus hosting)](https://medlineplus.gov/druginfo/meds/a601040.html)。版本/审订：2026-08-15；访问：`page_opened`；编写组：`US-ASHP`。定位：Precautions65–73; Other information123；Why prescribed53; How used57；Serious side effects91–98；Precautions67–68; Other information123。实际范围：Why prescribed; How used; Precautions; Serious side effects; Other information. ASHP authorship is explicit; NLM hosts it.
- `mi-mayo-vomiting-blood` — [Mayo Clinic — Vomiting blood](https://www.mayoclinic.org/symptoms/vomiting-blood/basics/causes/sym-20050732)。版本/审订：2023-12-07；访问：`page_opened`；编写组：`US-MAYO`。定位：When to see a doctor307–321。实际范围：Definition; When to see a doctor: immediate emergency department; shock signs for calling EMS. Medical review 23 February 2022.
- `mi-nice-cg95` — [NICE CG95 — Recent-onset chest pain: recommendations](https://www.nice.org.uk/guidance/CG95/chapter/recommendations)。版本/审订：2016-11-30；访问：`search_text_retrieved`；编写组：`UK-NICE`。定位：Final1.2.5.2–7；Final1.2.5.4,1.2.5.7,1.2.6.1–2；Final1.2.1.3,1.2.1.7–8；Final1.2.2.8;1.2.4.2;1.2.6.2；Final1.2.2.8,1.2.4.2,1.2.6.2。实际范围：Final recommendations 1.2.1.3–8,1.2.2.8,1.2.3.4,1.2.4.2,1.2.5.2–7,1.2.6.1–2. Official indexed passages read; direct page 403. Draft versions excluded.
- `mi-nlm-troponin` — [NLM — Troponin Test](https://medlineplus.gov/lab-tests/troponin-test/)。版本/审订：2023-10-30；访问：`page_opened`；编写组：`US-NIH`。定位：What is a troponin test34–44；What results mean84–89；What results mean84–102, myocarditis94。实际范围：What is a troponin test; What results mean; References. NIH/NHLBI shared group; references include NHLBI, Cleveland, textbooks. Generic hour examples not adopted as universal algorithm.
- `mi-nhs-angina` — [NHS — Angina](https://www.nhs.uk/conditions/angina/)。版本/审订：未取得明确日期；不推测；访问：`page_opened`；编写组：`UK-NHS`。定位：How to treat29–37; Call99938–49;11150–55。实际范围：How to treat angina; Immediate call999 versus urgent111 conditions; symptoms and assessment. Page opened; review date not extracted.
- `mi-mayo-angina` — [Mayo Clinic — Angina: symptoms and causes](https://www.mayoclinic.org/diseases-conditions/angina/symptoms-causes/syc-20369373)。版本/审订：未取得明确日期；不推测；访问：`page_opened`；编写组：`US-MAYO`。定位：Types: stable/unstable angina; Symptoms283–309。实际范围：Types: stable and unstable angina; Symptoms; When to see doctor. Current page opened; no date inferred.
- `mi-mayo-chest` — [Mayo Clinic — Chest pain: symptoms and causes](https://www.mayoclinic.org/diseases-conditions/chest-pain/symptoms-causes/syc-20370838)。版本/审订：2024-12-10；访问：`page_opened`；编写组：`US-MAYO`。定位：Heart-related causes352; Lung-related causes363; When to see a doctor。实际范围：Heart-related causes: aortic dissection; Lung-related causes: pulmonary embolism; urgent assessment. References cite vascular society/NHLBI/AHA and textbooks; not independent trials.
- `mi-nice-ng185` — [NICE NG185 — Acute coronary syndromes: recommendations](https://www.nice.org.uk/guidance/NG185/chapter/recommendations)。版本/审订：2020-11-18；访问：`search_text_retrieved`；编写组：`UK-NICE`。定位：Final1.1.1–6,1.1.19；Final1.1.1–6;1.1.19；NSTE-ACS section1.2; official NSTEMI visual summary；Final1.4.2: secondary prevention discharge and monitoring plan；Final1.4.2–3;1.2.27–29；Final1.2.27–29;1.4.2–3。实际范围：Final official indexed text 1.1.1–6,1.1.19,1.2.27–29,1.4.1–3 and visual NSTEMI summary. Recommendations include retained 2013 text; no whole-page access claimed.
- `mi-acs-2025` — [ACC/AHA/ACEP/NAEMSP/SCAI — 2025 ACS guideline](https://www.jacc.org/doi/10.1016/j.jacc.2024.11.009)。版本/审订：2025-02-27；访问：`search_text_retrieved`；编写组：`US-ACS-2025-JOINT`。定位：§5.3.1 synopsis and Table14；§5.3.1 synopsis; Table14。实际范围：Official indexed section5.3.1 synopsis/Table14 and section6; shared joint guideline, not independent from AHA summary. Full article fetch unavailable.
- `mi-aha-acs-summary` — [AHA — 2025 ACS Top Things to Know](https://professional.heart.org/en/science-news/2025-guideline-for-the-management-of-patients-with-acute-coronary-syndromes/top-things-to-know)。版本/审订：2025-02-27；访问：`page_opened`；编写组：`US-ACS-2025-JOINT`。定位：Items1,4,6；Item2；Item9。实际范围：Items2,4,9: conditional DAPT, NSTE-ACS risk, lipid reassessment. Same source origin as joint guideline; not a second independent guideline.
- `mi-aha-aspirin` — [AHA — Aspirin and dual antiplatelet therapy](https://www.heart.org/en/health-topics/heart-attack/treatment-of-a-heart-attack/aspirin-and-heart-disease)。版本/审订：2025-02-28；访问：`page_opened`；编写组：`US-AHA`。定位：Know the risks24–35；Why aspirin?; DAPT overview；DAPT: Who needs it and for how long58–83；Recommendation18–23; Know risks24–35。实际范围：Recommendation; Know the risks; DAPT medicines and duration. AHA writing shares organization and upstream guidelines with joint ACS material.
- `mi-fda-aspirin` — [FDA — Before using aspirin to lower heart attack or stroke risk](https://www.fda.gov/drugs/safe-use-aspirin/using-aspirin-lower-your-risk-heart-attack-or-stroke-what-you-should-know)。版本/审订：未取得明确日期；不推测；访问：`page_opened`；编写组：`US-FDA-CONSUMER`。定位：Not Without Risks71–73；Not Without Risks72–73；Opening61; Not Without Risks71–73。实际范围：Opening advice; Not Without Risks. FDA consumer writing, not manufacturer label. Page has no extracted publication date; no absolute ban on all primary prevention inferred.
- `mi-mayo-ace` — [Mayo Clinic — ACE inhibitors](https://www.mayoclinic.org/diseases-conditions/high-blood-pressure/in-depth/ace-inhibitors/art-20047480)。版本/审订：未取得明确日期；不推测；访问：`page_opened`；编写组：`US-MAYO`。定位：Side effects303–316。实际范围：Side effects: dry cough, low-BP dizziness, potassium, kidney function; questions to healthcare team. References include AHA hypertension guideline and textbooks.
- `mi-mayo-beta` — [Mayo Clinic — Beta blockers](https://www.mayoclinic.org/diseases-conditions/high-blood-pressure/in-depth/beta-blockers/art-20044522)。版本/审订：未取得明确日期；不推测；访问：`page_opened`；编写组：`US-MAYO`。定位：Side effects290–310。实际范围：Side effects: fatigue/dizziness, asthma caution, do not stop suddenly. References include AHA hypertension guideline and textbooks.
- `mi-nhs-bisoprolol` — [NHS — Bisoprolol](https://www.nhs.uk/medicines/bisoprolol/)。版本/审订：2026-01-08；访问：`page_opened`；编写组：`UK-NHS`。定位：How to take40; side effects68–83; suitability112–120。实际范围：How to take: no abrupt stop; Side effects; Who can and cannot take: breathing problems. Specific bisoprolol information used within beta-blocker context, not all-agent contraindication.
- `mi-nhs-ramipril` — [NHS — Ramipril side effects](https://www.nhs.uk/medicines/ramipril/side-effects-of-ramipril/)。版本/审订：未取得明确日期；不推测；访问：`page_opened`；编写组：`UK-NHS`。定位：Common effects22–31；Common adverse effects22–31。实际范围：Common adverse effects: persistent dry cough and dizziness; contact prescriber for troublesome cough. Specific ramipril exemplar; no date inferred.
- `mi-cuh-ace` — [Cambridge University Hospitals — ACE inhibitors](https://www.cuh.nhs.uk/patient-information/ace-inhibitors/)。版本/审订：2023-10-25；访问：`page_opened`；编写组：`UK-NHS`。定位：Adverse effects324–329；Monitoring316–321; adverse effects324–329。实际范围：Kidney-patient information; blood pressure/potassium/kidney-function monitoring and troublesome dry cough. Kidney context retained, not a generic post-MI protocol. Version6/document7624, approved25October2023.
- `mi-nhs-statins` — [NHS — Statins](https://www.nhs.uk/medicines/statins/)。版本/审订：未取得明确日期；不推测；访问：`page_opened`；编写组：`UK-NHS`。定位：Side effects75–88。实际范围：Current statin page opened; side-effect and consultation guidance. Old /conditions/statins/side-effects URL failed; no claim of reading that old page.
- `mi-cuh-statins` — [Cambridge University Hospitals — Cholesterol lowering medicines](https://www.cuh.nhs.uk/patient-information/statins-cholesterol-lowering-medicines/)。版本/审订：2023-08-25；访问：`page_opened`；编写组：`UK-NHS`。定位：Action301–308; Problems309–320。实际范围：Version7 document3951: Action; Problems to watch for, muscle pain/weakness contact. Blanket grapefruit/pregnancy wording not adopted.
- `mi-nhs-wounds` — [NHS — Cuts and grazes](https://www.nhs.uk/conditions/cuts-and-grazes/)。版本/审订：未取得明确日期；不推测；访问：`page_opened`；编写组：`UK-NHS`。定位：Immediate action55–66。实际范围：Immediate action: uncontrolled wound bleeding, spurting/large/deep cut; do not drive. External wound scope only.
- `mi-mayo-bleeding` — [Mayo Clinic — Severe bleeding first aid](https://www.mayoclinic.org/first-aid/first-aid-severe-bleeding/basics/art-20056661)。版本/审订：2024-10-16；访问：`page_opened`；编写组：`US-MAYO`。定位：Severe bleeding first aid262–266。实际范围：Severe external bleeding; call local EMS for deep or uncertain severe wound; no GI-bleed classification borrowed.
- `mi-esc-pregnancy-2025` — [ESC — 2025 cardiovascular disease and pregnancy guideline](https://academic.oup.com/eurheartj/article/46/43/4462/8234487)。版本/审订：2025-08-29；访问：`search_text_retrieved`；编写组：`EU-ESC-PREGNANCY-2025`。定位：§12.1,§5.1,§4.3.5；§12.1/Figure11;§4.3.5;§5.1; coronary PCI passage；§12.1/Figure11。实际范围：Official publisher indexed section12.1, Figure11,5.1 and12.3.3.2 read; direct HTML/official slides fetch unavailable. Same ESC guideline across slides/journal; no mirror counted independently. Additional official indexed sections2.2,4.3.5–4.3.5.3 and coronary intervention passage actually read; source notes a2026 correction (ehaf1011), whose direct fetch failed and contents remain unverified.
- `mi-aha-bls-2025` — [AHA — 2025 Adult Basic Life Support](https://cpr.heart.org/en/resuscitation-science/cpr-and-ecc-guidelines/adult-basic-life-support)。版本/审订：未取得明确日期；不推测；访问：`page_opened`；编写组：`US-AHA`。定位：Part7 §6.1 recommendation1;§6.2 recommendations1–3 and synopsis。实际范围：2025 Part7 sections6.1–6.2; unresponsive absent/abnormal breathing lay recognition, immediate CPR/dispatch. Shares ILCOR evidence, not independent trials.
- `mi-sja-cpr` — [St John Ambulance — How to do CPR](https://www.sja.org.uk/first-aid-advice/cpr/)。版本/审订：2025-04-28；访问：`page_opened`；编写组：`UK-STJOHN`。定位：What is CPR128–135; What to do146–170。实际范围：Clinical reviewer Dr Lynn Thomas; adults unresponsive/not breathing normally; immediate CPR and ambulance-controller instructions. NHS CPR link redirects here; SJA is author.
- `mi-nhlbi-shock` — [NHLBI — Cardiogenic shock overview](https://www.nhlbi.nih.gov/health/cardiogenic-shock)。版本/审订：2022-03-24；访问：`page_opened`；编写组：`US-NIH`。定位：Overview94–97。实际范围：Overview94–97: inadequate pump perfusion, serious heart attack and heart failure; same NIH group as other NHLBI pages.
- `mi-niddk-ckd-food` — [NIDDK — Healthy eating for adults with CKD](https://www.niddk.nih.gov/health-information/kidney-disease/chronic-kidney-disease-ckd/healthy-eating-adults-chronic-kidney-disease)。版本/审订：未取得明确日期；不推测；访问：`page_opened`；编写组：`US-NIH`。定位：Potassium200–213。实际范围：Choose foods to keep potassium in goal range200–213; portions according to high potassium, medicines and blood tests. Adult CKD scope.
- `mi-nkf-ckd-food` — [National Kidney Foundation — Nutrition and CKD stages1–5, not on dialysis](https://www.kidney.org/kidney-topics/nutrition-and-kidney-disease-stages-1-5-not-dialysis)。版本/审订：未取得明确日期；不推测；访问：`page_opened`；编写组：`US-NKF`。定位：Changes to diet40–44; nutrients57–73。实际范围：Changes to diet; registered dietitians; nutrients57–73; no universal plan, kidney function, drugs and tests guide potassium. Excludes dialysis.
- `mi-niddk-diabetes-food` — [NIDDK — Healthy living with diabetes](https://www.niddk.nih.gov/health-information/diabetes/overview/healthy-living-with-diabetes)。版本/审订：未取得明确日期；不推测；访问：`page_opened`；编写组：`US-NIH`。定位：Meal planning; Find best times176–182。实际范围：Meal plan and timing; timing depends on glucose medicines, activity and other disease. Does not create a post-MI dosing or meal formula.
- `mi-mayo-rehab` — [Mayo Clinic — Cardiac rehabilitation](https://www.mayoclinic.org/tests-procedures/cardiac-rehabilitation/about/pac-20385192)。版本/审订：2024-11-21；访问：`page_opened`；编写组：`US-MAYO`。定位：Preparation315–317; gradual exercise339–346；Nutrition347–351；Nutrition347–351; Medicine education352–356；Preparation315–317; programme339–367。实际范围：Preparation315–317; during rehab339–364; follow-up367. Nutrition tailored to diabetes/BP/lipids; activity capability/risk assessment; clinical review9September2024.
- `mi-adam-activity` — [A.D.A.M. — Being active after your heart attack](https://medlineplus.gov/ency/patientinstructions/000093.htm)。版本/审订：2024-08-05；访问：`page_opened`；编写组：`US-ADAM`。定位：Household activities94; When to call97–113。实际范围：Household activities94; When to call97–113. NLM hosts, ADAM writes/reviews; textbook references and copyright retained. Universal week-by-week progression not adopted.

原有来源中本轮重新打开了 NHS 心梗、Mayo 心梗症状/诊疗、NHLBI 诊断/治疗/恢复/女性、NHS 氯吡格雷等相关原段。未改变且原独立报告已验证的主张只提供哈希关联，不声称本轮逐条重新审阅全部旧内容。

## 尚未通过的具体支持范围

这些条目不等于已证实医学错误；它们说明当前证据不能冒充完整双源或相同人群。

1. `diagnosis-5`：NSTEMI 可有严重堵塞由 Mayo 直接说明；未补第二份直接说明。纯描述性事实保留原正确措辞。
2. `care-1b/1c`：Mayo 与 NHS 的阿司匹林建议是各自机构有归属的不同说明；不谎称同一句获得两家相同支持。`care-3c` 驾驶法规来自 NHLBI，未加入任何具体驾驶时限。
3. `diagnosis-1a` 的 ECG 原理、`diagnosis-2a` 的早期血样及 `diagnosis-4b` 的同期介入分别有直接材料；目前精确短语并非都完成独立第二编写来源绑定。是否需要补证由其临床影响与独立审读判断，不机械删掉解释。
4. `treatment-2c`：重大出血风险直接见美国联合 ACS 指南；此次实际读取的 NICE 部分主要证明 STEMI/时间/PCI 条件，不冒充其出血禁忌详表。正文不列具体禁忌算法。
5. `medications-1b`：两条 AHA/联合 ACS 材料共同机构及指南依据，未据网址数认作独立双源。`medications-3b` 肌痛/无力联系医生两条 NHS/CUH 材料按一组保守登记。`medications-3c` 症状不直接等于严重肌损伤是编辑解释，未冒充来源明确量化诊断结论。
6. `medications-4b/4c`：ACE 钾/肾变化及监测的第二详细材料 CUH 为肾病人群；雷米普利页只支持干咳/头晕，不能覆盖整类药全部风险；已读 NICE 1.4.2 为 MI 后血压/肾功能监测计划，不含完整逐项血钾或通用复查时间。
7. `diet-2b`：降糖药与活动影响进餐安排直接见 NIDDK；Mayo 康复支持营养计划，未直接覆盖这个完整条件句。
8. `daily_care-1b`：活动胸痛/气短即停止并联系团队直接见 ADAM；已确诊心绞痛的 NHS 路径未借用作所有 MI 人群的第二材料。后面的急救危险行动另外绑定 NHS 与 NHLBI。
9. `special_populations-2b`：孕期/产后公众立即呼叫急救有 NHLBI 直接建议；ESC 专业 ACS 评估路径不冒充第二份公众急救原句。孕周和分娩时间告知是情境整理。ESC 页面标注 2026 更正 `ehaf1011`，本次无法取得更正内容；正文未增加具体孕期药品、剂量或数值阈值，仍留该版本边界。
10. `prognosis_followup-1c`：记录/使用心功能结果有依据，是否再次检查的具体触发条件尚未完成精确支持。未提供统一重复超声时间。

低风险药单、日期及症状整理不设临床双源硬门槛。以上和其他保留限制均见各节 `unresolved_questions`，作者没有将任何记录升级为 cross_checked。

## 绑定与验证

本轮已执行：模型 preview 验证、condition/source JSON Schema、14 个内容哈希、90 个主张精确双语摘录及全文顺序覆盖、来源元数据哈希、真实 pending/false 状态、共有文件非 MI 对象与 HEAD 深比较，以及 CRLF/无 CRCRLF 检查，全部通过。preview 在内存临时合并当前 74 篇加此草稿（75），没有修改生产库；结果临床签审 0、已核验章节仍为线上原有 28。

保留既有 CRLF 时普通 `git diff --check` 将行尾 CR 识别为 trailing whitespace；按既定行尾运行 `git -c core.whitespace=cr-at-eol diff --check` 通过，未改变 Git 配置或转换其他文件。

未运行与本次仅草稿修改无关的完整网站/数据库/浏览器回归；未进行本修订稿的独立医学交叉审核。通过结构校验不等于正文发布合格。

- 当前正文 canonical SHA-256：`491b41e0cf5aa8adf79a4011fd60986fba90272c838735337fb41604a63db27a`。
- 当前正文文件 SHA-256（CRLF）：`0aa9ed2849362a48f2011a167b12c69706581573e77c3330b67464aef20f1fce`。
- MI 14 条记录数组 canonical SHA-256（磁盘顺序）：`440147d0b0278371d9190ee58ef5aae3ab53896304bcfc046c14482f10d3f4f6`。
- MI 43 条来源数组 canonical SHA-256（磁盘顺序）：`b4b97981374130b8709781762a80ceb035571d6858cea4d4101948b81e8a595b`。
- 共有 editorial 文件 SHA-256：`1905a85bbe7e2c86a6b8682fdc2dbb95a3714962352be42dccfccf8673538d4d`。
- 共有 sources 文件 SHA-256：`26bb27377af2890c812ef5ff9d2801e370bbc1ab652bc12eb4e05f4546db87e9`。

| 章节 | 当前内容 SHA-256 | 主张数 |
|---|---|---:|
| summary | `1fb9d77067c1cbe98c3aa1d145606ddb8299ee48ac495eb2cc5e309dfbe96364` | 3 |
| causes_risks | `4a309319615b9076e96332b581df7b1800ded804f004c946911045522f21c941` | 3 |
| red_flags | `6b255da43626934cd26a1ed30f002bfcef82438d14e8792f0f612506ec8b4f8b` | 4 |
| care | `c8d9190cb9dc1a54460272db82a6266cf470d234605c8f4e99459dc5dd1cabac` | 9 |
| diagnosis | `3b129b17f1d91ba2efe36735d021a1ced3ff59773cc404448459df3cf84925cd` | 9 |
| differentials | `cfd2149f8d9a2c8cd54956ee6a2d1b89abac4b1bf250c0be8b1bd2ce094f131e` | 8 |
| treatment | `cd821115b947f498aa762e2a15b3adc581d47d87179b71a1d88d5c6240144f50` | 6 |
| medications | `31935b6421cfd3c538ad94b81eed629740805e9779c0ac7ec3a7312dacbdbd83` | 19 |
| diet | `6d1f8af0e583d5da6ac4217df0c06f4221f536c5559e5bc1d9647f7524e91259` | 6 |
| daily_care | `aceec413c28cc0a59ea5defee0a0580737e06fd15faf6ff8938818d391f910dc` | 6 |
| special_populations | `da39bb824a6ef2a9d270e2a1b9448786e72c2d7f4594f09a3224d511ecc695c3` | 6 |
| prognosis_followup | `358ef1b6166092748f08af0cd750a07872a4c2bfa04858aecdf52a39f36b5233` | 5 |
| complications | `bbd2d0fbebf3110309da035f53dde46a3596908a60b413abfdf91d56f93ca407` | 3 |
| prevention | `ac5a6ebd10d23f5361a899bdc490eb9861441e67c623c5e2fac6c33d87beb75a` | 3 |

与原独立报告已验证主张的双语摘录哈希一致（24 项，仅关联旧审核，不自动批准本版）：`summary-0`, `summary-1`, `summary-2`, `causes_risks-0`, `causes_risks-1`, `causes_risks-2`, `red_flags-0`, `red_flags-1`, `care-0`, `diagnosis-0`, `differentials-0`, `differentials-1`, `treatment-0`, `treatment-1`, `medications-0`, `diet-1`, `daily_care-0`, `special_populations-1`, `prognosis_followup-0`, `prognosis_followup-2`, `complications-0`, `complications-2`, `prevention-0`, `prevention-1`。

对象已冻结，等待其他审核角色对改动与真实缺口作一次定向复核。本作者停止写入；不以草稿数量、主张数或来源数申报新增覆盖。
