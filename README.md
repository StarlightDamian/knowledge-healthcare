# 开放医学指南 · Open Medical Guide

**v0.2.0-online · 支持本地检索、科室导航和横向比较的医学知识库。**

**在线访问：[https://www.zengyuwei.cn/healthcare/](https://www.zengyuwei.cn/healthcare/)**

[GitHub 仓库](https://github.com/StarlightDamian/knowledge-healthcare) · [个人主页入口](https://www.zengyuwei.cn/home/)

[English](README.en.md) · [本地网页](index.html) · [正文标准](docs/content-depth-standard.md) · [覆盖审计与补充计划](docs/coverage-audit-and-roadmap.md) · [使用/部署](docs/deployment.md) · [证据政策](docs/evidence-policy.md) · [本批候选验证记录](reports/p0-04-release-validation.json) · [最近公网记录](reports/p0-03-release-validation.json) · [全部病症优先清单](docs/icd-priorities/index.md)

## 已经可以做什么

在左侧按“大科 → 亚科”选择范围，在右侧搜索疾病名称、俗称和部分中英文症状。详情先展示危险信号，提供章节目录和分条正文；比较表可展开全文，CSV 保留全文及换行。右上角可切换语言，并保留筛选、查询、比较选择和当前详情。代码不调用远程模型、搜索服务、CDN、字体服务或统计服务，不把查询写入 URL 或浏览器历史存储。

新增“癌症地图”和“全生命周期”入口。癌症地图按34个统计癌症分组及两个补充分组组织，分别解释病理、分期、治疗路径、证据和负担口径；全生命周期将健康影响拆为20个共用因素，按6个互不重叠的年龄段查阅，孕产作为附加情境。乳腺癌、结直肠癌等复用已有病症正文，癌症风险和年龄行动引用同一份健康因素。三个入口分别保留查询；点击科室可返回病症主题。详见 [MECE 内容映射](docs/research-mece-map.md)。

网页通过同源 API 读取 PostgreSQL 中的不可变发布版本。搜索词、月龄和体温留在浏览器；主题访问可能进入服务器日志。正文需要联网，全文可导出为 CSV。

## 内容与来源状态

以下为当前仓库计量；P0-04为本地候选，公网状态以 [P0-03实际发布记录](reports/p0-03-release-validation.json) 为准。

| 项目 | 当前仓库状态 |
|---|---|
| 健康主题 | **98** 个病症主题，包含92个疾病或健康问题及6个症状入口 |
| 分类 | **11** 个大科、**34** 个有内容的亚科；保留18个归档主目录及既有科室ID |
| 医学正文 | 98篇中英正文，共 **1,372** 个双语章节；全项目 **1,680** 章；卡片从概览首段自动提取 |
| 参考资料 | 逐节来源定位与边界见 [扩写记录](reports/content-expansion/)；保留929条来源记录 |
| 论文卡 | 3 个原始随机试验的摘要级草稿；1 个仅书目元数据，未抽取治疗结论 |
| 抽样交叉检查 | 普通感冒 5 条窄主张的双来源编辑核对，见 [记录](reports/claim-spot-checks.md) |
| 国际化 | 12 种界面语言；仅中英有医学正文，其余明确回退英语，未完成地区医学本地化 |
| 检索 | 本地词法/BM25、名称及别名加权、中文二元切词、有限否定处理 |
| 危险提示 | 13 条模式规则 + 小月龄婴儿发热结构化规则 |
| 横向比较 | 每页50个主题；跨页多选；22列全文CSV；保留来源和状态 |
| 癌症地图 | 36 个中英知识单元；癌症统计分组与病理、分期、分子标志物分开解释 |
| 全生命周期 | 8 组、20 个中英健康因素；6 个年龄段与孕产附加情境引用共用因素 |
| 扩充清单 | **188** 个仅标题待办，与完整正文分开统计 |
| 医学签审 / 完成逐项编辑核验的主题 | **0 / 31**；合计434节、1677项中英主张；P0-04新增5篇、扩写2篇，见 [候选验证记录](reports/p0-04-release-validation.json)；尚未证明公网发布 |
| 全病种覆盖目标 | ICD-11 MMS 2026-01：冻结13,155个合格类别；完整核验覆盖131 / 13,155（约0.995819%），剩余13,024类；目标100%，95%为阶段里程碑；131条确认、2条部分、44条待裁定 |

独立医学审阅、译文审核与危险提示规则的临床验证待完成。网页通过“内容与来源说明”和详情末尾的“来源与编辑信息”集中展示状态，每节保留参考链接。高级专业数据（如患病率、定量预后和地区药品批准）待整理，标为 `null / not_yet_curated`。

最初20个主题中10篇已完成逐项核验，另外10篇保留具体补证与修订任务。P0-01新增5篇、扩写严重过敏反应；P0-02继续扩写脑膜炎、严重过敏反应和产后出血，新增25项双语主张、涉及21节，保留其余79篇原文。医学签审仍为0。

历史P0-03批次：P0-03完成19个规范主题的独立编辑审核，保留原ID并逐叶裁定，见 [本批接受记录](reports/p0-03-acceptance.json)。全量P0共133个类别，97个已完整、36个继续待补；最初10项急危重正文缺口已补9项，一氧化碳中毒仍在后续清单。文章提及、父级名称或共同急救措施不自动算作完整覆盖。

P0-04当前本地候选完成7个规范主题（新增5、扩写2），见 [接受记录](reports/p0-04-acceptance.json)。P0已完整130/133，剩余3个SAH类别（8B01.0、8B01.1、8B01.2）被阻断，未宣称全部完成；医学签审仍为0。

已保存 [文案审查记录](reports/anti-defensive-writing-audit.md) 和 [冻结目录覆盖数据](reports/icd-coverage.json)。新增病种按冻结目录、急危重症、常见病症、其余类别、95%阶段复核和100%终点验收的顺序推进。完整目录逐项列于[专业优先清单](docs/icd-priorities/index.md)，可[下载全量CSV](reports/icd-priorities.csv)。

两份研究报告的整理与重新核对见 [癌症导入记录](reports/research-cancer-import.md) 和 [生命周期导入记录](reports/research-lifecycle-import.md)。新增地图单元单独统计，不作为新增完整病症或ICD映射计入病种覆盖率。来源逐节定位，统计数值保留年份、地区和适用范围。

## 使用

打开 [在线医学站](https://www.zengyuwei.cn/healthcare/)。GitHub 保存唯一编辑源；服务器按发布清单导入数据库，网页在一次会话内固定版本。部署和回滚见 [部署文档](docs/deployment.md)。本地静态服务器及 GitHub Pages 不提供正文 API。

## 开发、更新与验证

运行环境：Python 3.10+、PostgreSQL 18.6、FastAPI/Uvicorn/psycopg；Node.js 22+（JavaScript 测试）；测试使用 JSON Schema 与 Playwright。

```bash
python -m pip install -r requirements-runtime.txt -r requirements-dev.txt
python -m src.guide validate
python -m src.guide editorial-audit
python -m src.guide coverage-icd
python -m src.guide priorities-icd
npm test
python -m unittest discover -s tests -p "test_*.py"
python -m src.guide content-audit
python -m src.guide build

# 浏览器检查需已初始化的独立测试库，见部署文档
python -m pip install -r requirements-dev.txt
python -m playwright install chromium
python -m unittest discover -s tests/e2e -p "test_browser.py"

# 更新来源时找出受影响条目和字段
python -m src.guide impact common-cold-secondary

# 创建未索引的条目草稿：填完后再移入 data/conditions
python -m src.guide new example-topic --zh "示例主题" --en "Example topic"

# 临床发布检查：当前医学签审为0，预期拒绝
python -m src.guide validate --mode clinical
```

`content-audit` 输出每篇正文与编辑记录哈希及缺项；字数和列表只能发现异常，不能替代医学和双语内容判断。

只修改 `index.html` 会在下次构建时丢失；请修改 `data/conditions/*.json`、`data/knowledge/*.json` 或 `src/web/`。修改医学内容不会自动获得任何审核状态。

## 仓库导航：按需阅读

```text
src/guide/                Python 构建、验证、来源影响、覆盖率、打包 CLI
src/web/                  浏览器界面、搜索、危险信号与 CSV 模块
src/web/benchmark.mjs     可重复的合成检索基准，不是临床验证
tests/                    单元测试、检索/危险表达回归、浏览器测试
schemas/                  JSON Schema 2020-12
data/catalog/index.json   轻量索引：Agent 先读此文件，再读单个主题
data/conditions/          98 个双语结构化主题
data/knowledge/           癌症地图、健康因素与年龄情境；通过ID复用正文
data/evidence/            来源、论文卡、冲突、空审核者注册表
data/catalog/backlog.json 188 个未完成标题，与正文分离
templates/                新主题模板
docs/                     架构、钢人论证、证据、覆盖率、本地化、贡献和部署
reports/                  当前检查结果和审查记录
reports/content-expansion/逐篇来源定位、适用边界与编辑核对记录
index.html                已构建的在线静态网页
```

## 许可和责任

原创软件为 [MIT](LICENSE)，原创解释文字和摘要为 [CC BY 4.0](DATA_LICENSE.md)。第三方论文、医学术语体系、来源网页和品牌**不因被引用而改用本项目许可**。本实现借鉴两个参考项目的静态分发思想，没有复制它们的代码或正文。见 [第三方说明](THIRD_PARTY_NOTICES.md)、[医学免责声明](DISCLAIMER.md) 和 [治理](GOVERNANCE.md)。
