# 在线阅读、数据库发布与回滚

正式入口：[医学站](https://www.zengyuwei.cn/healthcare/)；[主页](https://www.zengyuwei.cn/home/)；[GitHub](https://github.com/StarlightDamian/knowledge-healthcare)。首次静态部署的历史回执保留在 `reports/deployment-20260930.md`；本次数据库迁移的实际进展见 `reports/implementation-postgres-icd.md`。

## 数据与进程

Git 中的 JSON 是唯一编辑入口。导入器校验 JSON、证据记录及哈希，创建不可变候选版本，回读核对后才事务切换发布指针。线上 API 使用只读角色，不修改正文。迁移既有72篇和两个知识模块不提升其医学或编辑审核状态；后续医学正文变更必须经过编辑证据门禁。

- 独立 PostgreSQL 18.6：`127.0.0.1:54330`，程序复用服务器已有安装，数据位于 `/mnt/raid1/03_software_engineering/01_database/project/knowledge-healthcare/data`。
- 正式数据库 `knowledge_healthcare`，测试库 `knowledge_healthcare_test`。`healthcare_admin` 管理医学库，`healthcare_importer` 导入发布，`healthcare_reader` 只读；均不访问其他项目库。
- API：`127.0.0.1:11004`，系统服务 `knowledge-healthcare-api.service`。读配置以0600权限存放，不进入Git或终端输出。
- 共享入口11003仅将精确的 `/healthcare`、`/healthcare/` 前缀交给医学服务；主页和其他静态路径沿用原发布目录。近似前缀不会转发。既有Cloudflare隧道和其他应用路由保持原配置。
- 网页和API返回 `no-transform`，防止托管层注入分析脚本。正文访问可进入服务器日志，搜索词、月龄与体温不上传。

## 本地开发与检查

```bash
python -m pip install -r requirements-runtime.txt -r requirements-dev.txt
python -m src.guide validate
python -m src.guide content-audit
python -m src.guide editorial-audit
python -m src.guide coverage-icd
npm test
python -m unittest discover -s tests -p 'test_*.py'
python -m src.guide build
```

数据库集成测试要求设置三个 `HEALTHCARE_TEST_*_DSN`：`ADMIN`、`IMPORT`、`READ`。测试仅允许重置名称以 `_test` 结尾的库。缺少连接配置时数据库单测会跳过，不算验证通过。浏览器检查需要真正的数据库与HTTP：

```bash
python -c "from tests.test_store_publication import database_fixture; database_fixture()"
python -m playwright install chromium
python -m unittest discover -s tests/e2e -p 'test_browser.py'
```

`GUIDE_URL` 可指定已启动的候选HTTP服务。没有这个变量时浏览器测试启动本地Uvicorn，读取 `HEALTHCARE_TEST_READ_DSN`。普通 `python -m http.server` 和直接打开HTML不会提供正文接口。GitHub Pages静态发布入口已移除。

## 导入、发布与回滚

正式操作通过私有环境设置 `HEALTHCARE_ADMIN_DSN`、`HEALTHCARE_IMPORT_DSN`、`HEALTHCARE_READ_DSN`；公开API进程仅获得READ变量。不要把密码放到命令参数、提交记录或截图中。

1. 备份当前发布目录、服务配置与医学数据库，使用独立测试库完成恢复演练。
2. 对待发布Git提交运行CI和真实HTTP检查。将该提交放入新的独立运行目录，保留上一个目录。
3. 执行 `python -m src.guide db-migrate`。首次等价迁移使用 `db-import --git-commit <完整提交SHA> --initial-baseline`，后续导入省略该标志。导入返回候选 `release_id`，不切换当前版本。
4. 回读核对后执行 `db-publish <候选ID> --expected-current <当前ID>`；首次为 `--expected-current none`。冲突或校验失败不切换指针。
5. 切换API运行目录并重启医学服务，先核对回环 `/healthcare/api/v1/healthz`、详情和CSV，再更新精确前缀入口。核对公网版本、主页及其他原有路径。
6. 回滚内容使用 `db-rollback <上一已发布ID> --expected-current <当前ID>`；同时按需恢复上一API运行目录或共享入口服务配置。旧浏览器仍固定其原发布ID，历史版本不能在有活跃页面时随意删除。

`db-status` 读取当前发布元数据；`db-status --release-id <ID>` 检查特定版本。每次导入相同清单幂等；正文哈希包括内容，旧签审不能为修改后的正文背书。

## 接口与容量

`/healthcare/api/v1` 提供 bootstrap、分页catalog、单篇conditions、最多100项batch、knowledge模块、流式CSV及healthz。目录只包含检索字段与概览首段；正文按需加载。卡片与矩阵每页50项，选择集合跨页保留。CSV导出目标全集，保持22列和原始段落换行。

每个接口都使用同一 `release_id`；无效版本明确报错，数据库失败显示加载失败。危险规则随小型网页资源提供，独立于正文接口和筛选。合成大目录只用于性能测试，不进入线上发布和医学覆盖分子。

## 完整性与临床签审

```bash
python -m src.guide validate --mode clinical  # 当前应失败：没有真实临床签审
python -m src.guide package --out release.zip
python -m src.guide verify
```

打包包含官方ICD快照和哈希。完整性检查不提供数字签名或医学认证。编辑交叉核验、ICD类别映射和执业医生签审分别统计。
