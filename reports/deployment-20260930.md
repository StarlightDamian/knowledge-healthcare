# 医学站上线记录 · 2026-09-30

- 正式网址：https://www.zengyuwei.cn/healthcare/
- 主页入口：https://www.zengyuwei.cn/home/
- 源码仓库：https://github.com/StarlightDamian/knowledge-healthcare
- 医学产物：`index.html`，1,456,051字节。
- SHA-256：`e8a4208db9a3185c7f1f2479709603a2c1d32398760b93f39af7e9613576cb1d`。

## 发布内容

复用现有主页静态服务和域名隧道，将自包含网页挂载到 `/healthcare/`，主页新增“开放医学指南”。线上原5项目保留，现为6项目；服务器源码中16项目的完整候选只构建验证，未随本次上线。原有13个其他文件逐一核对哈希不变，包括健身页和旧版哈希资源。

当前版本为 `release-xivdxwrt`，上一版为 `release-fkl42kqn`，均在服务器 `~/.local/share/home-page/releases/`。发布通过已有脚本原子切换 `current`，随后重启 `home-page.service`；主页和网站隧道服务均运行正常。启动后的即时请求曾遇到短暂连接拒绝，随后的服务状态和请求确认就绪，自动重启次数为0。

发布器补充医学目录保留规则：普通主页候选缺少应用目录时继承当前版本；明确提供目录时完整替换，不混入旧文件。共享静态服务器仅为医学和健身路径设置 `no-transform` 响应头。未修改DNS、隧道路由或防火墙。

服务器保留发布回执、候选和源码备份于 `~/.local/state/knowledge-healthcare/deploy-20260930/`，主页目录登记备份于 `~/.local/state/knowledge-healthcare/source-backup-20260930/`。医学原始产物另按SHA-256归档于服务器 `knowledge/knowledge-healthcare/releases/`。回滚方法见 [部署文档](../docs/deployment.md)。

## 已完成验证

- 候选HTTP：医学200、末尾斜杠跳转、查询参数响应头、健身响应头、近似路径和未知路径404。
- 候选Chromium：主页6项目、2个可用入口、4个待上线；点击医学入口打开72病症、36癌症单元和20健康因素。
- 发布脚本Linux测试：7项通过，覆盖首次挂载、普通主页更新和回滚保留、显式版本替换。
- 正式域名 `npm run test:public`：6/6通过、退出码0；包括主页资源、LeetCode只读入口和404边界。
- 公网完整GET：医学HTTP200且SHA-256与本地产物一致；健身HTTP200且SHA-256与发布前一致。
- 内置浏览器实际打开正式网址，正文与菜单初始化正常；[截图](../docs/screenshots/public-healthcare.png)。
- 正式域名医学定向Chromium测试：3/3通过，退出码0，115.922秒；覆盖癌症正文互链与语言状态、搜索危险提示与无查询上传、手机生命周期筛选和阿语英文回退。命令为设置 `GUIDE_URL=https://www.zengyuwei.cn/healthcare` 后运行 `python -m unittest discover -s tests/e2e -p test_browser.py -v -f -k test_knowledge_search_preserves -k test_cancer_entry_reuses -k test_lifecycle_stage_group`，完整输出见 [公网日志](logs/browser-public.txt)。
- 服务器主页目录源码：typecheck、lint、build、21项Node、相关Chromium11子测试通过；WebKit缺少既有系统依赖，未执行。源码测试与线上最小候选分别验收。

初次公网完整抓取和默认30秒浏览器导航曾超时；完整抓取延长到120秒后通过。公网链路存在首访延迟，本记录不将功能通过等同于性能达标。医学正文和构建产物没有因部署而修改；此前本地332项Node、74项Python、28项HTTP/离线浏览器检查保留在原测试报告中。

较广的公网批次已通过语言、矩阵、CSV、阿语布局、癌症互链及比较展开6项，随后主动停止，改用上述3项针对部署的完整测试；不把中止的批次称为28项通过。完整28项仍由本地HTTP和GitHub CI运行。

Git通过 `.gitattributes` 保留文件原始字节，避免Windows/Linux换行转换使已发布产物与完整性清单不一致。
