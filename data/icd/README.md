# ICD-11 MMS 2026-01 官方快照与项目范围

`SimpleTabulation-ICD-11-MMS-en-2026-01.zip` 是未修改的 [WHO 官方下载](https://icdcdn.who.int/static/releasefiles/2026-01/SimpleTabulation-ICD-11-MMS-en.zip)，2026-09-30 获取，SHA-256 为 `f1356588f40953a83e3af2b662deab47c5e269f944d1ea4ed0cfeb2007c7cd39`。版本与规则哈希在 `manifest.json`。

`catalog.json.gz` 保留全部 37,152 个工作表行的代码、原始标题、Foundation URI、MMS URI、父级、章节、叶级和残余类别属性；缩进用的标题连字符原样保留。`decision`、`reason`、`release` 和 `row` 是本项目添加的审计字段，不是 WHO 的决定。不会把官方英文标题的自行翻译写成 WHO 中文版本。

项目正文范围由 `rules.json` 冻结：01–22 章的末级类别，包含其他特指/未特指；25 章逐个裁定；26 章传统医学补充分类单独公开；23、24、V、X 章分别按外因、医疗接触与健康状态因素、功能评估、扩展码排除。共 13,155 个合格类别。分类分母不等于人群患病负担，也不构成新的疾病分类标准。

`mappings.json` 关联网站文章与官方类别。名称相同只生成 `pending` 候选，不能证明临床范围一致。`confirmed` 必须绑定当前文章哈希，记录 `semantic_scope_review`、实际审核角色、日期、`entire_leaf_category` 范围、理由和所考虑的排除项。AI 辅助编辑审核须如实标明，不写成执业医生签审。知识地图、别名和待办标题不能增加覆盖分子。

版权与许可：International Classification of Diseases, Eleventh Revision (ICD-11), World Health Organization (WHO) 2019. [ICD-11](https://icd.who.int/browse11). Licensed under [CC BY-ND 3.0 IGO](https://creativecommons.org/licenses/by-nd/3.0/igo/). [WHO 数字版许可](https://icd.who.int/en/docs/ICD11-license.pdf)规定软件集成保留代码、标题和 URI，添加的字段须清楚标识；另行制作跨分类对照或翻译有单独许可要求。本项目不声称 WHO 认可本站。

重现：调用 `guide.icd.freeze_icd()` 从已保存的官方 ZIP 和明确的规则重新生成目录；`load_icd()` 将重新解析 ZIP，核对原文件、规则、完整目录哈希及压缩目录内容，不能用手改数字替代目录。

`SimpleTabulation-ICD-11-MMS-zh-2026-01.zip` 来自同版WHO中文浏览器“电子表格文件”链接；SHA-256为 `8cb750a5c6feaabe9f1d6cf705aa5727b5867990ca48c1c85b20444ff0e370da`。中文表的35,664个类别与英文表逐代码、Foundation URI、MMS URI、章节及叶级/残余属性一致，提供全部13,155个纳入项的官方中文名称。两份表有19个父级字段不同，仅附加中文名称，冻结英文树及分母保持不变。`load_chinese_titles()`每次重新验证原件及身份字段；详见[语言对齐记录](../../reports/icd-chinese-title-import.json)。

`priorities.json` 是本站编辑优先规则和来源范围，不是WHO分类字段或临床分诊级别。`python -m src.guide priorities-icd`生成全量中英CSV、23章清单及执行队列，`--check`验证生成物与当前输入一致。每个合格类别均列出，已完整覆盖的类别退出待补队列；未知的专业判断保留未知。最终目标100%，95%为里程碑，正文资格仍由原有证据和语义映射门禁判断。
