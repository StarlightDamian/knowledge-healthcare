# 开放医学指南 · Open Medical Guide

**v0.2.0-online · 支持本地检索、科室导航和横向比较的医学知识库。**

**在线访问：[https://www.zengyuwei.cn/healthcare/](https://www.zengyuwei.cn/healthcare/)**

[GitHub 仓库](https://github.com/StarlightDamian/knowledge-healthcare) · [个人主页入口](https://www.zengyuwei.cn/home/)

[English](README.en.md) · [本地网页](index.html) · [正文标准](docs/content-depth-standard.md) · [覆盖审计与补充计划](docs/coverage-audit-and-roadmap.md) · [使用/部署](docs/deployment.md) · [证据政策](docs/evidence-policy.md) · [本批测试与上线证据](reports/batch-01-osa-release-validation.json)

## 已经可以做什么

在左侧按“大科 → 亚科”选择范围，在右侧搜索疾病名称、俗称和部分中英文症状。详情先展示危险信号，提供章节目录和分条正文；比较表可展开全文，CSV 保留全文及换行。右上角可切换语言，并保留筛选、查询、比较选择和当前详情。代码不调用远程模型、搜索服务、CDN、字体服务或统计服务，不把查询写入 URL 或浏览器历史存储。

新增“癌症地图”和“全生命周期”入口。癌症地图按34个统计癌症分组及两个补充分组组织，分别解释病理、分期、治疗路径、证据和负担口径；全生命周期将健康影响拆为20个共用因素，按6个互不重叠的年龄段查阅，孕产作为附加情境。乳腺癌、结直肠癌等复用已有病症正文，癌症风险和年龄行动引用同一份健康因素。三个入口分别保留查询；点击科室可返回病症主题。详见 [MECE 内容映射](docs/research-mece-map.md)。

网页通过同源 API 读取 PostgreSQL 中的不可变发布版本。搜索词、月龄和体温留在浏览器；主题访问可能进入服务器日志。正文需要联网，全文可导出为 CSV。

## 内容与来源状态

| 项目 | 本版本状态 |
|---|---|
| 健康主题 | **73** 个病症主题，包含68个疾病或健康问题及5个症状入口 |
| 分类 | **11** 个大科、**33** 个有内容的亚科；保留18个归档主目录及既有科室ID |
| 医学正文 | 73篇中文、英文导读与分条知识，共 **1,022** 个双语字段块；卡片从概览首段自动提取 |
| 参考资料 | 逐节来源定位与边界见 [扩写记录](reports/content-expansion/)；保留332条来源记录 |
| 论文卡 | 3 个原始随机试验的摘要级草稿；1 个仅书目元数据，未抽取治疗结论 |
| 抽样交叉检查 | 普通感冒 5 条窄主张的双来源编辑核对，见 [记录](reports/claim-spot-checks.md) |
| 国际化 | 12 种界面语言；仅中英有医学正文，其余明确回退英语，未完成地区医学本地化 |
| 检索 | 本地词法/BM25、名称及别名加权、中文二元切词、有限否定处理 |
| 危险提示 | 12 条模式规则 + 小月龄婴儿发热结构化规则 |
| 横向比较 | 每页50个主题；跨页多选；22列全文CSV；保留来源和状态 |
| 癌症地图 | 36 个中英知识单元；癌症统计分组与病理、分期、分子标志物分开解释 |
| 全生命周期 | 8 组、20 个中英健康因素；6 个年龄段与孕产附加情境引用共用因素 |
| 扩充清单 | **197** 个仅标题待办，与完整正文分开统计 |
| 医学签审 / 完成逐项编辑核验的主题 | **0 / 1**；睡眠呼吸暂停14节、52项中英主张通过来源核验和独立对抗审阅 |
| 95% 全病种覆盖 | ICD-11 MMS 2026-01：冻结13,155个合格类别；完整证据核验覆盖1 / 13,155（约0.0076%），未达95%；1条语义映射确认，47条名称候选映射待裁定 |

独立医学审阅、译文审核与危险提示规则的临床验证待完成。网页通过“内容与来源说明”和详情末尾的“来源与编辑信息”集中展示状态，每节保留参考链接。高级专业数据（如患病率、定量预后和地区药品批准）待整理，标为 `null / not_yet_curated`。

首批20个主题已形成双语候选；睡眠呼吸暂停完成逐项核验，其余19个保留具体补证与修订任务，未计入完整覆盖。核验来源的共同依据和地区差异见 [独立审阅记录](reports/batch-01-osa-independent.json)。

已保存 [文案审查记录](reports/anti-defensive-writing-audit.md) 和 [冻结目录覆盖数据](reports/icd-coverage.json)。新增病种按冻结目录、急危重症、常见病症、其余类别和95%复核的顺序推进。

两份研究报告的整理与重新核对见 [癌症导入记录](reports/research-cancer-import.md) 和 [生命周期导入记录](reports/research-lifecycle-import.md)。新增地图单元单独统计，不作为新增完整病症或ICD映射计入95%覆盖率。来源逐节定位，统计数值保留年份、地区和适用范围。

## 使用

打开 [在线医学站](https://www.zengyuwei.cn/healthcare/)。GitHub 保存唯一编辑源；服务器按发布清单导入数据库，网页在一次会话内固定版本。部署和回滚见 [部署文档](docs/deployment.md)。本地静态服务器及 GitHub Pages 不提供正文 API。

## 开发、更新与验证

运行环境：Python 3.10+、PostgreSQL 18.6、FastAPI/Uvicorn/psycopg；Node.js 22+（JavaScript 测试）；测试使用 JSON Schema 与 Playwright。

```bash
python -m pip install -r requirements-runtime.txt -r requirements-dev.txt
python -m src.guide validate
python -m src.guide editorial-audit
python -m src.guide coverage-icd
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
data/conditions/          73 个双语结构化主题
data/knowledge/           癌症地图、健康因素与年龄情境；通过ID复用正文
data/evidence/            来源、论文卡、冲突、空审核者注册表
data/catalog/backlog.json 197 个未完成标题，与正文分离
templates/                新主题模板
docs/                     架构、钢人论证、证据、覆盖率、本地化、贡献和部署
reports/                  当前检查结果和审查记录
reports/content-expansion/逐篇来源定位、适用边界与编辑核对记录
index.html                已构建的在线静态网页
```

## 许可和责任

原创软件为 [MIT](LICENSE)，原创解释文字和摘要为 [CC BY 4.0](DATA_LICENSE.md)。第三方论文、医学术语体系、来源网页和品牌**不因被引用而改用本项目许可**。本实现借鉴两个参考项目的静态分发思想，没有复制它们的代码或正文。见 [第三方说明](THIRD_PARTY_NOTICES.md)、[医学免责声明](DISCLAIMER.md) 和 [治理](GOVERNANCE.md)。
